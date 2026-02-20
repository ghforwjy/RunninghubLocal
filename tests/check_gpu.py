#!/usr/bin/env python3
"""
检查GPU环境的测试脚本
"""
import subprocess
import sys

def check_nvidia_smi():
    """检查 nvidia-smi 是否可用"""
    print("=" * 60)
    print("1. 检查 nvidia-smi 命令")
    print("=" * 60)
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✓ nvidia-smi 可用")
            print(result.stdout)
            return True
        else:
            print("✗ nvidia-smi 返回错误:")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("✗ nvidia-smi 命令未找到")
        print("  可能原因: NVIDIA驱动未安装或未添加到PATH")
        return False
    except Exception as e:
        print(f"✗ 执行 nvidia-smi 时出错: {e}")
        return False

def check_pytorch_cuda():
    """检查 PyTorch CUDA 是否可用"""
    print("\n" + "=" * 60)
    print("2. 检查 PyTorch CUDA 支持")
    print("=" * 60)
    try:
        import torch
        print(f"PyTorch 版本: {torch.__version__}")
        print(f"CUDA 是否可用: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            print(f"CUDA 版本: {torch.version.cuda}")
            print(f"cuDNN 版本: {torch.backends.cudnn.version()}")
            print(f"GPU 数量: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
            return True
        else:
            print("✗ PyTorch CUDA 不可用")
            return False
    except ImportError:
        print("✗ PyTorch 未安装")
        return False
    except Exception as e:
        print(f"✗ 检查 PyTorch CUDA 时出错: {e}")
        return False

def check_environment():
    """检查环境变量"""
    print("\n" + "=" * 60)
    print("3. 检查相关环境变量")
    print("=" * 60)
    import os
    
    cuda_vars = [
        "CUDA_PATH",
        "CUDA_HOME",
        "CUDA_VISIBLE_DEVICES",
        "PATH"
    ]
    
    for var in cuda_vars:
        value = os.environ.get(var, "未设置")
        if var == "PATH":
            # 只显示包含cuda的路径
            paths = value.split(os.pathsep)
            cuda_paths = [p for p in paths if "cuda" in p.lower()]
            if cuda_paths:
                print(f"{var} 中的CUDA路径:")
                for p in cuda_paths:
                    print(f"  - {p}")
            else:
                print(f"{var}: 未找到CUDA相关路径")
        else:
            print(f"{var}: {value}")

def main():
    print("GPU 环境检查工具")
    print("=" * 60)
    
    nvidia_ok = check_nvidia_smi()
    pytorch_ok = check_pytorch_cuda()
    check_environment()
    
    print("\n" + "=" * 60)
    print("检查结果总结")
    print("=" * 60)
    
    if nvidia_ok and pytorch_ok:
        print("✓ GPU 环境正常，可以使用CUDA")
        return 0
    elif not nvidia_ok:
        print("✗ NVIDIA驱动问题")
        print("  建议:")
        print("  1. 确认是否安装了NVIDIA显卡驱动")
        print("  2. 确认当前环境是否有GPU访问权限（如WSL2、Docker等）")
        print("  3. 如果是远程服务器，确认GPU是否被正确分配")
        return 1
    elif not pytorch_ok:
        print("✗ PyTorch CUDA 问题")
        print("  建议:")
        print("  1. 重新安装支持CUDA的PyTorch版本")
        print("     命令: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        print("  2. 确认PyTorch版本与CUDA版本匹配")
        return 1
    else:
        print("✗ 未知问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
