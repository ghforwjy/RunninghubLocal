"""
RunningHub 图生图简化测试
使用网络图片URL直接测试
"""

import requests
import json
import time
from pathlib import Path

API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2016195556967714818"  # Z-image-base
BASE_URL = "https://www.runninghub.cn"
OUTPUT_DIR = Path("d:/mycode/runninghubLocal/Output")
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 使用一个公开的网络图片作为输入
TEST_IMAGE_URL = "https://rh-images.xiaoyaoyou.com/22533a0de60909a27e0191172a3f9861/output/ComfyUI_00001_bfbku_1771477422.png"


def create_task_with_image(image_url: str):
    """创建图生图任务"""
    url = f"{BASE_URL}/task/openapi/create"
    
    # 根据工作流JSON结构，修改节点6的text字段（正向提示词）
    # 并尝试添加图片输入
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": [
            {
                "nodeId": "6",  # CLIPTextEncode节点 - 正向提示词
                "fieldName": "text",
                "fieldValue": f"a beautiful girl, high quality, masterpiece, based on image: {image_url}"
            }
        ]
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"创建任务失败: {str(e)}")
        return None


def query_task_status(task_id: str):
    """查询任务状态"""
    url = f