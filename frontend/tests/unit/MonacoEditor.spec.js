import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MonacoEditor from '@/components/MonacoEditor.vue'

describe('MonacoEditor Component', () => {
  let mockEditor
  let mockModel

  beforeEach(() => {
    mockModel = {
      getLineCount: vi.fn(() => 10)
    }

    mockEditor = {
      dispose: vi.fn(),
      getValue: vi.fn(() => 'test content'),
      setValue: vi.fn(),
      onDidChangeModelContent: vi.fn((callback) => {
        mockEditor._contentCallback = callback
        return { dispose: vi.fn() }
      }),
      onDidChangeCursorPosition: vi.fn((callback) => {
        mockEditor._cursorCallback = callback
        return { dispose: vi.fn() }
      }),
      onDidChangeCursorSelection: vi.fn(),
      deltaDecorations: vi.fn(() => ['decoration-id']),
      getModel: vi.fn(() => mockModel),
      getSelection: vi.fn(() => ({
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 1,
        endColumn: 5
      })),
      updateOptions: vi.fn(),
      layout: vi.fn()
    }

    // Mock monaco.editor.create to return our mock editor
    const monaco = await import('monaco-editor')
    monaco.editor.create.mockReturnValue(mockEditor)
  })

  it('renders editor container', () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test'
      }
    })

    expect(wrapper.find('.monaco-editor-container').exists()).toBe(true)
  })

  it('initializes editor with correct options', async () => {
    const monaco = await import('monaco-editor')

    mount(MonacoEditor, {
      props: {
        modelValue: 'initial content',
        language: 'python',
        theme: 'vs-light',
        readonly: true
      }
    })

    await nextTick()

    expect(monaco.editor.create).toHaveBeenCalledWith(
      expect.any(Object),
      expect.objectContaining({
        value: 'initial content',
        language: 'python',
        theme: 'vs-light',
        readOnly: true
      })
    )
  })

  it('emits update:modelValue on content change', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test'
      }
    })

    await nextTick()

    // Simulate content change
    mockEditor.getValue.mockReturnValue('new content')
    mockEditor._contentCallback({
      changes: [{ text: 'new content' }]
    })

    await nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['new content'])
  })

  it('emits change event with value and changes', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test'
      }
    })

    await nextTick()

    const changes = [{ text: 'new text' }]
    mockEditor.getValue.mockReturnValue('updated')
    mockEditor._contentCallback({ changes })

    await nextTick()

    expect(wrapper.emitted('change')).toBeTruthy()
    expect(wrapper.emitted('change')[0]).toEqual(['updated', changes])
  })

  it('emits cursor-change event on cursor position change', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test'
      }
    })

    await nextTick()

    // Simulate cursor position change
    const position = { lineNumber: 5, column: 10 }
    mockEditor._cursorCallback({ position })

    await nextTick()

    expect(wrapper.emitted('cursor-change')).toBeTruthy()
    const emittedData = wrapper.emitted('cursor-change')[0]
    expect(emittedData[0]).toEqual({ lineNumber: 5, column: 10 })
  })

  it('updates editor value when modelValue prop changes', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'initial'
      }
    })

    await nextTick()

    // Change prop
    mockEditor.getValue.mockReturnValue('initial')
    await wrapper.setProps({ modelValue: 'updated' })

    await nextTick()

    expect(mockEditor.setValue).toHaveBeenCalledWith('updated')
  })

  it('updates editor language when language prop changes', async () => {
    const monaco = await import('monaco-editor')

    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        language: 'javascript'
      }
    })

    await nextTick()

    monaco.editor.setModelLanguage = vi.fn()
    await wrapper.setProps({ language: 'python' })

    await nextTick()

    expect(monaco.editor.setModelLanguage).toHaveBeenCalledWith(mockModel, 'python')
  })

  it('updates editor theme when theme prop changes', async () => {
    const monaco = await import('monaco-editor')

    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        theme: 'vs-dark'
      }
    })

    await nextTick()

    monaco.editor.setTheme = vi.fn()
    await wrapper.setProps({ theme: 'vs-light' })

    await nextTick()

    expect(monaco.editor.setTheme).toHaveBeenCalledWith('vs-light')
  })

  it('updates readonly option when readonly prop changes', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        readonly: false
      }
    })

    await nextTick()

    await wrapper.setProps({ readonly: true })

    await nextTick()

    expect(mockEditor.updateOptions).toHaveBeenCalledWith({ readOnly: true })
  })

  it('renders remote cursors with decorations', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        remoteCursors: {
          1: {
            position: { lineNumber: 1, column: 5 },
            username: 'Alice',
            selection: null
          }
        }
      }
    })

    await nextTick()

    expect(mockEditor.deltaDecorations).toHaveBeenCalled()
  })

  it('renders remote selections when present', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        remoteCursors: {
          1: {
            position: { lineNumber: 1, column: 1 },
            username: 'Bob',
            selection: {
              startLineNumber: 1,
              startColumn: 1,
              endLineNumber: 2,
              endColumn: 5
            }
          }
        }
      }
    })

    await nextTick()

    // Should be called for both cursor and selection decorations
    expect(mockEditor.deltaDecorations).toHaveBeenCalled()
  })

  it('clears decorations when remote cursor is removed', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        remoteCursors: {
          1: {
            position: { lineNumber: 1, column: 1 },
            username: 'Charlie'
          }
        }
      }
    })

    await nextTick()

    // Remove the cursor
    await wrapper.setProps({ remoteCursors: {} })

    await nextTick()

    // deltaDecorations should be called to clear
    expect(mockEditor.deltaDecorations).toHaveBeenCalled()
  })

  it('applies custom options from props', async () => {
    const monaco = await import('monaco-editor')

    const customOptions = {
      fontSize: 16,
      lineNumbers: 'off'
    }

    mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        options: customOptions
      }
    })

    await nextTick()

    expect(monaco.editor.create).toHaveBeenCalledWith(
      expect.any(Object),
      expect.objectContaining(customOptions)
    )
  })

  it('disposes editor on unmount', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test'
      }
    })

    await nextTick()

    wrapper.unmount()

    expect(mockEditor.dispose).toHaveBeenCalled()
  })

  it('exposes getEditor method', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test'
      }
    })

    await nextTick()

    expect(wrapper.vm.getEditor).toBeDefined()
    expect(typeof wrapper.vm.getEditor).toBe('function')
    expect(wrapper.vm.getEditor()).toBe(mockEditor)
  })

  it('handles empty modelValue gracefully', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: ''
      }
    })

    await nextTick()

    // Should not throw error
    expect(wrapper.exists()).toBe(true)
  })

  it('generates consistent colors for users', async () => {
    const wrapper = mount(MonacoEditor, {
      props: {
        modelValue: 'test',
        remoteCursors: {
          1: { position: { lineNumber: 1, column: 1 }, username: 'User1' },
          2: { position: { lineNumber: 2, column: 1 }, username: 'User2' }
        }
      }
    })

    await nextTick()

    // Check that style elements were added to document head
    const style1 = document.getElementById('remote-cursor-style-1')
    const style2 = document.getElementById('remote-cursor-style-2')

    expect(style1).toBeTruthy()
    expect(style2).toBeTruthy()
    expect(style1.textContent).toContain('#409EFF') // First color
    expect(style2.textContent).toContain('#67C23A') // Second color
  })
})
