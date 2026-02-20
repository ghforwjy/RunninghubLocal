#!/usr/bin/env python3
"""将 config.py 恢复到项目根目录"""
import shutil
import os

source = ".trae/skills/runninghub-api/scripts/config.py"
dest = "./config.py"

if os.path.exists(source):
    shutil.copy2(source, dest)
    print(f"✅ 已恢复: {source} -> {dest}")
else:
    print(f"❌ 源文件不存在: {source}")
