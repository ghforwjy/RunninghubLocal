"""
RunningHub API 客户端
封装了RunningHub API的常用操作

使用方法:
    from runninghub_client import RunningHubClient
    
    client = RunningHubClient(api_key="your-api-key")
    result = client.run_workflow(workflow_id="2016195556967714818")
"""

import requests
import json
import time
import os
from typing import Optional, List, Dict, Any


class RunningHubClient:
    """RunningHub API 客户端"""
    
    BASE_URL = "https://www.runninghub.cn"
    
    def __init__(self, api_key: str):
        """
        初始化客户端
        
        Args:
            api_key: RunningHub API Key (32位字符串)
        """
        self.api_key = api_key
        self.headers = {
            "Host": "www.runninghub.cn",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def _post(self, endpoint: str, payload: Dict) -> Dict[str, Any]:
        """发送POST请求"""
        url = f"{self.BASE_URL}{endpoint}"
        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            return {"code": -1, "msg": f"请求异常: {str(e)}", "data": None}
    
    def get_account_status(self) -> Dict[str, Any]:
        """
        获取账户信息
        
        Returns:
            包含账户余额、任务数量等信息的字典
        """
        payload = {"apikey": self.api_key}
        return self._post("/uc/openapi/accountStatus", payload)
    
    def get_workflow_json(self, workflow_id: str) -> Dict[str, Any]:
        """
        获取工作流JSON结构
        
        Args:
            workflow_id: 工作流ID
            
        Returns:
            工作流的JSON配置
        """
        payload = {
            "apiKey": self.api_key,
            "workflowId": workflow_id
        }
        return self._post("/api/openapi/getJsonApiFormat", payload)
    
    def create_task(
        self, 
        workflow_id: str, 
        node_info_list: Optional[List[Dict]] = None,
        webhook_url: Optional[str] = None,
        instance_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建任务
        
        Args:
            workflow_id: 工作流ID
            node_info_list: 节点参数修改列表，用于自定义工作流参数
            webhook_url: 任务完成后的回调URL
            instance_type: 实例类型，如 "plus" 表示48G显存机器
            
        Returns:
            包含taskId、taskStatus等信息的字典
            
        Example:
            # 简易调用
            result = client.create_task("2016195556967714818")
            
            # 自定义参数调用
            node_info = [{
                "nodeId": "6",
                "fieldName": "text",
                "fieldValue": "1 girl in classroom"
            }]
            result = client.create_task("2016195556967714818", node_info)
        """
        payload = {
            "apiKey": self.api_key,
            "workflowId": workflow_id
        }
        
        if node_info_list:
            payload["nodeInfoList"] = node_info_list
        if webhook_url:
            payload["webhookUrl"] = webhook_url
        if instance_type:
            payload["instanceType"] = instance_type
            
        return self._post("/task/openapi/create", payload)
    
    def query_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            包含任务状态的字典，状态值：QUEUED, RUNNING, SUCCESS, FAILED
        """
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        return self._post("/task/openapi/status", payload)
    
    def get_task_outputs(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务生成结果
        
        Args:
            task_id: 任务ID
            
        Returns:
            包含生成文件URL列表的字典
        """
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        return self._post("/task/openapi/outputs", payload)
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            取消结果
        """
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        return self._post("/task/openapi/cancel", payload)
    
    def upload_image(self, image_path: str) -> Dict[str, Any]:
        """
        上传图片到 RunningHub
        
        Args:
            image_path: 本地图片路径
            
        Returns:
            上传结果，包含 fileName 等信息
            
        Example:
            result = client.upload_image("path/to/image.jpg")
            if result.get("code") == 0:
                filename = result["data"]["fileName"]
        """
        url = f"{self.BASE_URL}/file/openapi/upload"
        
        headers = {
            "Host": "www.runninghub.cn",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                resp = requests.post(url, headers=headers, files=files, timeout=60)
                resp.raise_for_status()
                return resp.json()
        except FileNotFoundError:
            return {"code": -1, "msg": f"文件不存在: {image_path}", "data": None}
        except requests.exceptions.RequestException as e:
            return {"code": -1, "msg": f"上传失败: {str(e)}", "data": None}
    
    def upload_video(self, video_path: str) -> Dict[str, Any]:
        """
        上传视频到 RunningHub
        
        Args:
            video_path: 本地视频路径
            
        Returns:
            上传结果，包含 fileName 等信息
        """
        url = f"{self.BASE_URL}/file/openapi/upload"
        
        headers = {
            "Host": "www.runninghub.cn",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            with open(video_path, 'rb') as f:
                files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
                resp = requests.post(url, headers=headers, files=files, timeout=120)
                resp.raise_for_status()
                return resp.json()
        except FileNotFoundError:
            return {"code": -1, "msg": f"文件不存在: {video_path}", "data": None}
        except requests.exceptions.RequestException as e:
            return {"code": -1, "msg": f"上传失败: {str(e)}", "data": None}
    
    def wait_for_task(
        self, 
        task_id: str, 
        max_retries: int = 30, 
        interval: int = 10,
        callback=None
    ) -> Optional[Dict[str, Any]]:
        """
        轮询等待任务完成
        
        Args:
            task_id: 任务ID
            max_retries: 最大重试次数，默认30次
            interval: 轮询间隔（秒），默认10秒
            callback: 状态变更回调函数，接收(status, retry_count)参数
            
        Returns:
            任务成功时返回输出结果，失败或超时返回None
        """
        print(f"开始轮询任务状态 (taskId: {task_id})...")
        
        for i in range(max_retries):
            result = self.query_task_status(task_id)
            
            if result.get("code") != 0:
                print(f"查询状态失败: {result.get('msg')}")
                return None
            
            status = result.get("data")
            
            if callback:
                callback(status, i + 1)
            else:
                print(f"[{i+1}/{max_retries}] 任务状态: {status}")
            
            if status == "SUCCESS":
                print("✅ 任务执行成功！")
                return self.get_task_outputs(task_id)
            elif status == "FAILED":
                print("❌ 任务执行失败！")
                return None
            elif status == "QUEUED":
                print("⏳ 任务正在排队中...")
            elif status == "RUNNING":
                print("🔄 任务正在运行中...")
            
            time.sleep(interval)
        
        print("⏰ 轮询超时，任务可能仍在执行中")
        return None
    
    def run_workflow(
        self,
        workflow_id: str,
        node_info_list: Optional[List[Dict]] = None,
        max_retries: int = 30,
        interval: int = 10,
        webhook_url: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        运行完整工作流（创建任务 + 轮询等待 + 获取结果）
        
        Args:
            workflow_id: 工作流ID
            node_info_list: 节点参数修改列表
            max_retries: 最大轮询次数
            interval: 轮询间隔（秒）
            webhook_url: 回调URL
            
        Returns:
            任务成功时返回输出结果，失败返回None
            
        Example:
            client = RunningHubClient("your-api-key")
            result = client.run_workflow("2016195556967714818")
            
            if result:
                for item in result.get("data", []):
                    print(f"生成文件: {item['fileUrl']}")
        """
        # 1. 创建任务
        create_result = self.create_task(
            workflow_id=workflow_id,
            node_info_list=node_info_list,
            webhook_url=webhook_url
        )
        
        if create_result.get("code") != 0:
            print(f"❌ 创建任务失败: {create_result.get('msg')}")
            return None
        
        data = create_result.get("data", {})
        task_id = data.get("taskId")
        task_status = data.get("taskStatus")
        
        print(f"✅ 任务创建成功!")
        print(f"   Task ID: {task_id}")
        print(f"   Initial Status: {task_status}")
        
        # 2. 等待任务完成
        return self.wait_for_task(task_id, max_retries, interval)


# 便捷函数
def quick_run(api_key: str, workflow_id: str, **kwargs) -> Optional[List[str]]:
    """
    快速运行工作流并返回文件URL列表
    
    Args:
        api_key: API Key
        workflow_id: 工作流ID
        **kwargs: 其他参数传递给run_workflow
        
    Returns:
        生成文件的URL列表
        
    Example:
        urls = quick_run(
            api_key="your-api-key",
            workflow_id="2016195556967714818"
        )
        for url in urls:
            print(url)
    """
    client = RunningHubClient(api_key)
    result = client.run_workflow(workflow_id, **kwargs)
    
    if result and result.get("code") == 0:
        outputs = result.get("data", [])
        return [item["fileUrl"] for item in outputs]
    
    return None


if __name__ == "__main__":
    # 测试代码
    API_KEY = "acf7d42aedee45dfa8b78ee43eec82a9"
    WORKFLOW_ID = "2016195556967714818"
    
    client = RunningHubClient(API_KEY)
    
    # 查询账户信息
    print("=" * 50)
    print("查询账户信息...")
    account = client.get_account_status()
    print(json.dumps(account, indent=2, ensure_ascii=False))
    
    # 运行工作流
    print("\n" + "=" * 50)
    print("运行工作流...")
    result = client.run_workflow(WORKFLOW_ID)
    
    if result:
        print("\n生成结果:")
        for item in result.get("data", []):
            print(f"  - {item['fileUrl']}")
