<template>
  <div class="code-quality-report">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span>代码质量报告</span>
          <el-tag v-if="report" :type="getScoreType(report.quality_score)" size="large">
            质量得分: {{ report.quality_score }}/100
          </el-tag>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="!report" class="empty-container">
        <el-empty description="暂无质量报告">
          <el-button type="primary" @click="$emit('check-quality')">
            开始质量检查
          </el-button>
        </el-empty>
      </div>

      <div v-else class="report-content">
        <!-- Quality Score -->
        <div class="score-section">
          <el-progress
            :percentage="report.quality_score"
            :color="getScoreColor(report.quality_score)"
            :width="120"
            type="circle"
          >
            <template #default="{ percentage }">
              <span class="percentage-value">{{ percentage }}</span>
              <span class="percentage-label">分</span>
            </template>
          </el-progress>

          <div class="score-details">
            <div class="detail-item">
              <span class="label">语言:</span>
              <el-tag>{{ report.language }}</el-tag>
            </div>
            <div class="detail-item">
              <span class="label">总行数:</span>
              <span>{{ report.total_lines }}</span>
            </div>
            <div class="detail-item">
              <span class="label">问题数:</span>
              <span>{{ report.issues_count }}</span>
            </div>
          </div>
        </div>

        <!-- Issue Summary -->
        <el-divider />
        <div class="issues-summary">
          <h3>问题统计</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="严重问题" :value="report.critical_issues">
                <template #prefix>
                  <el-icon color="#F56C6C"><CircleCloseFilled /></el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="错误" :value="report.error_issues">
                <template #prefix>
                  <el-icon color="#E6A23C"><WarningFilled /></el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="警告" :value="report.warning_issues">
                <template #prefix>
                  <el-icon color="#409EFF"><InfoFilled /></el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic title="代码行" :value="report.metrics.code_lines || 0">
                <template #prefix>
                  <el-icon><DocumentCopy /></el-icon>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

        <!-- Metrics -->
        <el-divider />
        <div class="metrics-section" v-if="report.metrics">
          <h3>代码指标</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="注释行数">
              {{ report.metrics.comment_lines || 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="注释率">
              {{ (report.metrics.comment_ratio * 100).toFixed(1) }}%
            </el-descriptions-item>
            <el-descriptions-item label="问题密度">
              {{ report.metrics.issue_density?.toFixed(2) || 0 }} 问题/行
            </el-descriptions-item>
            <el-descriptions-item label="质量等级">
              <el-tag :type="getScoreType(report.quality_score)">
                {{ getQualityGrade(report.quality_score) }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Issues List -->
        <el-divider />
        <div class="issues-list" v-if="report.issues && report.issues.length > 0">
          <h3>问题详情 ({{ report.issues.length }})</h3>

          <el-table :data="paginatedIssues" stripe style="width: 100%">
            <el-table-column label="级别" width="100">
              <template #default="{ row }">
                <el-tag :type="getIssueType(row.level)" size="small">
                  {{ getIssueLabel(row.level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="line" label="行号" width="80" />
            <el-table-column prop="message" label="问题描述" min-width="300" />
            <el-table-column prop="suggestion" label="建议修复" min-width="250" />
            <el-table-column prop="rule_id" label="规则ID" width="150" />
          </el-table>

          <el-pagination
            v-if="report.issues.length > pageSize"
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="report.issues.length"
            layout="prev, pager, next, total"
            style="margin-top: 20px; justify-content: center"
          />
        </div>

        <div v-else class="no-issues">
          <el-result icon="success" title="太棒了！" sub-title="没有发现代码质量问题" />
        </div>

        <!-- Actions -->
        <el-divider />
        <div class="actions">
          <el-button type="primary" @click="$emit('check-quality')" :icon="Refresh">
            重新检查
          </el-button>
          <el-button @click="exportReport" :icon="Download">
            导出报告
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  CircleCloseFilled,
  WarningFilled,
  InfoFilled,
  DocumentCopy,
  Refresh,
  Download
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  report: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['check-quality'])

// Pagination
const currentPage = ref(1)
const pageSize = ref(10)

const paginatedIssues = computed(() => {
  if (!props.report?.issues) return []
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return props.report.issues.slice(start, end)
})

// Helper functions
function getScoreType(score) {
  if (score >= 90) return 'success'
  if (score >= 70) return 'warning'
  return 'danger'
}

function getScoreColor(score) {
  if (score >= 90) return '#67C23A'
  if (score >= 70) return '#E6A23C'
  return '#F56C6C'
}

function getQualityGrade(score) {
  if (score >= 95) return 'A+'
  if (score >= 90) return 'A'
  if (score >= 85) return 'B+'
  if (score >= 80) return 'B'
  if (score >= 70) return 'C'
  if (score >= 60) return 'D'
  return 'F'
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

function getIssueLabel(level) {
  const labels = {
    critical: '严重',
    error: '错误',
    warning: '警告',
    info: '信息'
  }
  return labels[level] || level
}

function exportReport() {
  if (!props.report) {
    ElMessage.warning('暂无报告可导出')
    return
  }

  const reportText = `代码质量报告
================

文件名: ${props.report.filename}
语言: ${props.report.language}
质量得分: ${props.report.quality_score}/100
总行数: ${props.report.total_lines}

问题统计:
- 严重问题: ${props.report.critical_issues}
- 错误: ${props.report.error_issues}
- 警告: ${props.report.warning_issues}
- 总计: ${props.report.issues_count}

代码指标:
- 代码行数: ${props.report.metrics.code_lines || 0}
- 注释行数: ${props.report.metrics.comment_lines || 0}
- 注释率: ${(props.report.metrics.comment_ratio * 100).toFixed(1)}%

问题详情:
${props.report.issues.map((issue, index) => `
${index + 1}. [${getIssueLabel(issue.level)}] 第${issue.line}行
   问题: ${issue.message}
   建议: ${issue.suggestion}
   规则: ${issue.rule_id}
`).join('\n')}
`

  const blob = new Blob([reportText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `code-quality-report-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('报告已导出')
}
</script>

<style scoped>
.code-quality-report {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container,
.empty-container {
  padding: 40px;
  text-align: center;
}

.report-content {
  padding: 20px 0;
}

.score-section {
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.percentage-value {
  font-size: 24px;
  font-weight: bold;
}

.percentage-label {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item .label {
  font-weight: 500;
  color: #606266;
  min-width: 60px;
}

.issues-summary,
.metrics-section,
.issues-list {
  margin-top: 20px;
}

.issues-summary h3,
.metrics-section h3,
.issues-list h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.no-issues {
  padding: 40px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding-top: 20px;
}
</style>
