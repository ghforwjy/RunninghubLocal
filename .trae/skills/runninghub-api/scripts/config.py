"""
RunningHub 去水印系统配置文件
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# API配置
API_KEY = os.getenv("RUNNINGHUB_API_KEY", "")
BASE_URL = "https://www.runninghub.cn"

# 工作流ID配置
WORKFLOW_IDS = {
    "video": {
        "landscape": "2024416533212045314",  # 新工作流（横版 16:9）
        "portrait": "2024416533212045314",   # 新工作流（竖版 9:16）- 同一工作流
    },
    # "image": {
    #     "default": "",  # 图片去水印工作流（暂未实现）
    # }
}

# 改变动作工作流配置
POSE_WORKFLOW_ID = "2024540737567727618"  # 改变人物动作工作流（新工作流）
POSE_SOURCE_IMAGE_NODE_ID = "24"  # LoadImage 节点ID - 原图
POSE_POSE_IMAGE_NODE_ID = "21"   # LoadImage 节点ID - 姿势参考图
POSE_PROMPT1_NODE_ID = "25"      # CR Text 节点ID - 提示词1（默认：图1中的人物换成图2的姿势，衣服换成比基尼）
POSE_PROMPT2_NODE_ID = "35"      # RH_Captioner 节点ID - 提示词2（姿势描述）
POSE_DEFAULT_PROMPT1 = "图1中的人物换成图2的姿势，衣服换成比基尼"  # 提示词1默认值
POSE_DEFAULT_PROMPT2 = "帮我描述图片中人物的姿势和朝向，只需要描述姿势和朝向，其他关于背景和人物信息一律不要描述，最后结果不带任何解释性文字，最后格式按照以下输出：双腿交叉坐在地上，双手撑地，头微微偏向一侧。"  # 提示词2默认值

# 视频节点ID（根据工作流JSON分析得到）
VIDEO_NODE_ID = "184"  # VHS_LoadVideo 节点
# IMAGE_NODE_ID = "21"  # 图片输入节点（未配置，如需图片功能请取消注释）

# 请求头
HEADERS = {
    "Host": "www.runninghub.cn",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 上传配置
UPLOAD_HEADERS = {
    "Host": "www.runninghub.cn"
}

# 轮询配置
MAX_RETRIES = 60
POLL_INTERVAL = 10

# 文件路径配置
INPUT_DIR = "Input"
OUTPUT_DIR = "Output"
