"""
RunningHub 图生图完整测试流程
工作流: 蜜蜂图片换头v1.1
工作流ID: 1843664931653828609

完整流程:
1. 获取工作流JSON结构
2. 上传本地图片
3. 调用图生图API
4. 等待任务完成
5. 下载输出图片到本地
6. 记录经验和问题
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
    """获取工作流JSON结构"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    
    print("\n【步骤1】获取工作流JSON结构...")
    print(f"请求URL: {url}")
    print(f"请求参数: {json.dumps(payload, indent=2)}")
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for