<template>
  <el-dialog
    v-model="dialogVisible"
    title="Publish Template"
    width="700px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="140px"
    >
      <el-form-item label="Template Name" prop="name" required>
        <el-input
          v-model="form.name"
          placeholder="Enter template name"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="Slug" prop="slug" required>
        <el-input
          v-model="form.slug"
          placeholder="template-slug"
          maxlength="200"
        >
          <template #append>.template</template>
        </el-input>
        <div class="form-help">
          URL-friendly identifier (lowercase, hyphens only)
        </div>
      </el-form-item>

      <el-form-item label="Category" prop="category" required>
        <el-select v-model="form.category" placeholder="Select category">
          <el-option label="Web App" value="web_app" />
          <el-option label="REST API" value="rest_api" />
          <el-option label="CLI Tool" value="cli_tool" />
          <el-option label="Microservice" value="microservice" />
          <el-option label="Data Pipeline" value="data_pipeline" />
          <el-option label="ML Project" value="ml_project" />
          <el-option label="Mobile App" value="mobile_app" />
          <el-option label="Other" value="other" />
        </el-select>
      </el-form-item>

      <el-form-item label="Version" prop="version" required>
        <el-input
          v-model="form.version"
          placeholder="1.0.0"
          maxlength="50"
        />
        <div class="form-help">
          Semantic versioning (e.g., 1.0.0)
        </div>
      </el-form-item>

      <el-form-item label="Description" prop="description" required>
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="4"
          placeholder="Describe what this template does and what it's for..."
          maxlength="1000"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="Tags" prop="tags">
        <el-select
          v-model="form.tags"
          multiple
          filterable
          allow-create
          placeholder="Add tags"
        />
        <div class="form-help">
          Add tags to help users find your template
        </div>
      </el-form-item>

      <el-form-item label="License" prop="license">
        <el-select v-model="form.license" placeholder="Select license">
          <el-option label="MIT" value="MIT" />
          <el-option label="Apache 2.0" value="Apache-2.0" />
          <el-option label="GPL 3.0" value="GPL-3.0" />
          <el-option label="BSD 3-Clause" value="BSD-3-Clause" />
          <el-option label="ISC" value="ISC" />
          <el-option label="Other" value="Other" />
        </el-select>
      </el-form-item>

      <el-form-item label="Documentation URL" prop="documentation_url">
        <el-input
          v-model="form.documentation_url"
          placeholder="https://..."
        />
      </el-form-item>

      <el-form-item label="Source URL" prop="source_url">
        <el-input
          v-model="form.source_url"
          placeholder="https://github.com/..."
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">Cancel</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        Submit for Review
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { templateApi } from '@/api/marketplace'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'published'): void
}>()

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formRef = ref<FormInstance>()
const submitting = ref(false)

const form = reactive({
  name: '',
  slug: '',
  category: '',
  version: '1.0.0',
  description: '',
  tags: [] as string[],
  license: 'MIT',
  documentation_url: '',
  source_url: '',
  template_data: {} // This would be populated from actual template files
})

const rules: FormRules = {
  name: [
    { required: true, message: 'Please enter template name', trigger: 'blur' }
  ],
  slug: [
    { required: true, message: 'Please enter slug', trigger: 'blur' },
    { pattern: /^[a-z0-9-]+$/, message: 'Slug must be lowercase with hyphens only', trigger: 'blur' }
  ],
  category: [
    { required: true, message: 'Please select category', trigger: 'change' }
  ],
  version: [
    { required: true, message: 'Please enter version', trigger: 'blur' },
    { pattern: /^\d+\.\d+\.\d+$/, message: 'Version must be in format X.Y.Z', trigger: 'blur' }
  ],
  description: [
    { required: true, message: 'Please enter description', trigger: 'blur' },
    { min: 20, message: 'Description must be at least 20 characters', trigger: 'blur' }
  ]
}

function handleClose() {
  emit('update:modelValue', false)
  resetForm()
}

function resetForm() {
  formRef.value?.resetFields()
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await templateApi.publishTemplate({
          name: form.name,
          slug: form.slug,
          category: form.category as any,
          version: form.version,
          description: form.description,
          template_data: form.template_data,
          tags: form.tags,
          license: form.license || undefined,
          documentation_url: form.documentation_url || undefined,
          source_url: form.source_url || undefined
        })

        ElMessage.success('Template submitted successfully!')
        emit('published')
        handleClose()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || 'Failed to publish template')
      } finally {
        submitting.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.form-help {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
</style>
