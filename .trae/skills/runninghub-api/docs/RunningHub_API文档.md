# RunningHub API 完整文档

> 版本: 1.0  
> 更新日期: 2026-02-20  
> 文档地址: https://www.runninghub.cn/runninghub-api-doc-cn/

---

## 目录

1. [概述](#1-概述)
2. [快速开始](#2-快速开始)
3. [通用规范](#3-通用规范)
4. [ComfyUI工作流API](#4-comfyui工作流api)
5. [任务查询API](#5-任务查询api)
6. [账户API](#6-账户api)
7. [快捷创作API](#7-快捷创作api)
8. [AI应用API](#8-ai应用api)
9. [高级功能](#9-高级功能)
10. [示例代码](#10-示例代码)
11. [错误码说明](#11-错误码说明)
12. [本地 ComfyUI 调用 RunningHub 工作流](#12-本地-comfyui-调用-runninghub-工作流)
13. [常见问题FAQ](#13-常见问题faq)

---

## 1. 概述

### 1.1 API介绍

RunningHub API 允许您将 RunningHub 云端的 ComfyUI 工作流无缝集成到您的产品中，实现批量处理与自动化运行。

### 1.2 核心优势

| 优势 | 说明 |
|------|------|
| **云端执行** | 直接调用 RunningHub 算力运行各类复杂工作流 |
| **批量处理** | 支持连续发起任务与批量运行 |
| **无缝迁移** | 凡是在 RunningHub 平台上能正常运行的工作流，均可直接通过 API 调用 |

### 1.3 账户类型说明

API 调用方式一致，但根据账户类型不同，计费与权益有所区别：

| 类型 | 适用场景 | 计费模式 | 并发支持 |
|------|----------|----------|----------|
| **消费级** | 基础会员及以上 | 消耗 RH 币，费率与网页端运行工作流一致 | 默认单任务 |
| **企业级** | 需充值余额 | 按实际运行时间计费 | 支持高并发，默认支持 50 并发 |

> **注意**：如需开通企业级独占 API，请联系商务团队。

---

## 2. 快速开始

### 2.1 准备工作

在发起 API 调用前，请完成以下准备事项：

1. **注册账号**  
   访问 https://www.runninghub.cn/ 注册 RunningHub 账号

2. **开通会员**  
   开通基础版及以上会员（免费用户暂不支持 API 调用）

3. **获取 Workflow ID**  
   打开目标工作流页面，从浏览器地址栏获取 ID。  
   以 `https://www.runninghub.cn/#/workflow/1850925505116598274` 为例：  
   其中 ID 为 `1850925505116598274`

   > **注意**：目标工作流必须在网页端手动成功运行过至少一次，否则 API 调用将报错。

### 2.2 获取 API KEY

RunningHub 为每位用户分配唯一的 32 位 API KEY 用于身份验证。

**获取方式：**

1. 登录 RunningHub 官网
2. 点击右上角头像悬浮窗，进入「API 控制台」
3. 复制并妥善保管您的 API KEY（请勿泄露给第三方）

---

## 3. 通用规范

### 3.1 请求基础信息

- **基础URL**: `https://www.runninghub.cn`
- **请求格式**: JSON
- **字符编码**: UTF-8

### 3.2 请求头规范

所有请求必须包含以下 Header：

| Header | 是否必填 | 示例值 | 说明 |
|--------|----------|--------|------|
| `Host` | 是 | `www.runninghub.cn` | API 域名，必须精确填写 |
| `Content-Type` | 是 | `application/json` | 请求体类型 |
| `Authorization` | 是 | `Bearer [Your API KEY]` | 身份验证 |

> ⚠️ **注意**：某些 HTTP 客户端可能会自动添加 Host 头，但建议在接口测试或 SDK 实现时手动确认。

### 3.3 响应格式

所有响应均为 JSON 格式，包含以下字段：

```json
{
  "code": 0,          // 返回标记：0表示成功，非0表示失败
  "msg": "success",   // 返回信息
  "data": {}          // 业务数据
}
```

### 3.4 通用请求参数

#### 基础参数（必填）

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| `apiKey` | string | 是 | 用户的 API 密钥，用于身份认证 |

---

## 4. ComfyUI工作流API

### 4.1 发起ComfyUI任务（简易版）

该方式运行 workflow，相当于在不改变原有 workflow 的任何参数的情况下，直接点了一下"运行"按钮。

#### 请求信息

- **请求地址**: `POST /task/openapi/create`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥 |
| workflowId | string | 是 | 工作流模板 ID |
| addMetadata | boolean | 否 | 是否在图片中写入元信息（如提示词），默认 true |

#### 请求示例

```json
{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 返回标记：成功标记=0，非0失败 |
| msg | string | 返回信息 |
| data | object | 数据对象 |
| data.netWssUrl | string | Wss服务地址（用于WebSocket监控） |
| data.taskId | integer | 任务Id |
| data.clientId | string | 客户端ID |
| data.taskStatus | string | 任务状态: CREATE, SUCCESS, FAILED, RUNNING, QUEUED |
| data.promptTips | string | 工作流验证结果提示 |

#### 响应示例

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "netWssUrl": "wss://www.runninghub.cn:443/ws/c_instance?c_host=10.129.240.44&c_port=80&clientId=e825290b08ca2015b8f62f0bbdb5f5f6&workflowId=1904136902449209346&Rh-Comfy-Auth=...",
    "taskId": "1904737800233889793",
    "clientId": "e825290b08ca2015b8f62f0bbdb5f5f6",
    "taskStatus": "RUNNING",
    "promptTips": "{\"result\": true, \"error\": null, \"outputs_to_execute\": [\"9\"], \"node_errors\": {}}"
  }
}
```

---

### 4.2 发起ComfyUI任务（高级版）

该接口用于基于已有的工作流模板（workflow）自定义节点参数，发起 ComfyUI 图像生成任务。

#### 请求信息

- **请求地址**: `POST /task/openapi/create`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Content-Type | string | 是 | application/json | 请求体类型 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数（基础）：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥，用于身份认证 |
| workflowId | string | 是 | 工作流模板 ID，可通过平台导出获得 |
| nodeInfoList | array | 是 | 节点参数修改列表，用于在执行前替换默认参数 |

**nodeInfoList 结构说明：**

每项表示一个节点参数的修改：

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeId | string | 节点的唯一编号，来源于工作流 JSON 文件 |
| fieldName | string | 要修改的字段名，例如 text、seed、steps |
| fieldValue | any | 替换后的新值，需与原字段类型一致 |

**示例请求体：**

```json
{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346",
  "nodeInfoList": [
    {
      "nodeId": "6",
      "fieldName": "text",
      "fieldValue": "1 girl in classroom"
    },
    {
      "nodeId": "3",
      "fieldName": "seed",
      "fieldValue": "1231231"
    }
  ]
}
```

**附加参数（可选）：**

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| addMetadata | boolean | true | 是否在图片中写入元信息（如提示词） |
| webhookUrl | string | - | 任务完成后回调的 URL，平台会主动向该地址发送任务结果 |
| workflow | string | - | 自定义完整工作流（JSON 字符串），如指定则忽略 workflowId |
| instanceType | string | - | 发起任务指定实例类型，如 "plus" 表示48G显存机器 |
| usePersonalQueue | boolean | false | 独占类型任务是否入队 |

**usePersonalQueue 使用说明：**

此参数只对独占类型的 apiKey 生效，若不想自己控制排队，可设置此参数为 true，任务会自动进入排队状态，当用户持有的独占机器空闲时会自动执行；

> **注意**：单用户排队的数量限制为1000，超过会返回错误码(814, "PERSONAL_QUEUE_COUNT_LIMIT")

**instanceType 使用说明：**

若希望发起 plus 任务到48G显存机器上执行，可设置 `instanceType` 参数。例如：

```json
{
  "instanceType": "plus"
}
```

**webhookUrl 使用说明（高级）：**

若希望任务执行完成后平台自动通知结果，可设置 `webhookUrl` 参数。例如：

```json
{
  "webhookUrl": "https://your-webhook-url"
}
```

> ⚠️ **推荐仅开发人员使用此参数**

---

### 4.3 获取工作流JSON

获取指定工作流的 JSON 配置信息。

#### 请求信息

- **请求地址**: `POST /api/openapi/getJsonApiFormat`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥 |
| workflowId | string | 是 | 工作流模板 ID |

#### 请求示例

```json
{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 返回标记 |
| msg | string | 返回信息 |
| data | object | 数据对象 |
| data.prompt | string | 工作流 JSON 字符串 |

#### 响应示例

```json
{
  "code": 0,
  "msg": "SUCCESS",
  "data": {
    "prompt": "{\"3\":{\"class_type\":\"KSampler\",\"inputs\":{...}},...}"
  }
}
```

---

### 4.4 取消ComfyUI任务

取消正在运行或排队的任务。

#### 请求信息

- **请求地址**: `POST /task/openapi/cancel`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥 |
| taskId | string | 否 | 任务ID |

#### 请求示例

```json
{
  "apiKey": "your-api-key",
  "taskId": "1904152026220003329"
}
```

#### 响应示例

**成功示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": null
}
```

**任务不存在：**
```json
{
  "code": 423,
  "msg": "TASK_NOT_FOUNED",
  "data": null
}
```

---

## 5. 任务查询API

### 5.1 查询任务状态

查询指定任务的当前状态。

#### 请求信息

- **请求地址**: `POST /task/openapi/status`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥 |
| taskId | string | 否 | 任务ID |

#### 请求示例

```json
{
  "apiKey": "your-api-key",
  "taskId": "1904152026220003329"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 返回标记 |
| msg | string | 返回信息 |
| data | string | 任务状态：QUEUED, RUNNING, FAILED, SUCCESS |

#### 响应示例

```json
{
  "code": 0,
  "msg": "",
  "data": "RUNNING"
}
```

---

### 5.2 查询任务生成结果

查询任务的生成结果，包括输出文件的 URL。

#### 请求信息

- **请求地址**: `POST /task/openapi/outputs`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥 |
| taskId | string | 否 | 任务ID |

#### 请求示例

```json
{
  "apiKey": "your-api-key",
  "taskId": "1904152026220003329"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 返回标记 |
| msg | string | 返回信息 |
| data | array | 结果列表 |
| data[].fileUrl | string | 文件链接 |
| data[].fileType | string | 文件类型 |
| data[].taskCostTime | string | 任务消耗时长（秒） |
| data[].nodeId | string | 节点id |
| data[].thirdPartyConsumeMoney | null | 第三方API平台消费金额 |
| data[].consumeMoney | null | 运行时长消费金额 |
| data[].consumeCoins | string | 运行所耗用的RH币 |

#### 响应示例

**成功示例：**
```json
{
  "code": 0,
  "msg": "success",
  "data": [
    {
      "fileUrl": "https://rh-images.xiaoyaoyou.com/.../output/ComfyUI_00033_hpgko_1742822929.png",
      "fileType": "png",
      "taskCostTime": "83",
      "nodeId": "12",
      "thirdPartyConsumeMoney": null,
      "consumeMoney": null,
      "consumeCoins": "17"
    }
  ]
}
```

**任务失败会返失败原因：**
```json
{
  "code": 500,
  "msg": "任务执行失败",
  "data": null
}
```

**运行中：**
```json
{
  "code": 0,
  "msg": "任务正在运行中",
  "data": null
}
```

**排队中：**
```json
{
  "code": 0,
  "msg": "任务正在排队中",
  "data": null
}
```

---

## 6. 账户API

### 6.1 获取账户信息

获取当前账户的余额、任务数量等信息。

#### 请求信息

- **请求地址**: `POST /uc/openapi/accountStatus`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Authorization | string | 是 | Bearer [Your API KEY] | 身份验证 |

**Body 参数：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apikey | string | 否 | 用户的 API 密钥 |

#### 请求示例

```json
{
  "apikey": "your-api-key"
}
```

#### 响应参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| code | integer | 返回标记 |
| msg | string | 返回信息 |
| data | object | 数据对象 |
| data.remainCoins | string | RH币数量 |
| data.currentTaskCounts | string | 当前正在运行任务数量 |
| data.remainMoney | null | 钱包余额 |
| data.currency | null | 钱包货币单位 |
| data.apiType | string | api类型 |

#### 响应示例

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "remainCoins": "99999",
    "currentTaskCounts": "0",
    "remainMoney": "999",
    "currency": "CNY",
    "apiType": "NORMAL"
  }
}
```

---

## 7. 快捷创作API

### 7.1 关于快捷创作调用

快捷创作是一种简化的工作流调用方式，通过 webappId 和 quickCreateCode 快速调用预设的 AI 应用。

#### 请求信息

- **请求地址**: `POST /task/openapi/quick-ai-app/run`
- **Content-Type**: `application/json`

#### 请求参数

**Header 参数：**

| 参数 | 类型 | 是否必填 | 示例值 | 说明 |
|------|------|----------|--------|------|
| Host | string | 是 | www.runninghub.cn | API 域名 |
| Content-Type | string | 是 | application/json | 请求体类型 |

**Body 参数（基础）：**

| 参数名 | 类型 | 是否必填 | 说明 |
|--------|------|----------|------|
| apiKey | string | 是 | 用户的 API 密钥 |
| webappId | string | 是 | AI应用ID |
| quickCreateCode | string | 是 | 快捷创作模块code |
| nodeInfoList | array | 是 | 节点列表，用于在执行前替换默认参数 |

**nodeInfoList 结构说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| nodeId | string | 节点的唯一编号 |
| nodeName | string | 节点的名称 |
| fieldName | string | 要修改的字段名 |
| fieldType | string | 字段类型 |
| fieldValue | any | 替换后的新值 |
| description | string | 描述 |

#### 请求示例

```json
{
  "webappId": "196********290",
  "apiKey": "your-api-key",
  "quickCreateCode": "***",
  "nodeInfoList": [
    {
      "nodeId": "2",
      "nodeName": "LoadImage",
      "fieldName": "image",
      "fieldType": "IMAGE",
      "fieldValue": "61a52873b2f16cf3734dad1d20f704d32ca5f1d77896847f27a1e1ee72eb626d.jpg",
      "description": "上传图像"
    },
    {
      "nodeId": "16",
      "nodeName": "RH_Translator",
      "fieldName": "prompt",
      "fieldType": "STRING",
      "fieldValue": "图中人物的1/7比例商业模型已制作完成...",
      "description": "输入文本"
    }
  ]
}
```

---

### 7.2 获取快捷创作-模型库风格参数数据

获取快捷创作的模型库风格参数数据。

#### 请求信息

- **请求方法**: POST
- **请求路径**: （待补充）

#### 响应字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 模型ID |
| type | integer | 类型 |
| webappId | string | 应用ID |
| modelCategory | integer | 模型分类 |
| modelName | string | 模型名称 |
| modelKey | string | 模型Key |
| modelPreviewUrl | string | 模型预览图URL |
| content | string | 内容/提示词 |
| modelTrigger | string | 模型触发词 |
| modelLoar1FileName | string | LoRA1文件名 |
| modelLoar1Weight | float | LoRA1权重 |
| modelLoar2FileName | string | LoRA2文件名 |
| modelLoar2Weight | float | LoRA2权重 |

---

### 7.3 发起快捷创作任务

使用快捷创作方式发起任务。

（详细说明参考 7.1 关于快捷创作调用）

---

## 8. AI应用API

### 8.1 发起AI应用任务

通过 AI 应用方式发起任务。

#### 请求信息

- **请求方法**: POST
- **请求路径**: （待补充）

---

### 8.2 获取AI应用API调用示例

获取指定 AI 应用的 API 调用示例。

#### 请求信息

- **请求方法**: GET
- **请求路径**: （待补充）

---

## 9. 高级功能

### 9.1 WebSocket进度监控

RunningHub 支持通过 WebSocket 实时监控任务执行进度。

#### 获取 WebSocket 地址

在发起任务成功后，响应中会返回 `netWssUrl` 字段，即为 WebSocket 连接地址。

```json
{
  "data": {
    "netWssUrl": "wss://www.runninghub.cn:443/ws/c_instance?..."
  }
}
```

#### WebSocket 消息类型

| 消息类型 | 说明 |
|----------|------|
| `progress` | 节点执行进度 |
| `executing` | 正在执行的节点 |
| `execution_cached` | 缓存节点完成 |
| `execution_success` | 任务执行完成 |

#### 消息格式示例

**progress 消息：**
```json
{
  "type": "progress",
  "data": {
    "node": "3",
    "value": 10,
    "max": 20
  }
}
```

**executing 消息：**
```json
{
  "type": "executing",
  "data": {
    "node": "3"
  }
}
```

**execution_cached 消息：**
```json
{
  "type": "execution_cached",
  "data": {
    "nodes": ["4", "5"]
  }
}
```

**execution_success 消息：**
```json
{
  "type": "execution_success",
  "data": {}
}
```

---

### 9.2 Webhook回调

平台支持在任务完成后向指定 URL 发送回调通知。

#### 设置 Webhook

在发起任务时，通过 `webhookUrl` 参数指定回调地址：

```json
{
  "apiKey": "your-api-key",
  "workflowId": "1904136902449209346",
  "webhookUrl": "https://your-domain.com/webhook"
}
```

#### Webhook事件类型

| 接口 | 说明 |
|------|------|
| 获取webhook事件详情 | 查询指定 webhook 事件的详细信息 |
| 重新发送指定webhook事件 | 重新发送失败的 webhook 通知 |

---

### 9.3 文件上传

对于需要上传图片（如图生图场景），需要先上传文件获取文件标识。

#### 上传资源（图片、视频、音频、压缩包）

**接口说明：** （待补充）

#### 上传Lora-获取Lora上传地址

**接口说明：** （待补充）

---

## 10. 示例代码

### 10.1 Python完整示例

```python
import requests
import json
import time
from websocket import WebSocketApp
from typing import Dict, Set, Optional

# 配置
API_KEY = "your-api-key"
WORKFLOW_ID = "your-workflow-id"
HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json"
}
URLS = {
    "create_task": "https://www.runninghub.cn/task/openapi/create",
    "get_outputs": "https://www.runninghub.cn/task/openapi/outputs",
    "get_nodes": "https://www.runninghub.cn/api/openapi/getJsonApiFormat"
}


def create_task(node_info_list: list) -> tuple:
    """发起ComfyUI任务"""
    try:
        resp = requests.post(
            URLS["create_task"],
            headers=HEADERS,
            data=json.dumps({
                "apiKey": API_KEY,
                "workflowId": WORKFLOW_ID,
                "nodeInfoList": node_info_list
            })
        )
        resp.raise_for_status()
        result = resp.json()
        
        if result.get("code") == 0:
            data = result.get("data", {})
            return data.get("netWssUrl"), data.get("taskId")
        else:
            print(f"任务发起失败：{result}")
            return None, None
            
    except Exception as e:
        print(f"任务发起异常：{str(e)}")
        return None, None


def get_task_results(task_id: str, max_retries: int = 3):
    """获取任务结果"""
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                URLS["get_outputs"],
                headers=HEADERS,
                data=json.dumps({"apiKey": API_KEY, "taskId": task_id})
            )
            resp.raise_for_status()
            
            data = resp.json().get("data")
            if isinstance(data, list) and data:
                return data
                
            time.sleep(5)
            
        except Exception as e:
            print(f"获取结果异常：{str(e)}")
            time.sleep(5)
    
    return None


# 使用示例
if __name__ == "__main__":
    # 定义节点参数
    node_info_list = [
        {
            "nodeId": "6",
            "fieldName": "text",
            "fieldValue": "1 girl in classroom, anime style"
        }
    ]
    
    # 发起任务
    wss_url, task_id = create_task(node_info_list)
    
    if task_id:
        print(f"任务已创建，taskId: {task_id}")
        
        # 轮询获取结果
        results = get_task_results(task_id)
        if results:
            for item in results:
                print(f"生成结果：{item.get('fileUrl')}")
```

---

### 10.2 任务进度监控示例

```python
import json
from websocket import WebSocketApp

class TaskProgressMonitor:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.completed_nodes: Set[str] = set()
        self.current_node: str = ""
        
    def start_monitor(self, wss_url: str):
        def on_open(ws):
            print("📊 进度监控已启动...")
            
        def on_message(ws, msg):
            try:
                data = json.loads(msg)
                msg_type = data.get("type", "")
                
                if msg_type == "progress":
                    d = data.get("data", {})
                    node = d.get("node", "")
                    value = d.get("value", 0)
                    max_val = d.get("max", 0)
                    progress = (value / max_val * 100) if max_val > 0 else 0
                    print(f"📈 节点 {node} 进度: {progress:.1f}%")
                    
                elif msg_type == "executing":
                    node = data.get("data", {}).get("node", "")
                    print(f"▶️ 正在执行节点: {node}")
                    
                elif msg_type == "execution_cached":
                    nodes = data.get("data", {}).get("nodes", [])
                    for node in nodes:
                        print(f"📌 节点 {node}（缓存完成）")
                        
                elif msg_type == "execution_success":
                    print("✅ 任务执行完成！")
                    ws.close()
                    
            except Exception as e:
                print(f"❌ 消息处理异常：{str(e)}")
                
        def on_close(ws, code, reason):
            print(f"🔌 监控关闭：{reason}")
            
        def on_error(ws, err):
            print(f"❌ 监控错误：{str(err)}")
            
        WebSocketApp(
            wss_url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error
        ).run_forever()


# 使用示例
# monitor = TaskProgressMonitor(task_id)
# monitor.start_monitor(wss_url)
```

---

### 10.3 批量处理示例

```python
import time
from concurrent.futures import ThreadPoolExecutor

def process_single_task(prompt: str, index: int):
    """处理单个任务"""
    node_info_list = [
        {
            "nodeId": "6",
            "fieldName": "text",
            "fieldValue": prompt
        }
    ]
    
    wss_url, task_id = create_task(node_info_list)
    
    if task_id:
        print(f"[{index}] 任务 {task_id} 已创建")
        
        # 轮询等待完成
        for _ in range(60):  # 最多等待5分钟
            time.sleep(5)
            results = get_task_results(task_id)
            if results:
                print(f"[{index}] 任务完成: {results[0].get('fileUrl')}")
                return results
                
    return None


# 批量处理
prompts = [
    "1 girl in classroom",
    "1 boy in park",
    "a cat on the roof",
    # ... 更多提示词
]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(process_single_task, prompt, i)
        for i, prompt in enumerate(prompts)
    ]
    
    for future in futures:
        result = future.result()
        if result:
            print(f"结果: {result}")
```

---

## 11. 错误码说明

### 11.1 错误码总览表

| 错误码 | 错误标识 | 中文含义与处理建议 |
|--------|----------|-------------------|
| 301 | PARAMS_INVALID | 参数错误。必填参数缺失或类型不符，请核对文档。 |
| 380 | WORKFLOW_NOT_EXISTS | 工作流不存在。指定的工作流 ID 无效。 |
| 412 | TOKEN_INVALID | API 路径拼写错误。请检查接口 URL 是否正确。 |
| 415 | TASK_INSTANCE_MAXED | 独占型 API 机器数不足。资源紧张，请等待 30-120 秒后重试。 |
| 416 | TASK_CREATE_FAILED_BY_NOT_ENOUGH_WALLET | 钱包余额不足。账户余额不足，请充值。 |
| 421 | TASK_QUEUE_MAXED | 共享型 API 并发上限。并发达上限，请自行排队或联系扩容。 |
| 423 | TASK_NOT_FOUNED | 未找到指定任务。任务 ID 错误或已被清理。 |
| 433 | VALIDATE_PROMPT_FAILED | 工作流校验未通过。节点参数或连接逻辑错误，请查看 msg 详情。 |
| 435 | TASK_USER_EXCLAPI_INSTANCE_NOT_FOUND | 未找到任务用户 API 实例。48G显存机器调用时请添加参数 "instanceType": "plus"。 |
| 436 | TASK_USER_EXCLAPI_REQUIRED | 独占会员到期。独占资源服务已到期。 |
| 500 | UNKNOWN_ERROR | 未知错误。服务端异常，请联系技术支持。 |
| 801 | APIKEY_UNSUPPORTED_FREE_USER | 免费用户不支持 API Key。请升级账户等级。 |
| 802 | APIKEY_UNAUTHORIZED | API Key 未授权/已失效。密钥错误或已被禁用。 |
| 803 | APIKEY_INVALID_NODE_INFO | nodeInfoList 不匹配。节点 ID 或字段名与工作流定义不一致。 |
| 804 | APIKEY_TASK_IS_RUNNING | 任务正在运行中。请勿重复提交，建议轮询结果。 |
| 805 | APIKEY_TASK_STATUS_ERROR | 任务状态异常。任务可能已被中断或取消。 |
| 806 | APIKEY_USER_NOT_FOUND | 未找到对应用户。Key 关联的用户信息不存在。 |
| 807 | APIKEY_TASK_NOT_FOUND | 未找到对应任务。无法查询到该 ID 的任务记录。 |
| 808 | APIKEY_UPLOAD_FAILED | 文件上传失败。存储服务异常或网络中断。 |
| 809 | APIKEY_FILE_SIZE_EXCEEDED | 文件大小超出限制。上传的文件体积过大。 |
| 810 | WORKFLOW_NOT_SAVED_OR_NOT_RUNNING | 未保存或未运行工作流。请在平台保存并手动运行一次该工作流。 |
| 811 | CORPAPIKEY_INVALID | 企业版 API Key 无效。密钥错误或无企业权限。 |
| 812 | CORPAPIKEY_INSUFFICIENT_FUNDS | 企业版余额不足。企业账户资金耗尽。 |
| 813 | APIKEY_TASK_IS_QUEUED | 任务已排队。任务已受理，无需重试。 |
| 814 | PERSONAL_QUEUE_COUNT_LIMIT | 个人队列数量限制。单用户排队的数量限制为1000。 |
| 901 | WEBAPP_NOT_EXISTS | WebApp 不存在。关联的应用 ID 错误。 |
| 1000 | Unknown error, please retry or contact support | 未知错误。请重试或联系支持。 |
| 1001 | Invalid URL, please check your link | 请求链接无效。请检查您的调用链接。 |
| 1002 | Invalid API Key, please check your credentials | API Key 无效。请检查您的密钥。 |
| 1003 | Rate limit exceeded, please slow down requests | 请求频率超限。请降低请求速度。 |
| 1004 | Task not found, please check the task ID | 任务不存在或已过期。请检查任务 ID。 |
| 1005 | Internal server error, please retry later | 系统内部错误。请稍后重试。 |
| 1006 | Task execution timed out, please retry | 任务执行超时。请重试。 |
| 1007 | Invalid parameters, please check your input | 参数校验失败。请检查输入参数。 |
| 1008 | File size limit exceeded | 文件大小超出限制。请压缩文件后重试。 |
| 1009 | HTTP method not supported, please check documentation | 请求方法不支持。请查阅文档确认 (GET/POST)。 |
| 1010 | Service unavailable, please retry later | 服务暂不可用。请稍后重试。 |
| 1011 | System is currently busy, please retry later | 系统繁忙。请求量大，请稍后重试。 |
| 1012 | Service response exception, please contact support or retry later | 上游服务响应异常。请联系技术支持或稍后重试。 |
| 1013 | File processing failed, please check the URL or retry | 文件处理失败。请检查链接或重新上传。 |
| 1014 | Access Denied: Standard Model API is restricted to Enterprise-Shared API Keys only. | 访问被拒绝。标准模型 API 仅限企业级-共享 API Key 调用。 |
| 1015 | Generation failed, please try again. | 生成失败。请重试。 |
| 1101 | Node info error | 节点信息异常。工作流节点数据解析错误。 |
| 1501 | Content verification failed, please modify your prompt or images | 内容审核未通过。请修改提示词或图片。 |
| 1504 | Model timed out, please retry later | 模型响应超时。请稍后重试。 |
| 1505 | Photorealistic real people are prohibited, please modify your prompt or image | 禁止生成真人。请修改提示词或参考图。 |

---

## 12. 本地 ComfyUI 调用 RunningHub 工作流

除了直接调用 REST API 外，RunningHub 还提供了 **ComfyUI 插件**，让你可以在本地 ComfyUI 环境中直接调用 RunningHub 云端的工作流。

### 12.1 插件简介

**ComfyUI_RH_APICall** 是 RunningHub 官方开发的 ComfyUI 自定义节点插件，提供以下核心功能：

- 在本地 ComfyUI 中调用 RunningHub 云端工作流
- 支持文生图、图生图、视频生成等多种任务类型
- 实时显示任务进度
- 支持多种输入/输出格式（图片、视频、音频、文本、Latent）

**GitHub 地址**: https://github.com/HM-RunningHub/ComfyUI_RH_APICall

### 12.2 安装方法

#### 方式一：通过 ComfyUI Manager 安装（推荐）

1. 启动 ComfyUI
2. 点击右上角 **Manager** 按钮
3. 点击 **Install Custom Nodes**
4. 搜索 `RunningHub` 或 `RH_API`
5. 找到 `ComfyUI_RH_APICall` 点击安装
6. 重启 ComfyUI

#### 方式二：Git 克隆安装

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/HM-RunningHub/ComfyUI_RH_APICall
```

#### 方式三：手动下载安装

1. 访问 https://github.com/HM-RunningHub/ComfyUI_RH_APICall
2. 点击 `Code` → `Download ZIP`
3. 解压到 `ComfyUI/custom_nodes/` 目录
4. 重命名文件夹为 `ComfyUI_RH_APICall`（去掉 `-main` 后缀）
5. 重启 ComfyUI

### 12.3 核心节点说明

| 节点名称 | 功能说明 |
|---------|---------|
| **RH_SettingsNode** | 配置 RunningHub API 设置（API Key、工作流ID等） |
| **RH_NodeInfoListNode** | 配置工作流节点参数（nodeId、fieldName、fieldValue） |
| **RH_ExecuteNode** | 执行 RunningHub 云端工作流 |
| **RH_ImageUploaderNode** | 上传本地图片到 RunningHub 服务器 |
| **RH_AnythingToString** | 将任意类型转换为字符串 |

### 12.4 基础工作流示例

```
[RH_SettingsNode]  -->  [RH_NodeInfoListNode]  -->  [RH_ExecuteNode]  -->  [输出节点]
     ↑                          ↑                      ↓
  API Key +                 配置节点参数            获取图片/
  Workflow ID              (提示词/种子等)          视频结果
```

### 12.5 支持的输入/输出类型

| 类型 | 支持情况 |
|------|---------|
| **输入** | 图片(Image)、视频(Video)、音频(Audio)、文本(Text)、Latent |
| **输出** | 图片(Images)、视频帧(Video frames)、Latent、文本(Text)、音频(Audio) |
| **多视频输出** | 支持 5 个独立视频输出端口 (video1-video5) |

### 12.6 使用步骤

1. **添加 RH_SettingsNode 节点**
   - 配置 RunningHub API Key
   - 配置 Workflow ID（从 RunningHub 工作流页面获取）

2. **添加 RH_NodeInfoListNode 节点**
   - 用于修改 RunningHub 工作流的节点参数
   - 可以设置：提示词、种子、生成批次、视频参数等
   - 支持链式连接多个节点

3. **添加 RH_ExecuteNode 节点**
   - 连接 RH_SettingsNode 和 RH_NodeInfoListNode
   - 执行云端工作流

4. **连接输出节点**
   - 图片输出：连接到 Save Image 或 Preview Image
   - 视频输出：支持直接输出 ComfyUI VIDEO 格式

### 12.7 高级功能

- **实时进度显示**：ComfyUI 进度条显示任务执行进度
- **网络容错**：WebSocket 连接中断时自动切换到 HTTP 轮询
- **并发控制**：支持多任务并发执行
- **AI WebAPP 调用**：支持调用 RunningHub 的快捷创作应用

### 12.8 示例工作流

插件的 `examples` 目录下提供了完整示例：

- **文生图工作流** (`rh_text_to_image.json`)
- **图生图工作流** (`rh_image_to_image.json`)
- **视频生成工作流** (`rh_video_generation.json`)
- **Photoshop 连接示例**

### 12.9 节点类型对照表

| 显示名称 | 类名 | 工作流 type 字段 |
|---------|------|-----------------|
| RH Settings | RH_SettingsNode | `RH_SettingsNode` |
| RH Node Info List | RH_NodeInfoListNode | `RH_NodeInfoListNode` |
| RH Execute | RH_ExecuteNode | `RH_ExecuteNode` |
| RH Image Uploader | RH_ImageUploaderNode | `RH_ImageUploaderNode` |
| RH Anything to String | AnyToStringNode | `AnyToStringNode` |

### 12.10 注意事项

1. **API Key**：需要从 RunningHub 官网获取
2. **工作流要求**：目标工作流必须在 RunningHub 网页端成功运行过至少一次
3. **网络要求**：需要能访问 RunningHub 服务
4. **费用**：调用会消耗 RunningHub 账户的 RH 币
5. **节点类型**：工作流 JSON 中的 `type` 字段必须使用正确的节点类型名称（不是类名）

---

## 13. 常见问题FAQ

### Q1: API 如何计费？

**A:** 消费级 API 没有独立计费体系，价格与在网页端运行同一个工作流完全一致，仅通过 API 触发执行。

### Q2: 如何实现高并发（同时发起多个任务）？

**A:** 需要开通企业级 API，默认支持 50 并发。如需更高并发，请联系商务团队。

### Q3: 如果工作流包含多个 Save 节点，结果如何返回？

**A:** 查询任务生成结果接口会返回一个数组，每个元素对应一个 Save 节点的输出文件。

### Q4: 图生图 (Img2Img) 场景下如何上传图片？

**A:** 需要先调用文件上传接口获取文件标识，然后在 nodeInfoList 中引用该标识。

### Q5: 返回 `APIKEY_INVALID_NODE_INFO` 错误？

**A:** 请检查 nodeInfoList 中的 nodeId 和 fieldName 是否与工作流定义一致。可以通过"获取工作流Json"接口查看工作流的完整结构。

### Q6: 返回 `APIKEY_TASK_STATUS_ERROR` 错误？

**A:** 任务可能已被中断或取消，建议重新发起任务。

### Q7: 任务一直处于 QUEUED 状态？

**A:** 表示任务正在排队等待执行。RunningHub 平台需要排队，只有排队成功处于运行状态时才能获取到 WebSocket 链接。

### Q8: 如何获取任务执行的实时进度？

**A:** 发起任务后会返回 `netWssUrl`，通过 WebSocket 连接该地址即可接收实时进度消息。

### Q9: Webhook 回调失败怎么办？

**A:** 可以使用"重新发送指定webhook事件"接口手动触发重发，或检查您的回调地址是否正确响应。

### Q10: 免费用户可以使用 API 吗？

**A:** 不可以，需要开通基础版及以上会员才能使用 API。

### Q11: ComfyUI 插件中的节点显示"缺失"？

**A:** 请检查工作流 JSON 中的 `type` 字段是否正确：
- 必须使用节点注册时的 `node_id`，而不是 Python 类名
- 例如：`PrimitiveStringMultiline` 是正确的，`StringMultiline` 是错误的

### Q12: 如何找到正确的节点类型名称？

**A:** 有两种方法：
1. 查看节点代码中的 `define_schema()` 方法，找到 `node_id` 字段
2. 在 ComfyUI 中拖拽节点到画布，然后导出工作流，查看 `type` 字段

### Q13: RH_NodeInfoListNode 的 fieldValue 如何接收输入？

**A:** `RH_NodeInfoListNode` 有一个 `fieldValue` 输入端口（类型 `STRING`），可以接收：
- `RH_ImageUploaderNode` 的 `filename` 输出（上传后的文件名）
- `PrimitiveStringMultiline` 的 `STRING` 输出（文本输入）
- 其他字符串类型节点的输出

### Q14: 工作流文件写入ComfyUI目录失败？

**A:** 直接写入 `ComfyUI/user/default/workflows/` 可能因权限不足而失败。

**解决方案**：
1. 先将工作流文件写入项目目录（如 `D:\mycode\runninghubLocal\workflows\`）
2. 使用 Python 脚本复制到 ComfyUI 目录

### Q15: 如何在ComfyUI中查找特定节点？

**A:** 不要带筛选条件搜索节点，因为节点名称可能不符合直觉。

**正确做法**：
1. 遍历所有节点类（不带任何筛选条件）
2. 人工查找需要的节点
3. 确认节点类型名称（查看 `define_schema()` 中的 `node_id`）

**示例**：多行文本输入节点叫 `PrimitiveStringMultiline`，不是 `StringMultiline`，如果搜索时带 "string" 或 "text" 筛选条件，就会漏掉这个节点。

---

## 14. 经验总结与最佳实践

### 14.1 工作流设计经验

#### 图片输入流程
```
LoadImage (本地加载) 
    ↓
RH_ImageUploaderNode (上传到RunningHub) 
    ↓
RH_NodeInfoListNode (接收filename，设置nodeId和fieldName)
    ↓
RH_ExecuteNode (执行)
```

#### 文本输入流程
```
PrimitiveStringMultiline (本地文本输入)
    ↓
RH_NodeInfoListNode (接收STRING，设置nodeId、fieldName="text")
    ↓
RH_ExecuteNode (执行)
```

### 14.2 常见错误及解决方案

| 错误现象 | 原因 | 解决方案 |
|---------|------|---------|
| 节点显示"缺失" | `type` 字段使用了类名而非 `node_id` | 使用 `define_schema()` 中的 `node_id` |
| `StringMultiline` 缺失 | 使用了类名而非节点ID | 改为 `PrimitiveStringMultiline` |
| 图片上传失败 | 网络问题或文件过大 | 检查网络，压缩图片 |
| 任务执行失败 | 工作流未在网页端运行过 | 先在RunningHub网页端运行一次 |
| 节点参数不生效 | nodeId 或 fieldName 错误 | 通过"获取工作流JSON"接口核对 |
| 文件写入失败 | 权限不足，直接写入ComfyUI目录被拒绝 | 先写入项目目录，再复制到目标位置 |
| 找不到节点 | 搜索时使用了筛选条件，漏掉了实际节点 | 遍历所有节点，不要带筛选条件 |

### 14.3 文件操作最佳实践

#### 工作流文件写入
**问题**：直接写入 `ComfyUI/user/default/workflows/` 目录可能因权限不足而失败

**解决方案**：
1. 先将工作流文件写入项目目录（如 `D:\mycode\runninghubLocal\workflows\`）
2. 使用 Python 脚本复制到 ComfyUI 目录

```python
import shutil

# 先写入项目目录
source = r"D:\mycode\runninghubLocal\workflows\workflow.json"
dest = r"D:\ComfyUI_windows_portable\ComfyUI\user\default\workflows\workflow.json"

# 再复制到目标位置
shutil.copy2(source, dest)
```

### 14.4 查找ComfyUI节点的正确方法

#### 错误做法
```python
# 不要带筛选条件，会漏掉节点
keywords = ['string', 'text']  # ❌ 不要这样做
for cls in classes:
    if any(kw in cls.lower() for kw in keywords):
        print(cls)
```

#### 正确做法
```python
# 遍历所有节点，不要带任何筛选条件
for cls in all_classes:
    print(f"  {cls}")
    
# 然后人工查找需要的节点
# 例如：PrimitiveStringMultiline 不一定包含 "string" 或 "text" 关键字
```

**经验**：ComfyUI 节点命名不一定符合直觉，例如：
- 多行文本输入节点叫 `PrimitiveStringMultiline`，不是 `StringMultiline`
- 如果不遍历所有节点，很容易漏掉正确的节点

### 14.5 调试技巧

1. **获取工作流JSON**：使用 `/api/openapi/getJsonApiFormat` 接口获取云端工作流结构，核对 nodeId 和 fieldName
2. **查看节点信息**：在ComfyUI中右键节点 → "查看节点信息"，确认节点类型
3. **导出工作流**：在ComfyUI中导出工作流JSON，检查 `type` 字段是否正确
4. **查看日志**：ComfyUI启动日志会显示节点加载情况，检查是否有导入错误

### 14.6 性能优化建议

1. **图片压缩**：上传前压缩图片，减少上传时间和流量
2. **批量处理**：使用并发或队列机制批量处理任务
3. **缓存结果**：对于相同参数的任务，考虑缓存结果避免重复执行
4. **合理设置轮询间隔**：查询任务状态时，设置合理的轮询间隔（建议5-10秒）

---

## 附录

### A. 相关链接

- **官网**: https://www.runninghub.cn/
- **API 文档**: https://www.runninghub.cn/runninghub-api-doc-cn/
- **工作流市场**: https://www.runninghub.cn/#/market
- **ComfyUI 插件 GitHub**: https://github.com/HM-RunningHub/ComfyUI_RH_APICall

### B. 技术支持

如有问题，请联系 RunningHub 官方技术支持团队。

---

*文档生成时间: 2026-02-20*  
*基于 RunningHub API 文档版本: 2025-03*  
*更新内容: 添加本地ComfyUI插件使用经验总结和常见问题*
