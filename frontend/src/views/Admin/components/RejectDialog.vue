<template>
  <el-dialog
    v-model="dialogVisible"
    title="Reject Submission"
    width="500px"
    @close="handleClose"
  >
    <div v-if="item" class="reject-dialog-content">
      <p class="info-text">
        You are about to reject <strong>{{ item.name }}</strong> by {{ item.author_name }}.
      </p>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="Feedback" prop="feedback" required>
          <el-input
            v-model="form.feedback"
            type="textarea"
            :rows="6"
            placeholder="Provide detailed feedback to help the author improve their submission..."
            maxlength="1000"
            show-word-limit
          />
          <div class="form-help">
            The author will receive this feedback via notification
          </div>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="handleClose">Cancel</el-button>
      <el-button type="danger" @click="handleConfirm">
        Reject
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, watch, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ReviewItem } from '@/types/api'

const props = defineProps<{
  modelValue: boolean
  item: ReviewItem | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm', data: { feedback: string }): void
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref<FormInstance>()
const form = reactive({
  feedback: ''
})

const rules: FormRules = {
  feedback: [
    { required: true, message: 'Please provide feedback', trigger: 'blur' },
    { min: 10, message: 'Feedback must be at least 10 characters', trigger: 'blur' }
  ]
}

watch(() => props.modelValue, (visible) => {
  if (visible) {
    form.feedback = ''
    formRef.value?.clearValidate()
  }
})

function handleClose() {
  emit('update:modelValue', false)
}

async function handleConfirm() {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      emit('confirm', {
        feedback: form.feedback
      })
    }
  })
}
</script>

<style scoped lang="scss">
.reject-dialog-content {
  .info-text {
    margin-bottom: 20px;
    line-height: 1.6;

    strong {
      color: var(--el-color-danger);
    }
  }

  .form-help {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
  }
}
</style>
