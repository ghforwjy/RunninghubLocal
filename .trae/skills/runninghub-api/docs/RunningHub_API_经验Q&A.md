# RunningHub API 调用经验 Q&A

> 文档生成时间: 2026-02-19
> 测试工作流: 
> - Z-image-base (ID: 2016195556967714818) - 文生图
> - 风格迁移转化 • 灵感造像师 (ID: 2014552598229032961) - 图生图

---

## 一、测试概况

### 1.1 测试目标
- 验证 RunningHub API 的可用性
- 跑通完整的工作流调用流程
- 记录遇到的问题和解决方案

### 1.2 测试环境
- **API Key**: acf7d42aedee45dfa8b78ee43eec82a9
- **测试工作流**: Z-image-base
- **工作流ID**: 2016195556967714818
- **工作流作者**: Aiwood爱屋研究室

### 1.3 测试结果
✅ **文生图测试成功** - 成功调用API并生成4张图片
✅ **图生图测试成功** - 成功调用风格迁移工作流并生成7张图片

---

## 二、操作步骤记录

### 步骤1: 获取工作流ID
1. 访问 https://www.runninghub.cn/workflows
2. 浏览并选择合适的工作流（本次选择 Z-image-base）
3. 点击进入工作流详情页
4. 从URL中获取工作流ID: `2016195556967714818`

### 步骤2: 编写API调用代码
核心代码结构：
```python
import requests
import json
import time

API_KEY = "your-api-key"
WORKFLOW_ID = "2016195556967714818"
BASE_URL = "https://www.runninghub.cn"

HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
```

### 步骤3: 发起任务调用
```python
def create_task_simple():
    url = f"{BASE_URL}/task/openapi/create"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()
```

### 步骤4: 轮询查询任务状态
```python
def wait_for_task_completion(task_id, max_retries=30, interval=10):
    for i in range(max_retries):
        status_result = query_task_status(task_id)
        status = status_result.get("data")
        
        if status == "SUCCESS":
            return get_task_outputs(task_id)
        elif status == "FAILED":
            return None
        
        time.sleep(interval)
```

### 步骤5: 获取生成结果
任务成功后，调用 `/task/openapi/outputs` 接口获取图片URL。

---

## 三、图生图(Img2Img)测试记录

### 3.1 测试目标
- 上传本地图片到RunningHub
- 调用风格迁移工作流进行图生图处理
- 下载输出图片到本地

### 3.2 测试工作流
- **工作流名称**: 风格迁移转化 • 灵感造像师
- **工作流ID**: 2014552598229032961
- **工作流URL**: https://www.runninghub.cn/post/2014552598229032961

### 3.3 关键步骤

#### 步骤1: 上传图片
```python
def upload_image(image_path: Path):
    """上传图片到RunningHub"""
    upload_url = f"{BASE_URL}/task/openapi/upload"
    
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        data = {
            'apiKey': API_KEY,
            'fileType': 'input'
        }
        headers = {'Host': 'www.runninghub.cn'}
        
        resp = requests.post(upload_url, data=data, files=files, headers=headers)
        return resp.json()
```

#### 步骤2: 创建图生图任务
```python
def create_img2img_task(source_image_filename: str, style_image_filename: str):
    """创建图生图任务"""
    url = f"{BASE_URL}/task/openapi/create"
    
    # 根据工作流JSON分析:
    # - 节点 21: LoadImage - 原图输入 (要转换风格的图片)
    # - 节点 24: LoadImage - 风格参考图输入 (要提取风格的图片)
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID,
        "nodeInfoList": [
            {
                "nodeId": "21",  # 原图输入节点
                "fieldName": "image",
                "fieldValue": source_image_filename
            },
            {
                "nodeId": "24",  # 风格参考图输入节点
                "fieldName": "image",
                "fieldValue": style_image_filename
            }
        ]
    }
    
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()
```

### 3.4 测试结果
✅ **成功** - 成功上传2张图片，生成7张风格迁移后的图片

---

## 四、遇到的问题及解决方案

### 问题1: 工作流必须先运行过才能调用API
**现象**: API文档说明"目标工作流必须在网页端手动成功运行过至少一次，否则 API 调用将报错"

**解决方案**: 
- 选择已经有人运行过的工作流（如 Z-image-base 有2.8k使用量）
- 或者先登录网页端手动运行一次工作流

**经验**: 选择热门工作流可以避免这个问题

---

### 问题2: 需要登录才能在网页端运行工作流
**现象**: 点击"运行工作流"按钮后弹出登录对话框，需要手机号+验证码登录

**解决方案**:
- 本次测试直接调用API成功，无需网页端登录
- 说明该工作流之前已经被运行过

**经验**: API调用和网页端运行是独立的，只要工作流被运行过即可

---

### 问题3: 任务状态轮询时间较长
**现象**: 任务状态从 RUNNING 到 SUCCESS 大约需要4-5分钟（253秒）

**解决方案**:
- 设置合理的轮询间隔（建议10秒）
- 设置最大重试次数（建议30次，约5分钟）

**经验**: 图像生成任务耗时较长，需要耐心等待

---

### 问题4: 如何获取工作流JSON结构
**解决方案**:
```python
def get_workflow_json():
    url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
    payload = {
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    return resp.json()
```

**经验**: 获取JSON结构后可以了解工作流的节点配置，便于自定义参数

---

### 问题5: 图片上传接口返回TOKEN_INVALID错误
**现象**: 调用 `/api/openapi/upload` 返回 `{"code": 412, "msg": "TOKEN_INVALID"}`

**原因**: 上传接口URL错误

**解决方案**:
- 正确的上传接口URL是: `/task/openapi/upload`
- 不是: `/api/openapi/upload`

**代码示例**:
```python
# ❌ 错误
upload_url = f"{BASE_URL}/api/openapi/upload"

# ✅ 正确
upload_url = f"{BASE_URL}/task/openapi/upload"
```

---

### 问题6: 创建任务返回APIKEY_INVALID_NODE_INFO错误
**现象**: 调用创建任务接口返回 `{"code": 803, "msg": "APIKEY_INVALID_NODE_INFO"}`

**原因**: nodeInfoList中的nodeId或fieldName与工作流定义不匹配

**解决方案**:
1. 先调用 `/api/openapi/getJsonApiFormat` 获取工作流JSON结构
2. 分析JSON结构，找到正确的节点ID和字段名
3. 对于图生图工作流，需要找到LoadImage节点的正确ID

**示例**:
```python
# 获取工作流JSON后分析节点结构
# 节点 21: LoadImage - 原图输入
# 节点 24: LoadImage - 风格参考图输入

node_info_list = [
    {
        "nodeId": "21",  # 正确的节点ID
        "fieldName": "image",
        "fieldValue": "api/xxx.png"
    }
]
```

---

### 问题7: 如何确定工作流的输入节点ID
**解决方案**:
1. 获取工作流JSON结构
2. 查找 `class_type` 为 `LoadImage` 的节点
3. 查看节点的 `inputs` 字段，确认是否有 `image` 字段
4. 根据工作流逻辑确定哪个节点是原图输入，哪个是风格参考图输入

**经验**: 不同的工作流节点ID不同，必须通过JSON分析确定

---

## 五、API调用关键要点

### 5.1 请求头规范（必须）
```python
HEADERS = {
    "Host": "www.runninghub.cn",           # 必须精确填写
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"   # API Key格式
}
```

**注意**: 文件上传接口不需要 `Authorization` 头，只需要 `Host` 头

### 5.2 任务状态流转
```
CREATE -> QUEUED -> RUNNING -> SUCCESS/FAILED
```

### 5.3 响应数据结构
```json
{
  "code": 0,          // 0表示成功，非0表示失败
  "msg": "success",   // 返回信息
  "data": {}          // 业务数据
}
```

### 5.4 生成结果数据结构
```json
{
  "code": 0,
  "data": [
    {
      "fileUrl": "https://rh-images.xiaoyaoyou.com/...",
      "fileType": "png",
      "taskCostTime": "253",
      "nodeId": "10",
      "consumeCoins": "51"
    }
  ]
}
```

### 5.5 图生图关键接口

#### 文件上传接口
- **URL**: `POST /task/openapi/upload`
- **Content-Type**: `multipart/form-data`
- **参数**:
  - `apiKey`: API密钥
  - `fileType`: 文件类型（如 `input`）
  - `file`: 文件内容
- **返回**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "fileName": "api/xxx.png",
    "fileType": "input"
  }
}
```

#### 创建任务接口（带图片参数）
- **URL**: `POST /task/openapi/create`
- **参数**:
```json
{
  "apiKey": "your-api-key",
  "workflowId": "2014552598229032961",
  "nodeInfoList": [
    {
      "nodeId": "21",
      "fieldName": "image",
      "fieldValue": "api/xxx.png"
    }
  ]
}
```

---

## 六、费用说明

### 文生图测试消耗
- **消耗RH币**: 51币/张图片 × 4张 = 204币
- **任务耗时**: 253秒

### 图生图测试消耗
- **消耗RH币**: 约100币（7张输出图片）
- **任务耗时**: 约290秒
- **账户余额**: 充足（测试前查询有99999币）

---

## 七、可用工作流推荐

| 工作流名称 | 工作流ID | 作者 | 热度 | 说明 |
|-----------|---------|------|------|------|
| Z-image-base | 2016195556967714818 | Aiwood爱屋研究室 | 2.8k | 文生图-基础图像生成 |
| 风格迁移转化 | 2014552598229032961 | 灵感造像师 | - | 图生图-风格迁移 |
| Flux2 Klein | - | 龙神ai | 3.0k | 控油+高清放大 |
| Qwen3 TTS | - | Aquila | 4.0k | 声音克隆 |
| LTX2.0 图生视频 | - | Aiwood爱屋研究室 | 推荐 | 视频生成 |

---

## 七、参考资料

- [RunningHub API 完整文档](./RunningHub_API文档.md)
- [RunningHub 官网](https://www.runninghub.cn/)
- [工作流市场](https://www.runninghub.cn/workflows)

---

## 八、图生图调用Todo List

### 前置条件
- [ ] 确认工作流已在网页端运行过至少一次
- [ ] 获取工作流ID（从URL中提取）
- [ ] 获取API Key

### 调用步骤
1. [ ] **获取工作流JSON结构**
   - 调用 `/api/openapi/getJsonApiFormat`
   - 分析节点结构，找到LoadImage节点ID

2. [ ] **上传本地图片**
   - 调用 `/task/openapi/upload`
   - 获取返回的 `fileName`（格式: `api/xxx.png`）

3. [ ] **创建图生图任务**
   - 调用 `/task/openapi/create`
   - 在 `nodeInfoList` 中设置正确的节点ID和图片文件名

4. [ ] **轮询任务状态**
   - 调用 `/task/openapi/status`
   - 等待状态变为 `SUCCESS` 或 `FAILED`

5. [ ] **获取输出结果**
   - 调用 `/task/openapi/outputs`
   - 下载输出图片到本地

---

## 九、后续建议

1. **工作流选择**: 优先选择热度高、运行稳定的工作流
2. **参数自定义**: 通过 `nodeInfoList` 可以修改工作流参数
3. **批量处理**: 可以实现批量调用API进行自动化处理
4. **Webhook**: 生产环境建议使用Webhook回调代替轮询
5. **图片上传**: 图生图场景必须先上传图片获取fileName
6. **节点分析**: 不同工作流的节点ID不同，必须通过JSON分析确定

---

*本文档基于实际测试经验编写，如有更新请参考官方文档*
