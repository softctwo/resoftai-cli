<template>
  <div class="organization-management">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>组织管理</h2>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          创建组织
        </el-button>
      </template>
    </el-page-header>

    <!-- Organization Cards -->
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="org in organizations" :key="org.id">
        <el-card shadow="hover" class="organization-card">
          <template #header>
            <div class="card-header">
              <div class="org-info">
                <el-avatar :size="40" :src="org.logo" :icon="OfficeBuilding" />
                <div class="org-title">
                  <h3>{{ org.name }}</h3>
                  <el-tag size="small" :type="getOrgStatusType(org.status)">
                    {{ getOrgStatusText(org.status) }}
                  </el-tag>
                </div>
              </div>
              <el-dropdown trigger="click">
                <el-icon class="more-icon"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="Edit" @click="editOrganization(org)">
                      编辑
                    </el-dropdown-item>
                    <el-dropdown-item :icon="Setting" @click="configureOrganization(org)">
                      配置
                    </el-dropdown-item>
                    <el-dropdown-item :icon="Delete" @click="deleteOrganization(org)" divided>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>

          <div class="org-description">
            {{ org.description || '暂无描述' }}
          </div>

          <el-divider />

          <div class="org-stats">
            <div class="stat-item">
              <el-icon><UserFilled /></el-icon>
              <span>{{ org.member_count || 0 }} 成员</span>
            </div>
            <div class="stat-item">
              <el-icon><FolderOpened /></el-icon>
              <span>{{ org.project_count || 0 }} 项目</span>
            </div>
            <div class="stat-item">
              <el-icon><Odometer /></el-icon>
              <span>{{ formatQuota(org.quota_used, org.quota_limit) }}</span>
            </div>
          </div>

          <el-divider />

          <div class="org-actions">
            <el-button size="small" :icon="User" @click="viewMembers(org)">
              成员
            </el-button>
            <el-button size="small" :icon="Team" @click="viewTeams(org)">
              团队
            </el-button>
            <el-button size="small" :icon="Setting" @click="viewSettings(org)">
              设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="organizations.length === 0 && !loading" description="暂无组织" />

    <!-- Create/Edit Organization Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingOrg ? '编辑组织' : '创建组织'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="orgForm" :rules="orgRules" ref="orgFormRef" label-width="100px">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="orgForm.name" placeholder="请输入组织名称" />
        </el-form-item>
        <el-form-item label="组织描述" prop="description">
          <el-input
            v-model="orgForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入组织描述"
          />
        </el-form-item>
        <el-form-item label="Logo URL" prop="logo">
          <el-input v-model="orgForm.logo" placeholder="请输入Logo URL（可选）" />
        </el-form-item>
        <el-form-item label="配额限制" prop="quota_limit">
          <el-input-number
            v-model="orgForm.quota_limit"
            :min="0"
            :step="1000"
            :precision="0"
          />
          <span class="form-helper">MB</span>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="orgForm.status">
            <el-radio label="active">激活</el-radio>
            <el-radio label="suspended">暂停</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveOrganization" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- Members Dialog -->
    <el-dialog v-model="showMembersDialog" title="组织成员" width="800px">
      <div class="members-toolbar">
        <el-button :icon="Plus" @click="showAddMemberDialog = true">添加成员</el-button>
      </div>
      <el-table :data="currentOrgMembers" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="joined_at" label="加入时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.joined_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button size="small" :icon="Edit" @click="editMemberRole(row)" link>
              编辑角色
            </el-button>
            <el-button size="small" :icon="Delete" @click="removeMember(row)" type="danger" link>
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- Teams Dialog -->
    <el-dialog v-model="showTeamsDialog" title="组织团队" width="800px">
      <div class="teams-toolbar">
        <el-button :icon="Plus" @click="createTeam">创建团队</el-button>
      </div>
      <el-table :data="currentOrgTeams" style="width: 100%">
        <el-table-column prop="name" label="团队名称" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="member_count" label="成员数" width="100" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" :icon="View" @click="viewTeamDetail(row)" link>
              查看
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- Settings Dialog -->
    <el-dialog v-model="showSettingsDialog" title="组织设置" width="700px">
      <el-tabs v-model="activeSettingTab">
        <el-tab-pane label="基本设置" name="basic">
          <el-form label-width="120px">
            <el-form-item label="允许自动加入">
              <el-switch v-model="orgSettings.allow_auto_join" />
              <span class="form-helper">允许用户自动加入组织</span>
            </el-form-item>
            <el-form-item label="默认角色">
              <el-select v-model="orgSettings.default_role">
                <el-option label="成员" value="member" />
                <el-option label="开发者" value="developer" />
              </el-select>
            </el-form-item>
            <el-form-item label="项目可见性">
              <el-radio-group v-model="orgSettings.project_visibility">
                <el-radio label="private">私有</el-radio>
                <el-radio label="organization">组织内可见</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="配额管理" name="quota">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="存储配额">
              {{ formatBytes(orgSettings.storage_quota) }}
            </el-descriptions-item>
            <el-descriptions-item label="已使用">
              {{ formatBytes(orgSettings.storage_used) }}
            </el-descriptions-item>
            <el-descriptions-item label="项目数限制">
              {{ orgSettings.max_projects }}
            </el-descriptions-item>
            <el-descriptions-item label="成员数限制">
              {{ orgSettings.max_members }}
            </el-descriptions-item>
          </el-descriptions>
          <el-progress
            :percentage="(orgSettings.storage_used / orgSettings.storage_quota) * 100"
            :color="getProgressColor((orgSettings.storage_used / orgSettings.storage_quota) * 100)"
            style="margin-top: 20px"
          />
        </el-tab-pane>
        <el-tab-pane label="权限控制" name="permissions">
          <el-tree
            :data="permissionTree"
            show-checkbox
            node-key="id"
            :default-checked-keys="orgSettings.enabled_permissions"
            :props="{ children: 'children', label: 'label' }"
          />
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="showSettingsDialog = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  Setting,
  User,
  Team,
  UserFilled,
  FolderOpened,
  Odometer,
  OfficeBuilding,
  MoreFilled,
  View
} from '@element-plus/icons-vue'

// State
const loading = ref(false)
const saving = ref(false)
const organizations = ref([])
const showCreateDialog = ref(false)
const showMembersDialog = ref(false)
const showTeamsDialog = ref(false)
const showSettingsDialog = ref(false)
const showAddMemberDialog = ref(false)
const activeSettingTab = ref('basic')

const editingOrg = ref(null)
const currentOrg = ref(null)
const currentOrgMembers = ref([])
const currentOrgTeams = ref([])

const orgFormRef = ref(null)
const orgForm = ref({
  name: '',
  description: '',
  logo: '',
  quota_limit: 10000,
  status: 'active'
})

const orgSettings = ref({
  allow_auto_join: false,
  default_role: 'member',
  project_visibility: 'private',
  storage_quota: 10737418240, // 10GB
  storage_used: 2147483648, // 2GB
  max_projects: 100,
  max_members: 50,
  enabled_permissions: [1, 2, 3]
})

const permissionTree = ref([
  {
    id: 1,
    label: '项目管理',
    children: [
      { id: 11, label: '创建项目' },
      { id: 12, label: '删除项目' },
      { id: 13, label: '修改项目设置' }
    ]
  },
  {
    id: 2,
    label: '成员管理',
    children: [
      { id: 21, label: '添加成员' },
      { id: 22, label: '移除成员' },
      { id: 23, label: '修改成员角色' }
    ]
  },
  {
    id: 3,
    label: '团队管理',
    children: [
      { id: 31, label: '创建团队' },
      { id: 32, label: '删除团队' }
    ]
  }
])

const orgRules = {
  name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }],
  quota_limit: [{ required: true, message: '请设置配额限制', trigger: 'blur' }]
}

// Fetch organizations
const fetchOrganizations = async () => {
  loading.value = true
  try {
    // TODO: Replace with actual API call
    // const response = await organizationAPI.getOrganizations()

    // Mock data
    organizations.value = [
      {
        id: 1,
        name: 'ResoftAI 技术团队',
        description: '专注于AI驱动的软件开发平台',
        logo: '',
        status: 'active',
        member_count: 15,
        project_count: 8,
        quota_used: 5000,
        quota_limit: 10000,
        created_at: new Date()
      },
      {
        id: 2,
        name: '企业客户A',
        description: '大型企业客户，定制化需求较多',
        logo: '',
        status: 'active',
        member_count: 50,
        project_count: 25,
        quota_used: 15000,
        quota_limit: 20000,
        created_at: new Date()
      }
    ]
  } catch (error) {
    ElMessage.error('加载组织列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// Create/Edit organization
const saveOrganization = async () => {
  if (!orgFormRef.value) return

  try {
    await orgFormRef.value.validate()
    saving.value = true

    // TODO: Replace with actual API call
    // if (editingOrg.value) {
    //   await organizationAPI.updateOrganization(editingOrg.value.id, orgForm.value)
    // } else {
    //   await organizationAPI.createOrganization(orgForm.value)
    // }

    ElMessage.success(editingOrg.value ? '组织更新成功' : '组织创建成功')
    showCreateDialog.value = false
    fetchOrganizations()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败：' + error.message)
    }
  } finally {
    saving.value = false
  }
}

// Edit organization
const editOrganization = (org) => {
  editingOrg.value = org
  orgForm.value = { ...org }
  showCreateDialog.value = true
}

// Delete organization
const deleteOrganization = (org) => {
  ElMessageBox.confirm(
    `确定要删除组织"${org.name}"吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      // TODO: API call
      ElMessage.success('组织已删除')
      fetchOrganizations()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}

// View members
const viewMembers = (org) => {
  currentOrg.value = org
  // Mock data
  currentOrgMembers.value = [
    {
      id: 1,
      username: 'admin',
      email: 'admin@resoftai.com',
      role: 'owner',
      joined_at: new Date()
    },
    {
      id: 2,
      username: 'developer1',
      email: 'dev1@resoftai.com',
      role: 'developer',
      joined_at: new Date()
    }
  ]
  showMembersDialog.value = true
}

// View teams
const viewTeams = (org) => {
  currentOrg.value = org
  // Mock data
  currentOrgTeams.value = [
    {
      id: 1,
      name: '前端团队',
      description: '负责前端开发',
      member_count: 5,
      created_at: new Date()
    },
    {
      id: 2,
      name: '后端团队',
      description: '负责后端开发',
      member_count: 8,
      created_at: new Date()
    }
  ]
  showTeamsDialog.value = true
}

// View settings
const viewSettings = (org) => {
  currentOrg.value = org
  showSettingsDialog.value = true
}

// Save settings
const saveSettings = () => {
  // TODO: API call
  ElMessage.success('设置已保存')
  showSettingsDialog.value = false
}

// Helper functions
const formatQuota = (used, limit) => {
  const percentage = ((used / limit) * 100).toFixed(0)
  return `${percentage}% (${used}/${limit} MB)`
}

const formatBytes = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(2) + ' MB'
  return (bytes / 1073741824).toFixed(2) + ' GB'
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

const getOrgStatusType = (status) => {
  return status === 'active' ? 'success' : 'warning'
}

const getOrgStatusText = (status) => {
  return status === 'active' ? '激活' : '暂停'
}

const getRoleType = (role) => {
  const typeMap = {
    owner: 'danger',
    admin: 'warning',
    developer: 'primary',
    member: 'info'
  }
  return typeMap[role] || 'info'
}

const getRoleText = (role) => {
  const textMap = {
    owner: '所有者',
    admin: '管理员',
    developer: '开发者',
    member: '成员'
  }
  return textMap[role] || role
}

const getProgressColor = (value) => {
  if (value < 60) return '#67C23A'
  if (value < 80) return '#E6A23C'
  return '#F56C6C'
}

const resetForm = () => {
  editingOrg.value = null
  orgForm.value = {
    name: '',
    description: '',
    logo: '',
    quota_limit: 10000,
    status: 'active'
  }
}

const editMemberRole = (member) => {
  ElMessage.info('编辑成员角色功能开发中...')
}

const removeMember = (member) => {
  ElMessage.info('移除成员功能开发中...')
}

const createTeam = () => {
  ElMessage.info('创建团队功能开发中...')
}

const viewTeamDetail = (team) => {
  ElMessage.info('查看团队详情功能开发中...')
}

const configureOrganization = (org) => {
  viewSettings(org)
}

// Lifecycle
onMounted(() => {
  fetchOrganizations()
})
</script>

<style scoped lang="scss">
.organization-management {
  padding: 20px;

  .el-page-header {
    margin-bottom: 20px;
  }

  .organization-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .org-info {
        display: flex;
        gap: 12px;
        flex: 1;

        .org-title {
          h3 {
            margin: 0 0 4px 0;
            font-size: 16px;
          }
        }
      }

      .more-icon {
        cursor: pointer;
        font-size: 20px;
        color: #909399;

        &:hover {
          color: #409EFF;
        }
      }
    }

    .org-description {
      color: #606266;
      font-size: 14px;
      line-height: 1.6;
      min-height: 40px;
    }

    .org-stats {
      display: flex;
      justify-content: space-around;

      .stat-item {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #606266;
        font-size: 14px;
      }
    }

    .org-actions {
      display: flex;
      gap: 10px;

      .el-button {
        flex: 1;
      }
    }
  }

  .form-helper {
    margin-left: 10px;
    color: #909399;
    font-size: 13px;
  }

  .members-toolbar,
  .teams-toolbar {
    margin-bottom: 16px;
  }
}
</style>
