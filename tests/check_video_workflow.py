"""
检查视频去水印工作流的结构，对比改变动作工作流
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from runninghub_client import RunningHubClient
from config import API_KEY, WORKFLOW_IDS

VIDEO_WORKFLOW_ID = WORKFLOW_IDS['video']['portrait']

def main():
    client = RunningHubClient(api_key=API_KEY)

    print("=" * 60)
    print(f"视频去水印工作流 {VIDEO_WORKFLOW_ID}")
    print("=" * 60)

    workflow_json = client.get_workflow_json(VIDEO_WORKFLOW_ID)

    if workflow_json.get("code") == 0:
        data = workflow_json.get("data", {})

        print("\nnodeInfoList (API输入节点):")
        print("-" * 60)
        if "nodeInfoList" in data and data["nodeInfoList"]:
            for node in data["nodeInfoList"]:
                print(f"\n节点: {node.get('nodeId')}")
                print(f"  名称: {node.get('nodeName')}")
                print(f"  字段: {node.get('fieldName')}")
                print(f"  值: {node.get('fieldValue')}")
                print(f"  类型: {node.get('fieldType')}")
        else:
            print("该工作流没有配置API输入节点")

        # 解析prompt中的JSON
        if "prompt" in data:
            prompt_data = json.loads(data["prompt"])

            print("\n\n所有节点:")
            print("-" * 60)
            for node_id, node_info in sorted(prompt_data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
                class_type = node_info.get("class_type", "")
                meta = node_info.get("_meta", {})
                title = meta.get("title", "")
                print(f"  节点 {node_id}: {class_type} ({title})")
    else:
        print(f"获取失败: {workflow_json.get('msg')}")

if __name__ == "__main__":
    main()
