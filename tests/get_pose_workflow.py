"""
获取改变动作工作流的JSON结构
"""
import requests
import json

API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2024540737567727618"  # 改变动作工作流

url = "https://www.runninghub.cn/api/openapi/getJsonApiFormat"
headers = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
payload = {
    "apiKey": API_KEY,
    "workflowId": WORKFLOW_ID
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

if result.get("code") == 0:
    workflow_json = json.loads(result["data"]["prompt"])
    print("工作流JSON获取成功！")
    print(f"\n工作流ID: {WORKFLOW_ID}")
    print(f"节点数量: {len(workflow_json)}")
    print("\n=== 节点列表 ===")
    for node_id, node_data in workflow_json.items():
        class_type = node_data.get("class_type", "Unknown")
        print(f"  节点 {node_id}: {class_type}")
    
    # 保存到文件
    output_file = f"pose_workflow_{WORKFLOW_ID}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(workflow_json, f, ensure_ascii=False, indent=2)
    print(f"\n工作流JSON已保存到: {output_file}")
else:
    print(f"获取失败: {result}")
