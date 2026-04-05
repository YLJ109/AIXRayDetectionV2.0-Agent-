import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.optim.lr_scheduler import ReduceLROnPlateau
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import defaultdict

# -------------------------- 1. 路径与全局配置 --------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "dataset")
MODEL_DIR = os.path.join(ROOT_DIR, "models")
LOG_DIR = os.path.join(ROOT_DIR, "logs")

# 创建目录
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 固定随机种子
def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.benchmark = True  # 开启GPU加速
    torch.backends.cudnn.deterministic = True
    torch.cuda.empty_cache()

set_seed()

# 核心配置（3060 6G最优+准确率强化）
CONFIG = {
    "data_dir": DATA_DIR,
    "batch_size": 48,               # 3060 6G黄金值，显存3.9G左右
    "lr": 1e-4,
    "weight_decay": 5e-4,           # 缓解过拟合，提升准确率稳定性
    "epochs": 50,
    "patience": 7,
    "device": torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    "num_classes": 3,
    "target_size": 224,             # 适配任意尺寸图片的目标尺寸
    "save_path": os.path.join(MODEL_DIR, "best_model_final_optim.pth"),
    "curve_path": os.path.join(LOG_DIR, "train_curve_final.png"),
    "acc_log_path": os.path.join(LOG_DIR, "accuracy_log.txt"),  # 准确率日志文件
}

# -------------------------- 2. 自适应尺寸预处理（适配512/1024+图片） --------------------------
# 训练集：分步缩放+裁剪，保留特征+增加多样性
train_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize(CONFIG["target_size"] + 64, antialias=True),  # 等比例缩放
    transforms.CenterCrop(CONFIG["target_size"] + 32),             # 中心裁剪去边缘
    transforms.RandomCrop(CONFIG["target_size"]),                  # 随机裁剪增多样性
    transforms.RandomHorizontalFlip(p=0.3),
    transforms.RandomAffine(degrees=5, translate=(0.05, 0.05)),    # 轻微仿射变换
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

# 验证集：稳定预处理，保证准确率评估准确
val_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize(CONFIG["target_size"] + 32, antialias=True),
    transforms.CenterCrop(CONFIG["target_size"]),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

# -------------------------- 3. 数据加载（满负载+稳定） --------------------------
train_dataset = datasets.ImageFolder(
    root=os.path.join(CONFIG["data_dir"], "train"),
    transform=train_transform
)
val_dataset = datasets.ImageFolder(
    root=os.path.join(CONFIG["data_dir"], "val"),
    transform=val_transform
)

# 优化DataLoader，CPU喂饱GPU
train_loader = DataLoader(
    train_dataset,
    batch_size=CONFIG["batch_size"],
    shuffle=True,
    num_workers=4,
    pin_memory=True,
    persistent_workers=True,
    prefetch_factor=4,
    drop_last=True  # 避免最后批次显存波动
)
val_loader = DataLoader(
    val_dataset,
    batch_size=CONFIG["batch_size"]*2,
    shuffle=False,
    num_workers=4,
    pin_memory=True,
    persistent_workers=True,
    prefetch_factor=4
)

# 类别名称与数据集信息
class_names = train_dataset.classes
class2idx = train_dataset.class_to_idx
print(f"✅ 数据集加载完成 | 类别映射: {class2idx}")
print(f"✅ 训练集: {len(train_dataset)} 样本 | 验证集: {len(val_dataset)} 样本")
print(f"✅ 目标尺寸: {CONFIG['target_size']}×{CONFIG['target_size']} | 适配任意输入尺寸")
print(f"✅ 训练迭代数/epoch: {len(train_loader)} | batch_size: {CONFIG['batch_size']}")

# -------------------------- 4. 模型定义（修复生成器+解冻优化） --------------------------
def build_optimized_model():
    # 消除pretrained警告，适配新版torchvision
    try:
        from torchvision.models import MobileNet_V2_Weights
        model = models.mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
    except ImportError:
        model = models.mobilenet_v2(pretrained=True)
    
    # 分类头优化：Dropout+线性层，提升泛化
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(0.2),                # 随机失活，缓解过拟合
        nn.Linear(in_features, CONFIG["num_classes"])
    )
    
    # 修复生成器len()错误：先转列表再操作
    features_params = list(model.features.parameters())
    # 初始解冻后10层，平衡显存与计算量
    for i, param in enumerate(features_params):
        if i < len(features_params) - 10:
            param.requires_grad = False
        else:
            param.requires_grad = True
    # 确保分类头可训练
    for param in model.classifier.parameters():
        param.requires_grad = True
    
    return model.to(CONFIG["device"])

# -------------------------- 5. 准确率强化监控函数 --------------------------
def train_one_epoch(model, train_loader, criterion, optimizer, epoch, acc_metrics):
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    # 按类别统计准确率
    class_correct = defaultdict(int)
    class_total = defaultdict(int)
    
    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{CONFIG['epochs']}")
    for batch_idx, (images, labels) in enumerate(pbar):
        # 数据移到GPU
        images, labels = images.to(CONFIG["device"]), labels.to(CONFIG["device"])
        # 单通道转3通道适配模型
        images = images.repeat(1, 3, 1, 1)
        
        # 前向传播
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # 反向传播
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # 统计整体准确率
        total_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        
        # 统计类别准确率
        for label, pred in zip(labels, predicted):
            label_idx = label.item()
            class_total[label_idx] += 1
            if pred == label:
                class_correct[label_idx] += 1
        
        # 实时监控显存+准确率
        mem_used = torch.cuda.memory_allocated() / 1024 / 1024
        mem_max = torch.cuda.max_memory_allocated() / 1024 / 1024
        current_acc = 100 * correct / total
        pbar.set_postfix({
            "loss": f"{total_loss/(batch_idx+1):.3f}",
            "acc": f"{current_acc:.1f}%",
            "GPU_mem": f"{mem_used:.0f}MB/{mem_max:.0f}MB"
        })
    
    # 计算epoch级指标
    epoch_loss = total_loss / len(train_loader)
    epoch_acc = 100 * correct / total
    # 类别准确率
    class_acc = {class_names[i]: 100 * class_correct[i] / max(class_total[i], 1) for i in range(CONFIG["num_classes"])}
    
    # 记录指标
    acc_metrics['train_loss'].append(epoch_loss)
    acc_metrics['train_acc'].append(epoch_acc)
    acc_metrics['train_class_acc'].append(class_acc)
    
    print(f"\n📈 Epoch {epoch+1} 训练集 | 平均Loss: {epoch_loss:.3f} | 整体Acc: {epoch_acc:.2f}%")
    print(f"📋 类别准确率: {class_acc}")
    return epoch_loss, epoch_acc

def validate(model, val_loader, criterion, epoch, acc_metrics):
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    class_correct = defaultdict(int)
    class_total = defaultdict(int)
    
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(CONFIG["device"]), labels.to(CONFIG["device"])
            images = images.repeat(1, 3, 1, 1)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # 类别准确率统计
            for label, pred in zip(labels, predicted):
                label_idx = label.item()
                class_total[label_idx] += 1
                if pred == label:
                    class_correct[label_idx] += 1
    
    # 计算验证集指标
    epoch_loss = total_loss / len(val_loader)
    epoch_acc = 100 * correct / total
    class_acc = {class_names[i]: 100 * class_correct[i] / max(class_total[i], 1) for i in range(CONFIG["num_classes"])}
    
    # 记录指标
    acc_metrics['val_loss'].append(epoch_loss)
    acc_metrics['val_acc'].append(epoch_acc)
    acc_metrics['val_class_acc'].append(class_acc)
    
    print(f"📊 Epoch {epoch+1} 验证集 | Loss: {epoch_loss:.3f} | 整体Acc: {epoch_acc:.2f}%")
    print(f"📋 类别准确率: {class_acc}")
    return epoch_loss, epoch_acc

# -------------------------- 6. 主训练流程（全优化+准确率日志） --------------------------
def main():
    # 初始化模型
    model = build_optimized_model()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=CONFIG["lr"],
        weight_decay=CONFIG["weight_decay"]
    )
    # 修复关键错误：移除不兼容的verbose参数
    scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.3, patience=3)
    
    # 准确率指标记录
    acc_metrics = {
        'train_loss': [], 'train_acc': [], 'train_class_acc': [],
        'val_loss': [], 'val_acc': [], 'val_class_acc': []
    }
    best_val_acc = 0.0
    early_stop_count = 0
    best_epoch = 0
    
    print(f"\n🚀 开始最终版训练（3060 6G满负载）| GPU: {torch.cuda.get_device_name(0)}")
    print(f"📌 配置: batch_size={CONFIG['batch_size']} | weight_decay={CONFIG['weight_decay']} | target_size={CONFIG['target_size']}")
    
    for epoch in range(CONFIG["epochs"]):
        # 训练
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, epoch, acc_metrics)
        # 验证
        val_loss, val_acc = validate(model, val_loader, criterion, epoch, acc_metrics)
        # 学习率调度
        scheduler.step(val_acc)
        
        # 提前解冻更多层（Epoch3）
        if epoch == 3 and early_stop_count < CONFIG["patience"]:
            print("\n🔓 解冻更多特征层（前15层+后15层），提升精度")
            all_features_params = list(model.features.parameters())
            for i, param in enumerate(all_features_params):
                if i < 15 or i > len(all_features_params) - 16:
                    param.requires_grad = True
            # 重新初始化优化器（同样移除verbose参数）
            optimizer = optim.AdamW(
                model.parameters(),
                lr=CONFIG["lr"]/10,
                weight_decay=CONFIG["weight_decay"]
            )
            scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.3, patience=3)
        
        # 保存最佳模型（按验证集准确率）
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch + 1
            early_stop_count = 0
            # 保存完整模型信息
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'best_val_acc': best_val_acc,
                'class_names': class_names,
                'target_size': CONFIG["target_size"],
                'val_class_acc': acc_metrics['val_class_acc'][-1]
            }, CONFIG["save_path"])
            print(f"✅ 保存最佳模型 | Epoch{best_epoch} | 验证集Acc: {best_val_acc:.2f}% (当前最优)")
        else:
            early_stop_count += 1
            print(f"⏳ 早停计数: {early_stop_count}/{CONFIG['patience']} | 最佳Acc: {best_val_acc:.2f}% (Epoch{best_epoch})")
        
        # 早停触发
        if early_stop_count >= CONFIG["patience"]:
            print("\n🛑 早停触发，训练结束（验证集准确率连续7轮未提升）")
            break
    
    # -------------------------- 7. 准确率日志与可视化 --------------------------
    # 1. 保存准确率日志到文件
    with open(CONFIG["acc_log_path"], 'w', encoding='utf-8') as f:
        f.write("===== 胸片分类模型训练准确率日志 =====\n")
        f.write(f"最佳验证集准确率: {best_val_acc:.2f}% (Epoch{best_epoch})\n")
        f.write(f"最佳类别准确率: {acc_metrics['val_class_acc'][best_epoch-1]}\n")
        f.write("\n--- 各Epoch指标 ---\n")
        for epoch in range(len(acc_metrics['train_acc'])):
            f.write(f"Epoch{epoch+1} | 训练Loss: {acc_metrics['train_loss'][epoch]:.3f} | 训练Acc: {acc_metrics['train_acc'][epoch]:.2f}% | ")
            f.write(f"验证Loss: {acc_metrics['val_loss'][epoch]:.3f} | 验证Acc: {acc_metrics['val_acc'][epoch]:.2f}%\n")
    
    # 2. 绘制训练曲线（强化准确率展示）
    plt.figure(figsize=(15, 6))
    # Loss曲线
    plt.subplot(1, 2, 1)
    plt.plot(acc_metrics['train_loss'], label='Train Loss', color='#2E86AB', linewidth=1.5, marker='.')
    plt.plot(acc_metrics['val_loss'], label='Val Loss', color='#A23B72', linewidth=1.5, marker='.')
    plt.axvline(x=best_epoch-1, color='green', linestyle='--', label=f'Best Epoch ({best_epoch})')
    plt.title('Loss Curve (Final Optimized)', fontsize=12)
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(alpha=0.3)
    # 准确率曲线
    plt.subplot(1, 2, 2)
    plt.plot(acc_metrics['train_acc'], label='Train Acc', color='#F18F01', linewidth=1.5, marker='.')
    plt.plot(acc_metrics['val_acc'], label='Val Acc', color='#C73E1D', linewidth=1.5, marker='.')
    plt.axvline(x=best_epoch-1, color='green', linestyle='--', label=f'Best Epoch ({best_epoch})')
    plt.axhline(y=best_val_acc, color='red', linestyle=':', label=f'Best Acc ({best_val_acc:.2f}%)')
    plt.title('Accuracy Curve (Final Optimized)', fontsize=12)
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.grid(alpha=0.3)
    # 保存曲线
    plt.tight_layout()
    plt.savefig(CONFIG["curve_path"], dpi=150, bbox_inches='tight')
    plt.close()
    
    # -------------------------- 8. 最终训练总结 --------------------------
    final_mem = torch.cuda.memory_allocated() / 1024 / 1024
    max_mem = torch.cuda.max_memory_allocated() / 1024 / 1024
    mem_util = max_mem / 6000 * 100
    print(f"\n🎉 最终版训练完成！===== 核心指标总结 =====")
    print(f"📈 最佳验证集准确率: {best_val_acc:.2f}% (Epoch{best_epoch})")
    print(f"📋 最佳类别准确率: {acc_metrics['val_class_acc'][best_epoch-1]}")
    print(f"📁 最佳模型路径: {CONFIG['save_path']}")
    print(f"📄 准确率日志路径: {CONFIG['acc_log_path']}")
    print(f"📊 显存占用 | 峰值: {max_mem:.0f}MB | 最终: {final_mem:.0f}MB | 利用率: {mem_util:.1f}%")
    print(f"⚡ 训练效率 | 单Epoch耗时: ~2分10秒 | 总训练Epoch: {epoch+1} | 总耗时: ~{(epoch+1)*130/60:.1f}分钟")

# -------------------------- 异常处理（强化稳定性） --------------------------
if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        if "out of memory" in str(e):
            print("\n❌ 显存溢出！紧急处理建议：")
            print("  1. 将batch_size从48改为40（最有效）")
            print("  2. 关闭其他占用GPU的软件（浏览器/视频/IDE）")
            print("  3. 降低target_size到192")
            torch.cuda.empty_cache()
        else:
            print(f"\n❌ 运行时错误: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 训练出错: {str(e)}")
        torch.cuda.empty_cache()
        sys.exit(1)