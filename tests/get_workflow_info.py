"""
获取工作流详细信息
"""
import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_KEY, BASE_URL, HEADERS

def get_workflow_detail(workflow_id):
    """获取工作流详情"""
    url = f"{BASE_URL}/workflow/openapi/detail"
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        print(f"状态码: {resp.status_code}")
        print(f"响应内容: {resp.text[:2000]}")
        result = resp.json()
        print(f"\n工作流 {workflow_id} 详情:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取工作流详情失败: {e}")
        return None

def get_workflow_json(workflow_id):
    """获取工作流JSON - 使用正确的API接口"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        print(f"\n状态码: {resp.status_code}")
        print(f"响应内容前2000字符: {resp.text[:2000]}")
        result = resp.json()
        print(f"\n工作流 {workflow_id} JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"获取工作流JSON失败: {e}")
        return None

if __name__ == "__main__":
    workflow_id = "2024401195896410114"
    print("=" * 60)
    print(f"获取工作流 {workflow_id} 信息")
    print("=" * 60)
    
    # 获取工作流详情
    detail = get_workflow_detail(workflow_id)
    
    # 获取工作流JSON
    workflow_json = get_workflow_json(workflow_id)
