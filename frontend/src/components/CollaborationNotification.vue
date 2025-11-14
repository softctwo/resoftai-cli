<template>
  <transition-group name="notification-list" tag="div" class="notification-container">
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="notification-item"
      :class="`notification-${notification.type}`"
    >
      <el-icon class="notification-icon">
        <component :is="getIcon(notification.type)" />
      </el-icon>
      <div class="notification-content">
        <div class="notification-title">{{ notification.title }}</div>
        <div class="notification-message">{{ notification.message }}</div>
      </div>
      <div
        v-if="notification.userColor"
        class="notification-color-indicator"
        :style="{ backgroundColor: notification.userColor }"
      ></div>
    </div>
  </transition-group>
</template>

<script setup>
import { ref } from 'vue'
import { UserFilled, CloseBold, EditPen, InfoFilled } from '@element-plus/icons-vue'

const notifications = ref([])

let notificationId = 0

// Add notification
const addNotification = (type, title, message, userColor = null, duration = 3000) => {
  const id = ++notificationId
  const notification = {
    id,
    type,
    title,
    message,
    userColor
  }

  notifications.value.push(notification)

  // Auto remove after duration
  if (duration > 0) {
    setTimeout(() => {
      removeNotification(id)
    }, duration)
  }
}

// Remove notification
const removeNotification = (id) => {
  const index = notifications.value.findIndex(n => n.id === id)
  if (index !== -1) {
    notifications.value.splice(index, 1)
  }
}

// Get icon for notification type
const getIcon = (type) => {
  const icons = {
    'join': UserFilled,
    'leave': CloseBold,
    'edit': EditPen,
    'info': InfoFilled
  }
  return icons[type] || InfoFilled
}

// Expose methods
defineExpose({
  addNotification,
  removeNotification
})
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 3000;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  border-left: 4px solid var(--el-color-primary);
  transition: all 0.3s ease;
  min-width: 320px;
  animation: slideInRight 0.3s ease-out;
}

.notification-item:hover {
  transform: translateX(-4px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.notification-join {
  border-left-color: var(--el-color-success);
  background: linear-gradient(135deg, #f0f9ff 0%, #ffffff 100%);
}

.notification-leave {
  border-left-color: var(--el-color-warning);
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
}

.notification-edit {
  border-left-color: var(--el-color-primary);
  background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%);
}

.notification-info {
  border-left-color: var(--el-color-info);
  background: linear-gradient(135deg, #f9fafb 0%, #ffffff 100%);
}

.notification-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notification-join .notification-icon {
  color: var(--el-color-success);
}

.notification-leave .notification-icon {
  color: var(--el-color-warning);
}

.notification-edit .notification-icon {
  color: var(--el-color-primary);
}

.notification-info .notification-icon {
  color: var(--el-color-info);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.notification-message {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.notification-color-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  animation: pulse 2s ease-in-out infinite;
}

/* Animations */
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

/* List transition animations */
.notification-list-enter-active {
  transition: all 0.3s ease-out;
}

.notification-list-leave-active {
  transition: all 0.3s ease-in;
}

.notification-list-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-list-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.notification-list-move {
  transition: transform 0.3s ease;
}
</style>
