import json
import shutil

# 工作流文件路径
workflow_path = r"D:\mycode\runninghubLocal\workflows\RunningHub_改变动作_使用版.json"

# 读取工作流
with open(workflow_path, 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print("=== 检查工作流中的节点类型 ===")
for node in workflow.get('nodes', []):
    node_id = node.get('id')
    node_type = node.get('type')
    print(f"  节点 {node_id}: {node_type}")

# 需要修复的节点类型映射
fix_map = {
    "RH Settings": "RH_SettingsNode",
    "RH Node Info List": "RH_NodeInfoListNode",
    "RH Execute": "RH_ExecuteNode"
}

# 修复节点类型
fixed_count = 0
for node in workflow.get('nodes', []):
    old_type = node.get('type')
    if old_type in fix_map:
        new_type = fix_map[old_type]
        print(f"\n修复节点 {node.get('id')}: {old_type} -> {new_type}")
        node['type'] = new_type
        fixed_count += 1

print(f"\n共修复 {fixed_count} 个节点")

# 保存修复后的工作流
with open(workflow_path, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"\n工作流已保存到: {workflow_path}")

# 复制到ComfyUI目录
dest_path = r"D:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\RunningHub_改变动作_使用版.json"
shutil.copy2(workflow_path, dest_path)
print(f"已复制到: {dest_path}")
