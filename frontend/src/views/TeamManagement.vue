<template>
  <div class="team-management">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>团队管理</h2>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          创建团队
        </el-button>
      </template>
    </el-page-header>

    <!-- Team List -->
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="team in teams" :key="team.id">
        <el-card shadow="hover" class="team-card">
          <template #header>
            <div class="card-header">
              <div class="team-info">
                <el-avatar :size="40" :icon="Team">
                  <template v-if="team.avatar">
                    <img :src="team.avatar" alt="team" />
                  </template>
                </el-avatar>
                <div class="team-title">
                  <h3>{{ team.name }}</h3>
                  <el-tag size="small">{{ team.organization_name }}</el-tag>
                </div>
              </div>
              <el-dropdown trigger="click">
                <el-icon class="more-icon"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :icon="Edit" @click="editTeam(team)">
                      编辑
                    </el-dropdown-item>
                    <el-dropdown-item :icon="Delete" @click="deleteTeam(team)" divided>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>

          <div class="team-description">
            {{ team.description || '暂无描述' }}
          </div>

          <el-divider />

          <div class="team-members">
            <div class="members-header">
              <span class="members-title">团队成员 ({{ team.members?.length || 0 }})</span>
              <el-button size="small" :icon="Plus" link @click="addMember(team)">
                添加
              </el-button>
            </div>
            <el-avatar-group :max="5" class="avatar-group">
              <el-avatar
                v-for="member in team.members"
                :key="member.id"
                :src="member.avatar"
                :size="32"
              >
                <template v-if="!member.avatar">
                  {{ member.username?.charAt(0).toUpperCase() }}
                </template>
              </el-avatar>
            </el-avatar-group>
          </div>

          <el-divider />

          <div class="team-stats">
            <div class="stat-item">
              <el-icon><FolderOpened /></el-icon>
              <span>{{ team.project_count || 0 }} 项目</span>
            </div>
            <div class="stat-item">
              <el-icon><Document /></el-icon>
              <span>{{ team.task_count || 0 }} 任务</span>
            </div>
            <div class="stat-item">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDate(team.created_at) }}</span>
            </div>
          </div>

          <el-divider />

          <div class="team-actions">
            <el-button size="small" :icon="View" @click="viewTeamDetail(team)">
              查看详情
            </el-button>
            <el-button size="small" :icon="Setting" @click="configureTeam(team)">
              设置
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="teams.length === 0 && !loading" description="暂无团队" />

    <!-- Create/Edit Team Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTeam ? '编辑团队' : '创建团队'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="teamForm" :rules="teamRules" ref="teamFormRef" label-width="100px">
        <el-form-item label="所属组织" prop="organization_id">
          <el-select v-model="teamForm.organization_id" placeholder="请选择组织" style="width: 100%">
            <el-option
              v-for="org in organizations"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="团队名称" prop="name">
          <el-input v-model="teamForm.name" placeholder="请输入团队名称" />
        </el-form-item>
        <el-form-item label="团队描述" prop="description">
          <el-input
            v-model="teamForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入团队描述"
          />
        </el-form-item>
        <el-form-item label="团队权限" prop="permissions">
          <el-checkbox-group v-model="teamForm.permissions">
            <el-checkbox label="create_project">创建项目</el-checkbox>
            <el-checkbox label="manage_files">管理文件</el-checkbox>
            <el-checkbox label="execute_workflow">执行工作流</el-checkbox>
            <el-checkbox label="manage_members">管理成员</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveTeam" :loading="saving">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- Team Detail Dialog -->
    <el-dialog v-model="showDetailDialog" title="团队详情" width="900px">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="成员" name="members">
          <div class="members-toolbar">
            <el-button :icon="Plus" @click="showAddMemberDialog = true">添加成员</el-button>
          </div>
          <el-table :data="currentTeamMembers" style="width: 100%">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-select v-model="row.role" size="small" @change="updateMemberRole(row)">
                  <el-option label="成员" value="member" />
                  <el-option label="负责人" value="lead" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="joined_at" label="加入时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.joined_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Delete" @click="removeMember(row)" type="danger" link>
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="项目" name="projects">
          <div class="projects-toolbar">
            <el-button :icon="Plus" @click="assignProject">分配项目</el-button>
          </div>
          <el-table :data="currentTeamProjects" style="width: 100%">
            <el-table-column prop="name" label="项目名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getProjectStatusType(row.status)">
                  {{ getProjectStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.progress" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column prop="assigned_at" label="分配时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.assigned_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="View" @click="viewProject(row)" link>
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="活动" name="activities">
          <el-timeline>
            <el-timeline-item
              v-for="activity in currentTeamActivities"
              :key="activity.id"
              :timestamp="formatDate(activity.created_at)"
              :type="getActivityType(activity.type)"
            >
              <div class="activity-content">
                <strong>{{ activity.user_name }}</strong>
                {{ activity.action }}
                <span class="activity-target">{{ activity.target }}</span>
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <el-tab-pane label="设置" name="settings">
          <el-form label-width="120px">
            <el-form-item label="团队可见性">
              <el-radio-group v-model="teamSettings.visibility">
                <el-radio label="private">私有</el-radio>
                <el-radio label="organization">组织内可见</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="允许成员邀请">
              <el-switch v-model="teamSettings.allow_member_invite" />
            </el-form-item>
            <el-form-item label="项目创建权限">
              <el-switch v-model="teamSettings.allow_create_project" />
            </el-form-item>
            <el-form-item label="通知设置">
              <el-checkbox-group v-model="teamSettings.notifications">
                <el-checkbox label="project_update">项目更新</el-checkbox>
                <el-checkbox label="member_change">成员变更</el-checkbox>
                <el-checkbox label="task_assigned">任务分配</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveTeamSettings">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
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
  View,
  Team,
  FolderOpened,
  Document,
  Clock,
  MoreFilled
} from '@element-plus/icons-vue'

// State
const loading = ref(false)
const saving = ref(false)
const teams = ref([])
const organizations = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showAddMemberDialog = ref(false)
const activeTab = ref('members')

const editingTeam = ref(null)
const currentTeam = ref(null)
const currentTeamMembers = ref([])
const currentTeamProjects = ref([])
const currentTeamActivities = ref([])

const teamFormRef = ref(null)
const teamForm = ref({
  organization_id: null,
  name: '',
  description: '',
  permissions: []
})

const teamSettings = ref({
  visibility: 'private',
  allow_member_invite: false,
  allow_create_project: true,
  notifications: []
})

const teamRules = {
  organization_id: [{ required: true, message: '请选择所属组织', trigger: 'change' }],
  name: [{ required: true, message: '请输入团队名称', trigger: 'blur' }]
}

// Fetch teams
const fetchTeams = async () => {
  loading.value = true
  try {
    // TODO: Replace with actual API call
    // const response = await teamAPI.getTeams()

    // Mock data
    teams.value = [
      {
        id: 1,
        name: '前端开发团队',
        organization_name: 'ResoftAI',
        description: '负责前端界面开发和用户体验优化',
        project_count: 5,
        task_count: 23,
        created_at: new Date(),
        members: [
          { id: 1, username: 'user1', avatar: '' },
          { id: 2, username: 'user2', avatar: '' },
          { id: 3, username: 'user3', avatar: '' }
        ]
      },
      {
        id: 2,
        name: '后端开发团队',
        organization_name: 'ResoftAI',
        description: '负责后端API开发和系统架构',
        project_count: 8,
        task_count: 45,
        created_at: new Date(),
        members: [
          { id: 4, username: 'user4', avatar: '' },
          { id: 5, username: 'user5', avatar: '' }
        ]
      }
    ]

    organizations.value = [
      { id: 1, name: 'ResoftAI' },
      { id: 2, name: '企业客户A' }
    ]
  } catch (error) {
    ElMessage.error('加载团队列表失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// Save team
const saveTeam = async () => {
  if (!teamFormRef.value) return

  try {
    await teamFormRef.value.validate()
    saving.value = true

    // TODO: API call

    ElMessage.success(editingTeam.value ? '团队更新成功' : '团队创建成功')
    showCreateDialog.value = false
    fetchTeams()
  } catch (error) {
    if (error !== false) {
      ElMessage.error('操作失败：' + error.message)
    }
  } finally {
    saving.value = false
  }
}

// View team detail
const viewTeamDetail = (team) => {
  currentTeam.value = team
  // Mock members
  currentTeamMembers.value = [
    {
      id: 1,
      username: 'developer1',
      email: 'dev1@resoftai.com',
      role: 'lead',
      joined_at: new Date()
    },
    {
      id: 2,
      username: 'developer2',
      email: 'dev2@resoftai.com',
      role: 'member',
      joined_at: new Date()
    }
  ]
  // Mock projects
  currentTeamProjects.value = [
    {
      id: 1,
      name: '项目A',
      status: 'in_progress',
      progress: 65,
      assigned_at: new Date()
    },
    {
      id: 2,
      name: '项目B',
      status: 'completed',
      progress: 100,
      assigned_at: new Date()
    }
  ]
  // Mock activities
  currentTeamActivities.value = [
    {
      id: 1,
      type: 'member_join',
      user_name: 'developer1',
      action: '加入了团队',
      target: '',
      created_at: new Date()
    }
  ]
  showDetailDialog.value = true
}

// Edit team
const editTeam = (team) => {
  editingTeam.value = team
  teamForm.value = { ...team }
  showCreateDialog.value = true
}

// Delete team
const deleteTeam = (team) => {
  ElMessageBox.confirm(
    `确定要删除团队"${team.name}"吗？此操作不可恢复。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      // TODO: API call
      ElMessage.success('团队已删除')
      fetchTeams()
    } catch (error) {
      ElMessage.error('删除失败：' + error.message)
    }
  })
}

// Helper functions
const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const getProjectStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return typeMap[status] || 'info'
}

const getProjectStatusText = (status) => {
  const textMap = {
    pending: '待开始',
    in_progress: '进行中',
    completed: '已完成'
  }
  return textMap[status] || status
}

const getActivityType = (type) => {
  const typeMap = {
    member_join: 'success',
    member_leave: 'warning',
    project_assign: 'primary'
  }
  return typeMap[type] || 'info'
}

const resetForm = () => {
  editingTeam.value = null
  teamForm.value = {
    organization_id: null,
    name: '',
    description: '',
    permissions: []
  }
}

const addMember = (team) => {
  ElMessage.info('添加成员功能开发中...')
}

const updateMemberRole = (member) => {
  ElMessage.success('角色已更新')
}

const removeMember = (member) => {
  ElMessage.info('移除成员功能开发中...')
}

const assignProject = () => {
  ElMessage.info('分配项目功能开发中...')
}

const viewProject = (project) => {
  ElMessage.info('查看项目详情功能开发中...')
}

const configureTeam = (team) => {
  viewTeamDetail(team)
  activeTab.value = 'settings'
}

const saveTeamSettings = () => {
  ElMessage.success('设置已保存')
}

// Lifecycle
onMounted(() => {
  fetchTeams()
})
</script>

<style scoped lang="scss">
.team-management {
  padding: 20px;

  .el-page-header {
    margin-bottom: 20px;
  }

  .team-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .team-info {
        display: flex;
        gap: 12px;
        flex: 1;

        .team-title {
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

    .team-description {
      color: #606266;
      font-size: 14px;
      line-height: 1.6;
      min-height: 40px;
    }

    .team-members {
      .members-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .members-title {
          font-weight: 500;
          color: #606266;
        }
      }

      .avatar-group {
        display: flex;
        gap: 8px;
      }
    }

    .team-stats {
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

    .team-actions {
      display: flex;
      gap: 10px;

      .el-button {
        flex: 1;
      }
    }
  }

  .members-toolbar,
  .projects-toolbar {
    margin-bottom: 16px;
  }

  .activity-content {
    .activity-target {
      color: #409EFF;
      font-weight: 500;
    }
  }
}
</style>
