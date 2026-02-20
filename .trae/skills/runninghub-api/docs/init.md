# RunningHub 项目初始化指南

## 新会话开始时的操作步骤

### 第一步：阅读文档

在开始任何工作之前，必须先阅读以下 MD 文件，了解 RunningHub 的工作原理和 API 调用经验：

1. **RunningHub_API文档.md** - API 完整文档，包含所有接口说明
2. **RunningHub_API_调用指南.md** - API 调用详细指南和示例
3. **RunningHub_API_经验Q&A.md** - 常见问题及解决方案
4. **RunningHub_API_测试总结.md** - 测试结果和经验总结

### 第二步：了解项目结构

```
runninghubLocal/
├── config.py              # 配置文件（工作流ID、节点ID等）- AI去水印工具的核心配置
├── config_manager.py      # 配置文件管理工具（自动更新工作流配置）
├── app.py                 # Flask 后端 API - AI去水印工具的主程序
├── templates/
│   └── index.html         # 网页前端
├── tests/                 # 测试脚本
│   ├── test_web_api.py    # API 测试
│   ├── test_config_manager.py # 配置管理器测试
│   ├── analyze_workflow.py # 工作流分析
│   ├── get_workflow_info.py # 获取工作流信息
│   └── get_video_workflow.py # 获取视频工作流JSON
├── workflow/              # 工作流JSON文件目录
│   ├── 动态水印 去除 Seedance 2.0 豆包 即梦 小云雀.json  # 当前视频去水印工作流
│   ├── video_workflow_*.json   # 从API下载的视频工作流JSON备份
│   └── improved_video_workflow.json # 改进版工作流配置（针对动态水印优化）
├── Input/                 # 输入文件目录
├── Output/                # 输出文件目录
└── *.md                   # 文档文件
```

**目录说明：**

| 目录/文件 | 用途 | 备注 |
|---------|------|------|
| `workflow/` | 存放从RunningHub下载的工作流JSON文件 | 通过API获取的工作流配置备份，以及工作流改进版本 |
| `tests/` | 测试和工具脚本 | 包含获取工作流、分析工作流的工具 |
| `Input/` | 待处理的视频/图片输入 | 本地测试用 |
| `Output/` | 处理后的输出文件 | 本地测试用 |

**核心配置文件说明：**

AI去水印工具（`app.py`）使用以下配置文件：

| 配置文件 | 用途 | 关键配置项 |
|---------|------|-----------|
| `config.py` | 工作流和API配置 | `WORKFLOW_IDS` - 视频/图片工作流ID<br>`VIDEO_NODE_ID` - 视频输入节点ID<br>`IMAGE_NODE_ID` - 图片输入节点ID<br>`API_KEY` - RunningHub API密钥 |

### 第三步：更换工作流时的标准流程

**⚠️ 重要：更换模型/工作流时，必须按以下步骤操作**

#### 方式一：使用配置管理工具（推荐）

我们提供了自动化的配置管理工具 `config_manager.py`，可以一键完成工作流配置更新。

**基本用法：**

```bash
# 使用工作流ID更新
python config_manager.py 2024416533212045314

# 使用URL更新
python config_manager.py "https://www.runninghub.cn/workflow/2024416533212045314"

# 指定类型和方向（视频去水印）
python config_manager.py 2024416533212045314 --type video_watermark --orientation landscape
python config_manager.py 2024416533212045314 --type video_watermark --orientation portrait

# 指定类型（图片去水印）
python config_manager.py 2014552598229032961 --type image_watermark

# 跳过测试
python config_manager.py 2024416533212045314 --no-test
```

**功能说明：**
- ✅ 自动从ID或URL提取工作流ID
- ✅ 自动获取工作流JSON并分析节点结构
- ✅ 自动识别视频/图片输入节点
- ✅ 自动更新 `config.py` 配置文件
- ✅ 自动测试工作流可用性

#### 方式二：手动配置（备用）

如果自动工具无法满足需求，可以手动配置：

##### 1. 获取工作流 JSON

使用 API 获取新工作流的 JSON 结构：

```python
POST /api/openapi/getJsonApiFormat
{
    "apiKey": "your-api-key",
    "workflowId": "新工作流ID"
}
```

##### 2. 分析节点结构

运行分析脚本获取节点信息：

```bash
python tests/analyze_workflow.py
```

重点查找：
- **视频输入节点**：通常是 `VHS_LoadVideo` 或 `LoadVideo` 类型
- **图片输入节点**：通常是 `LoadImage` 类型
- **字段名**：通常是 `video` 或 `image`

##### 3. 更新配置文件

根据分析结果修改 `config.py`：

```python
# 更新工作流ID
WORKFLOW_IDS = {
    "video": {
        "landscape": "新工作流ID",
        "portrait": "新工作流ID",
    },
    "image": {
        "default": "新图片工作流ID",
    }
}

# 更新节点ID（根据JSON分析结果）
VIDEO_NODE_ID = "184"  # 例如：VHS_LoadVideo 节点的ID
IMAGE_NODE_ID = "21"   # 例如：LoadImage 节点的ID
```

#### 4. 测试验证

运行测试脚本验证配置：

```bash
# 测试配置管理器
python tests/test_config_manager.py

# 测试网页API
python tests/test_web_api.py
```

### 第四步：常见问题

| 错误码 | 错误信息 | 解决方案 |
|--------|----------|----------|
| 803 | APIKEY_INVALID_NODE_INFO | 节点ID或字段名错误，重新分析JSON获取正确节点 |
| 810 | WORKFLOW_NOT_SAVED_OR_NOT_RUNNING | 工作流未运行过，需要在网页端先运行一次 |
| 380 | WORKFLOW_NOT_EXISTS | 工作流ID不存在，检查ID是否正确 |

### 第五步：服务启动

配置完成后，启动 Flask 服务：

```bash
python app.py
```

访问 http://127.0.0.1:5000 使用网页系统。

---

**记住：每次更换工作流，都必须先获取JSON -> 分析节点 -> 更新配置 -> 测试验证！**
