"""
获取当前配置的工作流JSON并分析
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

def analyze_nodes(workflow_json):
    """分析节点"""
    print("\n" + "="*60)
    print("节点分析结果")
    print("="*60)

    for node_id, node_data in sorted(workflow_json.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
        class_type = node_data.get('class_type', '')
        inputs = node_data.get('inputs', {})
        title = node_data.get('_meta', {}).get('title', '')

        # 识别输入节点
        if class_type in ['LoadImage', 'LoadImageMask']:
            print(f"\n🖼️  图片输入节点:")
            print(f"   节点ID: {node_id}")
            print(f"   类型: {class_type}")
            print(f"   标题: {title}")
            print(f"   字段: {list(inputs.keys())}")

        elif class_type in ['VHS_LoadVideo', 'LoadVideo', 'LoadVideoPath']:
            print(f"\n🎬 视频输入节点:")
            print(f"   节点ID: {node_id}")
            print(f"   类型: {class_type}")
            print(f"   标题: {title}")
            print(f"   字段: {list(inputs.keys())}")

        elif class_type in ['SaveImage']:
            print(f"\n💾 保存图片节点:")
            print(f"   节点ID: {node_id}")
            print(f"   类型: {class_type}")
            print(f"   标题: {title}")

if __name__ == "__main__":
    # 图片工作流
    image_workflow_id = "2014552598229032961"
    print(f"\n{'='*60}")
    print(f"获取图片工作流 JSON (ID: {image_workflow_id})")
    print(f"{'='*60}")

    workflow_json = get_workflow_json(image_workflow_id)
    if workflow_json:
        # 保存到文件
        output_file = f"workflow_{image_workflow_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_json, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON已保存到: {output_file}")

        # 分析节点
        analyze_nodes(workflow_json)

    # 视频工作流
    video_workflow_id = "2024416533212045314"
    print(f"\n{'='*60}")
    print(f"获取视频工作流 JSON (ID: {video_workflow_id})")
    print(f"{'='*60}")

    workflow_json = get_workflow_json(video_workflow_id)
    if workflow_json:
        # 保存到文件
        output_file = f"workflow_{video_workflow_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(workflow_json, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON已保存到: {output_file}")

        # 分析节点
        analyze_nodes(workflow_json)
