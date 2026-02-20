"""
测试 get_outputs 接口是否正确下载文件
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5000"
OUTPUT_DIR = Path(__file__).parent.parent / "Output"

def test_get_outputs():
    """测试获取输出接口"""
    print("=" * 60)
    print("测试 get_outputs 接口")
    print("=" * 60)

    # 需要一个已完成的任务ID来测试
    task_id = input("请输入一个已完成的任务ID: ").strip()

    if not task_id:
        print("❌ 未提供任务ID")
        return

    print(f"\n获取任务 {task_id} 的输出...")

    response = requests.post(
        f"{BASE_URL}/api/get_outputs",
        json={'taskId': task_id}
    )

    result = response.json()
    print(f"\n响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    if result.get('code') != 0:
        print("❌ 获取输出失败")
        return

    # 检查本地文件
    print(f"\n检查本地文件...")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"目录是否存在: {OUTPUT_DIR.exists()}")

    outputs = result.get('data', [])
    for item in outputs:
        file_url = item.get('fileUrl', '')
        local_url = item.get('localUrl', '')
        file_type = item.get('fileType', 'unknown')

        print(f"\n  文件类型: {file_type}")
        print(f"  fileUrl: {file_url}")
        print(f"  localUrl: {local_url}")

        if local_url:
            file_name = local_url.split('/')[-1]
            local_path = OUTPUT_DIR / file_name
            print(f"  本地路径: {local_path}")
            print(f"  文件是否存在: {local_path.exists()}")

            if local_path.exists():
                print(f"  文件大小: {local_path.stat().st_size} bytes")
        else:
            print("  ⚠️ 没有 localUrl，文件未下载到本地")

if __name__ == "__main__":
    test_get_outputs()
