"""
解析工作流JSON，查找节点35
"""
import json

# 读取JSON
with open("workflow_full_new.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# prompt字段是一个嵌套的JSON字符串
prompt_str = data.get("prompt", "{}")
prompt_data = json.loads(prompt_str)

print("=" * 60)
print("工作流中的所有节点:")
print("=" * 60)

for node_id, node_data in prompt_data.items():
    class_type = node_data.get("class_type", "")
    inputs = node_data.get("inputs", {})
    meta = node_data.get("_meta", {})
    title = meta.get("title", "")
    
    # 查找文本相关的节点
    if "text" in class_type.lower() or "prompt" in str(inputs).lower():
        print(f"\nNode {node_id}: {class_type}")
        print(f"  Title: {title}")
        print(f"  Inputs: {inputs}")

# 特别查找节点35
print("\n" + "=" * 60)
print("查找节点 35:")
print("=" * 60)
if "35" in prompt_data:
    node = prompt_data["35"]
    print(f"Node 35: {node}")
else:
    print("节点35不存在")
    print("\n所有可用节点ID:", sorted(prompt_data.keys(), key=int))
