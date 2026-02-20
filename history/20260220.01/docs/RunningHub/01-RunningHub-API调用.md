# 01 - RunningHub API 调用指南

> 通过 REST API 调用 RunningHub 云端工作流
> 
> 适合读者: 开发者、需要通过代码调用 RunningHub 的用户

---

## 目录

1. [快速开始](#1-快速开始)
2. [准备工作](#2-准备工作)
3. [API 认证](#3-api-认证)
4. [发起任务](#4-发起任务)
5. [查询任务](#5-查询任务)
6. [完整示例代码](#6-完整示例代码)
7. [错误码说明](#7-错误码说明)

---

## 1. 快速开始

### 1.1 最小可运行示例

```python
import requests
import time

# 配置
API_KEY = "your-api-key"
WORKFLOW_ID = "your-workflow-id"
BASE_URL = "https://www.runninghub.cn"

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 1. 发起任务
resp = requests.post(
    f"{BASE_URL}/task/openapi/create",
    headers=HEADERS,
    json={"apiKey": API_KEY, "workflowId": WORKFLOW_ID}
)

task_id = resp.json()["data"]["taskId"]
print(f"任务已创建: {task_id}")

# 2. 轮询等待完成
for i in range(30):
    time.sleep(10)
    status_resp = requests.post(
        f"{BASE_URL}/task/openapi/status",
        headers=HEADERS,
        json={"apiKey": API_KEY, "taskId": task_id}
    )
    status = status_resp.json()["data"]
    
    if status == "SUCCESS":
        # 3. 获取结果
        result_resp = requests.post(
            f"{BASE_URL}/task/openapi/outputs",
            headers=HEADERS,
            json={"apiKey": API_KEY, "taskId": task_id}
        )
        for item in result_resp.json()["data"]:
            print(f"生成结果: {item['fileUrl']}")
        break
    elif status == "FAILED":
        print("任务执行失败")
        break
```

---

## 2. 准备工作

### 2.1 注册账号

访问 https://www.runninghub.cn/ 注册 RunningHub 账号

### 2.2 开通会员

开通基础版及以上会员（免费用户暂不支持 API 调用）

### 2.3 获取 API Key

1. 登录 RunningHub 官网
2. 点击右上角头像 → 「API 控制台」
3. 复制您的 API Key（32位字符串）

### 2.4 获取 Workflow ID

1. 访问 https://www.runninghub.cn/workflows
2. 选择合适的工作流
3. 从 URL 中提取 ID，例如：
   - URL: `https://www.runninghub.cn/post/2016195556967714818`
   - Workflow ID: `2016195556967714818`

> ⚠️ **重要**: 目标工作流必须在网页端成功运行过至少一次，否则 API 调用会报错。

---

## 3. API 认证

### 3.1 请求头规范

所有请求必须包含以下 Header：

| Header | 值 | 说明 |
|--------|-----|------|
| `Host` | `www.runninghub.cn` | API 域名 |
| `Content-Type` | `application/json` | 请求体类型 |
| `Authorization` | `Bearer [Your API KEY]` | 身份验证 |

### 3.2 请求体规范

所有请求体必须包含 `apiKey` 字段：

```json
{
  "apiKey": "your-api-key",
  "workflowId": "your-workflow-id"
}
```

---

## 4. 发起任务

### 4.1 简易版（不修改参数）

直接运行工作流，不修改任何参数。

**请求**:
```http
POST /task/openapi/create
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "taskId": "1904737800233889793",
    "taskStatus": "RUNNING",
    "netWssUrl": "wss://www.runninghub.cn:443/ws/..."
  }
}
```

### 4.2 高级版（自定义参数）

通过 `nodeInfoList` 修改工作流节点参数。

**请求**:
```http
POST /task/openapi/create
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346",
  "nodeInfoList": [
    {
      "nodeId": "6",
      "fieldName": "text",
      "fieldValue": "1 girl in classroom, anime style"
    },
    {
      "nodeId": "3",
      "fieldName": "seed",
      "fieldValue": "123456"
    }
  ]
}
```

**nodeInfoList 说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `nodeId` | string | 节点的唯一编号 |
| `fieldName` | string | 要修改的字段名 |
| `fieldValue` | any | 替换后的新值 |

**如何获取 nodeId 和 fieldName**:

1. 调用 `/api/openapi/getJsonApiFormat` 接口获取工作流 JSON
2. 查看工作流结构，找到对应节点的 ID 和字段名

---

## 5. 查询任务

### 5.1 查询任务状态

**请求**:
```http
POST /task/openapi/status
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "apiKey": "your-api-key",
  "taskId": "1904152026220003329"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "",
  "data": "RUNNING"  // QUEUED, RUNNING, SUCCESS, FAILED
}
```

### 5.2 查询任务结果

**请求**:
```http
POST /task/openapi/outputs
Content-Type: application/json
Authorization: Bearer your-api-key

{
  "apiKey": "your-api-key",
  "taskId": "1904152026220003329"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "fileUrl": "https://rh-images.xiaoyaoyou.com/.../output.png",
      "fileType": "png",
      "taskCostTime": "83",
      "consumeCoins": "17"
    }
  ]
}
```

---

## 6. 完整示例代码

### 6.1 基础封装类

```python
import requests
import json
import time
from typing import List, Dict, Optional

class RunningHubClient:
    """RunningHub API 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.runninghub.cn"
        self.headers = {
            "Host": "www.runninghub.cn",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def create_task(self, workflow_id: str, node_info_list: List[Dict] = None) -> Dict:
        """发起任务"""
        payload = {
            "apiKey": self.api_key,
            "workflowId": workflow_id
        }
        if node_info_list:
            payload["nodeInfoList"] = node_info_list
            
        resp = requests.post(
            f"{self.base_url}/task/openapi/create",
            headers=self.headers,
            json=payload
        )
        resp.raise_for_status()
        return resp.json()
    
    def get_task_status(self, task_id: str) -> str:
        """查询任务状态"""
        resp = requests.post(
            f"{self.base_url}/task/openapi/status",
            headers=self.headers,
            json={"apiKey": self.api_key, "taskId": task_id}
        )
        return resp.json().get("data")
    
    def get_task_outputs(self, task_id: str) -> List[Dict]:
        """获取任务结果"""
        resp = requests.post(
            f"{self.base_url}/task/openapi/outputs",
            headers=self.headers,
            json={"apiKey": self.api_key, "taskId": task_id}
        )
        return resp.json().get("data", [])
    
    def wait_for_completion(self, task_id: str, max_retries: int = 30, interval: int = 10) -> List[Dict]:
        """等待任务完成并返回结果"""
        for i in range(max_retries):
            status = self.get_task_status(task_id)
            
            if status == "SUCCESS":
                return self.get_task_outputs(task_id)
            elif status == "FAILED":
                raise Exception("任务执行失败")
            
            time.sleep(interval)
        
        raise TimeoutError("任务执行超时")


# 使用示例
if __name__ == "__main__":
    client = RunningHubClient(api_key="your-api-key")
    
    # 发起任务
    result = client.create_task(workflow_id="your-workflow-id")
    task_id = result["data"]["taskId"]
    print(f"任务已创建: {task_id}")
    
    # 等待完成
    outputs = client.wait_for_completion(task_id)
    for item in outputs:
        print(f"生成结果: {item['fileUrl']}")
```

### 6.2 图生图示例

```python
import requests

# 1. 上传图片（如果需要）
# 2. 调用 API
client = RunningHubClient(api_key="your-api-key")

# 配置图生图参数
node_info_list = [
    {
        "nodeId": "2",  # LoadImage 节点
        "fieldName": "image",
        "fieldValue": "uploaded-image-filename.jpg"
    },
    {
        "nodeId": "6",  # Prompt 节点
        "fieldName": "text",
        "fieldValue": "convert to oil painting style"
    }
]

result = client.create_task(
    workflow_id="your-img2img-workflow-id",
    node_info_list=node_info_list
)

# 等待完成...
```

---

## 7. 错误码说明

### 7.1 常见错误码

| 错误码 | 错误标识 | 说明 | 解决方案 |
|--------|----------|------|----------|
| 301 | PARAMS_INVALID | 参数错误 | 检查必填参数是否完整 |
| 380 | WORKFLOW_NOT_EXISTS | 工作流不存在 | 检查 workflowId 是否正确 |
| 412 | TOKEN_INVALID | API 路径错误 | 检查 URL 拼写 |
| 433 | VALIDATE_PROMPT_FAILED | 工作流校验失败 | 检查 nodeInfoList 参数 |
| 802 | APIKEY_UNAUTHORIZED | API Key 无效 | 检查 API Key 是否正确 |
| 803 | APIKEY_INVALID_NODE_INFO | 节点信息不匹配 | 检查 nodeId 和 fieldName |
| 810 | WORKFLOW_NOT_SAVED_OR_NOT_RUNNING | 工作流未运行过 | 先在网页端运行一次 |

### 7.2 完整错误码表

详见 [官方错误码文档](https://www.runninghub.cn/runninghub-api-doc-cn/)

---

## 相关文档

- [02-本地ComfyUI与RunningHub对接](./02-本地ComfyUI与RunningHub对接.md) - 可视化操作指南
- [03-ComfyUI使用技巧](./03-ComfyUI使用技巧.md) - ComfyUI 通用技巧
- [README](./README.md) - 返回总入口

---

*本文档基于 RunningHub API 实践经验整理*
