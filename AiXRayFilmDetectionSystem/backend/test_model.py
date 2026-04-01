#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
胸影智诊V2.0 - AI模型测试脚本
用于验证模型加载和推理功能
"""
import os
import sys
import torch
from PIL import Image
import numpy as np

# 添加项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.services.model_service import model_service

def test_model_loading():
    """测试模型加载"""
    print("\n" + "="*60)
    print("📦 测试 1: 模型加载")
    print("="*60)
    
    # 检查模型文件是否存在
    weights_path = os.path.join(BASE_DIR, 'backend', 'weights', 'best_model_full_mem.pth')
    
    if os.path.exists(weights_path):
        file_size = os.path.getsize(weights_path) / (1024 * 1024)
        print(f"✅ 模型文件存在: {weights_path}")
        print(f"   文件大小: {file_size:.2f} MB")
    else:
        print(f"❌ 模型文件不存在: {weights_path}")
        print("   请确保模型文件已放置到正确位置")
        return False
    
    # 加载模型
    success = model_service.load_model()
    
    if success:
        print("✅ 模型加载成功")
        
        # 显示模型状态
        status = model_service.get_model_status()
        print(f"\n📊 模型状态:")
        print(f"   设备: {status['device']}")
        print(f"   架构: {status['architecture']}")
        print(f"   类别: {status['classes']}")
        print(f"   GPU可用: {status['gpu_available']}")
        if status['gpu_available']:
            print(f"   GPU名称: {status['gpu_name']}")
            print(f"   GPU显存: {status['gpu_memory_gb']} GB")
        
        return True
    else:
        print("❌ 模型加载失败")
        return False


def test_model_inference():
    """测试模型推理"""
    print("\n" + "="*60)
    print("🔍 测试 2: 模型推理")
    print("="*60)
    
    # 创建测试图像（随机噪声）
    test_image_path = os.path.join(BASE_DIR, 'backend', 'static', 'test_image.jpg')
    os.makedirs(os.path.dirname(test_image_path), exist_ok=True)
    
    # 生成随机测试图像
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(test_image).save(test_image_path)
    print(f"✅ 测试图像已创建: {test_image_path}")
    
    # 执行推理
    try:
        result = model_service.predict(test_image_path)
        
        print("\n✅ 推理成功!")
        print(f"\n📊 诊断结果:")
        print(f"   诊断结论: {result['result_cn']} ({result['result']})")
        print(f"   置信度: {result['confidence']:.2%}")
        print(f"   推理时间: {result['inference_time']:.4f}秒")
        
        print(f"\n📈 概率分布:")
        for cls, prob in result['probabilities'].items():
            bar = '█' * int(prob * 50)
            print(f"   {cls:12s}: {prob:.2%} {bar}")
        
        # 清理测试文件
        os.remove(test_image_path)
        print(f"\n🧹 测试文件已清理")
        
        return True
    except Exception as e:
        print(f"❌ 推理失败: {str(e)}")
        return False


def test_gradcam_generation():
    """测试Grad-CAM生成"""
    print("\n" + "="*60)
    print("🔥 测试 3: Grad-CAM热力图生成")
    print("="*60)
    
    # 创建测试图像
    test_image_path = os.path.join(BASE_DIR, 'backend', 'static', 'test_gradcam.jpg')
    test_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(test_image).save(test_image_path)
    
    try:
        # 生成热力图
        heatmap = model_service.generate_gradcam(test_image_path)
        
        print(f"✅ Grad-CAM生成成功")
        print(f"   热力图尺寸: {heatmap.shape}")
        print(f"   数据类型: {heatmap.dtype}")
        
        # 保存测试热力图
        heatmap_path = os.path.join(BASE_DIR, 'backend', 'static', 'test_heatmap.jpg')
        model_service.save_heatmap(heatmap, heatmap_path)
        print(f"   保存路径: {heatmap_path}")
        
        # 清理测试文件
        os.remove(test_image_path)
        os.remove(heatmap_path)
        print(f"🧹 测试文件已清理")
        
        return True
    except Exception as e:
        print(f"❌ Grad-CAM生成失败: {str(e)}")
        # 尝试清理
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        return False


def test_model_status():
    """测试模型状态查询"""
    print("\n" + "="*60)
    print("📊 测试 4: 模型状态查询")
    print("="*60)
    
    status = model_service.get_model_status()
    
    print("✅ 模型状态获取成功\n")
    for key, value in status.items():
        print(f"   {key:20s}: {value}")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 胸影智诊V2.0 - AI模型测试套件")
    print("="*60)
    
    tests = [
        ("模型加载", test_model_loading),
        ("模型推理", test_model_inference),
        ("Grad-CAM生成", test_gradcam_generation),
        ("模型状态查询", test_model_status),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试异常: {test_name} - {str(e)}")
            results.append((test_name, False))
    
    # 打印测试总结
    print("\n" + "="*60)
    print("📋 测试总结")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name:20s}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n   总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过! 模型功能正常")
        print("✨ 系统已准备好进行肺部影像诊断")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
    
    print("="*60 + "\n")


if __name__ == '__main__':
    run_all_tests()
