#!/usr/bin/env python3
"""将核心脚本拷贝到 Skill 目录"""
import shutil
import os

# 核心脚本列表
scripts = [
    "runninghub_client.py",
    "config_manager.py",
    "config.py"
]

# 目标目录
dest_dir = ".trae/skills/runninghub-api/scripts"

# 创建目标目录
os.makedirs(dest_dir, exist_ok=True)

# 拷贝文件
for file in scripts:
    if os.path.exists(file):
        dest_path = os.path.join(dest_dir, file)
        shutil.copy2(file, dest_path)
        print(f"✅ 已拷贝: {file} -> {dest_path}")
    else:
        print(f"❌ 文件不存在: {file}")

print("\n完成!")
