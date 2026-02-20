"""
测试工作流节点配置
尝试不同的节点ID组合
"""
import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_KEY, BASE_URL, HEADERS

def test_create_task(workflow_id, node_id, field_name, file_name):
    """测试创建任务"""
    url = f"{BASE_URL}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id,
        "nodeInfoList": [
            {
                "nodeId": node_id,
                "fieldName": field_name,
                "fieldValue": file_name
            }
        ]
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()
        return result
    except Exception as e:
        return {"code": -1, "msg": str(e)}

def main():
    workflow_id = "2024401195896410114"
    file_name = "api/test_video.mp4"
    
    # 常见的视频输入节点配置
    test_configs = [
        {"nodeId": "1", "fieldName": "video"},
        {"nodeId": "2", "fieldName": "video"},
        {"nodeId": "3", "fieldName": "video"},
        {"nodeId": "5", "fieldName": "video"},
        {"nodeId": "10", "fieldName": "video"},
        {"nodeId": "11", "fieldName": "video"},
        {"nodeId": "12", "fieldName": "video"},
        {"nodeId": "15", "fieldName": "video"},
        {"nodeId": "20", "fieldName": "video"},
        {"nodeId": "21", "fieldName": "video"},
        {"nodeId": "205", "fieldName": "video"},
        {"nodeId": "1", "fieldName": "input"},
        {"nodeId": "2", "fieldName": "input"},
        {"nodeId": "3", "fieldName": "input"},
        {"nodeId": "1", "fieldName": "file"},
        {"nodeId": "2", "fieldName": "file"},
        {"nodeId": "3", "fieldName": "file"},
    ]
    
    print("=" * 60)
    print(f"测试工作流 {workflow_id} 的节点配置")
    print("=" * 60)
    
    for config in test_configs:
        node_id = config["nodeId"]
        field_name = config["fieldName"]
        print(f"\n测试: nodeId={node_id}, fieldName={field_name}")
        
        result = test_create_task(workflow_id, node_id, field_name, file_name)
        print(f"结果: {result}")
        
        if result.get('code') == 0:
            print(f"✅ 成功! 正确的节点配置: nodeId={node_id}, fieldName={field_name}")
            break
        elif result.get('code') != 803:  # 不是节点信息错误
            print(f"⚠️ 其他错误: {result.get('msg')}")
            break

if __name__ == "__main__":
    main()
