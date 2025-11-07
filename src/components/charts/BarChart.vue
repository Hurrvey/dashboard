<template>
  <BaseChart :data="data" chartType="Bar" :options="chartOptions" />
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
  unxkcdify: false,
  yTickCount: 5,
  chartMargins: {
    top: 12,
    right: 12,
    bottom: 24,
    left: 32,
  },
}
</script>

