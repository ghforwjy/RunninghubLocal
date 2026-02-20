"""
测试配置文件管理器

运行方式:
    python tests/test_config_manager.py

功能:
1. 测试工作流ID提取功能
2. 测试工作流JSON获取
3. 测试节点分析
4. 测试工作流可用性
5. 测试配置文件更新
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_manager import ConfigManager, WorkflowConfig, NodeConfig, WorkflowType
from config import API_KEY


class TestWorkflowIdExtraction(unittest.TestCase):
    """测试工作流ID提取"""

    def setUp(self):
        self.manager = ConfigManager(API_KEY)

    def test_pure_id(self):
        """测试纯ID格式"""
        test_id = "2024401195896410114"
        result = self.manager.extract_workflow_id(test_id)
        self.assertEqual(result, test_id)

    def test_url_format(self):
        """测试URL格式"""
        test_cases = [
            ("https://www.runninghub.cn/workflow/2024401195896410114", "2024401195896410114"),
            ("https://www.runninghub.cn/workflow/2024401195896410114/", "2024401195896410114"),
            ("www.runninghub.cn/workflow/2024401195896410114", "2024401195896410114"),
        ]
        for url, expected in test_cases:
            result = self.manager.extract_workflow_id(url)
            self.assertEqual(result, expected, f"Failed for URL: {url}")

    def test_invalid_input(self):
        """测试无效输入"""
        invalid_inputs = [
            "not_a_valid_id",
            "123",  # 太短
            "https://example.com/other",
            "",
        ]
        for inp in invalid_inputs:
            result = self.manager.extract_workflow_id(inp)
            self.assertIsNone(result, f"Should return None for: {inp}")


class TestWorkflowJson(unittest.TestCase):
    """测试工作流JSON获取"""

    def setUp(self):
        self.manager = ConfigManager(API_KEY)

    def test_get_existing_workflow(self):
        """测试获取现有工作流"""
        # 使用当前配置中的工作流ID
        from config import WORKFLOW_IDS
        workflow_id = WORKFLOW_IDS['video']['landscape']

        result = self.manager.get_workflow_json(workflow_id)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_get_nonexistent_workflow(self):
        """测试获取不存在的工作流"""
        result = self.manager.get_workflow_json("9999999999999999999")
        self.assertIsNone(result)


class TestNodeAnalysis(unittest.TestCase):
    """测试节点分析"""

    def setUp(self):
        self.manager = ConfigManager(API_KEY)

    def test_analyze_video_workflow(self):
        """测试分析视频工作流"""
        from config import WORKFLOW_IDS
        workflow_id = WORKFLOW_IDS['video']['landscape']

        workflow_json = self.manager.get_workflow_json(workflow_id)
        self.assertIsNotNone(workflow_json)

        nodes = self.manager.analyze_workflow_nodes(workflow_json)

        # 检查是否有视频节点
        self.assertIn('video', nodes)
        self.assertGreater(len(nodes['video']), 0, "应该至少有一个视频节点")

        # 检查节点结构
        for node in nodes['video']:
            self.assertIsInstance(node, NodeConfig)
            self.assertIsNotNone(node.node_id)
            self.assertIsNotNone(node.field_name)
            self.assertIsNotNone(node.class_type)

    def test_detect_workflow_type(self):
        """测试工作流类型检测"""
        from config import WORKFLOW_IDS

        # 测试视频工作流
        video_workflow_id = WORKFLOW_IDS['video']['landscape']
        video_json = self.manager.get_workflow_json(video_workflow_id)
        video_nodes = self.manager.analyze_workflow_nodes(video_json)
        detected_type = self.manager.detect_workflow_type(video_nodes)
        self.assertEqual(detected_type, WorkflowType.VIDEO_WATERMARK)


class TestNodeSelection(unittest.TestCase):
    """测试节点选择"""

    def setUp(self):
        self.manager = ConfigManager(API_KEY)

    def test_select_best_node(self):
        """测试选择最佳节点"""
        # 创建测试节点列表
        nodes = [
            NodeConfig(node_id="10", field_name="other", class_type="Test", node_type="video"),
            NodeConfig(node_id="5", field_name="video", class_type="VHS_LoadVideo", node_type="video"),
            NodeConfig(node_id="3", field_name="input", class_type="LoadVideo", node_type="video"),
        ]

        best = self.manager.select_best_node(nodes)
        # 应该选择有标准字段名'video'的节点
        self.assertEqual(best.node_id, "5")
        self.assertEqual(best.field_name, "video")

    def test_select_from_empty_list(self):
        """测试从空列表选择"""
        result = self.manager.select_best_node([])
        self.assertIsNone(result)


class TestWorkflowTesting(unittest.TestCase):
    """测试工作流可用性测试"""

    def setUp(self):
        self.manager = ConfigManager(API_KEY)

    def test_test_existing_workflow(self):
        """测试现有工作流"""
        from config import WORKFLOW_IDS, VIDEO_NODE_ID

        workflow_id = WORKFLOW_IDS['video']['landscape']
        node_config = NodeConfig(
            node_id=VIDEO_NODE_ID,
            field_name="video",
            class_type="VHS_LoadVideo",
            node_type="video"
        )

        # 测试工作流（不传入实际文件）
        result = self.manager.test_workflow(workflow_id, node_config)
        # 可能成功也可能因为需要文件而失败，但不应抛出异常
        self.assertIsInstance(result, bool)


class TestConfigUpdate(unittest.TestCase):
    """测试配置文件更新"""

    def setUp(self):
        self.manager = ConfigManager(API_KEY)
        # 保存原始配置内容
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")
        with open(config_path, 'r', encoding='utf-8') as f:
            self.original_content = f.read()

    def tearDown(self):
        # 恢复原始配置
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(self.original_content)

    def test_update_video_config(self):
        """测试更新视频配置"""
        config = WorkflowConfig(
            workflow_id="1234567890123456789",
            workflow_type="video_watermark",
            orientation="landscape",
            node_id="184",
            field_name="video",
            class_type="VHS_LoadVideo"
        )

        result = self.manager.update_config_file(config)
        self.assertTrue(result)

        # 验证更新
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('"landscape": "1234567890123456789"', content)
        self.assertIn('VIDEO_NODE_ID = "184"', content)

    def test_update_image_config(self):
        """测试更新图片配置"""
        config = WorkflowConfig(
            workflow_id="9876543210987654321",
            workflow_type="image_watermark",
            orientation=None,
            node_id="21",
            field_name="image",
            class_type="LoadImage"
        )

        result = self.manager.update_config_file(config)
        self.assertTrue(result)

        # 验证更新
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn('"default": "9876543210987654321"', content)
        self.assertIn('IMAGE_NODE_ID = "21"', content)


def run_integration_test():
    """运行集成测试"""
    print("\n" + "=" * 60)
    print("集成测试：完整配置流程")
    print("=" * 60)

    manager = ConfigManager(API_KEY)

    # 使用当前配置的工作流ID进行测试
    from config import WORKFLOW_IDS
    workflow_id = WORKFLOW_IDS['video']['landscape']

    print(f"\n测试工作流ID: {workflow_id}")

    # 执行完整配置流程
    success = manager.configure_workflow(
        workflow_input=workflow_id,
        workflow_type='video_watermark',
        orientation='landscape',
        test=True
    )

    if success:
        print("\n✅ 集成测试通过!")
    else:
        print("\n❌ 集成测试失败!")

    return success


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("配置文件管理器测试")
    print("=" * 60)

    # 运行单元测试
    print("\n运行单元测试...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowIdExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowJson))
    suite.addTests(loader.loadTestsFromTestCase(TestNodeAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestNodeSelection))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowTesting))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 运行集成测试
    print("\n" + "=" * 60)
    integration_success = run_integration_test()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"单元测试: {'✅ 通过' if result.wasSuccessful() else '❌ 失败'}")
    print(f"集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")

    return result.wasSuccessful() and integration_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
