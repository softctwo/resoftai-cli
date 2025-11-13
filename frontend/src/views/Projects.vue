<template>
  <div class="projects-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <h1>项目管理</h1>
      <div class="toolbar-actions">
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          新建项目
        </el-button>
      </div>
    </div>

    <!-- 项目列表 -->
    <el-card shadow="never">
      <el-table :data="projects" v-loading="loading" stripe>
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
        <el-table-column prop="llm_provider" label="AI模型" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.llm_provider" size="small">
              {{ row.llm_provider }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewProject(row.id)">
              查看
            </el-button>
            <el-button type="danger" link @click="deleteProject(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建项目对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新项目"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>

        <el-form-item label="需求描述" prop="requirements">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="6"
            placeholder="请详细描述项目需求..."
          />
        </el-form-item>

        <el-form-item label="AI模型" prop="llm_provider">
          <el-select v-model="form.llm_provider" placeholder="选择AI模型（可选）" clearable>
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="Claude" value="anthropic" />
            <el-option label="GLM-4" value="zhipu" />
            <el-option label="Kimi" value="moonshot" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const loading = ref(false)
const creating = ref(false)
const projects = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const showCreateDialog = ref(false)
const formRef = ref(null)
const form = ref({
  name: '',
  requirements: '',
  llm_provider: ''
})

const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  requirements: [
    { required: true, message: '请输入需求描述', trigger: 'blur' },
    { min: 10, message: '需求描述至少10个字符', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadProjects()
})

async function loadProjects() {
  loading.value = true

  try {
    const response = await axios.get(`${API_BASE}/projects`, {
      params: {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value
      },
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    projects.value = response.data.projects
    total.value = response.data.total

  } catch (error) {
    console.error('Load projects error:', error)
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreate() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    creating.value = true

    try {
      await axios.post(`${API_BASE}/projects`, form.value, {
        headers: {
          Authorization: `Bearer ${authStore.token}`
        }
      })

      ElMessage.success('项目创建成功')
      showCreateDialog.value = false
      form.value = { name: '', requirements: '', llm_provider: '' }
      await loadProjects()

    } catch (error) {
      console.error('Create project error:', error)
      ElMessage.error(error.response?.data?.detail || '创建项目失败')
    } finally {
      creating.value = false
    }
  })
}

async function deleteProject(project) {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目"${project.name}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await axios.delete(`${API_BASE}/projects/${project.id}`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    ElMessage.success('项目已删除')
    await loadProjects()

  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete project error:', error)
      ElMessage.error('删除项目失败')
    }
  }
}

function handleSizeChange() {
  currentPage.value = 1
  loadProjects()
}

function handlePageChange() {
  loadProjects()
}

function viewProject(id) {
  router.push(`/projects/${id}`)
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
</script>

<style scoped>
.projects-page {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar h1 {
  margin: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
