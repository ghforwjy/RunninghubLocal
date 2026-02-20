"""
深度分析工作流节点连接关系
"""
import json
import os

def main():
    # 读取工作流JSON
    workflow_path = os.path.join(os.path.dirname(__file__), "pose_workflow.json")
    with open(workflow_path, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)
    
    # 解析工作流
    if "workflow" in workflow_data:
        workflow = workflow_data["workflow"]
    elif "prompt" in workflow_data:
        workflow = json.loads(workflow_data["prompt"])
    else:
        workflow = workflow_data
    
    print("=" * 80)
    print("深度分析：改变动作工作流节点连接关系")
    print("=" * 80)
    
    # 详细分析每个节点的输入连接
    print("\n📊 节点输入连接详情：\n")
    
    for node_id in sorted(workflow.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        node_data = workflow[node_id]
        if not isinstance(node_data, dict):
            continue
            
        node_type = node_data.get("class_type", "Unknown")
        title = node_data.get("_meta", {}).get("title", "")
        inputs = node_data.get("inputs", {})
        
        print(f"\n{'='*60}")
        print(f"Node {node_id}: {node_type}")
        print(f"标题: {title}")
        print(f"{'-'*60}")
        
        for input_name, input_value in inputs.items():
            if isinstance(input_value, list) and len(input_value) == 2:
                # 这是一个连接引用 [node_id, output_slot]
                ref_node_id, output_slot = input_value
                print(f"  📎 {input_name}: ← Node {ref_node_id} [{output_slot}]")
            else:
                # 这是一个直接值
                value_str = str(input_value)[:50]
                if len(str(input_value)) > 50:
                    value_str += "..."
                print(f"  📝 {input_name}: {value_str}")
    
    # 特别关注尺寸相关节点的链路
    print("\n" + "=" * 80)
    print("🔍 尺寸控制链路追踪")
    print("=" * 80)
    
    # Node 38 EmptyLatentImage
    print("\n📐 Node 38 (EmptyLatentImage) 的输入:")
    node_38 = workflow.get("38", {})
    for input_name, input_value in node_38.get("inputs", {}).items():
        if isinstance(input_value, list) and len(input_value) == 2:
            ref_node_id, slot = input_value
            print(f"  {input_name}: ← Node {ref_node_id}")
            
            # 追踪这个节点的输入
            ref_node = workflow.get(str(ref_node_id), {})
            print(f"    Node {ref_node_id} ({ref_node.get('class_type')}) 的输入:")
            for ref_input_name, ref_input_value in ref_node.get("inputs", {}).items():
                if isinstance(ref_input_value, list) and len(ref_input_value) == 2:
                    ref_ref_id, ref_slot = ref_input_value
                    print(f"      {ref_input_name}: ← Node {ref_ref_id}")
                    
                    # 继续追踪
                    ref_ref_node = workflow.get(str(ref_ref_id), {})
                    if ref_ref_node:
                        print(f"        Node {ref_ref_id} ({ref_ref_node.get('class_type')}) 的输入:")
                        for rr_name, rr_value in ref_ref_node.get("inputs", {}).items():
                            if isinstance(rr_value, list) and len(rr_value) == 2:
                                print(f"          {rr_name}: ← Node {rr_value[0]}")
                            else:
                                print(f"          {rr_name}: {rr_value}")
                else:
                    print(f"      {ref_input_name}: {ref_input_value}")
        else:
            print(f"  {input_name}: {input_value}")
    
    # 分析Node 39 Get Image Size
    print("\n" + "=" * 80)
    print("🖼️  Node 39 (Get Image Size) 分析")
    print("=" * 80)
    node_39 = workflow.get("39", {})
    print(f"类型: {node_39.get('class_type')}")
    print(f"标题: {node_39.get('_meta', {}).get('title')}")
    print("输入:")
    for input_name, input_value in node_39.get("inputs", {}).items():
        if isinstance(input_value, list):
            print(f"  {input_name}: ← Node {input_value[0]}")
        else:
            print(f"  {input_name}: {input_value}")
    
    # 总结尺寸计算逻辑
    print("\n" + "=" * 80)
    print("📋 尺寸计算逻辑总结")
    print("=" * 80)
    print("""
根据节点连接关系分析：

1. Node 25 (LoadImage) 加载输入图片
        ↓
2. Node 39 (Get Image Size) 获取原图尺寸
   - 输出 [0] = 原图宽度
   - 输出 [1] = 原图高度
        ↓
3. Node 52 (SeargeIntegerMath-width) 计算目标宽度
   - 输入 a = Node 39 [0] (原图宽度)
   - 输入 b = 1 (乘数)
   - 运算: a * b = 原图宽度 * 1 = 原图宽度
        ↓
4. Node 53 (SeargeIntegerMath-height) 计算目标高度
   - 输入 a = Node 39 [1] (原图高度)
   - 输入 b = 1 (乘数)
   - 运算: a * b = 原图高度 * 1 = 原图高度
        ↓
5. Node 38 (EmptyLatentImage) 使用计算出的尺寸
   - width = Node 52 的输出 (原图宽度)
   - height = Node 53 的输出 (原图高度)

结论：
- 当前工作流确实会读取原图尺寸
- 通过 Node 52 和 53 的乘数(b)可以调整输出比例
- 默认 b=1 表示保持原尺寸
- 修改 b 的值可以实现比例调整
    """)

if __name__ == "__main__":
    main()
