<template>
  <el-card class="stat-card" shadow="hover">
    <div class="stat-card-content">
      <div class="stat-card-icon" :style="{ background: iconBg, color: color }">
        <el-icon :size="24">
          <component :is="iconComponent" />
        </el-icon>
      </div>
      <div class="stat-card-info">
        <div class="stat-card-label">{{ title }}</div>
        <div class="stat-card-value">{{ formattedValue }}</div>
        <div v-if="trend !== undefined && trend !== null" class="stat-card-trend" :class="trendClass">
          <el-icon>
            <component :is="trendIcon" />
          </el-icon>
          <span>{{ trendText }}</span>
        </div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Download,
  Upload,
  User,
  Star,
  Files,
  Document,
  Check,
  TrendCharts,
  ArrowUp,
  ArrowDown,
  Minus
} from '@element-plus/icons-vue'
import { formatNumber, formatCompactNumber } from '@/utils/format'

const props = withDefaults(
  defineProps<{
    title: string
    value: number
    trend?: number
    icon?: string
    color?: string
    decimals?: number
    compact?: boolean
  }>(),
  {
    color: '#409eff',
    decimals: 0,
    compact: false
  }
)

const iconComponents = {
  Download,
  Upload,
  User,
  Star,
  Files,
  Document,
  Check,
  TrendCharts
}

const iconComponent = computed(() => {
  return iconComponents[props.icon as keyof typeof iconComponents] || TrendCharts
})

const iconBg = computed(() => {
  const color = props.color
  // Convert hex to rgba with low opacity for background
  const r = parseInt(color.slice(1, 3), 16)
  const g = parseInt(color.slice(3, 5), 16)
  const b = parseInt(color.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, 0.1)`
})

const formattedValue = computed(() => {
  if (props.compact) {
    return formatCompactNumber(props.value)
  }
  if (props.decimals > 0) {
    return props.value.toFixed(props.decimals)
  }
  return formatNumber(props.value)
})

const trendIcon = computed(() => {
  if (props.trend === undefined || props.trend === null) return Minus
  if (props.trend > 0) return ArrowUp
  if (props.trend < 0) return ArrowDown
  return Minus
})

const trendClass = computed(() => {
  if (props.trend === undefined || props.trend === null) return ''
  if (props.trend > 0) return 'trend-up'
  if (props.trend < 0) return 'trend-down'
  return 'trend-neutral'
})

const trendText = computed(() => {
  if (props.trend === undefined || props.trend === null) return ''
  const abs = Math.abs(props.trend)
  const formatted = abs >= 1 ? abs.toFixed(0) : abs.toFixed(1)
  return `${formatted}%`
})
</script>

<style scoped lang="scss">
.stat-card {
  height: 100%;

  &-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  &-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  &-info {
    flex: 1;
    min-width: 0;
  }

  &-label {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin-bottom: 4px;
  }

  &-value {
    font-size: 28px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.2;
  }

  &-trend {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    font-size: 12px;
    font-weight: 500;

    &.trend-up {
      color: #67c23a;
    }

    &.trend-down {
      color: #f56c6c;
    }

    &.trend-neutral {
      color: var(--el-text-color-secondary);
    }
  }
}
</style>
