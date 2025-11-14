<template>
  <div class="organization-management">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>组织管理</h2>
          <p class="subtitle">管理企业组织、订阅计划和设置</p>
        </div>
        <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
          创建组织
        </el-button>
      </div>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#409eff"><OfficeBuilding /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.total }}</div>
              <div class="stat-label">总组织数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#67c23a"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.active }}</div>
              <div class="stat-label">活跃组织</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#e6a23c"><Star /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.enterprise }}</div>
              <div class="stat-label">企业版</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#f56c6c"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.trial }}</div>
              <div class="stat-label">试用中</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="搜索">
          <el-input
            v-model="filters.search"
            placeholder="组织名称或Slug"
            :prefix-icon="Search"
            clearable
            style="width: 250px"
          />
        </el-form-item>
        <el-form-item label="订阅级别">
          <el-select v-model="filters.tier" placeholder="全部" clearable style="width: 150px">
            <el-option label="免费版" value="free" />
            <el-option label="入门版" value="starter" />
            <el-option label="专业版" value="professional" />
            <el-option label="企业版" value="enterprise" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.isActive" placeholder="全部" clearable style="width: 120px">
            <el-option label="活跃" :value="true" />
            <el-option label="已停用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadOrganizations">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Organizations Table -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="filteredOrganizations"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="组织">
          <template #default="{ row }">
            <div class="org-info">
              <div class="org-name">{{ row.name }}</div>
              <div class="org-slug">{{ row.slug }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="订阅级别" width="120">
          <template #default="{ row }">
            <el-tag :type="getTierType(row.tier)">
              {{ getTierLabel(row.tier) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '活跃' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="SSO" width="80" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.sso_enabled" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#dcdfe6"><CircleClose /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="contact_email" label="联系邮箱" width="200" />
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewOrganization(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editOrganization(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除此组织吗？这将删除所有相关数据！"
              @confirm="deleteOrganization(row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadOrganizations"
          @current-change="loadOrganizations"
        />
      </div>
    </el-card>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑组织' : '创建组织'"
      width="600px"
    >
      <el-form
        ref="orgFormRef"
        :model="orgForm"
        :rules="orgFormRules"
        label-width="120px"
      >
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="orgForm.name" placeholder="输入组织名称" />
        </el-form-item>
        <el-form-item label="Slug" prop="slug" v-if="!isEditing">
          <el-input v-model="orgForm.slug" placeholder="组织唯一标识（小写字母和短横线）" />
        </el-form-item>
        <el-form-item label="订阅级别" prop="tier">
          <el-select v-model="orgForm.tier" style="width: 100%">
            <el-option label="免费版" value="free" />
            <el-option label="入门版" value="starter" />
            <el-option label="专业版" value="professional" />
            <el-option label="企业版" value="enterprise" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系邮箱" prop="contact_email">
          <el-input v-model="orgForm.contact_email" placeholder="contact@example.com" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="orgForm.description"
            type="textarea"
            :rows="3"
            placeholder="组织描述"
          />
        </el-form-item>
        <el-form-item label="状态" v-if="isEditing">
          <el-switch v-model="orgForm.is_active" active-text="活跃" inactive-text="停用" />
        </el-form-item>
        <el-form-item label="启用SSO" v-if="isEditing">
          <el-switch v-model="orgForm.sso_enabled" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitOrganization" :loading="submitting">
          {{ isEditing ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- View Organization Dialog -->
    <el-dialog
      v-model="showViewDialog"
      title="组织详情"
      width="700px"
    >
      <div v-if="selectedOrg" class="org-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedOrg.id }}</el-descriptions-item>
          <el-descriptions-item label="组织名称">{{ selectedOrg.name }}</el-descriptions-item>
          <el-descriptions-item label="Slug">{{ selectedOrg.slug }}</el-descriptions-item>
          <el-descriptions-item label="订阅级别">
            <el-tag :type="getTierType(selectedOrg.tier)">
              {{ getTierLabel(selectedOrg.tier) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedOrg.is_active ? 'success' : 'danger'">
              {{ selectedOrg.is_active ? '活跃' : '已停用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="SSO">
            {{ selectedOrg.sso_enabled ? '已启用' : '未启用' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系邮箱" :span="2">
            {{ selectedOrg.contact_email || '未设置' }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedOrg.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedOrg.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(selectedOrg.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="action-buttons">
          <el-button @click="$router.push(`/teams?org_id=${selectedOrg.id}`)">
            管理团队
          </el-button>
          <el-button @click="$router.push(`/quotas?org_id=${selectedOrg.id}`)">
            配额管理
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus, Search, OfficeBuilding, CircleCheck, CircleClose,
  Star, Warning
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// State
const loading = ref(false)
const submitting = ref(false)
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const isEditing = ref(false)
const organizations = ref([])
const selectedOrg = ref(null)

const statistics = reactive({
  total: 0,
  active: 0,
  enterprise: 0,
  trial: 0
})

const filters = reactive({
  search: '',
  tier: null,
  isActive: null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const orgForm = reactive({
  name: '',
  slug: '',
  tier: 'free',
  contact_email: '',
  description: '',
  is_active: true,
  sso_enabled: false
})

const orgFormRef = ref(null)
const orgFormRules = {
  name: [
    { required: true, message: '请输入组织名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ],
  slug: [
    { required: true, message: '请输入Slug', trigger: 'blur' },
    { pattern: /^[a-z0-9-]+$/, message: 'Slug只能包含小写字母、数字和短横线', trigger: 'blur' }
  ],
  contact_email: [
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

// Computed
const filteredOrganizations = computed(() => {
  let result = organizations.value

  if (filters.search) {
    const search = filters.search.toLowerCase()
    result = result.filter(org =>
      org.name.toLowerCase().includes(search) ||
      org.slug.toLowerCase().includes(search)
    )
  }

  return result
})

// Methods
const loadOrganizations = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (filters.tier) params.tier = filters.tier
    if (filters.isActive !== null) params.is_active = filters.isActive

    const response = await api.get('/organizations', { params })
    organizations.value = response.data
    pagination.total = response.data.length

    updateStatistics()
  } catch (error) {
    ElMessage.error('加载组织列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const updateStatistics = () => {
  statistics.total = organizations.value.length
  statistics.active = organizations.value.filter(o => o.is_active).length
  statistics.enterprise = organizations.value.filter(o => o.tier === 'enterprise').length
  statistics.trial = organizations.value.filter(o => o.trial_ends_at && new Date(o.trial_ends_at) > new Date()).length
}

const resetFilters = () => {
  filters.search = ''
  filters.tier = null
  filters.isActive = null
  loadOrganizations()
}

const viewOrganization = (org) => {
  selectedOrg.value = org
  showViewDialog.value = true
}

const editOrganization = (org) => {
  isEditing.value = true
  Object.assign(orgForm, {
    id: org.id,
    name: org.name,
    tier: org.tier,
    contact_email: org.contact_email || '',
    description: org.description || '',
    is_active: org.is_active,
    sso_enabled: org.sso_enabled
  })
  showCreateDialog.value = true
}

const submitOrganization = async () => {
  if (!orgFormRef.value) return

  await orgFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditing.value) {
        await api.put(`/organizations/${orgForm.id}`, {
          name: orgForm.name,
          tier: orgForm.tier,
          contact_email: orgForm.contact_email,
          description: orgForm.description,
          is_active: orgForm.is_active,
          sso_enabled: orgForm.sso_enabled
        })
        ElMessage.success('组织更新成功')
      } else {
        await api.post('/organizations', {
          name: orgForm.name,
          slug: orgForm.slug,
          tier: orgForm.tier,
          contact_email: orgForm.contact_email,
          description: orgForm.description
        })
        ElMessage.success('组织创建成功')
      }

      showCreateDialog.value = false
      resetForm()
      await loadOrganizations()
    } catch (error) {
      ElMessage.error(isEditing.value ? '更新失败: ' + error.message : '创建失败: ' + error.message)
    } finally {
      submitting.value = false
    }
  })
}

const deleteOrganization = async (id) => {
  try {
    await api.delete(`/organizations/${id}`)
    ElMessage.success('组织删除成功')
    await loadOrganizations()
  } catch (error) {
    ElMessage.error('删除失败: ' + error.message)
  }
}

const resetForm = () => {
  Object.assign(orgForm, {
    name: '',
    slug: '',
    tier: 'free',
    contact_email: '',
    description: '',
    is_active: true,
    sso_enabled: false
  })
  isEditing.value = false
  if (orgFormRef.value) {
    orgFormRef.value.resetFields()
  }
}

const getTierType = (tier) => {
  const types = {
    free: '',
    starter: 'info',
    professional: 'success',
    enterprise: 'warning'
  }
  return types[tier] || ''
}

const getTierLabel = (tier) => {
  const labels = {
    free: '免费版',
    starter: '入门版',
    professional: '专业版',
    enterprise: '企业版'
  }
  return labels[tier] || tier
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// Lifecycle
onMounted(() => {
  loadOrganizations()
})
</script>

<style scoped lang="scss">
.organization-management {
  .header-card {
    margin-bottom: 20px;

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
      }

      .subtitle {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 20px;

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 28px;
            font-weight: bold;
            color: #303133;
          }

          .stat-label {
            margin-top: 4px;
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  .filter-card {
    margin-bottom: 20px;
  }

  .table-card {
    .org-info {
      .org-name {
        font-weight: 500;
        margin-bottom: 4px;
      }

      .org-slug {
        font-size: 12px;
        color: #909399;
      }
    }

    .pagination {
      margin-top: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }

  .org-detail {
    .action-buttons {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      justify-content: center;
    }
  }
}
</style>
