# 本地 ComfyUI 调用 RunningHub 指南

> 本文档涵盖：在本地 ComfyUI 环境中使用插件调用 RunningHub 云端工作流

---

## 目录

1. [方案概述](#方案概述)
2. [插件安装](#插件安装)
3. [节点使用](#节点使用)
4. [工作流示例](#工作流示例)
5. [常见问题](#常见问题)
6. [进阶技巧](#进阶技巧)

---

## 方案概述

### 两种调用方式对比

| 方式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| **直接 API 调用** | 批量处理、自动化 | 灵活、可编程 | 需要编写代码 |
| **ComfyUI 插件** | 可视化操作、本地调试 | 图形界面、实时预览 | 需要本地 ComfyUI 环境 |

### 插件简介

**ComfyUI_RH_APICall** 是 RunningHub 官方开发的 ComfyUI 自定义节点插件：

- 在本地 ComfyUI 中调用 RunningHub 云端工作流
- 支持文生图、图生图、视频生成等多种任务
- 实时显示任务进度
- 支持多种输入/输出格式（图片、视频、音频、文本、Latent）

**GitHub**: https://github.com/HM-RunningHub/ComfyUI_RH_APICall

---

## 插件安装

### 方式一：ComfyUI Manager 安装（推荐）

1. 启动 ComfyUI
2. 点击右上角 **Manager** 按钮
3. 点击 **Install Custom Nodes**
4. 搜索 `RunningHub` 或 `RH_API`
5. 找到 `ComfyUI_RH_APICall` 点击安装
6. 重启 ComfyUI

### 方式二：Git 克隆安装

```bash
# 进入 ComfyUI 自定义节点目录
cd ComfyUI/custom_nodes

# 克隆仓库
git clone https://github.com/HM-RunningHub/ComfyUI_RH_APICall.git

# 重启 ComfyUI
```

### 方式三：手动下载安装

1. 下载插件 ZIP 包
2. 解压到 `ComfyUI/custom_nodes/` 目录
3. 重启 ComfyUI

---

## 节点使用

### 核心节点

安装完成后，在 ComfyUI 右键菜单中会出现 **RunningHub** 分类：

#### 1. RH API Call 节点

**功能**: 发起 RunningHub API 调用

**输入参数**:
- `api_key`: API Key（可在节点中直接输入或从配置文件读取）
- `workflow_id`: 工作流 ID
- `prompt`: 提示词（可选）
- `image`: 输入图片（可选）
- `video`: 输入视频（可选）

**输出**:
- `image`: 生成的图片
- `video`: 生成的视频
- `text`: 生成的文本

#### 2. RH Upload Image 节点

**功能**: 上传图片到 RunningHub

**输入**:
- `image`: 本地图片

**输出**:
- `file_name`: 上传后的文件名（用于后续节点）

#### 3. RH Upload Video 节点

**功能**: 上传视频到 RunningHub

**输入**:
- `video`: 本地视频

**输出**:
- `file_name`: 上传后的文件名

---

## 工作流示例

### 示例 1: 文生图

```
[RH API Call]
    ├── api_key: your-api-key
    ├── workflow_id: 2016195556967714818
    └── prompt: "1 girl in classroom, anime style"
            ↓
        [输出图片]
```

### 示例 2: 图生图

```
[Load Image] 
      ↓
[RH Upload Image]
      ↓ (file_name)
[RH API Call]
    ├── api_key: your-api-key
    ├── workflow_id: 2014552598229032961
    └── image: [上传后的文件名]
            ↓
        [输出图片]
```

### 示例 3: 视频去水印

```
[Load Video]
      ↓
[RH Upload Video]
      ↓ (file_name)
[RH API Call]
    ├── api_key: your-api-key
    ├── workflow_id: 2024416533212045314
    └── video: [上传后的文件名]
            ↓
        [输出视频]
```

---

## 常见问题

### Q1: 插件安装后找不到节点

**解决**:
1. 确认插件已正确安装到 `custom_nodes/` 目录
2. 检查 ComfyUI 启动日志是否有报错
3. 重启 ComfyUI

### Q2: 调用返回 803 错误

**原因**: 节点 ID 或字段名错误

**解决**:
1. 在 RunningHub 网页端运行一次工作流
2. 检查工作流 ID 是否正确
3. 查看工作流 JSON 确认正确的节点 ID

### Q3: 任务一直显示 RUNNING

**原因**: 正常执行中

**说明**:
- 图片生成通常需要 2-5 分钟
- 视频处理可能需要更久
- 节点会显示实时进度

### Q4: 如何查看任务进度

**方法**:
- RH API Call 节点会显示当前状态
- 也可登录 RunningHub 网页端查看

---

## 进阶技巧

### 批量处理

使用 ComfyUI 的批量节点配合 RH 插件：

```
[Load Images Batch]
      ↓
[Iterate]
      ↓
[RH API Call] (逐个处理)
      ↓
[Save Image]
```

### 结合本地节点

可以将 RunningHub 云端处理与本地 ComfyUI 节点结合：

```
[本地 KSampler 生成] 
      ↓
[RH Upload Image]
      ↓
[RH API Call] (云端风格迁移)
      ↓
[本地后期处理]
```

### 使用配置文件

创建 `rh_config.json`：

```json
{
  "api_key": "your-api-key",
  "default_workflow": "2016195556967714818"
}
```

然后在节点中选择从配置文件读取。

---

## 与直接 API 调用的选择

| 场景 | 推荐方式 | 原因 |
|------|----------|------|
| 批量自动化处理 | 直接 API | 可编程、可调度 |
| 调试工作流 | ComfyUI 插件 | 可视化、实时预览 |
| 本地+云端混合 | ComfyUI 插件 | 灵活组合 |
| 生产环境部署 | 直接 API | 稳定、可控 |

---

## 相关文档

- [01-runninghub-api.md](01-runninghub-api.md) - RunningHub API 直接调用
- [03-comfyui-usage.md](03-comfyui-usage.md) - ComfyUI 本身使用经验
