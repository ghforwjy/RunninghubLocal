"""
测试工作流节点配置 - 更全面的测试
"""
import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_KEY, BASE_URL, HEADERS

def test_create_task(workflow_id, node_id, field_name, field_value, file_name):
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
    
    # 更全面的测试配置
    test_configs = []
    
    # 测试更多节点ID
    for node_id in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", 
                    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                    "100", "101", "102", "103", "104", "105",
                    "200", "201", "202", "203", "204", "205", "206", "207", "208", "209",
                    "210", "211", "212", "213", "214", "215"]:
        for field_name in ["video", "input", "file", "image", "path", "url", "source", "data"]:
            test_configs.append({"nodeId": node_id, "fieldName": field_name})
    
    print("=" * 60)
    print(f"测试工作流 {workflow_id} 的节点配置")
    print("=" * 60)
    
    for config in test_configs:
        node_id = config["nodeId"]
        field_name = config["fieldName"]
        
        result = test_create_task(workflow_id, node_id, field_name, None, file_name)
        
        if result.get('code') == 0:
            print(f"\n✅ 成功! nodeId={node_id}, fieldName={field_name}")
            print(f"结果: {json.dumps(result, indent=2)}")
            return
        elif result.get('code') != 803:  # 不是节点信息错误
            print(f"\n⚠️ 其他错误 (code={result.get('code')}): {result.get('msg')}")
            print(f"nodeId={node_id}, fieldName={field_name}")
    
    print("\n❌ 所有常见节点配置都失败了")
    print("\n尝试简易版API（不带nodeInfoList）...")
    
    # 测试简易版API
    url = f"{BASE_URL}/task/openapi/create"
