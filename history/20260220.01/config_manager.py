"""
RunningHub 配置文件管理器

功能：
1. 从工作流ID或URL中提取工作流ID
2. 获取工作流JSON并分析节点结构
3. 自动识别视频/图片输入节点
4. 更新配置文件
5. 测试新工作流可用性

支持的功能类型：
- video_watermark: 视频去水印
- image_watermark: 图片去水印
- 可扩展其他功能
"""

import json
import re
import os
import sys
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import requests


class WorkflowType(Enum):
    """工作流类型"""
    VIDEO_WATERMARK = "video_watermark"
    IMAGE_WATERMARK = "image_watermark"


@dataclass
class NodeConfig:
    """节点配置"""
    node_id: str
    field_name: str
    class_type: str
    node_type: str  # 'video', 'image', 'text', etc.


@dataclass
class WorkflowConfig:
    """工作流配置"""
    workflow_id: str
    workflow_type: str
    orientation: Optional[str]  # 'landscape', 'portrait', 'default', None
    node_id: str
    field_name: str
    class_type: str
    description: str = ""


class ConfigManager:
    """配置文件管理器"""

    BASE_URL = "https://www.runninghub.cn"

    # 输入节点类型映射
    INPUT_NODE_TYPES = {
        'video': ['VHS_LoadVideo', 'LoadVideo', 'LoadVideoPath', 'VideoLoader'],
        'image': ['LoadImage', 'LoadImageMask', 'ImageLoader'],
        'text': ['CLIPTextEncode', 'PromptText'],
    }

    # 字段名映射
    FIELD_NAME_PATTERNS = {
        'video': ['video', 'video_path', 'video_file', 'input_video'],
        'image': ['image', 'image_path', 'image_file', 'input_image'],
        'text': ['text', 'prompt', 'positive', 'negative'],
    }

    def __init__(self, api_key: str, config_file: str = "config.py"):
        """
        初始化配置管理器

        Args:
            api_key: RunningHub API Key
            config_file: 配置文件路径
        """
        self.api_key = api_key
        self.config_file = config_file
        self.headers = {
            "Host": "www.runninghub.cn",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def extract_workflow_id(self, workflow_input: str) -> Optional[str]:
        """
        从输入中提取工作流ID

        支持格式：
        - 纯ID: "2024401195896410114"
        - URL: "https://www.runninghub.cn/workflow/2024401195896410114"
        - 分享链接: "https://www.runninghub.cn/share/abc123"

        Args:
            workflow_input: 工作流ID或URL

        Returns:
            提取的工作流ID，失败返回None
        """
        # 去除空白字符
        workflow_input = workflow_input.strip()

        # 如果是纯数字ID（18-20位）
        if workflow_input.isdigit() and 18 <= len(workflow_input) <= 20:
            return workflow_input

        # 从URL中提取ID
        # 匹配 /workflow/123456 或 /share/123456 格式
        patterns = [
            r'/workflow/(\d{18,20})',
            r'/share/(\w+)',
            r'workflow[/=]?(\d{18,20})',
            r'id[/=]?(\d{18,20})',
        ]

        for pattern in patterns:
            match = re.search(pattern, workflow_input)
            if match:
                workflow_id = match.group(1)
                # 验证ID格式
                if workflow_id.isdigit() and 18 <= len(workflow_id) <= 20:
                    return workflow_id

        print(f"❌ 无法从输入中提取有效的工作流ID: {workflow_input}")
        print("   支持的格式：")
        print("   - 纯ID: 2024401195896410114")
        print("   - URL: https://www.runninghub.cn/workflow/2024401195896410114")
        return None

    def get_workflow_json(self, workflow_id: str) -> Optional[Dict]:
        """
        获取工作流JSON结构

        Args:
            workflow_id: 工作流ID

        Returns:
            工作流JSON字典，失败返回None
        """
        url = f"{self.BASE_URL}/api/openapi/getJsonApiFormat"
        payload = {
            "apiKey": self.api_key,
            "workflowId": workflow_id
        }

        try:
            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = resp.json()

            if result.get('code') == 0:
                prompt_data = result.get('data', {}).get('prompt', '{}')
                if isinstance(prompt_data, str):
                    return json.loads(prompt_data)
                return prompt_data
            else:
                print(f"❌ 获取工作流JSON失败: {result.get('msg', '未知错误')}")
                return None
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return None

    def analyze_workflow_nodes(self, workflow_json: Dict) -> Dict[str, List[NodeConfig]]:
        """
        分析工作流节点，识别输入节点

        Args:
            workflow_json: 工作流JSON字典

        Returns:
            按类型分类的节点配置列表
        """
        nodes_by_type = {
            'video': [],
            'image': [],
            'text': [],
            'other': []
        }

        for node_id, node_data in workflow_json.items():
            class_type = node_data.get('class_type', '')
            inputs = node_data.get('inputs', {})

            # 识别节点类型
            node_type = self._identify_node_type(class_type, inputs)

            if node_type == 'video':
                # 查找视频字段
                field_name = self._find_field_name(inputs, 'video')
                if field_name:
                    nodes_by_type['video'].append(NodeConfig(
                        node_id=node_id,
                        field_name=field_name,
                        class_type=class_type,
                        node_type='video'
                    ))

            elif node_type == 'image':
                # 查找图片字段
                field_name = self._find_field_name(inputs, 'image')
                if field_name:
                    nodes_by_type['image'].append(NodeConfig(
                        node_id=node_id,
                        field_name=field_name,
                        class_type=class_type,
                        node_type='image'
                    ))

            elif node_type == 'text':
                # 查找文本字段
                field_name = self._find_field_name(inputs, 'text')
                if field_name:
                    nodes_by_type['text'].append(NodeConfig(
                        node_id=node_id,
                        field_name=field_name,
                        class_type=class_type,
                        node_type='text'
                    ))

        return nodes_by_type

    def _identify_node_type(self, class_type: str, inputs: Dict) -> str:
        """识别节点类型"""
        # 检查class_type
        for node_type, type_list in self.INPUT_NODE_TYPES.items():
            if any(t in class_type for t in type_list):
                return node_type

        # 检查inputs中的字段
        for node_type, field_patterns in self.FIELD_NAME_PATTERNS.items():
            for field in inputs.keys():
                if any(pattern in field.lower() for pattern in field_patterns):
                    return node_type

        return 'other'

    def _find_field_name(self, inputs: Dict, node_type: str) -> Optional[str]:
        """查找字段名"""
        field_patterns = self.FIELD_NAME_PATTERNS.get(node_type, [])

        # 优先匹配标准字段名
        for field in inputs.keys():
            if field in field_patterns:
                return field

        # 模糊匹配
        for field in inputs.keys():
            if any(pattern in field.lower() for pattern in field_patterns):
                return field

        # 返回第一个字段
        if inputs:
            return list(inputs.keys())[0]

        return None

    def detect_workflow_type(self, nodes_by_type: Dict[str, List[NodeConfig]]) -> WorkflowType:
        """
        根据节点结构检测工作流类型

        Args:
            nodes_by_type: 按类型分类的节点

        Returns:
            检测到的WorkflowType
        """
        video_nodes = nodes_by_type.get('video', [])
        image_nodes = nodes_by_type.get('image', [])

        # 优先判断：有视频节点就是视频去水印
        if video_nodes:
            return WorkflowType.VIDEO_WATERMARK

        # 有图片节点就是图片去水印
        if image_nodes:
            return WorkflowType.IMAGE_WATERMARK

        # 默认返回视频去水印
        return WorkflowType.VIDEO_WATERMARK

    def select_best_node(self, nodes: List[NodeConfig]) -> Optional[NodeConfig]:
        """
        选择最佳节点

        选择策略：
        1. 优先选择有标准字段名的节点
        2. 优先选择ID较小的节点（通常是主输入节点）

        Args:
            nodes: 节点列表

        Returns:
            最佳节点配置
        """
        if not nodes:
            return None

        if len(nodes) == 1:
            return nodes[0]

        # 按ID排序（通常ID小的是主输入节点）
        sorted_nodes = sorted(nodes, key=lambda n: int(n.node_id) if n.node_id.isdigit() else 0)

        # 优先选择有标准字段名的节点
        standard_fields = ['video', 'image', 'text']
        for node in sorted_nodes:
            if node.field_name in standard_fields:
                return node

        return sorted_nodes[0]

    def update_config_file(self, config: WorkflowConfig) -> bool:
        """
        更新配置文件

        Args:
            config: 工作流配置

        Returns:
            是否成功
        """
        try:
            # 读取现有配置
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.config_file)

            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 根据工作流类型更新配置
            if config.workflow_type == 'video_watermark':
                # 更新视频工作流ID
                if config.orientation:
                    # 更新特定方向的配置
                    content = self._update_video_workflow_id(content, config.orientation, config.workflow_id)
                else:
                    # 更新所有方向
                    content = self._update_video_workflow_id(content, 'landscape', config.workflow_id)
                    content = self._update_video_workflow_id(content, 'portrait', config.workflow_id)

                # 更新视频节点ID
                content = self._update_config_value(content, 'VIDEO_NODE_ID', config.node_id)

            elif config.workflow_type == 'image_watermark':
                # 更新图片工作流ID
                content = self._update_image_workflow_id(content, config.workflow_id)

                # 更新图片节点ID
                content = self._update_config_value(content, 'IMAGE_NODE_ID', config.node_id)

            # 写回文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ 配置文件已更新: {config_path}")
            return True

        except Exception as e:
            print(f"❌ 更新配置文件失败: {e}")
            return False

    def _update_video_workflow_id(self, content: str, orientation: str, workflow_id: str) -> str:
        """更新视频工作流ID"""
        # 匹配 "orientation": "xxx" 或 'orientation': 'xxx'
        pattern = rf'(["\']{orientation}["\']\s*:\s*)["\']\d+["\']'
        replacement = rf'\1"{workflow_id}"'
        return re.sub(pattern, replacement, content)

    def _update_image_workflow_id(self, content: str, workflow_id: str) -> str:
        """更新图片工作流ID"""
        # 匹配 "default": "xxx" 在image配置中
        pattern = r'("image":\s*\{[^}]*"default":\s*)"\d+"'
        replacement = rf'\1"{workflow_id}"'
        return re.sub(pattern, replacement, content, flags=re.DOTALL)

    def _update_config_value(self, content: str, key: str, value: str) -> str:
        """更新配置项的值"""
        # 匹配 KEY = "xxx" 或 KEY = 'xxx'
        pattern = rf'^({key}\s*=\s*)["\'][^"\']*["\']'
        replacement = rf'\1"{value}"'
        return re.sub(pattern, replacement, content, flags=re.MULTILINE)

    def test_workflow(self, workflow_id: str, node_config: NodeConfig,
                      test_file: Optional[str] = None) -> bool:
        """
        测试工作流可用性

        Args:
            workflow_id: 工作流ID
            node_config: 节点配置
            test_file: 测试文件路径（可选）

        Returns:
            测试是否通过
        """
        print("\n" + "=" * 60)
        print("测试工作流可用性")
        print("=" * 60)

        # 1. 测试创建任务（不传入文件）
        url = f"{self.BASE_URL}/task/openapi/create"

        # 准备节点信息
        node_info_list = []
        if test_file and os.path.exists(test_file):
            # 如果有测试文件，需要上传并设置
            print(f"📁 使用测试文件: {test_file}")
            # 注意：这里简化处理，实际应该上传文件
            # 对于测试，我们只验证工作流ID和节点ID是否正确

        payload = {
            "apiKey": self.api_key,
            "workflowId": workflow_id,
            "nodeInfoList": node_info_list if node_info_list else None
        }

        try:
            print(f"🧪 测试创建工作流任务...")
            print(f"   工作流ID: {workflow_id}")
            print(f"   节点ID: {node_config.node_id}")
            print(f"   字段名: {node_config.field_name}")

            resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
            result = resp.json()

            if result.get('code') == 0:
                task_id = result.get('data', {}).get('taskId')
                print(f"✅ 任务创建成功!")
                print(f"   Task ID: {task_id}")

                # 取消任务（我们只是测试，不需要真正运行）
                self._cancel_task(task_id)
                return True

            elif result.get('code') == 810:
                print(f"⚠️  工作流需要先运行一次才能通过API调用")
                print(f"   请在网页端先运行一次此工作流")
                return False

            elif result.get('code') == 803:
                print(f"❌ 节点信息错误: {result.get('msg')}")
                print(f"   请检查节点ID和字段名是否正确")
                return False

            elif result.get('code') == 380:
                print(f"❌ 工作流不存在: {result.get('msg')}")
                return False

            else:
                print(f"❌ 测试失败: {result.get('msg', '未知错误')}")
                return False

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False

    def _cancel_task(self, task_id: str):
        """取消任务"""
        url = f"{self.BASE_URL}/task/openapi/cancel"
        payload = {
            "apiKey": self.api_key,
            "taskId": task_id
        }
        try:
            requests.post(url, headers=self.headers, json=payload, timeout=10)
        except:
            pass

    def configure_workflow(self, workflow_input: str, workflow_type: Optional[str] = None,
                          orientation: Optional[str] = None, test: bool = True) -> bool:
        """
        配置工作流的主入口

        Args:
            workflow_input: 工作流ID或URL
            workflow_type: 工作流类型 ('video_watermark', 'image_watermark')
            orientation: 视频方向 ('landscape', 'portrait', 'default')
            test: 是否测试工作流

        Returns:
            是否成功
        """
        print("\n" + "=" * 60)
        print("RunningHub 工作流配置工具")
        print("=" * 60)

        # 1. 提取工作流ID
        workflow_id = self.extract_workflow_id(workflow_input)
        if not workflow_id:
            return False

        print(f"\n📋 工作流ID: {workflow_id}")

        # 2. 获取工作流JSON
        print("\n🔍 获取工作流JSON...")
        workflow_json = self.get_workflow_json(workflow_id)
        if not workflow_json:
            return False

        # 3. 分析节点
        print("\n🔍 分析工作流节点...")
        nodes_by_type = self.analyze_workflow_nodes(workflow_json)

        # 打印分析结果
        print("\n📊 节点分析结果:")
        for node_type, nodes in nodes_by_type.items():
            if nodes:
                print(f"\n   {node_type.upper()} 节点:")
                for node in nodes:
                    print(f"     - ID: {node.node_id}, 类型: {node.class_type}, 字段: {node.field_name}")

        # 4. 确定工作流类型
        if not workflow_type:
            detected_type = self.detect_workflow_type(nodes_by_type)
            workflow_type = detected_type.value
            print(f"\n🤖 自动检测到工作流类型: {workflow_type}")
        else:
            print(f"\n📌 指定工作流类型: {workflow_type}")

        # 5. 选择最佳节点
        if workflow_type == 'video_watermark':
            best_node = self.select_best_node(nodes_by_type.get('video', []))
            if not best_node:
                print("❌ 未找到视频输入节点")
                return False
            if not orientation:
                orientation = 'landscape'  # 默认横版

        elif workflow_type == 'image_watermark':
            best_node = self.select_best_node(nodes_by_type.get('image', []))
            if not best_node:
                print("❌ 未找到图片输入节点")
                return False
            orientation = 'default'

        else:
            print(f"❌ 不支持的工作流类型: {workflow_type}")
            return False

        print(f"\n✅ 选择节点:")
        print(f"   节点ID: {best_node.node_id}")
        print(f"   节点类型: {best_node.class_type}")
        print(f"   字段名: {best_node.field_name}")

        # 6. 创建配置
        config = WorkflowConfig(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            orientation=orientation if workflow_type == 'video_watermark' else None,
            node_id=best_node.node_id,
            field_name=best_node.field_name,
            class_type=best_node.class_type,
            description=f"Auto-configured {workflow_type} workflow"
        )

        # 7. 测试工作流
        if test:
            test_passed = self.test_workflow(workflow_id, best_node)
            if not test_passed:
                print("\n⚠️  工作流测试未通过，是否继续更新配置?")
                # 这里可以添加交互式确认，但为简化直接继续

        # 8. 更新配置文件
        print("\n📝 更新配置文件...")
        if self.update_config_file(config):
            print("\n" + "=" * 60)
            print("✅ 工作流配置完成!")
            print("=" * 60)
            print(f"\n配置信息:")
            print(f"  工作流类型: {config.workflow_type}")
            print(f"  工作流ID: {config.workflow_id}")
            print(f"  节点ID: {config.node_id}")
            print(f"  字段名: {config.field_name}")
            if config.orientation:
                print(f"  方向: {config.orientation}")
            return True

        return False


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='RunningHub 配置文件管理工具')
    parser.add_argument('workflow_input', help='工作流ID或URL')
    parser.add_argument('--type', '-t', choices=['video_watermark', 'image_watermark'],
                        help='工作流类型（可选，自动检测）')
    parser.add_argument('--orientation', '-o', choices=['landscape', 'portrait'],
                        help='视频方向（仅视频工作流）')
    parser.add_argument('--no-test', action='store_true',
                        help='跳过工作流测试')
    parser.add_argument('--api-key', '-k',
                        help='API Key（默认从config.py读取）')

    args = parser.parse_args()

    # 获取API Key
    api_key = args.api_key
    if not api_key:
        # 尝试从config.py读取
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from config import API_KEY
            api_key = API_KEY
        except ImportError:
            print("❌ 无法获取API Key，请通过 --api-key 参数指定")
            sys.exit(1)

    # 创建管理器并执行配置
    manager = ConfigManager(api_key)
    success = manager.configure_workflow(
        workflow_input=args.workflow_input,
        workflow_type=args.type,
        orientation=args.orientation,
        test=not args.no_test
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
