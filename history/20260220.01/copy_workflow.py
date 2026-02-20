import shutil
import os

source = r"D:\mycode\runninghubLocal\workflows\RunningHub_改变动作_使用版.json"
dest = r"D:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\RunningHub_改变动作_使用版.json"

print(f"源文件: {source}")
print(f"目标文件: {dest}")

# 确保目标目录存在
os.makedirs(os.path.dirname(dest), exist_ok=True)

# 复制文件
shutil.copy2(source, dest)
print("复制成功!")

# 验证
if os.path.exists(dest):
    size = os.path.getsize(dest)
    print(f"文件大小: {size} 字节")
