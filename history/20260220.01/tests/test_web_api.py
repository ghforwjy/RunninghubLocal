"""
测试网页后端 API
"""
import requests
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://127.0.0.1:5000"
INPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Input")

def test_upload_video():
    """测试视频上传 API"""
    print("=" * 50)
    print("测试视频上传 API")
    print("=" * 50)
    
    # 查找测试视频
    video_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if not video_files:
        print("错误: 未找到测试视频文件")
        return None
    
    video_path = os.path.join(INPUT_DIR, video_files[0])
    print(f"使用测试视频: {video_files[0]}")
    
    # 测试上传
    url = f"{BASE_URL}/api/upload"
    
    with open(video_path, 'rb') as f:
        files = {'file': (video_files[0], f, 'video/mp4')}
        data = {'type': 'video'}
        
        try:
            response = requests.post(url, files=files, data=data, timeout=30)
            result = response.json()
            
            print(f"状态码: {response.status_code}")
            print(f"响应: {result}")
            
            if result.get('code') == 0:
                print(f"✅ 上传成功!")
                file_name = result.get('data', {}).get('fileName')
                print(f"   文件名: {file_name}")
                return file_name
            else:
                print(f"❌ 上传失败: {result.get('msg')}")
                return None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None

def test_create_task(file_name, file_type='video', orientation='portrait'):
    """测试创建任务 API"""
    print("\n" + "=" * 50)
    print("测试创建任务 API")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/create_task"
    data = {
        'fileName': file_name,
        'type': file_type,
        'orientation': orientation
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {result}")
        
        if result.get('code') == 0:
            print(f"✅ 任务创建成功!")
            task_id = result.get('data', {}).get('taskId')
            print(f"   任务ID: {task_id}")
            return task_id
        else:
            print(f"❌ 任务创建失败: {result.get('msg')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_query_status(task_id):
    """测试查询任务状态 API"""
    print("\n" + "=" * 50)
    print("测试查询任务状态 API")
    print("=" * 50)
    
    url = f"{BASE_URL}/api/query_status"
    data = {'taskId': task_id}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {result}")
        
        if result.get('code') == 0:
            print(f"✅ 状态查询成功!")
            data = result.get('data', {})
            print(f"   任务状态: {data.get('status')}")
            print(f"   进度: {data.get('progress', 'N/A')}")
            return result
        else:
            print(f"❌ 状态查询失败: {result.get('msg')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_webpage():
    """测试网页是否正常加载"""
    print("=" * 50)
    print("测试网页加载")
    print("=" * 50)
    
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 网页加载成功!")
            # 检查关键内容
            content = response.text
            if "AI去水印工具" in content:
                print("✅ 页面标题正确")
            if "视频去水印" in content:
                print("✅ 视频去水印功能存在")
            if "图片去水印" in content:
                print("✅ 图片去水印功能存在")
            return True
        else:
            print(f"❌ 网页加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("网页后端 API 测试")
    print("=" * 60 + "\n")
    
    # 1. 测试网页加载
    if not test_webpage():
        print("\n❌ 网页加载失败，停止测试")
        return
    
    # 2. 测试视频上传
    file_name = test_upload_video()
    if not file_name:
        print("\n❌ 视频上传失败，停止测试")
        return
    
    # 3. 测试创建任务（竖屏）
    task_id = test_create_task(file_name, 'video', 'portrait')
    if not task_id:
        print("\n❌ 任务创建失败，停止测试")
        return
    
    # 4. 测试查询状态
    test_query_status(task_id)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
