"""
RunningHub 图生图 API 测试 - 最终版
工作流: 风格迁移转化 • 灵感造像师
工作流ID: 2014552598229032961

测试流程:
1. 获取工作流JSON结构，了解输入参数
2. 上传本地图片到 RunningHub
3. 调用图生图 API
4. 等待任务完成
5. 下载输出图片到 Output 目录
"""

import requests
import json
import time
from pathlib import Path

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2014552598229032961"  # 风格迁移转化工作流
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
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 60)
        print("工作流JSON结构:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取工作流JSON失败: {str(e)}")
        return None


def upload_image(image_path: Path):
    """上传图片到RunningHub"""
    print(f"\n准备上传图片: {image_path}")
    
    # 正确的上传接口URL（根据官方文档）
    upload_url = f"{BASE_URL}/task/openapi/upload"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/png')}
            data = {
                'apiKey': API_KEY,
                'fileType': 'input'
            }
            
            # 注意：上传接口只需要Host头，不需要Authorization头
            headers = {
                'Host': 'www.runninghub.cn'
            }
            
            resp = requests.post(
                upload_url, 
                data=data,
                files=files,
                headers=headers
            )
            resp.raise_for_status()
            result = resp.json()
            print(f"上传结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
    except Exception as e:
        print(f"上传图片失败: {str(e)}")
        return None


def create_img2img_task(source_image_filename: str, style_image_filename: str = None):
    """创建图生图任务
    
    根据工作流JSON分析:
    - 节点 21: LoadImage - 原图输入 (要转换风格的图片)
    - 节点 24: LoadImage - 风格参考图输入 (要提取风格的图片)
    """
    url = f"{BASE_URL}/task/openapi/create"
    
    # 构建nodeInfoList
    node_info_list = [
        {
            "nodeId": "21",  # 原图输入节点
            "fieldName": "image",
            "fieldValue": source_image_filename
        }
    ]
    
    # 如果提供了风格参考图，也一并设置
    if style_image_filename:
        node_info_list.append({
            "nodeId": "24",  # 风格参考图输入节点
            "fieldName": "image",
            "fieldValue": style_image_filename
        })
    
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": node_info_list
    }
    
    print(f"\n创建任务参数:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 60)
        print("创建任务结果:")
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
    print("RunningHub 图生图 API 测试")
    print(f"工作流ID: {WORKFLOW_ID}")
    print("=" * 60)
    
    # 1. 获取工作流JSON结构
    print("\n【步骤1】获取工作流JSON结构...")
    workflow_json = get_workflow_json()
    
    if not workflow_json or workflow_json.get("code") != 0:
        print(f"❌ 获取工作流JSON失败: {workflow_json}")
        return
    
    print("✅ 工作流JSON获取成功")
    
    # 2. 选择输入图片
    print("\n【步骤2】选择输入图片...")
    input_images = list(INPUT_DIR.glob("*.png"))
    if len(input_images) < 1:
        print(f"❌ 未在 {INPUT_DIR} 找到PNG图片")
        return
    
    # 选择第一张作为原图，第二张作为风格参考图（如果有）
    source_image = input_images[0]
    style_image = input_images[1] if len(input_images) > 1 else input_images[0]  # 如果没有第二张，用同一张
    
    print(f"✅ 选择原图: {source_image.name}")
    print(f"✅ 选择风格参考图: {style_image.name}")
    
    # 3. 上传原图
    print("\n【步骤3】上传原图到RunningHub...")
    source_upload_result = upload_image(source_image)
    
    if not source_upload_result or source_upload_result.get("code") != 0:
        print(f"❌ 原图上传失败: {source_upload_result}")
        return
    
    source_filename = source_upload_result.get("data", {}).get("fileName")
    print(f"✅ 原图上传成功: {source_filename}")
    
    # 4. 上传风格参考图
    print("\n【步骤4】上传风格参考图到RunningHub...")
    style_upload_result = upload_image(style_image)
    
    if not style_upload_result or style_upload_result.get("code") != 0:
        print(f"❌ 风格参考图上传失败: {style_upload_result}")
        return
    
    style_filename = style_upload_result.get("data", {}).get("fileName")
    print(f"✅ 风格参考图上传成功: {style_filename}")
    
    # 5. 创建图生图任务
    print("\n【步骤5】创建图生图任务...")
    task_result = create_img2img_task(source_filename, style_filename)
    
    if not task_result or task_result.get("code") != 0:
        print(f"❌ 创建任务失败: {task_result}")
        return
    
    task_id = task_result["data"]["taskId"]
    print(f"✅ 任务创建成功, taskId: {task_id}")

    # 6. 等待任务完成并下载结果
    print("\n【步骤6】等待任务完成并下载结果...")
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


if __name__ == "__main__":
    main()
