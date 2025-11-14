<template>
  <div class="files-page">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>文件管理 - 实时协作编辑</h2>
      </template>
    </el-page-header>

    <el-card class="toolbar-card" shadow="never">
      <el-form :inline="true">
        <el-form-item label="项目">
          <el-select
            v-model="selectedProjectId"
            placeholder="选择项目"
            @change="loadFiles"
            style="width: 300px"
          >
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :icon="Plus"
            @click="showCreateDialog = true"
            :disabled="!selectedProjectId"
          >
            新建文件
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-tag v-if="isConnected" type="success">
            <el-icon><Connection /></el-icon>
            WebSocket已连接
          </el-tag>
          <el-tag v-else type="danger">
            <el-icon><Close /></el-icon>
            WebSocket未连接
          </el-tag>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" v-if="selectedProjectId">
      <!-- File Tree -->
      <el-col :span="6">
        <el-card class="file-tree-card" shadow="never" v-loading="loading">
          <template #header>
            <div class="card-header-flex">
              <span>文件列表</span>
              <el-badge :value="files.length" type="primary" />
            </div>
          </template>
          <el-tree
            :data="fileTree"
            :props="treeProps"
            node-key="id"
            highlight-current
            @node-click="handleNodeClick"
            :expand-on-click-node="false"
            default-expand-all
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon v-if="data.type === 'folder'" class="folder-icon">
                  <Folder />
                </el-icon>
                <el-icon v-else class="file-icon">
                  <Document />
                </el-icon>
                <span class="node-label">{{ node.label }}</span>
                <el-badge
                  v-if="data.type === 'file' && isFileBeingEdited(data.id)"
                  :value="getFileEditorCount(data.id)"
                  type="warning"
                  class="edit-badge"
                />
              </span>
            </template>
          </el-tree>

          <el-empty v-if="files.length === 0" description="暂无文件" :image-size="100" />
        </el-card>
      </el-col>

      <!-- File Editor -->
      <el-col :span="14">
        <el-card class="file-editor-card" shadow="never" v-if="editingFile">
          <template #header>
            <div class="file-header">
              <div class="file-title-section">
                <h3>{{ editingFile.path }}</h3>
                <div class="file-meta">
                  <el-tag size="small" v-if="editingFile.language" type="primary">
                    {{ editingFile.language }}
                  </el-tag>
                  <el-tag size="small" v-if="isInSession" type="success">
                    <el-icon><Connection /></el-icon>
                    协作中
                  </el-tag>
                  <el-text size="small" type="info">
                    {{ formatSize(editingFile.size) }}
                  </el-text>
                </div>
              </div>
              <el-button-group>
                <el-button
                  size="small"
                  :icon="Check"
                  type="success"
                  @click="saveFile"
                  :loading="saving"
                >
                  保存
                </el-button>
                <el-button
                  size="small"
                  :icon="Clock"
                  @click="showVersionHistory = true"
                >
                  历史
                </el-button>
                <el-button
                  size="small"
                  :icon="Close"
                  @click="closeEditor"
                >
                  关闭
                </el-button>
              </el-button-group>
            </div>
          </template>

          <!-- Monaco Editor with Collaborative Editing -->
          <div class="editor-container">
            <MonacoEditor
              v-model="fileContent"
              :language="editingFile.language || 'plaintext'"
              :theme="editorTheme"
              :readonly="false"
              :remoteCursors="remoteCursors"
              @change="handleEditorChange"
              @cursor-change="handleCursorChange"
              ref="monacoEditorRef"
            />
          </div>

          <!-- Editor Footer -->
          <div class="editor-footer">
            <div class="editor-stats">
              <el-text size="small">
                行: {{ editorStats.lines }} | 字符: {{ editorStats.characters }}
              </el-text>
            </div>
            <div class="editor-actions">
              <el-switch
                v-model="editorTheme"
                active-value="vs-dark"
                inactive-value="vs-light"
                active-text="暗色"
                inactive-text="亮色"
                size="small"
              />
            </div>
          </div>
        </el-card>

        <el-empty
          v-else
          description="请从左侧选择文件进行编辑"
          :image-size="200"
        >
          <template #image>
            <el-icon :size="100" color="#909399">
              <DocumentAdd />
            </el-icon>
          </template>
        </el-empty>
      </el-col>

      <!-- Active Users Panel -->
      <el-col :span="4">
        <ActiveUsers
          :users="activeUsers"
          :currentUserId="currentUserId"
        />

        <!-- File Actions Card -->
        <el-card class="actions-card" shadow="never" style="margin-top: 20px;" v-if="editingFile">
          <template #header>
            <span>文件操作</span>
          </template>
          <el-space direction="vertical" style="width: 100%" :size="10">
            <el-button :icon="Download" style="width: 100%">
              下载文件
            </el-button>
            <el-button :icon="Share" style="width: 100%">
              分享链接
            </el-button>
            <el-button :icon="Delete" type="danger" style="width: 100%" @click="handleDeleteFile">
              删除文件
            </el-button>
          </el-space>
        </el-card>

        <!-- Collaboration Notifications -->
        <CollaborationNotification
          v-if="showCollabNotification"
          :notification="collabNotification"
          @close="showCollabNotification = false"
        />
      </el-col>
    </el-row>

    <el-empty
      v-else
      description="请选择项目查看文件"
      :image-size="200"
    />

    <!-- Create File Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      title="新建文件"
      width="600px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="文件路径" prop="path">
          <el-input
            v-model="createForm.path"
            placeholder="例如: src/main.py"
          >
            <template #prepend>
              <el-icon><Folder /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="文件语言" prop="language">
          <el-select v-model="createForm.language" placeholder="选择语言" style="width: 100%">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="TypeScript" value="typescript" />
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
            <el-option label="HTML" value="html" />
            <el-option label="CSS" value="css" />
            <el-option label="JSON" value="json" />
            <el-option label="Markdown" value="markdown" />
            <el-option label="纯文本" value="plaintext" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始内容">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="8"
            placeholder="输入初始文件内容（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFile" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- Version History Dialog -->
    <el-dialog
      v-model="showVersionHistory"
      title="版本历史"
      width="900px"
    >
      <el-timeline v-if="fileVersions.length > 0">
        <el-timeline-item
          v-for="version in fileVersions"
          :key="version.id"
          :timestamp="formatDate(version.created_at)"
          placement="top"
          type="primary"
        >
          <el-card shadow="hover">
            <div class="version-info">
              <div>
                <el-tag type="primary">v{{ version.version }}</el-tag>
                <el-text size="small" style="margin-left: 10px">
                  {{ version.created_by || '系统' }}
                </el-text>
              </div>
              <el-button
                size="small"
                :icon="RefreshLeft"
                @click="handleRestoreVersion(version)"
              >
                恢复此版本
              </el-button>
            </div>
            <el-divider />
            <el-scrollbar height="200px">
              <pre class="version-content"><code>{{ version.content }}</code></pre>
            </el-scrollbar>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无历史版本" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  Clock,
  Folder,
  Document,
  Check,
  Close,
  Connection,
  Download,
  Share,
  DocumentAdd,
  RefreshLeft
} from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useCollaborativeEditing } from '@/composables/useCollaborativeEditing'
import { useWebSocket } from '@/composables/useWebSocket'
import MonacoEditor from '@/components/MonacoEditor.vue'
import ActiveUsers from '@/components/ActiveUsers.vue'
import CollaborationNotification from '@/components/CollaborationNotification.vue'

const authStore = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// WebSocket
const { socket, isConnected } = useWebSocket()

// State
const projects = ref([])
const selectedProjectId = ref(null)
const files = ref([])
const editingFile = ref(null)
const fileContent = ref('')
const fileVersions = ref([])
const loading = ref(false)
const saving = ref(false)
const creating = ref(false)
const showCreateDialog = ref(false)
const showVersionHistory = ref(false)
const editorTheme = ref('vs-dark')
const monacoEditorRef = ref(null)

// Collaborative editing state
const currentUserId = computed(() => authStore.user?.id || 1)
const currentUsername = computed(() => authStore.user?.username || 'User')
const editingFileId = computed(() => editingFile.value?.id)

const {
  activeUsers,
  remoteCursors,
  isInSession,
  onlineUserCount,
  joinFileSession,
  leaveFileSession,
  sendFileEdit,
  sendCursorPosition,
  handleRemoteEdit
} = useCollaborativeEditing(
  editingFileId,
  selectedProjectId,
  currentUserId,
  currentUsername
)

// Collaboration notifications
const showCollabNotification = ref(false)
const collabNotification = ref({})

// Editor stats
const editorStats = computed(() => {
  const lines = fileContent.value ? fileContent.value.split('\n').length : 0
  const characters = fileContent.value ? fileContent.value.length : 0
  return { lines, characters }
})

// Create form
const createFormRef = ref(null)
const createForm = ref({
  path: '',
  language: 'python',
  content: ''
})

const createRules = {
  path: [
    { required: true, message: '请输入文件路径', trigger: 'blur' }
  ],
  language: [
    { required: true, message: '请选择文件语言', trigger: 'change' }
  ]
}

const treeProps = {
  children: 'children',
  label: 'label'
}

onMounted(async () => {
  await loadProjects()
})

onUnmounted(() => {
  if (isInSession.value) {
    leaveFileSession()
  }
})

// Load projects
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

// Load files
async function loadFiles() {
  if (!selectedProjectId.value) return

  loading.value = true
  try {
    // TODO: Implement API endpoint
    // Mock data
    files.value = [
      {
        id: 1,
        project_id: selectedProjectId.value,
        path: 'src/main.py',
        content: '# Main entry point\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()',
        language: 'python',
        size: 1024,
        current_version: 2,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 2,
        project_id: selectedProjectId.value,
        path: 'src/utils/helpers.py',
        content: '# Utility functions\n\ndef format_date(date):\n    return date.strftime("%Y-%m-%d")',
        language: 'python',
        size: 512,
        current_version: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 3,
        project_id: selectedProjectId.value,
        path: 'requirements.txt',
        content: 'fastapi>=0.104.0\nuvicorn>=0.24.0\nsqlalchemy>=2.0.0',
        language: 'plaintext',
        size: 256,
        current_version: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      {
        id: 4,
        project_id: selectedProjectId.value,
        path: 'README.md',
        content: '# Project Title\n\n## Description\n\nThis is a sample project.',
        language: 'markdown',
        size: 128,
        current_version: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ]

    editingFile.value = null
  } catch (error) {
    console.error('Load files error:', error)
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// Build file tree
const fileTree = computed(() => {
  const tree = []
  const map = {}

  files.value.forEach(file => {
    const parts = file.path.split('/')
    let currentLevel = tree

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1
      const path = parts.slice(0, index + 1).join('/')

      let node = map[path]

      if (!node) {
        node = {
          id: isFile ? file.id : `folder-${path}`,
          label: part,
          path: path,
          type: isFile ? 'file' : 'folder',
          data: isFile ? file : null,
          children: isFile ? undefined : []
        }

        map[path] = node
        currentLevel.push(node)
      }

      if (!isFile) {
        currentLevel = node.children
      }
    })
  })

  return tree
})

// Handle node click
async function handleNodeClick(data) {
  if (data.type === 'file' && data.data) {
    // Leave previous session if any
    if (isInSession.value && editingFile.value?.id !== data.data.id) {
      leaveFileSession()
    }

    editingFile.value = data.data
    fileContent.value = data.data.content || ''

    // Join collaborative session
    await nextTick()
    joinFileSession()

    await loadFileVersions(data.data.id)
  }
}

// Load file versions
async function loadFileVersions(fileId) {
  try {
    // TODO: API call
    fileVersions.value = [
      {
        id: 1,
        version: 1,
        content: 'Previous version content...',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        created_by: 'admin'
      }
    ]
  } catch (error) {
    console.error('Load file versions error:', error)
  }
}

// Handle editor change
function handleEditorChange(value, changes) {
  fileContent.value = value

  // Send changes to other collaborators
  if (isInSession.value && changes) {
    sendFileEdit(changes)
  }
}

// Handle cursor change
function handleCursorChange(position, selection) {
  if (isInSession.value) {
    sendCursorPosition(position, selection)
  }
}

// Save file
async function saveFile() {
  if (!editingFile.value) return

  saving.value = true
  try {
    // TODO: API call to save file
    await new Promise(resolve => setTimeout(resolve, 500)) // Simulate API call

    editingFile.value.content = fileContent.value
    editingFile.value.size = new Blob([fileContent.value]).size
    editingFile.value.current_version++
    editingFile.value.updated_at = new Date().toISOString()

    ElMessage.success('文件保存成功')
  } catch (error) {
    console.error('Save file error:', error)
    ElMessage.error('保存文件失败')
  } finally {
    saving.value = false
  }
}

// Close editor
function closeEditor() {
  if (isInSession.value) {
    leaveFileSession()
  }
  editingFile.value = null
  fileContent.value = ''
}

// Create file
async function handleCreateFile() {
  if (!createFormRef.value) return

  try {
    await createFormRef.value.validate()
    creating.value = true

    // TODO: API call
    const newFile = {
      id: Date.now(),
      project_id: selectedProjectId.value,
      path: createForm.value.path,
      content: createForm.value.content,
      language: createForm.value.language,
      size: new Blob([createForm.value.content]).size,
      current_version: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }

    files.value.push(newFile)

    ElMessage.success('文件创建成功')
    showCreateDialog.value = false
    resetCreateForm()
  } catch (error) {
    if (error !== false) {
      console.error('Create file error:', error)
      ElMessage.error('创建文件失败')
    }
  } finally {
    creating.value = false
  }
}

// Delete file
async function handleDeleteFile() {
  if (!editingFile.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除文件 ${editingFile.value.path} 吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: API call
    files.value = files.value.filter(f => f.id !== editingFile.value.id)

    ElMessage.success('文件删除成功')
    closeEditor()
  } catch (error) {
    if (error === 'cancel') return
    console.error('Delete file error:', error)
    ElMessage.error('删除文件失败')
  }
}

// Restore version
async function handleRestoreVersion(version) {
  try {
    await ElMessageBox.confirm(
      `确定要恢复到版本 v${version.version} 吗？当前内容将被覆盖。`,
      '确认恢复',
      {
        confirmButtonText: '恢复',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: API call
    fileContent.value = version.content
    ElMessage.success('版本恢复成功')
    showVersionHistory.value = false
  } catch (error) {
    if (error === 'cancel') return
    console.error('Restore version error:', error)
    ElMessage.error('恢复版本失败')
  }
}

// Helper functions
function resetCreateForm() {
  createForm.value = {
    path: '',
    language: 'python',
    content: ''
  }
}

function isFileBeingEdited(fileId) {
  return editingFile.value?.id === fileId && activeUsers.value.length > 1
}

function getFileEditorCount(fileId) {
  return editingFile.value?.id === fileId ? activeUsers.value.length - 1 : 0
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

function formatSize(bytes) {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Watch for remote edits
watch(() => handleRemoteEdit, (editHandler) => {
  if (editHandler && monacoEditorRef.value) {
    // Apply remote changes to editor
    // This is handled by the collaborative editing composable
  }
}, { deep: true })
</script>

<style scoped lang="scss">
.files-page {
  padding: 20px;

  .el-page-header {
    margin-bottom: 20px;
  }
}

.toolbar-card {
  margin-bottom: 20px;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-tree-card {
  height: calc(100vh - 250px);

  :deep(.el-card__body) {
    height: calc(100% - 56px);
    overflow-y: auto;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;

  .folder-icon {
    color: #E6A23C;
  }

  .file-icon {
    color: #409EFF;
  }

  .node-label {
    font-size: 14px;
    flex: 1;
  }

  .edit-badge {
    margin-left: auto;
  }
}

.file-editor-card {
  height: calc(100vh - 250px);

  :deep(.el-card__body) {
    height: calc(100% - 56px);
    display: flex;
    flex-direction: column;
    padding: 0;
  }
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .file-title-section {
    flex: 1;

    h3 {
      margin: 0 0 8px 0;
      font-size: 16px;
    }

    .file-meta {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }
}

.editor-container {
  flex: 1;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 20px;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-lighter);
}

.actions-card {
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.version-content {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  background: var(--el-fill-color-lighter);
  padding: 12px;
  border-radius: 4px;
}

.version-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
