FROM python:3.9-slim

# 安装系统依赖并创建用户
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        tzdata \
    && addgroup --gid 1000 appgroup \
    && adduser --shell /bin/sh --disabled-password --uid 1000 --gid 1000 appuser \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制并安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src

# 创建数据和日志目录
RUN mkdir -p data logs

# 更改工作目录所有权
RUN chown -R appuser:appgroup /app

# 切换到非root用户
USER appuser

# 设置环境变量
ENV PYTHONPATH=/app

CMD ["python", "-m", "src.main"]