# CODE996 数据看板 📊

<div align="center">

一个聚合多 Git 仓库提交信息的可视化分析系统，专注展示团队工作节奏、加班强度、贡献者排行和 AI 代码占比分析。

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node Version](https://img.shields.io/badge/node-16+-green.svg)](https://nodejs.org/)
[![Vue Version](https://img.shields.io/badge/vue-3.2+-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

[功能特性](#功能特性) • [快速开始](#快速开始) • [配置说明](#配置说明) • [API文档](#api-文档) • [部署指南](#部署指南)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [部署指南](#部署指南)
- [开发指南](#开发指南)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)

---

## 🎯 项目简介

CODE996 Dashboard 是一个开源的 Git 仓库数据可视化分析系统，旨在帮助团队和个人了解真实的工作节奏和代码贡献情况。

### 为什么选择 CODE996？

- **多仓库聚合**：支持同时分析多个 Git 仓库（本地或远程）
- **工作时间分析**：智能区分工作时间与加班时间（可自定义规则）
- **AI 代码检测**：集成 AI 分析，估算代码中 AI 生成与人工编写的比例
- **实时可视化**：基于 chart.xkcd 的手绘风格图表，直观展示数据
- **易于部署**：提供一键启动脚本、Docker 容器化部署
- **高性能缓存**：支持 Redis 缓存，未部署时自动降级到内存缓存

---

## ✨ 功能特性

### 📊 数据可视化

- **按小时分布**：24 小时提交热力图，清晰展示团队工作时段
- **按天分布**：一周七天的提交量对比，识别工作日与周末节奏
- **工作/加班占比**：基于时间规则（周一至周五 9:00-18:00）智能统计
- **工作日/周末占比**：区分工作日与周末的代码提交量
- **AI 代码占比**：通过 LLM 分析代码片段，估算 AI 生成代码比例

### 👥 团队洞察

- **贡献者排行榜**：自动滚动展示贡献者列表，包含提交数、增删行数
- **多项目聚合**：合并多个仓库的贡献数据，消除重复统计
- **996 指数**：量化团队加班强度的指标

### 🚀 性能与体验

- **并发数据抓取**：后端使用线程池并发拉取多个仓库数据
- **智能缓存策略**：Redis 优先，内存降级，支持手动刷新
- **健康检查接口**：便于监控和自动化部署
- **响应式设计**：适配大屏展示和移动端访问

---

## 🛠️ 技术栈

### 前端

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue.js | 3.2+ | 渐进式 JavaScript 框架 |
| TypeScript | 4.4+ | JavaScript 的超集，提供类型检查 |
| Vite | 2.6+ | 现代化前端构建工具 |
| chart.xkcd | 1.1+ | 手绘风格图表库 |
| Sass | 1.43+ | CSS 预处理器 |
| Vue Router | 4.0+ | 官方路由管理器 |

### 后端

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 编程语言 |
| Flask | 2.3+ | 轻量级 Web 框架 |
| GitPython | 3.1+ | Git 仓库操作库 |
| Redis | 5.0+ | 缓存数据库（可选） |
| Gunicorn | 21.2+ | WSGI HTTP 服务器 |
| pydantic | - | 数据验证和设置管理 |
| requests | 2.31+ | HTTP 客户端库 |

### 部署与运维

- **Docker & Docker Compose**：容器化部署
- **Nginx**：反向代理和静态资源服务（可选）
- **跨平台脚本**：Windows (BAT) 和 Linux/macOS (Shell) 启动脚本

---

## 📁 项目结构

```
dashboard/
├── app/                          # 后端应用
│   ├── api/                      # API 路由
│   │   ├── routes.py            # 主要 API 路由（summary, contributors, health）
│   │   ├── ai_routes.py         # AI 代码分析路由
│   │   ├── validators.py        # 参数验证
│   │   └── responses.py         # 响应格式封装
│   ├── config/                   # 配置模块
│   │   └── projects.py          # 项目配置管理
│   ├── models/                   # 数据模型
│   │   ├── commit.py            # Commit 模型
│   │   ├── stats.py             # 统计数据模型
│   │   └── contributor.py       # 贡献者模型
│   ├── services/                 # 业务逻辑服务
│   │   ├── git_service.py       # Git 仓库管理
│   │   ├── stats_service.py     # 统计数据服务
│   │   ├── cache_service.py     # 缓存服务
│   │   ├── ai_analyzer.py       # AI 代码分析
│   │   ├── project_registry.py  # 项目注册表
│   │   └── project_file_collector.py  # 文件采集
│   ├── utils/                    # 工具函数
│   │   ├── logger.py            # 日志配置
│   │   ├── stats_calculator.py  # 统计计算
│   │   └── time_utils.py        # 时间处理
│   ├── middleware/               # 中间件
│   │   └── cors.py              # CORS 配置
│   ├── main.py                   # Flask 应用主入口
│   └── settings.py               # 应用配置
│
├── src/                          # 前端源码
│   ├── api/                      # API 调用封装
│   │   └── dashboard.ts         # Dashboard API
│   ├── components/               # Vue 组件
│   │   ├── charts/              # 图表组件
│   │   │   ├── BaseChart.vue   # 基础图表组件
│   │   │   ├── BarChart.vue    # 柱状图
│   │   │   └── PieChart.vue    # 饼图
│   │   └── CommitScroller.vue   # 贡献者滚动榜
│   ├── views/                    # 页面视图
│   │   └── Dashboard.vue        # 仪表板主页
│   ├── router/                   # 路由配置
│   ├── styles/                   # 样式文件
│   ├── typings/                  # TypeScript 类型定义
│   ├── utils/                    # 前端工具函数
│   ├── App.vue                   # 根组件
│   └── main.ts                   # 前端入口
│
├── public/                       # 静态资源
│   ├── fonts/                    # 字体文件
│   └── images/                   # 图片资源
│
├── dist/                         # 前端构建产物
├── logs/                         # 日志文件
├── repos/                        # Git 仓库存储目录
│   └── _mirror/                 # 远程仓库镜像
│
├── scripts/                      # 脚本工具
│   ├── get_default_projects.py  # 获取默认项目
│   └── get_project_ids.py       # 获取项目 ID
│
├── docker-compose.yml            # Docker Compose 配置
├── Dockerfile                    # Docker 镜像构建
├── gunicorn.conf.py             # Gunicorn 生产环境配置
├── nginx.conf                    # Nginx 配置
├── run.py                        # 后端启动脚本
├── start-all.bat                 # Windows 一键启动脚本
├── start-all.sh                  # Linux/macOS 一键启动脚本
├── stop-all.bat                  # Windows 停止脚本
├── stop-all.sh                   # Linux/macOS 停止脚本
├── projects.json                 # 项目配置文件
├── projects.json.example         # 项目配置示例
├── package.json                  # Node.js 依赖
├── requirements.txt              # Python 依赖
├── vite.config.ts                # Vite 配置
├── tsconfig.json                 # TypeScript 配置
└── README.md                     # 项目文档
```

---

## 🚀 快速开始

### 前置要求

确保你的系统已安装以下软件：

- **Python** 3.9 或更高版本
- **Node.js** 16 或更高版本
- **npm** 或 **yarn**
- **Git** 2.0 或更高版本
- **Redis** 5.0+ （可选，未安装会自动降级到内存缓存）

### 方式一：一键启动脚本（推荐）

这是最简单的启动方式，脚本会自动完成所有准备工作。

#### Windows

```powershell
# 1. 克隆项目
git clone <your-repo-url>
cd dashboard

# 2. 一键启动
start-all.bat

# 停止服务
stop-all.bat
```

#### Linux / macOS

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd dashboard

# 2. 一键启动
bash start-all.sh

# 停止服务
bash stop-all.sh
```

#### 启动脚本功能

脚本会自动完成以下操作：

1. ✅ 检查 Python、Node.js、npm 是否已安装
2. ✅ 检查配置文件 `projects.json`，不存在则自动创建
3. ✅ 创建 Python 虚拟环境（首次运行）
4. ✅ 安装 Python 依赖（使用阿里云镜像加速）
5. ✅ 安装 Node.js 依赖
6. ✅ 启动后端服务（Flask，监听 9970 端口）
7. ✅ 健康检查，等待后端就绪
8. ✅ 数据预热（可选）
9. ✅ 启动前端服务（Vite，监听 3801 端口）
10. ✅ 输出访问地址和日志路径

### 方式二：手动启动

如果你想分步骤启动或自定义配置，可以手动启动各个服务。

#### 1. 安装后端依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

#### 2. 配置项目文件

```bash
# 复制示例配置文件
cp projects.json.example projects.json

# 编辑配置文件，添加你的项目
# 详见"配置说明"章节
```

#### 3. 启动后端服务

```bash
# 开发模式（带调试）
python run.py

# 或使用 Flask 直接启动
flask --app app.main:app run --host 0.0.0.0 --port 9970

# 生产模式（使用 Gunicorn）
gunicorn -c gunicorn.conf.py app.main:app
```

后端服务将在 `http://localhost:9970` 启动。

#### 4. 安装前端依赖并启动

打开新的终端窗口：

```bash
# 安装依赖
npm install

# 或使用镜像加速
npm install --registry=https://registry.npmmirror.com

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:3801` 启动。

#### 5. 访问应用

打开浏览器访问：

```
http://localhost:3801/?projects=项目1,项目2
```

将 `项目1,项目2` 替换为你在 `projects.json` 中配置的项目名称，或直接使用 Git URL。

---

## ⚙️ 配置说明

### 1. 项目配置文件 (`projects.json`)

该文件定义了项目名称到 Git 仓库路径的映射关系。

#### 配置格式

```json
{
  "项目名称": "仓库路径或URL"
}
```

#### 支持的仓库类型

1. **远程 Git URL**（推荐）

```json
{
  "my-project": "https://github.com/username/repo.git",
  "gitlab-project": "https://gitlab.com/company/project.git",
  "private-repo": "git@github.com:company/private-repo.git"
}
```

2. **本地相对路径**

```json
{
  "local-project": "repos/my-project",
  "another-project": "../another-project"
}
```

3. **本地绝对路径**

```json
{
  "production-app": "/var/repos/production-app",
  "legacy-system": "D:\\Projects\\legacy-system"
}
```

#### 使用方式

**方式 1：配置文件方式**

1. 在 `projects.json` 中配置项目
2. 访问 URL：`http://localhost:3801/?projects=my-project,another-project`

**方式 2：直接使用 Git URL（无需配置）**

直接在 URL 中使用完整的 Git URL：

```
http://localhost:3801/?projects=https://github.com/user/repo1,https://github.com/user/repo2
```

系统会自动克隆远程仓库到 `repos/_mirror/` 目录。

### 2. 环境变量配置 (`.env`)

创建 `.env` 文件以覆盖默认配置：

```env
# Flask 配置
DEBUG=False
SECRET_KEY=your-secret-key-change-in-production

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Git 配置
GIT_WORKSPACE=./repos
GIT_MAX_DEPTH=1000

# 缓存配置
CACHE_TTL=300

# 性能配置
MAX_WORKERS=5
MAX_PROJECTS=50
PROJECT_FETCH_TIMEOUT=180

# AI 分析服务配置
AI_ANALYZER_ENDPOINT=http://your-llm-service:7895/v1/chat/completions
AI_ANALYZER_MODEL=DeepSeek-R1-Distill-Qwen-14B-Q4_K_M:latest
AI_ANALYZER_MAX_TOKENS=4096
AI_ANALYZER_TIMEOUT=60
AI_ANALYZER_MAX_FILES=30
AI_ANALYZER_MAX_FILE_SIZE=204800
AI_ANALYZER_MAX_CHARACTERS=6000
AI_ANALYZER_CONCURRENCY=5

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=./logs

# 默认项目（可选，逗号分隔）
DEFAULT_PROJECTS=project1,project2
```

### 3. AI 代码分析配置

系统支持通过外部 LLM 服务分析代码中 AI 生成的比例。

#### 配置步骤

1. **部署 LLM 服务**：可以使用 Ollama、LM Studio 等本地部署 LLM
2. **配置环境变量**：在 `.env` 中设置 `AI_ANALYZER_ENDPOINT` 和 `AI_ANALYZER_MODEL`
3. **重启服务**：重启后端服务使配置生效

#### 注意事项

- 如果未配置或 AI 服务不可用，系统会使用默认值（50% AI / 50% 人工）
- AI 分析结果会缓存，默认 5 分钟
- 可以通过 `force_refresh=1` 参数强制刷新

### 4. 工作时间规则自定义

默认工作时间规则：

- **工作时间**：周一至周五 9:00-18:00
- **加班时间**：其他所有时间

如需自定义，修改 `app/models/commit.py` 中的 `is_work_hour` 属性：

```python
@property
def is_work_hour(self) -> bool:
    """自定义工作时间规则"""
    # 示例：修改为 8:00-17:00
    return self.is_weekday and 8 <= self.hour < 17
```

---

## 📖 使用指南

### 基本使用

#### 1. 查看单个项目

```
http://localhost:3801/?projects=my-project
```

#### 2. 查看多个项目

```
http://localhost:3801/?projects=project1,project2,project3
```

#### 3. 使用远程 Git URL

```
http://localhost:3801/?projects=https://github.com/user/repo1,https://github.com/user/repo2
```

#### 4. 强制刷新数据

在 URL 末尾添加 `&force_refresh=1`：

```
http://localhost:3801/?projects=my-project&force_refresh=1
```

### 图表说明

#### 按小时分布图

- **横轴**：0-23 小时
- **纵轴**：提交数量
- **说明**：展示 24 小时内的提交分布，可识别团队活跃时段

#### 按天分布图

- **横轴**：周一至周日
- **纵轴**：提交数量
- **说明**：展示一周内的提交分布，识别工作日与周末的工作节奏

#### 工作/加班占比饼图

- **绿色**：工作时间（周一至周五 9:00-18:00）
- **橙色**：加班时间（其他时间）
- **说明**：按时间维度统计，反映团队加班强度

#### 工作日/周末占比饼图

- **蓝色**：工作日（周一至周五）
- **灰色**：周末（周六至周日）
- **说明**：按日期维度统计，反映周末工作情况

#### AI 编写代码比例饼图

- **紫色**：AI 编写
- **青色**：人工编写
- **说明**：通过 LLM 分析代码片段，估算 AI 生成代码的比例

#### 贡献者滚动榜

自动滚动展示贡献者信息：

- 贡献者姓名和邮箱
- 提交次数
- 增加行数
- 删除行数
- 修改文件数

### 数据刷新策略

- **自动缓存**：数据默认缓存 5 分钟
- **手动刷新**：URL 参数 `force_refresh=1`
- **定期刷新**：前端每周一 10:00 自动刷新

---

## 🔌 API 文档

### 1. 获取汇总数据

获取多个项目的汇总统计数据。

```http
GET /api/dashboard/summary
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `projects` | string | 是 | 项目名称列表，逗号分隔 |
| `force_refresh` | string | 否 | 强制刷新缓存，值为 `1`、`true`、`yes` 或 `y` |

#### 请求示例

```bash
curl "http://localhost:9970/api/dashboard/summary?projects=project1,project2"
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "total_count": 1234,
    "repo_count": 2,
    "hour_data": [
      {"time": "00", "count": 10},
      {"time": "01", "count": 5},
      ...
    ],
    "week_data": [
      {"time": "周一", "count": 200},
      {"time": "周二", "count": 180},
      ...
    ],
    "work_hour_pl": [
      {"time": "工作时间", "count": 800},
      {"time": "加班时间", "count": 434}
    ],
    "work_week_pl": [
      {"time": "工作日", "count": 1000},
      {"time": "周末", "count": 234}
    ],
    "index_996": 0.35,
    "overtime_ratio": 0.35,
    "is_standard": false
  }
}
```

### 2. 获取贡献者列表

获取多个项目的贡献者排行榜。

```http
GET /api/dashboard/contributors
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `projects` | string | 是 | 项目名称列表，逗号分隔 |
| `force_refresh` | string | 否 | 强制刷新缓存 |

#### 请求示例

```bash
curl "http://localhost:9970/api/dashboard/contributors?projects=project1,project2"
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "name": "张三",
      "email": "zhangsan@example.com",
      "commits": 150,
      "additions": 5000,
      "deletions": 2000,
      "files_changed": 300,
      "projects": ["project1", "project2"],
      "project_names": ["项目1", "项目2"]
    },
    ...
  ]
}
```

### 3. 获取 AI 代码比例

获取单个项目的 AI 代码生成比例。

```http
GET /api/ai-ratio
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `repo` | string | 是 | 项目名称或 Git URL |
| `force_refresh` | string | 否 | 强制刷新缓存 |

#### 请求示例

```bash
curl "http://localhost:9970/api/ai-ratio?repo=my-project"
```

#### 响应示例

```json
{
  "ai_lines": 45.5,
  "human_lines": 54.5,
  "projects": 1,
  "total_files": 120,
  "sampled_files": 30,
  "analyzed_files": 28,
  "failed_files": 2,
  "average_ratio": 45.5,
  "total_weight": 30
}
```

### 4. 获取默认项目列表

获取服务器配置的默认项目列表。

```http
GET /api/dashboard/defaults
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "projects": ["project1", "project2", "project3"],
    "count": 3
  }
}
```

### 5. 健康检查

检查服务是否正常运行。

```http
GET /api/dashboard/health
```

#### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok",
    "message": "服务运行正常"
  }
}
```

---

## 🐳 部署指南

### Docker Compose 部署（推荐）

使用 Docker Compose 可以一键部署完整的服务栈（包括 Redis、后端、Nginx）。

#### 1. 准备配置文件

```bash
# 复制示例配置
cp projects.json.example projects.json

# 编辑配置文件
vim projects.json
```

#### 2. 启动服务

```bash
# 启动所有服务（不含 Nginx）
docker-compose up -d

# 或启动生产环境（包含 Nginx）
docker-compose --profile production up -d
```

#### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看 Redis 日志
docker-compose logs -f redis
```

#### 4. 停止服务

```bash
docker-compose down
```

#### 5. 访问应用

- **直接访问后端**：http://localhost:9970
- **通过 Nginx 访问**（生产模式）：http://localhost

### 手动 Docker 部署

#### 1. 构建镜像

```bash
docker build -t code996-dashboard .
```

#### 2. 运行容器

```bash
docker run -d \
  --name code996-dashboard \
  -p 9970:9970 \
  -v $(pwd)/repos:/app/repos \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/projects.json:/app/projects.json \
  -e REDIS_HOST=your-redis-host \
  -e REDIS_PORT=6379 \
  code996-dashboard
```

### 生产环境部署建议

#### 1. 使用 Gunicorn + Nginx

后端使用 Gunicorn 作为 WSGI 服务器，Nginx 作为反向代理。

**Gunicorn 配置** (`gunicorn.conf.py`)：

```python
workers = 4
bind = "0.0.0.0:9970"
timeout = 60
```

**Nginx 配置示例**：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /app/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:9970;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. 配置 HTTPS

使用 Let's Encrypt 申请免费 SSL 证书：

```bash
# 安装 Certbot
apt-get install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d your-domain.com
```

#### 3. 配置日志轮转

创建 `/etc/logrotate.d/code996` 文件：

```
/app/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0644 root root
}
```

#### 4. 监控与告警

- 使用 `docker-compose` 的 `healthcheck` 功能
- 配置 Prometheus + Grafana 监控
- 设置日志告警（ELK Stack 或云服务）

#### 5. 性能优化

- **Redis 持久化**：开启 AOF 或 RDB
- **Git 仓库缓存**：定期清理 `repos/_mirror/` 中不再使用的仓库
- **CDN 加速**：前端静态资源使用 CDN
- **数据库索引**：如果使用数据库存储数据，添加合适的索引

---

## 💻 开发指南

### 本地开发环境搭建

#### 1. 克隆项目

```bash
git clone <your-repo-url>
cd dashboard
```

#### 2. 安装后端依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
npm install
```

#### 4. 启动 Redis（可选）

```bash
# Docker 方式
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 或使用本地安装的 Redis
redis-server
```

#### 5. 启动后端

```bash
python run.py
```

后端运行在 `http://localhost:9970`

#### 6. 启动前端

```bash
npm run dev
```

前端运行在 `http://localhost:3801`

### 目录说明

- **`app/api/`**：API 路由和请求处理
- **`app/services/`**：业务逻辑层（Git 操作、统计计算、缓存等）
- **`app/models/`**：数据模型定义
- **`app/utils/`**：通用工具函数
- **`src/components/`**：Vue 组件
- **`src/views/`**：页面视图
- **`src/api/`**：前端 API 调用封装

### 代码规范

#### Python 后端

- 遵循 PEP 8 代码风格
- 使用类型注解（Type Hints）
- 函数和类添加文档字符串（Docstring）
- 使用 `logging` 记录日志

#### TypeScript 前端

- 使用 ESLint 和 Prettier 格式化代码
- 组件使用 Composition API
- 使用 TypeScript 类型定义
- CSS 使用 SCSS 预处理器

### 测试

#### 后端测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

#### 前端测试

```bash
# 安装测试依赖
npm install --save-dev @vue/test-utils vitest

# 运行测试
npm run test
```

### 调试技巧

#### 后端调试

1. **Flask 调试模式**：在 `.env` 中设置 `DEBUG=True`
2. **日志查看**：查看 `logs/app.log` 或 `logs/backend.log`
3. **断点调试**：使用 VS Code 的 Python Debugger

#### 前端调试

1. **Vue DevTools**：安装浏览器扩展
2. **控制台日志**：前端有详细的 `console.log` 输出
3. **网络请求**：浏览器开发者工具查看 API 请求

---

## ❓ 常见问题

### 1. 启动脚本报错：`Python 未找到`

**问题**：系统未安装 Python 或未添加到 PATH。

**解决方案**：

- 下载并安装 Python：https://www.python.org/downloads/
- 安装时勾选 "Add Python to PATH"
- 验证安装：`python --version`

### 2. 后端启动失败：`Redis 连接失败`

**问题**：系统未安装 Redis。

**解决方案**：

- Redis 是可选的，后端会自动降级到内存缓存
- 如需使用 Redis：
  - Docker：`docker run -d --name redis -p 6379:6379 redis:7-alpine`
  - Windows：下载 Redis for Windows
  - Linux：`apt-get install redis` 或 `yum install redis`

### 3. 前端访问报错：`Failed to fetch`

**问题**：后端未启动或端口不匹配。

**解决方案**：

- 检查后端是否运行：访问 `http://localhost:9970/api/dashboard/health`
- 检查前端代理配置：`vite.config.ts` 中的 `proxy` 设置
- 检查 CORS 配置：`app/middleware/cors.py`

### 4. 图表不显示数据

**问题**：项目配置错误或缓存问题。

**解决方案**：

- 检查 `projects.json` 配置是否正确
- 检查仓库路径是否存在
- 尝试强制刷新：URL 添加 `&force_refresh=1`
- 查看浏览器控制台和后端日志

### 5. AI 代码比例一直显示 50%

**问题**：AI 分析服务未配置或不可用。

**解决方案**：

- 检查 `.env` 中的 `AI_ANALYZER_ENDPOINT` 配置
- 确认 AI 服务正常运行
- 查看后端日志中的 AI 分析相关信息
- 如不需要 AI 分析，可忽略此功能

### 6. Git 仓库克隆慢或失败

**问题**：网络问题或仓库过大。

**解决方案**：

- 使用 Git 代理或 VPN
- 修改 Git 配置：`git config --global http.proxy http://proxy:port`
- 项目使用浅克隆（depth=1000），减少数据量
- 对于超大仓库，考虑本地克隆后使用本地路径

### 7. 贡献者滚动过快或过慢

**问题**：滚动速度需要调整。

**解决方案**：

修改 `src/components/CommitScroller.vue` 中的 `SCROLL_SPEED_PX_PER_SEC` 常量：

```typescript
const SCROLL_SPEED_PX_PER_SEC = 50 // 调整此值（默认 50）
```

### 8. Docker 容器启动失败

**问题**：端口占用或权限问题。

**解决方案**：

- 检查端口是否被占用：`netstat -tuln | grep 9970`
- 修改 `docker-compose.yml` 中的端口映射
- 检查 Docker 权限：`sudo usermod -aG docker $USER`
- 查看容器日志：`docker-compose logs backend`

### 9. 时区显示不正确

**问题**：Git commit 时间戳时区不一致。

**解决方案**：

- 后端使用 commit 的原始时区
- 确保 Git 配置正确：`git config --global user.timezone Asia/Shanghai`
- 或在 Docker 中设置时区环境变量：`TZ=Asia/Shanghai`

### 10. 日志文件过大

**问题**：日志累积过多占用磁盘空间。

**解决方案**：

- 配置日志轮转（见"部署指南"）
- 定期清理旧日志：`rm logs/*.log.*`
- 调整日志级别：`.env` 中设置 `LOG_LEVEL=WARNING`

---

## 🤝 贡献指南

欢迎参与 CODE996 项目的开发和改进！

### 如何贡献

1. **Fork 项目**

点击 GitHub 页面右上角的 "Fork" 按钮。

2. **克隆你的 Fork**

```bash
git clone https://github.com/your-username/dashboard.git
cd dashboard
```

3. **创建功能分支**

```bash
git checkout -b feature/your-feature-name
```

4. **进行修改**

- 添加新功能或修复 Bug
- 确保代码符合规范
- 添加必要的测试

5. **提交更改**

```bash
git add .
git commit -m "feat: add your feature description"
```

提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建或辅助工具变动

6. **推送到你的 Fork**

```bash
git push origin feature/your-feature-name
```

7. **创建 Pull Request**

在 GitHub 上创建 PR，描述你的更改内容。

### 开发规范

- **代码风格**：遵循项目现有的代码风格
- **测试覆盖**：为新功能添加单元测试
- **文档更新**：更新相关文档（README、API 文档等）
- **提交信息**：使用清晰的提交信息
- **分支管理**：一个功能或修复一个分支

### 报告问题

如果发现 Bug 或有功能建议，请创建 Issue：

1. 访问项目的 Issues 页面
2. 点击 "New Issue"
3. 选择合适的模板（Bug Report / Feature Request）
4. 详细描述问题或建议

### 社区准则

- 尊重所有贡献者
- 提供建设性的反馈
- 欢迎新手参与
- 保持友善和专业

---

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Flask](https://flask.palletsprojects.com/) - 轻量级 Web 框架
- [GitPython](https://gitpython.readthedocs.io/) - Git 仓库操作库
- [chart.xkcd](https://timqian.com/chart.xkcd/) - 手绘风格图表库
- [Redis](https://redis.io/) - 高性能缓存数据库

---

## 📞 联系方式

- **项目地址**：https://github.com/your-username/dashboard
- **问题反馈**：https://github.com/your-username/dashboard/issues
- **邮箱**：your-email@example.com

---

<div align="center">

**如果觉得这个项目有帮助，请给个 ⭐️ Star 支持一下！**

Made with ❤️ by CODE996 Team

</div>

