"""
测试获取改变动作工作流的JSON结构
"""
import json
from runninghub_client import RunningHubClient
from config import API_KEY

# 工作流ID
POSE_WORKFLOW_ID = "2008590031811776514"

def main():
    client = RunningHubClient(api_key=API_KEY)
    
    # 获取工作流JSON结构
    print("=" * 60)
    print(f"获取工作流 {POSE_WORKFLOW_ID} 的JSON结构...")
    print("=" * 60)
    
    workflow_json = client.get_workflow_json(POSE_WORKFLOW_ID)
    
    if workflow_json.get("code") == 0:
        data = workflow_json.get("data", {})
        
        # 解析prompt中的JSON
        if "prompt" in data:
            prompt_data = json.loads(data["prompt"])
            print("\n工作流节点分析:")
            print("=" * 60)
            
            for node_id, node_info in prompt_data.items():
                class_type = node_info.get("class_type", "")
                inputs = node_info.get("inputs", {})
                meta = node_info.get("_meta", {})
                title = meta.get("title", "")
                
                # 查找关键输入节点
                if class_type == "LoadImage":
                    print(f"\n🖼️ 图片输入节点:")
                    print(f"   节点ID: {node_id}")
                    print(f"   节点类型: {class_type}")
                    print(f"   标题: {title}")
                    print(f"   当前图片: {inputs.get('image', 'N/A')}")
                    
                elif class_type == "TextEncodeQwenImageEditPlus":
                    print(f"\n📝 提示词输入节点 (Plus):")
                    print(f"   节点ID: {node_id}")
                    print(f"   节点类型: {class_type}")
                    print(f"   标题: {title}")
                    print(f"   当前提示词: {inputs.get('prompt', 'N/A')[:100]}...")
                    
                elif class_type == "TextEncodeQwenImageEdit":
                    print(f"\n📝 提示词输入节点:")
                    print(f"   节点ID: {node_id}")
                    print(f"   节点类型: {class_type}")
                    print(f"   标题: {title}")
                    print(f"   当前提示词: {inputs.get('prompt', 'N/A')[:100]}...")
                    
                elif class_type == "KSampler":
                    print(f"\n🎲 采样器节点:")
                    print(f"   节点ID: {node_id}")
                    print(f"   节点类型: {class_type}")
                    print(f"   标题: {title}")
                    print(f"   种子: {inputs.get('seed', 'N/A')}")
                    print(f"   步数: {inputs.get('steps', 'N/A')}")
                    print(f"   CFG: {inputs.get('cfg', 'N/A')}")
                    
                elif class_type == "SaveImage":
                    print(f"\n💾 保存图片节点:")
                    print(f"   节点ID: {node_id}")
                    print(f"   节点类型: {class_type}")
                    print(f"   标题: {title}")
                    print(f"   文件名前缀: {inputs.get('filename_prefix', 'N/A')}")
        
        # 分析nodeInfoList（如果有的话）
        print("\n" + "=" * 60)
        print("API节点信息 (nodeInfoList):")
        print("=" * 60)
        
        if "nodeInfoList" in data and data["nodeInfoList"]:
            for node in data["nodeInfoList"]:
                print(f"\n节点ID: {node.get('nodeId')}")
                print(f"  节点名称: {node.get('nodeName')}")
                print(f"  字段名: {node.get('fieldName')}")
                print(f"  字段值: {node.get('fieldValue')}")
                print(f"  字段类型: {node.get('fieldType')}")
        else:
            print("\n该工作流没有配置API输入节点，需要手动分析prompt字段")
            print("\n关键节点信息汇总:")
            print("-" * 60)
            print("图片输入节点ID: 25 (LoadImage)")
            print("提示词输入节点ID: 40 (TextEncodeQwenImageEditPlus)")
            print("备用提示词节点ID: 48 (TextEncodeQwenImageEdit)")
    else:
        print(f"获取失败: {workflow_json.get('msg')}")

if __name__ == "__main__":
    main()
