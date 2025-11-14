<template>
  <div class="review-queue">
    <el-table
      v-loading="loading"
      :data="items"
      style="width: 100%"
      stripe
    >
      <el-table-column prop="name" label="Name" min-width="200">
        <template #default="{ row }">
          <div class="item-name">
            <strong>{{ row.name }}</strong>
            <el-tag size="small" effect="plain">v{{ row.version }}</el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="category" label="Category" width="150">
        <template #default="{ row }">
          <el-tag size="small">{{ formatCategory(row.category) }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="author_name" label="Author" width="150" />

      <el-table-column prop="description" label="Description" min-width="250" show-overflow-tooltip />

      <el-table-column prop="submitted_at" label="Submitted" width="120">
        <template #default="{ row }">
          {{ formatDate(row.submitted_at, 'relative') }}
        </template>
      </el-table-column>

      <el-table-column label="Actions" width="200" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="success"
              size="small"
              @click="$emit('approve', row, type)"
            >
              Approve
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="$emit('reject', row, type)"
            >
              Reject
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { formatDate } from '@/utils/format'
import type { ReviewItem } from '@/types/api'

defineProps<{
  type: 'plugin' | 'template'
  items: ReviewItem[]
  loading?: boolean
}>()

defineEmits<{
  (e: 'approve', item: ReviewItem, type: 'plugin' | 'template'): void
  (e: 'reject', item: ReviewItem, type: 'plugin' | 'template'): void
  (e: 'refresh'): void
}>()

function formatCategory(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>

<style scoped lang="scss">
.review-queue {
  .item-name {
    display: flex;
    align-items: center;
    gap: 8px;

    strong {
      font-weight: 500;
    }
  }

  .action-buttons {
    display: flex;
    gap: 8px;
  }
}
</style>
