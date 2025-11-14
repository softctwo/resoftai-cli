<template>
  <div class="performance-monitor">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>性能监控</h2>
      </template>
      <template #extra>
        <el-button-group>
          <el-button :icon="Refresh" @click="refreshData" :loading="loading">
            刷新
          </el-button>
          <el-button :icon="Download" @click="exportMetrics">
            导出数据
          </el-button>
        </el-button-group>
      </template>
    </el-page-header>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="API请求总数" :value="stats.total_requests">
            <template #prefix>
              <el-icon color="#409EFF"><DataAnalysis /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span class="stat-label">今日: {{ stats.today_requests || 0 }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="平均响应时间" :value="stats.avg_response_time" :precision="2" suffix="ms">
            <template #prefix>
              <el-icon color="#67C23A"><Timer /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span :class="getChangeClass(stats.response_time_change)">
              <el-icon v-if="stats.response_time_change < 0"><Bottom /></el-icon>
              <el-icon v-else><Top /></el-icon>
              {{ Math.abs(stats.response_time_change) }}%
            </span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="活跃用户" :value="stats.active_users">
            <template #prefix>
              <el-icon color="#E6A23C"><UserFilled /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span class="stat-label">峰值: {{ stats.peak_users || 0 }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="错误率" :value="stats.error_rate" :precision="2" suffix="%">
            <template #prefix>
              <el-icon color="#F56C6C"><WarningFilled /></el-icon>
            </template>
          </el-statistic>
          <div class="stat-footer">
            <span :class="getChangeClass(-stats.error_rate_change)">
              {{ stats.error_count || 0 }} 个错误
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row 1 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>请求趋势</span>
            <el-select v-model="timeRange" size="small" style="float: right; width: 120px">
              <el-option label="最近1小时" value="1h" />
              <el-option label="最近6小时" value="6h" />
              <el-option label="最近24小时" value="24h" />
              <el-option label="最近7天" value="7d" />
            </el-select>
          </template>
          <div ref="requestChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>响应时间分布</span>
          </template>
          <div ref="responseTimeChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row 2 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>系统资源使用</span>
          </template>
          <div class="resource-metrics">
            <div class="metric-item">
              <div class="metric-header">
                <span>CPU使用率</span>
                <span class="metric-value">{{ stats.cpu_usage }}%</span>
              </div>
              <el-progress :percentage="stats.cpu_usage" :color="getProgressColor(stats.cpu_usage)" />
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span>内存使用率</span>
                <span class="metric-value">{{ stats.memory_usage }}%</span>
              </div>
              <el-progress :percentage="stats.memory_usage" :color="getProgressColor(stats.memory_usage)" />
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span>磁盘使用率</span>
                <span class="metric-value">{{ stats.disk_usage }}%</span>
              </div>
              <el-progress :percentage="stats.disk_usage" :color="getProgressColor(stats.disk_usage)" />
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span>网络吞吐量</span>
                <span class="metric-value">{{ formatBytes(stats.network_throughput) }}/s</span>
              </div>
              <el-progress :percentage="(stats.network_throughput / 10485760) * 100" :color="['#67C23A', '#E6A23C', '#F56C6C']" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <span>API端点性能</span>
          </template>
          <el-table :data="endpointStats" style="width: 100%" max-height="300">
            <el-table-column prop="endpoint" label="端点" width="200" show-overflow-tooltip />
            <el-table-column prop="requests" label="请求数" width="100" align="center" sortable />
            <el-table-column prop="avg_time" label="平均时间(ms)" width="120" align="center" sortable>
              <template #default="{ row }">
                <el-tag :type="getResponseTimeType(row.avg_time)" size="small">
                  {{ row.avg_time }}ms
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="error_rate" label="错误率" align="center" sortable>
              <template #default="{ row }">
                <span :style="{ color: row.error_rate > 5 ? '#F56C6C' : '#67C23A' }">
                  {{ row.error_rate }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Alerts -->
    <el-card shadow="never" class="alerts-card">
      <template #header>
        <span>实时告警</span>
        <el-badge :value="activeAlerts.length" class="alert-badge">
          <el-icon><Bell /></el-icon>
        </el-badge>
      </template>
      <el-timeline v-if="activeAlerts.length > 0">
        <el-timeline-item
          v-for="alert in activeAlerts"
          :key="alert.id"
          :timestamp="formatDate(alert.timestamp)"
          :type="getAlertType(alert.severity)"
        >
          <el-alert
            :title="alert.message"
            :type="getAlertType(alert.severity)"
            :description="alert.details"
            show-icon
            :closable="false"
          />
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无活跃告警" :image-size="100" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download,
  DataAnalysis,
  Timer,
  UserFilled,
  WarningFilled,
  Bell,
  Top,
  Bottom
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// State
const loading = ref(false)
const timeRange = ref('24h')
const stats = ref({
  total_requests: 0,
  today_requests: 0,
  avg_response_time: 0,
  response_time_change: 0,
  active_users: 0,
  peak_users: 0,
  error_rate: 0,
  error_rate_change: 0,
  error_count: 0,
  cpu_usage: 0,
  memory_usage: 0,
  disk_usage: 0,
  network_throughput: 0
})

const endpointStats = ref([])
const activeAlerts = ref([])

// Chart refs
const requestChart = ref(null)
const responseTimeChart = ref(null)
let requestChartInstance = null
let responseTimeChartInstance = null
let updateInterval = null

// Fetch performance metrics
const fetchMetrics = async () => {
  loading.value = true
  try {
    // Simulated data - replace with actual API call
    // const response = await performanceAPI.getMetrics()

    // Mock data
    stats.value = {
      total_requests: Math.floor(Math.random() * 100000),
      today_requests: Math.floor(Math.random() * 5000),
      avg_response_time: Math.random() * 200 + 50,
      response_time_change: (Math.random() - 0.5) * 20,
      active_users: Math.floor(Math.random() * 50),
      peak_users: Math.floor(Math.random() * 100),
      error_rate: Math.random() * 5,
      error_rate_change: (Math.random() - 0.5) * 2,
      error_count: Math.floor(Math.random() * 10),
      cpu_usage: Math.floor(Math.random() * 100),
      memory_usage: Math.floor(Math.random() * 100),
      disk_usage: Math.floor(Math.random() * 100),
      network_throughput: Math.floor(Math.random() * 10485760) // bytes/s
    }

    endpointStats.value = [
      { endpoint: '/api/projects', requests: 1234, avg_time: 45, error_rate: 0.2 },
      { endpoint: '/api/files', requests: 892, avg_time: 78, error_rate: 1.1 },
      { endpoint: '/api/execution/start', requests: 567, avg_time: 234, error_rate: 2.3 },
      { endpoint: '/api/llm-configs', requests: 345, avg_time: 56, error_rate: 0.5 },
      { endpoint: '/api/templates', requests: 234, avg_time: 89, error_rate: 0.8 }
    ]

    activeAlerts.value = [
      {
        id: 1,
        severity: 'warning',
        message: 'CPU使用率高',
        details: 'CPU使用率持续超过80%',
        timestamp: new Date(Date.now() - 300000)
      },
      {
        id: 2,
        severity: 'info',
        message: '新版本可用',
        details: 'ResoftAI v0.3.1已发布',
        timestamp: new Date(Date.now() - 600000)
      }
    ]

    updateCharts()
  } catch (error) {
    ElMessage.error('加载性能数据失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// Refresh data
const refreshData = () => {
  fetchMetrics()
}

// Export metrics
const exportMetrics = () => {
  // TODO: Implement export functionality
  ElMessage.success('导出功能开发中...')
}

// Initialize charts
const initCharts = () => {
  if (requestChart.value) {
    requestChartInstance = echarts.init(requestChart.value)
  }
  if (responseTimeChart.value) {
    responseTimeChartInstance = echarts.init(responseTimeChart.value)
  }
  updateCharts()
}

// Update charts with data
const updateCharts = () => {
  // Request trend chart
  if (requestChartInstance) {
    const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
    const requestData = Array.from({ length: 24 }, () => Math.floor(Math.random() * 500))

    requestChartInstance.setOption({
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: hours,
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: '请求数'
      },
      series: [
        {
          name: '请求数',
          type: 'line',
          data: requestData,
          smooth: true,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
            ])
          },
          lineStyle: {
            color: '#409EFF'
          }
        }
      ]
    })
  }

  // Response time distribution chart
  if (responseTimeChartInstance) {
    const responseTimeData = [
      { value: 40, name: '0-50ms' },
      { value: 30, name: '50-100ms' },
      { value: 20, name: '100-200ms' },
      { value: 8, name: '200-500ms' },
      { value: 2, name: '>500ms' }
    ]

    responseTimeChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c}% ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '响应时间分布',
          type: 'pie',
          radius: '50%',
          data: responseTimeData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    })
  }
}

// Helper functions
const getChangeClass = (change) => {
  return change > 0 ? 'stat-increase' : 'stat-decrease'
}

const getProgressColor = (value) => {
  if (value < 60) return '#67C23A'
  if (value < 80) return '#E6A23C'
  return '#F56C6C'
}

const getResponseTimeType = (time) => {
  if (time < 100) return 'success'
  if (time < 300) return 'warning'
  return 'danger'
}

const getAlertType = (severity) => {
  const typeMap = {
    critical: 'error',
    warning: 'warning',
    info: 'info'
  }
  return typeMap[severity] || 'info'
}

const formatBytes = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / 1048576).toFixed(2) + ' MB'
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

// Lifecycle hooks
onMounted(() => {
  fetchMetrics()
  initCharts()

  // Auto-refresh every 30 seconds
  updateInterval = setInterval(() => {
    fetchMetrics()
  }, 30000)

  // Handle window resize
  window.addEventListener('resize', () => {
    requestChartInstance?.resize()
    responseTimeChartInstance?.resize()
  })
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  requestChartInstance?.dispose()
  responseTimeChartInstance?.dispose()
})

watch(timeRange, () => {
  fetchMetrics()
})
</script>

<style scoped lang="scss">
.performance-monitor {
  padding: 20px;

  .el-page-header {
    margin-bottom: 20px;
  }

  .stats-cards {
    margin-bottom: 20px;

    .stat-card {
      .stat-footer {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #f0f0f0;

        .stat-label {
          color: #606266;
          font-size: 14px;
        }

        .stat-increase {
          color: #F56C6C;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .stat-decrease {
          color: #67C23A;
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
  }

  .charts-row {
    margin-bottom: 20px;

    .chart-container {
      height: 300px;
    }

    .resource-metrics {
      .metric-item {
        margin-bottom: 20px;

        &:last-child {
          margin-bottom: 0;
        }

        .metric-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;

          .metric-value {
            font-weight: bold;
            color: #409EFF;
          }
        }
      }
    }
  }

  .alerts-card {
    .alert-badge {
      float: right;
    }

    .el-timeline {
      padding-left: 0;
    }
  }
}
</style>
