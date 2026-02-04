import tensorflow as tf
from flask import Flask, request, render_template_string

app = Flask(__name__)

model = None

def load_model():
    """延迟加载模型"""
    global model
    if model is None:
        model = tf.keras.models.load_model('xserver_captcha.keras')
    return model

def _recognize_captcha():
    """验证码识别核心逻辑"""
    try:
        # 获取 base64 编码的图片数据
        data_url = request.get_data(as_text=True)
        if not data_url:
            return '', 400

        # print(data_url)

        # 解码 base64 图片
        base64_data = data_url.split(',')[-1].translate(str.maketrans({'+': '-', '/': '_'}))
        img = tf.io.decode_base64(base64_data)
        img = tf.image.decode_png(img, channels=3)
        img = tf.image.resize(img, [60, 300]) / 255.0
        batch = tf.expand_dims(img, 0)

        # 加载模型并预测
        model = load_model()
        preds = model(batch)
        input_len = tf.fill([tf.shape(preds)[0]], tf.shape(preds)[1])
        decoded = tf.keras.backend.ctc_decode(preds, input_length=input_len, greedy=True)[0][0]
        code = ''.join(str(c) for c in decoded.numpy()[0] if c >= 0)

        # print('iVBOR', code)

        # 返回纯文本验证码字符串
        return code, 200

    except Exception as e:
        print(f'Error: {str(e)}')
        return '', 500

@app.route('/', methods=['GET', 'POST'])
def index():
    """前端页面和 API 接口"""
    if request.method == 'POST':
        # POST 请求处理识别
        return _recognize_captcha()

    # GET 请求返回前端页面
    """前端页面"""
    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>验证码识别服务</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            padding: 40px;
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }

        h1 .emoji {
            display: inline-block;
            margin-right: 10px;
        }

        h1 .text {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }

        .tab {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            color: #666;
            transition: all 0.3s;
            position: relative;
            font-weight: 500;
        }

        .tab:hover {
            color: #667eea;
        }

        .tab.active {
            color: #667eea;
        }

        .tab.active::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 2px;
            background: #667eea;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: slideIn 0.3s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }

        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
            transform: translateY(-2px);
        }

        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }

        .upload-text {
            color: #667eea;
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 5px;
        }

        .upload-hint {
            color: #999;
            font-size: 14px;
        }

        #fileInput {
            display: none;
        }

        .base64-input {
            width: 100%;
            min-height: 150px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
            transition: border-color 0.3s;
            margin-bottom: 20px;
        }

        .base64-input:focus {
            outline: none;
            border-color: #667eea;
        }

        .preview-section {
            margin-bottom: 20px;
        }

        .preview-title {
            color: #333;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
        }

        .preview-image {
            max-width: 100%;
            max-height: 300px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            display: block;
            margin: 0 auto;
        }

        .btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            display: none;
        }

        .result-section.show {
            display: block;
            animation: slideUp 0.3s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-label {
            color: #666;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .result-value {
            color: #333;
            font-size: 32px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            letter-spacing: 4px;
            text-align: center;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .error {
            color: #e74c3c;
            background: #ffeaea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }

        .error.show {
            display: block;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            margin-top: 10px;
            color: #667eea;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1><span class="emoji">🔐</span><span class="text">验证码识别</span></h1>
        <p class="subtitle">上传图片或输入 Base64 编码进行识别</p>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('upload')">📁 上传图片</button>
            <button class="tab" onclick="switchTab('base64')">📝 Base64 输入</button>
        </div>

        <div id="uploadTab" class="tab-content active">
            <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                <div class="upload-icon">📤</div>
                <div class="upload-text">点击或拖拽图片到此处</div>
                <div class="upload-hint">支持 PNG、JPG、JPEG 格式</div>
            </div>
            <input type="file" id="fileInput" accept="image/*">
            <div class="preview-section" id="previewSection" style="display: none;">
                <div class="preview-title">预览图片：</div>
                <img id="previewImage" class="preview-image" alt="预览">
            </div>
        </div>

        <div id="base64Tab" class="tab-content">
            <textarea
                id="base64Input"
                class="base64-input"
                placeholder="请输入 Base64 编码的图片数据（支持 data:image/... 格式）"
            ></textarea>
            <div class="preview-section" id="base64PreviewSection" style="display: none;">
                <div class="preview-title">预览图片：</div>
                <img id="base64PreviewImage" class="preview-image" alt="预览">
            </div>
        </div>

        <button class="btn" id="recognizeBtn" onclick="recognizeCaptcha()">🚀 开始识别</button>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div class="loading-text">正在识别中...</div>
        </div>

        <div class="result-section" id="resultSection">
            <div class="result-label">识别结果：</div>
            <div class="result-value" id="resultValue"></div>
        </div>

        <div class="error" id="error"></div>
    </div>

    <script>
        let currentImageData = null;

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));

            if (tab === 'upload') {
                document.querySelectorAll('.tab')[0].classList.add('active');
                document.getElementById('uploadTab').classList.add('active');
            } else {
                document.querySelectorAll('.tab')[1].classList.add('active');
                document.getElementById('base64Tab').classList.add('active');
            }

            hideResult();
        }

        function hideResult() {
            document.getElementById('resultSection').classList.remove('show');
            document.getElementById('error').classList.remove('show');
        }

        // 文件上传处理
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFile(file);
            }
        });

        // 拖拽上传
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                handleFile(file);
            } else {
                showError('请上传图片文件');
            }
        });

        function handleFile(file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                currentImageData = e.target.result;
                document.getElementById('previewImage').src = currentImageData;
                document.getElementById('previewSection').style.display = 'block';
                hideResult();
            };
            reader.readAsDataURL(file);
        }

        // Base64 输入处理
        document.getElementById('base64Input').addEventListener('input', function() {
            const value = this.value.trim();
            if (value) {
                try {
                    // 如果已经是 data URL，直接使用
                    if (value.startsWith('data:image/')) {
                        currentImageData = value;
                    } else {
                        // 如果不是 data URL，尝试添加前缀
                        currentImageData = 'data:image/png;base64,' + value;
                    }
                    document.getElementById('base64PreviewImage').src = currentImageData;
                    document.getElementById('base64PreviewSection').style.display = 'block';
                    hideResult();
                } catch (e) {
                    document.getElementById('base64PreviewSection').style.display = 'none';
                }
            } else {
                document.getElementById('base64PreviewSection').style.display = 'none';
                currentImageData = null;
            }
        });

        async function recognizeCaptcha() {
            let imageData = null;

            // 获取当前标签页的图片数据
            const uploadTab = document.getElementById('uploadTab').classList.contains('active');
            if (uploadTab) {
                imageData = currentImageData;
            } else {
                const base64Value = document.getElementById('base64Input').value.trim();
                if (base64Value) {
                    if (base64Value.startsWith('data:image/')) {
                        imageData = base64Value;
                    } else {
                        imageData = 'data:image/png;base64,' + base64Value;
                    }
                }
            }

            if (!imageData) {
                showError('请先上传图片或输入 Base64 编码');
                return;
            }

            // 显示加载状态
            document.getElementById('loading').classList.add('show');
            document.getElementById('recognizeBtn').disabled = true;
            hideResult();

            try {
                const response = await fetch('/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'text/plain',
                    },
                    body: imageData
                });

                if (response.ok) {
                    const result = await response.text();
                    showResult(result);
                } else {
                    showError('识别失败，请检查图片格式是否正确');
                }
            } catch (error) {
                showError('网络错误：' + error.message);
            } finally {
                document.getElementById('loading').classList.remove('show');
                document.getElementById('recognizeBtn').disabled = false;
            }
        }

        function showResult(code) {
            document.getElementById('resultValue').textContent = code;
            document.getElementById('resultSection').classList.add('show');
            document.getElementById('error').classList.remove('show');
        }

        function showError(message) {
            document.getElementById('error').textContent = message;
            document.getElementById('error').classList.add('show');
            document.getElementById('resultSection').classList.remove('show');
        }
    </script>
</body>
</html>'''
    return render_template_string(html_template)

if __name__ == '__main__':
    # 开发环境运行
    app.run(host='0.0.0.0', port=5000, debug=True)
