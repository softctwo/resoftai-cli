<template>
  <div class="recently-reviewed">
    <el-table
      :data="items"
      style="width: 100%"
      stripe
    >
      <el-table-column prop="name" label="Name" min-width="200">
        <template #default="{ row }">
          <div class="item-name">
            <strong>{{ row.name }}</strong>
            <el-tag size="small" effect="plain">v{{ row.version }}</el-tag>
            <el-tag
              v-if="status === 'rejected'"
              type="danger"
              size="small"
            >
              Rejected
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="category" label="Category" width="150">
        <template #default="{ row }">
          <el-tag size="small">{{ formatCategory(row.category) }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="author_name" label="Author" width="150" />

      <el-table-column prop="submitted_at" label="Date" width="120">
        <template #default="{ row }">
          {{ formatDate(row.submitted_at, 'short') }}
        </template>
      </el-table-column>

      <el-table-column v-if="status !== 'rejected'" label="Actions" width="150" fixed="right">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="handleFeature(row)"
          >
            {{ row.is_featured ? 'Unfeature' : 'Feature' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { formatDate } from '@/utils/format'
import type { ReviewItem } from '@/types/api'

defineProps<{
  items: ReviewItem[]
  status?: 'approved' | 'rejected'
}>()

const emit = defineEmits<{
  (e: 'feature', item: ReviewItem, type: 'plugin' | 'template'): void
}>()

function formatCategory(category: string): string {
  return category
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function handleFeature(item: ReviewItem) {
  emit('feature', item, item.type)
}
</script>

<style scoped lang="scss">
.recently-reviewed {
  .item-name {
    display: flex;
    align-items: center;
    gap: 8px;

    strong {
      font-weight: 500;
    }
  }
}
</style>
