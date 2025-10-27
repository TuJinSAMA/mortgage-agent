# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 使用 pip 安装 uv (最稳定的方式)
RUN pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --no-cache-dir uv

# 复制项目文件
COPY pyproject.toml ./
COPY app ./app
COPY data ./data

# 使用 uv 安装依赖（不使用 lock 文件）
RUN uv sync --no-dev

# 暴露端口
EXPOSE 8000

# 健康检查 - 使用 Python 而不是 curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# 启动应用
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

