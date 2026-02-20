#!/usr/bin/env python3
"""
复制工作流文件到ComfyUI目录的脚本
由于权限限制，需要用户手动运行此脚本
"""
import shutil
import os

# 源文件路径
source = r"D:\mycode\runninghubLocal\workflows\RunningHub_改变动作_Latent解码版.json"

# 目标路径（请根据你的ComfyUI安装位置修改）
dest = r"D:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\RunningHub_改变动作_Latent解码版.json"

# 检查源文件是否存在
if not os.path.exists(source):
    print(f"❌ 源文件不存在: {source}")
    exit(1)

print(f"📁 源文件: {source}")
print(f"📂 目标路径: {dest}")

try:
    # 复制文件
    shutil.copy2(source, dest)
    print("✅ 复制成功!")
    print(f"📝 工作流文件已复制到: {dest}")
    print("\n💡 使用说明:")
    print("1. 启动ComfyUI")
    print("2. 在ComfyUI中加载工作流: RunningHub_改变动作_Latent解码版")
    print("3. 确保已下载VAE模型: qwen_image_vae.safetensors")
    print("4. 放入目录: ComfyUI/models/vae/")
except Exception as e:
    print(f"❌ 复制失败: {e}")
    print("\n💡 请手动复制文件:")
    print(f"从: {source}")
    print(f"到: {dest}")
