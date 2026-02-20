# ComfyUI 使用经验总结

> 本文档涵盖：ComfyUI 本地部署、节点使用、工作流设计、常见问题等

---

## 目录

1. [安装部署](#安装部署)
2. [核心概念](#核心概念)
3. [常用节点](#常用节点)
4. [工作流设计](#工作流设计)
5. [性能优化](#性能优化)
6. [常见问题](#常见问题)

---

## 安装部署

### Windows 便携版安装

1. 下载 ComfyUI Windows 便携版
2. 解压到任意目录
3. 运行 `run_nvidia_gpu.bat`（N卡）或 `run_cpu.bat`（CPU）

### GPU 环境检查（重要）

安装完成后，**NVIDIA 显卡用户**必须检查 PyTorch 是否与 CUDA 版本匹配，否则 GPU 无法正常工作。

#### 检查步骤

**1. 检查显卡驱动和 CUDA 版本**
```powershell
nvidia-smi
```
查看输出中的 `CUDA Version`，例如 `CUDA Version: 12.8`。

**2. 检查 PyTorch CUDA 版本**
在 ComfyUI 目录下执行：
```powershell
.\python_embeded\python.exe -c "import torch; print('PyTorch版本:', torch.__version__); print('CUDA可用:', torch.cuda.is_available())"
```

#### 版本匹配规则

| 驱动 CUDA 版本 | 推荐的 PyTorch CUDA 版本 | 说明 |
|----------------|--------------------------|------|
| CUDA 12.8 | cu126 或 cu124 | 向下兼容 |
| CUDA 12.6 | cu126 | 完全匹配 |
| CUDA 12.4 | cu124 | 完全匹配 |
| CUDA 12.1 | cu121 | 完全匹配 |

**⚠️ 重要**: PyTorch 的 CUDA 版本**不能高于**驱动支持的 CUDA 版本。

例如：
- 驱动支持 CUDA 12.8 → 可以安装 cu126、cu124、cu121
- 驱动支持 CUDA 12.4 → **不能**安装 cu126，只能安装 cu124 或更低

#### 问题诊断

如果 `CUDA可用: False`，说明 PyTorch 版本不匹配，需要重新安装。

**常见错误日志**：
```
cudaGetDeviceCount() returned cudaErrorNotSupported
CUDA not available on this system
```

#### 修复方法

**1. 卸载当前 PyTorch**
```powershell
.\python_embeded\python.exe -m pip uninstall torch torchvision torchaudio -y
```

**2. 安装匹配版本的 PyTorch**

根据你的驱动 CUDA 版本选择：

```powershell
# 如果驱动支持 CUDA 12.6+
.\python_embeded\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# 如果驱动支持 CUDA 12.4+
.\python_embeded\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 如果驱动支持 CUDA 12.1+
.\python_embeded\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**3. 验证修复**
```powershell
.\python_embeded\python.exe -c "import torch; print('CUDA可用:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

输出应为：
```
CUDA可用: True
GPU: NVIDIA GeForce RTX 4060
```

#### 快速检查脚本

创建 `check_gpu.py` 文件：
```python
import torch

print(f"PyTorch版本: {torch.__version__}")
print(f"CUDA可用: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA版本: {torch.version.cuda}")
    print(f"GPU数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
else:
    print("⚠️ GPU 不可用，请检查 PyTorch CUDA 版本是否匹配")
```

运行：
```powershell
.\python_embeded\python.exe check_gpu.py
```

### 自定义节点安装

**通过 Manager 安装**:
1. 安装 ComfyUI-Manager 插件
2. 点击 Manager → Install Custom Nodes
3. 搜索需要的节点包

**手动安装**:
```bash
cd ComfyUI/custom_nodes
git clone <节点仓库地址>
```

### 模型安装路径

| 模型类型 | 路径 |
|----------|------|
| Checkpoint | `ComfyUI/models/checkpoints/` |
| VAE | `ComfyUI/models/vae/` |
| LoRA | `ComfyUI/models/loras/` |
| ControlNet | `ComfyUI/models/controlnet/` |
| CLIP | `ComfyUI/models/clip/` |
| Upscale | `ComfyUI/models/upscale_models/` |

### Qwen-Image VAE 模型安装（RunningHub 工作流必需）

使用 RunningHub 的 Qwen-Image 工作流时，需要下载专用的 VAE 模型。

#### 下载地址

**模型文件**: `qwen_image_vae.safetensors`

**Hugging Face 下载链接**:
```
https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors
```

**文件大小**: 约 242 MB

#### 安装路径

将下载的文件放置到:
```
ComfyUI/models/vae/qwen_image_vae.safetensors
```

#### 下载方法

**使用 Python 下载（需要代理）**:
```python
import urllib.request
import os

# 设置代理（根据你的代理配置调整）
proxy_handler = urllib.request.ProxyHandler({
    'http': 'http://127.0.0.1:1080',
    'https': 'http://127.0.0.1:1080'
})
opener = urllib.request.build_opener(proxy_handler)
urllib.request.install_opener(opener)

url = 'https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors'
output_path = 'ComfyUI/models/vae/qwen_image_vae.safetensors'

urllib.request.urlretrieve(url, output_path)
print('下载完成!')
```

---

## 核心概念

### 节点（Node）

ComfyUI 的基本组成单元，每个节点执行特定功能：

- **输入**: 节点左侧的连接点
- **输出**: 节点右侧的连接点
- **参数**: 节点可调节的设置

### 工作流（Workflow）

由多个节点连接而成的完整处理流程：

```
[Load Checkpoint] → [CLIP Text Encode] → [KSampler] → [VAE Decode] → [Save Image]
```

### Latent 空间

ComfyUI 的核心概念：

- 图像在生成过程中以 Latent 形式存在
- 通过 VAE Encode 将图片转为 Latent
- 通过 VAE Decode 将 Latent 转为图片

---

## 常用节点

### 基础节点

#### Load Checkpoint

加载大模型（Checkpoint），必选节点。

**输出**:
- `MODEL`: 模型
- `CLIP`: CLIP 编码器
- `VAE`: VAE 编解码器

#### CLIP Text Encode

将文本提示词编码为模型可理解的格式。

**输入**:
- `clip`: 来自 Load Checkpoint
- `text`: 提示词文本

**输出**:
- `CONDITIONING`: 条件信息

#### KSampler

核心采样节点，控制生成过程。

**参数**:
- `seed`: 随机种子
- `steps`: 采样步数（20-30）
- `cfg`: 提示词相关性（7-8）
- `sampler_name`: 采样器名称
- `scheduler`: 调度器
- `denoise`: 去噪强度（0-1）

#### VAE Decode

将 Latent 解码为图像。

**输入**:
- `vae`: 来自 Load Checkpoint
- `samples`: Latent 数据

**输出**:
- `IMAGE`: 生成的图像

### 实用节点

#### Load Image

加载本地图片。

#### Save Image

保存生成的图片。

#### Preview Image

预览图片（不保存）。

#### Empty Latent Image

创建空白 Latent 图像。

**参数**:
- `width`: 宽度
- `height`: 高度
- `batch_size`: 批次大小

---

## 工作流设计

### 文生图基础工作流

```
[Load Checkpoint]
       ├─MODEL──────────────┐
       ├─CLIP──┐            │
       └─VAE───┼────────────┼──────┐
               │            │      │
[CLIP Text Encode]    [Empty Latent]
       │                     │
       └─CONDITIONING───────┼──────┐
                            │      │
                       [KSampler]   │
                            │      │
                            └──────┼──┐
                                   │  │
                            [VAE Decode]
                                   │
                            [Save Image]
```

### 图生图工作流

在文生图基础上：

1. 添加 `Load Image` 节点
2. 添加 `VAE Encode` 节点
3. 将图片编码为 Latent
4. 设置 `denoise` 参数（0.5-0.75）

### 高清修复工作流

```
[生成图片] → [Upscale Latent] → [KSampler] → [VAE Decode] → [Save Image]
                ↑
         [Upscale Model]
```

---

## 性能优化

### 显存优化

1. **使用 --lowvram 参数**: 低显存模式
2. **减少批次大小**: batch_size 设为 1
3. **使用 FP16**: 半精度模式
4. **清空缓存**: 定期清理显存

### 生成速度优化

1. **减少采样步数**: 20-25 步通常足够
2. **使用快速采样器**: euler_ancestral, dpmpp_2m
3. **降低分辨率**: 先生成小图再放大
4. **使用 TensorRT**: 加速推理

### 常用启动参数

```bash
# 低显存模式
--lowvram

# 正常显存模式
--normalvram

# 高显存模式
--highvram

# 仅使用 CPU
--cpu

# 监听所有 IP
--listen 0.0.0.0

# 指定端口
--port 8188

# 自动启动浏览器
--auto-launch
```

---

## 常见问题

### Q1: CUDA out of memory

**原因**: 显存不足

**解决**:
1. 使用 `--lowvram` 启动
2. 减小图片尺寸
3. 关闭其他占用显存的程序
4. 使用 FP16 模式

### Q2: 生成的图片全黑/全白

**原因**: VAE 问题或参数设置错误

**解决**:
1. 检查 VAE 是否正确加载
2. 检查提示词是否有效
3. 调整 cfg 值

### Q3: 节点显示红色错误

**原因**: 节点缺少依赖或配置错误

**解决**:
1. 检查节点是否已安装
2. 查看控制台错误信息
3. 重新安装节点

### Q4: 工作流无法加载

**原因**: 缺少节点或版本不兼容

**解决**:
1. 安装缺失的自定义节点
2. 更新 ComfyUI 到最新版
3. 检查工作流 JSON 格式

### Q5: 如何导入/导出工作流

**导出**: 右键 → Save (API Format) 或 Save (Workflow)

**导入**: 拖动 JSON 文件到 ComfyUI 界面，或使用 Load 按钮

---

## 推荐节点包

| 节点包 | 功能 | 安装方式 |
|--------|------|----------|
| ComfyUI-Manager | 节点管理 | 必装 |
| ComfyUI-Custom-Scripts | 实用脚本 | 推荐 |
| ComfyUI-ControlNet-Aux | ControlNet 预处理 | 推荐 |
| WAS Node Suite | 多功能节点 | 可选 |
| ComfyUI-VideoHelperSuite | 视频处理 | 视频相关 |
| **comfyui-easytoolkit** | 算法、编码、图像处理工具集 | 推荐 |

### comfyui-easytoolkit 安装

**GitHub**: https://github.com/fuyouawa/comfyui-easytoolkit

**功能特性**:
- 🧮 算法节点：帧计算器、字节处理、Zlib 压缩
- 🖼️ 图像处理：图像加密、批量处理、安全预览
- 🔐 编码与隐写术：Base64、隐写术编码/解码
- 📦 序列化：图像/视频序列化和反序列化
- 🎬 视频处理：视频信息解析
- 🔧 格式化工具：Base64 URL 格式化
- 🪲 调试工具：Toast 通知框、对话框

**安装步骤**:

```bash
# 进入 ComfyUI 自定义节点目录
cd ComfyUI/custom_nodes

# 克隆仓库
git clone https://github.com/fuyouawa/comfyui-easytoolkit.git

# 重启 ComfyUI
```

**使用示例**:

```
基础图像处理:
[Load Image] → [EasyToolkit/Image/图像加密器] → [Preview]

隐写术工作流:
[字节数据] → [EasyToolkit/Encoding/隐写术编码器] → [Save Image]

视频帧计算:
[Video Info] → [EasyToolkit/Algorithm/帧计算器] → [用于动画制作]
```

**节点类别**:
- `EasyToolkit/Algorithm` - 数学和数据处理
- `EasyToolkit/Image` - 图像处理
- `EasyToolkit/Video` - 视频元数据
- `EasyToolkit/Encoding` - 数据编码和隐写术
- `EasyToolkit/Serialization` - 数据序列化
- `EasyToolkit/Formatting` - 数据格式化
- `EasyToolkit/Debug` - 调试工具

---

## 学习资源

- **官方文档**: https://docs.comfy.org/
- **GitHub**: https://github.com/comfyanonymous/ComfyUI
- **工作流分享**: https://comfyworkflows.com/

---

## 相关文档

- [01-runninghub-api.md](01-runninghub-api.md) - RunningHub API 直接调用
- [02-comfyui-rh-plugin.md](02-comfyui-rh-plugin.md) - 本地 ComfyUI 调用 RunningHub
