"""
RunningHub 图生图 API 测试 - 最终版本
使用已验证可用的 Z-image-base 工作流 (ID: 2016195556967714818)

测试流程：
1. 获取工作流JSON结构，了解输入参数
2. 上传本地图片到 RunningHub
3. 调用 API 传入图片参数
4. 等待任务完成
5. 下载输出图片到 Output 目录
"""

import requests
import json
import time
import os
from pathlib import Path

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2016195556967714818"  # 已验证可用的 Z-image-base 工作流
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
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        return result
    except Exception as e:
