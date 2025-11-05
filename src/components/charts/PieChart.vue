<template>
  <BaseChart :data="data" chartType="Pie" :options="chartOptions" />
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
  backgroundColor: '#2a2a2a',
  strokeColor: '#fff',
  innerRadius: 0.4,  // 内环半径，创建更厚的圆环
  legendPosition: 1,  // 图例放置在右上角
  dataColors: ['#4CAF50', '#de335e'],  // AI 绿色，人工粉色
}
</script>

