<template>
  <div class="bar-chart" :style="{ height: height + 'px' }">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    data: any
    height?: number
    horizontal?: boolean
  }>(),
  {
    height: 300,
    horizontal: false
  }
)

const chartCanvas = ref<HTMLCanvasElement | null>(null)

onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
})

function renderChart() {
  // Placeholder for bar chart rendering
  console.log('BarChart: Rendering chart with data:', props.data)
}
</script>

<style scoped lang="scss">
.bar-chart {
  width: 100%;
  position: relative;

  canvas {
    width: 100%;
    height: 100%;
  }
}
</style>
