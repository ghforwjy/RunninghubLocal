"""
获取新工作流JSON结构
工作流ID: 2024540737567727618
"""
import json
import sys
sys.path.insert(0, 'd:\\mycode\\runninghubLocal')

from runninghub_client import RunningHubClient
from config import API_KEY

client = RunningHubClient(api_key=API_KEY)

# 获取工作流JSON
workflow_id = "2024540737567727618"
print(f"正在获取工作流 {workflow_id} 的JSON结构...")
print("=" * 60)

result = client.get_workflow_json(workflow_id)

if result.get("code") == 0:
    workflow_data = result.get("data", {})
    print(f"工作流名称: {workflow_data.get('workflowName', '未知')}")
    print(f"工作流ID: {workflow_data.get('workflowId', '未知')}")
    print()
    
    # 保存完整JSON到文件
    with open(f"workflow_{workflow_id}.json", "w", encoding="utf-8") as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    print(f"完整JSON已保存到: workflow_{workflow_id}.json")
    print()
    
    # 分析节点
    node_info_list = workflow_data.get("nodeInfoList", [])
    print(f"节点数量: {len(node_info_list)}")
    print("-" * 60)
    
    # 查找关键节点
    for node in node_info_list:
        node_id = node.get("nodeId", "")
        node_name = node.get("nodeName", "")
        field_name = node.get("fieldName", "")
        field_value = node.get("fieldValue", "")
        
        # 查找图片输入节点
        if "image" in field_name.lower() or "loadimage" in node_name.lower():
            print(f"\n🖼️ 图片输入节点:")
            print(f"   Node ID: {node_id}")
            print(f"   Node Name: {node_name}")
            print(f"   Field Name: {field_name}")
            print(f"   Field Value: {field_value}")
        
        # 查找文本/提示词节点
        if field_name in ["text", "prompt", "positive", "negative"] or "text" in node_name.lower():
            print(f"\n📝 文本节点:")
            print(f"   Node ID: {node_id}")
            print(f"   Node Name: {node_name}")
            print(f"   Field Name: {field_name}")
            print(f"   Field Value: {field_value[:100]}..." if len(str(field_value)) > 100 else f"   Field Value: {field_value}")
        
        # 查找尺寸相关节点
        if field_name in ["width", "height"] or "size" in node_name.lower() or "latent" in node_name.lower():
            print(f"\n📐 尺寸节点:")
            print(f"   Node ID: {node_id}")
            print(f"   Node Name: {node_name}")
            print(f"   Field Name: {field_name}")
            print(f"   Field Value: {field_value}")
    
    print("\n" + "=" * 60)
    print("所有节点列表:")
    print("-" * 60)
    for node in node_info_list:
        print(f"Node {node.get('nodeId')}: {node.get('nodeName')} | {node.get('fieldName')} = {str(node.get('fieldValue', ''))[:50]}")
else:
    print(f"获取失败: {result.get('msg', '未知错误')}")
    print(f"完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
