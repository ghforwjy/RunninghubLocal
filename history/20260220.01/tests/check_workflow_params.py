"""
检查工作流的完整参数结构
"""
import json
from runninghub_client import RunningHubClient
from config import API_KEY

POSE_WORKFLOW_ID = "2008590031811776514"

def main():
    client = RunningHubClient(api_key=API_KEY)

    print("=" * 60)
    print(f"获取工作流 {POSE_WORKFLOW_ID} 的完整参数")
    print("=" * 60)

    workflow_json = client.get_workflow_json(POSE_WORKFLOW_ID)

    if workflow_json.get("code") == 0:
        data = workflow_json.get("data", {})

        # 保存完整JSON到文件以便查看
        with open('workflow_full.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("完整JSON已保存到 workflow_full.json")

        # 解析prompt中的JSON
        if "prompt" in data:
            prompt_data = json.loads(data["prompt"])

            print("\n" + "=" * 60)
            print("所有节点及其可配置参数:")
            print("=" * 60)

            for node_id, node_info in sorted(prompt_data.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999):
                class_type = node_info.get("class_type", "")
                inputs = node_info.get("inputs", {})
                meta = node_info.get("_meta", {})
                title = meta.get("title", "")

                # 只显示有输入参数的节点
                if inputs:
                    print(f"\n节点 {node_id}: {class_type} ({title})")
                    for key, value in inputs.items():
                        # 截断长值
                        if isinstance(value, str) and len(value) > 50:
                            value_str = value[:50] + "..."
                        else:
                            value_str = value
                        print(f"  - {key}: {value_str}")

        # 检查是否有 nodeInfoList
        print("\n" + "=" * 60)
        print("nodeInfoList (API输入节点):")
        print("=" * 60)
        if "nodeInfoList" in data and data["nodeInfoList"]:
            for node in data["nodeInfoList"]:
                print(f"\n节点: {node.get('nodeId')}")
                print(f"  名称: {node.get('nodeName')}")
                print(f"  字段: {node.get('fieldName')}")
                print(f"  值: {node.get('fieldValue')[:50] if isinstance(node.get('fieldValue'), str) and len(node.get('fieldValue')) > 50 else node.get('fieldValue')}...")
                print(f"  类型: {node.get('fieldType')}")
        else:
            print("该工作流没有配置API输入节点")
            print("这意味着所有参数都需要通过 nodeInfoList 传递")
    else:
        print(f"获取失败: {workflow_json.get('msg')}")

if __name__ == "__main__":
    main()
