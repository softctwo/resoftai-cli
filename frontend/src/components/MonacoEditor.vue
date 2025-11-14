<template>
  <div ref="editorContainer" class="monaco-editor-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, defineProps, defineEmits } from 'vue'
import * as monaco from 'monaco-editor'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'javascript'
  },
  theme: {
    type: String,
    default: 'vs-dark'
  },
  readonly: {
    type: Boolean,
    default: false
  },
  options: {
    type: Object,
    default: () => ({})
  },
  remoteCursors: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'cursor-change'])

const editorContainer = ref(null)
let editor = null
let cursorDecorations = {}  // Store decorations for each remote cursor
let selectionDecorations = {}  // Store selection decorations

// User color palette for remote cursors
const userColors = [
  '#409EFF', // blue
  '#67C23A', // green
  '#E6A23C', // orange
  '#F56C6C', // red
  '#c71585', // purple
  '#20b2aa', // teal
  '#ff69b4', // pink
  '#ffa500', // orange
]

function getUserColor(userId) {
  return userColors[userId % userColors.length]
}

onMounted(() => {
  if (editorContainer.value) {
    // Create editor instance
    editor = monaco.editor.create(editorContainer.value, {
      value: props.modelValue,
      language: props.language,
      theme: props.theme,
      readOnly: props.readonly,
      automaticLayout: true,
      minimap: {
        enabled: true
      },
      scrollBeyondLastLine: false,
      fontSize: 14,
      tabSize: 2,
      wordWrap: 'on',
      ...props.options
    })

    // Listen for content changes
    editor.onDidChangeModelContent((e) => {
      const value = editor.getValue()
      emit('update:modelValue', value)
      emit('change', value, e.changes)
    })

    // Listen for cursor position changes
    editor.onDidChangeCursorPosition((e) => {
      const position = e.position
      const selection = editor.getSelection()
      emit('cursor-change', {
        lineNumber: position.lineNumber,
        column: position.column
      }, selection ? {
        startLineNumber: selection.startLineNumber,
        startColumn: selection.startColumn,
        endLineNumber: selection.endLineNumber,
        endColumn: selection.endColumn
      } : null)
    })
  }
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
  }
})

// Watch for external value changes
watch(() => props.modelValue, (newValue) => {
  if (editor && newValue !== editor.getValue()) {
    editor.setValue(newValue || '')
  }
})

// Watch for language changes
watch(() => props.language, (newLanguage) => {
  if (editor) {
    const model = editor.getModel()
    if (model) {
      monaco.editor.setModelLanguage(model, newLanguage)
    }
  }
})

// Watch for theme changes
watch(() => props.theme, (newTheme) => {
  if (editor) {
    monaco.editor.setTheme(newTheme)
  }
})

// Watch for readonly changes
watch(() => props.readonly, (newReadonly) => {
  if (editor) {
    editor.updateOptions({ readOnly: newReadonly })
  }
})

// Watch for remote cursors changes and render decorations
watch(() => props.remoteCursors, (newCursors) => {
  if (!editor) return

  // Clear old decorations
  Object.keys(cursorDecorations).forEach(userId => {
    if (!newCursors[userId]) {
      editor.deltaDecorations(cursorDecorations[userId] || [], [])
      delete cursorDecorations[userId]
      if (selectionDecorations[userId]) {
        editor.deltaDecorations(selectionDecorations[userId] || [], [])
        delete selectionDecorations[userId]
      }
    }
  })

  // Add/update decorations for each remote cursor
  Object.entries(newCursors).forEach(([userId, cursorData]) => {
    const { position, selection, username } = cursorData
    const color = getUserColor(parseInt(userId))

    // Create cursor decoration
    const cursorDecoration = {
      range: new monaco.Range(
        position.lineNumber,
        position.column,
        position.lineNumber,
        position.column
      ),
      options: {
        className: 'remote-cursor',
        stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
        beforeContentClassName: 'remote-cursor-line',
        before: {
          content: username,
          inlineClassName: 'remote-cursor-label',
          inlineClassNameAffectsLetterSpacing: true
        },
        // Add inline style for color
        glyphMarginClassName: 'remote-cursor-glyph',
      }
    }

    // Create CSS for this specific cursor
    addCursorStyle(userId, color)

    // Update cursor decoration
    const oldDecorations = cursorDecorations[userId] || []
    cursorDecorations[userId] = editor.deltaDecorations(oldDecorations, [cursorDecoration])

    // Add selection decoration if exists
    if (selection && (
      selection.startLineNumber !== selection.endLineNumber ||
      selection.startColumn !== selection.endColumn
    )) {
      const selectionDecoration = {
        range: new monaco.Range(
          selection.startLineNumber,
          selection.startColumn,
          selection.endLineNumber,
          selection.endColumn
        ),
        options: {
          className: `remote-selection remote-selection-${userId}`,
          stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
        }
      }

      const oldSelectionDecorations = selectionDecorations[userId] || []
      selectionDecorations[userId] = editor.deltaDecorations(oldSelectionDecorations, [selectionDecoration])
    } else if (selectionDecorations[userId]) {
      // Clear selection if no longer exists
      editor.deltaDecorations(selectionDecorations[userId], [])
      delete selectionDecorations[userId]
    }
  })
}, { deep: true })

// Dynamically add CSS for cursor colors
function addCursorStyle(userId, color) {
  const styleId = `remote-cursor-style-${userId}`
  let styleElement = document.getElementById(styleId)

  if (!styleElement) {
    styleElement = document.createElement('style')
    styleElement.id = styleId
    document.head.appendChild(styleElement)
  }

  styleElement.textContent = `
    .remote-cursor-line {
      border-left: 2px solid ${color} !important;
      position: relative;
    }
    .remote-cursor-label {
      background-color: ${color} !important;
      color: white !important;
      padding: 2px 6px !important;
      border-radius: 3px !important;
      font-size: 12px !important;
      position: absolute !important;
      top: -20px !important;
      left: 0 !important;
      white-space: nowrap !important;
      z-index: 1000 !important;
    }
    .remote-selection-${userId} {
      background-color: ${color}33 !important;
    }
  `
}

// Expose editor instance for parent component
defineExpose({
  getEditor: () => editor
})
</script>

<style scoped>
.monaco-editor-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>

<style>
/* Remote cursor styles */
.remote-cursor {
  position: relative;
}

.remote-cursor-line {
  border-left: 2px solid #409EFF;
  position: relative;
  animation: cursor-blink 1s ease-in-out infinite;
}

.remote-cursor-label {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  pointer-events: none;
  animation: fadeIn 0.3s ease-in;
}

.remote-selection {
  opacity: 0.3;
  transition: opacity 0.2s ease;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
