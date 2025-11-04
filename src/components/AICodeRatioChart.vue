<template>
  <div class="ai-ratio-chart">
    <h2>AI 编写代码比例</h2>
    <div class="chart-content" v-if="!loading && hasData">
      <div class="chart-container">
        <PieChart :data="chartData" />
      </div>
      <div class="stats">
        <div class="stat-item ai">
          <span class="label">AI 编写</span>
          <span class="value">{{ aiPercentage }}%</span>
        </div>
        <div class="stat-item human">
          <span class="label">人工编写</span>
          <span class="value">{{ humanPercentage }}%</span>
        </div>
      </div>
    </div>
    <div class="loading" v-else-if="loading">
      <div class="pixel-spinner"></div>
      <p>加载中...</p>
    </div>
    <div class="no-data" v-else>
      <p>暂无数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import PieChart from './charts/PieChart.vue'
import { AIRatioData } from '../typings'

const props = defineProps<{
  data: AIRatioData | null
  loading: boolean
}>()

const hasData = computed(() => {
  return props.data && (props.data.ai_lines > 0 || props.data.human_lines > 0)
})

const aiPercentage = computed(() => {
  if (!props.data) return 0
  const total = props.data.ai_lines + props.data.human_lines
  return total > 0 ? ((props.data.ai_lines / total) * 100).toFixed(1) : 0
})

const humanPercentage = computed(() => {
  if (!props.data) return 0
  const total = props.data.ai_lines + props.data.human_lines
  return total > 0 ? ((props.data.human_lines / total) * 100).toFixed(1) : 0
})

const chartData = computed(() => [
  { time: 'AI编写', count: props.data?.ai_lines || 0 },
  { time: '人工编写', count: props.data?.human_lines || 0 }
])
</script>

<style lang="scss" scoped>
.ai-ratio-chart {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #2a2a2a;
  padding: 20px;
  box-shadow: 10px 10px 0px rgba(0, 0, 0, 0.1);
  
  h2 {
    font-size: 1.5em;
    margin-bottom: 10px;
    text-align: center;
    color: #fff;
    font-family: 'vcr-osd', monospace;
    flex-shrink: 0;
  }
  
  .chart-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 0;
    padding: 20px 0;
  }
  
  .chart-container {
    width: 100%;
    max-width: 450px;
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
  }
  
  .stats {
    display: flex;
    gap: 60px;
    justify-content: center;
    flex-shrink: 0;
    
    .stat-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      
      .label {
        font-size: 1.1em;
        color: #999;
        margin-bottom: 10px;
        font-family: 'Pixel', sans-serif;
      }
      
      .value {
        font-size: 2.5em;
        font-family: 'vcr-osd', monospace;
        font-weight: bold;
      }
      
      &.ai .value {
        color: #4CAF50;
      }
      
      &.human .value {
        color: #de335e;
      }
    }
  }
  
  .loading, .no-data {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    
    p {
      margin-top: 20px;
      color: #999;
      font-size: 1.2em;
    }
  }
}

.pixel-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #555;
  border-top-color: #de335e;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

// 响应式优化
@media (max-height: 800px) {
  .ai-ratio-chart {
    .chart-container {
      max-width: 350px;
    }
    
    .stats .stat-item .value {
      font-size: 2em;
    }
  }
}

@media (min-height: 1000px) {
  .ai-ratio-chart {
    .chart-container {
      max-width: 500px;
    }
  }
}
</style>

