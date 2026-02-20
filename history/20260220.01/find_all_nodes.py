# 遍历ComfyUI所有节点文件，查找所有节点类型
import os
import re

comfyui_path = r"D:\ComfyUI_windows_portable\ComfyUI"

print("=== 查找ComfyUI中的所有节点 ===\n")

all_classes = []

# 遍历所有Python文件
for root, dirs, files in os.walk(comfyui_path):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 查找所有类定义
                    classes = re.findall(r'class\s+(\w+)', content)
                    if classes:
                        for cls in classes:
                            all_classes.append((cls, filepath.replace(comfyui_path, "")))
            except:
                pass

# 保存到文件
with open(r"D:\mycode\runninghubLocal\all_nodes.txt", "w", encoding="utf-8") as f:
    f.write(f"共找到 {len(all_classes)} 个类\n\n")
    f.write("所有类：\n")
    for cls, path in all_classes:
        f.write(f"  {cls} ({path})\n")

print(f"共找到 {len(all_classes)} 个类")
print("结果已保存到 all_nodes.txt")

# 查找可能相关的节点
print("\n=== 可能相关的节点 ===")
keywords = ['string', 'text', 'prompt', 'input', 'value', 'multiline']
for cls, path in all_classes:
    if any(kw in cls.lower() for kw in keywords):
        print(f"  {cls} ({path})")
