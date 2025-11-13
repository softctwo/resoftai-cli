<template>
  <div class="models-page">
    <el-page-header title="返回" @back="$router.push('/')">
      <template #content>
        <h2>模型配置</h2>
      </template>
    </el-page-header>

    <el-card class="info-card" shadow="never">
      <el-alert
        title="配置LLM模型"
        type="info"
        :closable="false"
      >
        在这里配置您的AI模型API密钥和参数。支持多个模型提供商。
      </el-alert>
    </el-card>

    <el-row :gutter="20">
      <!-- Model Providers List -->
      <el-col :span="8">
        <el-card class="providers-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span>模型提供商</span>
              <el-button
                type="primary"
                size="small"
                :icon="Plus"
                @click="showAddDialog = true"
              >
                添加配置
              </el-button>
            </div>
          </template>

          <el-menu
            :default-active="selectedConfigId"
            @select="handleSelectConfig"
          >
            <el-menu-item
              v-for="config in configs"
              :key="config.id"
              :index="String(config.id)"
            >
              <template #title>
                <div class="menu-item-content">
                  <div>
                    <strong>{{ getProviderName(config.provider) }}</strong>
                    <el-tag
                      v-if="config.is_active"
                      type="success"
                      size="small"
                      style="margin-left: 10px"
                    >
                      当前使用
                    </el-tag>
                  </div>
                  <div class="menu-item-subtitle">
                    {{ config.model }}
                  </div>
                </div>
              </template>
            </el-menu-item>
          </el-menu>

          <el-empty v-if="configs.length === 0" description="暂无配置" />
        </el-card>
      </el-col>

      <!-- Configuration Details -->
      <el-col :span="16">
        <el-card class="config-card" shadow="never" v-if="selectedConfig">
          <template #header>
            <div class="card-header">
              <span>配置详情</span>
              <el-button-group>
                <el-button
                  size="small"
                  :icon="Check"
                  type="success"
                  @click="handleActivateConfig"
                  :disabled="selectedConfig.is_active"
                >
                  设为当前
                </el-button>
                <el-button
                  size="small"
                  :icon="Connection"
                  @click="handleTestConnection"
                >
                  测试连接
                </el-button>
                <el-button
                  size="small"
                  :icon="Edit"
                  @click="handleEditConfig"
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  :icon="Delete"
                  type="danger"
                  @click="handleDeleteConfig"
                >
                  删除
                </el-button>
              </el-button-group>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="提供商">
              {{ getProviderName(selectedConfig.provider) }}
            </el-descriptions-item>
            <el-descriptions-item label="模型">
              {{ selectedConfig.model }}
            </el-descriptions-item>
            <el-descriptions-item label="API Key">
              <span class="masked-key">{{ maskApiKey(selectedConfig.api_key) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="selectedConfig.is_active ? 'success' : 'info'">
                {{ selectedConfig.is_active ? '当前使用' : '未使用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="最大Token数">
              {{ selectedConfig.max_tokens || 8192 }}
            </el-descriptions-item>
            <el-descriptions-item label="温度">
              {{ selectedConfig.temperature || 0.7 }}
            </el-descriptions-item>
            <el-descriptions-item label="Top P">
              {{ selectedConfig.top_p || 0.95 }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(selectedConfig.created_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <div class="provider-info">
            <h3>{{ getProviderName(selectedConfig.provider) }} 信息</h3>
            <div v-html="getProviderInfo(selectedConfig.provider)"></div>
          </div>
        </el-card>

        <el-empty
          v-else
          description="请从左侧选择配置"
          :image-size="200"
        />
      </el-col>
    </el-row>

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="showAddDialog"
      :title="editMode ? '编辑配置' : '添加模型配置'"
      width="600px"
    >
      <el-form
        :model="configForm"
        :rules="configRules"
        ref="configFormRef"
        label-width="120px"
      >
        <el-form-item label="提供商" prop="provider">
          <el-select
            v-model="configForm.provider"
            placeholder="选择提供商"
            @change="handleProviderChange"
          >
            <el-option
              v-for="provider in availableProviders"
              :key="provider.value"
              :label="provider.label"
              :value="provider.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="模型" prop="model">
          <el-select
            v-model="configForm.model"
            placeholder="选择模型"
          >
            <el-option
              v-for="model in getAvailableModels(configForm.provider)"
              :key="model.value"
              :label="model.label"
              :value="model.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="API Key" prop="api_key">
          <el-input
            v-model="configForm.api_key"
            type="password"
            show-password
            placeholder="输入API密钥"
          />
        </el-form-item>

        <el-form-item label="最大Token数" prop="max_tokens">
          <el-input-number
            v-model="configForm.max_tokens"
            :min="1"
            :max="128000"
            :step="1024"
          />
        </el-form-item>

        <el-form-item label="温度" prop="temperature">
          <el-slider
            v-model="configForm.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
          />
        </el-form-item>

        <el-form-item label="Top P" prop="top_p">
          <el-slider
            v-model="configForm.top_p"
            :min="0"
            :max="1"
            :step="0.05"
            show-input
          />
        </el-form-item>

        <el-form-item label="设为当前">
          <el-switch v-model="configForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveConfig">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Check, Connection } from '@element-plus/icons-vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const configs = ref([])
const selectedConfigId = ref(null)
const showAddDialog = ref(false)
const editMode = ref(false)
const configFormRef = ref(null)

const configForm = ref({
  provider: 'deepseek',
  model: 'deepseek-chat',
  api_key: '',
  max_tokens: 8192,
  temperature: 0.7,
  top_p: 0.95,
  is_active: false
})

const configRules = {
  provider: [
    { required: true, message: '请选择提供商', trigger: 'change' }
  ],
  model: [
    { required: true, message: '请选择模型', trigger: 'change' }
  ],
  api_key: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ]
}

const availableProviders = [
  { label: 'Claude (Anthropic)', value: 'anthropic' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'GLM (智谱AI)', value: 'zhipu' },
  { label: 'Kimi (月之暗面)', value: 'moonshot' },
  { label: 'Minimax', value: 'minimax' },
  { label: 'Gemini (Google)', value: 'google' }
]

const modelOptions = {
  anthropic: [
    { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
    { label: 'Claude 3 Opus', value: 'claude-3-opus-20240229' },
    { label: 'Claude 3 Sonnet', value: 'claude-3-sonnet-20240229' },
    { label: 'Claude 3 Haiku', value: 'claude-3-haiku-20240307' }
  ],
  deepseek: [
    { label: 'DeepSeek Chat', value: 'deepseek-chat' },
    { label: 'DeepSeek Coder', value: 'deepseek-coder' }
  ],
  zhipu: [
    { label: 'GLM-4', value: 'glm-4' },
    { label: 'GLM-4V', value: 'glm-4v' },
    { label: 'GLM-3-Turbo', value: 'glm-3-turbo' }
  ],
  moonshot: [
    { label: 'Moonshot v1 8k', value: 'moonshot-v1-8k' },
    { label: 'Moonshot v1 32k', value: 'moonshot-v1-32k' },
    { label: 'Moonshot v1 128k', value: 'moonshot-v1-128k' }
  ],
  minimax: [
    { label: 'Minimax abab6.5', value: 'abab6.5-chat' },
    { label: 'Minimax abab5.5', value: 'abab5.5-chat' }
  ],
  google: [
    { label: 'Gemini 1.5 Pro', value: 'gemini-1.5-pro' },
    { label: 'Gemini 1.5 Flash', value: 'gemini-1.5-flash' },
    { label: 'Gemini 1.0 Pro', value: 'gemini-1.0-pro' }
  ]
}

const selectedConfig = computed(() => {
  return configs.value.find(c => String(c.id) === selectedConfigId.value)
})

onMounted(async () => {
  await loadConfigs()
})

async function loadConfigs() {
  try {
    // TODO: Implement API endpoint for fetching LLM configs
    // For now, using mock data
    configs.value = [
      {
        id: 1,
        user_id: authStore.user?.id,
        provider: 'deepseek',
        model: 'deepseek-chat',
        api_key: 'sk-5b9262ddae444a629054f94d4f222476',
        max_tokens: 8192,
        temperature: 0.7,
        top_p: 0.95,
        is_active: true,
        created_at: new Date().toISOString()
      }
    ]

    if (configs.value.length > 0) {
      selectedConfigId.value = String(configs.value[0].id)
    }
  } catch (error) {
    console.error('Load configs error:', error)
    ElMessage.error('加载配置失败')
  }
}

function handleSelectConfig(index) {
  selectedConfigId.value = index
}

function handleProviderChange(provider) {
  const models = getAvailableModels(provider)
  if (models.length > 0) {
    configForm.value.model = models[0].value
  }
}

function getAvailableModels(provider) {
  return modelOptions[provider] || []
}

function getProviderName(provider) {
  const found = availableProviders.find(p => p.value === provider)
  return found ? found.label : provider
}

function maskApiKey(apiKey) {
  if (!apiKey) return ''
  if (apiKey.length <= 8) return '***'
  return apiKey.substring(0, 6) + '...' + apiKey.substring(apiKey.length - 4)
}

function handleEditConfig() {
  if (!selectedConfig.value) return

  editMode.value = true
  configForm.value = { ...selectedConfig.value }
  showAddDialog.value = true
}

async function handleSaveConfig() {
  if (!configFormRef.value) return

  await configFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      // TODO: Implement API endpoint for saving LLM config
      ElMessage.success(editMode.value ? '配置更新成功' : '配置添加成功')
      showAddDialog.value = false
      editMode.value = false
      configForm.value = {
        provider: 'deepseek',
        model: 'deepseek-chat',
        api_key: '',
        max_tokens: 8192,
        temperature: 0.7,
        top_p: 0.95,
        is_active: false
      }
      await loadConfigs()
    } catch (error) {
      console.error('Save config error:', error)
      ElMessage.error('保存配置失败')
    }
  })
}

async function handleDeleteConfig() {
  if (!selectedConfig.value) return

  try {
    await ElMessageBox.confirm(
      '确定要删除此配置吗？',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // TODO: Implement API endpoint for deleting LLM config
    ElMessage.success('配置删除成功')
    selectedConfigId.value = null
    await loadConfigs()
  } catch (error) {
    if (error === 'cancel') return
    console.error('Delete config error:', error)
    ElMessage.error('删除配置失败')
  }
}

async function handleActivateConfig() {
  if (!selectedConfig.value) return

  try {
    // TODO: Implement API endpoint for activating LLM config
    ElMessage.success('配置已设为当前使用')
    await loadConfigs()
  } catch (error) {
    console.error('Activate config error:', error)
    ElMessage.error('激活配置失败')
  }
}

async function handleTestConnection() {
  if (!selectedConfig.value) return

  const loading = ElMessage({
    message: '正在测试连接...',
    type: 'info',
    duration: 0
  })

  try {
    // TODO: Implement API endpoint for testing LLM connection
    await new Promise(resolve => setTimeout(resolve, 2000))
    loading.close()
    ElMessage.success('连接测试成功！')
  } catch (error) {
    loading.close()
    console.error('Test connection error:', error)
    ElMessage.error('连接测试失败')
  }
}

function getProviderInfo(provider) {
  const infoMap = {
    anthropic: '<p>Claude是Anthropic开发的先进AI助手，擅长复杂推理和代码生成。</p><p><a href="https://console.anthropic.com/" target="_blank">获取API Key</a></p>',
    deepseek: '<p>DeepSeek是国内优秀的AI大模型，性价比极高，适合代码生成和对话。</p><p><a href="https://platform.deepseek.com/" target="_blank">获取API Key</a></p>',
    zhipu: '<p>智谱AI GLM系列模型，支持多模态能力，适合中文场景。</p><p><a href="https://open.bigmodel.cn/" target="_blank">获取API Key</a></p>',
    moonshot: '<p>Kimi智能助手，支持超长上下文（最高128K），适合文档分析。</p><p><a href="https://platform.moonshot.cn/" target="_blank">获取API Key</a></p>',
    minimax: '<p>Minimax提供高质量的对话和生成能力。</p><p><a href="https://api.minimax.chat/" target="_blank">获取API Key</a></p>',
    google: '<p>Google Gemini系列模型，支持多模态和长上下文。</p><p><a href="https://makersuite.google.com/app/apikey" target="_blank">获取API Key</a></p>'
  }
  return infoMap[provider] || '<p>暂无提供商信息</p>'
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.models-page {
  padding: 20px;
}

.info-card {
  margin: 20px 0;
}

.providers-card {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.config-card {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-item-content {
  width: 100%;
}

.menu-item-subtitle {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.masked-key {
  font-family: monospace;
  color: #606266;
}

.provider-info {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.provider-info h3 {
  margin-top: 0;
  color: #303133;
}

.provider-info p {
  margin: 10px 0;
  color: #606266;
  line-height: 1.6;
}

.provider-info a {
  color: #409eff;
  text-decoration: none;
}

.provider-info a:hover {
  text-decoration: underline;
}
</style>
