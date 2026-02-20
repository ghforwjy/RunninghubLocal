#!/usr/bin/env python3
"""
修复 PyTorch CUDA 版本不匹配问题的脚本
"""
import subprocess
import sys

def get_cuda_version():
    """获取系统 CUDA 版本"""
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # 解析 CUDA 版本
            for line in result.stdout.split('\n'):
                if "CUDA Version:" in line:
                    # 格式: | NVIDIA-SMI 572.83                 Driver Version: 572.83         CUDA Version: 12.8     |
                    parts = line.split("CUDA Version:")
                    if len(parts) > 1:
                        cuda_version = parts[1].split("|")[0].strip()
                        return cuda_version
