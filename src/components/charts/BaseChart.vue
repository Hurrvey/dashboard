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

const SVG_NS = 'http://www.w3.org/2000/svg'

function ensureLegendWrapper(legend: SVGGElement): SVGGElement {
  const existing = legend.querySelector('g.legend-scale-wrapper') as SVGGElement | null
  if (existing) {
    return existing
  }

  const wrapper = document.createElementNS(SVG_NS, 'g') as SVGGElement
  wrapper.classList.add('legend-scale-wrapper')

  while (legend.firstChild) {
    wrapper.appendChild(legend.firstChild)
  }

  legend.appendChild(wrapper)
  return wrapper
}

function applyLegendEnhancements(svg: SVGSVGElement, options: Record<string, any>) {
  const legend = svg.querySelector('g.legend') as SVGGElement | null

  if (!legend) {
    return
  }

  const legendScale = Number(options.legendScale) || 1
  const legendFontSize = Number(options.legendFontSize) || 0

  const wrapper = ensureLegendWrapper(legend)

  if (legendScale !== 1) {
    wrapper.setAttribute('transform', `scale(${legendScale})`)
  } else {
    wrapper.removeAttribute('transform')
  }

  if (legendFontSize > 0) {
    wrapper.querySelectorAll('text').forEach(node => {
      node.setAttribute('font-size', `${legendFontSize}`)
      ;(node as SVGTextElement).style.setProperty('font-size', `${legendFontSize}px`, 'important')
    })
  }
}

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

  // 确保数据至少有一个值，并且检查是否需要强制Y轴从0开始
  const dataValues = props.data.map(item => item.count)
  const minValue = Math.min(...dataValues)
  const maxValue = Math.max(...dataValues)
  
  // 检查是否所有值都为0
  const allZero = dataValues.every(v => v === 0)
  
  chartInstance = new ChartConstructor(svg, {
    data: {
      labels: props.data.map(item => item.time),
      datasets: [
        {
          data: dataValues,
        },
      ],
    },
    options: {
      width: chartWidth,
      height: chartHeight,
      // 如果所有数据都是0，设置Y轴范围为0-5，让0值柱子在底部
      ...(allZero ? { yTickCount: 3, dataMin: 0, dataMax: 5 } : {}),
      ...(props.options || {}),
    },
  })

  window.requestAnimationFrame(() => {
    applyLegendEnhancements(svg, props.options || {})
    
    // 确保Y轴从0开始 - 修改SVG中的Y轴刻度和柱子
    if (props.chartType === 'Bar') {
      try {
        // 如果所有数据都是0，隐藏柱子
        if (allZero) {
          // chart.xkcd 可能使用 rect 或 path 来绘制柱子
          const rects = svg.querySelectorAll('rect')
          rects.forEach(rect => {
            // 排除边框和背景矩形，只处理数据柱子
            const height = parseFloat(rect.getAttribute('height') || '0')
            const width = parseFloat(rect.getAttribute('width') || '0')
            // 数据柱子通常宽度较小且有高度
            if (width > 5 && width < 200 && height > 0) {
              rect.setAttribute('height', '0')
            }
          })
          
          // 也处理可能的 path 元素
          const paths = svg.querySelectorAll('path')
          paths.forEach(path => {
            const d = path.getAttribute('d') || ''
            // 如果是垂直的路径（柱子），尝试隐藏
            if (d && (d.includes('V') || d.includes('v'))) {
              const fill = path.getAttribute('fill')
              // 不是坐标轴（坐标轴通常是stroke）
              if (fill && fill !== 'none') {
                path.style.display = 'none'
              }
            }
          })
        }
        
        // 查找Y轴刻度文本
        const yAxisTexts = svg.querySelectorAll('text')
        const yAxisValues: number[] = []
        const yAxisElements: { element: SVGTextElement, value: number, y: number }[] = []
        
        yAxisTexts.forEach(text => {
          const content = text.textContent?.trim() || ''
          const numValue = parseFloat(content)
          if (!isNaN(numValue) && content === String(numValue)) {
            const y = parseFloat(text.getAttribute('y') || '0')
            yAxisElements.push({ element: text, value: numValue, y })
            yAxisValues.push(numValue)
          }
        })
        
        if (yAxisElements.length > 0) {
          const minYValue = Math.min(...yAxisValues)
          const maxYValue = Math.max(...yAxisValues)
          
          // 如果最小值不是0且所有值都是正数，调整刻度
          if (minYValue > 0 && minYValue < maxYValue) {
            // 按Y坐标排序（Y坐标大的在下面）
            yAxisElements.sort((a, b) => b.y - a.y)
            
            // 找到最下面的刻度（Y坐标最大的）
            const bottomElement = yAxisElements[0]
            
            // 如果最下面的刻度不是0，将其修改为0
            if (bottomElement && bottomElement.value !== 0) {
              bottomElement.element.textContent = '0'
            }
          }
        }
      } catch (e) {
        console.warn('Failed to adjust Y axis:', e)
      }
    }
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
