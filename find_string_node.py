import os
import re

# 查找ComfyUI中的字符串输入节点
comfyui_path = r"D:\ComfyUI_windows_portable\ComfyUI"

print("=== 查找ComfyUI中的字符串/文本输入节点 ===\n")

# 遍历查找nodes.py文件
for root, dirs, files in os.walk(comfyui_path):
    for file in files:
        if file.endswith(".py") and "node" in file.lower():
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # 查找包含STRING或text的类定义
                    if 'STRING' in content or 'class.*Text' in content:
                        # 提取类名
                        classes = re.findall(r'class\s+(\w+)', content)
                        if classes:
                            print(f"文件: {filepath.replace(comfyui_path, '')}")
                            for cls in classes[:5]:  # 只显示前5个类
                                print(f"  - {cls}")
                            print()
            except:
                pass
