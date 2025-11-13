import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

// Singleton socket instance
let socket = null
let connectionCount = 0

export function useWebSocket() {
  const authStore = useAuthStore()
  const connected = ref(false)
  const connecting = ref(false)

  // Event listeners storage
  const listeners = new Map()

  const SOCKET_URL = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000'

  function connect() {
    if (socket && socket.connected) {
      connected.value = true
      return socket
    }

    if (connecting.value) {
      return socket
    }

    connecting.value = true

    socket = io(SOCKET_URL, {
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling'],
      auth: {
        token: authStore.token,
        user_id: authStore.user?.id
      }
    })

    // Connection events
    socket.on('connect', () => {
      console.log('WebSocket connected:', socket.id)
      connected.value = true
      connecting.value = false
      connectionCount++
    })

    socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      connected.value = false
      connecting.value = false
    })

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      connecting.value = false
      ElMessage.error('实时通信连接失败')
    })

    socket.on('reconnect', (attemptNumber) => {
      console.log('WebSocket reconnected after', attemptNumber, 'attempts')
      ElMessage.success('实时通信已恢复')
    })

    socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed')
      ElMessage.error('实时通信重连失败')
    })

    // Custom event handlers
    socket.on('joined', (data) => {
      console.log('Joined room:', data)
    })

    socket.on('left', (data) => {
      console.log('Left room:', data)
    })

    socket.on('error', (error) => {
      console.error('Socket error:', error)
      ElMessage.error(error.message || '实时通信错误')
    })

    return socket
  }

  function disconnect() {
    if (socket && socket.connected) {
      socket.disconnect()
      socket = null
      connected.value = false
    }
  }

  function joinProject(projectId) {
    if (!socket || !socket.connected) {
      console.warn('Socket not connected, cannot join project')
      return
    }

    socket.emit('join_project', {
      project_id: projectId,
      user_id: authStore.user?.id
    })
  }

  function leaveProject(projectId) {
    if (!socket || !socket.connected) {
      console.warn('Socket not connected, cannot leave project')
      return
    }

    socket.emit('leave_project', {
      project_id: projectId,
      user_id: authStore.user?.id
    })
  }

  function on(event, callback) {
    if (!socket) {
      console.warn('Socket not initialized')
      return
    }

    socket.on(event, callback)

    // Store listener for cleanup
    if (!listeners.has(event)) {
      listeners.set(event, [])
    }
    listeners.get(event).push(callback)
  }

  function off(event, callback) {
    if (!socket) {
      return
    }

    socket.off(event, callback)

    // Remove from listeners storage
    if (listeners.has(event)) {
      const eventListeners = listeners.get(event)
      const index = eventListeners.indexOf(callback)
      if (index > -1) {
        eventListeners.splice(index, 1)
      }
    }
  }

  function emit(event, data) {
    if (!socket || !socket.connected) {
      console.warn('Socket not connected, cannot emit event')
      return
    }

    socket.emit(event, data)
  }

  // Event-specific helpers
  function onProjectProgress(callback) {
    on('project.progress', callback)
  }

  function onAgentStatus(callback) {
    on('agent.status', callback)
  }

  function onTaskUpdate(callback) {
    on('task.update', callback)
  }

  function onLogNew(callback) {
    on('log.new', callback)
  }

  function onFileChange(callback) {
    on('file.change', callback)
  }

  function onError(callback) {
    on('error', callback)
  }

  // Cleanup function
  function cleanup() {
    // Remove all listeners
    for (const [event, callbacks] of listeners.entries()) {
      for (const callback of callbacks) {
        socket?.off(event, callback)
      }
    }
    listeners.clear()
  }

  onMounted(() => {
    if (authStore.isAuthenticated) {
      connect()
    }
  })

  onUnmounted(() => {
    cleanup()
  })

  return {
    socket,
    connected,
    connecting,
    connect,
    disconnect,
    joinProject,
    leaveProject,
    on,
    off,
    emit,
    onProjectProgress,
    onAgentStatus,
    onTaskUpdate,
    onLogNew,
    onFileChange,
    onError,
    cleanup
  }
}
