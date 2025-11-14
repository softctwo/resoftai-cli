import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板', icon: 'DataAnalysis' }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: () => import('@/views/Projects.vue'),
        meta: { title: '项目管理', icon: 'FolderOpened' }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/ProjectDetail.vue'),
        meta: { title: '项目详情', icon: 'Document' }
      },
      {
        path: 'agents',
        name: 'Agents',
        component: () => import('@/views/Agents.vue'),
        meta: { title: '智能体管理', icon: 'UserFilled' }
      },
      {
        path: 'files',
        name: 'Files',
        component: () => import('@/views/FilesEnhanced.vue'),
        meta: { title: '文件管理', icon: 'Files' }
      },
      {
        path: 'models',
        name: 'Models',
        component: () => import('@/views/Models.vue'),
        meta: { title: '模型配置', icon: 'Setting' }
      },
      {
        path: 'code-quality',
        name: 'CodeQuality',
        component: () => import('@/views/CodeQualityChecker.vue'),
        meta: { title: '代码质量检查', icon: 'DocumentChecked' }
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import('@/views/TemplateMarketplace.vue'),
        meta: { title: '模板市场', icon: 'Box' }
      },
      {
        path: 'performance',
        name: 'Performance',
        component: () => import('@/views/PerformanceMonitor.vue'),
        meta: { title: '性能监控', icon: 'Odometer' }
      },
      {
        path: 'organizations',
        name: 'Organizations',
        component: () => import('@/views/OrganizationManagement.vue'),
        meta: { title: '组织管理', icon: 'OfficeBuilding' }
      },
      {
        path: 'teams',
        name: 'Teams',
        component: () => import('@/views/TeamManagement.vue'),
        meta: { title: '团队管理', icon: 'PictureFilled' }
      },
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Authentication guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Allow access to login page
  if (to.path === '/login') {
    // If already logged in, redirect to dashboard
    if (authStore.isAuthenticated) {
      next('/')
      return
    }
    next()
    return
  }

  // Check authentication for all other routes
  if (!authStore.isAuthenticated) {
    next('/login')
    return
  }

  next()
})

export default router
