import shutil
import os

# 源目录
source = r"D:\mycode\runninghubLocal\tmp\ComfyUI_RH_APICall"
# 目标目录
dest = r"D:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI_RH_APICall"

print(f"源目录: {source}")
print(f"目标目录: {dest}")

# 如果目标目录已存在，先删除（跳过.git目录）
def onerror(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        print(f"跳过: {path}")

if os.path.exists(dest):
    print("目标目录已存在，正在删除...")
    try:
        shutil.rmtree(dest, onerror=onerror)
        print("旧目录已删除")
    except Exception as e:
        print(f"删除时出错: {e}")
        print("尝试直接覆盖...")

# 复制目录
print("正在复制节点...")
try:
    shutil.copytree(source, dest, dirs_exist_ok=True)
    print("复制完成")
except Exception as e:
    print(f"复制出错: {e}")
    print("尝试逐个文件复制...")
    # 手动复制文件
    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(dest, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    print("逐个文件复制完成")

# 验证
if os.path.exists(dest):
    files = os.listdir(dest)
    print(f"\n复制成功！")
    print(f"节点文件数量: {len(files)}")
    print("文件列表:")
    for f in files:
        print(f"  - {f}")
else:
    print("复制失败！")
