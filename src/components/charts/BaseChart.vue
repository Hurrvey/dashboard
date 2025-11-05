<template>
  <div class='chart-container' ref='containerRef'>
    <svg class='chart' ref='chartRef'></svg>
  </div>
</template>

<script setup lang='ts'>
import { ref, onMounted, onBeforeUnmount, nextTick, watch, defineProps, defineExpose } from 'vue'
import chartXkcd from '../../utils/chartXkcd'
import type { ChartData } from '../../typings'

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
    type: Object as () => Record<string, any>,
    default: () => ({
      backgroundColor: '#212121',
      strokeColor: '#fff',
      unxkcdify: false,
    }),
  },
})

const containerRef = ref<HTMLDivElement | null>(null)
const chartRef = ref<SVGSVGElement | null>(null)
let chartInstance: any = null
let resizeObserver: ResizeObserver | null = null
let pendingRender: number | null = null

function clearChart() {
  if (!chartRef.value) return
  while (chartRef.value.firstChild) {
    chartRef.value.removeChild(chartRef.value.firstChild)
  }
}

function renderChart() {
  const svg = chartRef.value
  const container = containerRef.value

  if (!svg || !container) return

  const width = container.clientWidth
  const height = container.clientHeight

  if (!width || !height) {
    if (pendingRender !== null) {
      window.clearTimeout(pendingRender)
    }
    pendingRender = window.setTimeout(() => {
      pendingRender = null
      renderChart()
    }, 160)
    return
  }

  clearChart()
  chartInstance = null

  const ChartConstructor = (chartXkcd as any)[props.chartType]
  if (!ChartConstructor) {
    console.error('图表类型 ' + props.chartType + ' 不存在')
    return
  }

  const chartWidth = Math.max(width, 1)
  const chartHeight = Math.max(height, 1)

  svg.setAttribute('width', String(chartWidth))
  svg.setAttribute('height', String(chartHeight))
  svg.setAttribute('viewBox', `0 0 ${chartWidth} ${chartHeight}`)
  svg.style.width = '100%'
  svg.style.height = '100%'
  svg.style.display = 'block'
  svg.style.margin = '0'
  svg.style.background = (props.options as any)?.backgroundColor ?? 'transparent'
  svg.style.overflow = 'hidden'

  chartInstance = new ChartConstructor(svg, {
    data: {
      labels: props.data.map(item => item.time),
      datasets: [
        {
          data: props.data.map(item => item.count),
        },
      ],
    },
    options: {
      width: chartWidth,
      height: chartHeight,
      ...(props.options || {}),
    },
  })
}

function debounce<T extends (...args: any[]) => void>(fn: T, delay: number) {
  let timer: number | null = null
  return (...args: Parameters<T>) => {
    if (timer !== null) {
      window.clearTimeout(timer)
    }
    timer = window.setTimeout(() => {
      timer = null
      fn(...args)
    }, delay)
  }
}

const debouncedRender = debounce(renderChart, 160)

watch(
  () => props.data,
  () => {
    nextTick(() => {
      debouncedRender()
    })
  },
  { deep: true }
)

watch(
  () => props.chartType,
  () => {
    nextTick(() => {
      debouncedRender()
    })
  }
)

watch(
  () => props.options,
  () => {
    nextTick(() => {
      debouncedRender()
    })
  },
  { deep: true }
)

onMounted(() => {
  nextTick(() => {
    renderChart()

    if (containerRef.value && typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        debouncedRender()
      })
      resizeObserver.observe(containerRef.value)
    }

    window.addEventListener('resize', debouncedRender)
  })
})

onBeforeUnmount(() => {
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value)
    resizeObserver.disconnect()
  }
  window.removeEventListener('resize', debouncedRender)
  if (pendingRender !== null) {
    window.clearTimeout(pendingRender)
  }
})

defineExpose({
  get chartInstance() {
    return chartInstance
  },
  refresh: renderChart,
})
</script>

<style lang='scss' scoped>
.chart-container {
  width: 100%;
  height: 100%;
  position: relative;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.chart {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
