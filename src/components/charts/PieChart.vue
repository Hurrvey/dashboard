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
    transform: translate(4%, -6%) scale(1.7);
  }

  :deep(svg .legend text) {
    font-size: clamp(1.6rem, 2.2vw, 2.6rem) !important;
    font-family: 'Pixel', sans-serif;
    dominant-baseline: middle;
  }

  :deep(svg .legend rect),
  :deep(svg .legend circle),
  :deep(svg .legend path) {
    transform-origin: center;
    transform: scale(1.7);
    stroke-width: 2.6;
  }
}
</style>

