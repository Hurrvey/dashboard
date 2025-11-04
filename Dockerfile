# CODE996 数据看板 - Docker 镜像
FROM node:16-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app

# 复制前端依赖文件
COPY package*.json ./

# 安装前端依赖
RUN npm install

# 复制前端源码
COPY src ./src
COPY public ./public
COPY index.html .
COPY vite.config.ts .
COPY tsconfig.json .

# 构建前端
RUN npm run build

# ============================================================================
# 后端镜像
# ============================================================================
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制Python依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY app ./app
COPY run.py .

# 复制配置文件（如果存在）
COPY projects.json* ./

# 从前端构建阶段复制构建产物
COPY --from=frontend-builder /app/dist ./dist

# 创建必要的目录
RUN mkdir -p logs repos

# 暴露端口
EXPOSE 9970

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:9970/api/dashboard/health || exit 1

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9970", "--timeout", "60", "--access-logfile", "logs/access.log", "--error-logfile", "logs/error.log", "app.main:app"]

