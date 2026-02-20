import py7zr
import os

# 定义解压路径
archive_path = "D:/ComfyUI_windows_portable_nvidia_cu118_or_cpu.7z"
destination_path = "D:/"

print(f"开始解压: {archive_path}")
print(f"目标路径: {destination_path}")

try:
    # 使用py7zr解压文件
    with py7zr.SevenZipFile(archive_path, mode='r') as z:
        z.extractall(path=destination_path)
    print("解压完成！")
    
    # 验证解压结果
    if os.path.exists("D:/ComfyUI_windows_portable"):
        print("ComfyUI_windows_portable目录创建成功！")
        # 列出目录内容
        print("目录内容:")
        for item in os.listdir("D:/ComfyUI_windows_portable")[:10]:  # 只显示前10个项目
            print(f"  - {item}")
    else:
        print("警告: ComfyUI_windows_portable目录未创建！")
        
except Exception as e:
    print(f"解压失败: {e}")
