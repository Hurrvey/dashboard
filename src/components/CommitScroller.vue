<template>
  <div class="commit-scroller">
    <h2>🏆 Top Contributors</h2>
    <div class="scroller-container" v-if="contributors.length > 0">
      <transition-group name="slide" tag="div" class="contributor-list">
        <div 
          v-for="contributor in visibleContributors" 
          :key="contributor.email"
          class="contributor-card"
        >
          <div class="rank">#{{ contributor.rank }}</div>
          <div class="avatar">👤</div>
          <div class="info">
            <div class="name">{{ contributor.name }}</div>
            <div class="email">{{ contributor.email }}</div>
            <div class="metrics">
              <div class="metric-major">
                <span class="value">{{ formatNumber(contributor.contributionScore) }}</span>
                <span class="label">贡献行数</span>
              </div>
              <div class="metric-detail">
                <span>新增 {{ formatNumber(contributor.additions ?? 0) }}</span>
                <span>删除 {{ formatNumber(contributor.deletions ?? 0) }}</span>
                <span>净增 {{ formatSigned(contributor.netAdditions ?? 0) }}</span>
                <span>提交 {{ contributor.commits }}</span>
                <span>平均 {{ formatAverage(contributor.averageChange) }}/次</span>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
    <div class="no-data" v-else>
      <p>暂无贡献者数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Contributor } from '../typings'

const props = defineProps<{
  contributors: Contributor[]
}>()

const currentIndex = ref(0)
const pageSize = 6 // 每页显示 6 个

const numberFormatter = new Intl.NumberFormat('zh-CN', {
  maximumFractionDigits: 0,
})

const decimalFormatter = new Intl.NumberFormat('zh-CN', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

const formatNumber = (value: number) => numberFormatter.format(Math.max(0, Math.round(value ?? 0)))
const formatAverage = (value: number) => decimalFormatter.format(Math.max(0, value ?? 0))
const formatSigned = (value: number) => {
  if (!value) return '0'
  const prefix = value > 0 ? '+' : '-'
  return `${prefix}${numberFormatter.format(Math.abs(Math.round(value)))}`
}

// 当前可见的贡献者
const visibleContributors = computed(() => {
  if (props.contributors.length === 0) return []
  
  const start = currentIndex.value
  const end = start + pageSize
  
  // 如果不够一页，从头补充
  if (end <= props.contributors.length) {
    return props.contributors.slice(start, end)
  } else {
    const firstPart = props.contributors.slice(start)
    const remaining = pageSize - firstPart.length
    const secondPart = props.contributors.slice(0, remaining)
    return [...firstPart, ...secondPart]
  }
})

// 自动滚动
let scrollTimer: number

const autoScroll = () => {
  currentIndex.value += 1
  
  // 循环滚动
  if (currentIndex.value >= props.contributors.length) {
    currentIndex.value = 0
  }
}

onMounted(() => {
  if (props.contributors.length > pageSize) {
    // 每 3 秒滚动一次
    scrollTimer = setInterval(autoScroll, 3000) as unknown as number
  }
})

onUnmounted(() => {
  if (scrollTimer) {
    clearInterval(scrollTimer)
  }
})
</script>

<style lang="scss" scoped>
.commit-scroller {
  width: 100%;
  height: 100%;
  background-color: #212121;
  padding: 30px;
  overflow: hidden;
  
  h2 {
    font-size: 2em;
    text-align: center;
    margin-bottom: 30px;
    color: #de335e;
    text-shadow: 6px 6px 0px rgba(0, 0, 0, 0.2);
    font-family: 'vcr-osd', monospace;
  }
  
  .scroller-container {
    height: calc(100% - 100px);
    overflow: hidden;
  }
  
  .contributor-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .contributor-card {
    display: flex;
    align-items: center;
    background-color: #2a2a2a;
    padding: 20px 30px;
    box-shadow: 8px 8px 0px rgba(0, 0, 0, 0.2);
    border: 2px solid #444;
    transition: all 0.3s;
    
    &:hover {
      transform: translateX(10px);
      border-color: #de335e;
    }
    
    .rank {
      font-size: 2em;
      font-family: 'vcr-osd', monospace;
      color: #de335e;
      min-width: 80px;
      text-align: center;
    }
    
    .avatar {
      font-size: 3em;
      margin: 0 30px;
    }
    
    .info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;

      .name {
        font-size: 1.5em;
        color: #fff;
      }

      .email {
        font-size: 0.9em;
        color: #999;
      }

      .metrics {
        display: flex;
        flex-direction: column;
        gap: 12px;

        .metric-major {
          display: flex;
          align-items: baseline;
          gap: 10px;

          .value {
            font-size: 2.4em;
            font-family: 'vcr-osd', monospace;
            color: #4CAF50;
            font-weight: bold;
          }

          .label {
            font-size: 1em;
            color: #9acd32;
            text-transform: uppercase;
            letter-spacing: 1px;
          }
        }

        .metric-detail {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 8px 12px;
          font-size: 0.85em;
          color: #bbb;

          span {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 6px 10px;
          }
        }
      }
    }
  }
  
  .no-data {
    height: calc(100% - 100px);
    display: flex;
    align-items: center;
    justify-content: center;
    
    p {
      font-size: 1.5em;
      color: #999;
    }
  }
}

// 滑动动画
.slide-enter-active,
.slide-leave-active {
  transition: all 0.5s ease;
}

.slide-enter-from {
  transform: translateY(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>

