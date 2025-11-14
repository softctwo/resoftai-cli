<template>
  <div class="realtime-log">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>实时日志</span>
          <div class="header-actions">
            <el-switch
              v-model="autoScroll"
              active-text="自动滚动"
              inactive-text=""
              size="small"
            />
            <el-button
              size="small"
              @click="clearLogs"
              :icon="Delete"
              :disabled="logs.length === 0"
            >
              清空
            </el-button>
            <el-button
              size="small"
              @click="downloadLogs"
              :icon="Download"
              :disabled="logs.length === 0"
            >
              下载
            </el-button>
          </div>
        </div>
      </template>

      <div class="log-filters">
        <el-radio-group v-model="filterLevel" size="small">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="info">信息</el-radio-button>
          <el-radio-button label="warning">警告</el-radio-button>
          <el-radio-button label="error">错误</el-radio-button>
          <el-radio-button label="debug">调试</el-radio-button>
        </el-radio-group>

        <el-input
          v-model="searchQuery"
          placeholder="搜索日志..."
          :prefix-icon="Search"
          size="small"
          clearable
          style="width: 300px; margin-left: auto"
        />
      </div>

      <div class="log-container" ref="logContainer">
        <div v-if="filteredLogs.length === 0" class="empty-logs">
          <el-empty description="暂无日志">
            <el-button type="primary" size="small" @click="$emit('start-project')">
              开始项目执行
            </el-button>
          </el-empty>
        </div>

        <div v-else class="log-list">
          <div
            v-for="(log, index) in filteredLogs"
            :key="index"
            :class="['log-entry', `log-${log.level}`]"
          >
            <div class="log-header">
              <el-tag :type="getLogType(log.level)" size="small">
                {{ log.level.toUpperCase() }}
              </el-tag>
              <span class="log-time">{{ formatTime(log.timestamp) }}</span>
              <span v-if="log.source" class="log-source">{{ log.source }}</span>
            </div>
            <div class="log-message">{{ log.message }}</div>
            <div v-if="log.details" class="log-details">
              <el-collapse>
                <el-collapse-item title="详细信息">
                  <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="log-loading">
          <el-icon class="is-loading"><Loading /></el-icon>
          正在加载日志...
        </div>
      </div>

      <div class="log-footer">
        <el-text type="info" size="small">
          共 {{ logs.length }} 条日志，显示 {{ filteredLogs.length }} 条
        </el-text>
        <el-tag v-if="isConnected" type="success" size="small" effect="dark">
          <el-icon><Connection /></el-icon>
          已连接
        </el-tag>
        <el-tag v-else type="info" size="small" effect="dark">
          <el-icon><CloseBold /></el-icon>
          未连接
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import {
  Delete,
  Download,
  Search,
  Loading,
  Connection,
  CloseBold
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const props = defineProps({
  projectId: {
    type: [Number, String],
    required: true
  },
  isConnected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['start-project'])

// State
const logs = ref([])
const filterLevel = ref('all')
const searchQuery = ref('')
const autoScroll = ref(true)
const isLoading = ref(false)
const logContainer = ref(null)

// Add sample logs for demonstration
onMounted(() => {
  // Add welcome log
  addLog({
    level: 'info',
    message: '日志系统已就绪，等待项目执行...',
    source: 'System',
    timestamp: new Date()
  })
})

// Filtered logs
const filteredLogs = computed(() => {
  let result = logs.value

  // Filter by level
  if (filterLevel.value !== 'all') {
    result = result.filter(log => log.level === filterLevel.value)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(log =>
      log.message.toLowerCase().includes(query) ||
      log.source?.toLowerCase().includes(query)
    )
  }

  return result
})

// Watch for new logs and auto-scroll
watch(() => logs.value.length, async () => {
  if (autoScroll.value) {
    await nextTick()
    scrollToBottom()
  }
})

// Methods
function addLog(log) {
  logs.value.push({
    ...log,
    timestamp: log.timestamp || new Date()
  })

  // Limit log size to prevent memory issues
  if (logs.value.length > 1000) {
    logs.value = logs.value.slice(-1000)
  }
}

function clearLogs() {
  logs.value = []
  ElMessage.success('日志已清空')
}

function downloadLogs() {
  const logText = logs.value.map(log => {
    return `[${formatTime(log.timestamp)}] [${log.level.toUpperCase()}] ${log.source ? `[${log.source}] ` : ''}${log.message}`
  }).join('\n')

  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `project-${props.projectId}-logs-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('日志已下载')
}

function scrollToBottom() {
  if (logContainer.value) {
    const container = logContainer.value
    container.scrollTop = container.scrollHeight
  }
}

function formatTime(timestamp) {
  return dayjs(timestamp).format('HH:mm:ss.SSS')
}

function getLogType(level) {
  const types = {
    error: 'danger',
    warning: 'warning',
    info: 'info',
    debug: '',
    success: 'success'
  }
  return types[level] || ''
}

// Expose method to add logs from parent
defineExpose({
  addLog,
  clearLogs
})
</script>

<style scoped>
.realtime-log {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.log-filters {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.log-container {
  height: 500px;
  overflow-y: auto;
  background: #1e1e1e;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.empty-logs {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.log-entry {
  padding: 8px 12px;
  border-left: 3px solid #409eff;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 4px;
}

.log-entry.log-error {
  border-left-color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.log-entry.log-warning {
  border-left-color: #e6a23c;
  background: rgba(230, 162, 60, 0.1);
}

.log-entry.log-success {
  border-left-color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.log-entry.log-debug {
  border-left-color: #909399;
  background: rgba(144, 147, 153, 0.1);
}

.log-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.log-time {
  color: #909399;
  font-size: 12px;
}

.log-source {
  color: #67c23a;
  font-size: 12px;
  font-weight: 600;
}

.log-message {
  color: #e0e0e0;
  word-wrap: break-word;
}

.log-details {
  margin-top: 8px;
}

.log-details pre {
  color: #909399;
  font-size: 12px;
  margin: 0;
  white-space: pre-wrap;
}

.log-loading {
  text-align: center;
  padding: 16px;
  color: #909399;
}

.log-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #dcdfe6;
}
</style>
