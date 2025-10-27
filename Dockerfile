# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装 uv (快速的 Python 包管理器)
# 使用 ADD 直接下载，避免安装 curl
ADD https://astral.sh/uv/install.sh /tmp/uv-install.sh
RUN sh /tmp/uv-install.sh && rm /tmp/uv-install.sh
ENV PATH="/root/.cargo/bin:${PATH}"

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

