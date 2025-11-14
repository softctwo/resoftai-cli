/**
 * Composable for collaborative editing functionality
 * Handles real-time multi-user editing, cursor positions, and online status
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useWebSocket } from './useWebSocket'
import { ElNotification } from 'element-plus'

// User color palette (same as Monaco editor)
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

export function useCollaborativeEditing(fileId, projectId, userId, username) {
  const { socket, isConnected, on, emit, off } = useWebSocket()

  // State
  const activeUsers = ref([])
  const remoteCursors = ref({}) // { userId: { position, selection, username } }
  const fileVersion = ref(0)
  const isInSession = ref(false)

  // Computed
  const onlineUserCount = computed(() => activeUsers.value.length)
  const otherUsers = computed(() =>
    activeUsers.value.filter(user => user.user_id !== userId.value)
  )

  /**
   * Join file editing session
   */
  const joinFileSession = () => {
    if (!isConnected.value || !fileId || !projectId || !userId || !username) {
      console.warn('Cannot join file session: missing required parameters')
      return
    }

    emit('join_file_session', {
      file_id: fileId,
      project_id: projectId,
      user_id: userId,
      username: username
    })
  }

  /**
   * Leave file editing session
   */
  const leaveFileSession = () => {
    if (!isConnected.value || !fileId) {
      return
    }

    emit('leave_file_session', {
      file_id: fileId
    })
    isInSession.value = false
  }

  /**
   * Send file edit changes to other users
   */
  const sendFileEdit = (changes) => {
    if (!isConnected.value || !isInSession.value) {
      return
    }

    emit('file_edit', {
      file_id: fileId,
      changes: changes
    })
  }

  /**
   * Send cursor position update
   */
  const sendCursorPosition = (position, selection = null) => {
    if (!isConnected.value || !isInSession.value) {
      return
    }

    emit('cursor_position', {
      file_id: fileId,
      position: position,
      selection: selection
    })
  }

  // Event handlers

  /**
   * Handle successful file session join
   */
  const handleFileJoined = (data) => {
    console.log('Joined file session:', data)
    activeUsers.value = data.active_users || []
    fileVersion.value = data.version || 0
    isInSession.value = true
  }

  /**
   * Handle user joining the file
   */
  const handleUserJoined = (data) => {
    console.log('User joined file:', data)
    if (data.file_id === fileId.value && data.user_id !== userId.value) {
      activeUsers.value = data.active_users || []

      // Show notification
      const userColor = getUserColor(data.user_id)
      ElNotification({
        title: '用户加入',
        message: `${data.username} 加入了协作编辑`,
        type: 'success',
        duration: 3000,
        customClass: 'collaboration-notification',
        icon: 'UserFilled',
        offset: 80
      })
    }
  }

  /**
   * Handle user leaving the file
   */
  const handleUserLeft = (data) => {
    console.log('User left file:', data)
    if (data.file_id === fileId.value && data.user_id !== userId.value) {
      activeUsers.value = data.active_users || []

      // Remove cursor for the user who left
      if (remoteCursors.value[data.user_id]) {
        delete remoteCursors.value[data.user_id]
      }

      // Show notification
      ElNotification({
        title: '用户离开',
        message: `${data.username} 离开了协作编辑`,
        type: 'warning',
        duration: 3000,
        offset: 80
      })
    }
  }

  /**
   * Handle remote file edits
   * Returns the change object to be applied to the editor
   */
  const handleRemoteEdit = (data) => {
    console.log('Remote file edit:', data)
    if (data.file_id === fileId.value && data.user_id !== userId.value) {
      fileVersion.value = data.version
      return data.changes
    }
    return null
  }

  /**
   * Handle remote cursor position updates
   */
  const handleRemoteCursor = (data) => {
    if (data.file_id === fileId.value && data.user_id !== userId.value) {
      remoteCursors.value[data.user_id] = {
        position: data.position,
        selection: data.selection,
        username: data.username
      }
    }
  }

  // Setup event listeners
  onMounted(() => {
    on('file.joined', handleFileJoined)
    on('file.join', handleUserJoined)
    on('file.leave', handleUserLeft)
    on('file.edit', handleRemoteEdit)
    on('cursor.position', handleRemoteCursor)

    // Auto-join session when connected
    if (isConnected.value) {
      joinFileSession()
    }
  })

  // Cleanup
  onUnmounted(() => {
    leaveFileSession()
    off('file.joined', handleFileJoined)
    off('file.join', handleUserJoined)
    off('file.leave', handleUserLeft)
    off('file.edit', handleRemoteEdit)
    off('cursor.position', handleRemoteCursor)
  })

  return {
    // State
    activeUsers,
    remoteCursors,
    fileVersion,
    isInSession,
    onlineUserCount,
    otherUsers,

    // Methods
    joinFileSession,
    leaveFileSession,
    sendFileEdit,
    sendCursorPosition,

    // Event handlers (exposed for custom handling)
    handleRemoteEdit,
    handleRemoteCursor
  }
}
