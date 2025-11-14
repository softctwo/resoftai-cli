import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useCollaborativeEditing } from '@/composables/useCollaborativeEditing'

// Mock useWebSocket
vi.mock('@/composables/useWebSocket', () => ({
  useWebSocket: () => {
    const mockSocket = {
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn(),
      connected: true
    }

    const eventHandlers = {}

    return {
      socket: mockSocket,
      isConnected: ref(true),
      on: vi.fn((event, handler) => {
        eventHandlers[event] = handler
        mockSocket._eventHandlers = eventHandlers
      }),
      off: vi.fn(),
      emit: vi.fn(),
      _getHandlers: () => eventHandlers
    }
  }
}))

// Mock Element Plus notification
vi.mock('element-plus', () => ({
  ElNotification: vi.fn()
}))

describe('useCollaborativeEditing Composable', () => {
  let fileId, projectId, userId, username

  beforeEach(() => {
    fileId = ref(123)
    projectId = ref(456)
    userId = ref(1)
    username = ref('TestUser')
    vi.clearAllMocks()
  })

  it('initializes with default state', () => {
    const {
      activeUsers,
      remoteCursors,
      fileVersion,
      isInSession,
      onlineUserCount
    } = useCollaborativeEditing(fileId, projectId, userId, username)

    expect(activeUsers.value).toEqual([])
    expect(remoteCursors.value).toEqual({})
    expect(fileVersion.value).toBe(0)
    expect(isInSession.value).toBe(false)
    expect(onlineUserCount.value).toBe(0)
  })

  it('exposes required methods', () => {
    const composable = useCollaborativeEditing(fileId, projectId, userId, username)

    expect(composable.joinFileSession).toBeDefined()
    expect(composable.leaveFileSession).toBeDefined()
    expect(composable.sendFileEdit).toBeDefined()
    expect(composable.sendCursorPosition).toBeDefined()
    expect(composable.handleRemoteEdit).toBeDefined()
    expect(composable.handleRemoteCursor).toBeDefined()
  })

  it('joins file session with correct parameters', () => {
    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const { joinFileSession } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    joinFileSession()

    expect(mockWs.emit).toHaveBeenCalledWith('join_file_session', {
      file_id: fileId,
      project_id: projectId,
      user_id: userId,
      username: username
    })
  })

  it('leaves file session and updates state', () => {
    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const { leaveFileSession, isInSession } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    isInSession.value = true
    leaveFileSession()

    expect(mockWs.emit).toHaveBeenCalledWith('leave_file_session', {
      file_id: fileId
    })
    expect(isInSession.value).toBe(false)
  })

  it('sends file edits when in session', () => {
    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const { sendFileEdit, isInSession } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    isInSession.value = true
    const changes = [{ text: 'new text', range: {} }]
    sendFileEdit(changes)

    expect(mockWs.emit).toHaveBeenCalledWith('file_edit', {
      file_id: fileId,
      changes: changes
    })
  })

  it('does not send edits when not in session', () => {
    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const { sendFileEdit, isInSession } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    isInSession.value = false
    const changes = [{ text: 'new text' }]
    sendFileEdit(changes)

    expect(mockWs.emit).not.toHaveBeenCalledWith('file_edit', expect.any(Object))
  })

  it('sends cursor position updates', () => {
    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const { sendCursorPosition, isInSession } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    isInSession.value = true
    const position = { lineNumber: 5, column: 10 }
    const selection = { startLineNumber: 5, startColumn: 10, endLineNumber: 6, endColumn: 5 }

    sendCursorPosition(position, selection)

    expect(mockWs.emit).toHaveBeenCalledWith('cursor_position', {
      file_id: fileId,
      position: position,
      selection: selection
    })
  })

  it('updates active users on file join', () => {
    const { activeUsers, fileVersion, isInSession } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    // Trigger the file.joined event handler
    const handlers = mockWs.socket._eventHandlers
    const joinData = {
      active_users: [
        { user_id: 1, username: 'User1' },
        { user_id: 2, username: 'User2' }
      ],
      version: 5
    }

    if (handlers && handlers['file.joined']) {
      handlers['file.joined'](joinData)
    }

    expect(activeUsers.value).toEqual(joinData.active_users)
    expect(fileVersion.value).toBe(5)
    expect(isInSession.value).toBe(true)
  })

  it('handles user joining the file', () => {
    const { ElNotification } = await import('element-plus')
    const { activeUsers } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const handlers = mockWs.socket._eventHandlers
    const joinData = {
      file_id: fileId.value,
      user_id: 2,
      username: 'NewUser',
      active_users: [
        { user_id: 1, username: 'TestUser' },
        { user_id: 2, username: 'NewUser' }
      ]
    }

    if (handlers && handlers['file.join']) {
      handlers['file.join'](joinData)
    }

    expect(activeUsers.value).toEqual(joinData.active_users)
    expect(ElNotification).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '用户加入',
        type: 'success'
      })
    )
  })

  it('handles user leaving the file', () => {
    const { ElNotification } = await import('element-plus')
    const { activeUsers, remoteCursors } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    // Set up initial state
    remoteCursors.value[2] = {
      position: { lineNumber: 1, column: 1 },
      username: 'LeavingUser'
    }

    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const handlers = mockWs.socket._eventHandlers
    const leaveData = {
      file_id: fileId.value,
      user_id: 2,
      username: 'LeavingUser',
      active_users: [
        { user_id: 1, username: 'TestUser' }
      ]
    }

    if (handlers && handlers['file.leave']) {
      handlers['file.leave'](leaveData)
    }

    expect(activeUsers.value).toEqual(leaveData.active_users)
    expect(remoteCursors.value[2]).toBeUndefined()
    expect(ElNotification).toHaveBeenCalledWith(
      expect.objectContaining({
        title: '用户离开',
        type: 'warning'
      })
    )
  })

  it('handles remote file edits', () => {
    const { handleRemoteEdit, fileVersion } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    const editData = {
      file_id: fileId.value,
      user_id: 2, // Different user
      version: 10,
      changes: [{ text: 'edited text' }]
    }

    const result = handleRemoteEdit(editData)

    expect(result).toEqual(editData.changes)
    expect(fileVersion.value).toBe(10)
  })

  it('ignores edits from current user', () => {
    const { handleRemoteEdit, fileVersion } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    const editData = {
      file_id: fileId.value,
      user_id: userId.value, // Same user
      version: 10,
      changes: [{ text: 'edited text' }]
    }

    const result = handleRemoteEdit(editData)

    expect(result).toBeNull()
    expect(fileVersion.value).toBe(0) // Should not update
  })

  it('handles remote cursor position updates', () => {
    const { remoteCursors } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const handlers = mockWs.socket._eventHandlers
    const cursorData = {
      file_id: fileId.value,
      user_id: 2,
      username: 'OtherUser',
      position: { lineNumber: 3, column: 7 },
      selection: { startLineNumber: 3, startColumn: 7, endLineNumber: 3, endColumn: 15 }
    }

    if (handlers && handlers['cursor.position']) {
      handlers['cursor.position'](cursorData)
    }

    expect(remoteCursors.value[2]).toEqual({
      position: cursorData.position,
      selection: cursorData.selection,
      username: cursorData.username
    })
  })

  it('ignores cursor updates from current user', () => {
    const { remoteCursors } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    const { useWebSocket } = await import('@/composables/useWebSocket')
    const mockWs = useWebSocket()

    const handlers = mockWs.socket._eventHandlers
    const cursorData = {
      file_id: fileId.value,
      user_id: userId.value, // Same user
      position: { lineNumber: 3, column: 7 }
    }

    if (handlers && handlers['cursor.position']) {
      handlers['cursor.position'](cursorData)
    }

    expect(remoteCursors.value[userId.value]).toBeUndefined()
  })

  it('computes online user count correctly', () => {
    const { activeUsers, onlineUserCount } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    expect(onlineUserCount.value).toBe(0)

    activeUsers.value = [
      { user_id: 1, username: 'User1' },
      { user_id: 2, username: 'User2' },
      { user_id: 3, username: 'User3' }
    ]

    expect(onlineUserCount.value).toBe(3)
  })

  it('filters out current user in otherUsers computed', () => {
    const { activeUsers, otherUsers } = useCollaborativeEditing(
      fileId,
      projectId,
      userId,
      username
    )

    activeUsers.value = [
      { user_id: 1, username: 'TestUser' }, // Current user
      { user_id: 2, username: 'User2' },
      { user_id: 3, username: 'User3' }
    ]

    expect(otherUsers.value).toHaveLength(2)
    expect(otherUsers.value.find(u => u.user_id === 1)).toBeUndefined()
  })
})
