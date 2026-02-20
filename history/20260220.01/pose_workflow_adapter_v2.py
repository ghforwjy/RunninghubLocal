"""
改变动作工作流适配器 V2 - 支持自定义目标图片比例与分辨率

正确的改造方式：
- 工作流通过 Node 39 动态读取原图尺寸
- Node 52 和 53 使用乘数(b)来调整比例
- 修改 Node 52/53 的 b 参数，而不是直接修改 Node 38
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


class PoseWorkflowAdapterV2:
    """
    改变动作工作流适配器 V2
    
    工作流关键节点：
    - Node 25: LoadImage (输入图片)
    - Node 39: Get Image Size (动态获取原图尺寸)
    - Node 52: SeargeIntegerMath-width (宽度计算: 原宽 × b)
    - Node 53: SeargeIntegerMath-height (高度计算: 原高 × b)
    - Node 38: EmptyLatentImage (使用计算后的尺寸)
    
    正确的修改方式：
    - 修改 Node 52 的 b 参数来调整宽度
    - 修改 Node 53 的 b 参数来调整高度
    """
    
    # 节点ID常量
    NODE_IMAGE_INPUT = "25"      # LoadImage 节点
    NODE_GET_SIZE = "39"         # Get Image Size 节点
    NODE_WIDTH_MATH = "52"       # 宽度计算节点 (原宽 × b)
    NODE_HEIGHT_MATH = "53"      # 高度计算节点 (原高 × b)
    NODE_LATENT_IMAGE = "38"     # EmptyLatentImage 节点
    
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
    
    def keep_original_ratio(self) -> list:
        """
        方案1: 保持原图比例生成
        
        不修改任何参数，使用工作流默认配置 (b=1)
        """
        return []
    
    def fit_to_ratio(self, target_ratio: float, 
                     fit_mode: Literal["contain", "cover", "stretch"] = "contain") -> list:
        """
        方案2: 适配到指定比例
        
        通过修改 Node 52 和 53 的乘数(b)来实现
        
        Args:
            target_ratio: 目标宽高比 (宽/高)
            fit_mode: 适配模式
                - contain: 保持原图比例，完整显示（可能有黑边）
                - cover: 保持原图比例，填满目标比例（可能裁剪）
                - stretch: 拉伸到目标比例（可能变形）
                
        Returns:
            node_info_list: 节点参数列表
        """
        if fit_mode == "stretch":
            # 直接拉伸到目标比例
            # 假设原图比例是 r，目标比例是 R
            # 宽度: 原宽 × (R/r) = 原宽 × R/r
            # 高度: 原高 × 1 = 原高
            # 但我们不知道原图比例，所以需要另一种方式
            # 更简单的方法：固定高度，调整宽度
            width_multiplier = target_ratio
            height_multiplier = 1.0
            
        elif fit_mode == "contain":
            # 保持原比例，完整显示
            # 策略：以较长边为基准
            if target_ratio < 1:  # 竖版目标
                # 高度是限制因素
                width_multiplier = target_ratio
                height_multiplier = 1.0
            else:  # 横版目标
                # 宽度是限制因素
                width_multiplier = 1.0
                height_multiplier = 1.0 / target_ratio
                
        elif fit_mode == "cover":
            # 保持原比例，填满目标
            if target_ratio < 1:  # 竖版目标
                width_multiplier = 1.0
                height_multiplier = 1.0 / target_ratio
            else:  # 横版目标
                width_multiplier = target_ratio
                height_multiplier = 1.0
        else:
            raise ValueError(f"未知的fit_mode: {fit_mode}")
        
        return [
            {
                "nodeId": self.NODE_WIDTH_MATH,
                "fieldName": "b",
                "fieldValue": str(round(width_multiplier, 4))
            },
            {
                "nodeId": self.NODE_HEIGHT_MATH,
                "fieldName": "b",
                "fieldValue": str(round(height_multiplier, 4))
            }
        ]
    
    def fit_to_resolution(self, target_width: int, target_height: int,
                          source_ratio: Optional[float] = None,
                          fit_mode: Literal["contain", "cover", "stretch", "auto"] = "auto") -> list:
        """
        方案3: 适配到指定分辨率
        
        Args:
            target_width: 目标宽度
            target_height: 目标高度
            source_ratio: 原图比例（如果已知）
            fit_mode: 适配模式
                
        Returns:
            node_info_list: 节点参数列表
        """
        target_ratio = target_width / target_height
        
        if fit_mode == "auto":
            fit_mode = "contain"
        
        # 复用 fit_to_ratio 的逻辑
        params = self.fit_to_ratio(target_ratio, fit_mode)
        
        # 额外添加直接设置尺寸的参数作为备选
        # 注意：这会覆盖通过乘数计算的方式
        direct_size_params = [
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
        
        # 返回两种方式的组合，让工作流选择合适的
        return params + direct_size_params
    
    def rotate_orientation(self, source_ratio: float,
                          target_orientation: Literal["portrait", "landscape", "auto"] = "auto") -> list:
        """
        方案4: 旋转方向（横版↔竖版转换）
        
        Args:
            source_ratio: 原图宽高比
            target_orientation: 目标方向
                - portrait: 强制竖版
                - landscape: 强制横版
                - auto: 自动翻转（横→竖，竖→横）
                
        Returns:
            node_info_list: 节点参数列表
        """
        if target_orientation == "auto":
            # 自动翻转方向
            target_ratio = 1 / source_ratio
        elif target_orientation == "portrait":
            # 强制竖版（高>宽，比例<1）
            target_ratio = min(source_ratio, 3/4)
        elif target_orientation == "landscape":
            # 强制横版（宽>高，比例>1）
            target_ratio = max(source_ratio, 4/3)
        else:
            raise ValueError(f"未知的target_orientation: {target_orientation}")
        
        return self.fit_to_ratio(target_ratio, fit_mode="contain")
    
    def get_ratio_by_name(self, ratio_name: str) -> float:
        """通过名称获取比例值"""
        if ratio_name in self.ASPECT_RATIOS:
            return self.ASPECT_RATIOS[ratio_name]
        raise ValueError(f"未知的比例名称: {ratio_name}，可选: {list(self.ASPECT_RATIOS.keys())}")


# 便捷函数
def adapt_pose_workflow_v2(
    mode: str = "original",
    **kwargs
) -> list:
    """
    便捷函数：适配改变动作工作流 V2
    
    Args:
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
        adapt_pose_workflow_v2(mode="original")
        
        # 转换为9:16竖版
        adapt_pose_workflow_v2(mode="ratio", target_ratio=9/16)
        
        # 转换为指定分辨率
        adapt_pose_workflow_v2(mode="resolution", target_width=720, target_height=1280)
        
        # 自动旋转方向（横→竖或竖→横）
        adapt_pose_workflow_v2(mode="rotate", source_ratio=4/3, target_orientation="auto")
    """
    adapter = PoseWorkflowAdapterV2()
    
    if mode == "original":
        return adapter.keep_original_ratio()
    
    elif mode == "ratio":
        target_ratio = kwargs.get("target_ratio")
        fit_mode = kwargs.get("fit_mode", "contain")
        if target_ratio is None:
            raise ValueError("ratio模式需要提供target_ratio参数")
        return adapter.fit_to_ratio(target_ratio, fit_mode)
    
    elif mode == "resolution":
        target_width = kwargs.get("target_width")
        target_height = kwargs.get("target_height")
        source_ratio = kwargs.get("source_ratio")
        fit_mode = kwargs.get("fit_mode", "auto")
        if target_width is None or target_height is None:
            raise ValueError("resolution模式需要提供target_width和target_height参数")
        return adapter.fit_to_resolution(target_width, target_height, source_ratio, fit_mode)
    
    elif mode == "rotate":
        source_ratio = kwargs.get("source_ratio")
        target_orientation = kwargs.get("target_orientation", "auto")
        if source_ratio is None:
            raise ValueError("rotate模式需要提供source_ratio参数（原图宽高比）")
        return adapter.rotate_orientation(source_ratio, target_orientation)
    
    else:
        raise ValueError(f"未知的mode: {mode}")


if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("改变动作工作流适配器 V2 - 测试示例")
    print("=" * 60)
    
    # 假设原图是横版 1024x768 (4:3 = 1.333)
    source_ratio = 4/3
    print(f"\n原图比例: {source_ratio:.3f} (横版)")
    print("-" * 60)
    
    # 测试1: 保持原比例
    print("\n1. 保持原图比例:")
    params = adapt_pose_workflow_v2(mode="original")
    print(f"   不修改任何参数")
    
    # 测试2: 转换为9:16竖版
    print("\n2. 转换为9:16竖版 (contain模式):")
    params = adapt_pose_workflow_v2(mode="ratio", target_ratio=9/16, fit_mode="contain")
    for p in params:
        print(f"   Node {p['nodeId']} ({p['fieldName']}): {p['fieldValue']}")
    
    # 测试3: 指定分辨率
    print("\n3. 适配到720x1280分辨率:")
    params = adapt_pose_workflow_v2(mode="resolution", target_width=720, target_height=1280)
    for p in params:
        print(f"   Node {p['nodeId']} ({p['fieldName']}): {p['fieldValue']}")
    
    # 测试4: 自动旋转方向
    print("\n4. 自动旋转方向 (横→竖):")
    params = adapt_pose_workflow_v2(mode="rotate", source_ratio=source_ratio, target_orientation="auto")
    for p in params:
        print(f"   Node {p['nodeId']} ({p['fieldName']}): {p['fieldValue']}")
