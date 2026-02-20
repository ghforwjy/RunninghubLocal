import os

# 检查节点目录
node_dir = r"D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI_RH_APICall"

print("=== 检查节点文件 ===")
files = [
    "__init__.py",
    "RH_SettingsNode.py",
    "RH_NodeInfoListNode.py",
    "RH_ExecuteNode.py",
    "RH_ImageUploaderNode.py",
    "RH_VideoUploader.py",
    "RH_AudioUploader.py",
    "RH_Utils.py",
]

for f in files:
    path = os.path.join(node_dir, f)
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    print(f"  {f}: {'✓' if exists else '✗'} ({size} bytes)")

# 检查web目录
web_dir = os.path.join(node_dir, "web", "js")
print(f"\n=== 检查web目录 ===")
print(f"  web/js: {'✓' if os.path.exists(web_dir) else '✗'}")
if os.path.exists(web_dir):
    web_files = os.listdir(web_dir)
    print(f"  文件数: {len(web_files)}")
    for f in web_files:
        print(f"    - {f}")

print("\n=== 检查__init__.py内容 ===")
init_file = os.path.join(node_dir, "__init__.py")
with open(init_file, 'r', encoding='utf-8') as f:
    content = f.read()
    print(content)
