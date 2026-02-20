"""
测试改变动作工作流API
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_pose_page():
    """测试页面是否能正常访问"""
    print("=" * 60)
    print("测试1: 访问改变动作页面")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/pose")
    if response.status_code == 200:
        print("✅ 页面访问成功")
        return True
    else:
        print(f"❌ 页面访问失败: {response.status_code}")
        return False

def test_create_pose_task_without_file():
    """测试不带文件的创建任务请求"""
    print("\n" + "=" * 60)
    print("测试2: 测试创建任务API（无文件）")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/create_pose_task",
        json={"prompt": "test prompt"}
    )
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    if result.get("code") == -1 and "缺少文件名" in result.get("msg", ""):
        print("✅ 参数验证正确")
        return True
    else:
        print("❌ 参数验证异常")
        return False

def test_create_pose_task_without_prompt():
    """测试不带提示词的创建任务请求"""
    print("\n" + "=" * 60)
    print("测试3: 测试创建任务API（无提示词）")
    print("=" * 60)

    response = requests.post(
        f"{BASE_URL}/api/create_pose_task",
        json={"fileName": "test.jpg"}
    )
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

    if result.get("code") == -1 and "缺少提示词" in result.get("msg", ""):
        print("✅ 参数验证正确")
        return True
    else:
        print("❌ 参数验证异常")
        return False

def main():
    print("\n🧪 开始测试改变动作工作流API\n")

    tests = [
        test_pose_page,
        test_create_pose_task_without_file,
        test_create_pose_task_without_prompt,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {passed + failed}")

if __name__ == "__main__":
    main()
