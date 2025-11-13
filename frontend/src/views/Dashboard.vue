<template>
  <div class="dashboard">
    <h1>仪表板</h1>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="项目总数" :value="stats.totalProjects">
            <template #prefix>
              <el-icon color="#409eff"><Folder /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="进行中" :value="stats.activeProjects">
            <template #prefix>
              <el-icon color="#67c23a"><Loading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="已完成" :value="stats.completedProjects">
            <template #prefix>
              <el-icon color="#409eff"><CircleCheck /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="Token使用" :value="formatNumber(stats.totalTokens)">
            <template #prefix>
              <el-icon color="#e6a23c"><CreditCard /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近项目 -->
    <el-card shadow="never" class="recent-projects">
      <template #header>
        <div class="card-header">
          <span>最近项目</span>
          <el-button type="primary" link @click="$router.push('/projects')">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="recentProjects" v-loading="loading" stripe>
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewProject(row.id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && recentProjects.length === 0" description="还没有项目" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Folder,
  Loading,
  CircleCheck,
  CreditCard,
  ArrowRight
} from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const loading = ref(false)
const stats = ref({
  totalProjects: 0,
  activeProjects: 0,
  completedProjects: 0,
  totalTokens: 0
})
const recentProjects = ref([])

onMounted(async () => {
  await loadDashboardData()
})

async function loadDashboardData() {
  loading.value = true

  try {
    // Load recent projects
    const response = await axios.get(`${API_BASE}/projects`, {
      params: { limit: 5 },
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    recentProjects.value = response.data.projects

    // Calculate stats
    stats.value.totalProjects = response.data.total
    stats.value.activeProjects = recentProjects.value.filter(
      p => p.status === 'developing' || p.status === 'planning'
    ).length
    stats.value.completedProjects = recentProjects.value.filter(
      p => p.status === 'completed'
    ).length
    // TODO: Add real token tracking
    stats.value.totalTokens = 0

  } catch (error) {
    console.error('Load dashboard error:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

function getStatusType(status) {
  const statusMap = {
    pending: 'info',
    planning: 'warning',
    developing: 'primary',
    testing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return statusMap[status] || 'info'
}

function getStatusLabel(status) {
  const labelMap = {
    pending: '待开始',
    planning: '规划中',
    developing: '开发中',
    testing: '测试中',
    completed: '已完成',
    failed: '失败'
  }
  return labelMap[status] || status
}

function viewProject(id) {
  router.push(`/projects/${id}`)
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: default;
}

.recent-projects {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
