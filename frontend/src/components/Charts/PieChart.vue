<template>
  <div class="pie-chart" :style="{ height: height + 'px' }">
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

onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
})

function renderChart() {
  // Placeholder for pie chart rendering
  console.log('PieChart: Rendering chart with data:', props.data)
}
</script>

<style scoped lang="scss">
.pie-chart {
  width: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;

  canvas {
    max-width: 100%;
    max-height: 100%;
  }
}
</style>
