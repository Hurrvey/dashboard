<template>
  <div class="dashboard">
    <transition name="fade" mode="out-in">
      <div v-if="isLoading" key="loading" class="dashboard-overlay loading-state" role="status" aria-live="polite">
        <div class="pixel-spinner"></div>
        <p class="primary">{{ loadingMessage }}</p>
        <p class="secondary">首次加载远程仓库可能需要几分钟，请耐心等待。</p>
      </div>
      <div v-else-if="errorMessage" key="error" class="dashboard-overlay error-state" role="alert">
        <h2>数据加载失败</h2>
        <p>{{ errorMessage }}</p>
        <button type="button" @click="retryLoad">重试加载</button>
      </div>
    </transition>

    <div class="dashboard-inner" v-show="!isLoading && !errorMessage">
      <!-- 顶部标题 -->
      <header class="dashboard-header">
        <h1>CODE996 DATA DASHBOARD</h1>
        <div class="meta">
          <span>项目数: {{ projectCount }}</span>
          <span>总提交数: {{ totalCommits }}</span>
          <span class="time">{{ currentTime }}</span>
        </div>
      </header>
      
      <!-- 上半部分 -->
      <section class="top-section">
        <div class="chart-row chart-row--distribution">
          <article class="chart-item">
            <header class="chart-header">
              <h2 class="chart-title">按小时 commit 分布</h2>
            </header>
            <div class="chart-body chart-body--bar">
              <BarChart :data="hourData" />
            </div>
          </article>

          <article class="chart-item">
            <header class="chart-header">
              <h2 class="chart-title">按天 commit 分布</h2>
            </header>
            <div class="chart-body chart-body--bar">
              <BarChart :data="weekData" />
            </div>
          </article>
        </div>

        <div class="chart-row chart-row--ratio">
          <article class="chart-item chart-item--pie">
            <header class="chart-header">
              <h2 class="chart-title">加班/工作占比（按小时）</h2>
            </header>
            <div class="chart-body chart-body--pie">
              <PieChart :data="workHourChartData" />
            </div>
          </article>

          <article class="chart-item chart-item--pie">
            <header class="chart-header">
              <h2 class="chart-title">工作日/周末占比</h2>
            </header>
            <div class="chart-body chart-body--pie">
              <PieChart :data="workWeekChartData" />
            </div>
          </article>

          <article class="chart-item chart-item--pie">
            <header class="chart-header">
              <h2 class="chart-title">AI 编写代码比例</h2>
            </header>
            <div class="chart-body chart-body--pie">
              <PieChart :data="aiRatioChart" />
            </div>
          </article>
        </div>
      </section>
      
      <!-- 下半部分 -->
      <section class="bottom-section">
        <CommitScroller :contributors="contributors" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { fetchDashboardData, fetchContributors, fetchAIRatio, fetchDefaultProjects } from '../api/dashboard'
import { getCurrentTimeString } from '../utils/time'
import BarChart from '../components/charts/BarChart.vue'
import PieChart from '../components/charts/PieChart.vue'
import CommitScroller from '../components/CommitScroller.vue'
import type { ChartData, Contributor, AIRatioData } from '../typings'

// 响应式数据
const projectCount = ref(0)
const totalCommits = ref(0)
const currentTime = ref('')
const hourData = ref<ChartData[]>([])
const weekData = ref<ChartData[]>([])
const workHourRatio = ref<ChartData[]>([])
const workWeekRatio = ref<ChartData[]>([])
const aiRatioData = ref<AIRatioData | null>(null)
const aiRatioLoading = ref(true)
const contributors = ref<Contributor[]>([])
const isLoading = ref(false)
const errorMessage = ref('')
const loadingMessage = ref('正在加载数据...')

// 更新时间
const updateTime = () => {
  currentTime.value = getCurrentTimeString()
}

// 从 URL 获取项目列表
const defaultProjects = ref<string[]>([])
const defaultProjectsLoaded = ref(false)

const getProjectsFromURL = (): string[] => {
  const urlParams = new URLSearchParams(window.location.search)
  const projectsParam = urlParams.get('projects')
  if (!projectsParam) {
    return []
  }
  return projectsParam.split(',').map(p => p.trim()).filter(p => p)
}

const resolveProjects = async (forceRefresh = false): Promise<string[]> => {
  const urlProjects = getProjectsFromURL()
  if (urlProjects.length) {
    return urlProjects
  }

  if (forceRefresh) {
    defaultProjectsLoaded.value = false
  }

  if (!defaultProjectsLoaded.value) {
    const fetched = await fetchDefaultProjects()
    defaultProjects.value = fetched
    defaultProjectsLoaded.value = true
  }

  return defaultProjects.value
}

// 初始化数据
interface InitOptions {
  forceRefresh?: boolean
}

const initDashboard = async (options: InitOptions = {}) => {
  const { forceRefresh = false } = options
  isLoading.value = true
  errorMessage.value = ''
  loadingMessage.value = '正在加载数据...'
  aiRatioData.value = null
  try {
    const projects = await resolveProjects(forceRefresh)
    if (!projects.length) {
      throw new Error('未检测到可用的项目配置。请访问 http://localhost:3801/dashboard 并在服务端配置 DEFAULT_PROJECTS 或 projects.json。')
    }

    if (projects.some(project => project.startsWith('http'))) {
      loadingMessage.value = '正在加载远程仓库数据，首次克隆可能会稍慢...'
    }

    console.log('🚀 加载项目:', projects)
    console.log('📊 项目数量:', projects.length)
    
    // 并行请求数据
    console.log('⏳ 正在请求后端数据...')
    const [summaryData, contributorsData] = await Promise.all([
      fetchDashboardData(projects, { forceRefresh }),
      fetchContributors(projects, { forceRefresh })
    ])
    
    console.log('✅ 汇总数据获取成功:', summaryData)
    console.log('✅ 贡献者数据获取成功:', contributorsData)
    
    // 更新总览数据
    projectCount.value = summaryData.repo_count
    totalCommits.value = summaryData.total_count
    hourData.value = summaryData.hour_data.map((item, index) => ({
      ...item,
      time: index % 2 === 0 ? item.time : ' '
    }))
    weekData.value = summaryData.week_data
    workHourRatio.value = summaryData.work_hour_pl
    workWeekRatio.value = summaryData.work_week_pl
    
    console.log('📈 图表数据已更新')
    console.log('   - 项目数:', projectCount.value)
    console.log('   - 总提交数:', totalCommits.value)
    console.log('   - 小时数据:', hourData.value.length, '条')
    console.log('   - 星期数据:', weekData.value.length, '条')
    
    // 更新贡献者数据
    contributors.value = contributorsData
    console.log('👥 贡献者数量:', contributors.value.length)
    
    // 请求 AI 代码比例
    fetchAIRatioData(projects, { forceRefresh })
    isLoading.value = false
    
  } catch (error) {
    console.error('❌ 初始化失败:', error)
    const message = error instanceof Error ? error.message : '未知错误'
    errorMessage.value = message || '加载仪表板数据失败，请稍后重试。'
    isLoading.value = false
  } finally {
    // 保证加载状态及时更新
    if (!errorMessage.value) {
      isLoading.value = false
    }
  }
}

// 请求 AI 代码比例
const fetchAIRatioData = async (projects: string[], options: InitOptions = {}) => {
  try {
    aiRatioLoading.value = true
    console.log('🤖 正在获取 AI 代码比例...')
    const ratioData = await fetchAIRatio(projects, { forceRefresh: options.forceRefresh })
    aiRatioData.value = ratioData
    console.log('✅ AI 代码比例获取成功:', ratioData)
    console.log('   - AI 行数:', ratioData.ai_lines)
    console.log('   - 人工行数:', ratioData.human_lines)
    console.log('   - 项目数:', ratioData.projects)
  } catch (error) {
    console.error('❌ 获取 AI 比例失败:', error)
    aiRatioData.value = null
  } finally {
    aiRatioLoading.value = false
  }
}

const retryLoad = () => {
  initDashboard({ forceRefresh: true })
}

const workHourSummary = computed(() => {
  const workItem = workHourRatio.value.find(item => item.time.includes('工作'))
  const overtimeItem = workHourRatio.value.find(item => item.time.includes('加班'))
  const work = workItem?.count ?? 0
  const overtime = overtimeItem?.count ?? 0
  const total = work + overtime
  const percent = (count: number) => (total > 0 ? ((count / total) * 100).toFixed(1) : '0.0')
  return {
    total,
    work,
    overtime,
    workPercent: percent(work),
    overtimePercent: percent(overtime),
  }
})

const workHourChartData = computed<ChartData[]>(() => {
  if (workHourSummary.value.total === 0) {
    return [
      { time: '工作时间', count: 1 },
      { time: '加班时间', count: 1 },
    ]
  }
  return workHourRatio.value
})

const workWeekSummary = computed(() => {
  const weekdayItem = workWeekRatio.value.find(item => item.time.includes('工作'))
  const weekendItem = workWeekRatio.value.find(item => item.time.includes('周末'))
  const weekday = weekdayItem?.count ?? 0
  const weekend = weekendItem?.count ?? 0
  const total = weekday + weekend
  const percent = (count: number) => (total > 0 ? ((count / total) * 100).toFixed(1) : '0.0')
  return {
    total,
    weekday,
    weekend,
    weekdayPercent: percent(weekday),
    weekendPercent: percent(weekend),
  }
})

const workWeekChartData = computed<ChartData[]>(() => {
  if (workWeekSummary.value.total === 0) {
    return [
      { time: '工作日', count: 1 },
      { time: '周末', count: 1 },
    ]
  }
  return workWeekRatio.value
})

const aiRatioSummary = computed(() => {
  const ai = aiRatioData.value?.ai_lines ?? 0
  const human = aiRatioData.value?.human_lines ?? 0
  const total = ai + human
  return {
    total,
    ai,
    human,
    aiPercent: total > 0 ? ((ai / total) * 100).toFixed(1) : '0.0',
    humanPercent: total > 0 ? ((human / total) * 100).toFixed(1) : '0.0',
  }
})

const aiRatioChart = computed<ChartData[]>(() => {
  if (aiRatioSummary.value.total === 0) {
    return [
      { time: 'AI编写', count: 1 },
      { time: '人工编写', count: 1 },
    ]
  }
  return [
    { time: 'AI编写', count: aiRatioSummary.value.ai },
    { time: '人工编写', count: aiRatioSummary.value.human },
  ]
})

// 定时器
let timeTimer: number
let scheduleTimer: number

const calculateDelayToNextMondayTen = (): number => {
  const now = new Date()
  const dayOfWeek = now.getDay() // 0=Sunday, 1=Monday
  const daysUntilMonday = (8 - dayOfWeek) % 7 || 0

  const target = new Date(now)
  target.setDate(now.getDate() + daysUntilMonday)
  target.setHours(10, 0, 0, 0)

  if (target <= now) {
    target.setDate(target.getDate() + 7)
  }

  return target.getTime() - now.getTime()
}

const scheduleWeeklyRefresh = () => {
  const delay = calculateDelayToNextMondayTen()
  scheduleTimer = window.setTimeout(() => {
    initDashboard({ forceRefresh: true })
    scheduleWeeklyRefresh()
  }, delay) as unknown as number
}

onMounted(() => {
  initDashboard()
  updateTime()
  timeTimer = setInterval(updateTime, 1000) as unknown as number
  scheduleWeeklyRefresh()
})

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer)
  if (scheduleTimer) clearTimeout(scheduleTimer)
})
</script>

<style lang="scss" scoped>
// 样式在 dashboard.scss 中定义
</style>

