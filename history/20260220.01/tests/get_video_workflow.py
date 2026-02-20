"""
获取视频去水印工作流JSON并分析
"""
import requests
import json
import sys
sys.path.insert(0, '..')
from config import API_KEY, BASE_URL

def get_workflow_json(workflow_id):
    """获取工作流JSON"""
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    headers = {
        "Host": "www.runninghub.cn",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "apiKey": API_KEY,
        "workflowId": workflow_id
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        result = resp.json()

        if result.get('code') == 0:
            prompt_data = result.get('data', {}).get('prompt', '{}')
            if isinstance(prompt_data, str):
                return json.loads(prompt_data)
            return prompt_data
        else:
            print(f"❌ 获取失败: {result.get('msg', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def analyze_workflow(workflow_json):
    """分析工作流结构和去水印原理"""
    print("\n" + "="*70)
    print("视频去水印工作流分析")
    print("="*70)

    # 1. 找出所有关键节点
    nodes_info = []
    for node_id, node_data in workflow_json.items():
        class_type = node_data.get('class_type', '')
        inputs = node_data.get('inputs', {})
        title = node_data.get('_meta', {}).get('title', '')

        nodes_info.append({
            'id': node_id,
            'type': class_type,
            'title': title,
            'inputs': list(inputs.keys())
        })

    # 2. 分类节点
    input_nodes = [n for n in nodes_info if 'Load' in n['type'] or 'Input' in n['type']]
    output_nodes = [n for n in nodes_info if 'Save' in n['type'] or 'Output' in n['type']]
    processing_nodes = [n for n in nodes_info if n not in input_nodes and n not in output_nodes]

    print("\n【输入节点】")
    for node in input_nodes:
        print(f"  节点 {node['id']}: {node['type']} - {node['title']}")
        print(f"    输入字段: {node['inputs']}")

    print("\n【输出节点】")
    for node in output_nodes:
        print(f"  节点 {node['id']}: {node['type']} - {node['title']}")

    print("\n【核心处理节点】")
    key_types = ['VHS_', 'Sampler', 'Model', 'Mask', 'Inpaint', 'Remove', 'Denoise']
    for node in processing_nodes:
        if any(k in node['type'] for k in key_types):
            print(f"  节点 {node['id']}: {node['type']} - {node['title']}")

    return nodes_info

if __name__ == "__main__":
    # 视频去水印工作流ID
    workflow_id = "2024416533212045314"
    print(f"获取视频去水印工作流 JSON (ID: {workflow_id})")

    workflow_json = get_workflow_json(workflow_id)
    if workflow_json:
        # 保存到文件
        output_file = f"video_workflow_{workflow_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_json, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON已保存到: {output_file}")

        # 分析工作流
        analyze_workflow(workflow_json)
