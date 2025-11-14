<template>
  <el-card class="template-card" shadow="hover" @click="$emit('click')">
    <div class="template-card-header">
      <div class="template-card-badges">
        <el-tag v-if="template.is_official" type="success" size="small">Official</el-tag>
        <el-tag v-if="template.is_featured" type="warning" size="small">Featured</el-tag>
      </div>
      <div class="template-card-category">
        <el-tag size="small" effect="plain">{{ formatCategory(template.category) }}</el-tag>
      </div>
    </div>

    <div class="template-card-content">
      <h3 class="template-card-title">{{ template.name }}</h3>
      <p class="template-card-description">{{ template.description }}</p>

      <div class="template-card-meta">
        <div class="template-card-author">
          <el-icon><User /></el-icon>
          <span>{{ template.author_name }}</span>
        </div>
        <div class="template-card-stats">
          <div class="stat-item">
            <el-icon><Download /></el-icon>
            <span>{{ formatNumber(template.downloads_count) }}</span>
          </div>
          <div class="stat-item">
            <el-icon><Star /></el-icon>
            <span>{{ template.rating_average.toFixed(1) }} ({{ template.rating_count }})</span>
          </div>
        </div>
      </div>

      <div v-if="template.tags && template.tags.length" class="template-card-tags">
        <el-tag
          v-for="tag in template.tags.slice(0, 3)"
          :key="tag"
          size="small"
          type="info"
          effect="plain"
        >
          {{ tag }}
        </el-tag>
        <span v-if="template.tags.length > 3" class="more-tags">
          +{{ template.tags.length - 3 }}
        </span>
      </div>
    </div>

    <div class="template-card-footer">
      <div class="template-card-version">v{{ template.version }}</div>
      <el-button type="primary" size="small" @click.stop="$emit('install', template)">
        Use Template
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { User, Download, Star } from '@element-plus/icons-vue'
import { formatNumber } from '@/utils/format'
import type { Template } from '@/types/api'

defineProps<{
  template: Template
}>()

defineEmits<{
  (e: 'click'): void
  (e: 'install', template: Template): void
}>()

function formatCategory(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>

<style scoped lang="scss">
.template-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  &-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
  }

  &-badges {
    display: flex;
    gap: 4px;
  }

  &-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  &-title {
    margin: 0 0 8px;
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    line-height: 1.3;
  }

  &-description {
    margin: 0 0 12px;
    font-size: 14px;
    color: var(--el-text-color-secondary);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    flex: 1;
  }

  &-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  &-author {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  &-stats {
    display: flex;
    gap: 12px;

    .stat-item {
      display: flex;
      align-items: center;
      gap: 4px;
    }
  }

  &-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 12px;

    .more-tags {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      padding: 0 4px;
    }
  }

  &-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid var(--el-border-color);
  }

  &-version {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    font-family: monospace;
  }
}
</style>
