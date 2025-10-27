# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制 requirements.txt（利用 Docker 缓存层）
COPY requirements.txt ./

# 配置 pip 使用清华镜像源（加速下载）
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 安装依赖（使用 uv 导出的 requirements.txt，锁定版本）
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY app ./app
COPY data ./data

# 暴露端口
EXPOSE 8000

# 健康检查 - 使用 Python 而不是 curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# 启动应用（直接使用 uvicorn，不需要 uv run）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

