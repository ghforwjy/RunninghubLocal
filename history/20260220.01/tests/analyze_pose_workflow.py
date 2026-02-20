"""
分析"改变动作"工作流结构，找出与图片比例/分辨率相关的节点
"""
import json
import sys
import os

def main():
    # 读取工作流JSON
    workflow_path = os.path.join(os.path.dirname(__file__), "pose_workflow.json")
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)
    
    # 保存格式化后的JSON
    formatted_path = os.path.join(os.path.dirname(__file__), "pose_workflow_formatted.json")
    with open(formatted_path, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
    print(f"✅ 格式化后的JSON已保存到: {formatted_path}")
    
    # 分析工作流
    if "workflow" in workflow_data:
        workflow = workflow_data["workflow"]
    elif "prompt" in workflow_data:
        # 有些API返回的格式是 {"prompt": {...}}
        workflow = json.loads(workflow_data["prompt"])
    else:
        workflow = workflow_data
    
    print("\n" + "=" * 80)
    print("工作流节点分析")
    print("=" * 80)
    
    # 收集所有节点信息
    nodes_info = []
    for node_id, node_data in workflow.items():
        if isinstance(node_data, dict):
            node_type = node_data.get("class_type", "Unknown")
            meta = node_data.get("_meta", {})
            title = meta.get("title", "")
            inputs = node_data.get("inputs", {})
            
            nodes_info.append({
                "id": node_id,
                "type": node_type,
                "title": title,
                "inputs": inputs
            })
    
    # 按节点ID排序
    nodes_info.sort(key=lambda x: int(x["id"]) if x["id"].isdigit() else 0)
    
    print(f"\n总节点数: {len(nodes_info)}")
    print("\n所有节点列表:")
    print("-" * 80)
    for node in nodes_info:
        print(f"  Node {node['id']:>3}: {node['type']:<40} | {node['title']}")
    
    # 分析与图片尺寸/分辨率相关的节点
    print("\n" + "=" * 80)
    print("🔍 图片尺寸/分辨率相关节点分析")
    print("=" * 80)
    
    # 关键词匹配
    size_keywords = ['width', 'height', 'size', 'resolution', 'scale', 'EmptyImage', 
                     'LoadImage', 'ImageScale', 'Upscale', 'Resize', 'Crop']
    
    relevant_nodes = []
    for node in nodes_info:
        node_str = json.dumps(node, ensure_ascii=False).lower()
        if any(kw.lower() in node_str for kw in size_keywords):
            relevant_nodes.append(node)
    
    print(f"\n找到 {len(relevant_nodes)} 个可能相关的节点:\n")
    for node in relevant_nodes:
        print(f"  📍 Node {node['id']}: {node['type']}")
        print(f"     标题: {node['title']}")
        print(f"     输入参数:")
        for key, value in node['inputs'].items():
            print(f"       - {key}: {value}")
        print()
    
    # 分析连接关系
    print("=" * 80)
    print("🔗 节点连接关系分析")
    print("=" * 80)
    
    # 查找图像处理链
    image_nodes = []
    for node in nodes_info:
        if any(x in node['type'].lower() for x in ['image', 'vae', 'sample', 'decode']):
            image_nodes.append(node)
    
    print(f"\n图像处理链节点 ({len(image_nodes)} 个):")
    for node in image_nodes:
        print(f"  Node {node['id']}: {node['type']} - {node['title']}")
    
    # 查找EmptyImage节点（通常用于设置输出尺寸）
    print("\n" + "=" * 80)
    print("🎯 关键节点详细分析")
    print("=" * 80)
    
    for node in nodes_info:
        if node['type'] in ['EmptyImage', 'EmptyLatentImage']:
            print(f"\n📐 发现尺寸控制节点 (Node {node['id']}):")
            print(f"   类型: {node['type']}")
            print(f"   标题: {node['title']}")
            print(f"   参数:")
            for key, value in node['inputs'].items():
                print(f"     - {key}: {value}")
    
    # 查找LoadImage节点
    for node in nodes_info:
        if node['type'] == 'LoadImage':
            print(f"\n🖼️  发现图片输入节点 (Node {node['id']}):")
            print(f"   类型: {node['type']}")
            print(f"   标题: {node['title']}")
            print(f"   参数:")
            for key, value in node['inputs'].items():
                print(f"     - {key}: {value}")

if __name__ == "__main__":
    main()
