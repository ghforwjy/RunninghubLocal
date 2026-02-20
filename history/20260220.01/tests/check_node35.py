"""
查看工作流节点35的内容
"""
import json
import sys
sys.path.insert(0, 'd:\\mycode\\runninghubLocal')

from runninghub_client import RunningHubClient
from config import API_KEY

client = RunningHubClient(api_key=API_KEY)

# 获取工作流JSON
workflow_id = "2024540737567727618"
result = client.get_workflow_json(workflow_id)

if result.get("code") == 0:
    workflow_data = result.get("data", {})
    node_info_list = workflow_data.get("nodeInfoList", [])
    
    print("=" * 60)
    print("查找节点35的内容:")
    print("=" * 60)
    
    for node in node_info_list:
        node_id = node.get("nodeId", "")
        if node_id == "35":
            print(f"\n找到节点 35:")
            print(f"  Node ID: {node_id}")
            print(f"  Node Name: {node.get('nodeName', '')}")
            print(f"  Field Name: {node.get('fieldName', '')}")
            print(f"  Field Value: {node.get('fieldValue', '')}")
            print()
    
    # 也查找所有文本相关的节点
    print("=" * 60)
    print("所有文本相关节点:")
    print("=" * 60)
    for node in node_info_list:
        node_id = node.get("nodeId", "")
        node_name = node.get("nodeName", "")
        field_name = node.get("fieldName", "")
        field_value = node.get("fieldValue", "")
        
        if "text" in node_name.lower() or field_name in ["text", "prompt"]:
            print(f"\nNode {node_id}: {node_name}")
            print(f"  Field: {field_name}")
            print(f"  Value: {field_value}")
else:
    print(f"获取失败: {result.get('msg', '未知错误')}")
