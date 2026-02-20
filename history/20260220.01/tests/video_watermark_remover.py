"""
视频去水印批量处理程序
支持自动识别横屏/竖屏视频并选择对应工作流
并行处理多个视频

工作流配置:
- 横版(16:9): 2020848647759466498
- 竖版(9:16): 需要用户补充
"""

import requests
import json
import time
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
import cv2

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
BASE_URL = "https://www.runninghub.cn"
INPUT_DIR = Path("d:/mycode/runninghubLocal/Input")
OUTPUT_DIR = Path("d:/mycode/runninghubLocal/Output")

# 工作流配置
WORKFLOW_HORIZONTAL = "2020848647759466498"  # 横版16:9
WORKFLOW_VERTICAL = "2020848647759466498"    # 竖版9:16 (暂时用同一个，需要用户确认)

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def get_video_orientation(video_path: Path) -> str:
    """
    判断视频是横屏还是竖屏
    返回: 'horizontal' (横屏16:9) 或 'vertical' (竖屏9:16)
    """
    try:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"无法打开视频: {video_path}")
            return "horizontal"  # 默认横屏
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        aspect_ratio = width / height
        
        print(f"视频 {video_path.name}: 分辨率 {width}x{height}, 宽高比 {aspect_ratio:.2f}")
        
        # 判断横竖屏
        if aspect_ratio < 1:  # 宽高比小于1，是竖屏
            return "vertical"
        else:  # 宽高比大于等于1，是横屏
            return "horizontal"
            
    except Exception as e:
        print(f"判断视频方向失败 {video_path}: {str(e)}")
        return "horizontal"  # 默认横屏


def upload_video(video_path: Path) -> Optional[str]:
    """
    上传视频到RunningHub
    返回: 上传后的文件名，失败返回None
    """
    print(f"\n上传视频: {video_path.name}")
    upload_url = f"{BASE_URL}/task/openapi/upload"
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (video_path.name, f, 'video/mp4')}
            data = {
                'apiKey': API_KEY,
                'fileType': 'input'
            }
            headers = {'Host': 'www.runninghub.cn'}
            
            resp = requests.post(upload_url, data=data, files=files, headers=headers, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            
            if result.get("code") == 0:
                filename = result.get("data", {}).get("fileName")
                print(f"✅ 上传成功: {filename}")
                return filename
            else:
                print(f"❌ 上传失败: {result}")
                return None
    except Exception as e:
        print(f"❌ 上传异常: {str(e)}")
        return None


def create_video_task(workflow_id: str, video_filename: str) -> Optional[str]:
    """
    创建视频去水印任务
    返回: task_id，失败返回None
    """
    url = f"{BASE_URL}/task/openapi/create"
    
    # 获取工作流JSON，分析视频输入节点
    workflow_json = get_workflow_json(workflow_id)
    if not workflow_json or workflow_json.get("code") != 0:
        print(f"❌ 获取工作流JSON失败")
        return None
    
    # 分析工作流，找到视频输入节点
    # 通常视频输入节点是LoadVideo或类似类型
    node_info_list = analyze_video_input_nodes(workflow_json, video_filename)
    
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id,
        "nodeInfoList": node_info_list
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            task_id = result["data"]["taskId"]
