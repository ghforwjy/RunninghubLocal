"""
测试改变动作工作流完整流程 - 使用真实图片测试
"""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = Path(__file__).parent / "test_image.jpg"

def test_full_workflow():
    """测试完整的工作流程"""
    print("=" * 60)
    print("测试完整改变动作工作流程")
    print("=" * 60)

    # 1. 上传图片
    print("\n1. 上传图片...")
    if not TEST_IMAGE_PATH.exists():
        print(f"❌ 测试图片不存在: {TEST_IMAGE_PATH}")
        print("请先在 tests 目录下放置一张名为 test_image.jpg 的图片")
        return False

    with open(TEST_IMAGE_PATH, 'rb') as f:
        files = {'file': ('test_image.jpg', f, 'image/jpeg')}
        data = {'type': 'image'}
        response = requests.post(f"{BASE_URL}/api/upload", data=data, files=files)

    upload_result = response.json()
    print(f"上传响应: {json.dumps(upload_result, indent=2, ensure_ascii=False)}")

    if upload_result.get('code') != 0:
        print("❌ 上传失败")
        return False

    file_name = upload_result['data']['fileName']
    print(f"✅ 上传成功，文件名: {file_name}")

    # 2. 创建任务
    print("\n2. 创建任务...")
    prompt = "保持图片不变,保持参考图中人物头部所有细节都不改变,只改变以下内容：让人物举起双手，做出欢呼的动作"

    response = requests.post(
        f"{BASE_URL}/api/create_pose_task",
        json={'fileName': file_name, 'prompt': prompt}
    )

    task_result = response.json()
    print(f"创建任务响应: {json.dumps(task_result, indent=2, ensure_ascii=False)}")

    if task_result.get('code') != 0:
        print("❌ 创建任务失败")
        return False

    task_id = task_result['data']['taskId']
    print(f"✅ 任务创建成功，任务ID: {task_id}")

    # 3. 轮询状态
    print("\n3. 轮询任务状态...")
    max_retries = 60
    interval = 5

    for i in range(max_retries):
        response = requests.post(
            f"{BASE_URL}/api/query_status",
            json={'taskId': task_id}
        )

        status_result = response.json()
        status = status_result.get('data', 'UNKNOWN')
        print(f"  [{i+1}/{max_retries}] 状态: {status}")

        if status == 'SUCCESS':
            print("✅ 任务执行成功！")
            break
        elif status == 'FAILED':
            print("❌ 任务执行失败")
            return False

        import time
        time.sleep(interval)
    else:
        print("⏰ 轮询超时")
        return False

    # 4. 获取输出
    print("\n4. 获取任务输出...")
    response = requests.post(
        f"{BASE_URL}/api/get_outputs",
        json={'taskId': task_id}
    )

    outputs_result = response.json()
    print(f"输出响应: {json.dumps(outputs_result, indent=2, ensure_ascii=False)}")

    if outputs_result.get('code') != 0:
        print("❌ 获取输出失败")
        return False

    # 5. 检查本地文件
    print("\n5. 检查本地文件...")
    output_dir = Path(__file__).parent.parent / "Output"
    print(f"输出目录: {output_dir}")

    outputs = outputs_result.get('data', [])
    for item in outputs:
        file_url = item.get('fileUrl', '')
        local_url = item.get('localUrl', '')
        print(f"  fileUrl: {file_url}")
        print(f"  localUrl: {local_url}")

        if local_url:
            # 从 localUrl 提取文件名
            file_name = local_url.split('/')[-1]
            local_path = output_dir / file_name
            print(f"  本地路径: {local_path}")
            print(f"  文件是否存在: {local_path.exists()}")

            if local_path.exists():
                print(f"  文件大小: {local_path.stat().st_size} bytes")

    print("\n✅ 完整流程测试完成")
    return True

if __name__ == "__main__":
    test_full_workflow()
