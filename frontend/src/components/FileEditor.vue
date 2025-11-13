<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="90%"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="editor-container">
      <div class="editor-toolbar">
        <el-select
          v-model="currentLanguage"
          placeholder="语言"
          size="small"
          style="width: 150px; margin-right: 10px"
        >
          <el-option label="JavaScript" value="javascript" />
          <el-option label="TypeScript" value="typescript" />
          <el-option label="Python" value="python" />
          <el-option label="Java" value="java" />
          <el-option label="Go" value="go" />
          <el-option label="HTML" value="html" />
          <el-option label="CSS" value="css" />
          <el-option label="JSON" value="json" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="SQL" value="sql" />
          <el-option label="Bash" value="shell" />
        </el-select>

        <el-select
          v-model="currentTheme"
          placeholder="主题"
          size="small"
          style="width: 150px"
        >
          <el-option label="暗色主题" value="vs-dark" />
          <el-option label="亮色主题" value="vs" />
          <el-option label="高对比度" value="hc-black" />
        </el-select>

        <div class="editor-info">
          <span>{{ currentFile?.path || '未选择文件' }}</span>
        </div>
      </div>

      <MonacoEditor
        v-model="editorContent"
        :language="currentLanguage"
        :theme="currentTheme"
        :readonly="readonly"
        :options="editorOptions"
        @change="handleContentChange"
      />
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button
        v-if="!readonly"
        type="primary"
        @click="handleSave"
        :loading="saving"
      >
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import MonacoEditor from './MonacoEditor.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  file: {
    type: Object,
    default: null
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const editorContent = ref('')
const currentLanguage = ref('javascript')
const currentTheme = ref('vs-dark')
const saving = ref(false)
const hasChanges = ref(false)

const currentFile = computed(() => props.file)

const title = computed(() => {
  if (!currentFile.value) return '文件编辑器'
  return props.readonly ? `查看文件: ${currentFile.value.path}` : `编辑文件: ${currentFile.value.path}`
})

const editorOptions = {
  automaticLayout: true,
  scrollBeyondLastLine: false,
  fontSize: 14,
  tabSize: 2,
  wordWrap: 'on',
  minimap: {
    enabled: true
  }
}

// Watch for file changes
watch(() => props.file, (newFile) => {
  if (newFile) {
    editorContent.value = newFile.content || ''
    currentLanguage.value = newFile.language || detectLanguage(newFile.path)
    hasChanges.value = false
  }
}, { immediate: true })

function detectLanguage(path) {
  if (!path) return 'javascript'

  const ext = path.split('.').pop().toLowerCase()
  const languageMap = {
    'js': 'javascript',
    'jsx': 'javascript',
    'ts': 'typescript',
    'tsx': 'typescript',
    'py': 'python',
    'java': 'java',
    'go': 'go',
    'html': 'html',
    'htm': 'html',
    'css': 'css',
    'scss': 'scss',
    'sass': 'sass',
    'json': 'json',
    'md': 'markdown',
    'sql': 'sql',
    'sh': 'shell',
    'bash': 'shell'
  }

  return languageMap[ext] || 'plaintext'
}

function handleContentChange(content) {
  hasChanges.value = content !== (props.file?.content || '')
}

function handleClose() {
  if (hasChanges.value && !props.readonly) {
    ElMessageBox.confirm(
      '文件已修改，确定要关闭吗？未保存的更改将丢失。',
      '确认关闭',
      {
        confirmButtonText: '关闭',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      visible.value = false
    }).catch(() => {
      // 用户取消
    })
  } else {
    visible.value = false
  }
}

async function handleSave() {
  if (!currentFile.value) return

  saving.value = true
  try {
    await emit('save', {
      file: currentFile.value,
      content: editorContent.value,
      language: currentLanguage.value
    })

    hasChanges.value = false
    ElMessage.success('文件保存成功')
  } catch (error) {
    ElMessage.error('文件保存失败: ' + error.message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.editor-container {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.editor-info {
  flex: 1;
  text-align: right;
  color: #606266;
  font-size: 14px;
}

.monaco-editor-container {
  flex: 1;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}
</style>
