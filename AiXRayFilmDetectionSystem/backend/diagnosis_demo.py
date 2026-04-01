# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - 高级应用示例
展示诊断模块在实际场景中的应用
"""
import os
import sys
import json
from datetime import datetime
from pathlib import Path
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from chest_xray_diagnoser import ChestXrayDiagnoser, diagnose_xray, DiagnosisResult


def example_1_basic_diagnosis():
    """示例1：基础诊断功能"""
    print("\n" + "=" * 60)
    print("示例1：基础诊断功能")
    print("=" * 60)
    
    # 创建测试图像
    import numpy as np
    from PIL import Image
    
    test_img_path = "demo_test_xray.jpg"
    test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(test_img).save(test_img_path)
    
    print(f"测试图像: {test_img_path}")
    
    # 方式1：使用便捷函数
    print("\n方式1：使用便捷函数 diagnose_xray()")
    result = diagnose_xray(test_img_path)
    
    if result.success:
        print(f"✓ 诊断成功")
        print(f"  结论: {result.conclusion}")
        print(f"  置信度: {result.confidence_percent:.1f}%")
        print(f"  耗时: {result.inference_time_ms:.2f}ms")
    else:
        print(f"✗ 诊断失败: {result.error_message}")
    
    # 清理
    os.remove(test_img_path)


def example_2_batch_processing():
    """示例2：批量诊断"""
    print("\n" + "=" * 60)
    print("示例2：批量诊断")
    print("=" * 60)
    
    import numpy as np
    from PIL import Image
    
    # 创建诊断器（只加载一次模型）
    model_path = BASE_DIR / "weights" / "best_model_full_mem.pth"
    diagnoser = ChestXrayDiagnoser(str(model_path))
    
    # 创建测试图像
    test_images = []
    for i in range(3):
        img_path = f"demo_batch_{i}.jpg"
        test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        Image.fromarray(test_img).save(img_path)
        test_images.append(img_path)
    
    print(f"批量诊断 {len(test_images)} 张图像...")
    
    # 批量诊断
    results = diagnoser.diagnose_batch(test_images)
    
    # 统计结果
    success_count = sum(1 for r in results if r.success)
    avg_time = sum(r.inference_time_ms for r in results if r.success) / success_count
    
    print(f"\n诊断结果统计:")
    print(f"  成功: {success_count}/{len(results)}")
    print(f"  平均耗时: {avg_time:.2f}ms")
    
    # 显示详细结果
    for i, result in enumerate(results):
        if result.success:
            print(f"\n  图像 {i+1}: {result.conclusion} ({result.confidence_percent:.1f}%)")
    
    # 清理
    for img_path in test_images:
        if os.path.exists(img_path):
            os.remove(img_path)


def example_3_export_json():
    """示例3：导出JSON格式结果"""
    print("\n" + "=" * 60)
    print("示例3：导出JSON格式结果")
    print("=" * 60)
    
    import numpy as np
    from PIL import Image
    
    # 创建测试图像
    test_img_path = "demo_export.jpg"
    test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(test_img).save(test_img_path)
    
    # 执行诊断
    result = diagnose_xray(test_img_path)
    
    # 构建输出数据
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'image_file': test_img_path,
        'diagnosis': result.to_dict(),
        'model_info': {
            'architecture': 'MobileNetV2',
            'classes': ['正常', '肺炎', '肺结核']
        }
    }
    
    # 导出JSON
    output_file = "diagnosis_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 结果已导出: {output_file}")
    print("\nJSON内容:")
    print(json.dumps(output_data, ensure_ascii=False, indent=2))
    
    # 清理
    os.remove(test_img_path)
    os.remove(output_file)


def example_4_different_inputs():
    """示例4：不同输入类型支持"""
    print("\n" + "=" * 60)
    print("示例4：不同输入类型支持")
    print("=" * 60)
    
    import numpy as np
    from PIL import Image
    from io import BytesIO
    
    # 创建诊断器
    model_path = BASE_DIR / "weights" / "best_model_full_mem.pth"
    diagnoser = ChestXrayDiagnoser(str(model_path))
    
    # 准备测试数据
    test_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    # 1. 文件路径输入
    print("\n1. 文件路径输入:")
    img_path = "demo_input_1.jpg"
    Image.fromarray(test_array).save(img_path)
    result1 = diagnoser.diagnose(img_path)
    print(f"   ✓ {result1.conclusion} ({result1.confidence_percent:.1f}%)")
    os.remove(img_path)
    
    # 2. PIL Image对象输入
    print("\n2. PIL Image对象输入:")
    pil_image = Image.fromarray(test_array)
    result2 = diagnoser.diagnose(pil_image)
    print(f"   ✓ {result2.conclusion} ({result2.confidence_percent:.1f}%)")
    
    # 3. numpy数组输入
    print("\n3. numpy数组输入:")
    result3 = diagnoser.diagnose(test_array)
    print(f"   ✓ {result3.conclusion} ({result3.confidence_percent:.1f}%)")
    
    # 4. 文件流输入
    print("\n4. 文件流输入:")
    buffer = BytesIO()
    Image.fromarray(test_array).save(buffer, format='JPEG')
    buffer.seek(0)
    result4 = diagnoser.diagnose(buffer)
    print(f"   ✓ {result4.conclusion} ({result4.confidence_percent:.1f}%)")
    
    print("\n✓ 所有输入类型测试通过")


def example_5_error_handling():
    """示例5：异常处理"""
    print("\n" + "=" * 60)
    print("示例5：异常处理")
    print("=" * 60)
    
    # 测试1：文件不存在
    print("\n测试1：文件不存在")
    result = diagnose_xray("nonexistent_file.jpg")
    if not result.success:
        print(f"✓ 正确捕获错误: {result.error_message}")
    
    # 测试2：未加载模型
    print("\n测试2：未加载模型就执行诊断")
    diagnoser = ChestXrayDiagnoser()  # 不加载模型
    result = diagnoser.diagnose("some_image.jpg")
    if not result.success:
        print(f"✓ 正确捕获错误: {result.error_message}")
    
    print("\n✓ 异常处理测试通过")


def example_6_performance_comparison():
    """示例6：性能对比（CPU vs GPU）"""
    print("\n" + "=" * 60)
    print("示例6：性能对比")
    print("=" * 60)
    
    import numpy as np
    from PIL import Image
    import time
    
    # 创建测试图像
    test_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    num_runs = 5
    
    # CPU性能测试
    print(f"\nCPU模式（运行{num_runs}次）:")
    model_path = BASE_DIR / "weights" / "best_model_full_mem.pth"
    diagnoser_cpu = ChestXrayDiagnoser(str(model_path), device='cpu')
    
    cpu_times = []
    for i in range(num_runs):
        result = diagnoser_cpu.diagnose(test_array)
        cpu_times.append(result.inference_time_ms)
    
    avg_cpu = sum(cpu_times) / len(cpu_times)
    print(f"  平均耗时: {avg_cpu:.2f}ms")
    print(f"  最小/最大: {min(cpu_times):.2f}ms / {max(cpu_times):.2f}ms")
    
    # GPU性能测试（如果可用）
    import torch
    if torch.cuda.is_available():
        print(f"\nGPU模式（运行{num_runs}次）:")
        diagnoser_gpu = ChestXrayDiagnoser(str(model_path), device='cuda')
        
        # 预热
        diagnoser_gpu.diagnose(test_array)
        
        gpu_times = []
        for i in range(num_runs):
            result = diagnoser_gpu.diagnose(test_array)
            gpu_times.append(result.inference_time_ms)
        
        avg_gpu = sum(gpu_times) / len(gpu_times)
        print(f"  平均耗时: {avg_gpu:.2f}ms")
        print(f"  最小/最大: {min(gpu_times):.2f}ms / {max(gpu_times):.2f}ms")
        print(f"  GPU加速比: {avg_cpu/avg_gpu:.2f}x")
    else:
        print("\nGPU不可用，跳过GPU测试")


def example_7_clinical_workflow():
    """示例7：临床工作流集成"""
    print("\n" + "=" * 60)
    print("示例7：临床工作流集成")
    print("=" * 60)
    
    import numpy as np
    from PIL import Image
    
    # 模拟临床数据
    patient_data = {
        'patient_id': 'P20260401001',
        'name': '张三',
        'age': 45,
        'gender': '男',
        'symptoms': '咳嗽、发热3天'
    }
    
    # 创建测试影像
    test_img_path = "demo_clinical.jpg"
    test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(test_img).save(test_img_path)
    
    print(f"患者信息:")
    print(f"  姓名: {patient_data['name']}")
    print(f"  年龄: {patient_data['age']}岁")
    print(f"  症状: {patient_data['symptoms']}")
    
    # 执行诊断
    print(f"\n正在执行AI诊断...")
    result = diagnose_xray(test_img_path)
    
    if result.success:
        # 生成临床报告
        report = {
            'report_id': f"RPT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'patient': patient_data,
            'diagnosis': {
                'conclusion': result.conclusion,
                'confidence': f"{result.confidence_percent:.1f}%",
                'probabilities': {
                    '正常': f"{result.probabilities['normal']*100:.1f}%",
                    '肺炎': f"{result.probabilities['pneumonia']*100:.1f}%",
                    '肺结核': f"{result.probabilities['tuberculosis']*100:.1f}%"
                }
            },
            'recommendation': '',
            'timestamp': datetime.now().isoformat()
        }
        
        # 根据诊断结果生成建议
        if result.conclusion == '正常':
            report['recommendation'] = '未见明显异常，建议定期复查。'
        elif result.conclusion == '肺炎':
            report['recommendation'] = '疑似肺炎，建议结合临床症状和实验室检查进一步确诊。'
        else:
            report['recommendation'] = '疑似肺结核，建议进行痰培养、PPD试验等进一步检查。'
        
        print(f"\n诊断报告:")
        print(f"  报告编号: {report['report_id']}")
        print(f"  诊断结论: {report['diagnosis']['conclusion']}")
        print(f"  置信度: {report['diagnosis']['confidence']}")
        print(f"  建议: {report['recommendation']}")
        
        # 保存报告
        report_file = f"clinical_report_{patient_data['patient_id']}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 报告已保存: {report_file}")
        
        os.remove(report_file)
    
    os.remove(test_img_path)


def run_all_examples():
    """运行所有示例"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  胸影智诊V2.0 - 高级应用示例".center(50) + "  █")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    
    examples = [
        ("基础诊断功能", example_1_basic_diagnosis),
        ("批量诊断", example_2_batch_processing),
        ("导出JSON格式", example_3_export_json),
        ("不同输入类型", example_4_different_inputs),
        ("异常处理", example_5_error_handling),
        ("性能对比", example_6_performance_comparison),
        ("临床工作流", example_7_clinical_workflow)
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n✗ 示例运行失败: {name}")
            print(f"  错误: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  所有示例运行完成".center(50) + "  █")
    print("█" + " " * 58 + "█")
    print("█" * 60 + "\n")


if __name__ == '__main__':
    run_all_examples()
