<template>
  <div class="team-management">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>团队管理</h2>
          <p class="subtitle">管理团队成员和权限</p>
        </div>
        <div class="header-actions">
          <el-select
            v-model="selectedOrgId"
            placeholder="选择组织"
            @change="loadTeams"
            style="width: 250px; margin-right: 10px"
          >
            <el-option
              v-for="org in organizations"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
          <el-button type="primary" @click="showCreateTeamDialog = true" :icon="Plus" :disabled="!selectedOrgId">
            创建团队
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- Statistics -->
    <el-row :gutter="20" class="stats-row" v-if="selectedOrgId">
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#409eff"><UserFilled /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.totalTeams }}</div>
              <div class="stat-label">总团队数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#67c23a"><Avatar /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.totalMembers }}</div>
              <div class="stat-label">总成员数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon :size="40" color="#e6a23c"><StarFilled /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ statistics.defaultTeams }}</div>
              <div class="stat-label">默认团队</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Teams List -->
    <el-card class="table-card" v-if="selectedOrgId">
      <el-input
        v-model="searchQuery"
        placeholder="搜索团队名称或描述"
        :prefix-icon="Search"
        clearable
        style="width: 300px; margin-bottom: 20px"
      />

      <el-table
        v-loading="loading"
        :data="filteredTeams"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="团队名称">
          <template #default="{ row }">
            <div class="team-info">
              <div class="team-name">
                {{ row.name }}
                <el-tag v-if="row.is_default" size="small" type="warning" style="margin-left: 8px">
                  默认
                </el-tag>
              </div>
              <div class="team-desc" v-if="row.description">{{ row.description }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="成员数" width="100" align="center">
          <template #default="{ row }">
            <el-tag>{{ row.memberCount || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewTeam(row)">查看</el-button>
            <el-button size="small" type="primary" @click="manageMembers(row)">成员管理</el-button>
            <el-button size="small" @click="editTeam(row)">编辑</el-button>
            <el-popconfirm
              title="确定要删除此团队吗？"
              @confirm="deleteTeam(row.id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Empty State -->
    <el-card v-if="!selectedOrgId" class="empty-state">
      <el-empty description="请先选择一个组织">
        <el-button type="primary" @click="$router.push('/organizations')">
          前往组织管理
        </el-button>
      </el-empty>
    </el-card>

    <!-- Create/Edit Team Dialog -->
    <el-dialog
      v-model="showCreateTeamDialog"
      :title="isEditingTeam ? '编辑团队' : '创建团队'"
      width="500px"
    >
      <el-form
        ref="teamFormRef"
        :model="teamForm"
        :rules="teamFormRules"
        label-width="100px"
      >
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="teamForm.name" placeholder="输入团队名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="teamForm.description"
            type="textarea"
            :rows="3"
            placeholder="团队描述"
          />
        </el-form-item>
        <el-form-item label="默认团队">
          <el-switch v-model="teamForm.is_default" />
          <div class="form-tip">新成员将自动加入默认团队</div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateTeamDialog = false">取消</el-button>
        <el-button type="primary" @click="submitTeam" :loading="submitting">
          {{ isEditingTeam ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- View Team Dialog -->
    <el-dialog
      v-model="showViewDialog"
      title="团队详情"
      width="600px"
    >
      <div v-if="selectedTeam">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ selectedTeam.id }}</el-descriptions-item>
          <el-descriptions-item label="团队名称">{{ selectedTeam.name }}</el-descriptions-item>
          <el-descriptions-item label="所属组织" :span="2">
            {{ getOrganizationName(selectedTeam.organization_id) }}
          </el-descriptions-item>
          <el-descriptions-item label="默认团队">
            {{ selectedTeam.is_default ? '是' : '否' }}
          </el-descriptions-item>
          <el-descriptions-item label="成员数">
            {{ selectedTeam.memberCount || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ selectedTeam.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedTeam.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(selectedTeam.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Manage Members Dialog -->
    <el-dialog
      v-model="showMembersDialog"
      title="成员管理"
      width="800px"
    >
      <div v-if="selectedTeam">
        <div class="members-header">
          <h3>{{ selectedTeam.name }} - 成员列表</h3>
          <el-button type="primary" size="small" @click="showAddMemberDialog = true" :icon="Plus">
            添加成员
          </el-button>
        </div>

        <el-table
          v-loading="loadingMembers"
          :data="teamMembers"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="user_id" label="用户ID" width="100" />
          <el-table-column label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="getRoleType(row.role)">
                {{ getRoleLabel(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="加入时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.joined_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="changeRole(row)">修改角色</el-button>
              <el-popconfirm
                title="确定要移除此成员吗？"
                @confirm="removeMember(row.user_id)"
              >
                <template #reference>
                  <el-button size="small" type="danger">移除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- Add Member Dialog -->
    <el-dialog
      v-model="showAddMemberDialog"
      title="添加成员"
      width="400px"
    >
      <el-form
        ref="memberFormRef"
        :model="memberForm"
        :rules="memberFormRules"
        label-width="80px"
      >
        <el-form-item label="用户ID" prop="user_id">
          <el-input-number v-model="memberForm.user_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="memberForm.role" style="width: 100%">
            <el-option label="所有者" value="owner" />
            <el-option label="管理员" value="admin" />
            <el-option label="成员" value="member" />
            <el-option label="查看者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddMemberDialog = false">取消</el-button>
        <el-button type="primary" @click="submitMember" :loading="submitting">添加</el-button>
      </template>
    </el-dialog>

    <!-- Change Role Dialog -->
    <el-dialog
      v-model="showChangeRoleDialog"
      title="修改角色"
      width="400px"
    >
      <el-form label-width="80px">
        <el-form-item label="用户ID">
          <el-input v-model="roleChangeForm.user_id" disabled />
        </el-form-item>
        <el-form-item label="新角色">
          <el-select v-model="roleChangeForm.role" style="width: 100%">
            <el-option label="所有者" value="owner" />
            <el-option label="管理员" value="admin" />
            <el-option label="成员" value="member" />
            <el-option label="查看者" value="viewer" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showChangeRoleDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRoleChange" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Plus, Search, UserFilled, Avatar, StarFilled
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// State
const route = useRoute()
const loading = ref(false)
const loadingMembers = ref(false)
const submitting = ref(false)
const showCreateTeamDialog = ref(false)
const showViewDialog = ref(false)
const showMembersDialog = ref(false)
const showAddMemberDialog = ref(false)
const showChangeRoleDialog = ref(false)
const isEditingTeam = ref(false)

const organizations = ref([])
const selectedOrgId = ref(null)
const teams = ref([])
const selectedTeam = ref(null)
const teamMembers = ref([])
const searchQuery = ref('')

const statistics = reactive({
  totalTeams: 0,
  totalMembers: 0,
  defaultTeams: 0
})

const teamForm = reactive({
  name: '',
  description: '',
  is_default: false
})

const memberForm = reactive({
  user_id: null,
  role: 'member'
})

const roleChangeForm = reactive({
  user_id: null,
  role: ''
})

const teamFormRef = ref(null)
const memberFormRef = ref(null)

const teamFormRules = {
  name: [
    { required: true, message: '请输入团队名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ]
}

const memberFormRules = {
  user_id: [
    { required: true, message: '请输入用户ID', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// Computed
const filteredTeams = computed(() => {
  if (!searchQuery.value) return teams.value

  const query = searchQuery.value.toLowerCase()
  return teams.value.filter(team =>
    team.name.toLowerCase().includes(query) ||
    (team.description && team.description.toLowerCase().includes(query))
  )
})

// Methods
const loadOrganizations = async () => {
  try {
    const response = await api.get('/organizations')
    organizations.value = response.data

    // Auto-select from query param if available
    if (route.query.org_id) {
      selectedOrgId.value = parseInt(route.query.org_id)
      await loadTeams()
    }
  } catch (error) {
    ElMessage.error('加载组织列表失败: ' + error.message)
  }
}

const loadTeams = async () => {
  if (!selectedOrgId.value) return

  loading.value = true
  try {
    const response = await api.get('/teams', {
      params: { organization_id: selectedOrgId.value }
    })
    teams.value = response.data

    // Load member counts for each team
    for (const team of teams.value) {
      team.memberCount = 0  // TODO: Load actual member count
    }

    updateStatistics()
  } catch (error) {
    ElMessage.error('加载团队列表失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const updateStatistics = () => {
  statistics.totalTeams = teams.value.length
  statistics.totalMembers = teams.value.reduce((sum, t) => sum + (t.memberCount || 0), 0)
  statistics.defaultTeams = teams.value.filter(t => t.is_default).length
}

const viewTeam = (team) => {
  selectedTeam.value = team
  showViewDialog.value = true
}

const editTeam = (team) => {
  isEditingTeam.value = true
  Object.assign(teamForm, {
    id: team.id,
    name: team.name,
    description: team.description || '',
    is_default: team.is_default
  })
  showCreateTeamDialog.value = true
}

const submitTeam = async () => {
  if (!teamFormRef.value) return

  await teamFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditingTeam.value) {
        await api.put(`/teams/${teamForm.id}`, {
          name: teamForm.name,
          description: teamForm.description,
          is_default: teamForm.is_default
        })
        ElMessage.success('团队更新成功')
      } else {
        await api.post('/teams', {
          organization_id: selectedOrgId.value,
          name: teamForm.name,
          description: teamForm.description,
          is_default: teamForm.is_default
        })
        ElMessage.success('团队创建成功')
      }

      showCreateTeamDialog.value = false
      resetTeamForm()
      await loadTeams()
    } catch (error) {
      ElMessage.error(isEditingTeam.value ? '更新失败: ' + error.message : '创建失败: ' + error.message)
    } finally {
      submitting.value = false
    }
  })
}

const deleteTeam = async (id) => {
  try {
    await api.delete(`/teams/${id}`)
    ElMessage.success('团队删除成功')
    await loadTeams()
  } catch (error) {
    ElMessage.error('删除失败: ' + error.message)
  }
}

const manageMembers = async (team) => {
  selectedTeam.value = team
  showMembersDialog.value = true
  await loadTeamMembers(team.id)
}

const loadTeamMembers = async (teamId) => {
  loadingMembers.value = true
  try {
    // TODO: Implement team members endpoint
    // const response = await api.get(`/teams/${teamId}/members`)
    // teamMembers.value = response.data
    teamMembers.value = []  // Placeholder
  } catch (error) {
    ElMessage.error('加载成员列表失败: ' + error.message)
  } finally {
    loadingMembers.value = false
  }
}

const submitMember = async () => {
  if (!memberFormRef.value) return

  await memberFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      await api.post(`/teams/${selectedTeam.value.id}/members`, {
        user_id: memberForm.user_id,
        role: memberForm.role
      })
      ElMessage.success('成员添加成功')
      showAddMemberDialog.value = false
      resetMemberForm()
      await loadTeamMembers(selectedTeam.value.id)
    } catch (error) {
      ElMessage.error('添加失败: ' + error.message)
    } finally {
      submitting.value = false
    }
  })
}

const removeMember = async (userId) => {
  try {
    await api.delete(`/teams/${selectedTeam.value.id}/members/${userId}`)
    ElMessage.success('成员移除成功')
    await loadTeamMembers(selectedTeam.value.id)
  } catch (error) {
    ElMessage.error('移除失败: ' + error.message)
  }
}

const changeRole = (member) => {
  roleChangeForm.user_id = member.user_id
  roleChangeForm.role = member.role
  showChangeRoleDialog.value = true
}

const submitRoleChange = async () => {
  submitting.value = true
  try {
    await api.put(`/teams/${selectedTeam.value.id}/members/${roleChangeForm.user_id}/role`, {
      role: roleChangeForm.role
    })
    ElMessage.success('角色修改成功')
    showChangeRoleDialog.value = false
    await loadTeamMembers(selectedTeam.value.id)
  } catch (error) {
    ElMessage.error('修改失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const resetTeamForm = () => {
  Object.assign(teamForm, {
    name: '',
    description: '',
    is_default: false
  })
  isEditingTeam.value = false
  if (teamFormRef.value) {
    teamFormRef.value.resetFields()
  }
}

const resetMemberForm = () => {
  Object.assign(memberForm, {
    user_id: null,
    role: 'member'
  })
  if (memberFormRef.value) {
    memberFormRef.value.resetFields()
  }
}

const getOrganizationName = (orgId) => {
  const org = organizations.value.find(o => o.id === orgId)
  return org ? org.name : '-'
}

const getRoleType = (role) => {
  const types = {
    owner: 'danger',
    admin: 'warning',
    member: 'success',
    viewer: 'info'
  }
  return types[role] || ''
}

const getRoleLabel = (role) => {
  const labels = {
    owner: '所有者',
    admin: '管理员',
    member: '成员',
    viewer: '查看者'
  }
  return labels[role] || role
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
.team-management {
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

      .header-actions {
        display: flex;
        align-items: center;
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

  .table-card {
    .team-info {
      .team-name {
        font-weight: 500;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
      }

      .team-desc {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .empty-state {
    margin-top: 40px;
  }

  .members-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      margin: 0;
    }
  }

  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}
</style>
