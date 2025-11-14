<template>
  <el-dialog
    v-model="dialogVisible"
    title="Approve Submission"
    width="500px"
    @close="handleClose"
  >
    <div v-if="item" class="approve-dialog-content">
      <p class="info-text">
        You are about to approve <strong>{{ item.name }}</strong> by {{ item.author_name }}.
      </p>

      <el-form :model="form" label-width="120px">
        <el-form-item label="Feature Item">
          <el-switch
            v-model="form.is_featured"
            active-text="Yes"
            inactive-text="No"
          />
          <div class="form-help">
            Featured items will be highlighted in the marketplace
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="handleClose">Cancel</el-button>
      <el-button type="primary" @click="handleConfirm">
        Approve
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import type { ReviewItem } from '@/types/api'

const props = defineProps<{
  modelValue: boolean
  item: ReviewItem | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { is_featured: boolean }): void
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const form = reactive({
  is_featured: false
})

watch(() => props.modelValue, (visible) => {
  if (visible) {
    form.is_featured = false
  }
})

function handleClose() {
  emit('update:modelValue', false)
}

function handleConfirm() {
  emit('confirm', {
    is_featured: form.is_featured
  })
}
</script>

<style scoped lang="scss">
.approve-dialog-content {
  .info-text {
    margin-bottom: 20px;
    line-height: 1.6;

    strong {
      color: var(--el-color-primary);
    }
  }

  .form-help {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
  }
}
</style>
