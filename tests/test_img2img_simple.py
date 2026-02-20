"""
RunningHub 图生图测试 - 使用已验证的工作流
工作流: Z-image-base (ID: 2016195556967714818)

测试流程:
1. 获取工作流JSON结构
2. 调用API创建任务
3. 下载输出图片到本地
"""

import requests
import json
import time
from pathlib import Path

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2016195556967714818"  # Z-image-base 工作流
BASE_URL = "https://www.runninghub.cn"
OUTPUT_DIR = Path("d:/mycode/runninghubLocal/Output")

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def get_workflow_json():
    """获取工作流JSON结构"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result =