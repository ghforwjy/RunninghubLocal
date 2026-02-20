import os
import json

# 检查工作流目录
workflows_dir = r"D:\ComfyUI_windows_portable\ComfyUI\user\default\workflows"

print(f"检查目录: {workflows_dir}")
print(f"目录存在: {os.path.exists(workflows_dir)}")

if os.path.exists(workflows_dir):
    files = os.listdir(workflows_dir)
    print(f"\n文件数量: {len(files)}")
    for f in files:
        print(f"  - {f}")
else:
    print("\n目录不存在，正在创建...")
    os.makedirs(workflows_dir, exist_ok=True)
    print("目录已创建")
