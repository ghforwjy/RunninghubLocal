import json

# 读取工作流文件
workflow_path = r"D:\mycode\runninghubLocal\workflows\RunningHub_改变动作_使用版.json"
with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 修正节点类型
for node in workflow.get('nodes', []):
    if node.get('type') == 'StringMultiline':
        print(f"修正节点 {node.get('id')}: StringMultiline -> PrimitiveStringMultiline")
        node['type'] = 'PrimitiveStringMultiline'

# 保存修正后的工作流
with open(workflow_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print("\n修正完成！")
