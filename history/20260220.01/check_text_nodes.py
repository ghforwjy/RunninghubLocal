# 检查ComfyUI的nodes.py中的文本相关节点
nodes_file = r"D:\ComfyUI_windows_portable\ComfyUI\nodes.py"

with open(nodes_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 查找所有类定义
import re
classes = re.findall(r'class\s+(\w+).*?:', content)

print("=== ComfyUI nodes.py 中的所有节点类 ===\n")
for cls in classes:
    print(f"  - {cls}")

# 查找包含text或string的类
text_classes = [cls for cls in classes if 'text' in cls.lower() or 'string' in cls.lower()]
print(f"\n=== 文本/字符串相关节点 ===\n")
for cls in text_classes:
    print(f"  - {cls}")
