<template>
  <div class="commit-scroller">
    <h2>🏆 Top Contributors</h2>
    <div class="scroller-container" v-if="sortedContributors.length > 0">
      <div
        class="marquee-track"
        :style="marqueeStyle"
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

const marqueeRef = ref<HTMLDivElement | null>(null)
const translateY = ref(0)
const enableAnimation = ref(false)
const contentHeight = ref(0)
const SCROLL_SPEED_PX_PER_SEC = 18

let animationFrameId: number | null = null
let lastTimestamp: number | null = null

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

const marqueeContributors = computed(() => {
  if (!sortedContributors.value.length) return []
  return [...sortedContributors.value, ...sortedContributors.value]
})

const marqueeStyle = computed(() => ({
  transform: `translateY(-${translateY.value}px)`
}))

const stopScrolling = () => {
  if (animationFrameId !== null) {
    window.cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
  lastTimestamp = null
}

const step = (timestamp: number) => {
  if (lastTimestamp === null) {
    lastTimestamp = timestamp
  }
  const delta = (timestamp - lastTimestamp) / 1000
  lastTimestamp = timestamp

  translateY.value += delta * SCROLL_SPEED_PX_PER_SEC
  const cycle = contentHeight.value
  if (cycle > 0) {
    while (translateY.value >= cycle) {
      translateY.value -= cycle
    }
  }

  animationFrameId = window.requestAnimationFrame(step)
}

const startScrolling = () => {
  if (!enableAnimation.value || animationFrameId !== null) return
  lastTimestamp = null
  animationFrameId = window.requestAnimationFrame(step)
}

const updateMeasurements = () => {
  if (!marqueeRef.value) return

  const containerHeight = marqueeRef.value.parentElement?.clientHeight ?? 0
  const totalHeight = marqueeRef.value.scrollHeight
  contentHeight.value = totalHeight / 2

  if (totalHeight > containerHeight && sortedContributors.value.length > 0) {
    enableAnimation.value = true
  } else {
    enableAnimation.value = false
    translateY.value = 0
  }
}

const handleResize = () => {
  nextTick(() => {
    updateMeasurements()
  })
}

watch(() => props.contributors, () => {
  nextTick(() => {
    translateY.value = 0
    updateMeasurements()
  })
})

watch(enableAnimation, value => {
  nextTick(() => {
    if (!marqueeRef.value) {
      stopScrolling()
      return
    }

    if (value) {
      const totalHeight = marqueeRef.value.scrollHeight
      contentHeight.value = totalHeight / 2
      startScrolling()
    } else {
      contentHeight.value = marqueeRef.value.scrollHeight
      stopScrolling()
      translateY.value = 0
    }
  })
})

onMounted(() => {
  nextTick(() => {
    updateMeasurements()
    if (enableAnimation.value) {
      startScrolling()
    }
  })
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopScrolling()
  window.removeEventListener('resize', handleResize)
})
</script>

<style lang="scss" scoped>
.commit-scroller {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #2a2a2a;
  padding: 0px 30px 30px;
  overflow: hidden;

  h2 {
    font-size: clamp(2.4rem, 3.2vw, 3.2rem);
    text-align: center;
    margin-bottom: 20px;
    color: #de335e;
    text-shadow: 6px 6px 0px rgba(0, 0, 0, 0.2);
    font-family: 'vcr-osd', monospace;
  }

  .scroller-container {
    flex: 0 0 clamp(1300px, 52vh, 1350px);
    height: clamp(1300px, 52vh, 1350px);
    overflow: hidden;
    position: relative;
    align-self: stretch;
  }

  .marquee-track {
    display: flex;
    flex-direction: column;
    gap: 10px;
    will-change: transform;
  }
  
  .contributor-card {
    display: flex;
    align-items: center;
    background-color: #2a2a2a;
    padding: 14px 24px;
    box-shadow: 8px 8px 0px rgba(0, 0, 0, 0.2);
    border: 1px solid #3a3a3a;
    transition: all 0.3s;

    &:hover {
      transform: translateX(10px);
      border-color: #de335e;
    }

    .rank {
      font-size: 1.6em;
      font-family: 'vcr-osd', monospace;
      color: #de335e;
      min-width: 64px;
      text-align: center;
    }

    .avatar {
      font-size: 2.4em;
      margin: 0 24px;
    }

    .info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .name {
        font-size: 1.2em;
        color: #fff;
      }

      .email {
        font-size: 0.8em;
        color: #999;
      }

      .metrics {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .metric-major {
          display: flex;
          align-items: baseline;
          gap: 8px;

          .value {
            font-size: 1.8em;
            font-family: 'vcr-osd', monospace;
            color: #4CAF50;
            font-weight: bold;
          }

          .label {
            font-size: 0.85em;
            color: #9acd32;
            text-transform: uppercase;
            letter-spacing: 1px;
          }
        }

        .metric-detail {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 6px 10px;
          font-size: 0.75em;
          color: #bbb;

          span {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 5px;
            padding: 5px 8px;
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
</style>

