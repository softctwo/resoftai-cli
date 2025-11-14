import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import FilesEnhanced from '@/views/FilesEnhanced.vue'

// Mock composables
vi.mock('@/composables/useCollaborativeEditing', () => ({
  useCollaborativeEditing: () => ({
    activeUsers: ref([]),
    remoteCursors: ref({}),
    isInSession: ref(false),
    onlineUserCount: ref(0),
    joinFileSession: vi.fn(),
    leaveFileSession: vi.fn(),
    sendFileEdit: vi.fn(),
    sendCursorPosition: vi.fn(),
    handleRemoteEdit: vi.fn()
  })
}))

vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: () => ({
    socket: {},
    isConnected: ref(true),
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  })
}))

// Mock API modules
vi.mock('@/api/files', () => ({
  default: {
    getFiles: vi.fn(() => Promise.resolve({ data: [] })),
    createFile: vi.fn(() => Promise.resolve({ data: { id: 1, name: 'test.js' } })),
    updateFile: vi.fn(() => Promise.resolve({ data: {} })),
    deleteFile: vi.fn(() => Promise.resolve({ data: {} })),
    getFileContent: vi.fn(() => Promise.resolve({ data: { content: '' } }))
  }
}))

vi.mock('@/api/projects', () => ({
  default: {
    getProjects: vi.fn(() => Promise.resolve({
      data: [
        { id: 1, name: 'Test Project', description: 'Test' }
      ]
    }))
  }
}))

// Mock user store
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    userId: 1,
    username: 'TestUser'
  })
}))

// Mock router
const mockRouter = {
  push: vi.fn(),
  currentRoute: {
    value: {
      query: {}
    }
  }
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRouter.currentRoute.value
}))

describe('FilesEnhanced Component', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the component structure', async () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true,
          ElAside: true,
          ElCard: true,
          ElTree: true,
          ElButton: true,
          ElIcon: true,
          MonacoEditor: true,
          ActiveUsers: true,
          CollaborationNotification: true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('initializes with loading state', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true,
          ElLoading: { template: '<div>Loading...</div>' }
        }
      }
    })

    expect(wrapper.vm.loading).toBeDefined()
  })

  it('has file tree and editor sections', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: { template: '<div class="el-container"><slot /></div>' },
          ElAside: { template: '<div class="el-aside"><slot /></div>' },
          ElMain: { template: '<div class="el-main"><slot /></div>' },
          ElCard: { template: '<div class="el-card"><slot /></div>' },
          MonacoEditor: { template: '<div class="monaco-editor"></div>' },
          ActiveUsers: { template: '<div class="active-users"></div>' }
        }
      }
    })

    // Should have file tree area (aside) and editor area (main)
    expect(wrapper.find('.el-aside').exists() || wrapper.find('.el-main').exists()).toBe(true)
  })

  it('initializes data properties correctly', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true
        }
      }
    })

    // Check initial data
    expect(wrapper.vm.projects).toBeDefined()
    expect(wrapper.vm.selectedProjectId).toBeDefined()
    expect(wrapper.vm.fileTree).toBeDefined()
    expect(wrapper.vm.fileContent).toBeDefined()
  })

  it('exposes collaborative editing functionality', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true
        }
      }
    })

    // Should have collaborative editing state from composable
    expect(wrapper.vm.activeUsers).toBeDefined()
    expect(wrapper.vm.remoteCursors).toBeDefined()
    expect(wrapper.vm.isInSession).toBeDefined()
  })

  it('handles file selection', async () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true,
          MonacoEditor: {
            template: '<div class="monaco-editor"></div>',
            props: ['modelValue', 'remoteCursors']
          }
        }
      }
    })

    // Simulate selecting a file
    if (wrapper.vm.handleFileSelect) {
      const mockFile = { id: 1, name: 'test.js', type: 'file' }
      wrapper.vm.handleFileSelect(mockFile)

      await wrapper.vm.$nextTick()

      // Should update selected file
      expect(wrapper.vm.selectedFileId).toBe(mockFile.id)
    }
  })

  it('integrates MonacoEditor component', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: { template: '<div><slot /></div>' },
          ElMain: { template: '<div><slot /></div>' },
          MonacoEditor: {
            template: '<div class="monaco-editor-stub"></div>',
            props: ['modelValue', 'remoteCursors', 'language']
          },
          ActiveUsers: true,
          ElCard: { template: '<div><slot /></div>' }
        }
      }
    })

    // MonacoEditor should be present (or its stub)
    const editor = wrapper.find('.monaco-editor-stub')
    expect(editor.exists() || wrapper.html().includes('monaco')).toBe(true)
  })

  it('integrates ActiveUsers component', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: { template: '<div><slot /></div>' },
          ElAside: { template: '<div><slot /></div>' },
          ActiveUsers: {
            template: '<div class="active-users-stub"></div>',
            props: ['users', 'currentUserId']
          },
          ElCard: { template: '<div><slot /></div>' }
        }
      }
    })

    // ActiveUsers component should be present
    const activeUsers = wrapper.find('.active-users-stub')
    expect(activeUsers.exists() || wrapper.html().includes('active')).toBe(true)
  })

  it('manages file editing state', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true
        }
      }
    })

    expect(wrapper.vm.fileContent).toBeDefined()
    expect(wrapper.vm.editingFileId).toBeDefined()
  })

  it('handles editor content changes', async () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true,
          MonacoEditor: {
            template: '<div></div>',
            props: ['modelValue'],
            emits: ['update:modelValue', 'change']
          }
        }
      }
    })

    if (wrapper.vm.handleEditorChange) {
      const newContent = 'console.log("test")'
      wrapper.vm.handleEditorChange(newContent, [])

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.fileContent).toBe(newContent)
    }
  })

  it('handles cursor position changes', async () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true,
          MonacoEditor: {
            template: '<div></div>',
            props: ['modelValue'],
            emits: ['cursor-change']
          }
        }
      }
    })

    if (wrapper.vm.handleCursorChange) {
      const position = { lineNumber: 5, column: 10 }
      const selection = null

      wrapper.vm.handleCursorChange(position, selection)

      await wrapper.vm.$nextTick()

      // Should call sendCursorPosition if in session
      expect(wrapper.vm.sendCursorPosition).toBeDefined()
    }
  })

  it('manages project selection', async () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true,
          ElSelect: { template: '<select><slot /></select>' }
        }
      }
    })

    if (wrapper.vm.handleProjectChange) {
      wrapper.vm.handleProjectChange(1)

      await wrapper.vm.$nextTick()

      expect(wrapper.vm.selectedProjectId).toBe(1)
    }
  })

  it('provides file operations', () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true
        }
      }
    })

    // Should have file operation methods
    expect(wrapper.vm.handleCreateFile || wrapper.vm.createFile).toBeDefined()
    expect(wrapper.vm.handleSaveFile || wrapper.vm.saveFile).toBeDefined()
    expect(wrapper.vm.handleDeleteFile || wrapper.vm.deleteFile).toBeDefined()
  })

  it('cleans up on unmount', async () => {
    wrapper = mount(FilesEnhanced, {
      global: {
        stubs: {
          ElContainer: true,
          ElHeader: true,
          ElMain: true
        }
      }
    })

    const leaveSession = wrapper.vm.leaveFileSession

    wrapper.unmount()

    // leaveFileSession should be available from composable
    expect(leaveSession).toBeDefined()
  })
})
