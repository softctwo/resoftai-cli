<template>
  <div class="template-marketplace">
    <PageHeader title="Template Marketplace" subtitle="Discover and use community templates">
      <template #actions>
        <el-button type="primary" icon="Plus" @click="showPublishDialog">
          Publish Template
        </el-button>
      </template>
    </PageHeader>

    <!-- Search and Filters -->
    <div class="marketplace-filters">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-input
            v-model="searchQuery"
            placeholder="Search templates..."
            prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="categoryFilter" placeholder="Category" clearable @change="handleFilter">
            <el-option label="All Categories" value="" />
            <el-option label="Web App" value="web_app" />
            <el-option label="REST API" value="rest_api" />
            <el-option label="CLI Tool" value="cli_tool" />
            <el-option label="Microservice" value="microservice" />
            <el-option label="Data Pipeline" value="data_pipeline" />
            <el-option label="ML Project" value="ml_project" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="sortBy" placeholder="Sort By" @change="handleFilter">
            <el-option label="Most Recent" value="created_at" />
            <el-option label="Most Downloaded" value="downloads" />
            <el-option label="Highest Rated" value="rating" />
            <el-option label="Most Installed" value="installs" />
          </el-select>
        </el-col>
      </el-row>

      <!-- Quick Filters -->
      <div class="quick-filters">
        <el-checkbox v-model="filters.featured" @change="handleFilter">
          Featured Only
        </el-checkbox>
        <el-checkbox v-model="filters.official" @change="handleFilter">
          Official Only
        </el-checkbox>
      </div>
    </div>

    <!-- Template Grid -->
    <div v-loading="loading" class="template-grid">
      <el-empty v-if="!loading && templates.length === 0" description="No templates found" />

      <el-row :gutter="20">
        <el-col
          v-for="template in templates"
          :key="template.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <TemplateCard
            :template="template"
            @click="viewTemplate(template.id)"
            @install="handleInstall(template)"
          />
        </el-col>
      </el-row>

      <!-- Load More -->
      <div v-if="hasMore" class="load-more">
        <el-button @click="loadMore" :loading="loadingMore">
          Load More Templates
        </el-button>
      </div>
    </div>

    <!-- Template Detail Dialog -->
    <TemplateDetailDialog
      v-model="showDetail"
      :template-id="selectedTemplateId"
      @install="handleInstall"
    />

    <!-- Publish Dialog -->
    <PublishTemplateDialog
      v-model="showPublish"
      @published="handlePublished"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { templateApi } from '@/api/templates'
import PageHeader from '@/components/PageHeader.vue'
import TemplateCard from './components/TemplateCard.vue'
import TemplateDetailDialog from './components/TemplateDetailDialog.vue'
import PublishTemplateDialog from './components/PublishTemplateDialog.vue'

interface Template {
  id: number
  name: string
  slug: string
  category: string
  version: string
  description: string
  author_name: string
  is_official: boolean
  is_featured: boolean
  downloads_count: number
  installs_count: number
  rating_average: number
  rating_count: number
  tags: string[]
  created_at: string
}

const loading = ref(false)
const loadingMore = ref(false)
const templates = ref<Template[]>([])
const searchQuery = ref('')
const categoryFilter = ref('')
const sortBy = ref('created_at')
const filters = reactive({
  featured: false,
  official: false
})

const currentPage = ref(0)
const pageSize = 20
const hasMore = ref(true)

const showDetail = ref(false)
const selectedTemplateId = ref<number | null>(null)
const showPublish = ref(false)

onMounted(() => {
  loadTemplates()
})

async function loadTemplates(append = false) {
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    templates.value = []
    currentPage.value = 0
  }

  try {
    const response = await templateApi.listMarketplace({
      search: searchQuery.value || undefined,
      category: categoryFilter.value || undefined,
      is_featured: filters.featured || undefined,
      is_official: filters.official || undefined,
      sort_by: sortBy.value,
      skip: currentPage.value * pageSize,
      limit: pageSize
    })

    if (append) {
      templates.value.push(...response.data)
    } else {
      templates.value = response.data
    }

    hasMore.value = response.data.length === pageSize
    currentPage.value++
  } catch (error) {
    ElMessage.error('Failed to load templates')
    console.error('Error loading templates:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function handleSearch() {
  loadTemplates()
}

function handleFilter() {
  loadTemplates()
}

function loadMore() {
  loadTemplates(true)
}

function viewTemplate(id: number) {
  selectedTemplateId.value = id
  showDetail.value = true
}

async function handleInstall(template: Template) {
  // Navigate to template application page
  // or show installation dialog
  console.log('Install template:', template)
}

function showPublishDialog() {
  showPublish.value = true
}

function handlePublished() {
  ElMessage.success('Template published successfully! It will be reviewed by our team.')
  loadTemplates()
}
</script>

<style scoped lang="scss">
.template-marketplace {
  .marketplace-filters {
    margin-bottom: 24px;
    padding: 20px;
    background: var(--el-bg-color);
    border-radius: 8px;

    .quick-filters {
      margin-top: 16px;
      display: flex;
      gap: 20px;
    }
  }

  .template-grid {
    .load-more {
      display: flex;
      justify-content: center;
      margin-top: 32px;
    }
  }
}
</style>
