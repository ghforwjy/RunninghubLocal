"""
改变动作工作流适配器 - 支持自定义目标图片比例与分辨率

功能：
1. 保持原图比例生成
2. 指定目标比例生成（如原图横向→输出纵向）
3. 指定目标分辨率生成
"""
from typing import Optional, Tuple, Literal
from dataclasses import dataclass


@dataclass
class ImageSize:
    """图片尺寸"""
    width: int
    height: int
    
    @property
    def aspect_ratio(self) -> float:
        """宽高比"""
        return self.width / self.height
    
    @property
    def is_portrait(self) -> bool:
        """是否为竖版（高>宽）"""
        return self.height > self.width
    
    @property
    def is_landscape(self) -> bool:
        """是否为横版（宽>高）"""
        return self.width > self.height


class PoseWorkflowAdapter:
    """
    改变动作工作流适配器
    
    工作流关键节点：
    - Node 25: LoadImage (输入图片)
    - Node 38: EmptyLatentImage (输出尺寸控制)
    - Node 39: Get Image Size (获取原图尺寸)
    - Node 52: SeargeIntegerMath-width (宽度计算)
    - Node 53: SeargeIntegerMath-height (高度计算)
    """
    
    # 节点ID常量
    NODE_IMAGE_INPUT = "25"      # LoadImage 节点
    NODE_LATENT_IMAGE = "38"     # EmptyLatentImage 节点
    NODE_GET_SIZE = "39"         # Get Image Size 节点
    NODE_WIDTH_MATH = "52"       # 宽度计算节点
    NODE_HEIGHT_MATH = "53"      # 高度计算节点
    
    # 常用比例配置
    ASPECT_RATIOS = {
        "1:1": 1.0,
        "4:3": 4/3,
        "3:4": 3/4,
        "16:9": 16/9,
        "9:16": 9/16,
        "3:2": 3/2,
        "2:3": 2/3,
        "21:9": 21/9,
        "9:21": 9/21,
    }
    
    def __init__(self):
        pass
    
    def keep_original_ratio(self, source_width: int, source_height: int) -> list:
        """
        方案1: 保持原图比例生成
        
        Args:
            source_width: 原图宽度
            source_height: 原图高度
            
        Returns:
            node_info_list: 节点参数列表
        """
        # 直接设置EmptyLatentImage节点的宽高
        return [
            {
                "nodeId": self.NODE_LATENT_IMAGE,
                "fieldName": "width",
                "fieldValue": str(source_width)
            },
            {
                "nodeId": self.NODE_LATENT_IMAGE,
                "fieldName": "height",
                "fieldValue": str(source_height)
            }
        ]
    
    def fit_to_ratio(self, source_width: int, source_height: int, 
                     target_ratio: float, fit_mode: Literal["contain", "cover", "stretch"] = "contain") -> list:
        """
        方案2: 适配到指定比例
        
        Args:
            source_width: 原图宽度
            source_height: 原图高度
            target_ratio: 目标宽高比 (宽/高)
            fit_mode: 适配模式
                - contain: 保持原图比例，完整显示在目标比例内（可能有黑边）
                - cover: 保持原图比例，填满目标比例（可能裁剪）
                - stretch: 拉伸到目标比例（可能变形）
                
        Returns:
            node_info_list: 节点参数列表
        """
        source_ratio = source_width / source_height
        
        if fit_mode == "stretch":
            # 直接拉伸到目标比例，以原图高度为基准
            target_width = int(source_height * target_ratio)
            target_height = source_height
            
        elif fit_mode == "contain":
            # 保持原比例，完整显示
            if source_ratio > target_ratio:
                # 原图更宽，以宽度为基准
                target_width = source_width
                target_height = int(source_width / target_ratio)
            else:
                # 原图更高，以高度为基准
                target_width = int(source_height * target_ratio)
                target_height = source_height
                
        elif fit_mode == "cover":
            # 保持原比例，填满目标
            if source_ratio > target_ratio:
                # 原图更宽，以高度为基准
                target_width = int(source_height * target_ratio)
                target_height = source_height
            else:
                # 原图更高，以宽度为基准
                target_width = source_width
                target_height = int(source_width / target_ratio)
        else:
            raise ValueError(f"未知的fit_mode: {fit_mode}")
        
        # 确保是8的倍数（SD模型要求）
        target_width = (target_width // 8) * 8
        target_height = (target_height // 8) * 8
        
        return [
            {
                "nodeId": self.NODE_LATENT_IMAGE,
                "fieldName": "width",
                "fieldValue": str(target_width)
            },
            {
                "nodeId": self.NODE_LATENT_IMAGE,
                "fieldName": "height",
                "fieldValue": str(target_height)
            }
        ]
    
    def fit_to_resolution(self, source_width: int, source_height: int,
                          target_width: int, target_height: int,
                          fit_mode: Literal["contain", "cover", "stretch", "auto"] = "auto") -> list:
        """
        方案3: 适配到指定分辨率
        
        Args:
            source_width: 原图宽度
            source_height: 原图高度
            target_width: 目标宽度
            target_height: 目标高度
            fit_mode: 适配模式
                - auto: 智能选择最佳模式
                - contain: 保持比例，完整显示
                - cover: 保持比例，填满画面
                - stretch: 拉伸填充
                
        Returns:
            node_info_list: 节点参数列表
        """
        if fit_mode == "auto":
            # 智能选择：如果比例差异大使用contain，否则使用stretch
            source_ratio = source_width / source_height
            target_ratio = target_width / target_height
            ratio_diff = abs(source_ratio - target_ratio) / max(source_ratio, target_ratio)
            
            if ratio_diff < 0.2:  # 比例差异小于20%
                fit_mode = "stretch"
            else:
                fit_mode = "contain"
        
        if fit_mode == "stretch":
            final_width = target_width
            final_height = target_height
            
        elif fit_mode in ["contain", "cover"]:
            source_ratio = source_width / source_height
            target_ratio = target_width / target_height
            
            if fit_mode == "contain":
                if source_ratio > target_ratio:
                    final_width = target_width
                    final_height = int(target_width / source_ratio)
                else:
                    final_height = target_height
                    final_width = int(target_height * source_ratio)
            else:  # cover
                if source_ratio > target_ratio:
                    final_height = target_height
                    final_width = int(target_height * source_ratio)
                else:
                    final_width = target_width
                    final_height = int(target_width / source_ratio)
        else:
            raise ValueError(f"未知的fit_mode: {fit_mode}")
        
        # 确保是8的倍数
        final_width = (final_width // 8) * 8
        final_height = (final_height // 8) * 8
        
        return [
            {
                "nodeId": self.NODE_LATENT_IMAGE,
                "fieldName": "width",
                "fieldValue": str(final_width)
            },
            {
                "nodeId": self.NODE_LATENT_IMAGE,
                "fieldName": "height",
                "fieldValue": str(final_height)
            }
        ]
    
    def rotate_orientation(self, source_width: int, source_height: int,
                          target_orientation: Literal["portrait", "landscape", "auto"] = "auto") -> list:
        """
        方案4: 旋转方向（横版↔竖版转换）
        
        Args:
            source_width: 原图宽度
            source_height: 原图高度
            target_orientation: 目标方向
                - portrait: 强制竖版
                - landscape: 强制横版
                - auto: 自动翻转（横→竖，竖→横）
                
        Returns:
            node_info_list: 节点参数列表
        """
        source_ratio = source_width / source_height
        
        if target_orientation == "auto":
            # 自动翻转方向
            target_ratio = 1 / source_ratio
        elif target_orientation == "portrait":
            # 强制竖版（高>宽）
            target_ratio = min(source_ratio, 3/4)  # 使用3:4或更窄
        elif target_orientation == "landscape":
            # 强制横版（宽>高）
            target_ratio = max(source_ratio, 4/3)  # 使用4:3或更宽
        else:
            raise ValueError(f"未知的target_orientation: {target_orientation}")
        
        # 使用contain模式适配
        return self.fit_to_ratio(source_width, source_height, target_ratio, fit_mode="contain")
    
    def get_ratio_by_name(self, ratio_name: str) -> float:
        """通过名称获取比例值"""
        if ratio_name in self.ASPECT_RATIOS:
            return self.ASPECT_RATIOS[ratio_name]
        raise ValueError(f"未知的比例名称: {ratio_name}，可选: {list(self.ASPECT_RATIOS.keys())}")


# 便捷函数
def adapt_pose_workflow(
    source_width: int,
    source_height: int,
    mode: Literal["original", "ratio", "resolution", "rotate"] = "original",
    **kwargs
) -> list:
    """
    便捷函数：适配改变动作工作流
    
    Args:
        source_width: 原图宽度
        source_height: 原图高度
        mode: 适配模式
            - original: 保持原图比例
            - ratio: 适配到指定比例
            - resolution: 适配到指定分辨率
            - rotate: 旋转方向
        **kwargs: 其他参数
            
    Returns:
        node_info_list: 节点参数列表
        
    Examples:
        # 保持原图比例
        adapt_pose_workflow(1024, 768, mode="original")
        
        # 转换为9:16竖版
        adapt_pose_workflow(1024, 768, mode="ratio", target_ratio=9/16)
        
        # 转换为指定分辨率
        adapt_pose_workflow(1024, 768, mode="resolution", target_width=720, target_height=1280)
        
        # 自动旋转方向（横→竖或竖→横）
        adapt_pose_workflow(1024, 768, mode="rotate", target_orientation="auto")
    """
    adapter = PoseWorkflowAdapter()
    
    if mode == "original":
        return adapter.keep_original_ratio(source_width, source_height)
    
    elif mode == "ratio":
        target_ratio = kwargs.get("target_ratio")
        fit_mode = kwargs.get("fit_mode", "contain")
        if target_ratio is None:
            raise ValueError("ratio模式需要提供target_ratio参数")
        return adapter.fit_to_ratio(source_width, source_height, target_ratio, fit_mode)
    
    elif mode == "resolution":
        target_width = kwargs.get("target_width")
        target_height = kwargs.get("target_height")
        fit_mode = kwargs.get("fit_mode", "auto")
        if target_width is None or target_height is None:
            raise ValueError("resolution模式需要提供target_width和target_height参数")
        return adapter.fit_to_resolution(source_width, source_height, target_width, target_height, fit_mode)
    
    elif mode == "rotate":
        target_orientation = kwargs.get("target_orientation", "auto")
        return adapter.rotate_orientation(source_width, source_height, target_orientation)
    
    else:
        raise ValueError(f"未知的mode: {mode}")


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("改变动作工作流适配器 - 测试示例")
    print("=" * 60)
    
    # 假设原图是横版 1024x768 (4:3)
    source_w, source_h = 1024, 768
    print(f"\n原图尺寸: {source_w}x{source_h} (比例: {source_w/source_h:.3f})")
    print("-" * 60)
    
    # 测试1: 保持原比例
    print("\n1. 保持原图比例:")
    params = adapt_pose_workflow(source_w, source_h, mode="original")
    for p in params:
        print(f"   {p['fieldName']}: {p['fieldValue']}")
    
    # 测试2: 转换为9:16竖版
    print("\n2. 转换为9:16竖版 (contain模式):")
    params = adapt_pose_workflow(source_w, source_h, mode="ratio", target_ratio=9/16, fit_mode="contain")
    for p in params:
        print(f"   {p['fieldName']}: {p['fieldValue']}")
    w = int([p for p in params if p['fieldName'] == 'width'][0]['fieldValue'])
    h = int([p for p in params if p['fieldName'] == 'height'][0]['fieldValue'])
    print(f"   输出比例: {w/h:.3f}")
    
    # 测试3: 转换为指定分辨率
    print("\n3. 适配到720x1280分辨率 (auto模式):")
    params = adapt_pose_workflow(source_w, source_h, mode="resolution", target_width=720, target_height=1280)
    for p in params:
        print(f"   {p['fieldName']}: {p['fieldValue']}")
    w = int([p for p in params if p['fieldName'] == 'width'][0]['fieldValue'])
    h = int([p for p in params if p['fieldName'] == 'height'][0]['fieldValue'])
    print(f"   输出比例: {w/h:.3f}")
    
    # 测试4: 自动旋转方向
    print("\n4. 自动旋转方向 (横→竖):")
    params = adapt_pose_workflow(source_w, source_h, mode="rotate", target_orientation="auto")
    for p in params:
        print(f"   {p['fieldName']}: {p['fieldValue']}")
    w = int([p for p in params if p['fieldName'] == 'width'][0]['fieldValue'])
    h = int([p for p in params if p['fieldName'] == 'height'][0]['fieldValue'])
    print(f"   输出比例: {w/h:.3f}")
