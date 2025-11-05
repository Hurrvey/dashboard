# CODE996 数据看板 - 前后端接口文档

## 文档概述

本文档定义了 CODE996 数据看板前端与后端之间的所有 API 接口规范。

**版本**: v1.0.0  
**更新日期**: 2025-10-31  
**协议**: HTTP/HTTPS  
**数据格式**: JSON  

---

## 目录

1. [接口基础信息](#接口基础信息)
2. [接口列表](#接口列表)
3. [接口详细说明](#接口详细说明)
4. [数据类型定义](#数据类型定义)
5. [错误码说明](#错误码说明)
6. [调用示例](#调用示例)

---

## 接口基础信息

### 基础 URL

```
生产环境: https://your-domain.com/api/dashboard
开发环境: http://localhost:8000/api/dashboard
```

### 通用请求头

```http
Content-Type: application/json
Accept: application/json
```

### 通用响应头

```http
Content-Type: application/json; charset=utf-8
```

### 字符编码

所有接口统一使用 **UTF-8** 编码。

---

## 接口列表

| 序号 | 接口名称 | 请求方法 | 接口路径 | 说明 |
|------|---------|---------|---------|------|
| 1 | 获取汇总数据 | GET | `/api/dashboard/summary` | 获取所有项目的汇总统计数据 |
| 2 | 获取贡献者列表 | GET | `/api/dashboard/contributors` | 获取所有项目的贡献者列表 |
| 3 | 获取 AI 代码比例 | GET | `/api/ai-ratio` | 获取单个项目的 AI 代码比例 |

---

## 接口详细说明

### 1. 获取汇总数据

#### 接口信息

- **接口名称**: 获取汇总数据
- **接口路径**: `/api/dashboard/summary`
- **请求方法**: GET
- **接口说明**: 获取所有指定项目的汇总统计数据，包括按小时/按天 commit 分布、工作时间分析等

#### 请求参数

**Query 参数**

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| projects | string | 是 | 项目列表，多个项目用英文逗号分隔 | `project1,project2,project3` |

**请求示例**

```http
GET /api/dashboard/summary?projects=project-a,project-b,project-c HTTP/1.1
Host: your-domain.com
Content-Type: application/json
```

#### 响应数据

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "total_count": 1250,
    "repo_count": 3,
    "hour_data": [
      { "time": "00", "count": 10 },
      { "time": "01", "count": 5 },
      { "time": "02", "count": 3 },
      { "time": "03", "count": 2 },
      { "time": "04", "count": 1 },
      { "time": "05", "count": 4 },
      { "time": "06", "count": 8 },
      { "time": "07", "count": 15 },
      { "time": "08", "count": 25 },
      { "time": "09", "count": 80 },
      { "time": "10", "count": 95 },
      { "time": "11", "count": 88 },
      { "time": "12", "count": 45 },
      { "time": "13", "count": 60 },
      { "time": "14", "count": 105 },
      { "time": "15", "count": 110 },
      { "time": "16", "count": 98 },
      { "time": "17", "count": 85 },
      { "time": "18", "count": 70 },
      { "time": "19", "count": 95 },
      { "time": "20", "count": 110 },
      { "time": "21", "count": 125 },
      { "time": "22", "count": 88 },
      { "time": "23", "count": 42 }
    ],
    "week_data": [
      { "time": "周一", "count": 220 },
      { "time": "周二", "count": 195 },
      { "time": "周三", "count": 210 },
      { "time": "周四", "count": 185 },
      { "time": "周五", "count": 175 },
      { "time": "周六", "count": 125 },
      { "time": "周日", "count": 140 }
    ],
    "work_hour_pl": [
      { "time": "工作时间", "count": 650 },
      { "time": "加班时间", "count": 600 }
    ],
    "work_week_pl": [
      { "time": "工作日", "count": 985 },
      { "time": "周末", "count": 265 }
    ],
    "index_996": 0.85,
    "overtime_ratio": 0.48,
    "is_standard": false
  }
}
```

**字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | number | 响应状态码，200 表示成功 |
| message | string | 响应消息 |
| data | object | 数据对象 |
| data.start_date | string | 统计开始日期 (YYYY-MM-DD) |
| data.end_date | string | 统计结束日期 (YYYY-MM-DD) |
| data.total_count | number | 总 commit 数量 |
| data.repo_count | number | 项目数量 |
| data.hour_data | array | 按小时统计的数据，24 个元素 (00-23) |
| data.hour_data[].time | string | 小时值，格式: "00" ~ "23" |
| data.hour_data[].count | number | 该小时的 commit 数量 |
| data.week_data | array | 按星期统计的数据，7 个元素 |
| data.week_data[].time | string | 星期值: "周一" ~ "周日" |
| data.week_data[].count | number | 该天的 commit 数量 |
| data.work_hour_pl | array | 工作/加班时间占比，2 个元素 |
| data.work_hour_pl[].time | string | "工作时间" 或 "加班时间" |
| data.work_hour_pl[].count | number | 对应时间段的 commit 数量 |
| data.work_week_pl | array | 工作日/周末占比，2 个元素 |
| data.work_week_pl[].time | string | "工作日" 或 "周末" |
| data.work_week_pl[].count | number | 对应时间段的 commit 数量 |
| data.index_996 | number | 996 指数，范围 0-1 |
| data.overtime_ratio | number | 加班比例，范围 0-1 |
| data.is_standard | boolean | 是否符合标准工作时间 |

**错误响应**

```json
{
  "code": 400,
  "message": "参数错误: projects 参数不能为空",
  "data": null
}
```

```json
{
  "code": 500,
  "message": "服务器内部错误",
  "data": null
}
```

---

### 2. 获取贡献者列表

#### 接口信息

- **接口名称**: 获取贡献者列表
- **接口路径**: `/api/dashboard/contributors`
- **请求方法**: GET
- **接口说明**: 获取所有指定项目的贡献者列表，按照代码变更量（贡献度）降序排列

#### 请求参数

**Query 参数**

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| projects | string | 是 | 项目列表，多个项目用英文逗号分隔 | `project1,project2,project3` |

**请求示例**

```http
GET /api/dashboard/contributors?projects=project-a,project-b,project-c HTTP/1.1
Host: your-domain.com
Content-Type: application/json
```

#### 响应数据

**成功响应 (200)**

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "rank": 1,
      "name": "张三",
      "email": "zhangsan@example.com",
      "contribution_score": 15650,
      "total_changes": 15650,
      "average_change": 64.06,
      "net_additions": 9250,
      "commits": 245,
      "additions": 12450,
      "deletions": 3200
    },
    {
      "rank": 2,
      "name": "李四",
      "email": "lisi@example.com",
      "contribution_score": 11900,
      "total_changes": 11900,
      "average_change": 62.96,
      "net_additions": 7700,
      "commits": 189,
      "additions": 9800,
      "deletions": 2100
    },
    {
      "rank": 3,
      "name": "王五",
      "email": "wangwu@example.com",
      "contribution_score": 10700,
      "total_changes": 10700,
      "average_change": 68.59,
      "net_additions": 7100,
      "commits": 156,
      "additions": 8900,
      "deletions": 1800
    }
  ]
}
```

**字段说明**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| code | number | 是 | 响应状态码，200 表示成功 |
| message | string | 是 | 响应消息 |
| data | array | 是 | 贡献者数组，按贡献度降序排列 |
| data[].rank | number | 是 | 排名，从 1 开始 |
| data[].name | string | 是 | 贡献者姓名 |
| data[].email | string | 是 | 贡献者邮箱 |
| data[].contribution_score | number | 是 | 贡献度分值，等于新增行数 + 删除行数 |
| data[].total_changes | number | 是 | 总变更行数（与 contribution_score 相同） |
| data[].average_change | number | 是 | 平均每次提交的变更行数 |
| data[].net_additions | number | 是 | 净新增行数（新增 - 删除） |
| data[].commits | number | 是 | commit 次数 |
| data[].additions | number | 否 | 新增代码行数（可选） |
| data[].deletions | number | 否 | 删除代码行数（可选） |

**注意事项**

1. 数组默认按 `contribution_score` 字段降序排列
2. `rank` 字段必须连续递增，从 1 开始
3. `average_change` 四舍五入保留两位小数
4. `additions` 和 `deletions` 字段为可选，前端会做兼容处理

**错误响应**

```json
{
  "code": 400,
  "message": "参数错误: projects 参数不能为空",
  "data": null
}
```

---

### 3. 获取 AI 代码比例

#### 接口信息

- **接口名称**: 获取 AI 代码比例
- **接口路径**: `/api/ai-ratio`
- **请求方法**: GET
- **接口说明**: 获取单个项目中 AI 编写代码的比例数据
- **特别说明**: 此接口由独立的 AI 分析服务提供，默认运行在 `http://localhost:9970`

#### 请求参数

**Query 参数**

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| repo | string | 是 | 单个项目的标识或路径 | `project-a` 或 `https://github.com/user/repo` |

**请求示例**

```http
GET /api/ai-ratio?repo=project-a HTTP/1.1
Host: localhost:9970
Content-Type: application/json
```

或

```http
GET /api/ai-ratio?repo=https%3A%2F%2Fgithub.com%2Fuser%2Frepo HTTP/1.1
Host: localhost:9970
Content-Type: application/json
```

#### 响应数据

**成功响应 (200)**

```json
{
  "ai_lines": 15680,
  "human_lines": 28340
}
```

**字段说明**

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ai_lines | number | 是 | AI 编写的代码行数 |
| human_lines | number | 是 | 人工编写的代码行数 |

**注意事项**

1. 前端会并行请求多个项目的数据
2. 前端会自动汇总所有项目的 AI 和人工代码行数
3. 如果某个项目请求失败，不影响其他项目
4. 响应格式应尽可能简洁，只包含必要字段

**错误响应**

```json
{
  "error": "项目不存在",
  "ai_lines": 0,
  "human_lines": 0
}
```

或 HTTP 状态码 404/500 等

---

## 数据类型定义

### TypeScript 类型定义

前端使用的 TypeScript 类型定义如下（位于 `src/typings/index.ts`）：

```typescript
/**
 * 图表数据类型
 */
export interface ChartData {
  time: string
  count: number
}

/**
 * 仪表板汇总数据
 */
export interface DashboardSummary {
  start_date: string
  end_date: string
  total_count: number
  repo_count: number
  hour_data: ChartData[]
  week_data: ChartData[]
  work_hour_pl: ChartData[]
  work_week_pl: ChartData[]
  index_996: number
  overtime_ratio: number
  is_standard: boolean
}

/**
 * 贡献者数据
 */
export interface Contributor {
  rank: number
  name: string
  email: string
  commits: number
  additions?: number
  deletions?: number
}

/**
 * AI 代码比例数据
 */
export interface AIRatioData {
  ai_lines: number
  human_lines: number
  projects: number
}
```

### JSON Schema

#### DashboardSummary Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": [
    "start_date", "end_date", "total_count", "repo_count",
    "hour_data", "week_data", "work_hour_pl", "work_week_pl",
    "index_996", "overtime_ratio", "is_standard"
  ],
  "properties": {
    "start_date": { "type": "string", "format": "date" },
    "end_date": { "type": "string", "format": "date" },
    "total_count": { "type": "integer", "minimum": 0 },
    "repo_count": { "type": "integer", "minimum": 1 },
    "hour_data": {
      "type": "array",
      "minItems": 24,
      "maxItems": 24,
      "items": {
        "type": "object",
        "properties": {
          "time": { "type": "string", "pattern": "^([01][0-9]|2[0-3])$" },
          "count": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "week_data": {
      "type": "array",
      "minItems": 7,
      "maxItems": 7,
      "items": {
        "type": "object",
        "properties": {
          "time": { "type": "string", "enum": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"] },
          "count": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "work_hour_pl": {
      "type": "array",
      "minItems": 2,
      "maxItems": 2,
      "items": {
        "type": "object",
        "properties": {
          "time": { "type": "string", "enum": ["工作时间", "加班时间"] },
          "count": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "work_week_pl": {
      "type": "array",
      "minItems": 2,
      "maxItems": 2,
      "items": {
        "type": "object",
        "properties": {
          "time": { "type": "string", "enum": ["工作日", "周末"] },
          "count": { "type": "integer", "minimum": 0 }
        }
      }
    },
    "index_996": { "type": "number", "minimum": 0, "maximum": 1 },
    "overtime_ratio": { "type": "number", "minimum": 0, "maximum": 1 },
    "is_standard": { "type": "boolean" }
  }
}
```

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 | 处理方式 |
|--------|------|----------|
| 200 | 成功 | 正常处理返回数据 |
| 400 | 请求参数错误 | 检查参数格式和必填项 |
| 401 | 未授权 | 需要身份验证 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 资源不存在 | 项目不存在或路径错误 |
| 500 | 服务器内部错误 | 联系后端排查 |
| 502 | 网关错误 | 后端服务不可用 |
| 503 | 服务不可用 | 服务暂时不可用，稍后重试 |

### 业务错误码

在响应 JSON 中的 `code` 字段：

| 错误码 | 说明 | 示例 |
|--------|------|------|
| 200 | 成功 | `{ "code": 200, "message": "success" }` |
| 400 | 参数错误 | `{ "code": 400, "message": "参数错误: projects 不能为空" }` |
| 404 | 资源不存在 | `{ "code": 404, "message": "项目不存在" }` |
| 500 | 服务器错误 | `{ "code": 500, "message": "服务器内部错误" }` |

---

## 调用示例

### 示例 1: 获取汇总数据

**cURL 请求**

```bash
curl -X GET "http://localhost:8000/api/dashboard/summary?projects=project1,project2,project3" \
  -H "Content-Type: application/json"
```

**JavaScript 请求**

```javascript
const projects = ['project1', 'project2', 'project3']
const response = await fetch(`/api/dashboard/summary?projects=${encodeURIComponent(projects.join(','))}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
})
const data = await response.json()
console.log(data)
```

**Python 请求**

```python
import requests

projects = ['project1', 'project2', 'project3']
url = f"http://localhost:8000/api/dashboard/summary?projects={','.join(projects)}"
response = requests.get(url, headers={'Content-Type': 'application/json'})
data = response.json()
print(data)
```

---

### 示例 2: 获取贡献者列表

**cURL 请求**

```bash
curl -X GET "http://localhost:8000/api/dashboard/contributors?projects=project1,project2" \
  -H "Content-Type: application/json"
```

**JavaScript 请求**

```javascript
const projects = ['project1', 'project2']
const response = await fetch(`/api/dashboard/contributors?projects=${encodeURIComponent(projects.join(','))}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
})
const data = await response.json()
console.log(data)
```

---

### 示例 3: 获取 AI 代码比例

**cURL 请求**

```bash
curl -X GET "http://localhost:9970/api/ai-ratio?repo=project1" \
  -H "Content-Type: application/json"
```

**JavaScript 请求（单个项目）**

```javascript
const repo = 'project1'
const response = await fetch(`http://localhost:9970/api/ai-ratio?repo=${encodeURIComponent(repo)}`, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
  },
})
const data = await response.json()
console.log(data)
```

**JavaScript 请求（批量汇总）**

```javascript
const projects = ['project1', 'project2', 'project3']

// 并行请求所有项目
const promises = projects.map(repo =>
  fetch(`http://localhost:9970/api/ai-ratio?repo=${encodeURIComponent(repo)}`)
    .then(res => res.json())
    .catch(err => {
      console.warn(`项目 ${repo} 请求失败:`, err)
      return { ai_lines: 0, human_lines: 0 }
    })
)

const results = await Promise.all(promises)

// 汇总数据
const totalAiLines = results.reduce((sum, res) => sum + (res.ai_lines || 0), 0)
const totalHumanLines = results.reduce((sum, res) => sum + (res.human_lines || 0), 0)

console.log({
  ai_lines: totalAiLines,
  human_lines: totalHumanLines,
  projects: results.length
})
```

---

## 前端配置说明

### 修改 API 基础地址

如果后端 API 地址与默认配置不同，需要修改以下文件：

**文件位置**: `dashboard/src/api/dashboard.ts`

```typescript
// 修改这两个常量
const API_BASE = '/api/dashboard'  // 修改为实际的后端地址
const AI_SERVICE_BASE = 'http://localhost:9970'  // 修改为 AI 服务地址
```

**示例配置**

```typescript
// 生产环境
const API_BASE = 'https://api.example.com/api/dashboard'
const AI_SERVICE_BASE = 'https://ai.example.com'

// 开发环境（使用代理）
const API_BASE = '/api/dashboard'
const AI_SERVICE_BASE = 'http://localhost:9970'
```

---

## 跨域处理

### 开发环境代理配置

在 `vite.config.ts` 中配置代理：

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

### 生产环境 CORS 配置

后端需要设置 CORS 响应头：

```http
Access-Control-Allow-Origin: https://your-frontend-domain.com
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## 性能优化建议

### 1. 数据缓存

建议后端实现缓存机制，避免频繁计算：

```
缓存时间: 5 分钟
缓存键: projects 参数的 MD5 值
```

### 2. 请求频率限制

建议设置 API 请求频率限制：

```
限制: 每分钟 60 次请求
超限响应: HTTP 429 Too Many Requests
```

### 3. 数据压缩

建议启用 gzip/br 压缩：

```http
Content-Encoding: gzip
```

### 4. 分页支持（可选）

如果贡献者数量很多，建议支持分页：

```
GET /api/dashboard/contributors?projects=xxx&page=1&page_size=50
```

---

## 测试建议

### 单元测试要点

1. 测试参数验证（空值、格式错误）
2. 测试数据格式（字段类型、必填项）
3. 测试边界条件（空数组、超大数值）
4. 测试错误处理（服务不可用、超时）

### 集成测试要点

1. 测试端到端流程
2. 测试并发请求
3. 测试数据一致性
4. 测试性能（响应时间、吞吐量）

---

## 联系方式

如有疑问，请联系：

- 前端开发: frontend@example.com
- 后端开发: backend@example.com
- 技术支持: support@example.com

---

## 更新日志

### v1.0.0 (2025-10-31)

- 初始版本
- 定义三个核心接口
- 完整的类型定义和示例

---

**文档结束**

