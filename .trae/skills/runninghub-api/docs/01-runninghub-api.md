# RunningHub API 直接调用指南

> 本文档涵盖：直接调用 RunningHub REST API 进行文生图、图生图、视频生成等任务

---

## 目录

1. [前置条件](#前置条件)
2. [快速开始](#快速开始)
3. [核心概念](#核心概念)
4. [API 接口详解](#api-接口详解)
5. [任务类型示例](#任务类型示例)
6. [错误处理](#错误处理)
7. [最佳实践](#最佳实践)

---

## 前置条件

### 1. 注册与开通

- 注册 RunningHub 账号：https://www.runninghub.cn/
- 开通基础版及以上会员（免费用户不支持 API）

### 2. 获取 API Key

1. 登录官网
2. 点击右上角头像 → 「API 控制台」
3. 复制 32 位 API Key

### 3. 准备工作流

- 在网页端找到目标工作流
- **必须先在网页端成功运行至少一次**
- 记录工作流 ID（从 URL 获取）

---

## 快速开始

### 最小可用示例

```python
import requests
import time

API_KEY = "your-32-char-api-key"
WORKFLOW_ID = "2016195556967714818"
BASE_URL = "https://www.runninghub.cn"

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json"
}

# 1. 创建任务
def create_task():
    url = f"{BASE_URL}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": [{
            "nodeId": "6",
            "fieldName": "text",
            "fieldValue": "1 girl in classroom, anime style"
        }]
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()["data"]["taskId"]

# 2. 查询状态
def query_status(task_id):
    url = f"{BASE_URL}/task/openapi/status"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()["data"]

# 3. 获取结果
def get_outputs(task_id):
    url = f"{BASE_URL}/task/openapi/outputs"
    payload = {
        "apiKey": API_KEY,
        "taskId": task_id
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()["data"]

# 执行流程
task_id = create_task()
print(f"任务创建: {task_id}")

# 轮询等待
for i in range(30):
    status = query_status(task_id)
    print(f"[{i+1}/30] 状态: {status}")
    
    if status == "SUCCESS":
        outputs = get_outputs(task_id)
        for item in outputs:
            print(f"✅ 完成: {item['fileUrl']}")
        break
    elif status == "FAILED":
        print("❌ 任务失败")
        break
    
    time.sleep(10)
```

---

## 核心概念

### 工作流 ID

从工作流 URL 中提取：

```
https://www.runninghub.cn/workflow/2016195556967714818
                              └──────────────────┘
                                    工作流ID
```

### 节点信息 (nodeInfoList)

用于修改工作流中的参数：

```python
node_info_list = [
    {
        "nodeId": "6",           # 节点ID（从工作流JSON获取）
        "fieldName": "text",      # 字段名
        "fieldValue": "prompt"    # 字段值
    }
]
```

### 任务状态

| 状态 | 说明 |
|------|------|
| CREATE | 任务已创建 |
| QUEUED | 排队中 |
| RUNNING | 运行中 |
| SUCCESS | 成功 |
| FAILED | 失败 |

---

## API 接口详解

### 1. 创建任务

**端点**: `POST /task/openapi/create`

**请求参数**:

```json
{
  "apiKey": "your-api-key",
  "workflowId": "2016195556967714818",
  "nodeInfoList": [
    {
      "nodeId": "6",
      "fieldName": "text",
      "fieldValue": "prompt text"
    }
  ]
}
```

**响应**:

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "taskId": "task-xxx-xxx"
  }
}
```

### 2. 查询状态

**端点**: `POST /task/openapi/status`

**请求参数**:

```json
{
  "apiKey": "your-api-key",
  "taskId": "task-xxx-xxx"
}
```

### 3. 获取结果

**端点**: `POST /task/openapi/outputs`

**响应**:

```json
{
  "code": 0,
  "data": [
    {
      "fileUrl": "https://...",
      "fileType": "png",
      "taskCostTime": "83",
      "consumeCoins": "5"
    }
  ]
}
```

### 4. 取消任务

**端点**: `POST /task/openapi/cancel`

### 5. 获取工作流 JSON

**端点**: `POST /api/openapi/getJsonApiFormat`

用于分析工作流结构，获取节点 ID。

### 6. 查询账户

**端点**: `POST /uc/openapi/accountStatus`

---

## 任务类型示例

### 文生图

```python
node_info_list = [{
    "nodeId": "6",
    "fieldName": "text",
    "fieldValue": "1 girl in classroom, anime style"
}]

result = client.run_workflow(
    workflow_id="2016195556967714818",
    node_info_list=node_info_list
)
```

### 图生图（需上传图片）

```python
# 1. 上传图片
upload_result = client.upload_image("source.png")
filename = upload_result["data"]["fileName"]

# 2. 调用工作流
node_info_list = [{
    "nodeId": "21",
    "fieldName": "image",
    "fieldValue": filename
}]

result = client.run_workflow(
    workflow_id="2014552598229032961",
    node_info_list=node_info_list
)
```

### 风格迁移（双图片）

```python
# 上传两张图片
source = client.upload_image("source.png")
style = client.upload_image("style.png")

node_info_list = [
    {
        "nodeId": "21",
        "fieldName": "image",
        "fieldValue": source["data"]["fileName"]
    },
    {
        "nodeId": "24",
        "fieldName": "image",
        "fieldValue": style["data"]["fileName"]
    }
]
```

### 视频去水印

```python
# 上传视频
upload = client.upload_video("video.mp4")

node_info_list = [{
    "nodeId": "184",
    "fieldName": "video",
    "fieldValue": upload["data"]["fileName"]
}]

result = client.run_workflow(
    workflow_id="2024416533212045314",
    node_info_list=node_info_list
)
```

---

## 错误处理

### 错误码速查

| 错误码 | 错误信息 | 原因 | 解决方案 |
|--------|----------|------|----------|
| 803 | APIKEY_INVALID_NODE_INFO | 节点ID或字段名错误 | 重新分析工作流JSON |
| 810 | WORKFLOW_NOT_SAVED_OR_NOT_RUNNING | 工作流未运行过 | 在网页端运行一次 |
| 802 | APIKEY_UNAUTHORIZED | API Key无效 | 检查API Key |
| 421 | TASK_QUEUE_MAXED | 并发上限 | 等待后重试 |

### 803 错误排查

```python
# 验证节点配置
workflow = client.get_workflow_json(workflow_id)

if node_id in workflow:
    node = workflow[node_id]
    inputs = node.get("inputs", {})
    
    if field_name in inputs:
        print("✅ 配置正确")
    else:
        print(f"❌ 字段错误，可用字段: {list(inputs.keys())}")
else:
    print(f"❌ 节点不存在")
```

---

## 最佳实践

### 使用客户端封装

脚本位置: `scripts/runninghub_client.py`

```python
from scripts.runninghub_client import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

# 一键运行
result = client.run_workflow(
    workflow_id="2016195556967714818",
    node_info_list=[{
        "nodeId": "6",
        "fieldName": "text",
        "fieldValue": "prompt"
    }],
    max_retries=30,
    interval=10
)
```

### 批量处理

```python
from concurrent.futures import ThreadPoolExecutor

def process_prompt(prompt):
    return client.run_workflow(
        workflow_id="2016195556967714818",
        node_info_list=[{
            "nodeId": "6",
            "fieldName": "text",
            "fieldValue": prompt
        }]
    )

prompts = ["prompt1", "prompt2", "prompt3"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_prompt, prompts))
```

### 配置管理

脚本位置: `scripts/config_manager.py`

使用 `config_manager.py` 自动管理工作流配置：

```bash
python scripts/config_manager.py 2024416533212045314
```

---

## 相关文档

- [02-comfyui-rh-plugin.md](02-comfyui-rh-plugin.md) - 本地 ComfyUI 调用 RunningHub
- [03-comfyui-usage.md](03-comfyui-usage.md) - ComfyUI 本身使用经验
