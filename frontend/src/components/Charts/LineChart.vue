<template>
  <div class="line-chart" :style="{ height: height + 'px' }">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    data: any
    height?: number
  }>(),
  {
    height: 300
  }
)

const chartCanvas = ref<HTMLCanvasElement | null>(null)

// TODO: Implement actual chart rendering with Chart.js or ECharts
// For now, this is a placeholder
onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
})

function renderChart() {
  // Placeholder for chart rendering logic
  // In a real implementation, you would use a library like Chart.js:
  //
  // import Chart from 'chart.js/auto'
  //
  // new Chart(chartCanvas.value, {
  //   type: 'line',
  //   data: props.data,
  //   options: { ... }
  // })

  console.log('LineChart: Rendering chart with data:', props.data)
}
</script>

<style scoped lang="scss">
.line-chart {
  width: 100%;
  position: relative;

  canvas {
    width: 100%;
    height: 100%;
  }
}
</style>
