#!/usr/bin/env python3
"""
获取云端工作流JSON结构
"""
import requests
import json

# 配置
API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
WORKFLOW_ID = "2024703585040211969"  # 目标工作流ID
BASE_URL = "https://www.runninghub.cn"

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def get_workflow_json():
    """获取工作流JSON结构"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    
    resp = requests.post(url, headers=HEADERS, json=payload)
    result = resp.json()
    
    if result.get("code") == 0:
        prompt = result["data"]["prompt"]
        # 解析JSON字符串
        workflow = json.loads(prompt)
        return workflow
    else:
        print(f"获取失败: {result}")
        return None


def analyze_workflow(workflow):
    """分析工作流结构"""
    print("=" * 80)
    print(f"工作流ID: {WORKFLOW_ID}")
    print("=" * 80)
    
    # 查找所有节点
    print("\n【节点列表】")
    for node_id, node_info in workflow.items():
        class_type = node_info.get("class_type", "Unknown")
        print(f"  节点 {node_id}: {class_type}")
    
    # 查找输出节点（SaveImage, SaveLatent等）
    print("\n【输出节点】")
    for node_id, node_info in workflow.items():
        class_type = node_info.get("class_type", "")
        if "Save" in class_type or "Output" in class_type:
            print(f"  节点 {node_id}: {class_type}")
            print(f"    inputs: {json.dumps(node_info.get('inputs', {}), indent=4)}")
    
    # 查找Latent相关节点
    print("\n【Latent相关节点】")
    for node_id, node_info in workflow.items():
        class_type = node_info.get("class_type", "")
        if "Latent" in class_type or "latent" in str(node_info).lower():
            print(f"  节点 {node_id}: {class_type}")
            print(f"    inputs: {json.dumps(node_info.get('inputs', {}), indent=4)}")
    
    # 查找VAE Decode节点
    print("\n【VAE Decode节点】")
    for node_id, node_info in workflow.items():
        class_type = node_info.get("class_type", "")
        if "VAEDecode" in class_type or "Decode" in class_type:
            print(f"  节点 {node_id}: {class_type}")
            print(f"    inputs: {json.dumps(node_info.get('inputs', {}), indent=4)}")
    
    # 查找LoadImage节点（输入）
    print("\n【输入节点(LoadImage)】")
    for node_id, node_info in workflow.items():
        class_type = node_info.get("class_type", "")
        if class_type == "LoadImage":
            print(f"  节点 {node_id}: {class_type}")
            print(f"    inputs: {json.dumps(node_info.get('inputs', {}), indent=4)}")
    
    # 保存完整JSON到文件
    output_file = f"d:\\mycode\\runninghubLocal\\workflows\\cloud_workflow_{WORKFLOW_ID}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    print(f"\n【完整JSON已保存到】{output_file}")
    
    return workflow


if __name__ == "__main__":
    workflow = get_workflow_json()
    if workflow:
        analyze_workflow(workflow)
