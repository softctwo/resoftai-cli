<template>
  <div class="quota-monitoring">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h2>配额监控</h2>
          <p class="subtitle">监控组织资源使用情况和配额限制</p>
        </div>
        <el-select
          v-model="selectedOrgId"
          placeholder="选择组织"
          @change="loadQuotas"
          style="width: 250px"
        >
          <el-option
            v-for="org in organizations"
            :key="org.id"
            :label="org.name"
            :value="org.id"
          />
        </el-select>
      </div>
    </el-card>

    <!-- Quota Cards -->
    <div v-if="selectedOrgId && !loading" class="quotas-container">
      <!-- Projects Quota -->
      <el-card class="quota-card">
        <div class="quota-header">
          <div class="quota-title">
            <el-icon :size="24" color="#409eff"><FolderOpened /></el-icon>
            <span>项目配额</span>
          </div>
          <el-tag :type="getQuotaStatus(quotas.projects)">
            {{ getStatusText(quotas.projects) }}
          </el-tag>
        </div>
        <div class="quota-content">
          <div class="usage-text">
            <span class="current">{{ quotas.projects.used || 0 }}</span>
            <span class="separator">/</span>
            <span class="limit">{{ quotas.projects.limit }}</span>
            <span class="unit">个项目</span>
          </div>
          <el-progress
            :percentage="getPercentage(quotas.projects)"
            :color="getProgressColor(quotas.projects)"
            :status="getPercentage(quotas.projects) >= 100 ? 'exception' : undefined"
          />
          <div class="quota-footer">
            <span>剩余: {{ quotas.projects.limit - (quotas.projects.used || 0) }}</span>
            <span v-if="quotas.projects.reset_at">
              重置: {{ formatDate(quotas.projects.reset_at) }}
            </span>
          </div>
        </div>
      </el-card>

      <!-- API Calls Quota -->
      <el-card class="quota-card">
        <div class="quota-header">
          <div class="quota-title">
            <el-icon :size="24" color="#67c23a"><Connection /></el-icon>
            <span>API调用配额</span>
          </div>
          <el-tag :type="getQuotaStatus(quotas.api_calls)">
            {{ getStatusText(quotas.api_calls) }}
          </el-tag>
        </div>
        <div class="quota-content">
          <div class="usage-text">
            <span class="current">{{ formatNumber(quotas.api_calls.used || 0) }}</span>
            <span class="separator">/</span>
            <span class="limit">{{ formatNumber(quotas.api_calls.limit) }}</span>
            <span class="unit">次</span>
          </div>
          <el-progress
            :percentage="getPercentage(quotas.api_calls)"
            :color="getProgressColor(quotas.api_calls)"
            :status="getPercentage(quotas.api_calls) >= 100 ? 'exception' : undefined"
          />
          <div class="quota-footer">
            <span>剩余: {{ formatNumber(quotas.api_calls.limit - (quotas.api_calls.used || 0)) }}</span>
            <span v-if="quotas.api_calls.reset_at">
              重置: {{ formatDate(quotas.api_calls.reset_at) }}
            </span>
          </div>
        </div>
      </el-card>

      <!-- Storage Quota -->
      <el-card class="quota-card">
        <div class="quota-header">
          <div class="quota-title">
            <el-icon :size="24" color="#e6a23c"><Files /></el-icon>
            <span>存储配额</span>
          </div>
          <el-tag :type="getQuotaStatus(quotas.storage)">
            {{ getStatusText(quotas.storage) }}
          </el-tag>
        </div>
        <div class="quota-content">
          <div class="usage-text">
            <span class="current">{{ formatBytes(quotas.storage.used || 0) }}</span>
            <span class="separator">/</span>
            <span class="limit">{{ formatBytes(quotas.storage.limit) }}</span>
          </div>
          <el-progress
            :percentage="getPercentage(quotas.storage)"
            :color="getProgressColor(quotas.storage)"
            :status="getPercentage(quotas.storage) >= 100 ? 'exception' : undefined"
          />
          <div class="quota-footer">
            <span>剩余: {{ formatBytes(quotas.storage.limit - (quotas.storage.used || 0)) }}</span>
            <span v-if="quotas.storage.reset_at">
              重置: {{ formatDate(quotas.storage.reset_at) }}
            </span>
          </div>
        </div>
      </el-card>

      <!-- Team Members Quota -->
      <el-card class="quota-card">
        <div class="quota-header">
          <div class="quota-title">
            <el-icon :size="24" color="#f56c6c"><UserFilled /></el-icon>
            <span>团队成员配额</span>
          </div>
          <el-tag :type="getQuotaStatus(quotas.team_members)">
            {{ getStatusText(quotas.team_members) }}
          </el-tag>
        </div>
        <div class="quota-content">
          <div class="usage-text">
            <span class="current">{{ quotas.team_members.used || 0 }}</span>
            <span class="separator">/</span>
            <span class="limit">{{ quotas.team_members.limit }}</span>
            <span class="unit">人</span>
          </div>
          <el-progress
            :percentage="getPercentage(quotas.team_members)"
            :color="getProgressColor(quotas.team_members)"
            :status="getPercentage(quotas.team_members) >= 100 ? 'exception' : undefined"
          />
          <div class="quota-footer">
            <span>剩余: {{ quotas.team_members.limit - (quotas.team_members.used || 0) }}</span>
          </div>
        </div>
      </el-card>

      <!-- LLM Tokens Quota -->
      <el-card class="quota-card">
        <div class="quota-header">
          <div class="quota-title">
            <el-icon :size="24" color="#9c27b0"><ChatDotRound /></el-icon>
            <span>LLM Token配额</span>
          </div>
          <el-tag :type="getQuotaStatus(quotas.llm_tokens)">
            {{ getStatusText(quotas.llm_tokens) }}
          </el-tag>
        </div>
        <div class="quota-content">
          <div class="usage-text">
            <span class="current">{{ formatNumber(quotas.llm_tokens.used || 0) }}</span>
            <span class="separator">/</span>
            <span class="limit">{{ formatNumber(quotas.llm_tokens.limit) }}</span>
            <span class="unit">tokens</span>
          </div>
          <el-progress
            :percentage="getPercentage(quotas.llm_tokens)"
            :color="getProgressColor(quotas.llm_tokens)"
            :status="getPercentage(quotas.llm_tokens) >= 100 ? 'exception' : undefined"
          />
          <div class="quota-footer">
            <span>剩余: {{ formatNumber(quotas.llm_tokens.limit - (quotas.llm_tokens.used || 0)) }}</span>
            <span v-if="quotas.llm_tokens.reset_at">
              重置: {{ formatDate(quotas.llm_tokens.reset_at) }}
            </span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Empty State -->
    <el-card v-if="!selectedOrgId" class="empty-state">
      <el-empty description="请先选择一个组织">
        <el-button type="primary" @click="$router.push('/organizations')">
          前往组织管理
        </el-button>
      </el-empty>
    </el-card>

    <!-- Alerts -->
    <el-card v-if="selectedOrgId && alerts.length > 0" class="alerts-card">
      <h3>配额告警</h3>
      <el-alert
        v-for="alert in alerts"
        :key="alert.id"
        :title="alert.title"
        :type="alert.type"
        :description="alert.description"
        :closable="false"
        show-icon
        style="margin-bottom: 10px"
      />
    </el-card>

    <!-- Usage History Chart -->
    <el-card v-if="selectedOrgId" class="chart-card">
      <h3>使用趋势</h3>
      <el-tabs v-model="activeTab" @tab-change="loadUsageHistory">
        <el-tab-pane label="项目" name="projects" />
        <el-tab-pane label="API调用" name="api_calls" />
        <el-tab-pane label="存储" name="storage" />
        <el-tab-pane label="LLM Tokens" name="llm_tokens" />
      </el-tabs>
      <div ref="chartContainer" style="width: 100%; height: 300px"></div>
    </el-card>

    <!-- Subscription Info -->
    <el-card v-if="selectedOrgId && organizationInfo" class="subscription-card">
      <h3>订阅信息</h3>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="当前套餐">
          <el-tag :type="getTierType(organizationInfo.tier)">
            {{ getTierLabel(organizationInfo.tier) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="organizationInfo.is_active ? 'success' : 'danger'">
            {{ organizationInfo.is_active ? '活跃' : '已停用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="试用到期" v-if="organizationInfo.trial_ends_at">
          {{ formatDate(organizationInfo.trial_ends_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="订阅到期" v-if="organizationInfo.subscription_ends_at">
          {{ formatDate(organizationInfo.subscription_ends_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="action-buttons">
        <el-button type="primary">升级套餐</el-button>
        <el-button>管理订阅</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  FolderOpened, Connection, Files, UserFilled, ChatDotRound
} from '@element-plus/icons-vue'
import api from '@/utils/api'

// State
const route = useRoute()
const loading = ref(false)
const organizations = ref([])
const selectedOrgId = ref(null)
const organizationInfo = ref(null)
const activeTab = ref('projects')
const chartContainer = ref(null)

const quotas = reactive({
  projects: { limit: 0, used: 0 },
  api_calls: { limit: 0, used: 0 },
  storage: { limit: 0, used: 0 },
  team_members: { limit: 0, used: 0 },
  llm_tokens: { limit: 0, used: 0 }
})

const alerts = ref([])

// Methods
const loadOrganizations = async () => {
  try {
    const response = await api.get('/organizations')
    organizations.value = response.data

    // Auto-select from query param if available
    if (route.query.org_id) {
      selectedOrgId.value = parseInt(route.query.org_id)
      await loadQuotas()
    }
  } catch (error) {
    ElMessage.error('加载组织列表失败: ' + error.message)
  }
}

const loadQuotas = async () => {
  if (!selectedOrgId.value) return

  loading.value = true
  try {
    // Load organization info
    const orgResponse = await api.get(`/organizations/${selectedOrgId.value}`)
    organizationInfo.value = orgResponse.data

    // TODO: Implement quota API endpoint
    // For now, using mock data based on tier
    const tierLimits = {
      free: {
        projects: 5,
        api_calls: 10000,
        storage: 1073741824, // 1GB
        team_members: 3,
        llm_tokens: 100000
      },
      starter: {
        projects: 20,
        api_calls: 100000,
        storage: 10737418240, // 10GB
        team_members: 10,
        llm_tokens: 1000000
      },
      professional: {
        projects: 100,
        api_calls: 1000000,
        storage: 107374182400, // 100GB
        team_members: 50,
        llm_tokens: 10000000
      },
      enterprise: {
        projects: -1, // Unlimited
        api_calls: -1,
        storage: -1,
        team_members: -1,
        llm_tokens: -1
      }
    }

    const tier = organizationInfo.value.tier
    const limits = tierLimits[tier] || tierLimits.free

    // Mock usage data (replace with actual API call)
    Object.assign(quotas, {
      projects: { limit: limits.projects, used: Math.floor(limits.projects * 0.6) },
      api_calls: { limit: limits.api_calls, used: Math.floor(limits.api_calls * 0.45) },
      storage: { limit: limits.storage, used: Math.floor(limits.storage * 0.75) },
      team_members: { limit: limits.team_members, used: Math.floor(limits.team_members * 0.8) },
      llm_tokens: { limit: limits.llm_tokens, used: Math.floor(limits.llm_tokens * 0.55) }
    })

    // Generate alerts
    generateAlerts()
  } catch (error) {
    ElMessage.error('加载配额信息失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const generateAlerts = () => {
  alerts.value = []

  Object.entries(quotas).forEach(([key, quota]) => {
    const percentage = getPercentage(quota)
    const resourceNames = {
      projects: '项目',
      api_calls: 'API调用',
      storage: '存储空间',
      team_members: '团队成员',
      llm_tokens: 'LLM Token'
    }

    if (percentage >= 90) {
      alerts.value.push({
        id: key,
        type: percentage >= 100 ? 'error' : 'warning',
        title: `${resourceNames[key]}配额${percentage >= 100 ? '已耗尽' : '即将耗尽'}`,
        description: `当前使用 ${percentage.toFixed(1)}%，请考虑升级套餐或清理资源`
      })
    }
  })
}

const loadUsageHistory = async (resourceType) => {
  // TODO: Implement usage history API and chart rendering
  console.log('Loading usage history for:', resourceType || activeTab.value)
}

const getPercentage = (quota) => {
  if (!quota.limit || quota.limit === -1) return 0
  return Math.min((quota.used / quota.limit) * 100, 100)
}

const getQuotaStatus = (quota) => {
  const percentage = getPercentage(quota)
  if (percentage >= 100) return 'danger'
  if (percentage >= 80) return 'warning'
  return 'success'
}

const getStatusText = (quota) => {
  const percentage = getPercentage(quota)
  if (percentage >= 100) return '已满'
  if (percentage >= 80) return '即将满'
  return '正常'
}

const getProgressColor = (quota) => {
  const percentage = getPercentage(quota)
  if (percentage >= 90) return '#f56c6c'
  if (percentage >= 75) return '#e6a23c'
  return '#67c23a'
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

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  if (bytes === -1) return '无限制'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// Lifecycle
onMounted(() => {
  loadOrganizations()
})

watch(selectedOrgId, () => {
  if (selectedOrgId.value) {
    loadUsageHistory()
  }
})
</script>

<style scoped lang="scss">
.quota-monitoring {
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

  .quotas-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 20px;

    .quota-card {
      .quota-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;

        .quota-title {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 16px;
          font-weight: 500;
        }
      }

      .quota-content {
        .usage-text {
          display: flex;
          align-items: baseline;
          gap: 8px;
          margin-bottom: 12px;
          font-size: 14px;

          .current {
            font-size: 28px;
            font-weight: bold;
            color: #303133;
          }

          .separator {
            font-size: 20px;
            color: #909399;
          }

          .limit {
            font-size: 18px;
            color: #606266;
          }

          .unit {
            color: #909399;
          }
        }

        .quota-footer {
          display: flex;
          justify-content: space-between;
          margin-top: 12px;
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .empty-state {
    margin-top: 40px;
  }

  .alerts-card {
    margin-bottom: 20px;

    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
    }
  }

  .chart-card {
    margin-bottom: 20px;

    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
    }
  }

  .subscription-card {
    h3 {
      margin: 0 0 16px 0;
      font-size: 18px;
    }

    .action-buttons {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      justify-content: center;
    }
  }
}
</style>
