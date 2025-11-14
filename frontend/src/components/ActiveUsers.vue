<template>
  <div class="active-users">
    <div class="active-users-header">
      <el-icon class="header-icon pulse"><UserFilled /></el-icon>
      <span class="title">在线协作</span>
      <el-badge :value="userCount" class="user-count-badge" type="success" />
    </div>
    <transition-group name="user-list" tag="div" class="users-list">
      <div
        v-for="user in users"
        :key="user.user_id"
        class="user-item"
        :class="{ 'current-user': isCurrentUser(user) }"
      >
        <div class="user-avatar" :style="{ backgroundColor: getUserColor(user.user_id) }">
          {{ getUserInitials(user.username) }}
        </div>
        <div class="user-info">
          <span class="user-name">{{ user.username }}</span>
          <span v-if="isCurrentUser(user)" class="user-label">(你)</span>
        </div>
        <div class="user-status">
          <div class="status-dot" :style="{ backgroundColor: getUserColor(user.user_id) }"></div>
          <span class="status-text">编辑中</span>
        </div>
      </div>
      <div v-if="users.length === 0" key="no-users" class="no-users">
        <el-icon class="empty-icon"><User /></el-icon>
        <el-text type="info">等待其他用户加入...</el-text>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { User, UserFilled } from '@element-plus/icons-vue'

const props = defineProps({
  users: {
    type: Array,
    default: () => []
  },
  currentUserId: {
    type: Number,
    default: null
  }
})

const userCount = computed(() => props.users.length)

const isCurrentUser = (user) => {
  return user.user_id === props.currentUserId
}

// Generate consistent colors for users based on their ID (same as Monaco editor)
const getUserColor = (userId) => {
  const colors = [
    '#409EFF', // blue
    '#67C23A', // green
    '#E6A23C', // orange
    '#F56C6C', // red
    '#c71585', // purple
    '#20b2aa', // teal
    '#ff69b4', // pink
    '#ffa500', // orange
  ]
  return colors[userId % colors.length]
}

// Get user initials for avatar
const getUserInitials = (username) => {
  if (!username) return '?'
  const parts = username.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return username.substring(0, 2).toUpperCase()
}
</script>

<style scoped>
.active-users {
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.active-users-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.header-icon {
  font-size: 18px;
  color: var(--el-color-primary);
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}

.title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  flex: 1;
}

.user-count-badge {
  margin-left: auto;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s ease;
  cursor: default;
}

.user-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: var(--el-color-primary-light-5);
}

.user-item.current-user {
  background: linear-gradient(135deg, #e3f2fd 0%, #f5f5f5 100%);
  border-color: var(--el-color-primary-light-3);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease-out;
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.user-label {
  font-size: 12px;
  color: var(--el-color-success);
  font-weight: 600;
}

.user-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.no-users {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
  color: var(--el-text-color-disabled);
  opacity: 0.5;
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* List transition animations */
.user-list-enter-active,
.user-list-leave-active {
  transition: all 0.3s ease;
}

.user-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.user-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.user-list-move {
  transition: transform 0.3s ease;
}

/* Scrollbar styling */
.users-list::-webkit-scrollbar {
  width: 6px;
}

.users-list::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.users-list::-webkit-scrollbar-thumb {
  background: var(--el-color-primary-light-5);
  border-radius: 3px;
}

.users-list::-webkit-scrollbar-thumb:hover {
  background: var(--el-color-primary);
}
</style>
