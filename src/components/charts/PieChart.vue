<template>
  <div class="pie-chart">
    <BaseChart :data="data" chartType="Pie" :options="chartOptions" />
  </div>
</template>
<script setup lang="ts">
import { ChartData } from '../../typings'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: {
    type: Array as () => ChartData[],
    default: () => [],
  },
})

const chartOptions = {
  backgroundColor: 'transparent',
  strokeColor: '#fff',
  innerRadius: 0.4,
  outerRadiusExpand: 22,
  legendPosition: 1,
  dataColors: ['#27A3DD', '#DD4526'],
  chartMargins: { top: 0, right: 0, bottom: 0, left: 0 },
  legendScale: 2.4,
  legendFontSize: 28,
}
</script>

<style scoped lang="scss">
.pie-chart {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateY(12px);

  :deep(.chart-container) {
    width: 100%;
    height: 100%;
  }

  :deep(svg .legend) {
    transform-origin: top right;
    transform: translate(2%, -8%);
  }

  :deep(svg .legend text) {
    font-family: 'Pixel', sans-serif;
    dominant-baseline: middle;
  }
}
</style>