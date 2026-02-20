"""
测试：改变动作工作流 - 自定义图片比例/分辨率

使用示例：原图是横版，但希望输出为竖版（如9:16）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
from runninghub_client import RunningHubClient
from config import API_KEY, POSE_WORKFLOW_ID, POSE_IMAGE_NODE_ID, POSE_PROMPT_NODE_ID
from pose_workflow_adapter import adapt_pose_workflow


def get_image_size(image_path: str) -> tuple:
    """获取图片尺寸"""
    with Image.open(image_path) as img:
        return img.size


def run_pose_workflow_with_custom_size(
    image_path: str,
    prompt: str,
    mode: str = "original",
    **kwargs
):
    """
    运行改变动作工作流，支持自定义输出尺寸
    
    Args:
        image_path: 输入图片路径
        prompt: 动作描述提示词
        mode: 尺寸适配模式 (original, ratio, resolution, rotate)
        **kwargs: 其他参数
        
    Returns:
        生成结果的URL列表
    """
    # 1. 获取原图尺寸
    source_width, source_height = get_image_size(image_path)
    print(f"📷 原图尺寸: {source_width}x{source_height}")
    
    # 2. 计算目标尺寸参数
    size_params = adapt_pose_workflow(source_width, source_height, mode=mode, **kwargs)
    print(f"📐 目标尺寸参数:")
    for p in size_params:
        print(f"   {p['fieldName']}: {p['fieldValue']}")
    
    # 3. 构建node_info_list
    node_info_list = [
        # 输入图片
        {
            "nodeId": POSE_IMAGE_NODE_ID,
            "fieldName": "image",
            "fieldValue": os.path.basename(image_path)
        },
        # 动作提示词
        {
            "nodeId": POSE_PROMPT_NODE_ID,
            "fieldName": "prompt",
            "fieldValue": prompt
        }
    ]
    
    # 添加尺寸参数
    node_info_list.extend(size_params)
    
    # 4. 运行工作流
    client = RunningHubClient(api_key=API_KEY)
    result = client.run_workflow(
        workflow_id=POSE_WORKFLOW_ID,
        node_info_list=node_info_list
    )
    
    return result


def main():
    print("=" * 60)
    print("改变动作工作流 - 自定义比例/分辨率测试")
    print("=" * 60)
    
    # 测试图片路径（请替换为实际图片路径）
    test_image = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Input", "test_image.jpg")
    
    if not os.path.exists(test_image):
        print(f"\n⚠️ 测试图片不存在: {test_image}")
        print("请准备一张测试图片并修改路径")
        return
    
    # 示例1: 保持原图比例
    print("\n" + "=" * 60)
    print("示例1: 保持原图比例")
    print("=" * 60)
    result = run_pose_workflow_with_custom_size(
        image_path=test_image,
        prompt="a girl dancing",
        mode="original"
    )
    
    # 示例2: 转换为9:16竖版
    print("\n" + "=" * 60)
    print("示例2: 转换为9:16竖版")
    print("=" * 60)
    result = run_pose_workflow_with_custom_size(
        image_path=test_image,
        prompt="a girl dancing",
        mode="ratio",
        target_ratio=9/16,
        fit_mode="contain"
    )
    
    # 示例3: 指定输出分辨率
    print("\n" + "=" * 60)
    print("示例3: 指定输出分辨率 720x1280")
    print("=" * 60)
    result = run_pose_workflow_with_custom_size(
        image_path=test_image,
        prompt="a girl dancing",
        mode="resolution",
        target_width=720,
        target_height=1280,
        fit_mode="contain"
    )
    
    # 示例4: 自动旋转方向（横版→竖版）
    print("\n" + "=" * 60)
    print("示例4: 自动旋转方向（横版→竖版）")
    print("=" * 60)
    result = run_pose_workflow_with_custom_size(
        image_path=test_image,
        prompt="a girl dancing",
        mode="rotate",
        target_orientation="auto"
    )


if __name__ == "__main__":
    main()
