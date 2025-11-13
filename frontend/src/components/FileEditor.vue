<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="90%"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="editor-container">
      <div class="editor-toolbar">
        <el-select
          v-model="currentLanguage"
          placeholder="语言"
          size="small"
          style="width: 150px; margin-right: 10px"
        >
          <el-option label="JavaScript" value="javascript" />
          <el-option label="TypeScript" value="typescript" />
          <el-option label="Python" value="python" />
          <el-option label="Java" value="java" />
          <el-option label="Go" value="go" />
          <el-option label="HTML" value="html" />
          <el-option label="CSS" value="css" />
          <el-option label="JSON" value="json" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="SQL" value="sql" />
          <el-option label="Bash" value="shell" />
        </el-select>

        <el-select
          v-model="currentTheme"
          placeholder="主题"
          size="small"
          style="width: 150px"
        >
          <el-option label="暗色主题" value="vs-dark" />
          <el-option label="亮色主题" value="vs" />
          <el-option label="高对比度" value="hc-black" />
        </el-select>

        <el-button
          size="small"
          @click="checkQuality"
          :loading="checking"
          :icon="MagicStick"
        >
          质量检查
        </el-button>

        <div v-if="qualityScore !== null" class="quality-badge">
          <el-tag :type="getQualityType(qualityScore)" size="small">
            质量: {{ qualityScore }}/100
          </el-tag>
        </div>

        <div class="editor-info">
          <span>{{ currentFile?.path || '未选择文件' }}</span>
          <el-divider direction="vertical" />
          <el-tag v-if="isInSession" type="success" size="small">
            <el-icon><Connection /></el-icon>
            协作模式
          </el-tag>
        </div>
      </div>

      <!-- Active Users Panel -->
      <ActiveUsers
        v-if="activeUsers.length > 0"
        :users="activeUsers"
        :current-user-id="currentUserId"
        style="margin-bottom: 10px"
      />

      <!-- Quality Issues Alert -->
      <el-alert
        v-if="qualityIssues.length > 0"
        type="warning"
        :closable="false"
        style="margin-bottom: 10px"
      >
        <template #title>
          发现 {{ qualityIssues.length }} 个代码质量问题
          <el-link type="primary" @click="showQualityPanel = !showQualityPanel" style="margin-left: 10px">
            {{ showQualityPanel ? '隐藏详情' : '查看详情' }}
          </el-link>
        </template>
      </el-alert>

      <!-- Quality Issues Panel -->
      <el-collapse-transition>
        <div v-show="showQualityPanel && qualityIssues.length > 0" class="quality-panel">
          <div
            v-for="(issue, index) in qualityIssues.slice(0, 5)"
            :key="index"
            class="quality-issue"
            @click="goToLine(issue.line)"
          >
            <el-tag :type="getIssueType(issue.level)" size="small">
              {{ issue.level }}
            </el-tag>
            <span class="issue-line">第 {{ issue.line }} 行:</span>
            <span class="issue-message">{{ issue.message }}</span>
          </div>
          <div v-if="qualityIssues.length > 5" class="more-issues">
            还有 {{ qualityIssues.length - 5 }} 个问题...
          </div>
        </div>
      </el-collapse-transition>

      <MonacoEditor
        v-model="editorContent"
        :language="currentLanguage"
        :theme="currentTheme"
        :readonly="readonly"
        :options="editorOptions"
        :remote-cursors="remoteCursors"
        @change="handleContentChange"
        @cursor-change="handleCursorChange"
      />
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        v-if="!readonly"
        type="primary"
        @click="handleSave"
        :loading="saving"
      >
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Connection } from '@element-plus/icons-vue'
import MonacoEditor from './MonacoEditor.vue'
import ActiveUsers from './ActiveUsers.vue'
import { useCollaborativeEditing } from '../composables/useCollaborativeEditing'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  file: {
    type: Object,
    default: null
  },
  readonly: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: Number,
    default: null
  },
  userId: {
    type: Number,
    default: null
  },
  username: {
    type: String,
    default: 'Anonymous'
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

// Collaborative editing setup
const currentUserId = computed(() => props.userId)
const {
  activeUsers,
  remoteCursors,
  isInSession,
  joinFileSession,
  leaveFileSession,
  sendFileEdit,
  sendCursorPosition,
  handleRemoteEdit
} = useCollaborativeEditing(
  computed(() => props.file?.id),
  computed(() => props.projectId),
  currentUserId,
  computed(() => props.username)
)

// Track content change timer for sending edits
let editDebounceTimer = null
let cursorDebounceTimer = null

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const editorContent = ref('')
const currentLanguage = ref('javascript')
const currentTheme = ref('vs-dark')
const saving = ref(false)
const checking = ref(false)
const hasChanges = ref(false)
const qualityScore = ref(null)
const qualityIssues = ref([])
const showQualityPanel = ref(false)

const currentFile = computed(() => props.file)

const title = computed(() => {
  if (!currentFile.value) return '文件编辑器'
  return props.readonly ? `查看文件: ${currentFile.value.path}` : `编辑文件: ${currentFile.value.path}`
})

const editorOptions = {
  automaticLayout: true,
  scrollBeyondLastLine: false,
  fontSize: 14,
  tabSize: 2,
  wordWrap: 'on',
  minimap: {
    enabled: true
  }
}

// Watch for file changes
watch(() => props.file, (newFile) => {
  if (newFile) {
    editorContent.value = newFile.content || ''
    currentLanguage.value = newFile.language || detectLanguage(newFile.path)
    hasChanges.value = false

    // Join collaborative session when file is opened
    if (props.projectId && props.userId && newFile.id) {
      setTimeout(() => {
        joinFileSession()
      }, 500)
    }
  }
}, { immediate: true })

// Cleanup on component unmount
onUnmounted(() => {
  leaveFileSession()
  clearTimeout(editDebounceTimer)
  clearTimeout(cursorDebounceTimer)
})

function detectLanguage(path) {
  if (!path) return 'javascript'

  const ext = path.split('.').pop().toLowerCase()
  const languageMap = {
    'js': 'javascript',
    'jsx': 'javascript',
    'ts': 'typescript',
    'tsx': 'typescript',
    'py': 'python',
    'java': 'java',
    'go': 'go',
    'html': 'html',
    'htm': 'html',
    'css': 'css',
    'scss': 'scss',
    'sass': 'sass',
    'json': 'json',
    'md': 'markdown',
    'sql': 'sql',
    'sh': 'shell',
    'bash': 'shell'
  }

  return languageMap[ext] || 'plaintext'
}

function handleContentChange(content, changes) {
  hasChanges.value = content !== (props.file?.content || '')

  // Send collaborative edit if in session
  if (isInSession.value && changes) {
    // Debounce to avoid too many messages
    clearTimeout(editDebounceTimer)
    editDebounceTimer = setTimeout(() => {
      sendFileEdit(changes)
    }, 300)
  }
}

// Handle cursor position changes
function handleCursorChange(position, selection) {
  if (isInSession.value) {
    clearTimeout(cursorDebounceTimer)
    cursorDebounceTimer = setTimeout(() => {
      sendCursorPosition(position, selection)
    }, 500)
  }
}

function handleClose() {
  if (hasChanges.value && !props.readonly) {
    ElMessageBox.confirm(
      '文件已修改，确定要关闭吗？未保存的更改将丢失。',
      '确认关闭',
      {
        confirmButtonText: '关闭',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      visible.value = false
    }).catch(() => {
      // 用户取消
    })
  } else {
    visible.value = false
  }
}

async function handleSave() {
  if (!currentFile.value) return

  saving.value = true
  try {
    await emit('save', {
      file: currentFile.value,
      content: editorContent.value,
      language: currentLanguage.value
    })

    hasChanges.value = false
    ElMessage.success('文件保存成功')
  } catch (error) {
    ElMessage.error('文件保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

async function checkQuality() {
  checking.value = true

  try {
    // TODO: Implement actual API call
    // For now, simulate with mock data
    await new Promise(resolve => setTimeout(resolve, 1500))

    // Simulate quality check results
    const mockIssues = []

    // Check for common issues
    const lines = editorContent.value.split('\n')
    lines.forEach((line, index) => {
      if (line.length > 120) {
        mockIssues.push({
          level: 'warning',
          line: index + 1,
          message: '行长度超过120个字符',
          suggestion: '将长行拆分为多行'
        })
      }
      if (line.includes('password') || line.includes('secret')) {
        mockIssues.push({
          level: 'critical',
          line: index + 1,
          message: '可能包含硬编码的敏感信息',
          suggestion: '使用环境变量或配置文件'
        })
      }
      if (currentLanguage.value === 'javascript' && line.includes('var ')) {
        mockIssues.push({
          level: 'warning',
          line: index + 1,
          message: '使用var声明变量已过时',
          suggestion: '使用let或const代替'
        })
      }
    })

    qualityIssues.value = mockIssues
    qualityScore.value = Math.max(40, 100 - mockIssues.length * 5)

    if (mockIssues.length === 0) {
      ElMessage.success('代码质量检查完成，未发现问题！')
    } else {
      ElMessage.warning(`发现 ${mockIssues.length} 个代码质量问题`)
      showQualityPanel.value = true
    }

  } catch (error) {
    ElMessage.error('质量检查失败: ' + error.message)
  } finally {
    checking.value = false
  }
}

function getQualityType(score) {
  if (score >= 90) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}

function getIssueType(level) {
  const types = {
    critical: 'danger',
    error: 'warning',
    warning: 'info',
    info: ''
  }
  return types[level] || ''
}

function goToLine(lineNumber) {
  // TODO: Implement monaco editor goToLine functionality
  ElMessage.info(`跳转到第 ${lineNumber} 行`)
}
</script>

<style scoped>
.editor-container {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.quality-badge {
  margin-left: 10px;
}

.editor-info {
  flex: 1;
  text-align: right;
  color: #606266;
  font-size: 14px;
}

.monaco-editor-container {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.quality-panel {
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  background: #fff8e6;
  border: 1px solid #ffe58f;
  border-radius: 4px;
  margin-bottom: 10px;
}

.quality-issue {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  margin-bottom: 6px;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.quality-issue:hover {
  background: #f5f7fa;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.issue-line {
  font-weight: 600;
  color: #409eff;
  min-width: 60px;
}

.issue-message {
  flex: 1;
  color: #606266;
}

.more-issues {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 8px;
}
</style>
