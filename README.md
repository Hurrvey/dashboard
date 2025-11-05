# CODE996 数据看板

实时展示多项目代码提交情况以及 AI 编写占比的可视化系统，涵盖前后端一体化的一键启动体验。

---

## ✨ 亮点功能

- **一键启动脚本**：`start-all.bat` / `start-all.sh` 自动完成依赖检查、后端启动、前端启动与健康检查。
- **多项目数据聚合**：支持通过 URL 传入多个仓库地址自动汇总 Commit、贡献者与 996 指标。
- **AI 代码占比分析**：调用外部 LLM 服务估算项目内 AI 生成代码占比，并做可视化展示。
- **Redis/内存双模缓存**：默认使用 Redis，缺省时自动降级为内存缓存不停机。
- **贡献度排行升级**：基于代码变更行数衡量个人贡献，兼顾新增、删除与平均单次影响。
- **柱状图满幅渲染**：通过自定义 `chart.xkcd` 补丁与 `chartMargins` 配置，让 x/y 轴在卡片内自动撑满，更适合大屏展示。
- **贡献者慢速匀速滚动**：底部榜单采用 `requestAnimationFrame` 驱动的丝滑循环滚动，长列表也能持续播放无明显跳帧。

---

## ✅ 项目状态

- **前端**：已完成（Vue 3 + TypeScript + chart.xkcd）
- **后端**：已完成（Flask + GitPython + Redis 降级缓存）
- **脚本**：Windows / macOS / Linux 一键启动与停止脚本均可用

---

## 🚀 快速开始

### 方式一：一键启动（推荐）

**Windows**

```powershell
start-all.bat
# 运行结束后访问提示的仪表盘地址，例如:
# http://localhost:3801/?projects=https-gitea-zhifukj-com-cn-zhifukeji-dev-docs-59c55330e4d2

# 关闭全部服务
stop-all.bat
```

**macOS / Linux**

```bash
bash start-all.sh
# 关闭
bash stop-all.sh
```

脚本会自动：

1. 检查 Python / Node 环境并安装依赖
2. 初始化虚拟环境、安装后端依赖
3. 启动 Flask 后端并执行健康检查
4. 预热默认项目数据并启动前端 Vite 服务
5. 输出仪表盘访问地址与日志路径

### 方式二：手动启动

```bash
# 后端
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py                     # 默认 http://localhost:9970

# 前端（另开终端）
npm install
npm run dev                       # 默认 http://localhost:3801

# 在浏览器访问
http://localhost:3801/?projects=<项目标识1>,<项目标识2>
```

---

## 🔧 配置说明

### projects.json

用于声明需要汇总的本地仓库路径或远程仓库地址。执行启动脚本时若不存在，会自动从 `projects.json.example` 创建。

### 环境变量

- `.env`（可选）：覆盖默认的 Redis、AI 分析器等配置。
- 关键变量请参考 `后端技术开发文档.md` 与 `app/settings.py`。

### 默认项目

脚本会调用 `scripts/get_default_projects.py` 读取默认项目列表，亦可通过 `?projects=` URL 参数传入任意逗号分隔的仓库地址或本地目录别名。

### 图表与滚动细节

- **柱状图边距**：在 `src/components/charts/BarChart.vue` 中通过 `chartOptions.chartMargins` 调整四周留白；底层逻辑由 `src/utils/chartXkcd.ts` 自动套用到 `chart.xkcd`，无需改动第三方库。
- **贡献者滚动速度**：`CommitScroller` 使用常量 `SCROLL_SPEED_PX_PER_SEC`（默认 12）控制滚动速度；若用于更大屏幕，可在组件内调整该数值。

---

## 📚 相关文档

- [后端重构与前端接入指导.md](./后端重构与前端接入指导.md)：整体架构、改造背景与对接流程
- [API接口文档.md](./API接口文档.md)：详细接口协议与字段说明
- [后端技术开发文档.md](./后端技术开发文档.md)：后端实现细节、模块说明
- [前端技术开发方案.txt](./前端技术开发方案.txt)：前端页面结构、组件设计与样式规范

---

## 🧪 测试与验证

```bash
# 后端健康检查
curl http://localhost:9970/api/dashboard/health

# 汇总与贡献者 API
curl "http://localhost:9970/api/dashboard/summary?projects=test1,test2"
curl "http://localhost:9970/api/dashboard/contributors?projects=test1,test2"

# AI 代码比例
curl "http://localhost:9970/api/ai-ratio?repo=test1"
```

推荐在浏览器打开仪表盘并确认四个图表 + AI 饼图 + 贡献者列表全部正常渲染。

---

## 📡 API 概览

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 汇总数据 | GET | `/api/dashboard/summary?projects=xxx` | 多仓库 996 指标与 Commit 统计 |
| 贡献者列表 | GET | `/api/dashboard/contributors?projects=xxx` | 按 Commit 数量排序的成员列表 |
| 健康检查 | GET | `/api/dashboard/health` | 服务状态检查，用于脚本心跳 |
| AI 代码比例 | GET | `/api/ai-ratio?repo=xxx` | 单项目 AI 代码与人工代码占比 |

更详细的字段定义请参见 [API接口文档.md](./API接口文档.md)。

---

## 🛠️ 常见问题

- **健康检查一直显示 ERR？** 请确认 9970 端口未被占用，并查看 `logs/backend.log`。脚本已改进为宽容处理启动日志，若依旧失败可单独运行 `python run.py` 查看输出。
- **Redis 未启动怎么办？** 系统会自动降级为进程内内存缓存，可以稍后再连上 Redis。
- **AI 分析失败？** 确认 `.env` 内 AI 分析服务的 endpoint、API Key 与模型配置正确，或等待重试。
- **前端空白？** 检查 `npm run dev` 是否启动成功，浏览器控制台是否存在跨域或网络错误。

更多排查技巧请参考 [后端重构与前端接入指导.md](./后端重构与前端接入指导.md) 的 FAQ 部分。

---

## 📂 日志与排查

- 后端实时日志：`logs/backend.log`
- 前端输出：`logs/frontend.log`
- 启动脚本记录：`logs/startup-<timestamp>.log`
- Flask 应用日志轮转：`logs/app.log`

如需诊断，可配合 `diagnose.sh` / `diagnose.bat` 脚本收集信息。

---

## ✅ 开发完成清单

- [ ] `start-all` / `stop-all` 脚本往返成功，无健康检查错误
- [ ] 仪表盘页面 5 个可视化组件全部加载
- [ ] 后端 API 返回时间 < 2s（默认数据量）
- [ ] 追加新项目后，`projects.json` / URL 参数生效
- [ ] 关键日志落盘，便于排查

---

如需要更多帮助，请通过日志、文档或提 Issue 的方式联系我们。祝使用愉快！🚀
