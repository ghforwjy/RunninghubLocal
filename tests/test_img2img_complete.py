"""
RunningHub 图生图完整测试
目标：上传本地图片 -> 调用图生图API -> 下载输出图片

使用工作流：蜜蜂图片换头v1.1 (ID: 1843664931653828609)
"""

import requests
import json
import time
import base64
from pathlib import Path

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "1843664931653828609"  # 蜜蜂图片换头v1.1
BASE_URL = "https://www.runninghub.cn"
INPUT_DIR = Path("d:/mycode/runninghubLocal/Input")
OUTPUT_DIR = Path("d:/mycode/runninghubLocal/Output")

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def get_workflow_json():
    """获取工作流JSON结构，了解输入参数"""
    url = f"