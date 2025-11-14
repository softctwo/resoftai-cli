<template>
  <div class="template-marketplace">
    <!-- Header -->
    <el-page-header @back="goBack" class="page-header">
      <template #content>
        <div class="header-content">
          <h1>Template Marketplace</h1>
          <p>Browse and apply project templates to kickstart your development</p>
        </div>
      </template>
      <template #extra>
        <el-button type="primary" @click="refreshTemplates" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </template>
    </el-page-header>

    <!-- Filters -->
    <el-card class="filter-card" shadow="never">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-select
            v-model="filters.category"
            placeholder="Filter by category"
            clearable
            @change="applyFilters"
            style="width: 100%"
          >
            <el-option label="All Categories" value="" />
            <el-option label="Web Application" value="web_app" />
            <el-option label="REST API" value="rest_api" />
            <el-option label="CLI Tool" value="cli_tool" />
            <el-option label="Microservice" value="microservice" />
            <el-option label="Data Pipeline" value="data_pipeline" />
            <el-option label="ML Project" value="ml_project" />
            <el-option label="Mobile App" value="mobile_app" />
            <el-option label="Desktop App" value="desktop_app" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select
            v-model="filters.tags"
            placeholder="Filter by tags"
            multiple
            clearable
            @change="applyFilters"
            style="width: 100%"
          >
            <el-option label="Python" value="python" />
            <el-option label="JavaScript" value="javascript" />
            <el-option label="TypeScript" value="typescript" />
            <el-option label="FastAPI" value="fastapi" />
            <el-option label="Docker" value="docker" />
            <el-option label="Kubernetes" value="kubernetes" />
            <el-option label="Airflow" value="airflow" />
            <el-option label="ML" value="ml" />
            <el-option label="REST" value="rest" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="Search templates..."
            clearable
            @input="applyFilters"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
      </el-row>
    </el-card>

    <!-- Template Grid -->
    <el-row :gutter="20" class="template-grid" v-loading="loading">
      <el-col
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
        v-for="template in filteredTemplates"
        :key="template.id"
      >
        <el-card class="template-card" shadow="hover" @click="showTemplateDetails(template)">
          <template #header>
            <div class="card-header">
              <span class="template-name">{{ template.name }}</span>
              <el-tag :type="getCategoryType(template.category)" size="small">
                {{ formatCategory(template.category) }}
              </el-tag>
            </div>
          </template>

          <div class="template-description">{{ template.description }}</div>

          <div class="template-meta">
            <div class="meta-item">
              <el-icon><Document /></el-icon>
              <span>{{ template.file_count }} files</span>
            </div>
            <div class="meta-item">
              <el-icon><Folder /></el-icon>
              <span>{{ template.directory_count }} dirs</span>
            </div>
          </div>

          <div class="template-tags">
            <el-tag
              v-for="tag in template.tags"
              :key="tag"
              size="small"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>

          <div class="template-footer">
            <el-button type="primary" size="small" @click.stop="showApplyDialog(template)">
              <el-icon><Plus /></el-icon>
              Apply
            </el-button>
            <el-button size="small" @click.stop="showTemplateDetails(template)">
              <el-icon><View /></el-icon>
              Preview
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Empty State -->
    <el-empty
      v-if="!loading && filteredTemplates.length === 0"
      description="No templates found"
    />

    <!-- Template Details Dialog -->
    <el-dialog
      v-model="detailsDialogVisible"
      :title="selectedTemplate?.name"
      width="60%"
      :close-on-click-modal="false"
    >
      <div v-if="templatePreview" class="template-details">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryType(templatePreview.category)">
              {{ formatCategory(templatePreview.category) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Version">
            {{ templatePreview.version }}
          </el-descriptions-item>
          <el-descriptions-item label="Author">
            {{ templatePreview.author }}
          </el-descriptions-item>
          <el-descriptions-item label="Files">
            {{ templatePreview.file_count }} files, {{ templatePreview.directory_count }} directories
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">Description</el-divider>
        <p>{{ templatePreview.description }}</p>

        <el-divider content-position="left">Tags</el-divider>
        <div class="template-tags">
          <el-tag v-for="tag in templatePreview.tags" :key="tag" size="small">
            {{ tag }}
          </el-tag>
        </div>

        <el-divider content-position="left">Variables</el-divider>
        <el-table :data="templatePreview.variables" stripe>
          <el-table-column prop="name" label="Name" width="150" />
          <el-table-column prop="description" label="Description" />
          <el-table-column prop="type" label="Type" width="100" />
          <el-table-column prop="required" label="Required" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.required ? 'danger' : 'info'" size="small">
                {{ scope.row.required ? 'Yes' : 'No' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="default" label="Default" width="150" />
        </el-table>

        <el-divider content-position="left">File Structure</el-divider>
        <el-tree
          :data="fileTreeData"
          :props="{ label: 'name', children: 'children' }"
          node-key="id"
          default-expand-all
        >
          <template #default="{ node, data }">
            <span class="tree-node">
              <el-icon v-if="data.type === 'directory'"><Folder /></el-icon>
              <el-icon v-else><Document /></el-icon>
              <span>{{ node.label }}</span>
            </span>
          </template>
        </el-tree>

        <el-divider content-position="left">Setup Commands</el-divider>
        <el-tag
          v-for="(cmd, index) in templatePreview.setup_commands"
          :key="index"
          type="info"
          class="command-tag"
        >
          <code>{{ cmd }}</code>
        </el-tag>

        <el-divider content-position="left">Requirements</el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="(value, key) in templatePreview.requirements"
            :key="key"
            :label="key"
          >
            {{ value }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">Dependencies</el-divider>
        <div class="dependencies">
          <el-tag
            v-for="dep in templatePreview.dependencies"
            :key="dep"
            type="success"
            size="small"
          >
            {{ dep }}
          </el-tag>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="showApplyDialogFromPreview">
          <el-icon><Plus /></el-icon>
          Apply Template
        </el-button>
      </template>
    </el-dialog>

    <!-- Apply Template Dialog -->
    <el-dialog
      v-model="applyDialogVisible"
      title="Apply Template"
      width="50%"
      :close-on-click-modal="false"
    >
      <el-form
        ref="applyFormRef"
        :model="applyForm"
        :rules="applyFormRules"
        label-width="150px"
      >
        <el-form-item label="Template">
          <el-input :value="selectedTemplate?.name" disabled />
        </el-form-item>

        <el-form-item label="Output Directory" prop="output_dir">
          <el-input
            v-model="applyForm.output_dir"
            placeholder="/path/to/project"
          >
            <template #prepend>
              <el-icon><FolderOpened /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-divider content-position="left">Template Variables</el-divider>

        <el-form-item
          v-for="variable in selectedTemplate?.variables"
          :key="variable.name"
          :label="variable.description"
          :prop="`variables.${variable.name}`"
          :required="variable.required"
        >
          <!-- String/Integer input -->
          <el-input
            v-if="variable.type === 'string' || variable.type === 'integer'"
            v-model="applyForm.variables[variable.name]"
            :placeholder="variable.default || `Enter ${variable.name}`"
            :type="variable.type === 'integer' ? 'number' : 'text'"
          />

          <!-- Boolean switch -->
          <el-switch
            v-else-if="variable.type === 'boolean'"
            v-model="applyForm.variables[variable.name]"
            :active-value="true"
            :inactive-value="false"
          />

          <!-- Choice select -->
          <el-select
            v-else-if="variable.type === 'choice'"
            v-model="applyForm.variables[variable.name]"
            :placeholder="`Select ${variable.name}`"
          >
            <el-option
              v-for="choice in variable.choices"
              :key="choice"
              :label="choice"
              :value="choice"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Overwrite Existing" prop="overwrite">
          <el-switch v-model="applyForm.overwrite" />
          <span class="form-hint">
            Overwrite files if output directory already exists
          </span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="applyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="applyTemplate" :loading="applying">
          <el-icon><Check /></el-icon>
          Apply Template
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  Refresh,
  Search,
  Document,
  Folder,
  Plus,
  View,
  FolderOpened,
  Check
} from '@element-plus/icons-vue'
import {
  getTemplates,
  getTemplatePreview,
  applyTemplate as applyTemplateApi
} from '@/api/templates'

// State
const loading = ref(false)
const applying = ref(false)
const templates = ref([])
const selectedTemplate = ref(null)
const templatePreview = ref(null)
const detailsDialogVisible = ref(false)
const applyDialogVisible = ref(false)
const applyFormRef = ref(null)

// Filters
const filters = reactive({
  category: '',
  tags: []
})
const searchQuery = ref('')

// Apply form
const applyForm = reactive({
  output_dir: '',
  variables: {},
  overwrite: false
})

const applyFormRules = {
  output_dir: [
    { required: true, message: 'Please enter output directory', trigger: 'blur' }
  ]
}

// Computed
const filteredTemplates = computed(() => {
  let result = templates.value

  // Filter by category
  if (filters.category) {
    result = result.filter(t => t.category === filters.category)
  }

  // Filter by tags
  if (filters.tags.length > 0) {
    result = result.filter(t =>
      filters.tags.some(tag => t.tags.includes(tag))
    )
  }

  // Search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.name.toLowerCase().includes(query) ||
      t.description.toLowerCase().includes(query)
    )
  }

  return result
})

const fileTreeData = computed(() => {
  if (!templatePreview.value) return []

  const tree = []
  const dirMap = new Map()

  // Add directories
  templatePreview.value.directories.forEach((dir, index) => {
    const parts = dir.split('/')
    let currentPath = ''
    let currentLevel = tree

    parts.forEach((part, i) => {
      currentPath = currentPath ? `${currentPath}/${part}` : part

      if (!dirMap.has(currentPath)) {
        const node = {
          id: `dir-${currentPath}`,
          name: part,
          type: 'directory',
          children: []
        }
        dirMap.set(currentPath, node)
        currentLevel.push(node)
        currentLevel = node.children
      } else {
        currentLevel = dirMap.get(currentPath).children
      }
    })
  })

  // Add files
  templatePreview.value.files.forEach((file, index) => {
    const parts = file.path.split('/')
    const fileName = parts.pop()
    const dirPath = parts.join('/')

    let targetChildren = tree
    if (dirPath && dirMap.has(dirPath)) {
      targetChildren = dirMap.get(dirPath).children
    }

    targetChildren.push({
      id: `file-${index}`,
      name: fileName,
      type: 'file'
    })
  })

  return tree
})

// Methods
const fetchTemplates = async () => {
  loading.value = true
  try {
    const response = await getTemplates({
      category: filters.category || undefined,
      tags: filters.tags.length > 0 ? filters.tags.join(',') : undefined
    })
    templates.value = response.data.templates
  } catch (error) {
    ElMessage.error('Failed to fetch templates: ' + error.message)
  } finally {
    loading.value = false
  }
}

const refreshTemplates = () => {
  fetchTemplates()
}

const applyFilters = () => {
  // Filters are reactive, computed property will update automatically
}

const showTemplateDetails = async (template) => {
  selectedTemplate.value = template
  detailsDialogVisible.value = true

  // Fetch preview
  try {
    const response = await getTemplatePreview(template.id)
    templatePreview.value = response.data
  } catch (error) {
    ElMessage.error('Failed to fetch template preview: ' + error.message)
  }
}

const showApplyDialog = (template) => {
  selectedTemplate.value = template

  // Initialize form variables
  applyForm.variables = {}
  template.variables.forEach(variable => {
    applyForm.variables[variable.name] = variable.default || ''
  })

  applyDialogVisible.value = true
}

const showApplyDialogFromPreview = () => {
  detailsDialogVisible.value = false
  showApplyDialog(selectedTemplate.value)
}

const applyTemplate = async () => {
  // Validate form
  if (!applyFormRef.value) return

  try {
    await applyFormRef.value.validate()
  } catch (error) {
    return
  }

  applying.value = true
  try {
    const response = await applyTemplateApi({
      template_id: selectedTemplate.value.id,
      output_dir: applyForm.output_dir,
      variables: applyForm.variables,
      overwrite: applyForm.overwrite
    })

    ElNotification({
      title: 'Success',
      message: `Template "${selectedTemplate.value.name}" applied successfully!`,
      type: 'success',
      duration: 5000
    })

    applyDialogVisible.value = false

    // Reset form
    applyForm.output_dir = ''
    applyForm.variables = {}
    applyForm.overwrite = false
  } catch (error) {
    ElMessage.error('Failed to apply template: ' + error.message)
  } finally {
    applying.value = false
  }
}

const getCategoryType = (category) => {
  const typeMap = {
    web_app: 'primary',
    rest_api: 'success',
    cli_tool: 'info',
    microservice: 'warning',
    data_pipeline: 'danger',
    ml_project: '',
    mobile_app: 'primary',
    desktop_app: 'info'
  }
  return typeMap[category] || ''
}

const formatCategory = (category) => {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

const goBack = () => {
  window.history.back()
}

// Lifecycle
onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.template-marketplace {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-content p {
  margin: 5px 0 0 0;
  color: #909399;
  font-size: 14px;
}

.filter-card {
  margin-bottom: 20px;
}

.template-grid {
  margin-top: 20px;
}

.template-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.template-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.template-name {
  font-weight: 600;
  font-size: 16px;
}

.template-description {
  margin-bottom: 15px;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
  min-height: 60px;
}

.template-meta {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #909399;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 15px;
  min-height: 30px;
}

.template-footer {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

.template-details {
  max-height: 600px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 5px;
}

.command-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.command-tag code {
  font-family: 'Courier New', monospace;
}

.dependencies {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.form-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>
