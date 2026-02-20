"""
RunningHub 去水印系统 - Flask后端API
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import json
import os
import time
import tempfile
from pathlib import Path
from werkzeug.utils import secure_filename
from config import (
    API_KEY, BASE_URL, WORKFLOW_IDS, VIDEO_NODE_ID,
    HEADERS, UPLOAD_HEADERS, MAX_RETRIES, POLL_INTERVAL,
    INPUT_DIR, OUTPUT_DIR,
    POSE_WORKFLOW_ID, POSE_SOURCE_IMAGE_NODE_ID, POSE_POSE_IMAGE_NODE_ID,
    POSE_PROMPT1_NODE_ID, POSE_PROMPT2_NODE_ID, POSE_DEFAULT_PROMPT1, POSE_DEFAULT_PROMPT2
)

try:
    from config import IMAGE_NODE_ID
except ImportError:
    IMAGE_NODE_ID = None  # 图片功能未配置

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 最大500MB

# 确保目录存在
Path(INPUT_DIR).mkdir(exist_ok=True)
Path(OUTPUT_DIR).mkdir(exist_ok=True)

# 允许的文件类型
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename, file_type):
    """检查文件类型是否允许"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if file_type == 'video':
        return ext in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'image':
        return ext in ALLOWED_IMAGE_EXTENSIONS
    return False


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件到RunningHub"""
    try:
        if 'file' not in request.files:
            return jsonify({'code': -1, 'msg': '没有文件'}), 400
        
        file = request.files['file']
        file_type = request.form.get('type', 'video')
        
        if file.filename == '':
            return jsonify({'code': -1, 'msg': '文件名为空'}), 400
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'code': -1, 'msg': '不支持的文件类型'}), 400
        
        # 保存到临时目录
        filename = secure_filename(file.filename)
        temp_dir = tempfile.gettempdir()
        local_path = Path(temp_dir) / filename
        file.save(local_path)
        
        # 上传到RunningHub
        upload_url = f"{BASE_URL}/task/openapi/upload"
        
        with open(local_path, 'rb') as f:
            files = {'file': (filename, f, f'{"video" if file_type == "video" else "image"}/{filename.rsplit(".", 1)[1]}')}
            data = {'apiKey': API_KEY, 'fileType': 'input'}
            
            resp = requests.post(upload_url, data=data, files=files, headers=UPLOAD_HEADERS, timeout=120)
            result = resp.json()
        
        # 删除本地临时文件
        local_path.unlink(missing_ok=True)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'上传失败: {str(e)}'}), 500


@app.route('/api/create_task', methods=['POST'])
def create_task():
    """创建去水印任务"""
    try:
        data = request.json
        file_name = data.get('fileName')
        file_type = data.get('type', 'video')
        orientation = data.get('orientation', 'portrait')
        
        if not file_name:
            return jsonify({'code': -1, 'msg': '缺少文件名'}), 400
        
        # 选择工作流ID
        if file_type == 'video':
            workflow_id = WORKFLOW_IDS['video'].get(orientation, WORKFLOW_IDS['video']['portrait'])
            node_id = VIDEO_NODE_ID
            field_name = 'video'
        else:
            if IMAGE_NODE_ID is None:
                return jsonify({'code': -1, 'msg': '图片去水印功能未配置'}), 400
            workflow_id = WORKFLOW_IDS['image'].get('default')
            node_id = IMAGE_NODE_ID
            field_name = 'image'
        
        # 创建任务
        url = f"{BASE_URL}/task/openapi/create"
        payload = {
            "apiKey": API_KEY,
            "workflowId": workflow_id,
            "nodeInfoList": [
                {
                    "nodeId": node_id,
                    "fieldName": field_name,
                    "fieldValue": file_name
                }
            ]
        }
        
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'创建任务失败: {str(e)}'}), 500


@app.route('/api/query_status', methods=['POST'])
def query_status():
    """查询任务状态"""
    try:
        data = request.json
        task_id = data.get('taskId')
        
        if not task_id:
            return jsonify({'code': -1, 'msg': '缺少任务ID'}), 400
        
        url = f"{BASE_URL}/task/openapi/status"
        payload = {"apiKey": API_KEY, "taskId": task_id}
        
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'查询失败: {str(e)}'}), 500


@app.route('/api/get_outputs', methods=['POST'])
def get_outputs():
    """获取任务输出"""
    try:
        data = request.json
        task_id = data.get('taskId')
        
        if not task_id:
            return jsonify({'code': -1, 'msg': '缺少任务ID'}), 400
        
        url = f"{BASE_URL}/task/openapi/outputs"
        payload = {"apiKey": API_KEY, "taskId": task_id}
        
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()
        
        # 如果有输出文件，下载到本地
        if result.get('code') == 0 and result.get('data'):
            for item in result['data']:
                file_url = item.get('fileUrl')
                if file_url:
                    try:
                        file_resp = requests.get(file_url, timeout=300)
                        if file_resp.status_code == 200:
                            # 从URL中提取文件名
                            file_name = file_url.split('/')[-1]
                            local_path = Path(OUTPUT_DIR) / file_name
                            with open(local_path, 'wb') as f:
                                f.write(file_resp.content)
                            item['localUrl'] = f'/output/{file_name}'
                    except Exception as e:
                        print(f"下载文件失败: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'code': -1, 'msg': f'获取输出失败: {str(e)}'}), 500


@app.route('/output/<filename>')
def serve_output(filename):
    """提供输出文件下载"""
    return send_from_directory(OUTPUT_DIR, filename)


@app.route('/pose')
def pose_page():
    """改变动作页面"""
    return render_template('pose.html')


@app.route('/api/get_workflow_prompts', methods=['GET'])
def get_workflow_prompts():
    """获取工作流的默认提示词（实时从RunningHub获取）"""
    try:
        # 从RunningHub获取工作流JSON
        url = f"{BASE_URL}/api/openapi/getJsonApiFormat"
        payload = {
            "apiKey": API_KEY,
            "workflowId": POSE_WORKFLOW_ID
        }
        
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()
        
        if result.get("code") != 0:
            # 如果获取失败，返回本地配置的默认值
            return jsonify({
                'code': 0,
                'msg': '使用本地默认值',
                'data': {
                    'prompt1': POSE_DEFAULT_PROMPT1,
                    'prompt2': POSE_DEFAULT_PROMPT2
                }
            })
        
        # 解析工作流JSON
        workflow_data = result.get("data", {})
        prompt_str = workflow_data.get("prompt", "{}")
        prompt_data = json.loads(prompt_str)
        
        # 提取提示词
        prompt1 = POSE_DEFAULT_PROMPT1
        prompt2 = POSE_DEFAULT_PROMPT2
        
        # 获取节点25的提示词1
        if POSE_PROMPT1_NODE_ID in prompt_data:
            node25 = prompt_data[POSE_PROMPT1_NODE_ID]
            inputs = node25.get("inputs", {})
            if "text" in inputs:
                prompt1 = inputs["text"]
        
        # 获取节点35的提示词2
        if POSE_PROMPT2_NODE_ID in prompt_data:
            node35 = prompt_data[POSE_PROMPT2_NODE_ID]
            inputs = node35.get("inputs", {})
            if "prompt" in inputs:
                prompt2 = inputs["prompt"]
        
        return jsonify({
            'code': 0,
            'msg': '获取成功',
            'data': {
                'prompt1': prompt1,
                'prompt2': prompt2
            }
        })
        
    except Exception as e:
        # 出错时返回本地默认值
        return jsonify({
            'code': 0,
            'msg': f'获取远程配置失败，使用本地默认值: {str(e)}',
            'data': {
                'prompt1': POSE_DEFAULT_PROMPT1,
                'prompt2': POSE_DEFAULT_PROMPT2
            }
        })


@app.route('/api/create_pose_task', methods=['POST'])
def create_pose_task():
    """创建改变动作任务"""
    try:
        data = request.json
        source_file_name = data.get('sourceFileName')  # 原图文件名
        pose_file_name = data.get('poseFileName')      # 姿势参考图文件名
        prompt1 = data.get('prompt1', POSE_DEFAULT_PROMPT1)  # 提示词1，使用默认值
        prompt2 = data.get('prompt2', POSE_DEFAULT_PROMPT2)  # 提示词2，使用默认值

        if not source_file_name:
            return jsonify({'code': -1, 'msg': '缺少原图文件名'}), 400

        if not pose_file_name:
            return jsonify({'code': -1, 'msg': '缺少姿势参考图文件名'}), 400

        # 创建任务
        url = f"{BASE_URL}/task/openapi/create"
        node_info_list = [
            {
                "nodeId": POSE_SOURCE_IMAGE_NODE_ID,
                "fieldName": "image",
                "fieldValue": source_file_name
            },
            {
                "nodeId": POSE_POSE_IMAGE_NODE_ID,
                "fieldName": "image",
                "fieldValue": pose_file_name
            },
            {
                "nodeId": POSE_PROMPT1_NODE_ID,
                "fieldName": "text",
                "fieldValue": prompt1
            }
        ]
        
        # 如果提示词2不为空，则添加
        if prompt2 and prompt2.strip():
            node_info_list.append({
                "nodeId": POSE_PROMPT2_NODE_ID,
                "fieldName": "prompt",
                "fieldValue": prompt2
            })
        
        payload = {
            "apiKey": API_KEY,
            "workflowId": POSE_WORKFLOW_ID,
            "nodeInfoList": node_info_list
        }

        resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        result = resp.json()

        return jsonify(result)

    except Exception as e:
        return jsonify({'code': -1, 'msg': f'创建任务失败: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
