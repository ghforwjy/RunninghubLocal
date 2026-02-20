# RunningHub API 调用指南 - 可用Todo List

> 本文档提供RunningHub API调用的完整步骤清单
> 最后更新: 2026-02-19

---

## 前置条件检查清单

- [ ] 已注册RunningHub账号
- [ ] 已开通基础版及以上会员
- [ ] 已获取API Key (32位字符串)
- [ ] 已选择要调用的工作流，并确认该工作流已被运行过至少一次

---

## 调用流程 Todo List

### 第一阶段: 准备工作

- [ ] **1.1 获取工作流ID**
  - 访问 https://www.runninghub.cn/workflows
  - 选择合适的工作流
  - 从URL中提取工作流ID (例如: `2016195556967714818`)

- [ ] **1.2 配置API密钥**
  ```python
  API_KEY = "your-api-key-here"
  WORKFLOW_ID = "2016195556967714818"
  BASE_URL = "https://www.runninghub.cn"
  ```

- [ ] **1.3 设置请求头**
  ```python
  HEADERS = {
      "Host": "www.runninghub.cn",
      "Content-Type": "application/json",
      "Authorization": f"Bearer {API_KEY}"
  }
  ```

---

### 第二阶段: 发起任务

- [ ] **2.1 调用创建任务接口**
  - 接口: `POST /task/openapi/create`
  - 简易版（不修改参数）:
    ```python
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    ```
  - 高级版（自定义参数）:
    ```python
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": [
            {
                "nodeId": "6",
                "fieldName": "text",
                "fieldValue": "custom prompt"
            }
        ]
    }
    ```

- [ ] **2.2 解析响应获取taskId**
  ```python
  response = requests.post(url, headers=HEADERS, json=payload)
  result = response.json()
  
  if result.get("code") == 0:
      task_id = result["data"]["taskId"]
      task_status = result["data"]["taskStatus"]
      wss_url = result["data"]["netWssUrl"]  # WebSocket监控地址
  ```

---

### 第三阶段: 轮询任务状态

- [ ] **3.1 实现状态轮询逻辑**
  ```python
  def wait_for_task(task_id, max_retries=30, interval=10):
      for i in range(max_retries):
          status = query_task_status(task_id)
          
          if status == "SUCCESS":
              return True
          elif status == "FAILED":
              return False
          elif status == "QUEUED":
              print("任务排队中...")
          elif status == "RUNNING":
              print("任务运行中...")
          
          time.sleep(interval)
      
      return None  # 超时
  ```

- [ ] **3.2 查询任务状态接口**
  - 接口: `POST /task/openapi/status`
  - 参数:
    ```python
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    ```

---

### 第四阶段: 获取结果

- [ ] **4.1 任务成功后获取输出**
  - 接口: `POST /task/openapi/outputs`
  - 参数:
    ```python
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    ```

- [ ] **4.2 解析并下载生成文件**
  ```python
  response = requests.post(url, headers=HEADERS, json=payload)
  result = response.json()
  
  if result.get("code") == 0:
      outputs = result.get("data", [])
      for item in outputs:
          file_url = item["fileUrl"]
          file_type = item["fileType"]
          consume_coins = item["consumeCoins"]
          # 下载文件...
  ```

---

## 完整代码示例

```python
import requests
import json
import time

class RunningHubAPI:
    def __init__(self, api_key, workflow_id):
        self.api_key = api_key
        self.workflow_id = workflow_id
        self.base_url = "https://www.runninghub.cn"
        self.headers = {
            "Host": "www.runninghub.cn",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def create_task(self, node_info_list=None):
        """创建任务"""
        url = f"{self.base_url}/task/openapi/create"
        payload = {
            "apiKey": self.api_key,
            "workflowId": self.workflow_id
        }
        if node_info_list:
            payload["nodeInfoList"] = node_info_list
        
        resp = requests.post(url, headers=self.headers, json=payload)
        return resp.json()
    
    def query_status(self, task_id):
        """查询任务状态"""
        url = f"{self.base_url}/task/openapi/status"
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        return resp.json()
    
    def get_outputs(self, task_id):
        """获取任务结果"""
        url = f"{self.base_url}/task/openapi/outputs"
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        resp = requests.post(url, headers=self.headers, json=payload)
        return resp.json()
    
    def run_workflow(self, node_info_list=None, max_retries=30, interval=10):
        """运行完整工作流并返回结果"""
        # 1. 创建任务
        create_result = self.create_task(node_info_list)
        if create_result.get("code") != 0:
            print(f"创建任务失败: {create_result}")
            return None
        
        task_id = create_result["data"]["taskId"]
        print(f"任务创建成功, taskId: {task_id}")
        
        # 2. 轮询等待完成
        for i in range(max_retries):
            status_result = self.query_status(task_id)
            if status_result.get("code") != 0:
                print(f"查询状态失败: {status_result}")
                return None
            
            status = status_result["data"]
            print(f"[{i+1}/{max_retries}] 状态: {status}")
            
            if status == "SUCCESS":
                print("任务执行成功!")
                return self.get_outputs(task_id)
            elif status == "FAILED":
                print("任务执行失败!")
                return None
            
            time.sleep(interval)
        
        print("轮询超时")
        return None


# 使用示例
if __name__ == "__main__":
    api = RunningHubAPI(
        api_key="acf7d42aedee45dfa8b78ee43eec82a9",
        workflow_id="2016195556967714818"
    )
    
    # 运行工作流
    result = api.run_workflow()
    
    if result and result.get("code") == 0:
        outputs = result.get("data", [])
        print(f"\n生成 {len(outputs)} 个文件:")
        for item in outputs:
            print(f"  - {item['fileUrl']}")
```

---

## 常用接口速查

| 功能 | 接口 | 方法 |
|------|------|------|
| 创建任务 | /task/openapi/create | POST |
| 查询状态 | /task/openapi/status | POST |
| 获取结果 | /task/openapi/outputs | POST |
| 取消任务 | /task/openapi/cancel | POST |
| 获取工作流JSON | /api/openapi/getJsonApiFormat | POST |
| 查询账户信息 | /uc/openapi/accountStatus | POST |

---

## 任务状态说明

| 状态 | 说明 |
|------|------|
| CREATE | 任务已创建 |
| QUEUED | 任务排队中 |
| RUNNING | 任务运行中 |
| SUCCESS | 任务执行成功 |
| FAILED | 任务执行失败 |

---

## 错误码速查

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| 0 | 成功 | - |
| 301 | 参数错误 | 检查请求参数 |
| 802 | API Key无效 | 检查API Key |
| 810 | 工作流未运行过 | 先在网页端运行一次 |
| 421 | 并发上限 | 等待后重试 |

---

## 注意事项

1. **工作流必须先运行过**: 新工作流需要先在网页端成功运行至少一次
2. **轮询间隔**: 建议10秒，避免频繁请求
3. **超时设置**: 图像生成通常需要2-5分钟
4. **费用**: 按生成图片数量和复杂度扣费
5. **Host头**: 必须精确填写 `www.runninghub.cn`

---

*本文档配合 `RunningHub_API_经验Q&A.md` 使用效果更佳*
