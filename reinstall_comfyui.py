import os
import shutil
import subprocess
import time

def delete_directory(path):
    """删除目录"""
    if os.path.exists(path):
        print(f"正在删除目录: {path}")
        try:
            shutil.rmtree(path)
            print(f"目录删除成功: {path}")
            return True
        except Exception as e:
            print(f"删除目录失败: {e}")
            return False
    else:
        print(f"目录不存在: {path}")
        return True

def extract_7z(archive_path, destination_path):
    """使用7z解压文件"""
    print(f"开始解压: {archive_path}")
    print(f"目标路径: {destination_path}")
    
    # 构建7z命令
    sevenzip_path = "C:/Users/junyu/scoop/shims/7z.exe"
    cmd = [sevenzip_path, "x", archive_path, f"-o{destination_path}"]
    
    try:
        # 执行7z命令
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="D:")
        print(f"解压命令返回码: {result.returncode}")
        
        if result.returncode == 0:
            print("解压成功！")
            return True
        else:
            print(f"解压失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"解压过程异常: {e}")
        return False

def check_run_scripts():
    """检查运行脚本是否存在"""
    base_dir = "D:/ComfyUI_windows_portable"
    
    # 检查run_cpu.bat
    run_cpu_path = os.path.join(base_dir, "run_cpu.bat")
    if os.path.exists(run_cpu_path):
        print(f"找到run_cpu.bat: {run_cpu_path}")
    else:
        print(f"未找到run_cpu.bat: {run_cpu_path}")
        
    # 检查run_nvidia_gpu.bat
    run_gpu_path = os.path.join(base_dir, "run_nvidia_gpu.bat")
    if os.path.exists(run_gpu_path):
        print(f"找到run_nvidia_gpu.bat: {run_gpu_path}")
    else:
        print(f"未找到run_nvidia_gpu.bat: {run_gpu_path}")

def main():
    """主函数"""
    print("=== ComfyUI 重新安装脚本 ===")
    
    # 定义路径
    archive_path = "D:/ComfyUI_windows_portable_nvidia_cu118_or_cpu.7z"
    destination_path = "D:/"
    comfyui_dir = "D:/ComfyUI_windows_portable"
    
    # 1. 删除现有目录
    delete_success = delete_directory(comfyui_dir)
    if not delete_success:
        print("警告: 删除目录失败，可能会导致解压覆盖问题")
    
    # 2. 解压文件
    extract_success = extract_7z(archive_path, destination_path)
    if not extract_success:
        print("错误: 解压失败，安装中止")
        return
    
    # 3. 检查解压结果
    print("\n=== 检查解压结果 ===")
    if os.path.exists(comfyui_dir):
        print(f"ComfyUI目录创建成功: {comfyui_dir}")
        print("目录内容:")
        for item in os.listdir(comfyui_dir)[:10]:
            print(f"  - {item}")
        
        # 检查运行脚本
        check_run_scripts()
    else:
        print(f"错误: ComfyUI目录未创建: {comfyui_dir}")

if __name__ == "__main__":
    main()
