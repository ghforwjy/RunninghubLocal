#!/usr/bin/env python3
"""将 MD 文档拷贝到 Skill 目录"""
import shutil
import os

# 源文件列表
source_files = [
    "RunningHub_API文档.md",
    "RunningHub_API_经验Q&A.md",
    "RunningHub_API_调用指南.md",
    "RunningHub_API_测试总结.md",
    "init.md"
]

# 目标目录
dest_dir = ".trae/skills/runninghub-api/docs"

# 创建目标目录
os.makedirs(dest_dir, exist_ok=True)

# 拷贝文件
for file in source_files:
    if os.path.exists(file):
        dest_path = os.path.join(dest_dir, file)
        shutil.copy2(file, dest_path)
        print(f"✅ 已拷贝: {file} -> {dest_path}")
    else:
        print(f"❌ 文件不存在: {file}")

print("\n完成!")
