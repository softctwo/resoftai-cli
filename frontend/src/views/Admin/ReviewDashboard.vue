<template>
  <div class="review-dashboard">
    <PageHeader title="Review Dashboard" subtitle="Manage plugin and template submissions">
      <template #actions>
        <el-badge :value="pendingCount" type="warning" :hidden="pendingCount === 0">
          <el-button icon="Bell">
            Pending Reviews
          </el-button>
        </el-badge>
      </template>
    </PageHeader>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #ecf5ff; color: #409eff">
              <el-icon :size="24"><Files /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">Pending Plugins</div>
              <div class="stat-value">{{ stats.pending_plugins }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f0f9ff; color: #67c23a">
              <el-icon :size="24"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">Pending Templates</div>
              <div class="stat-value">{{ stats.pending_templates }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #fef0f0; color: #f56c6c">
              <el-icon :size="24"><Check /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">Approved Today</div>
              <div class="stat-value">{{ todayApproved }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f4f4f5; color: #909399">
              <el-icon :size="24"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">Contributors</div>
              <div class="stat-value">{{ stats.total_contributors }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Tabs for different review queues -->
    <el-tabs v-model="activeTab" class="review-tabs">
      <el-tab-pane label="Pending Plugins" name="plugins">
        <ReviewQueue
          type="plugin"
          :items="pendingPlugins"
          :loading="loadingPlugins"
          @approve="handleApprove"
          @reject="handleReject"
          @refresh="loadPendingPlugins"
        />
      </el-tab-pane>

      <el-tab-pane label="Pending Templates" name="templates">
        <ReviewQueue
          type="template"
          :items="pendingTemplates"
          :loading="loadingTemplates"
          @approve="handleApprove"
          @reject="handleReject"
          @refresh="loadPendingTemplates"
        />
      </el-tab-pane>

      <el-tab-pane label="Recently Approved" name="approved">
        <RecentlyReviewed
          :items="recentlyApproved"
          @feature="handleFeature"
        />
      </el-tab-pane>

      <el-tab-pane label="Rejected" name="rejected">
        <RecentlyReviewed
          :items="rejected"
          status="rejected"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- Approve Dialog -->
    <ApproveDialog
      v-model="showApproveDialog"
      :item="selectedItem"
      @confirm="confirmApprove"
    />

    <!-- Reject Dialog -->
    <RejectDialog
      v-model="showRejectDialog"
      :item="selectedItem"
      @confirm="confirmReject"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/marketplace/admin'
import PageHeader from '@/components/PageHeader.vue'
import ReviewQueue from './components/ReviewQueue.vue'
import RecentlyReviewed from './components/RecentlyReviewed.vue'
import ApproveDialog from './components/ApproveDialog.vue'
import RejectDialog from './components/RejectDialog.vue'
import type { ReviewItem, ReviewStats } from '@/types/api'

type Stats = ReviewStats

const activeTab = ref('plugins')
const stats = ref<Stats>({
  pending_plugins: 0,
  pending_templates: 0,
  approved_plugins: 0,
  approved_templates: 0,
  rejected_plugins: 0,
  rejected_templates: 0,
  total_contributors: 0,
  total_downloads: 0,
  total_installs: 0
})

const loadingPlugins = ref(false)
const loadingTemplates = ref(false)
const pendingPlugins = ref<ReviewItem[]>([])
const pendingTemplates = ref<ReviewItem[]>([])
const recentlyApproved = ref<ReviewItem[]>([])
const rejected = ref<ReviewItem[]>([])

const showApproveDialog = ref(false)
const showRejectDialog = ref(false)
const selectedItem = ref<ReviewItem | null>(null)

const pendingCount = computed(() => {
  return stats.value.pending_plugins + stats.value.pending_templates
})

const todayApproved = computed(() => {
  // Filter approved items from today
  const today = new Date().toDateString()
  return recentlyApproved.value.filter(item => {
    return new Date(item.submitted_at).toDateString() === today
  }).length
})

onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadPendingPlugins(),
    loadPendingTemplates(),
    loadRecentlyApproved(),
    loadRejected()
  ])
})

async function loadStats() {
  try {
    const response = await adminApi.getStats()
    stats.value = response.data
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

async function loadPendingPlugins() {
  loadingPlugins.value = true
  try {
    const response = await adminApi.getPendingPlugins()
    pendingPlugins.value = response.data
  } catch (error) {
    ElMessage.error('Failed to load pending plugins')
  } finally {
    loadingPlugins.value = false
  }
}

async function loadPendingTemplates() {
  loadingTemplates.value = true
  try {
    const response = await adminApi.getPendingTemplates()
    pendingTemplates.value = response.data
  } catch (error) {
    ElMessage.error('Failed to load pending templates')
  } finally {
    loadingTemplates.value = false
  }
}

async function loadRecentlyApproved() {
  try {
    // Load recently approved items
    const [plugins, templates] = await Promise.all([
      adminApi.getAllPlugins({ status: 'approved', limit: 20 }),
      adminApi.getAllTemplates({ status: 'approved', limit: 20 })
    ])
    recentlyApproved.value = [...plugins.data, ...templates.data]
      .sort((a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime())
      .slice(0, 20)
  } catch (error) {
    console.error('Error loading approved items:', error)
  }
}

async function loadRejected() {
  try {
    const [plugins, templates] = await Promise.all([
      adminApi.getAllPlugins({ status: 'rejected', limit: 20 }),
      adminApi.getAllTemplates({ status: 'rejected', limit: 20 })
    ])
    rejected.value = [...plugins.data, ...templates.data]
      .sort((a, b) => new Date(b.submitted_at).getTime() - new Date(a.submitted_at).getTime())
      .slice(0, 20)
  } catch (error) {
    console.error('Error loading rejected items:', error)
  }
}

function handleApprove(item: ReviewItem, type: 'plugin' | 'template') {
  selectedItem.value = { ...item, type }
  showApproveDialog.value = true
}

function handleReject(item: ReviewItem, type: 'plugin' | 'template') {
  selectedItem.value = { ...item, type }
  showRejectDialog.value = true
}

async function confirmApprove(data: { is_featured: boolean }) {
  if (!selectedItem.value) return

  try {
    const type = selectedItem.value.type
    const id = selectedItem.value.id

    if (type === 'plugin') {
      await adminApi.approvePlugin(id, {
        status: 'approved',
        is_featured: data.is_featured
      })
    } else {
      await adminApi.approveTemplate(id, {
        status: 'approved',
        is_featured: data.is_featured
      })
    }

    ElMessage.success(`${type} approved successfully!`)
    showApproveDialog.value = false
    selectedItem.value = null

    // Refresh data
    if (type === 'plugin') {
      await loadPendingPlugins()
    } else {
      await loadPendingTemplates()
    }
    await Promise.all([loadStats(), loadRecentlyApproved()])
  } catch (error) {
    ElMessage.error('Failed to approve item')
    console.error('Approval error:', error)
  }
}

async function confirmReject(data: { feedback: string }) {
  if (!selectedItem.value) return

  try {
    const type = selectedItem.value.type
    const id = selectedItem.value.id

    if (type === 'plugin') {
      await adminApi.rejectPlugin(id, {
        status: 'rejected',
        feedback: data.feedback
      })
    } else {
      await adminApi.rejectTemplate(id, {
        status: 'rejected',
        feedback: data.feedback
      })
    }

    ElMessage.success(`${type} rejected with feedback sent to author`)
    showRejectDialog.value = false
    selectedItem.value = null

    // Refresh data
    if (type === 'plugin') {
      await loadPendingPlugins()
    } else {
      await loadPendingTemplates()
    }
    await Promise.all([loadStats(), loadRejected()])
  } catch (error) {
    ElMessage.error('Failed to reject item')
    console.error('Rejection error:', error)
  }
}

async function handleFeature(item: ReviewItem, type: 'plugin' | 'template') {
  try {
    await ElMessageBox.confirm(
      `Feature this ${type}? It will be highlighted in the marketplace.`,
      'Feature Item',
      {
        confirmButtonText: 'Feature',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
    )

    if (type === 'plugin') {
      await adminApi.featurePlugin(item.id, true)
    } else {
      await adminApi.featureTemplate(item.id, true)
    }

    ElMessage.success(`${type} is now featured!`)
    await loadRecentlyApproved()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to feature item')
    }
  }
}
</script>

<style scoped lang="scss">
.review-dashboard {
  .stats-row {
    margin-bottom: 24px;

    .stat-card {
      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .stat-info {
          flex: 1;

          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin-bottom: 4px;
          }

          .stat-value {
            font-size: 24px;
            font-weight: 600;
            color: var(--el-text-color-primary);
          }
        }
      }
    }
  }

  .review-tabs {
    background: var(--el-bg-color);
    padding: 20px;
    border-radius: 8px;
  }
}
</style>
