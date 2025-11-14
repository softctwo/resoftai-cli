<template>
  <div class="performance-monitoring">
    <div class="page-header">
      <h1>Performance Monitoring</h1>
      <div class="header-actions">
        <button @click="refreshData" class="btn btn-primary" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
        <button @click="exportMetrics" class="btn btn-secondary">
          <i class="fas fa-download"></i>
          Export
        </button>
      </div>
    </div>

    <!-- Overview Cards -->
    <div class="metrics-overview">
      <div class="metric-card">
        <div class="metric-icon" style="background-color: #4CAF50;">
          <i class="fas fa-project-diagram"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Active Workflows</div>
          <div class="metric-value">{{ overview.active_workflows }}</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #2196F3;">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Success Rate</div>
          <div class="metric-value">{{ (overview.success_rate * 100).toFixed(1) }}%</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #FF9800;">
          <i class="fas fa-clock"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Avg Completion Time</div>
          <div class="metric-value">{{ formatDuration(overview.avg_completion_time_seconds) }}</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #9C27B0;">
          <i class="fas fa-coins"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Tokens Used Today</div>
          <div class="metric-value">{{ formatNumber(overview.total_tokens_used_today) }}</div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon" style="background-color: #00BCD4;">
          <i class="fas fa-database"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Cache Hit Rate</div>
          <div class="metric-value">{{ (overview.cache_hit_rate * 100).toFixed(1) }}%</div>
        </div>
      </div>

      <div class="metric-card" :class="{ 'alert-card': overview.active_alerts > 0 }">
        <div class="metric-icon" style="background-color: #F44336;">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="metric-content">
          <div class="metric-label">Active Alerts</div>
          <div class="metric-value">{{ overview.active_alerts }}</div>
        </div>
      </div>
    </div>

    <!-- Performance Alerts -->
    <div v-if="alerts.length > 0" class="alerts-section">
      <h2>Performance Alerts</h2>
      <div class="alerts-list">
        <div v-for="alert in alerts" :key="alert.id"
             :class="['alert-item', `alert-${alert.severity}`]">
          <div class="alert-header">
            <span class="alert-title">{{ alert.title }}</span>
            <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
          </div>
          <div class="alert-description">{{ alert.description }}</div>
          <div class="alert-metric">
            {{ alert.metric_name }}: {{ alert.metric_value }} (threshold: {{ alert.threshold_value }})
          </div>
          <div class="alert-actions">
            <button @click="acknowledgeAlert(alert.id)"
                    v-if="alert.status === 'active'"
                    class="btn-sm">
              Acknowledge
            </button>
            <button @click="resolveAlert(alert.id)"
                    v-if="alert.status !== 'resolved'"
                    class="btn-sm btn-success">
              Resolve
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs for Different Views -->
    <div class="tabs-container">
      <div class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['tab', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id">
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <!-- Workflows Tab -->
      <div v-show="activeTab === 'workflows'" class="tab-content">
        <h2>Workflow Statistics</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <label>Total Workflows (7 days)</label>
            <span>{{ workflowStats.total }}</span>
          </div>
          <div class="stat-item">
            <label>Completed</label>
            <span class="success">{{ workflowStats.completed }}</span>
          </div>
          <div class="stat-item">
            <label>Failed</label>
            <span class="error">{{ workflowStats.failed }}</span>
          </div>
          <div class="stat-item">
            <label>Running</label>
            <span class="warning">{{ workflowStats.running }}</span>
          </div>
        </div>

        <div class="chart-container">
          <h3>Workflow Duration Trend</h3>
          <canvas ref="workflowChart"></canvas>
        </div>
      </div>

      <!-- Agents Tab -->
      <div v-show="activeTab === 'agents'" class="tab-content">
        <h2>Agent Performance</h2>
        <div class="agents-table">
          <table>
            <thead>
              <tr>
                <th>Agent Role</th>
                <th>Executions</th>
                <th>Success Rate</th>
                <th>Avg Time</th>
                <th>Tokens Used</th>
                <th>Cache Hit Rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="agent in agentMetrics" :key="agent.agent_role">
                <td><strong>{{ formatAgentRole(agent.agent_role) }}</strong></td>
                <td>{{ agent.total_executions }}</td>
                <td>
                  <span :class="getSuccessRateClass(agent.success_rate)">
                    {{ (agent.success_rate * 100).toFixed(1) }}%
                  </span>
                </td>
                <td>{{ agent.avg_execution_time.toFixed(2) }}s</td>
                <td>{{ formatNumber(agent.total_tokens) }}</td>
                <td>{{ (agent.cache_hit_rate * 100).toFixed(1) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- System Tab -->
      <div v-show="activeTab === 'system'" class="tab-content">
        <h2>System Metrics</h2>
        <div class="chart-container">
          <h3>Token Usage Over Time</h3>
          <canvas ref="tokenChart"></canvas>
        </div>
        <div class="chart-container">
          <h3>Cache Performance</h3>
          <canvas ref="cacheChart"></canvas>
        </div>
      </div>

      <!-- LLM Usage Tab -->
      <div v-show="activeTab === 'llm'" class="tab-content">
        <h2>LLM Usage & Costs</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <label>Total API Calls (30 days)</label>
            <span>{{ llmUsage.total_calls }}</span>
          </div>
          <div class="stat-item">
            <label>Total Tokens</label>
            <span>{{ formatNumber(llmUsage.total_tokens) }}</span>
          </div>
          <div class="stat-item">
            <label>Estimated Cost</label>
            <span>${{ llmUsage.total_cost.toFixed(2) }}</span>
          </div>
          <div class="stat-item">
            <label>Success Rate</label>
            <span :class="getSuccessRateClass(llmUsage.success_rate)">
              {{ (llmUsage.success_rate * 100).toFixed(1) }}%
            </span>
          </div>
        </div>

        <div class="usage-breakdown">
          <h3>Usage by Provider</h3>
          <div class="provider-list">
            <div v-for="(data, provider) in llmUsage.by_provider"
                 :key="provider"
                 class="provider-item">
              <div class="provider-header">
                <strong>{{ provider }}</strong>
              </div>
              <div class="provider-stats">
                <span>Calls: {{ data.calls }}</span>
                <span>Tokens: {{ formatNumber(data.tokens) }}</span>
                <span>Cost: ${{ data.cost.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/utils/api'

Chart.register(...registerables)

export default {
  name: 'PerformanceMonitoring',

  setup() {
    const loading = ref(false)
    const activeTab = ref('workflows')

    const overview = reactive({
      active_workflows: 0,
      total_workflows_today: 0,
      avg_completion_time_seconds: 0,
      success_rate: 0,
      total_tokens_used_today: 0,
      cache_hit_rate: 0,
      active_alerts: 0,
      llm_cost_today_usd: 0
    })

    const workflowStats = reactive({
      total: 0,
      completed: 0,
      failed: 0,
      running: 0,
      avg_duration: 0,
      total_tokens: 0,
      avg_cache_hit_rate: 0
    })

    const agentMetrics = ref([])
    const llmUsage = reactive({
      total_calls: 0,
      total_tokens: 0,
      total_cost: 0,
      by_provider: {},
      by_model: {},
      success_rate: 0
    })

    const alerts = ref([])
    const systemMetrics = ref([])

    const tabs = [
      { id: 'workflows', label: 'Workflows', icon: 'fas fa-project-diagram' },
      { id: 'agents', label: 'Agents', icon: 'fas fa-robot' },
      { id: 'system', label: 'System', icon: 'fas fa-server' },
      { id: 'llm', label: 'LLM Usage', icon: 'fas fa-brain' }
    ]

    const workflowChart = ref(null)
    const tokenChart = ref(null)
    const cacheChart = ref(null)

    let workflowChartInstance = null
    let tokenChartInstance = null
    let cacheChartInstance = null

    const fetchDashboardOverview = async () => {
      try {
        const response = await api.get('/monitoring/dashboard/overview')
        Object.assign(overview, response.data)
      } catch (error) {
        console.error('Failed to fetch dashboard overview:', error)
      }
    }

    const fetchWorkflowStats = async () => {
      try {
        const response = await api.get('/monitoring/workflows/stats?days=7')
        Object.assign(workflowStats, response.data)
      } catch (error) {
        console.error('Failed to fetch workflow stats:', error)
      }
    }

    const fetchAgentMetrics = async () => {
      try {
        const response = await api.get('/monitoring/agents/summary?days=7')
        agentMetrics.value = response.data
      } catch (error) {
        console.error('Failed to fetch agent metrics:', error)
      }
    }

    const fetchLLMUsage = async () => {
      try {
        const response = await api.get('/monitoring/llm/usage?days=30')
        Object.assign(llmUsage, response.data)
      } catch (error) {
        console.error('Failed to fetch LLM usage:', error)
      }
    }

    const fetchAlerts = async () => {
      try {
        const response = await api.get('/monitoring/alerts')
        alerts.value = response.data
      } catch (error) {
        console.error('Failed to fetch alerts:', error)
      }
    }

    const fetchSystemMetrics = async () => {
      try {
        const response = await api.get('/monitoring/system/metrics?hours=24')
        systemMetrics.value = response.data
      } catch (error) {
        console.error('Failed to fetch system metrics:', error)
      }
    }

    const refreshData = async () => {
      loading.value = true
      try {
        await Promise.all([
          fetchDashboardOverview(),
          fetchWorkflowStats(),
          fetchAgentMetrics(),
          fetchLLMUsage(),
          fetchAlerts(),
          fetchSystemMetrics()
        ])

        await nextTick()
        renderCharts()
      } finally {
        loading.value = false
      }
    }

    const renderCharts = () => {
      renderWorkflowChart()
      renderTokenChart()
      renderCacheChart()
    }

    const renderWorkflowChart = () => {
      if (!workflowChart.value) return

      if (workflowChartInstance) {
        workflowChartInstance.destroy()
      }

      const ctx = workflowChart.value.getContext('2d')
      workflowChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: systemMetrics.value.map(m =>
            new Date(m.timestamp).toLocaleTimeString()
          ),
          datasets: [{
            label: 'Avg Workflow Duration (s)',
            data: systemMetrics.value.map(m => m.avg_workflow_duration),
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true
            }
          }
        }
      })
    }

    const renderTokenChart = () => {
      if (!tokenChart.value) return

      if (tokenChartInstance) {
        tokenChartInstance.destroy()
      }

      const ctx = tokenChart.value.getContext('2d')
      tokenChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: systemMetrics.value.map(m =>
            new Date(m.timestamp).toLocaleTimeString()
          ),
          datasets: [{
            label: 'Tokens Used',
            data: systemMetrics.value.map(m => m.total_tokens_used),
            backgroundColor: '#9C27B0'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }

    const renderCacheChart = () => {
      if (!cacheChart.value) return

      if (cacheChartInstance) {
        cacheChartInstance.destroy()
      }

      const ctx = cacheChart.value.getContext('2d')
      cacheChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: systemMetrics.value.map(m =>
            new Date(m.timestamp).toLocaleTimeString()
          ),
          datasets: [{
            label: 'Cache Hit Rate (%)',
            data: systemMetrics.value.map(m => (m.cache_hit_rate || 0) * 100),
            borderColor: '#00BCD4',
            backgroundColor: 'rgba(0, 188, 212, 0.1)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      })
    }

    const acknowledgeAlert = async (alertId) => {
      try {
        await api.post(`/monitoring/alerts/${alertId}/acknowledge`)
        await fetchAlerts()
      } catch (error) {
        console.error('Failed to acknowledge alert:', error)
      }
    }

    const resolveAlert = async (alertId) => {
      try {
        await api.post(`/monitoring/alerts/${alertId}/resolve`)
        await fetchAlerts()
      } catch (error) {
        console.error('Failed to resolve alert:', error)
      }
    }

    const exportMetrics = async () => {
      try {
        const response = await api.get('/monitoring/export/metrics?format=json&days=30')
        const blob = new Blob([JSON.stringify(response.data, null, 2)],
                              { type: 'application/json' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `performance-metrics-${new Date().toISOString()}.json`
        a.click()
      } catch (error) {
        console.error('Failed to export metrics:', error)
      }
    }

    const formatDuration = (seconds) => {
      if (seconds < 60) return `${seconds.toFixed(1)}s`
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}m ${secs}s`
    }

    const formatNumber = (num) => {
      return new Intl.NumberFormat().format(num)
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleString()
    }

    const formatAgentRole = (role) => {
      return role.split('_').map(word =>
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    }

    const getSuccessRateClass = (rate) => {
      if (rate >= 0.9) return 'success'
      if (rate >= 0.7) return 'warning'
      return 'error'
    }

    onMounted(() => {
      refreshData()
      // Refresh data every 30 seconds
      setInterval(refreshData, 30000)
    })

    return {
      loading,
      activeTab,
      tabs,
      overview,
      workflowStats,
      agentMetrics,
      llmUsage,
      alerts,
      systemMetrics,
      workflowChart,
      tokenChart,
      cacheChart,
      refreshData,
      acknowledgeAlert,
      resolveAlert,
      exportMetrics,
      formatDuration,
      formatNumber,
      formatTime,
      formatAgentRole,
      getSuccessRateClass
    }
  }
}
</script>

<style scoped>
.performance-monitoring {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196F3;
  color: white;
}

.btn-primary:hover {
  background: #1976D2;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover {
  background: #616161;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.metric-card.alert-card {
  border: 2px solid #F44336;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.metric-content {
  flex: 1;
}

.metric-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.alerts-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.alert-item {
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid;
}

.alert-critical {
  background: #FFEBEE;
  border-left-color: #F44336;
}

.alert-warning {
  background: #FFF3E0;
  border-left-color: #FF9800;
}

.alert-info {
  background: #E3F2FD;
  border-left-color: #2196F3;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.alert-title {
  font-weight: bold;
}

.alert-time {
  color: #666;
  font-size: 12px;
}

.alert-description {
  margin-bottom: 8px;
}

.alert-metric {
  font-family: monospace;
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.alert-actions {
  display: flex;
  gap: 10px;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #f0f0f0;
}

.btn-sm:hover {
  background: #e0e0e0;
}

.btn-sm.btn-success {
  background: #4CAF50;
  color: white;
}

.btn-sm.btn-success:hover {
  background: #45a049;
}

.tabs-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background: #f5f5f5;
}

.tab {
  padding: 15px 25px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab:hover {
  background: #eeeeee;
}

.tab.active {
  color: #2196F3;
  border-bottom: 3px solid #2196F3;
  background: white;
}

.tab-content {
  padding: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-item label {
  font-size: 13px;
  color: #666;
}

.stat-item span {
  font-size: 24px;
  font-weight: bold;
}

.stat-item .success {
  color: #4CAF50;
}

.stat-item .error {
  color: #F44336;
}

.stat-item .warning {
  color: #FF9800;
}

.chart-container {
  margin: 30px 0;
  height: 300px;
}

.chart-container h3 {
  margin-bottom: 15px;
  font-size: 16px;
}

.chart-container canvas {
  max-height: 250px;
}

.agents-table {
  overflow-x: auto;
}

.agents-table table {
  width: 100%;
  border-collapse: collapse;
}

.agents-table th,
.agents-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.agents-table th {
  background: #f5f5f5;
  font-weight: 600;
  font-size: 13px;
  color: #666;
}

.agents-table tbody tr:hover {
  background: #f9f9f9;
}

.usage-breakdown {
  margin-top: 30px;
}

.provider-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.provider-item {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
}

.provider-header {
  margin-bottom: 10px;
}

.provider-stats {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 13px;
  color: #666;
}
</style>
