<template>
  <div class="files-page">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>文件管理</h2>
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
      </el-form>
    </el-card>

    <el-row :gutter="20" v-if="selectedProjectId">
      <!-- File Tree -->
      <el-col :span="8">
        <el-card class="file-tree-card" shadow="never" v-loading="loading">
          <template #header>
            <span>文件列表</span>
          </template>
          <el-tree
            :data="fileTree"
            :props="treeProps"
            node-key="id"
            highlight-current
            @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon v-if="data.type === 'folder'">
                  <Folder />
                </el-icon>
                <el-icon v-else>
                  <Document />
                </el-icon>
                <span class="node-label">{{ node.label }}</span>
              </span>
            </template>
          </el-tree>

          <el-empty v-if="files.length === 0" description="暂无文件" />
        </el-card>
      </el-col>

      <!-- File Details and Content -->
      <el-col :span="16">
        <el-card class="file-content-card" shadow="never" v-if="selectedFile">
          <template #header>
            <div class="file-header">
              <div>
                <h3>{{ selectedFile.path }}</h3>
                <el-tag size="small" v-if="selectedFile.language">
                  {{ selectedFile.language }}
                </el-tag>
              </div>
              <el-button-group>
                <el-button
                  size="small"
                  :icon="Edit"
                  @click="handleEditFile"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  :icon="Clock"
                  @click="showVersionHistory = true"
                >
                  历史版本
                </el-button>
                <el-button
                  size="small"
                  :icon="Delete"
                  type="danger"
                  @click="handleDeleteFile"
                >
                  删除
                </el-button>
              </el-button-group>
            </div>
          </template>

          <el-descriptions :column="2" border class="file-info">
            <el-descriptions-item label="文件大小">
              {{ formatSize(selectedFile.size) }}
            </el-descriptions-item>
            <el-descriptions-item label="当前版本">
              v{{ selectedFile.current_version }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(selectedFile.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDate(selectedFile.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <div class="file-content">
            <el-scrollbar height="400px">
              <pre><code>{{ selectedFile.content || '文件内容为空' }}</code></pre>
            </el-scrollbar>
          </div>
        </el-card>

        <el-empty
          v-else
          description="请从左侧选择文件"
          :image-size="200"
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
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="文件路径" prop="path">
          <el-input
            v-model="createForm.path"
            placeholder="例如: src/main.py"
          />
        </el-form-item>
        <el-form-item label="文件语言" prop="language">
          <el-select v-model="createForm.language" placeholder="选择语言">
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="TypeScript" value="typescript" />
            <el-option label="Java" value="java" />
            <el-option label="Go" value="go" />
            <el-option label="HTML" value="html" />
            <el-option label="CSS" value="css" />
            <el-option label="JSON" value="json" />
            <el-option label="Markdown" value="markdown" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件内容" prop="content">
          <el-input
            v-model="createForm.content"
            type="textarea"
            :rows="10"
            placeholder="输入文件内容"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateFile">创建</el-button>
      </template>
    </el-dialog>

    <!-- Version History Dialog -->
    <el-dialog
      v-model="showVersionHistory"
      title="版本历史"
      width="800px"
    >
      <el-timeline v-if="fileVersions.length > 0">
        <el-timeline-item
          v-for="version in fileVersions"
          :key="version.id"
          :timestamp="formatDate(version.created_at)"
          placement="top"
        >
          <el-card>
            <div class="version-info">
              <span>版本 v{{ version.version }}</span>
              <el-button
                size="small"
                @click="handleRestoreVersion(version)"
              >
                恢复此版本
              </el-button>
            </div>
            <el-divider />
            <el-scrollbar height="200px">
              <pre><code>{{ version.content }}</code></pre>
            </el-scrollbar>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-else description="暂无历史版本" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Clock, Folder, Document } from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const projects = ref([])
const selectedProjectId = ref(null)
const files = ref([])
const selectedFile = ref(null)
const fileVersions = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showVersionHistory = ref(false)

const createFormRef = ref(null)
const createForm = ref({
  path: '',
  language: 'python',
  content: ''
})

const createRules = {
  path: [
    { required: true, message: '请输入文件路径', trigger: 'blur' }
  ]
}

const treeProps = {
  children: 'children',
  label: 'label'
}

onMounted(async () => {
  await loadProjects()
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

async function loadFiles() {
  if (!selectedProjectId.value) return

  loading.value = true
  try {
    // TODO: Implement API endpoint for fetching project files
    // For now, using mock data
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
        path: 'requirements.txt',
        content: 'fastapi>=0.104.0\nuvicorn>=0.24.0\nsqlalchemy>=2.0.0',
        language: 'text',
        size: 512,
        current_version: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    ]

    selectedFile.value = null
  } catch (error) {
    console.error('Load files error:', error)
    ElMessage.error('加载文件列表失败')
  } finally {
    loading.value = false
  }
}

// Build file tree from flat file list
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

function handleNodeClick(data) {
  if (data.type === 'file' && data.data) {
    selectedFile.value = data.data
    loadFileVersions(data.data.id)
  }
}

async function loadFileVersions(fileId) {
  try {
    // TODO: Implement API endpoint for fetching file versions
    fileVersions.value = []
  } catch (error) {
    console.error('Load file versions error:', error)
  }
}

async function handleCreateFile() {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      // TODO: Implement API endpoint for creating files
      ElMessage.success('文件创建成功')
      showCreateDialog.value = false
      createForm.value = { path: '', language: 'python', content: '' }
      await loadFiles()
    } catch (error) {
      console.error('Create file error:', error)
      ElMessage.error('创建文件失败')
    }
  })
}

function handleEditFile() {
  ElMessage.info('文件编辑功能开发中（将集成Monaco Editor）')
}

async function handleDeleteFile() {
  if (!selectedFile.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除文件 ${selectedFile.value.path} 吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: Implement API endpoint for deleting files
    ElMessage.success('文件删除成功')
    selectedFile.value = null
    await loadFiles()
  } catch (error) {
    if (error === 'cancel') return
    console.error('Delete file error:', error)
    ElMessage.error('删除文件失败')
  }
}

async function handleRestoreVersion(version) {
  try {
    await ElMessageBox.confirm(
      `确定要恢复到版本 v${version.version} 吗？`,
      '确认恢复',
      {
        confirmButtonText: '恢复',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: Implement API endpoint for restoring file version
    ElMessage.success('版本恢复成功')
    showVersionHistory.value = false
    await loadFiles()
  } catch (error) {
    if (error === 'cancel') return
    console.error('Restore version error:', error)
    ElMessage.error('恢复版本失败')
  }
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
</script>

<style scoped>
.files-page {
  padding: 20px;
}

.toolbar-card {
  margin: 20px 0;
}

.file-tree-card {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.file-content-card {
  height: calc(100vh - 200px);
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-label {
  font-size: 14px;
}

.file-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-header h3 {
  margin: 0 0 5px 0;
}

.file-info {
  margin-top: 20px;
}

.file-content {
  margin-top: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
}

.file-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.version-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
