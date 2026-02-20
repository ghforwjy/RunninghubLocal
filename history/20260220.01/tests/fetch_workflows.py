"""
通过API获取当前配置的实际工作流JSON
"""
import requests
import json
import sys
sys.path.insert(0, '..')
from config import API_KEY, BASE_URL

def get_workflow_json(workflow_id):
    """通过API获取工作流JSON"""
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
            print(f"❌ 获取工作流 {workflow_id} 失败: {result.get('msg', '未知错误')}")
            return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def analyze_watermark_removal(workflow_json, workflow_name):
    """分析去水印原理"""
    print(f"\n{'='*80}")
    print(f"【{workflow_name}】去水印原理分析")
    print(f"{'='*80}")

    # 1. 找出所有关键节点
    input_nodes = []  # 输入节点
    output_nodes = []  # 输出节点
    ai_model_nodes = []  # AI模型节点
    processing_nodes = []  # 处理节点

    for node_id, node_data in workflow_json.items():
        class_type = node_data.get('class_type', '')
        title = node_data.get('_meta', {}).get('title', '')

        # 输入节点
        if class_type in ['LoadImage', 'LoadVideo', 'VHS_LoadVideo']:
            input_nodes.append((node_id, class_type, title, node_data.get('inputs', {}).keys()))

        # 输出节点
        elif class_type in ['SaveImage', 'SaveVideo']:
            output_nodes.append((node_id, class_type, title))

        # AI模型节点
        elif class_type in ['UNETLoader', 'VAELoader', 'CLIPLoader']:
            model_name = node_data.get('inputs', {}).get('unet_name') or \
                        node_data.get('inputs', {}).get('vae_name') or \
                        node_data.get('inputs', {}).get('clip_name', '')
            ai_model_nodes.append((node_id, class_type, title, model_name))

        # 采样/生成节点
        elif 'Sampler' in class_type or class_type in ['KSampler', 'SamplerCustomAdvanced']:
            processing_nodes.append((node_id, class_type, title))

        # 编码/解码节点
        elif 'VAEEncode' in class_type or 'VAEDecode' in class_type:
            processing_nodes.append((node_id, class_type, title))

        # 参考 latent 节点（风格迁移关键）
        elif 'ReferenceLatent' in class_type:
            processing_nodes.append((node_id, class_type, title + " ⚠️风格参考"))

        # 文本编码（提示词）
        elif 'CLIPTextEncode' in class_type or 'JjkText' in class_type:
            text = node_data.get('inputs', {}).get('text', '')
            if isinstance(text, str) and len(text) > 50:
                processing_nodes.append((node_id, class_type, title[:50] + "..."))

    # 打印分析结果
    print("\n📥 输入节点:")
    for node in input_nodes:
        print(f"   节点 {node[0]}: {node[1]} - {node[2]}")
        print(f"      字段: {list(node[3])}")

    print("\n