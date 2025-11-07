<template>
  <div class="commit-scroller">
    <h2 class="commit-scroller__title">🏆 Top Contributors</h2>
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
            <div
              v-if="hasProjects(contributor)"
              class="projects"
            >
              <span
                v-for="project in displayProjects(contributor)"
                :key="project"
                class="project-chip"
              >
                {{ project }}
              </span>
            </div>
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
          <div 
            v-if="contributor.dailyCommits && contributor.dailyCommits.length > 0" 
            class="daily-chart"
          >
            <h3 class="daily-chart-title">按天commit分布（上周）</h3>
            <div class="daily-chart-content">
              <BaseChart
                :data="contributor.dailyCommits"
                chartType="Bar"
                :options="miniChartOptions"
              />
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
import BaseChart from './charts/BaseChart.vue'

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

const hasProjects = (contributor: Contributor) => {
  return Boolean(contributor.projectNames?.length || contributor.projects?.length)
}

const displayProjects = (contributor: Contributor): string[] => {
  if (contributor.projectNames && contributor.projectNames.length) {
    return contributor.projectNames
  }
  if (contributor.projects && contributor.projects.length) {
    return contributor.projects
  }
  return []
}

const miniChartOptions = {
  backgroundColor: 'transparent',
  strokeColor: '#fff',
  unxkcdify: false,
  yTickCount: 5,
  chartMargins: {
    top: 12,
    right: 12,
    bottom: 24,
    left: 32,
  },
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
  border-radius: 18px;
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.08), 0 16px 30px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;

  &::before,
  &::after {
    display: none;
  }

  .commit-scroller__title {
    font-size: clamp(2.6rem, 3.6vw, 4.2rem);
    margin: clamp(14px, 2vh, 24px) 0 clamp(18px, 2.4vh, 28px);
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #D8335E;
    text-shadow: 0 0 18px rgba(0, 0, 0, 0.6);
    text-align: center;
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
    padding: clamp(22px, 2.6vh, 30px) clamp(28px, 2.8vw, 36px);
    box-shadow: 12px 12px 0px rgba(0, 0, 0, 0.28);
    border: 1px solid #3a3a3a;
    transition: all 0.3s;
    border-radius: 18px;
    gap: clamp(20px, 2vw, 30px);

    &:hover {
      transform: translateX(14px);
      border-color: #de335e;
    }

    .rank {
      font-size: clamp(2.4rem, 2.6vw, 3rem);
      font-family: 'vcr-osd', monospace;
      color: #de335e;
      min-width: clamp(84px, 6vw, 96px);
      text-align: center;
    }

    .avatar {
      font-size: clamp(3.6rem, 4.2vw, 4.8rem);
      margin: 0 clamp(28px, 2.6vw, 38px);
    }

    .info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: clamp(10px, 1.4vh, 16px);

      .name {
        font-size: clamp(3.6rem, 3vw, 4.2rem);
        color: #fff;
        letter-spacing: 0.04em;
      }

      .email {
        font-size: clamp(1.2rem, 1.6vw, 1.8rem);
        color: #b5b5b5;
      }

      .metrics {
        display: flex;
        flex-direction: column;
        gap: clamp(12px, 1.8vh, 18px);

        .metric-major {
          display: flex;
          align-items: baseline;
          gap: clamp(14px, 1.8vw, 18px);

          .value {
            font-size: clamp(3.2rem, 4vw, 4.6rem);
            font-family: 'vcr-osd', monospace;
            color: #4CAF50;
            font-weight: bold;
            text-shadow: 0 0 14px rgba(76, 175, 80, 0.35);
          }

          .label {
            font-size: clamp(1.3rem, 1.6vw, 1.9rem);
            color: #a6dd44;
            text-transform: uppercase;
            letter-spacing: 0.2em;
          }
        }

        .metric-detail {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: clamp(12px, 1.4vh, 16px) clamp(14px, 1.6vw, 20px);
          font-size: clamp(1.2rem, 1.6vw, 1.8rem);
          color: #d5d5d5;

          span {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: clamp(8px, 1.2vh, 12px) clamp(12px, 1.4vw, 18px);
          }
        }
      }
    }

    .projects {
      display: flex;
      flex-wrap: wrap;
      gap: clamp(10px, 1.4vh, 16px);

      .project-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: clamp(1.1rem, 1.6vw, 1.8rem);
        color: #ffe8f0;
        background: rgba(216, 51, 94, 0.15);
        border: 1px solid rgba(216, 51, 94, 0.45);
        border-radius: 999px;
        padding: clamp(6px, 1vh, 10px) clamp(14px, 1.4vw, 18px);
        text-transform: uppercase;
        letter-spacing: 0.12em;
        box-shadow: 0 4px 10px rgba(216, 51, 94, 0.2);
      }
    }

    .daily-chart {
      width: clamp(380px, 28vw, 520px);
      height: clamp(240px, 20vh, 360px);
      flex-shrink: 0;
      background: transparent;
      border: 1px solid transparent;
      border-radius: 12px;
      padding: clamp(12px, 1.5vh, 16px);
      box-shadow: none;
      display: flex;
      flex-direction: column;
      gap: clamp(8px, 1vh, 12px);

      .daily-chart-title {
        font-size: clamp(1.4rem, 1.8vw, 2rem);
        color: #fff;
        text-align: center;
        margin: 0;
        padding: 0;
        letter-spacing: 0.05em;
        font-weight: 500;
      }

      .daily-chart-content {
        flex: 1;
        min-height: 0;
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

