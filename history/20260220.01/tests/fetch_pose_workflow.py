"""
获取"改变动作"工作流的JSON结构并保存到文件
"""
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runninghub_client import RunningHubClient
from config import API_KEY, POSE_WORKFLOW_ID

def main():
    client = RunningHubClient(api_key=API_KEY)
    
    print(f"正在获取工作流 JSON...")
    print(f"工作流ID: {POSE_WORKFLOW_ID}")
    
    result = client.get_workflow_json(workflow_id=POSE_WORKFLOW_ID)
    
    if result.get("code") != 0:
        print(f"❌ 获取失败: {result.get('msg')}")
        return
    
    workflow_data = result.get("data", {})
    
    # 保存到文件
    output_path = os.path.join(os.path.dirname(__file__), "pose_workflow.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 工作流JSON已保存到: {output_path}")
    
    # 分析工作流结构
    print("\n" + "=" * 60)
    print("工作流结构分析:")
    print("=" * 60)
    
    if "workflow" in workflow_data:
        workflow = workflow_data["workflow"]
        if "nodes" in workflow:
            nodes = workflow["nodes"]
            print(f"\n总节点数: {len(nodes)}")
            print("\n节点列表:")
            for node_id, node_data in nodes.items():
                node_type = node_data.get("type", "Unknown")
                node_title = node_data.get("title", "")
                print(f"  Node {node_id}: {node_type} - {node_title}")

if __name__ == "__main__":
    main()
