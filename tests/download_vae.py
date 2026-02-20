#!/usr/bin/env python3
"""
下载 qwen_image_vae.safetensors VAE模型
"""
import requests
import os
from pathlib import Path

# VAE模型下载地址
VAE_URL = "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors"

# 本地保存路径
VAE_DIR = Path("D:/ComfyUI_windows_portable/ComfyUI/models/vae")
VAE_FILENAME = "qwen_image_vae.safetensors"
VAE_PATH = VAE_DIR / VAE_FILENAME

def download_vae():
    """下载VAE模型"""
    print("=" * 60)
    print("开始下载 qwen_image_vae.safetensors")
    print("=" * 60)
    
    # 检查目录是否存在
    if not VAE_DIR.exists():
        print(f"❌ VAE目录不存在: {VAE_DIR}")
        print("请确认ComfyUI安装路径正确")
        return False
    
    # 检查文件是否已存在
    if VAE_PATH.exists():
        file_size = VAE_PATH.stat().st_size / (1024 * 1024)  # MB
        print(f"⚠️ 文件已存在: {VAE_PATH}")
        print(f"   文件大小: {file_size:.2f} MB")
        
        # 检查文件大小是否合理（VAE通常在300MB-1GB之间）
        if file_size > 100:  # 大于100MB认为是完整的
            print("✅ 文件看起来是完整的，跳过下载")
            return True
        else:
            print("⚠️ 文件可能不完整，重新下载...")
    
    # 开始下载
    print(f"\n📥 下载地址: {VAE_URL}")
    print(f"📂 保存路径: {VAE_PATH}")
    print()
    
    try:
        # 使用流式下载
        response = requests.get(VAE_URL, stream=True, timeout=300)
        response.raise_for_status()
        
        # 获取文件总大小
        total_size = int(response.headers.get('content-length', 0))
        if total_size > 0:
            print(f"📦 文件总大小: {total_size / (1024 * 1024):.2f} MB")
        
        # 下载并保存
        downloaded = 0
        chunk_size = 8192  # 8KB
        
        with open(VAE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 每10MB打印一次进度
                    if downloaded % (10 * 1024 * 1024) < chunk_size:
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"   已下载: {downloaded / (1024 * 1024):.2f} MB ({percent:.1f}%)")
                        else:
                            print(f"   已下载: {downloaded / (1024 * 1024):.2f} MB")
        
        # 验证下载结果
        final_size = VAE_PATH.stat().st_size / (1024 * 1024)
        print(f"\n✅ 下载完成!")
        print(f"   文件大小: {final_size:.2f} MB")
        print(f"   保存位置: {VAE_PATH}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 下载失败: {e}")
        # 删除不完整的文件
        if VAE_PATH.exists():
            VAE_PATH.unlink()
            print("   已删除不完整的文件")
        return False
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return False

if __name__ == "__main__":
    success = download_vae()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ VAE模型准备就绪!")
        print("=" * 60)
        print("\n💡 现在你可以:")
        print("1. 启动ComfyUI")
        print("2. 加载工作流: RunningHub_改变动作_Latent解码版")
        print("3. 运行工作流，云端生成潜空间后本地自动解码")
    else:
        print("❌ VAE模型下载失败")
        print("=" * 60)
        print("\n💡 请手动下载:")
        print(f"   从: {VAE_URL}")
        print(f"   到: {VAE_PATH}")
