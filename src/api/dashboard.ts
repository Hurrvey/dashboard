import type { DashboardSummary, Contributor, AIRatioData } from '../typings'

// 后端 API 基础地址配置
// 所有请求都通过 Vite 代理到后端，避免 CORS 问题
const API_BASE = '/api/dashboard'  // 通过代理访问 dashboard API
const AI_API_BASE = '/api'  // 通过代理访问 AI API

interface FetchOptions {
  forceRefresh?: boolean
}

function buildQuery(params: Record<string, string | undefined>): string {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      search.set(key, value)
    }
  })
  return search.toString()
}

export async function fetchDashboardData(projects: string[], options: FetchOptions = {}): Promise<DashboardSummary> {
  try {
    const query = buildQuery({
      projects: projects.join(','),
      force_refresh: options.forceRefresh ? '1' : undefined,
    })

    const response = await fetch(`${API_BASE}/summary?${query}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // 后端返回格式: { code, message, data }
    if (result.code === 200) {
      return result.data
    } else {
      throw new Error(result.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取仪表板汇总数据失败:', error)
    throw error
  }
}

/**
 * 获取贡献者列表
 * @param projects 项目列表
 * @returns 贡献者数组，按 commit 数量降序排列
 */
export async function fetchContributors(projects: string[], options: FetchOptions = {}): Promise<Contributor[]> {
  try {
    const query = buildQuery({
      projects: projects.join(','),
      force_refresh: options.forceRefresh ? '1' : undefined,
    })

    const response = await fetch(`${API_BASE}/contributors?${query}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    
    // 后端返回格式: { code, message, data }
    if (result.code === 200) {
      return result.data
    } else {
      throw new Error(result.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取贡献者列表失败:', error)
    throw error
  }
}

/**
 * 获取 AI 代码比例（批量）
 */
export async function fetchAIRatio(projects: string[], options: FetchOptions = {}): Promise<AIRatioData> {
  try {
    // 并行请求所有项目的 AI 比例
    const promises = projects.map(repo =>
      fetch(`${AI_API_BASE}/ai-ratio?${buildQuery({
        repo,
        force_refresh: options.forceRefresh ? '1' : undefined,
      })}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`)
        return res.json()
      }).catch(err => {
        console.warn(`获取项目 ${repo} 的 AI 比例失败:`, err)
        return { ai_lines: 0, human_lines: 0 }
      })
    )
    
    const results = await Promise.all(promises)
    
    // 汇总所有项目的数据
    const totalAiLines = results.reduce((sum, res) => sum + (res.ai_lines || 0), 0)
    const totalHumanLines = results.reduce((sum, res) => sum + (res.human_lines || 0), 0)
    const projectsCount = results.length
    const hasValidData = results.some(res => (res.ai_lines || 0) + (res.human_lines || 0) > 0)

    return {
      ai_lines: hasValidData ? totalAiLines : projectsCount > 0 ? 50 : 0,
      human_lines: hasValidData ? totalHumanLines : projectsCount > 0 ? 50 : 0,
      projects: projectsCount
    }
  } catch (error) {
    console.error('获取 AI 比例失败:', error)
    // 返回默认数据
    return { ai_lines: 0, human_lines: 0, projects: 0 }
  }
}

