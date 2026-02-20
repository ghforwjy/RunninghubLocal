"""
测试创建改变动作任务，检查传参是否正确
"""
import json
import requests
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import API_KEY, BASE_URL, POSE_WORKFLOW_ID, POSE_IMAGE_NODE_ID, POSE_PROMPT_NODE_ID

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def test_create_task():
    """测试创建任务"""
    print("=" * 60)
    print("测试创建改变动作任务")
    print("=" * 60)

    # 使用一个测试图片文件名（需要先上传图片获取）
    file_name = input("请输入已上传的图片文件名: ").strip()
    if not file_name:
        print("❌ 未提供文件名")
        return

    prompt = input("请输入提示词 (直接回车使用默认): ").strip()
    if not prompt:
        prompt = "保持图片不变,保持参考图中人物头部所有细节都不改变,只改变以下内容：让人物举起双手，做出欢呼的动作"

    print(f"\n图片文件名: {file_name}")
    print(f"提示词: {prompt}")

    # 创建任务
    url = f"{BASE_URL}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": POSE_WORKFLOW_ID,
        "nodeInfoList": [
            {
                "nodeId": POSE_IMAGE_NODE_ID,
                "fieldName": "image",
                "fieldValue": file_name
            },
            {
                "nodeId": POSE_PROMPT_NODE_ID,
                "fieldName": "prompt",
                "fieldValue": prompt
            }
        ]
    }

    print(f"\n发送请求:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    result = resp.json()

    print(f"\n收到响应:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result.get('code') == 0:
        print(f"\n✅ 任务创建成功")
        print(f"任务ID: {result['data']['taskId']}")
        print(f"任务状态: {result['data']['taskStatus']}")
    else:
        print(f"\n❌ 任务创建失败: {result.get('msg')}")

if __name__ == "__main__":
    test_create_task()
