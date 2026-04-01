# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - ONNX 模型转换工具
将 PyTorch .pth 模型转换为 ONNX 格式以获得更好的推理性能

使用方法:
    python backend/convert_to_onnx.py [--input weights/best_model_full_mem.pth] [--output weights/model.onnx]

优势:
    - 更快的推理速度（通常提升 2-5 倍）
    - 更低的内存占用
    - 跨平台兼容性
    - 支持 ONNX Runtime 优化
"""
import os
import sys
import argparse

# 添加项目根目录到路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import torch
import torch.nn as nn
from torchvision import models


def convert_to_onnx(input_path, output_path=None, opset_version=11):
    """
    将 PyTorch 模型转换为 ONNX 格式
    
    Args:
        input_path: PyTorch 模型路径 (.pth)
        output_path: ONNX 输出路径 (默认同目录下 model.onnx)
        opset_version: ONNX opset 版本
    """
    print("=" * 60)
    print("胸影智诊V2.0 - ONNX 模型转换工具")
    print("=" * 60)
    
    # 检查输入文件
    if not os.path.exists(input_path):
        print(f"❌ 错误: 模型文件不存在: {input_path}")
        return False
    
    # 设置默认输出路径
    if output_path is None:
        input_dir = os.path.dirname(input_path)
        output_path = os.path.join(input_dir, 'model.onnx')
    
    print(f"\n输入模型: {input_path}")
    print(f"输出路径: {output_path}")
    
    # 设备选择
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")
    
    # 创建模型架构
    print("\n正在构建 MobileNetV2 模型...")
    model = models.mobilenet_v2(weights=None)
    num_features = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_features, 3)  # 3分类
    
    # 加载权重
    print("正在加载模型权重...")
    checkpoint = torch.load(input_path, map_location=device, weights_only=False)
    
    if 'model_state_dict' in checkpoint:
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model.load_state_dict(checkpoint, strict=False)
    
    model.to(device)
    model.eval()
    print("✅ 模型加载成功")
    
    # 创建 dummy 输入
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    
    # 导出 ONNX
    print(f"\n正在导出 ONNX 模型 (opset_version={opset_version})...")
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print(f"\n✅ ONNX 模型转换成功!")
    print(f"输出文件: {output_path}")
    
    # 验证模型
    try:
        import onnx
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        print("✅ ONNX 模型验证通过")
    except ImportError:
        print("⚠️ 未安装 onnx 包，跳过模型验证")
        print("   可运行: pip install onnx")
    
    # 测试 ONNX Runtime
    try:
        import onnxruntime as ort
        print("\n正在测试 ONNX Runtime 推理...")
        
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        session = ort.InferenceSession(output_path, sess_options, providers=providers)
        
        # 测试推理
        import time
        test_input = dummy_input.cpu().numpy()
        
        # 预热
        for _ in range(3):
            session.run(None, {'input': test_input})
        
        # 计时
        start = time.time()
        for _ in range(10):
            session.run(None, {'input': test_input})
        avg_time = (time.time() - start) / 10 * 1000
        
        print(f"✅ ONNX Runtime 测试成功")
        print(f"   Provider: {session.get_providers()[0]}")
        print(f"   平均推理耗时: {avg_time:.2f} ms")
        
    except ImportError:
        print("⚠️ 未安装 onnxruntime 包，跳过推理测试")
        print("   可运行: pip install onnxruntime 或 pip install onnxruntime-gpu")
    
    # 文件大小比较
    pytorch_size = os.path.getsize(input_path) / (1024 * 1024)
    onnx_size = os.path.getsize(output_path) / (1024 * 1024)
    
    print(f"\n文件大小:")
    print(f"  PyTorch: {pytorch_size:.2f} MB")
    print(f"  ONNX:    {onnx_size:.2f} MB")
    
    print("\n" + "=" * 60)
    print("转换完成!")
    print("=" * 60)
    
    return True


def main():
    parser = argparse.ArgumentParser(description='将 PyTorch 模型转换为 ONNX 格式')
    parser.add_argument('--input', '-i', 
                       default='weights/best_model_full_mem.pth',
                       help='输入 PyTorch 模型路径')
    parser.add_argument('--output', '-o', 
                       default=None,
                       help='输出 ONNX 模型路径')
    parser.add_argument('--opset', type=int, default=11,
                       help='ONNX opset 版本 (默认: 11)')
    
    args = parser.parse_args()
    
    # 处理相对路径
    input_path = args.input
    if not os.path.isabs(input_path):
        input_path = os.path.join(BASE_DIR, input_path)
    
    output_path = args.output
    if output_path and not os.path.isabs(output_path):
        output_path = os.path.join(BASE_DIR, output_path)
    
    convert_to_onnx(input_path, output_path, args.opset)


if __name__ == '__main__':
    main()
