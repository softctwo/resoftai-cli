<template>
  <div class="agents-page">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>智能体监控</h2>
      </template>
    </el-page-header>

    <el-card class="filter-card" shadow="never">
      <el-form :inline="true">
        <el-form-item label="项目">
          <el-select
            v-model="selectedProject"
            placeholder="选择项目"
            clearable
            @change="loadAgents"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="selectedStatus"
            placeholder="全部状态"
            clearable
            @change="loadAgents"
          >
            <el-option label="空闲" value="idle" />
            <el-option label="工作中" value="working" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" class="agents-grid">
      <el-col
        v-for="agent in filteredAgents"
        :key="agent.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
      >
        <el-card class="agent-card" :class="`status-${agent.status}`">
          <template #header>
            <div class="card-header">
              <span class="agent-role">{{ getAgentRoleName(agent.agent_role) }}</span>
              <el-tag
                :type="getStatusType(agent.status)"
                size="small"
              >
                {{ getStatusLabel(agent.status) }}
              </el-tag>
            </div>
          </template>

          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="项目">
              {{ getProjectName(agent.project_id) }}
            </el-descriptions-item>
            <el-descriptions-item label="当前任务">
              <div class="task-text">
                {{ agent.current_task || '无任务' }}
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="Token使用">
              {{ agent.tokens_used || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ formatDate(agent.started_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="完成时间" v-if="agent.completed_at">
              {{ formatDate(agent.completed_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="agent-actions" v-if="agent.status === 'working'">
            <el-progress
              :percentage="agent.progress || 0"
              :status="agent.progress === 100 ? 'success' : undefined"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty
      v-if="filteredAgents.length === 0"
      description="暂无智能体活动"
    />

    <el-card class="stats-card" shadow="never">
      <template #header>
        <span>统计信息</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="总智能体" :value="agentStats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="工作中" :value="agentStats.working" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="已完成" :value="agentStats.completed" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="总Token" :value="agentStats.totalTokens" />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const agents = ref([])
const projects = ref([])
const selectedProject = ref(null)
const selectedStatus = ref(null)
const loading = ref(false)

// Agent role mappings
const agentRoles = {
  project_manager: '项目经理',
  requirement_analyst: '需求分析师',
  architect: '架构师',
  ui_designer: 'UI设计师',
  developer: '开发工程师',
  test_engineer: '测试工程师',
  qa_engineer: '质量工程师'
}

onMounted(async () => {
  await loadProjects()
  await loadAgents()
  // TODO: Connect to WebSocket for real-time updates
})

async function loadProjects() {
  try {
    const response = await axios.get(`${API_BASE}/projects`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    projects.value = response.data.projects || []
  } catch (error) {
    console.error('Load projects error:', error)
    ElMessage.error('加载项目列表失败')
  }
}

async function loadAgents() {
  loading.value = true
  try {
    // TODO: Implement API endpoint for fetching agent activities
    // For now, using mock data
    agents.value = [
      {
        id: 1,
        project_id: 1,
        agent_role: 'project_manager',
        status: 'working',
        current_task: '分析项目需求',
        tokens_used: 1250,
        progress: 45,
        started_at: new Date().toISOString()
      },
      {
        id: 2,
        project_id: 1,
        agent_role: 'requirement_analyst',
        status: 'idle',
        current_task: null,
        tokens_used: 0,
        started_at: new Date().toISOString()
      }
    ]
  } catch (error) {
    console.error('Load agents error:', error)
    ElMessage.error('加载智能体活动失败')
  } finally {
    loading.value = false
  }
}

const filteredAgents = computed(() => {
  let result = agents.value

  if (selectedProject.value) {
    result = result.filter(a => a.project_id === selectedProject.value)
  }

  if (selectedStatus.value) {
    result = result.filter(a => a.status === selectedStatus.value)
  }

  return result
})

const agentStats = computed(() => {
  return {
    total: agents.value.length,
    working: agents.value.filter(a => a.status === 'working').length,
    completed: agents.value.filter(a => a.status === 'completed').length,
    totalTokens: agents.value.reduce((sum, a) => sum + (a.tokens_used || 0), 0)
  }
})

function getAgentRoleName(role) {
  return agentRoles[role] || role
}

function getProjectName(projectId) {
  const project = projects.value.find(p => p.id === projectId)
  return project ? project.name : `项目 #${projectId}`
}

function getStatusType(status) {
  const typeMap = {
    idle: 'info',
    working: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

function getStatusLabel(status) {
  const labelMap = {
    idle: '空闲',
    working: '工作中',
    completed: '已完成',
    failed: '失败'
  }
  return labelMap[status] || status
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.agents-page {
  padding: 20px;
}

.filter-card {
  margin: 20px 0;
}

.agents-grid {
  margin: 20px 0;
}

.agent-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.agent-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.agent-card.status-working {
  border-left: 4px solid #409eff;
}

.agent-card.status-completed {
  border-left: 4px solid #67c23a;
}

.agent-card.status-failed {
  border-left: 4px solid #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-role {
  font-weight: bold;
  font-size: 16px;
}

.task-text {
  white-space: pre-wrap;
  font-size: 12px;
  color: #606266;
}

.agent-actions {
  margin-top: 15px;
}

.stats-card {
  margin-top: 20px;
}
</style>
