# CODE996 数据看板

CODE996 Dashboard 是一个聚合多 Git 仓库提交信息的可视化系统，专注展示团队的工作/加班时段分布、周内节奏、贡献者榜单以及 AI 代码占比。项目提供“一次配置、随时监控”的体验，适合团队大屏展示与工作强度分析。

---

## 核心能力

- **多仓库聚合**：通过 URL 参数批量指定仓库（本地别名或远程地址），后端并发抓取并整合时间序列、周度分布与 996 指标。
- **时间维度洞察**：内建“工作/加班”与“工作日/周末”拆分，当前逻辑将周一至周五 9:00-18:00 视为工作时间，其它全部视为加班，确保统计口径清晰。
- **AI 代码占比**：联通外部 LLM 服务估算 AI 生成行数，并在饼图中呈现 AI / 人工占比。
- **顺滑可视化体验**：前端基于 Vue 3 + TypeScript + `chart.xkcd` 定制封装，包含满幅柱状图、渐入动画与贡献者循环滚动。
- **缓存 & 健康监控**：后端使用 Redis 优先、内存降级的缓存策略，并开放健康检查接口供脚本自检。
- **跨平台启动脚本**：提供 `start-all` / `stop-all` 脚本，自动处理依赖校验、服务启动、日志落盘、缓存预热。

---

## 技术栈

- **前端**：Vue 3、TypeScript、Vite、Sass、`chart.xkcd`
- **后端**：Flask、GitPython、Redis/内存缓存、pydantic 校验
- **脚本/工具**：Python 虚拟环境、Node 包管理、跨平台启动脚本、日志轮转

项目结构简览：

```
app/
  api/          # Flask 路由与响应封装
  services/     # Git 同步、统计聚合、缓存等服务
  utils/        # 指标计算、格式化工具
  models/       # Commit、DashboardStats 等数据模型
src/
  views/        # Vue 页面入口
  components/   # 图表、贡献者滚动等组件
  utils/        # 前端 chart 封装、时间工具
scripts/        # 启动/诊断脚本、默认项目读取
```

---

## 快速启动

### 1. 一键脚本（推荐）

**Windows**

```powershell
start-all.bat
# 根据提示访问仪表盘，例如 http://localhost:3801/?projects=repoA,repoB

# 停止全部服务
stop-all.bat
```

**macOS / Linux**

```bash
bash start-all.sh
# 停止
bash stop-all.sh
```

脚本会完成：环境检查 → 依赖安装 → 后端启动 → 健康检查 → 数据预热 → 前端启动，并输出访问地址和日志目录。

### 2. 手动启动（可自定义流程）

```bash
# 后端
python -m venv venv
source venv/bin/activate          # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
python run.py                     # 默认监听 http://localhost:9970

# 前端（新终端）
npm install
npm run dev                       # 默认监听 http://localhost:3801

# 浏览器访问，projects 参数使用逗号分隔
http://localhost:3801/?projects=<项目1>,<项目2>
```

> 若需刷新统计缓存，可在 URL 上追加 `&force_refresh=1`，或在页面选择“重试加载”。

---

## 配置指南

- **projects.json**：定义常用项目的本地映射或远程仓库地址。启动脚本会从 `projects.json.example` 自动拷贝缺省文件。
- **环境变量**：可在 `.env` 中覆盖 Redis、AI 分析服务等配置，详见 `app/settings.py` 及《后端技术开发文档》。
- **时区说明**：后端按照 commit 时间的原始时区数据计算指标，请确保仓库提交记录的时区正确，或在 Git 上配置统一的 `TZ`。
- **缓存策略**：`/api/dashboard/summary` 与 `/api/dashboard/contributors` 默认缓存 5 分钟，传入 `force_refresh=1` 可立即刷新。

---

## 仪表盘说明

- **按小时分布**：展示 24 小时提交数量，奇偶刻度交替显示以增强可读性。
- **按天分布**：周一至周日提交量，可快速识别工作日与周末节奏。
- **工作/加班占比**：后端根据 `Commit.is_work_hour` 标识（周一至周五 9:00-18:00 为工作，其余为加班）统计饼图。
- **工作日/周末占比**：区分周内与周末提交总量。
- **AI 编写比例**：汇总外部 AI 服务返回的行数，未获取到有效数据时使用伪装填充以保持图表完整。
- **贡献者滚动榜**：按综合贡献度排序，滚动速度可在 `src/components/CommitScroller.vue` 中调节。

---

## API 概览

| 接口 | 方法 | 示例 | 说明 |
|------|------|------|------|
| 汇总数据 | GET | `/api/dashboard/summary?projects=repoA,repoB` | 返回总提交、按小时/按日分布、工作/加班比例等字段 |
| 贡献者列表 | GET | `/api/dashboard/contributors?projects=repoA,repoB` | 合并去重后的贡献者排行榜 |
| 健康检查 | GET | `/api/dashboard/health` | 启动脚本的心跳接口 |
| AI 代码比例 | GET | `/api/ai-ratio?repo=repoA` | 单项目的 AI/人工行数统计 |

详细字段定义见 `API接口文档.md`。

---

## 验证与调试

```bash
# 后端健康检查
curl http://localhost:9970/api/dashboard/health

# 强制刷新统计数据
curl "http://localhost:9970/api/dashboard/summary?projects=test&force_refresh=1"

# 贡献者信息
curl "http://localhost:9970/api/dashboard/contributors?projects=test"

# AI 比例
curl "http://localhost:9970/api/ai-ratio?repo=test"
```

推荐打开浏览器确认所有图表与滚动榜正常渲染，再结合 `logs/` 目录中的后端、前端、脚本日志排查潜在问题。

---

## 常见问题

- **饼图数据不更新？** 检查是否命中缓存；在请求上加 `force_refresh=1` 或重启后端即可使新逻辑生效。
- **Redis 未部署？** 系统自动回退到进程内缓存，功能不受影响；部署 Redis 后重启即可接管。
- **启动脚本失败？** 检查 9970/3801 端口是否被占用，或直接运行 `python run.py`、`npm run dev` 获取详细日志。
- **AI 分析异常？** 核对 `.env` 中的 API URL/Key/模型配置，待外部服务恢复后重新刷新。
- **贡献者滚动过快？** 在 `CommitScroller` 组件中调整 `SCROLL_SPEED_PX_PER_SEC` 常量。


---


若你在使用中遇到问题，欢迎通过 Issue / PR / 邮件反馈。祝使用顺利，数据常亮！
