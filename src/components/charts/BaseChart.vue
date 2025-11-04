<template>
  <div class="chart-container" ref="containerRef">
    <svg class="chart" ref="chartRef"></svg>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, watch, defineProps, defineExpose } from 'vue'
import chartXkcd from 'chart.xkcd'
import { ChartData } from '../../typings'

const props = defineProps({
  data: {
    type: Array as () => ChartData[],
    default: () => [],
  },
  chartType: {
    type: String as () => 'Bar' | 'Pie',
    required: true,
  },
  options: {
    type: Object,
    default: () => ({
      backgroundColor: '#212121',
      strokeColor: '#fff',
    }),
  },
})

const containerRef = ref<HTMLDivElement | null>(null)
const chartRef = ref<SVGElement | null>(null)
let chartInstance: any = null
let resizeObserver: ResizeObserver | null = null
let pendingInit: number | null = null

function init() {
  if (!chartRef.value || !containerRef.value) return
  
  // 获取容器的实际尺寸
  const containerWidth = containerRef.value.clientWidth
  const containerHeight = containerRef.value.clientHeight
  
  if (containerWidth === 0 || containerHeight === 0) {
    if (pendingInit !== null) {
      clearTimeout(pendingInit)
    }
    pendingInit = window.setTimeout(() => {
      pendingInit = null
      init()
    }, 200)
    return
  }

  // 完全清除旧图表（包括所有子元素）
  if (chartRef.value) {
    while (chartRef.value.firstChild) {
      chartRef.value.removeChild(chartRef.value.firstChild)
    }
    chartRef.value.classList.add('chart')
  }
  chartInstance = null

  const ChartConstructor = chartXkcd[props.chartType]
  if (!ChartConstructor) {
    console.error(`图表类型 ${props.chartType} 不存在`)
    return
  }

  // 计算合适的图表尺寸
  let chartWidth, chartHeight
  
  if (props.chartType === 'Pie') {
    // 饼图：强制正方形，确保圆形
    const size = Math.min(containerWidth, containerHeight)
    chartWidth = Math.max(size * 0.9, 200)  // 使用90%的容器尺寸
    chartHeight = chartWidth  // ⭐ 关键：宽高必须相等
  } else {
    // 柱状图：适应容器
    chartWidth = Math.max(containerWidth * 0.95, 200)
    chartHeight = Math.max(containerHeight * 0.95, 150)
  }

  // 设置 SVG 的固定尺寸（不使用 viewBox，避免缩放问题）
  chartRef.value.setAttribute('width', String(Math.floor(chartWidth)))
  chartRef.value.setAttribute('height', String(Math.floor(chartHeight)))
  
  // 使用 CSS 居中 SVG
  chartRef.value.style.display = 'block'
  chartRef.value.style.margin = '0 auto'

  try {
    chartInstance = new ChartConstructor(chartRef.value, {
      data: {
        labels: props.data.map((item: ChartData) => item.time),
        datasets: [
          {
            data: props.data.map((item: ChartData) => item.count),
          },
        ],
      },
      options: {
        ...props.options,
        width: chartWidth,
        height: chartHeight,
        xLabel: props.chartType === 'Bar' ? '' : undefined,
        yLabel: props.chartType === 'Bar' ? '' : undefined,
      },
    })
    
    console.log(`图表初始化成功 [${props.chartType}]:`, Math.floor(chartWidth), 'x', Math.floor(chartHeight))
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

// 监听数据变化
watch(() => props.data, () => {
  if (props.data && props.data.length > 0) {
    nextTick(() => {
      init()
    })
  }
}, { deep: true })

// 防抖函数
function debounce(func: Function, wait: number) {
  let timeout: number | null = null
  return function executedFunction(...args: any[]) {
    const later = () => {
      timeout = null
      func(...args)
    }
    if (timeout !== null) {
      clearTimeout(timeout)
    }
    timeout = window.setTimeout(later, wait)
  }
}

const debouncedInit = debounce(init, 300)

onMounted(() => {
  nextTick(() => {
    // 延迟初始化，确保容器已经渲染
    setTimeout(() => {
      init()
    }, 100)
    
    // 监听容器大小变化
    if (containerRef.value && typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        debouncedInit()
      })
      resizeObserver.observe(containerRef.value)
    }
    
    // 监听窗口大小变化（备用方案）
    window.addEventListener('resize', debouncedInit)
  })
})

onBeforeUnmount(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value)
    resizeObserver.disconnect()
  }
  window.removeEventListener('resize', debouncedInit)
  if (pendingInit !== null) {
    clearTimeout(pendingInit)
  }
})

defineExpose({
  chartInstance,
  refresh: init,
})
</script>
<style lang="scss" scoped>
.chart-container {
  width: 100%;
  height: 100%;
  position: relative;
  min-width: 0;
  min-height: 0;
}

.chart {
  width: 100%;
  height: 100%;
  display: block;
}
</style>

