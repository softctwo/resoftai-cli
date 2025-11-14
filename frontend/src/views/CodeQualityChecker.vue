<template>
  <div class="code-quality-checker">
    <el-page-header @back="$router.back()" content="代码质量检查器" />

    <el-row :gutter="20" class="main-content">
      <!-- Left: Code Editor -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>代码编辑器</span>
              <div class="header-actions">
                <el-select
                  v-model="language"
                  placeholder="选择语言"
                  style="width: 150px; margin-right: 10px"
                  @change="handleLanguageChange"
                >
                  <el-option label="Python" value="python" />
                  <el-option label="JavaScript" value="javascript" />
                  <el-option label="TypeScript" value="typescript" />
                </el-select>

                <el-upload
                  :show-file-list="false"
                  :before-upload="handleFileUpload"
                  accept=".py,.js,.ts,.jsx,.tsx"
                >
                  <el-button :icon="Upload" size="small">上传文件</el-button>
                </el-upload>
              </div>
            </div>
          </template>

          <!-- Monaco Editor -->
          <div class="editor-container">
            <monaco-editor
              v-model="code"
              :language="language"
              :height="500"
              @change="handleCodeChange"
            />
          </div>

          <!-- Action Buttons -->
          <div class="editor-actions">
            <el-button
              type="primary"
              :loading="checking"
              :icon="Check"
              @click="performQualityCheck"
              :disabled="!code.trim()"
            >
              {{ checking ? '检查中...' : '开始检查' }}
            </el-button>

            <el-button :icon="Delete" @click="clearCode">
              清空代码
            </el-button>

            <!-- Linter Selection -->
            <el-popover placement="bottom" :width="300" trigger="click">
              <template #reference>
                <el-button :icon="Setting">
                  配置 Linters
                </el-button>
              </template>
              <div class="linter-config">
                <h4>选择 Linters</h4>
                <el-checkbox-group v-model="selectedLinters">
                  <el-checkbox
                    v-for="linter in availableLinters"
                    :key="linter"
                    :label="linter"
                    :disabled="!linterStatus[linter]"
                  >
                    {{ linter }}
                    <el-tag
                      v-if="!linterStatus[linter]"
                      type="danger"
                      size="small"
                      style="margin-left: 5px"
                    >
                      未安装
                    </el-tag>
                  </el-checkbox>
                </el-checkbox-group>
              </div>
            </el-popover>
          </div>

          <!-- Code Stats -->
          <el-divider />
          <div class="code-stats">
            <el-statistic title="代码行数" :value="codeStats.lines" />
            <el-statistic title="字符数" :value="codeStats.characters" />
            <el-statistic title="字数" :value="codeStats.words" />
          </div>
        </el-card>
      </el-col>

      <!-- Right: Quality Report -->
      <el-col :span="12">
        <div v-if="!qualityResult && !checking" class="empty-state">
          <el-empty description="开始检查代码质量">
            <template #image>
              <el-icon :size="100" color="#909399">
                <DocumentChecked />
              </el-icon>
            </template>
            <p class="tip">
              在左侧输入或上传代码，然后点击"开始检查"按钮
            </p>
          </el-empty>
        </div>

        <el-card v-else shadow="never">
          <template #header>
            <div class="card-header">
              <span>质量检查结果</span>
              <el-tag v-if="qualityResult" :type="getScoreType(qualityResult.overall_score)" size="large">
                质量评分: {{ qualityResult.overall_score.toFixed(1) }}/100
              </el-tag>
            </div>
          </template>

          <div v-if="checking" class="loading-container">
            <el-skeleton :rows="8" animated />
            <p style="text-align: center; margin-top: 20px; color: #909399">
              正在分析代码...
            </p>
          </div>

          <div v-else-if="qualityResult" class="result-content">
            <!-- Overall Score -->
            <div class="score-section">
              <el-progress
                :percentage="Math.round(qualityResult.overall_score)"
                :color="getScoreColor(qualityResult.overall_score)"
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
                  <el-tag>{{ qualityResult.language }}</el-tag>
                </div>
                <div class="detail-item">
                  <span class="label">文件:</span>
                  <span>{{ qualityResult.file_path }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">总问题:</span>
                  <span class="issue-count">{{ qualityResult.total_issues }}</span>
                </div>
              </div>
            </div>

            <!-- Issue Summary -->
            <el-divider />
            <div class="issues-summary">
              <h3>问题统计</h3>
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-statistic title="错误" :value="qualityResult.errors">
                    <template #prefix>
                      <el-icon color="#F56C6C"><CircleCloseFilled /></el-icon>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="8">
                  <el-statistic title="警告" :value="qualityResult.warnings">
                    <template #prefix>
                      <el-icon color="#E6A23C"><WarningFilled /></el-icon>
                    </template>
                  </el-statistic>
                </el-col>
                <el-col :span="8">
                  <el-statistic title="信息" :value="qualityResult.info">
                    <template #prefix>
                      <el-icon color="#409EFF"><InfoFilled /></el-icon>
                    </template>
                  </el-statistic>
                </el-col>
              </el-row>
            </div>

            <!-- Linter Results -->
            <el-divider />
            <div class="linter-results">
              <h3>Linter 详细结果</h3>
              <el-collapse v-model="activeCollapse">
                <el-collapse-item
                  v-for="(result, index) in qualityResult.linter_results"
                  :key="index"
                  :name="result.linter"
                >
                  <template #title>
                    <div class="linter-title">
                      <el-tag :type="result.success ? 'success' : 'danger'">
                        {{ result.linter }}
                      </el-tag>
                      <span class="issue-badge">
                        {{ result.issues.length }} 个问题
                      </span>
                      <span class="exec-time">
                        执行时间: {{ result.execution_time.toFixed(2) }}s
                      </span>
                    </div>
                  </template>

                  <div v-if="!result.success" class="error-message">
                    <el-alert type="error" :closable="false">
                      {{ result.error_message }}
                    </el-alert>
                  </div>

                  <el-table v-else :data="result.issues" stripe style="width: 100%">
                    <el-table-column label="级别" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)" size="small">
                          {{ getSeverityLabel(row.severity) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="line" label="行" width="60" />
                    <el-table-column prop="column" label="列" width="60" />
                    <el-table-column prop="message" label="问题描述" min-width="250" />
                    <el-table-column prop="rule_id" label="规则ID" width="120" />
                  </el-table>

                  <div v-if="result.issues.length === 0" class="no-issues">
                    <el-result icon="success" title="太棒了！" sub-title="此 linter 未发现问题" />
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>

            <!-- Actions -->
            <el-divider />
            <div class="actions">
              <el-button type="primary" @click="exportReport" :icon="Download">
                导出报告
              </el-button>
              <el-button @click="shareReport" :icon="Share">
                分享结果
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Linter Health Status Drawer -->
    <el-drawer
      v-model="healthDrawerVisible"
      title="Linter 健康状态"
      size="400px"
    >
      <div v-if="linterHealth" class="health-status">
        <el-alert
          :type="linterHealth.status === 'healthy' ? 'success' : 'warning'"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #title>
            {{ linterHealth.message }}
          </template>
        </el-alert>

        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(available, tool) in linterHealth.tools"
            :key="tool"
            :label="tool"
          >
            <el-tag :type="available ? 'success' : 'danger'">
              {{ available ? '可用' : '不可用' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          v-if="linterHealth.status !== 'healthy'"
          type="info"
          :closable="false"
          style="margin-top: 20px"
        >
          <template #title>
            安装提示
          </template>
          <p>请在服务器上安装缺失的工具：</p>
          <pre class="install-command">pip install pylint mypy
npm install -g eslint</pre>
        </el-alert>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Upload,
  Check,
  Delete,
  Setting,
  Download,
  Share,
  DocumentChecked,
  CircleCloseFilled,
  WarningFilled,
  InfoFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MonacoEditor from '@/components/MonacoEditor.vue'
import { checkCodeQuality, getSupportedLinters, getHealthStatus } from '@/api/codeQuality'

// State
const code = ref(`# 输入或粘贴您的代码
def hello_world():
    print("Hello, World!")

hello_world()
`)

const language = ref('python')
const checking = ref(false)
const qualityResult = ref(null)
const selectedLinters = ref([])
const availableLinters = ref([])
const linterStatus = ref({})
const activeCollapse = ref([])
const healthDrawerVisible = ref(false)
const linterHealth = ref(null)

// Code stats
const codeStats = computed(() => {
  const text = code.value
  return {
    lines: text.split('\n').length,
    characters: text.length,
    words: text.split(/\s+/).filter(w => w.length > 0).length
  }
})

// Lifecycle
onMounted(async () => {
  await loadSupportedLinters()
  await checkLinterHealth()
})

// Methods
async function loadSupportedLinters() {
  try {
    const linters = await getSupportedLinters()
    availableLinters.value = linters[language.value] || []
    selectedLinters.value = [...availableLinters.value]
  } catch (error) {
    console.error('Failed to load linters:', error)
  }
}

async function checkLinterHealth() {
  try {
    linterHealth.value = await getHealthStatus()
    linterStatus.value = linterHealth.value.tools || {}

    if (linterHealth.value.status !== 'healthy') {
      ElMessage.warning('部分代码质量工具未安装')
    }
  } catch (error) {
    console.error('Failed to check linter health:', error)
  }
}

async function performQualityCheck() {
  if (!code.value.trim()) {
    ElMessage.warning('请输入代码')
    return
  }

  checking.value = true
  qualityResult.value = null

  try {
    const result = await checkCodeQuality({
      code: code.value,
      language: language.value,
      filename: `inline_code.${getFileExtension(language.value)}`,
      linters: selectedLinters.value.length > 0 ? selectedLinters.value : undefined
    })

    qualityResult.value = result
    activeCollapse.value = result.linter_results.map(r => r.linter)

    if (result.total_issues === 0) {
      ElMessage.success('代码质量检查通过，未发现问题！')
    } else {
      ElMessage.info(`发现 ${result.total_issues} 个问题`)
    }
  } catch (error) {
    console.error('Quality check failed:', error)
    ElMessage.error('代码质量检查失败')
  } finally {
    checking.value = false
  }
}

function handleLanguageChange() {
  loadSupportedLinters()
  // Update code template
  const templates = {
    python: '# Python 代码\ndef hello():\n    print("Hello, World!")\n\nhello()\n',
    javascript: '// JavaScript 代码\nfunction hello() {\n  console.log("Hello, World!");\n}\n\nhello();\n',
    typescript: '// TypeScript 代码\nfunction hello(): void {\n  console.log("Hello, World!");\n}\n\nhello();\n'
  }
  code.value = templates[language.value] || ''
}

function handleCodeChange(newCode) {
  code.value = newCode
}

function handleFileUpload(file) {
  const reader = new FileReader()
  reader.onload = (e) => {
    code.value = e.target.result

    // Auto-detect language
    const ext = file.name.split('.').pop().toLowerCase()
    const langMap = {
      'py': 'python',
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript'
    }
    if (langMap[ext]) {
      language.value = langMap[ext]
      loadSupportedLinters()
    }

    ElMessage.success('文件已加载')
  }
  reader.readAsText(file)
  return false // Prevent upload
}

function clearCode() {
  ElMessageBox.confirm('确定要清空代码吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    code.value = ''
    qualityResult.value = null
    ElMessage.success('已清空')
  }).catch(() => {})
}

function getFileExtension(lang) {
  const extensions = {
    python: 'py',
    javascript: 'js',
    typescript: 'ts'
  }
  return extensions[lang] || 'txt'
}

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

function getSeverityType(severity) {
  const types = {
    error: 'danger',
    warning: 'warning',
    info: 'info',
    convention: '',
    refactor: 'info'
  }
  return types[severity] || ''
}

function getSeverityLabel(severity) {
  const labels = {
    error: '错误',
    warning: '警告',
    info: '信息',
    convention: '规范',
    refactor: '重构'
  }
  return labels[severity] || severity
}

function exportReport() {
  if (!qualityResult.value) return

  const report = `代码质量检查报告
==================

文件: ${qualityResult.value.file_path}
语言: ${qualityResult.value.language}
质量评分: ${qualityResult.value.overall_score.toFixed(1)}/100

问题统计:
- 错误: ${qualityResult.value.errors}
- 警告: ${qualityResult.value.warnings}
- 信息: ${qualityResult.value.info}
- 总计: ${qualityResult.value.total_issues}

Linter 结果:
${qualityResult.value.linter_results.map(r => `
${r.linter}:
- 状态: ${r.success ? '成功' : '失败'}
- 问题数: ${r.issues.length}
- 执行时间: ${r.execution_time.toFixed(2)}s
${r.issues.map((issue, i) => `  ${i + 1}. [${getSeverityLabel(issue.severity)}] 第${issue.line}行:${issue.column}列 - ${issue.message}`).join('\n')}
`).join('\n')}
`

  const blob = new Blob([report], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `code-quality-report-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)

  ElMessage.success('报告已导出')
}

function shareReport() {
  if (!qualityResult.value) return

  const summary = `代码质量评分: ${qualityResult.value.overall_score.toFixed(1)}/100\n发现 ${qualityResult.value.total_issues} 个问题`

  ElMessageBox.alert(summary, '分享结果', {
    confirmButtonText: '复制到剪贴板',
    callback: () => {
      navigator.clipboard.writeText(summary)
      ElMessage.success('已复制到剪贴板')
    }
  })
}
</script>

<style scoped>
.code-quality-checker {
  padding: 20px;
}

.main-content {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.editor-container {
  margin: 20px 0;
}

.editor-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.linter-config h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.code-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.empty-state {
  height: 600px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state .tip {
  margin-top: 20px;
  color: #909399;
  font-size: 14px;
}

.loading-container {
  padding: 40px;
}

.result-content {
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
  min-width: 50px;
}

.issue-count {
  font-weight: 600;
  color: #F56C6C;
}

.issues-summary,
.linter-results {
  margin-top: 20px;
}

.issues-summary h3,
.linter-results h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.linter-title {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.issue-badge {
  color: #909399;
  font-size: 12px;
}

.exec-time {
  margin-left: auto;
  color: #909399;
  font-size: 12px;
}

.error-message {
  margin: 10px 0;
}

.no-issues {
  padding: 20px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  padding-top: 20px;
}

.health-status {
  padding: 20px;
}

.install-command {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  margin-top: 8px;
}
</style>
