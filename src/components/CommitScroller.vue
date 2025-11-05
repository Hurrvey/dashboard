<template>
  <div class="commit-scroller">
    <h2>🏆 Top Contributors</h2>
    <div class="scroller-container" v-if="sortedContributors.length > 0">
      <div
        class="marquee-track"
        :class="{ animate: shouldAnimate }"
        :style="animationStyle"
        ref="marqueeRef"
      >
        <div
          v-for="(contributor, index) in marqueeContributors"
          :key="`${contributor.email}-${index}`"
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
      </div>
    </div>
    <div class="no-data" v-else>
      <p>暂无贡献者数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Contributor } from '../typings'

const props = defineProps<{
  contributors: Contributor[]
}>()

const SPEED_PX_PER_SEC = 30

const marqueeRef = ref<HTMLDivElement | null>(null)
const animationDuration = ref(0)

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

const sortedContributors = computed(() => {
  const list = [...props.contributors]
  list.sort((a, b) => {
    const scoreDiff = (b.contributionScore ?? 0) - (a.contributionScore ?? 0)
    if (scoreDiff !== 0) return scoreDiff
    const additionDiff = (b.additions ?? 0) - (a.additions ?? 0)
    if (additionDiff !== 0) return additionDiff
    return (b.commits ?? 0) - (a.commits ?? 0)
  })
  return list
})

const shouldAnimate = computed(() => sortedContributors.value.length > 6)

const marqueeContributors = computed(() => {
  if (shouldAnimate.value) {
    return [...sortedContributors.value, ...sortedContributors.value]
  }
  return sortedContributors.value
})

const animationStyle = computed(() => {
  if (!shouldAnimate.value || animationDuration.value <= 0) {
    return { animation: 'none' }
  }
  return { animationDuration: `${animationDuration.value}s` }
})

const updateAnimation = () => {
  if (!marqueeRef.value || !shouldAnimate.value) {
    animationDuration.value = 0
    return
  }
  const totalHeight = marqueeRef.value.scrollHeight
  const distance = totalHeight / 2 // 因为列表重复了一遍
  animationDuration.value = distance > 0 ? distance / SPEED_PX_PER_SEC : 0
}

const handleResize = () => {
  nextTick(() => updateAnimation())
}

watch(() => props.contributors, () => {
  nextTick(() => updateAnimation())
})

onMounted(() => {
  nextTick(() => updateAnimation())
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
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
  
  .marquee-track {
    display: flex;
    flex-direction: column;
    gap: 15px;
    animation-name: scroll-up;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    animation-duration: 20s;
    animation-play-state: paused;
  }

  .marquee-track.animate {
    animation-play-state: running;
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

@keyframes scroll-up {
  0% {
    transform: translateY(0);
  }

  100% {
    transform: translateY(-50%);
  }
}
</style>

