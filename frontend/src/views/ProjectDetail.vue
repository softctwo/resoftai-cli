<template>
  <div class="project-detail">
    <el-page-header @back="$router.push('/projects')" :title="'返回'" />

    <el-card v-loading="loading" shadow="never" class="project-card">
      <template #header>
        <div class="card-header">
          <div>
            <h2>{{ project.name }}</h2>
            <el-tag :type="getStatusType(project.status)">
              {{ getStatusLabel(project.status) }}
            </el-tag>
          </div>
          <el-progress
            :percentage="project.progress"
            :width="80"
            type="circle"
          />
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="创建时间">
          {{ formatDate(project.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="AI模型">
          {{ project.llm_provider || '未指定' }}
        </el-descriptions-item>
        <el-descriptions-item label="当前阶段" :span="2">
          {{ project.current_stage || '未开始' }}
        </el-descriptions-item>
        <el-descriptions-item label="需求描述" :span="2">
          <div style="white-space: pre-wrap">{{ project.requirements }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="info-card">
      <template #header>
        <span>项目进度</span>
      </template>
      <el-alert
        title="项目详情页面开发中"
        type="info"
        :closable="false"
      >
        完整功能包括: 任务列表、智能体活动、生成的文档、代码查看、实时日志等
      </el-alert>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/composables/useWebSocket'

const route = useRoute()
const authStore = useAuthStore()
const { connect, joinProject, leaveProject, onProjectProgress, onAgentStatus, onTaskUpdate, cleanup } = useWebSocket()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const loading = ref(false)
const project = ref({
  name: '',
  status: '',
  progress: 0,
  requirements: '',
  created_at: '',
  llm_provider: '',
  current_stage: ''
})

onMounted(async () => {
  await loadProject()

  // Connect to WebSocket and join project room
  connect()
  joinProject(route.params.id)

  // Listen for real-time project updates
  onProjectProgress((data) => {
    if (data.project_id === parseInt(route.params.id)) {
      project.value.progress = data.percentage
      project.value.current_stage = data.stage
      ElMessage({
        message: data.message,
        type: 'info',
        duration: 2000
      })
    }
  })

  onAgentStatus((data) => {
    if (data.project_id === parseInt(route.params.id)) {
      console.log('Agent status update:', data)
    }
  })

  onTaskUpdate((data) => {
    if (data.project_id === parseInt(route.params.id)) {
      console.log('Task update:', data)
    }
  })
})

onUnmounted(() => {
  leaveProject(route.params.id)
  cleanup()
})

async function loadProject() {
  loading.value = true

  try {
    const response = await axios.get(
      `${API_BASE}/projects/${route.params.id}`,
      {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      }
    )

    project.value = response.data

  } catch (error) {
    console.error('Load project error:', error)
    ElMessage.error('加载项目详情失败')
  } finally {
    loading.value = false
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
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
</script>

<style scoped>
.project-detail {
  padding: 20px;
}

.project-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0 10px 0 0;
  display: inline-block;
}

.info-card {
  margin-top: 20px;
}
</style>
