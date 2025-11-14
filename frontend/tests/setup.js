import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// Mock Element Plus message and notification
config.global.mocks = {
  $message: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
  $notify: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  },
}

// Mock Monaco Editor
vi.mock('monaco-editor', () => ({
  editor: {
    create: vi.fn(() => ({
      dispose: vi.fn(),
      getValue: vi.fn(() => ''),
      setValue: vi.fn(),
      onDidChangeModelContent: vi.fn(),
      onDidChangeCursorPosition: vi.fn(),
      onDidChangeCursorSelection: vi.fn(),
      deltaDecorations: vi.fn(() => []),
      getModel: vi.fn(() => ({
        getLineCount: vi.fn(() => 1),
      })),
      layout: vi.fn(),
    })),
    defineTheme: vi.fn(),
    setTheme: vi.fn(),
  },
  languages: {
    register: vi.fn(),
    setMonarchTokensProvider: vi.fn(),
  },
  Range: class Range {
    constructor(startLine, startCol, endLine, endCol) {
      this.startLineNumber = startLine
      this.startColumn = startCol
      this.endLineNumber = endLine
      this.endColumn = endCol
    }
  },
}))

// Mock Socket.IO client
vi.mock('socket.io-client', () => ({
  default: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    connected: false,
  })),
  io: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
    connect: vi.fn(),
    disconnect: vi.fn(),
    connected: false,
  })),
}))

// Mock ECharts
vi.mock('echarts', () => ({
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
  })),
  use: vi.fn(),
}))

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
