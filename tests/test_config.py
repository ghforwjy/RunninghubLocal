"""
测试配置文件是否正确加载
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import API_KEY, BASE_URL, WORKFLOW_IDS, VIDEO_NODE_ID

print("=" * 50)
print("配置文件测试")
print("=" * 50)

print(f"\n✓ API_KEY: {'已设置' if API_KEY else '未设置'}")
if API_KEY:
    print(f"  值: {API_KEY[:10]}...{API_KEY[-4:]}")

print(f"\n✓ BASE_URL: {BASE_URL}")
print(f"✓ VIDEO_NODE_ID: {VIDEO_NODE_ID}")
print(f"✓ WORKFLOW_IDS: {WORKFLOW_IDS}")

print("\n" + "=" * 50)
print("测试完成！")
print("=" * 50)
