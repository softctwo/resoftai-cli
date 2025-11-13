<template>
  <div class="active-users">
    <div class="active-users-header">
      <el-icon><UserFilled /></el-icon>
      <span class="title">在线用户 ({{ userCount }})</span>
    </div>
    <div class="users-list">
      <el-tag
        v-for="user in users"
        :key="user.user_id"
        :type="getUserTagType(user)"
        :color="getUserColor(user.user_id)"
        effect="plain"
        size="small"
        class="user-tag"
      >
        <el-icon class="user-icon"><User /></el-icon>
        <span>{{ user.username }}</span>
        <el-icon v-if="isCurrentUser(user)" class="current-user-icon">
          <Check />
        </el-icon>
      </el-tag>
      <div v-if="users.length === 0" class="no-users">
        <el-text type="info">暂无其他用户在线</el-text>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { User, UserFilled, Check } from '@element-plus/icons-vue'

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

const getUserTagType = (user) => {
  return isCurrentUser(user) ? 'success' : 'info'
}

// Generate consistent colors for users based on their ID
const getUserColor = (userId) => {
  const colors = [
    '#409EFF', // blue
    '#67C23A', // green
    '#E6A23C', // orange
    '#F56C6C', // red
    '#909399', // gray
    '#c71585', // purple
    '#20b2aa', // teal
    '#ff69b4', // pink
  ]
  return colors[userId % colors.length]
}
</script>

<style scoped>
.active-users {
  padding: 12px;
  background: var(--el-bg-color);
  border-radius: 4px;
  border: 1px solid var(--el-border-color);
}

.active-users-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.title {
  font-size: 14px;
}

.users-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.user-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  cursor: default;
  transition: all 0.3s ease;
}

.user-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-icon {
  font-size: 12px;
}

.current-user-icon {
  font-size: 12px;
  color: var(--el-color-success);
  margin-left: 2px;
}

.no-users {
  width: 100%;
  text-align: center;
  padding: 12px 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
