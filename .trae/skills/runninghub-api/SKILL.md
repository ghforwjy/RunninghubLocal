---
name: "runninghub-api"
description: "RunningHub 知识库唯一入口。包含三类知识：1) RunningHub API 直接调用 2) 本地 ComfyUI 调用 RunningHub 3) ComfyUI 本身使用经验。当用户询问任何与 RunningHub、ComfyUI、文生图、图生图、视频生成相关问题时，必须首先调用此 Skill。"
---

# RunningHub 知识库

> 这是 RunningHub 和 ComfyUI 的统一知识入口，所有相关问题都从这里开始。

---

## 知识分类

本知识库分为三类，根据你的需求选择：

| 分类 | 适用场景 | 文档 |
|------|----------|------|
| **📡 RunningHub API** | 直接调用 API 进行批量处理、自动化 | [01-runninghub-api.md](docs/01-runninghub-api.md) |
| **🔌 ComfyUI + RunningHub** | 在本地 ComfyUI 中调用云端工作流 | [02-comfyui-rh-plugin.md](docs/02-comfyui-rh-plugin.md) |
| **🎨 ComfyUI 使用** | 本地 ComfyUI 部署、节点使用、工作流设计 | [03-comfyui-usage.md](docs/03-comfyui-usage.md) |

---

## 快速选择指南

### 场景 1: 我想写代码批量处理图片/视频

**选择**: 📡 RunningHub API 直接调用

**示例**:
- 批量生成图片
- 自动化视频去水印
- 集成到现有系统

**跳转**: [01-runninghub-api.md](docs/01-runninghub-api.md)

---

### 场景 2: 我想在本地 ComfyUI 里用 RunningHub 的工作流

**选择**: 🔌 ComfyUI + RunningHub 插件

**示例**:
- 本地可视化操作
- 调试 RunningHub 工作流
- 本地+云端混合处理

**跳转**: [02-comfyui-rh-plugin.md](docs/02-comfyui-rh-plugin.md)

---

### 场景 3: 我想学习 ComfyUI 本身怎么用

**选择**: 🎨 ComfyUI 使用经验

**示例**:
- 本地部署 ComfyUI
- 学习节点使用
- 设计工作流

**跳转**: [03-comfyui-usage.md](docs/03-comfyui-usage.md)

---

## 快速开始

### 方案 A: 直接 API 调用（推荐用于自动化）

```python
from runninghub_client import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

# 文生图
result = client.run_workflow(
    workflow_id="2016195556967714818",
    node_info_list=[{
        "nodeId": "6",
        "fieldName": "text",
        "fieldValue": "1 girl in classroom, anime style"
    }]
)
```

**详细文档**: [01-runninghub-api.md](docs/01-runninghub-api.md)

---

### 方案 B: ComfyUI 插件（推荐用于可视化）

1. 在 ComfyUI Manager 中搜索 `RunningHub`
2. 安装 `ComfyUI_RH_APICall` 插件
3. 重启 ComfyUI
4. 使用 RH API Call 节点调用云端工作流

**详细文档**: [02-comfyui-rh-plugin.md](docs/02-comfyui-rh-plugin.md)

---

## 常见问题速查

### 🔴 错误 803 - 节点信息无效

**原因**: 节点 ID 或字段名错误

**解决**:
1. 获取工作流 JSON 分析正确节点 ID
2. 确认字段名大小写
3. 参考: [01-runninghub-api.md#错误处理](docs/01-runninghub-api.md#错误处理)

---

### 🔴 错误 810 - 工作流未运行

**原因**: 工作流从未在网页端运行过

**解决**:
1. 登录 RunningHub 网页端
2. 找到该工作流
3. 点击"运行"按钮运行一次

---

### ❓ 如何选择调用方式？

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 批量自动化 | 直接 API | 可编程、可调度 |
| 可视化调试 | ComfyUI 插件 | 图形界面、实时预览 |
| 生产部署 | 直接 API | 稳定、可控 |
| 学习测试 | ComfyUI 插件 | 直观、易上手 |

---

## 文档和脚本清单

### 📁 完整目录结构

```
runninghub-api/
├── SKILL.md                      # 本文件（统一入口）
├── docs/                         # 文档目录
│   ├── 01-runninghub-api.md      # RunningHub API 直接调用
│   ├── 02-comfyui-rh-plugin.md   # 本地 ComfyUI 调用 RunningHub
│   ├── 03-comfyui-usage.md       # ComfyUI 本身使用经验
│   ├── RunningHub_API文档.md      # 原始完整 API 文档（备份）
│   ├── RunningHub_API_经验Q&A.md   # 原始经验 Q&A（备份）
│   ├── RunningHub_API_调用指南.md  # 原始调用指南（备份）
│   ├── RunningHub_API_测试总结.md  # 原始测试总结（备份）
│   └── init.md                    # 原始项目初始化（备份）
└── scripts/                      # 核心脚本
    ├── runninghub_client.py      # API 客户端封装
    └── config_manager.py         # 工作流配置管理
```

> **注意**: `config.py` 是应用配置文件，位于项目根目录，由 `app.py` 使用

### 📝 主要文档

| 文档 | 内容 | 行数 |
|------|------|------|
| **01-runninghub-api.md** | API 调用完整指南 | ~400 |
| **02-comfyui-rh-plugin.md** | ComfyUI 插件使用 | ~250 |
| **03-comfyui-usage.md** | ComfyUI 本身使用 | ~300 |

### 🔧 核心脚本

| 脚本 | 用途 | 使用方式 |
|------|------|----------|
| **runninghub_client.py** | API 客户端封装 | `from scripts.runninghub_client import RunningHubClient` |
| **config_manager.py** | 自动配置工作流 | `python scripts/config_manager.py <workflow_id>` |

> **注意**: `config.py` 是应用配置文件，位于项目根目录，不在 scripts 目录下

---

## 前置条件

无论使用哪种方案，都需要：

1. ✅ RunningHub 账号（基础版及以上会员）
2. ✅ API Key（32位字符串）
3. ✅ 目标工作流已在网页端成功运行过

**获取 API Key**:
1. 登录 https://www.runninghub.cn/
2. 点击右上角头像 → 「API 控制台」
3. 复制 32 位 API Key

---

## 使用流程

### 新用户入门

```
1. 阅读本 Skill 了解分类
2. 根据场景选择对应文档
3. 阅读详细文档
4. 执行示例代码
5. 遇到问题查阅 FAQ
```

### 开发者流程

```
1. 确定需求（批量/可视化）
2. 选择方案（API/插件）
3. 查阅对应文档
4. 编写/配置代码
5. 测试验证
```

---

## 更新记录

- 2026-02-20: 重构知识库，分为三类文档
- 2026-02-20: 创建统一入口 SKILL.md
- 2026-02-20: 整合原有分散文档

---

*本文档是 RunningHub 和 ComfyUI 的统一知识入口*
