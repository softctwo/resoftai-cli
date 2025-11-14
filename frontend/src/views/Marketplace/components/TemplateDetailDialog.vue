<template>
  <el-dialog
    v-model="dialogVisible"
    :title="template?.name || 'Template Details'"
    width="800px"
    @close="handleClose"
  >
    <div v-loading="loading" class="template-detail">
      <div v-if="template" class="detail-content">
        <!-- Header -->
        <div class="detail-header">
          <div class="detail-badges">
            <el-tag v-if="template.is_official" type="success">Official</el-tag>
            <el-tag v-if="template.is_featured" type="warning">Featured</el-tag>
            <el-tag>{{ formatCategory(template.category) }}</el-tag>
          </div>
          <div class="detail-stats">
            <div class="stat">
              <el-icon><Download /></el-icon>
              <span>{{ formatNumber(template.downloads_count) }} downloads</span>
            </div>
            <div class="stat">
              <el-icon><Star /></el-icon>
              <span>{{ template.rating_average.toFixed(1) }} ({{ template.rating_count }} reviews)</span>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="detail-section">
          <h3>Description</h3>
          <p>{{ template.description }}</p>
        </div>

        <!-- Metadata -->
        <div class="detail-section">
          <h3>Details</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Version">v{{ template.version }}</el-descriptions-item>
            <el-descriptions-item label="Author">{{ template.author_name }}</el-descriptions-item>
            <el-descriptions-item label="Created">
              {{ formatDate(template.created_at, 'short') }}
            </el-descriptions-item>
            <el-descriptions-item label="Updated">
              {{ formatDate(template.updated_at, 'short') }}
            </el-descriptions-item>
            <el-descriptions-item v-if="template.license" label="License" :span="2">
              {{ template.license }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Tags -->
        <div v-if="template.tags && template.tags.length" class="detail-section">
          <h3>Tags</h3>
          <div class="tags-list">
            <el-tag v-for="tag in template.tags" :key="tag" type="info">
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <!-- Links -->
        <div class="detail-section">
          <h3>Links</h3>
          <div class="links-list">
            <el-link
              v-if="template.documentation_url"
              :href="template.documentation_url"
              type="primary"
              target="_blank"
            >
              <el-icon><Document /></el-icon>
              Documentation
            </el-link>
            <el-link
              v-if="template.source_url"
              :href="template.source_url"
              type="primary"
              target="_blank"
            >
              <el-icon><Link /></el-icon>
              Source Code
            </el-link>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">Close</el-button>
      <el-button type="primary" @click="handleInstall">
        Use This Template
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Star, Document, Link } from '@element-plus/icons-vue'
import { templateApi } from '@/api/marketplace'
import { formatNumber, formatDate } from '@/utils/format'
import type { TemplateDetail } from '@/types/api'

const props = defineProps<{
  modelValue: boolean
  templateId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'install', template: TemplateDetail): void
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const template = ref<TemplateDetail | null>(null)

watch(() => props.templateId, (id) => {
  if (id && props.modelValue) {
    loadTemplate(id)
  }
})

watch(() => props.modelValue, (visible) => {
  if (visible && props.templateId) {
    loadTemplate(props.templateId)
  }
})

async function loadTemplate(id: number) {
  loading.value = true
  try {
    const response = await templateApi.getTemplate(id)
    template.value = response.data
  } catch (error) {
    ElMessage.error('Failed to load template details')
    handleClose()
  } finally {
    loading.value = false
  }
}

function formatCategory(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function handleClose() {
  emit('update:modelValue', false)
}

function handleInstall() {
  if (template.value) {
    emit('install', template.value)
  }
}
</script>

<style scoped lang="scss">
.template-detail {
  .detail-content {
    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--el-border-color);
    }

    .detail-badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .detail-stats {
      display: flex;
      gap: 16px;
      font-size: 14px;
      color: var(--el-text-color-secondary);

      .stat {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }

    .detail-section {
      margin-bottom: 24px;

      h3 {
        margin: 0 0 12px;
        font-size: 16px;
        font-weight: 600;
        color: var(--el-text-color-primary);
      }

      p {
        margin: 0;
        line-height: 1.6;
        color: var(--el-text-color-regular);
      }
    }

    .tags-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .links-list {
      display: flex;
      gap: 16px;
    }
  }
}
</style>
