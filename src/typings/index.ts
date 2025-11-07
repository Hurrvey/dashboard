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
  contributionScore: number
  totalChanges: number
  averageChange: number
  netAdditions: number
  commits: number
  additions?: number
  deletions?: number
  projects?: string[]
  projectNames?: string[]
  dailyCommits?: ChartData[]
}

/**
 * AI 代码比例数据
 */
export interface AIRatioData {
  ai_lines: number
  human_lines: number
  projects: number
}

