# Captcha Recognition Service

验证码识别服务，基于 TensorFlow 和 Flask 构建的 Web 服务。

## 功能

- 接收 base64 编码的验证码图片
- 使用深度学习模型识别验证码内容
- 返回识别结果

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

### 开发环境

```bash
python main.py
```

服务将在 `http://localhost:5000` 启动。

### 生产环境

使用 Gunicorn 运行（推荐）：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

或使用 uWSGI：

```bash
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --module main:app --processes 4
```

## API 接口

### POST /

识别验证码图片

**请求体：**

- 格式：纯文本，base64 编码的图片数据（支持 data URL 格式）

**响应：**

- 验证码文本内容

```
024049
```

**示例：**

```bash
curl -X POST http://localhost:5000/ \
  -H "Content-Type: text/plain" \
  -d "data:image/png;base64,iVBORw0KGgoAAAANS..."
```

## Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY xserver_captcha.keras .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]
```

构建和运行：

```bash
docker build -t captcha-service .
docker run -p 5000:5000 captcha-service
```

