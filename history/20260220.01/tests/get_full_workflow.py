"""
获取完整工作流JSON
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
    
    # 保存完整JSON
    with open("workflow_full_new.json", "w", encoding="utf-8") as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
    print("完整JSON已保存到 workflow_full_new.json")
    print()
    
    # 打印所有节点
    node_info_list = workflow_data.get("nodeInfoList", [])
    print(f"节点数量: {len(node_info_list)}")
    print("=" * 60)
    
    for node in node_info_list:
        node_id = node.get("nodeId", "")
        node_name = node.get("nodeName", "")
        field_name = node.get("fieldName", "")
        field_value = node.get("fieldValue", "")
        print(f"Node {node_id}: {node_name} | {field_name} = {field_value}")
else:
    print(f"获取失败: {result.get('msg', '未知错误')}")
    print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
