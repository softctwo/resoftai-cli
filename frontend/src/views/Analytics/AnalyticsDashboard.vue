<template>
  <div class="analytics-dashboard">
    <PageHeader title="Analytics Dashboard" subtitle="Track platform metrics and trends">
      <template #actions>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="To"
          start-placeholder="Start date"
          end-placeholder="End date"
          @change="loadData"
        />
        <el-button icon="Download" @click="exportReport">
          Export Report
        </el-button>
      </template>
    </PageHeader>

    <!-- Overview Stats -->
    <el-row :gutter="20" class="overview-row">
      <el-col :span="6">
        <StatCard
          title="Total Downloads"
          :value="stats.total_downloads"
          :trend="stats.downloads_trend"
          icon="Download"
          color="#409eff"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          title="Total Installs"
          :value="stats.total_installs"
          :trend="stats.installs_trend"
          icon="Upload"
          color="#67c23a"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          title="Active Contributors"
          :value="stats.active_contributors"
          :trend="stats.contributors_trend"
          icon="User"
          color="#e6a23c"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          title="Avg Rating"
          :value="stats.average_rating"
          :trend="stats.rating_trend"
          icon="Star"
          color="#f56c6c"
          :decimals="1"
        />
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="20" class="charts-row">
      <!-- Downloads Trend -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Downloads Over Time</span>
              <el-radio-group v-model="downloadChartPeriod" size="small" @change="updateDownloadChart">
                <el-radio-button label="7d">7 Days</el-radio-button>
                <el-radio-button label="30d">30 Days</el-radio-button>
                <el-radio-button label="90d">90 Days</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <LineChart
            :data="downloadChartData"
            :height="300"
          />
        </el-card>
      </el-col>

      <!-- Category Distribution -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>Category Distribution</span>
          </template>
          <PieChart
            :data="categoryChartData"
            :height="300"
          />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <!-- Top Plugins -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Top Plugins</span>
              <el-select v-model="topPluginsMetric" size="small" @change="updateTopPlugins">
                <el-option label="Downloads" value="downloads" />
                <el-option label="Installs" value="installs" />
                <el-option label="Rating" value="rating" />
              </el-select>
            </div>
          </template>
          <BarChart
            :data="topPluginsData"
            :height="300"
          />
        </el-card>
      </el-col>

      <!-- Top Templates -->
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Top Templates</span>
              <el-select v-model="topTemplatesMetric" size="small" @change="updateTopTemplates">
                <el-option label="Downloads" value="downloads" />
                <el-option label="Installs" value="installs" />
                <el-option label="Rating" value="rating" />
              </el-select>
            </div>
          </template>
          <BarChart
            :data="topTemplatesData"
            :height="300"
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- Top Contributors -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="contributors-card">
          <template #header>
            <div class="card-header">
              <span>Top Contributors</span>
              <el-button size="small" @click="viewFullLeaderboard">
                View Full Leaderboard
              </el-button>
            </div>
          </template>
          <el-table
            :data="topContributors"
            style="width: 100%"
            stripe
          >
            <el-table-column type="index" label="Rank" width="70" />
            <el-table-column prop="display_name" label="Contributor" min-width="200">
              <template #default="{ row }">
                <div class="contributor-cell">
                  <el-avatar :size="32" :src="row.avatar_url">
                    {{ row.display_name[0] }}
                  </el-avatar>
                  <span class="name">{{ row.display_name }}</span>
                  <el-tag v-if="row.is_verified" type="success" size="small">
                    Verified
                  </el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="plugins_count" label="Plugins" width="100" align="center" />
            <el-table-column prop="templates_count" label="Templates" width="100" align="center" />
            <el-table-column prop="total_downloads" label="Downloads" width="120" align="center">
              <template #default="{ row }">
                {{ formatNumber(row.total_downloads) }}
              </template>
            </el-table-column>
            <el-table-column prop="average_rating" label="Avg Rating" width="120" align="center">
              <template #default="{ row }">
                <el-rate
                  :model-value="row.average_rating"
                  disabled
                  show-score
                  text-color="#ff9900"
                />
              </template>
            </el-table-column>
            <el-table-column label="Badges" width="150">
              <template #default="{ row }">
                <div class="badges">
                  <el-tag
                    v-for="badge in row.badges.slice(0, 3)"
                    :key="badge"
                    size="small"
                    type="info"
                  >
                    {{ badge }}
                  </el-tag>
                  <span v-if="row.badges.length > 3" class="more-badges">
                    +{{ row.badges.length - 3 }}
                  </span>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Activity -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="activity-card">
          <template #header>
            <span>Recent Activity</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="activity in recentActivity"
              :key="activity.id"
              :timestamp="formatDate(activity.created_at)"
              :type="activity.type"
            >
              <div class="activity-item">
                <span class="activity-text" v-html="activity.text"></span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { analyticsApi } from '@/api/analytics'
import PageHeader from '@/components/PageHeader.vue'
import StatCard from '@/components/StatCard.vue'
import LineChart from '@/components/Charts/LineChart.vue'
import PieChart from '@/components/Charts/PieChart.vue'
import BarChart from '@/components/Charts/BarChart.vue'
import { formatNumber, formatDate } from '@/utils/format'

interface Stats {
  total_downloads: number
  downloads_trend: number
  total_installs: number
  installs_trend: number
  active_contributors: number
  contributors_trend: number
  average_rating: number
  rating_trend: number
}

const dateRange = ref<[Date, Date]>([
  new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
  new Date()
])

const stats = ref<Stats>({
  total_downloads: 0,
  downloads_trend: 0,
  total_installs: 0,
  installs_trend: 0,
  active_contributors: 0,
  contributors_trend: 0,
  average_rating: 0,
  rating_trend: 0
})

const downloadChartPeriod = ref('30d')
const downloadChartData = ref<any>(null)

const categoryChartData = ref<any>(null)

const topPluginsMetric = ref('downloads')
const topPluginsData = ref<any>(null)

const topTemplatesMetric = ref('downloads')
const topTemplatesData = ref<any>(null)

const topContributors = ref<any[]>([])
const recentActivity = ref<any[]>([])

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    await Promise.all([
      loadStats(),
      updateDownloadChart(),
      loadCategoryDistribution(),
      updateTopPlugins(),
      updateTopTemplates(),
      loadTopContributors(),
      loadRecentActivity()
    ])
  } catch (error) {
    ElMessage.error('Failed to load analytics data')
    console.error('Analytics load error:', error)
  }
}

async function loadStats() {
  try {
    const response = await analyticsApi.getOverviewStats({
      start_date: dateRange.value[0].toISOString(),
      end_date: dateRange.value[1].toISOString()
    })
    stats.value = response.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

async function updateDownloadChart() {
  try {
    const response = await analyticsApi.getDownloadsTrend({
      period: downloadChartPeriod.value
    })
    downloadChartData.value = response.data
  } catch (error) {
    console.error('Error loading download chart:', error)
  }
}

async function loadCategoryDistribution() {
  try {
    const response = await analyticsApi.getCategoryDistribution()
    categoryChartData.value = response.data
  } catch (error) {
    console.error('Error loading category distribution:', error)
  }
}

async function updateTopPlugins() {
  try {
    const response = await analyticsApi.getTopPlugins({
      metric: topPluginsMetric.value,
      limit: 10
    })
    topPluginsData.value = response.data
  } catch (error) {
    console.error('Error loading top plugins:', error)
  }
}

async function updateTopTemplates() {
  try {
    const response = await analyticsApi.getTopTemplates({
      metric: topTemplatesMetric.value,
      limit: 10
    })
    topTemplatesData.value = response.data
  } catch (error) {
    console.error('Error loading top templates:', error)
  }
}

async function loadTopContributors() {
  try {
    const response = await analyticsApi.getTopContributors({
      limit: 10
    })
    topContributors.value = response.data
  } catch (error) {
    console.error('Error loading top contributors:', error)
  }
}

async function loadRecentActivity() {
  try {
    const response = await analyticsApi.getRecentActivity({
      limit: 20
    })
    recentActivity.value = response.data
  } catch (error) {
    console.error('Error loading recent activity:', error)
  }
}

function viewFullLeaderboard() {
  // Navigate to full leaderboard page
  console.log('View full leaderboard')
}

async function exportReport() {
  try {
    const response = await analyticsApi.exportReport({
      start_date: dateRange.value[0].toISOString(),
      end_date: dateRange.value[1].toISOString(),
      format: 'csv'
    })

    // Download file
    const blob = new Blob([response.data], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `analytics-report-${Date.now()}.csv`
    link.click()
    window.URL.revokeObjectURL(url)

    ElMessage.success('Report exported successfully')
  } catch (error) {
    ElMessage.error('Failed to export report')
    console.error('Export error:', error)
  }
}
</script>

<style scoped lang="scss">
.analytics-dashboard {
  .overview-row,
  .charts-row {
    margin-bottom: 20px;
  }

  .chart-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }

  .contributors-card {
    .contributor-cell {
      display: flex;
      align-items: center;
      gap: 12px;

      .name {
        font-weight: 500;
      }
    }

    .badges {
      display: flex;
      gap: 4px;
      align-items: center;

      .more-badges {
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }
  }

  .activity-card {
    .activity-item {
      .activity-text {
        font-size: 14px;
      }
    }
  }
}
</style>
