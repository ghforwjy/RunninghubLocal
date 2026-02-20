import os
import sys

# 添加ComfyUI路径
sys.path.insert(0, r"D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI_RH_APICall")

print("=== 检查RunningHub节点导入 ===")

try:
    from RH_SettingsNode import SettingsNode
    print("✓ RH_SettingsNode 导入成功")
except Exception as e:
    print(f"✗ RH_SettingsNode 导入失败: {e}")

try:
    from RH_NodeInfoListNode import NodeInfoListNode
    print("✓ RH_NodeInfoListNode 导入成功")
except Exception as e:
    print(f"✗ RH_NodeInfoListNode 导入失败: {e}")

try:
    from RH_ExecuteNode import ExecuteNode
    print("✓ RH_ExecuteNode 导入成功")
except Exception as e:
    print(f"✗ RH_ExecuteNode 导入失败: {e}")

print("\n=== 检查__init__.py ===")
init_file = r"D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI_RH_APICall\__init__.py"
with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)
