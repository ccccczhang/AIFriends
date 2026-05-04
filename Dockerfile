# 使用官方 Python 3.11 轻量版镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=AIfriend

# 设置工作目录
WORKDIR /app

# 安装系统依赖（Django 常见的依赖，例如 PostgreSQL 客户端、sqlite3 等）
# 如果你只用 MySQL 或 PostgreSQL，可以按需调整
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装 Python 包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目
COPY . .

# 收集静态文件（生产环境需要）
RUN python manage.py collectstatic --noinput

# 创建非 root 用户并切换（提升安全性）
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口（gunicorn 默认 8000）
EXPOSE 8000

# 启动 gunicorn（替换 your_project 为你的 Django 项目名）
CMD ["gunicorn", "AIfriend", "--bind", "0.0.0.0:8000"]