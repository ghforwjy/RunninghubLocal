"""
RunningHub 视频去水印测试 - 并行处理3个视频
根据视频横竖屏自动选择对应工作流

工作流配置:
- 横版(16:9): 2020848647759466498
- 竖版(9:16): 2020836153632493569
"""

import requests
import json
import time
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any, Tuple

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
BASE_URL = "https://www.runninghub.cn"
INPUT_DIR = Path("d:/mycode/runninghubLocal/Input")
OUTPUT_DIR = Path("d:/mycode/runninghubLocal/Output")

# 工作流ID配置
WORKFLOW_IDS = {
    "landscape": "2020848647759466498",  # 横版 16:9
    "portrait": "2020836153632493569",   # 竖版 9:16
}

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
    
    Returns:
        "landscape" - 横屏 (宽度 > 高度)
        "portrait" - 竖屏 (高度 > 宽度)
    """
    try:
        # 使用ffprobe获取视频信息
        cmd = [
            'ffprobe', '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            dimensions = result.stdout.strip().split('x')
            if len(dimensions) == 2:
                width = int(dimensions[0])
                height = int(dimensions[1])
                
                if width > height:
                    return "landscape"
                else:
                    return "portrait"
        
        # 如果ffprobe失败，尝试使用文件大小作为启发式判断
        # 通常竖屏视频在社交媒体更常见，这里默认横屏
        print(f"[分析] 无法获取视频尺寸，默认使用横屏")
        return "landscape"
        
    except Exception as e:
        print(f"[分析] 判断视频方向失败 {video_path}: {e}")
        return "landscape"  # 默认横屏


def upload_video(video_path: Path) -> Optional[str]:
    """
    上传视频到RunningHub
    
    Returns:
        上传成功返回fileName，失败返回None
    """
    print(f"[上传] 开始上传视频: {video_path.name}")
    
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
                file_name = result.get("data", {}).get("fileName")
                print(f"[上传] ✅ 成功: {file_name}")
                return file_name
            else:
                print(f"[上传] ❌ 失败: {result}")
                return None
    except Exception as e:
        print(f"[上传] ❌ 异常: {e}")
        return None


def create_watermark_removal_task(video_filename: str, workflow_id: str) -> Optional[Dict]:
    """
    创建视频去水印任务
    
    Args:
        video_filename: 上传后的视频文件名
        workflow_id: 工作流ID
        
    Returns:
        任务创建结果
    """
    print(f"[任务] 创建去水印任务, 工作流: {workflow_id}")
    
    url = f"{BASE_URL}/task/openapi/create"
    
    # 先获取工作流JSON，找到视频输入节点
    workflow_json = get_workflow_json(workflow_id)
    if not workflow_json or workflow_json.get("code") != 0:
        print(f"[任务] ❌ 获取工作流JSON失败")
        return None
    
    # 查找LoadVideo节点
    prompt = workflow_json.get("data", {}).get("prompt", "{}")
    if isinstance(prompt, str):
        prompt = json.loads(prompt)
    
    video_node_id = None
    for node_id, node_data in prompt.items():
        if node_data.get("class_type") == "LoadVideo":
            video_node_id = node_id
            break
    
    if not video_node_id:
        # 如果没找到LoadVideo，尝试找其他视频相关节点
        for node_id, node_data in prompt.items():
            class_type = node_data.get("class_type", "")
            if "Video" in class_type or "video" in class_type:
                video_node_id = node_id
                break
    
    if not video_node_id:
        # 默认使用节点1
        video_node_id = "1"
        print(f"[任务] ⚠️ 未找到视频节点，使用默认节点: {video_node_id}")
    else:
        print(f"[任务] ✅ 找到视频节点: {video_node_id}")
    
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id,
        "nodeInfoList": [
            {
                "nodeId": video_node_id,
                "fieldName": "video",
                "fieldValue": video_filename
            }
        ]
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            task_id = result["data"]["taskId"]
            print(f"[任务] ✅ 创建成功, taskId: {task_id}")
            return result
        else:
            print(f"[任务] ❌ 创建失败: {result}")
            return None
    except Exception as e:
        print(f"[任务] ❌ 异常: {e}")
        return None


def get_workflow_json(workflow_id: str) -> Optional[Dict]:
    """获取工作流JSON结构"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[JSON] ❌ 获取失败: {e}")
        return None


def query_task_status(task_id: str) -> Optional[str]:
    """查询任务状态"""
    url = f"{BASE_URL}/task/openapi/status"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            return result.get("data")
        return None
    except Exception as e:
        print(f"[状态] ❌ 查询失败: {e}")
        return None


def get_task_outputs(task_id: str) -> Optional[Dict]:
    """获取任务输出结果"""
    url = f"{BASE_URL}/task/openapi/outputs"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[输出] ❌ 获取失败: {e}")
        return None


def download_file(url: str, output_path: Path) -> bool:
    """下载文件到本地"""
    try:
        resp = requests.get(url, timeout=300)
        resp.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        
        return True
    except Exception as e:
        print(f"[下载] ❌ 失败: {e}")
        return False


def wait_for_task_and_download(task_id: str, video_name: str, max_retries: int = 60, interval: int = 10) -> Tuple[bool, list]:
    """
    等待任务完成并下载结果
    
    Returns:
        (是否成功, 下载的文件列表)
    """
    print(f"[等待] 开始轮询任务状态 (taskId: {task_id})...")
    
    downloaded_files = []
    
    for i in range(max_retries):
        status = query_task_status(task_id)
        
        if status:
            print(f"[等待] [{i+1}/{max_retries}] 状态: {status}")
            
            if status == "SUCCESS":
                print(f"[等待] ✅ 任务完成!")
                
                # 获取输出结果
                outputs_result = get_task_outputs(task_id)
                if outputs_result and outputs_result.get("code") == 0:
                    outputs = outputs_result.get("data", [])
                    
                    for idx, item in enumerate(outputs):
                        file_url = item.get("fileUrl")
                        file_type = item.get("fileType", "mp4")
                        
                        if file_url:
                            output_filename = f"{video_name}_no_watermark_{idx+1}.{file_type}"
                            output_path = OUTPUT_DIR / output_filename
                            
                            print(f"[下载] 下载文件 {idx+1}: {output_filename}")
                            if download_file(file_url, output_path):
                                downloaded_files.append(output_path)
                                print(f"[下载] ✅ 成功: {output_path}")
                            else:
                                print(f"[下载] ❌ 失败: {file_url}")
                    
                    return True, downloaded_files
                else:
                    print(f"[输出] ❌ 获取输出失败")
                    return False, []
                    
            elif status == "FAILED":
                print(f"[等待] ❌ 任务失败!")
                return False, []
        
        time.sleep(interval)
    
    print(f"[等待] ⏰ 超时!")
    return False, []


def process_single_video(video_path: Path) -> Tuple[bool, list]:
    """
    处理单个视频的完整流程
    
    Returns:
        (是否成功, 下载的文件列表)
    """
    print(f"\n{'='*60}")
    print(f"[处理] 开始处理视频: {video_path.name}")
    print(f"{'='*60}")
    
    # 1. 判断视频方向
    orientation = get_video_orientation(video_path)
    workflow_id = WORKFLOW_IDS.get(orientation, WORKFLOW_IDS["landscape"])
    
    print(f"[分析] 视频方向: {orientation}")
    print(f"[分析] 使用工作流: {workflow_id}")
    
    # 2. 上传视频
    video_filename = upload_video(video_path)
    if not video_filename:
        print(f"[处理] ❌ 上传失败，跳过")
        return False, []
    
    # 3. 创建任务
    task_result = create_watermark_removal_task(video_filename, workflow_id)
    if not task_result:
        print(f"[处理] ❌ 创建任务失败，跳过")
        return False, []
    
    task_id = task_result["data"]["taskId"]
    
    # 4. 等待任务完成并下载
    success, files = wait_for_task_and_download(task_id, video_path.stem)
    
    if success:
        print(f"[处理] ✅ 完成! 下载 {len(files)} 个文件")
    else:
        print(f"[处理] ❌ 失败!")
    
    return success, files


def main():
    """主函数 - 并行处理3个视频"""
    print("="*60)
    print("RunningHub 视频去水印 - 并行处理")
    print("="*60)
    
    # 获取所有视频文件
    video_files = list(INPUT_DIR.glob("*.mp4"))
    
    if not video_files:
        print("❌ 未找到视频文件")
        return
    
    print(f"\n找到 {len(video_files)} 个视频文件:")
    for v in video_files:
        orientation = get_video_orientation(v)
        print(f"  - {v.name} ({orientation})")
    
    # 并行处理所有视频
    print(f"\n{'='*60}")
    print("开始并行处理...")
    print(f"{'='*60}\n")
    
    results = {
        "success": [],
        "failed": []
    }
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交所有任务
        future_to_video = {
            executor.submit(process_single_video, video_path): video_path 
            for video_path in video_files
        }
        
        # 收集结果
        for future in as_completed(future_to_video):
            video_path = future_to_video[future]
            try:
                success, files = future.result()
                if success:
                    results["success"].append({
                        "video": video_path.name,
                        "files": files
                    })
                else:
                    results["failed"].append(video_path.name)
            except Exception as e:
                print(f"[异常] 处理 {video_path.name} 时出错: {e}")
                results["failed"].append(video_path.name)
    
    # 输出总结
    print(f"\n{'='*60}")
    print("处理完成!")
    print(f"{'='*60}")
    print(f"\n✅ 成功: {len(results['success'])} 个")
    for item in results["success"]:
        print(f"  - {item['video']}")
        for f in item['files']:
            print(f"      → {f.name}")
    
    print(f"\n❌ 失败: {len(results['failed'])} 个")
    for name in results["failed"]:
        print(f"  - {name}")
    
    print(f"\n输出目录: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
