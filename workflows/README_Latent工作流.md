# RunningHub 改变动作工作流（Latent解码版）

## 工作流说明

这个工作流用于调用 RunningHub 云端工作流 `2024703585040211969`（改变动作），并将云端输出的潜空间（Latent）数据在本地解码成图片。

## 云端工作流分析

### 工作流ID
- **ID**: `2024703585040211969`
- **名称**: 改变动作
- **功能**: 将图1中的人物换成图2的姿势

### 云端工作流结构

#### 输入节点
| 节点ID | 类型 | 说明 |
|--------|------|------|
| 24 | LoadImage | 源图片（人物图） |
| 21 | LoadImage | 姿势参考图 |
| 25 | CR Text | 提示词1：服装和动作描述 |
| 35 | RH_Captioner | 提示词2：姿势描述（自动生成） |

#### 关键处理节点
| 节点ID | 类型 | 说明 |
|--------|------|------|
| 18 | UNETLoader | 加载 qwen_image_edit_2511_bf16.safetensors |
| 1 | VAELoader | 加载 qwen_image_vae.safetensors |
| 2 | CLIPLoader | 加载 qwen_2.5_vl_7b_fp8_scaled.safetensors |
| 9 | KSampler | 采样生成潜空间 |
| 52 | SaveLatentEXR | **输出潜空间（EXR格式）** |

#### 输出格式
云端工作流输出的是 **潜空间数据（Latent EXR格式）**，而不是直接输出图片。

## 本地解码方案

### 需要的VAE模型
- **模型名称**: `qwen_image_vae.safetensors`
- **用途**: 将云端生成的潜空间解码成图片
- **放置位置**: `ComfyUI/models/vae/`

### 如何获取VAE模型
1. 从HuggingFace搜索下载: `qwen_image_vae.safetensors`
2. 联系RunningHub客服获取
3. 尝试使用兼容的替代VAE（效果可能不如原模型）

## 工作流使用步骤

### 前置条件
1. 安装 ComfyUI_RH_APICall 插件
2. 获取 RunningHub API Key
3. 下载 `qwen_image_vae.safetensors` 放入 `ComfyUI/models/vae/` 目录

### 使用流程
1. **Step 1**: API设置（已配置）
2. **Step 2**: 选择源图片（人物）
3. **Step 3**: 选择姿势参考图
4. **Step 4**: 自动上传到RunningHub
5. **Step 5**: 设置提示词（已配置默认值）
6. **Step 6-8**: 节点配置（自动）
7. **Step 9**: 执行云端工作流，输出潜空间
8. **Step 10**: 本地VAE解码
9. **Step 11**: 查看解码后的图片

## 注意事项

1. **VAE模型必须匹配**: 必须使用 `qwen_image_vae.safetensors`，否则解码结果会异常
2. **网络连接**: 需要稳定的网络连接访问RunningHub API
3. **API额度**: 调用云端工作流会消耗RunningHub账户的RH币

## 文件列表

- `RunningHub_改变动作_Latent解码版.json` - 本地工作流文件
- `cloud_workflow_2024703585040211969.json` - 云端工作流JSON（分析用）
