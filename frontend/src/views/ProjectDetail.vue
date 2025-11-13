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
          <div class="header-actions">
            <el-button
              v-if="project.status !== 'completed'"
              type="primary"
              @click="startProject"
              :loading="starting"
              :disabled="project.status === 'developing'"
            >
              {{ project.status === 'developing' ? '执行中...' : '开始执行' }}
            </el-button>
            <el-progress
              :percentage="project.progress"
              :width="80"
              type="circle"
            />
          </div>
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
          <el-tag v-if="project.current_stage" type="primary">
            {{ project.current_stage }}
          </el-tag>
          <span v-else>未开始</span>
        </el-descriptions-item>
        <el-descriptions-item label="需求描述" :span="2">
          <div style="white-space: pre-wrap">{{ project.requirements }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Tabs for different sections -->
    <el-card shadow="never" class="content-card">
      <el-tabs v-model="activeTab" type="border-card">
        <!-- Real-time Log Tab -->
        <el-tab-pane label="实时日志" name="logs">
          <template #label>
            <span>
              <el-icon><Document /></el-icon>
              实时日志
              <el-badge v-if="newLogsCount > 0" :value="newLogsCount" />
            </span>
          </template>
          <RealtimeLog
            ref="logComponent"
            :project-id="route.params.id"
            :is-connected="wsConnected"
            @start-project="startProject"
          />
        </el-tab-pane>

        <!-- Code Quality Tab -->
        <el-tab-pane label="代码质量" name="quality">
          <template #label>
            <span>
              <el-icon><Check /></el-icon>
              代码质量
            </span>
          </template>
          <CodeQualityReport
            :report="qualityReport"
            :loading="qualityLoading"
            @check-quality="checkCodeQuality"
          />
        </el-tab-pane>

        <!-- Agent Activities Tab -->
        <el-tab-pane label="智能体活动" name="agents">
          <template #label>
            <span>
              <el-icon><User /></el-icon>
              智能体活动
            </span>
          </template>
          <div class="agent-activities">
            <el-timeline v-if="agentActivities.length > 0">
              <el-timeline-item
                v-for="activity in agentActivities"
                :key="activity.id"
                :timestamp="formatDate(activity.timestamp)"
                :type="getActivityType(activity.status)"
              >
                <el-card>
                  <h4>{{ activity.agent_role }}</h4>
                  <p>{{ activity.current_task || '待命中' }}</p>
                  <el-tag :type="getActivityType(activity.status)" size="small">
                    {{ activity.status }}
                  </el-tag>
                  <span v-if="activity.tokens_used" style="margin-left: 10px">
                    Token使用: {{ activity.tokens_used }}
                  </span>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无智能体活动记录" />
          </div>
        </el-tab-pane>

        <!-- Files Tab -->
        <el-tab-pane label="项目文件" name="files">
          <template #label>
            <span>
              <el-icon><Folder /></el-icon>
              项目文件
            </span>
          </template>
          <div class="project-files">
            <el-alert
              title="文件管理功能"
              type="info"
              :closable="false"
              show-icon
            >
              查看和编辑项目生成的文件，包括代码、文档、配置等
            </el-alert>
            <el-button type="primary" style="margin-top: 16px" @click="$router.push('/files')">
              前往文件管理
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Check, User, Folder } from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useWebSocket } from '@/composables/useWebSocket'
import CodeQualityReport from '@/components/CodeQualityReport.vue'
import RealtimeLog from '@/components/RealtimeLog.vue'

const route = useRoute()
const authStore = useAuthStore()
const {
  connected: wsConnected,
  connect,
  joinProject,
  leaveProject,
  onProjectProgress,
  onAgentStatus,
  onTaskUpdate,
  onLogNew,
  cleanup
} = useWebSocket()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Refs
const loading = ref(false)
const starting = ref(false)
const activeTab = ref('logs')
const logComponent = ref(null)
const newLogsCount = ref(0)
const qualityReport = ref(null)
const qualityLoading = ref(false)
const agentActivities = ref([])

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

      // Add log entry
      logComponent.value?.addLog({
        level: 'info',
        message: data.message,
        source: 'Project Progress',
        timestamp: new Date()
      })

      // Show notification
      ElMessage({
        message: `进度更新: ${data.percentage}% - ${data.message}`,
        type: 'info',
        duration: 3000
      })
    }
  })

  onAgentStatus((data) => {
    if (data.project_id === parseInt(route.params.id)) {
      console.log('Agent status update:', data)

      // Add to agent activities
      agentActivities.value.unshift({
        id: Date.now(),
        agent_role: data.agent_role,
        status: data.status,
        current_task: data.current_task,
        tokens_used: data.tokens_used,
        timestamp: new Date()
      })

      // Limit to last 20 activities
      if (agentActivities.value.length > 20) {
        agentActivities.value = agentActivities.value.slice(0, 20)
      }

      // Add log entry
      logComponent.value?.addLog({
        level: 'info',
        message: `智能体 ${data.agent_role} 状态: ${data.status}${data.current_task ? ` - ${data.current_task}` : ''}`,
        source: data.agent_role,
        timestamp: new Date()
      })
    }
  })

  onTaskUpdate((data) => {
    if (data.project_id === parseInt(route.params.id)) {
      console.log('Task update:', data)

      // Add log entry
      logComponent.value?.addLog({
        level: 'info',
        message: `任务更新: ${data.task_name || 'Unknown'} - ${data.status}`,
        source: 'Task Manager',
        timestamp: new Date(),
        details: data
      })
    }
  })

  onLogNew((data) => {
    if (data.project_id === parseInt(route.params.id)) {
      // Add log entry
      logComponent.value?.addLog({
        level: data.level || 'info',
        message: data.message,
        source: data.source,
        timestamp: new Date()
      })

      // Increment badge count if not on logs tab
      if (activeTab.value !== 'logs') {
        newLogsCount.value++
      }
    }
  })
})

onUnmounted(() => {
  leaveProject(route.params.id)
  cleanup()
})

// Reset log badge when switching to logs tab
const handleTabChange = () => {
  if (activeTab.value === 'logs') {
    newLogsCount.value = 0
  }
}

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

async function startProject() {
  starting.value = true

  try {
    await axios.post(
      `${API_BASE}/execution/${route.params.id}/start`,
      {},
      {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      }
    )

    ElMessage.success('项目执行已启动')
    project.value.status = 'developing'

    // Add initial log
    logComponent.value?.addLog({
      level: 'success',
      message: '项目执行已启动，智能体开始工作...',
      source: 'System',
      timestamp: new Date()
    })

    // Reload project
    await loadProject()

  } catch (error) {
    console.error('Start project error:', error)
    ElMessage.error('启动项目失败: ' + (error.response?.data?.detail || error.message))

    // Add error log
    logComponent.value?.addLog({
      level: 'error',
      message: '项目启动失败: ' + (error.response?.data?.detail || error.message),
      source: 'System',
      timestamp: new Date()
    })
  } finally {
    starting.value = false
  }
}

async function checkCodeQuality() {
  qualityLoading.value = true

  try {
    // TODO: Implement actual API call to check code quality
    // For now, simulate with mock data
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Mock quality report
    qualityReport.value = {
      filename: 'example.py',
      language: 'python',
      quality_score: 87,
      total_lines: 150,
      issues_count: 5,
      critical_issues: 0,
      error_issues: 1,
      warning_issues: 4,
      metrics: {
        code_lines: 120,
        comment_lines: 20,
        comment_ratio: 0.167,
        issue_density: 0.033
      },
      issues: [
        {
          level: 'error',
          line: 45,
          message: '变量未使用',
          suggestion: '删除未使用的变量或使用它',
          rule_id: 'unused-variable'
        },
        {
          level: 'warning',
          line: 78,
          message: '行长度超过120个字符',
          suggestion: '将长行拆分为多行',
          rule_id: 'line-too-long'
        },
        {
          level: 'warning',
          line: 92,
          message: '函数复杂度过高',
          suggestion: '考虑将函数拆分为更小的函数',
          rule_id: 'complex-function'
        },
        {
          level: 'warning',
          line: 105,
          message: '缺少类型注解',
          suggestion: '添加类型注解以提高代码可读性',
          rule_id: 'missing-type-hint'
        },
        {
          level: 'warning',
          line: 130,
          message: '魔法数字',
          suggestion: '使用命名常量代替魔法数字',
          rule_id: 'magic-number'
        }
      ]
    }

    ElMessage.success('代码质量检查完成')

    // Add log
    logComponent.value?.addLog({
      level: 'success',
      message: `代码质量检查完成 - 得分: ${qualityReport.value.quality_score}/100`,
      source: 'Quality Checker',
      timestamp: new Date()
    })

  } catch (error) {
    console.error('Quality check error:', error)
    ElMessage.error('代码质量检查失败')

    // Add error log
    logComponent.value?.addLog({
      level: 'error',
      message: '代码质量检查失败',
      source: 'Quality Checker',
      timestamp: new Date()
    })
  } finally {
    qualityLoading.value = false
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

function getActivityType(status) {
  const typeMap = {
    idle: 'info',
    working: 'primary',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.content-card {
  margin-top: 20px;
}

.agent-activities {
  padding: 20px;
}

.project-files {
  padding: 20px;
}

:deep(.el-tabs__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
