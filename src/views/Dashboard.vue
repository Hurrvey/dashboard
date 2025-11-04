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
      <!-- 左侧：总览图表 -->
      <div class="charts-grid">
        <div class="chart-item">
          <h2>按小时 commit 分布</h2>
          <div class="chart-wrapper">
            <BarChart :data="hourData" />
          </div>
        </div>
        <div class="chart-item">
          <h2>工作/加班占比（按小时）</h2>
          <div class="chart-wrapper">
            <PieChart :data="workHourRatio" />
          </div>
        </div>
        <div class="chart-item">
          <h2>按天 commit 分布</h2>
          <div class="chart-wrapper">
            <BarChart :data="weekData" />
          </div>
        </div>
        <div class="chart-item">
          <h2>工作日/周末占比</h2>
          <div class="chart-wrapper">
            <PieChart :data="workWeekRatio" />
          </div>
        </div>
      </div>
      
      <!-- 右侧：AI 代码比例 -->
      <div class="ai-ratio-panel">
        <AICodeRatioChart :data="aiRatioData" :loading="aiRatioLoading" />
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
import { ref, onMounted, onUnmounted } from 'vue'
import { fetchDashboardData, fetchContributors, fetchAIRatio } from '../api/dashboard'
import { getCurrentTimeString } from '../utils/time'
import BarChart from '../components/charts/BarChart.vue'
import PieChart from '../components/charts/PieChart.vue'
import AICodeRatioChart from '../components/AICodeRatioChart.vue'
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
const getProjectsFromURL = (): string[] => {
  const urlParams = new URLSearchParams(window.location.search)
  const projectsParam = urlParams.get('projects')
  if (!projectsParam) {
    return []
  }
  return projectsParam.split(',').map(p => p.trim()).filter(p => p)
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
    const projects = getProjectsFromURL()
    if (!projects.length) {
      throw new Error('未检测到 projects 参数。请按 http://localhost:3801/?projects=test1,test2 的格式在地址栏指定项目。')
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
    hourData.value = summaryData.hour_data
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

// 定时器
let timeTimer: number
let refreshTimer: number
let hardRefreshTimer: number

onMounted(() => {
  // 初始化仪表板
  initDashboard()
  
  // 初始化时间
  updateTime()
  
  // 每秒更新时间
  timeTimer = setInterval(updateTime, 1000) as unknown as number
  
  // 每 5 分钟刷新数据
  refreshTimer = setInterval(() => initDashboard(), 5 * 60 * 1000) as unknown as number
  hardRefreshTimer = setInterval(() => initDashboard({ forceRefresh: true }), 60 * 60 * 1000) as unknown as number
})

onUnmounted(() => {
  if (timeTimer) clearInterval(timeTimer)
  if (refreshTimer) clearInterval(refreshTimer)
  if (hardRefreshTimer) clearInterval(hardRefreshTimer)
})
</script>

<style lang="scss" scoped>
// 样式在 dashboard.scss 中定义
</style>

