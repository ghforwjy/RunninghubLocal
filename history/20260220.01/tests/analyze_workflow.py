"""
分析工作流JSON，找到视频输入节点
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import API_KEY, BASE_URL, HEADERS
import requests

def get_workflow_json(workflow_id):
    """获取工作流JSON"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id
    }
    
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()
        if result.get('code') == 0:
            return result.get('data', {}).get('prompt', '{}')
        return None
    except Exception as e:
        print(f"获取工作流JSON失败: {e}")
        return None

def analyze_workflow(json_str):
    """分析工作流节点"""
    try:
        workflow = json.loads(json_str)
        print("\n" + "=" * 60)
        print("工作流节点分析")
        print("=" * 60)
        
        # 查找视频加载节点
        video_nodes = []
        for node_id, node_data in workflow.items():
            class_type = node_data.get('class_type', '')
            inputs = node_data.get('inputs', {})
            
            # 查找视频加载相关节点
            if 'Video' in class_type or 'LoadVideo' in class_type:
                print(f"\n节点ID: {node_id}")
                print(f"  类型: {class_type}")
                print(f"  输入参数: {list(inputs.keys())}")
                video_nodes.append({
                    'nodeId': node_id,
                    'classType': class_type,
                    'inputs': inputs
                })
            
            # 查找有video字段的节点
            if 'video' in inputs:
                print(f"\n节点ID: {node_id}")
                print(f"  类型: {class_type}")
                print(f"  video字段: {inputs['video']}")
                video_nodes.append({
                    'nodeId': node_id,
                    'classType': class_type,
                    'fieldName': 'video',
                    'fieldValue': inputs['video']
                })
        
        return video_nodes
    except Exception as e:
        print(f"分析工作流失败: {e}")
        return []

if __name__ == "__main__":
    workflow_id = "2024401195896410114"
    
    print("=" * 60)
    print(f"分析工作流 {workflow_id}")
    print("=" * 60)
    
    # 获取工作流JSON
    json_str = get_workflow_json(workflow_id)
    if json_str:
        # 分析节点
        video_nodes = analyze_workflow(json_str)
        
        print("\n" + "=" * 60)
        print("视频输入节点汇总")
        print("=" * 60)
        for node in video_nodes:
            print(f"\n节点ID: {node.get('nodeId')}")
            print(f"类型: {node.get('classType')}")
            if 'fieldName' in node:
                print(f"字段名: {node.get('fieldName')}")
    else:
        print("无法获取工作流JSON")
