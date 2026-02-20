"""
文件拷贝脚本 - 用于拷贝文件到项目外部目录
由于权限限制，需要通过Python脚本来拷贝文件
"""

import shutil
import sys
import os

# 配置：目标目录映射
TARGET_DIRS = {
    "comfyui_workflows": "D:\\ComfyUI_windows_portable\\ComfyUI\\user\\default\\workflows",
}

# 配置：源文件映射
SOURCE_FILES = {
    "qwen_workflow": "workflows\\RunningHub_QwenImageEdit_姿态迁移.json",
}


def copy_file(source_name, target_name, new_filename=None):
    """
    拷贝文件到目标目录
    
    Args:
        source_name: 源文件标识（在SOURCE_FILES中配置）
        target_name: 目标目录标识（在TARGET_DIRS中配置）
        new_filename: 新文件名（可选，默认使用原文件名）
    """
    # 获取源文件路径
    if source_name not in SOURCE_FILES:
        print(f"❌ 未知的源文件: {source_name}")
        print(f"可用的源文件: {list(SOURCE_FILES.keys())}")
        return False
    
    source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SOURCE_FILES[source_name])
    
    # 获取目标目录
    if target_name not in TARGET_DIRS:
        print(f"❌ 未知的目标目录: {target_name}")
        print(f"可用的目标目录: {list(TARGET_DIRS.keys())}")
        return False
    
    target_dir = TARGET_DIRS[target_name]
    
    # 检查源文件是否存在
    if not os.path.exists(source_path):
        print(f"❌ 源文件不存在: {source_path}")
        return False
    
    # 检查目标目录是否存在
    if not os.path.exists(target_dir):
        print(f"❌ 目标目录不存在: {target_dir}")
        return False
    
    # 确定目标文件名
    if new_filename is None:
        new_filename = os.path.basename(source_path)
    
    target_path = os.path.join(target_dir, new_filename)
    
    # 拷贝文件
    try:
        shutil.copy2(source_path, target_path)
        print(f"✅ 文件拷贝成功")
        print(f"   源文件: {source_path}")
        print(f"   目标: {target_path}")
        return True
    except Exception as e:
        print(f"❌ 拷贝失败: {e}")
        return False


def main():
    """主函数 - 处理命令行参数"""
    if len(sys.argv) < 3:
        print("用法: python copyfile.py <source_name> <target_name> [new_filename]")
        print("\n示例:")
        print("  python copyfile.py qwen_workflow comfyui_workflows")
        print("  python copyfile.py qwen_workflow comfyui_workflows 新文件名.json")
        print("\n可用的源文件:")
        for key in SOURCE_FILES:
            print(f"  - {key}: {SOURCE_FILES[key]}")
        print("\n可用的目标目录:")
        for key in TARGET_DIRS:
            print(f"  - {key}: {TARGET_DIRS[key]}")
        return
    
    source_name = sys.argv[1]
    target_name = sys.argv[2]
    new_filename = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = copy_file(source_name, target_name, new_filename)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
