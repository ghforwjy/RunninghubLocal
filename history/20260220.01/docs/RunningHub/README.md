# RunningHub 使用指南

> 完整的 RunningHub API 调用和本地 ComfyUI 集成指南
> 
> 最后更新: 2026-02-20

---

## 文档导航

本文档包含三个主要部分，按主题组织：

### 📡 [01-RunningHub-API调用](./01-RunningHub-API调用.md)

介绍如何通过 API 调用 RunningHub 云端工作流。

**适合读者**: 开发者、需要通过代码调用 RunningHub 的用户

**核心内容**:
- 快速开始（5分钟上手）
- API 认证和请求规范
- 发起任务（简易版/高级版）
- 查询任务状态和结果
- 完整示例代码（Python）
- 错误码说明

---

### 🔌 [02-本地ComfyUI与RunningHub对接](./02-本地ComfyUI与RunningHub对接.md)

介绍如何在本地 ComfyUI 中调用 RunningHub 云端工作流。

**适合读者**: ComfyUI 用户、希望可视化操作的用户

**核心内容**:
- 插件安装（3种方式）
- 核心节点说明
- 工作流设计模式
  - 文生图工作流
  - 图生图工作流
  - 改变动作工作流（示例）
- 常见问题排查

---

### 🛠️ [03-ComfyUI使用技巧](./03-ComfyUI使用技巧.md)

介绍 ComfyUI 的通用使用技巧，不仅限于 RunningHub。

**适合读者**: ComfyUI 新手和进阶用户

**核心内容**:
- 节点查找技巧（重要！）
- 工作流文件操作（权限问题）
- 节点类型对照表
- 调试技巧
- 性能优化建议

---

## 快速开始

### 方式一：API调用（推荐开发者）

```python
import requests

API_KEY = "your-api-key"
WORKFLOW_ID = "your-workflow-id"

# 发起任务
resp = requests.post(
    "https://www.runninghub.cn/task/openapi/create",
    headers={
        "Host": "www.runninghub.cn",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    },
    json={
        "apiKey": API_KEY,
        "workflowId": WORKFLOW_ID
    }
)

task_id = resp.json()["data"]["taskId"]
print(f"任务已创建: {task_id}")
```

详见 [01-RunningHub-API调用](./01-RunningHub-API调用.md)

---

### 方式二：本地ComfyUI（推荐可视化用户）

1. 安装插件：`ComfyUI_RH_APICall`
2. 配置 API Key 和 Workflow ID
3. 连接节点并运行

详见 [02-本地ComfyUI与RunningHub对接](./02-本地ComfyUI与RunningHub对接.md)

---

## 重要提示

### ⚠️ 节点类型名称问题

**常见错误**: 使用 Python 类名作为节点类型

```json
// ❌ 错误
{ "type": "StringMultiline" }

// ✅ 正确
{ "type": "PrimitiveStringMultiline" }
```

**正确做法**: 查看节点代码中的 `define_schema()` 方法，使用 `node_id` 字段。

详见 [03-ComfyUI使用技巧](./03-ComfyUI使用技巧.md) 第2章

---

### ⚠️ 文件权限问题

**常见错误**: 直接写入 ComfyUI 目录失败

**解决方案**:
1. 先写入项目目录
2. 使用 Python 脚本复制到 ComfyUI 目录

```python
import shutil
shutil.copy2(
    r"项目目录\workflow.json",
    r"ComfyUI目录\workflow.json"
)
```

详见 [03-ComfyUI使用技巧](./03-ComfyUI使用技巧.md) 第3章

---

## 相关链接

- **RunningHub 官网**: https://www.runninghub.cn/
- **工作流市场**: https://www.runninghub.cn/workflows
- **官方 API 文档**: https://www.runninghub.cn/runninghub-api-doc-cn/
- **ComfyUI 插件 GitHub**: https://github.com/HM-RunningHub/ComfyUI_RH_APICall

---

## 目录结构

```
docs/RunningHub/
├── README.md                          # 本文档 - 总入口
├── 01-RunningHub-API调用.md            # API调用指南
├── 02-本地ComfyUI与RunningHub对接.md   # 本地集成指南
├── 03-ComfyUI使用技巧.md               # ComfyUI通用技巧
└── examples/                          # 示例代码
    ├── api_call_example.py
    ├── image_to_image_workflow.json
    └── pose_change_workflow.json
```

---

*本文档基于 RunningHub API 和 ComfyUI_RH_APICall 插件实践经验整理*
