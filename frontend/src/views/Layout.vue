<template>
  <el-container class="layout-container">
    <!-- Mobile Overlay -->
    <div class="mobile-overlay" :class="{ 'is-active': mobileMenuOpen }" @click="closeMobileMenu"></div>

    <!-- Sidebar -->
    <el-aside :width="sidebarWidth" class="sidebar" :class="{ 'mobile-sidebar': isMobile, 'is-open': mobileMenuOpen }">
      <div class="logo">
        <el-icon :size="30"><Platform /></el-icon>
        <span v-if="!isCollapsed">ResoftAI</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        :router="true"
        :collapse="isCollapsed && !isMobile"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表板</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-menu-item index="/agents">
          <el-icon><UserFilled /></el-icon>
          <span>智能体管理</span>
        </el-menu-item>
        <el-menu-item index="/files">
          <el-icon><Files /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
        <el-menu-item index="/models">
          <el-icon><Setting /></el-icon>
          <span>模型配置</span>
        </el-menu-item>
        <el-menu-item index="/code-quality">
          <el-icon><DocumentChecked /></el-icon>
          <span>代码质量检查</span>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><Box /></el-icon>
          <span>模板市场</span>
        </el-menu-item>
        <el-menu-item index="/plugins/marketplace">
          <el-icon><Grid /></el-icon>
          <span>插件市场</span>
        </el-menu-item>
        <el-menu-item index="/plugins/installed">
          <el-icon><Box /></el-icon>
          <span>已安装插件</span>
        </el-menu-item>
        <el-menu-item index="/performance">
          <el-icon><TrendCharts /></el-icon>
          <span>性能监控</span>
        </el-menu-item>
        <el-sub-menu index="/enterprise">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>企业管理</span>
          </template>
          <el-menu-item index="/organizations">
            <el-icon><OfficeBuilding /></el-icon>
            <span>组织管理</span>
          </el-menu-item>
          <el-menu-item index="/teams">
            <el-icon><UserFilled /></el-icon>
            <span>团队管理</span>
          </el-menu-item>
          <el-menu-item index="/quotas">
            <el-icon><DataLine /></el-icon>
            <span>配额监控</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <!-- Mobile Menu Button -->
        <el-button
          v-if="isMobile"
          class="mobile-menu-btn"
          circle
          @click="toggleMobileMenu"
          :icon="Menu"
        />

        <!-- Desktop Collapse Button -->
        <el-button
          v-if="!isMobile"
          class="collapse-btn"
          circle
          @click="toggleCollapse"
          :icon="isCollapsed ? Expand : Fold"
        />

        <div class="header-left">
          <el-breadcrumb separator="/" v-if="!isMobile || !showBreadcrumbOnMobile">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute">{{ currentRoute }}</el-breadcrumb-item>
          </el-breadcrumb>
          <span v-else class="mobile-title">{{ currentRoute || 'ResoftAI' }}</span>
        </div>
        <div class="header-right">
          <el-badge :value="notifications" class="notification-badge" v-if="!isMobile">
            <el-icon :size="20"><Bell /></el-icon>
          </el-badge>
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="isMobile ? 28 : 32">Admin</el-avatar>
              <span class="username" v-if="!isMobile">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, Expand, Fold } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const notifications = ref(3)
const isCollapsed = ref(false)
const mobileMenuOpen = ref(false)
const windowWidth = ref(window.innerWidth)

// Check if mobile
const isMobile = computed(() => windowWidth.value < 768)

// Sidebar width based on state
const sidebarWidth = computed(() => {
  if (isMobile.value) return '250px'
  return isCollapsed.value ? '64px' : '250px'
})

// Show breadcrumb on mobile
const showBreadcrumbOnMobile = computed(() => windowWidth.value < 480)

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route.meta?.title || '')

// Handle window resize
const handleResize = () => {
  windowWidth.value = window.innerWidth
  if (!isMobile.value && mobileMenuOpen.value) {
    mobileMenuOpen.value = false
  }
}

// Toggle mobile menu
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// Close mobile menu
const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// Toggle sidebar collapse (desktop)
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// Handle menu selection (close mobile menu after selection)
const handleMenuSelect = () => {
  if (isMobile.value) {
    closeMobileMenu()
  }
}

const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      console.log('个人信息')
      break
    case 'settings':
      console.log('系统设置')
      break
    case 'logout':
      router.push('/login')
      break
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  position: relative;
}

// Mobile overlay
.mobile-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  transition: opacity 0.3s ease;

  &.is-active {
    display: block;
  }
}

.sidebar {
  background-color: #304156;
  color: #fff;
  transition: width 0.3s ease;
  position: relative;
  z-index: 1000;

  &.mobile-sidebar {
    position: fixed;
    left: -250px;
    top: 0;
    bottom: 0;
    width: 250px !important;
    transition: left 0.3s ease;

    &.is-open {
      left: 0;
      box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
    }
  }

  .logo {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 20px;
    font-weight: bold;
    color: #fff;
    border-bottom: 1px solid #1f2d3d;
    transition: all 0.3s ease;

    span {
      transition: opacity 0.3s ease;
    }
  }

  .el-menu {
    border: none;
    height: calc(100vh - 50px);
    overflow-y: auto;
    overflow-x: hidden;

    // Custom scrollbar
    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: #1f2d3d;
    }

    &::-webkit-scrollbar-thumb {
      background: #409eff;
      border-radius: 3px;
    }
  }
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  position: relative;
  z-index: 100;
  gap: 12px;

  .mobile-menu-btn,
  .collapse-btn {
    margin-right: 12px;
  }

  .header-left {
    flex: 1;
    min-width: 0; // Allow text truncation

    .mobile-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;
    flex-shrink: 0;

    .notification-badge {
      cursor: pointer;
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;

      .username {
        font-size: 14px;
      }
    }
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// Mobile responsive styles
@media (max-width: 767px) {
  .header {
    padding: 0 12px;
    height: auto !important;
    min-height: 50px;

    .header-right {
      gap: 12px;
    }
  }

  .main-content {
    padding: 12px;
  }

  // Make breadcrumb scrollable on very small screens
  .el-breadcrumb {
    overflow-x: auto;
    white-space: nowrap;
    -webkit-overflow-scrolling: touch;

    &::-webkit-scrollbar {
      display: none;
    }
  }
}

@media (max-width: 480px) {
  .header {
    padding: 0 8px;
    gap: 8px;

    .mobile-menu-btn {
      margin-right: 8px;
    }
  }

  .main-content {
    padding: 8px;
  }
}

// Tablet styles
@media (min-width: 768px) and (max-width: 991px) {
  .header {
    .header-right {
      gap: 16px;
    }
  }

  .main-content {
    padding: 16px;
  }
}

// Print styles
@media print {
  .sidebar,
  .header {
    display: none !important;
  }

  .main-content {
    padding: 0 !important;
    background-color: #fff !important;
  }
}
</style>
