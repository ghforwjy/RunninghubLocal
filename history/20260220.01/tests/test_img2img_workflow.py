"""
RunningHub 图生图工作流测试
工作流: Anima图生图一键洗图生成动漫
工作流ID: 2071268016815824897

测试流程:
1. 获取工作流JSON结构，了解输入参数
2. 上传本地图片
3. 调用图生图API
4. 下载输出图片到本地
"""

import requests
import json
import time
import os
from pathlib import Path

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2071268016815824897"  # Anima图生图工作流
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
        print("=" * 50)
        print("工作流JSON结构:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取工作流JSON失败: {str(e)}")
        return None


def upload_image(image_path: Path):
    """
    上传图片到RunningHub
    
    根据API文档，图生图需要先上传文件获取文件标识
    """
    print(f"\n准备上传图片: {image_path}")
    
    # 首先尝试使用文件上传接口
    upload_url = f"{BASE_URL}/api/openapi/upload"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/png')}
            data = {'apiKey': API_KEY}
            
            resp = requests.post(
                upload_url, 
                data=data,
                files=files,
                headers={"Authorization": f"Bearer {API_KEY}"}
            )
            resp.raise_for_status()
            result = resp.json()
            print(f"上传结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
    except Exception as e:
        print(f"上传图片失败: {str(e)}")
        return None


def create_img2img_task(image_filename: str):
    """
    创建图生图任务
    
    对于图生图工作流，需要在nodeInfoList中指定图片参数
    """
    url = f"{BASE_URL}/task/openapi/create"
    
    # 根据工作流结构，需要找到LoadImage节点
    # 通常图生图工作流会有一个LoadImage节点来接收输入图片
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": [
            {
                "nodeId": "1",  # 假设LoadImage节点的ID是1
                "fieldName": "image",
                "fieldValue": image_filename
            }
        ]
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 50)
        print("创建图生图任务结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"创建任务失败: {str(e)}")
        return None


def query_task_status(task_id: str):
    """查询任务状态"""
    url = f"{BASE_URL}/task/openapi/status"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"查询状态失败: {str(e)}")
        return None


def get_task_outputs(task_id: str):
    """获取任务输出结果"""
    url = f"{BASE_URL}/task/openapi/outputs"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"获取输出失败: {str(e)}")
        return None


def download_image(url: str, output_path: Path):
    """下载图片到本地"""
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(resp.content)
        
        print(f"✅ 图片已保存: {output_path}")
        return True
    except Exception as e:
        print(f"❌ 下载图片失败: {str(e)}")
        return False


def wait_for_task_and_download(task_id: str, max_retries: int = 30, interval: int = 10):
    """等待任务完成并下载输出图片"""
    print(f"\n开始轮询任务状态 (taskId: {task_id})...")
    
    for i in range(max_retries):
        status_result = query_task_status(task_id)
        
        if status_result and status_result.get("code") == 0:
            status = status_result.get("data")
            print(f"[{i+1}/{max_retries}] 任务状态: {status}")
            
            if status == "SUCCESS":
                print("✅ 任务执行成功！")
                outputs_result = get_task_outputs(task_id)
                
                if outputs_result and outputs_result.get("code") == 0:
                    outputs = outputs_result.get("data", [])
                    downloaded_files = []
                    
                    for idx, item in enumerate(outputs):
                        file_url = item.get("fileUrl")
                        file_type = item.get("fileType", "png")
                        
                        if file_url:
                            output_filename = f"output_{task_id}_{idx+1}.{file_type}"
                            output_path = OUTPUT_DIR / output_filename
                            
                            if download_image(file_url, output_path):
                                downloaded_files.append(output_path)
                    
                    return downloaded_files
                
                return None
                
            elif status == "FAILED":
                print("❌ 任务执行失败！")
                return None
            elif status == "QUEUED":
                print("⏳ 任务正在排队中...")
            elif status == "RUNNING":
                print("🔄 任务正在运行中...")
        
        time.sleep(interval)
    
    print("⏰ 轮询超时")
    return None


def main():
    """主函数"""
    print("=" * 60)
    print("RunningHub 图生图工作流测试")
    print("=" * 60)
    
    # 1. 获取工作流JSON结构
    print("\n【步骤1】获取工作流JSON结构...")
    workflow_json = get_workflow_json()
    
    # 2. 选择输入图片
    print("\n【步骤2】选择输入图片...")
    input_images = list(INPUT_DIR.glob("*.png"))
    if not input_images:
        print(f"❌ 未在 {INPUT_DIR} 找到PNG图片")
        return
    
    input_image = input_images[0]
    print(f"✅ 选择图片: {input_image.name}")
    
    # 3. 上传图片
    print("\n【步骤3】上传图片...")
    upload_result = upload_image(input_image)
    
    if upload_result and upload_result.get("code") == 0:
        # 获取上传后的文件名
        uploaded_filename = upload_result.get("data", {}).get("fileName")
        if not uploaded_filename:
            # 如果上传接口不返回文件名，直接使用原文件名
            uploaded_filename = input_image.name
        
        print(f"✅ 图片上传成功: {uploaded_filename}")
        
        # 4. 创建图生图任务
        print("\n【步骤4】创建图生图任务...")
        task_result = create_img2img_task(uploaded_filename)
        
        if task_result and task_result.get("code") == 0:
            task_id = task_result["data"]["taskId"]
            print(f"✅ 任务创建成功, taskId: {task_id}")
            
            # 5. 等待任务完成并下载结果
            print("\n【步骤5】等待任务完成并下载结果...")
            downloaded_files = wait_for_task_and_download(task_id)
            
            if downloaded_files:
                print("\n" + "=" * 60)
                print("✅ 图生图任务完成!")
                print(f"输出图片保存位置: {OUTPUT_DIR}")
                print("下载的文件:")
                for f in downloaded_files:
                    print(f"  - {f}")
                print("=" * 60)
            else:
                print("\n❌ 未成功下载输出图片")
        else:
            print(f"❌ 创建任务失败: {task_result}")
    else:
        print(f"❌ 图片上传失败")
        # 尝试直接用文件名创建任务
        print("\n尝试直接使用本地文件名创建任务...")
        task_result = create_img2img_task(input_image.name)
        if task_result and task_result.get("code") == 0:
            task_id = task_result["data"]["taskId"]
            print(f"✅ 任务创建成功, taskId: {task_id}")
            downloaded_files = wait_for_task_and_download(task_id)
            if downloaded_files:
                print("\n✅ 图生图任务完成!")


if __name__ == "__main__":
    main()
