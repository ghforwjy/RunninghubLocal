"""
RunningHub API 测试脚本
测试工作流: Z-image-base (ID: 2016195556967714818)
API Key: acf7d42aedee45dfa8b78ee43eec82a9
"""

import requests
import json
import time

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2016195556967714818"
BASE_URL = "https://www.runninghub.cn"

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def get_account_status():
    """获取账户信息"""
    url = f"{BASE_URL}/uc/openapi/accountStatus"
    payload = {"apikey": API_KEY}
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 50)
        print("账户信息查询结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取账户信息失败: {str(e)}")
        return None


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
        print("=" * 50)
        print("工作流JSON结构:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取工作流JSON失败: {str(e)}")
        return None


def create_task_simple():
    """发起ComfyUI任务（简易版）"""
    url = f"{BASE_URL}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 50)
        print("发起任务结果(简易版):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"发起任务失败: {str(e)}")
        return None


def create_task_advanced(node_info_list):
    """发起ComfyUI任务（高级版）"""
    url = f"{BASE_URL}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": node_info_list
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 50)
        print("发起任务结果(高级版):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"发起任务失败: {str(e)}")
        return None


def query_task_status(task_id):
    """查询任务状态"""
    url = f"{BASE_URL}/task/openapi/status"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 50)
        print(f"任务状态查询结果 (taskId: {task_id}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"查询任务状态失败: {str(e)}")
        return None


def get_task_outputs(task_id):
    """获取任务生成结果"""
    url = f"{BASE_URL}/task/openapi/outputs"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload)
        resp.raise_for_status()
        result = resp.json()
        print("=" * 50)
        print(f"任务结果查询 (taskId: {task_id}):")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取任务结果失败: {str(e)}")
        return None


def wait_for_task_completion(task_id, max_retries=30, interval=10):
    """轮询等待任务完成"""
    print(f"\n开始轮询任务状态 (taskId: {task_id})...")
    
    for i in range(max_retries):
        status_result = query_task_status(task_id)
        
        if status_result and status_result.get("code") == 0:
            status = status_result.get("data")
            print(f"[{i+1}/{max_retries}] 任务状态: {status}")
            
            if status == "SUCCESS":
                print("任务执行成功！")
                return get_task_outputs(task_id)
            elif status == "FAILED":
                print("任务执行失败！")
                return None
            elif status == "QUEUED":
                print("任务正在排队中...")
            elif status == "RUNNING":
                print("任务正在运行中...")
        
        time.sleep(interval)
    
    print("轮询超时，任务可能仍在执行中")
    return None


if __name__ == "__main__":
    print("=" * 50)
    print("RunningHub API 测试开始")
    print(f"工作流ID: {WORKFLOW_ID}")
    print("=" * 50)
    
    # 1. 查询账户信息
    account = get_account_status()
    
    # 2. 获取工作流JSON结构
    workflow_json = get_workflow_json()
    
    # 3. 发起简易任务
    print("\n" + "=" * 50)
    print("测试1: 发起简易任务（不修改参数）")
    task_result = create_task_simple()
    
    if task_result and task_result.get("code") == 0:
        data = task_result.get("data", {})
        task_id = data.get("taskId")
        task_status = data.get("taskStatus")
        
        print(f"\n任务创建成功!")
        print(f"Task ID: {task_id}")
        print(f"Task Status: {task_status}")
        print(f"WebSocket URL: {data.get('netWssUrl')}")
        
        # 4. 等待任务完成并获取结果
        if task_id:
            outputs = wait_for_task_completion(task_id)
            if outputs:
                print("\n" + "=" * 50)
                print("最终任务结果:")
                print(json.dumps(outputs, indent=2, ensure_ascii=False))
    else:
        print(f"\n任务创建失败!")
        if task_result:
            print(f"错误码: {task_result.get('code')}")
            print(f"错误信息: {task_result.get('msg')}")
    
    print("\n" + "=" * 50)
    print("RunningHub API 测试结束")
    print("=" * 50)
