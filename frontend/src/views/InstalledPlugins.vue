<template>
  <div class="installed-plugins">
    <div class="page-header">
      <h1>已安装插件</h1>
      <div class="header-actions">
        <button @click="$router.push('/plugins/marketplace')" class="btn btn-secondary">
          <i class="fas fa-store"></i>
          浏览市场
        </button>
        <button @click="checkAllUpdates" class="btn btn-primary" :disabled="checking">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': checking }"></i>
          检查更新
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-cards">
      <div class="stat-card">
        <i class="fas fa-box"></i>
        <div>
          <div class="stat-value">{{ installedPlugins.length }}</div>
          <div class="stat-label">已安装</div>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-exclamation-circle" style="color: #FF9800;"></i>
        <div>
          <div class="stat-value">{{ availableUpdates.length }}</div>
          <div class="stat-label">可更新</div>
        </div>
      </div>
      <div class="stat-card">
        <i class="fas fa-check-circle" style="color: #4CAF50;"></i>
        <div>
          <div class="stat-value">{{ activePlugins }}</div>
          <div class="stat-label">已激活</div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
      <p>加载中...</p>
    </div>

    <!-- 插件列表 -->
    <div v-else-if="installedPlugins.length > 0" class="plugins-section">
      <!-- 有更新的插件 -->
      <section v-if="pluginsWithUpdates.length > 0" class="update-section">
        <h2>
          <i class="fas fa-arrow-circle-up"></i>
          可更新插件 ({{ pluginsWithUpdates.length }})
        </h2>
        <div class="plugins-list">
          <div v-for="plugin in pluginsWithUpdates" :key="plugin.slug" class="plugin-item update-available">
            <div class="plugin-icon">
              <i :class="getPluginIcon(plugin.category)"></i>
            </div>

            <div class="plugin-info">
              <div class="plugin-header">
                <h3>{{ plugin.name }}</h3>
                <span class="update-badge">
                  <i class="fas fa-arrow-up"></i>
                  v{{ plugin.version }} → v{{ getUpdateVersion(plugin.slug) }}
                </span>
              </div>
              <p class="plugin-description">{{ plugin.description }}</p>
              <div class="plugin-meta">
                <span><i class="fas fa-user"></i> {{ plugin.author }}</span>
                <span><i class="fas fa-calendar"></i> 安装于 {{ formatDate(plugin.installed_at) }}</span>
              </div>
            </div>

            <div class="plugin-actions">
              <button
                @click="updatePlugin(plugin.slug)"
                class="btn btn-success"
                :disabled="updating[plugin.slug]">
                <i class="fas fa-sync-alt"></i>
                {{ updating[plugin.slug] ? '更新中...' : '更新' }}
              </button>
              <button
                @click="viewDetails(plugin.slug)"
                class="btn btn-secondary">
                <i class="fas fa-info-circle"></i>
                详情
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 已安装的插件 -->
      <section class="installed-section">
        <h2>
          <i class="fas fa-box"></i>
          所有已安装插件 ({{ installedPlugins.length }})
        </h2>

        <!-- 筛选和搜索 -->
        <div class="filters">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索插件..."
            class="search-input"
          />
          <select v-model="filterCategory" class="filter-select">
            <option value="">所有分类</option>
            <option value="agent">智能体插件</option>
            <option value="llm">LLM提供商</option>
            <option value="code-quality">代码质量</option>
            <option value="integration">集成插件</option>
            <option value="tool">工具插件</option>
          </select>
        </div>

        <div class="plugins-list">
          <div v-for="plugin in filteredPlugins" :key="plugin.slug" class="plugin-item">
            <div class="plugin-icon">
              <i :class="getPluginIcon(plugin.category)"></i>
            </div>

            <div class="plugin-info">
              <div class="plugin-header">
                <h3>{{ plugin.name }}</h3>
                <span :class="['status-badge', plugin.active ? 'active' : 'inactive']">
                  {{ plugin.active ? '已激活' : '未激活' }}
                </span>
              </div>
              <p class="plugin-description">{{ plugin.description }}</p>
              <div class="plugin-meta">
                <span><i class="fas fa-user"></i> {{ plugin.author }}</span>
                <span><i class="fas fa-code-branch"></i> v{{ plugin.version }}</span>
                <span><i class="fas fa-calendar"></i> 安装于 {{ formatDate(plugin.installed_at) }}</span>
              </div>
            </div>

            <div class="plugin-actions">
              <button
                v-if="!plugin.active"
                @click="activatePlugin(plugin.slug)"
                class="btn btn-success"
                :disabled="activating[plugin.slug]">
                <i class="fas fa-play"></i>
                {{ activating[plugin.slug] ? '激活中...' : '激活' }}
              </button>
              <button
                v-else
                @click="deactivatePlugin(plugin.slug)"
                class="btn btn-warning"
                :disabled="deactivating[plugin.slug]">
                <i class="fas fa-pause"></i>
                {{ deactivating[plugin.slug] ? '停用中...' : '停用' }}
              </button>
              <button
                @click="viewDetails(plugin.slug)"
                class="btn btn-secondary">
                <i class="fas fa-info-circle"></i>
                详情
              </button>
              <button
                @click="uninstallPlugin(plugin.slug)"
                class="btn btn-danger"
                :disabled="uninstalling[plugin.slug]">
                <i class="fas fa-trash"></i>
                {{ uninstalling[plugin.slug] ? '卸载中...' : '卸载' }}
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <i class="fas fa-inbox fa-4x"></i>
      <h3>还没有安装任何插件</h3>
      <p>浏览插件市场，发现有用的插件</p>
      <button @click="$router.push('/plugins/marketplace')" class="btn btn-primary btn-lg">
        <i class="fas fa-store"></i>
        浏览插件市场
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

export default {
  name: 'InstalledPlugins',

  setup() {
    const router = useRouter()

    const loading = ref(true)
    const checking = ref(false)
    const searchQuery = ref('')
    const filterCategory = ref('')

    const installedPlugins = ref([])
    const availableUpdates = ref({})

    const updating = reactive({})
    const activating = reactive({})
    const deactivating = reactive({})
    const uninstalling = reactive({})

    const activePlugins = computed(() => {
      return installedPlugins.value.filter(p => p.active).length
    })

    const pluginsWithUpdates = computed(() => {
      return installedPlugins.value.filter(p =>
        p.slug in availableUpdates.value
      )
    })

    const filteredPlugins = computed(() => {
      let plugins = installedPlugins.value

      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        plugins = plugins.filter(p =>
          p.name.toLowerCase().includes(query) ||
          p.description.toLowerCase().includes(query) ||
          p.author.toLowerCase().includes(query)
        )
      }

      // 分类过滤
      if (filterCategory.value) {
        plugins = plugins.filter(p => p.category === filterCategory.value)
      }

      return plugins
    })

    const loadInstalledPlugins = async () => {
      loading.value = true
      try {
        const response = await api.get('/marketplace/plugins/installed')
        installedPlugins.value = response.data.map(plugin => ({
          ...plugin,
          active: true, // 假设已安装的都是激活的，实际应该从API获取
          installed_at: new Date().toISOString() // 假设安装时间，实际应该从API获取
        }))
      } catch (error) {
        console.error('Failed to load installed plugins:', error)
      } finally {
        loading.value = false
      }
    }

    const checkAllUpdates = async () => {
      checking.value = true
      try {
        const response = await api.get('/marketplace/updates/check')
        availableUpdates.value = response.data.updates_available || {}

        if (Object.keys(availableUpdates.value).length > 0) {
          alert(`发现 ${Object.keys(availableUpdates.value).length} 个可用更新！`)
        } else {
          alert('所有插件都是最新版本')
        }
      } catch (error) {
        console.error('Failed to check updates:', error)
        alert('检查更新失败')
      } finally {
        checking.value = false
      }
    }

    const updatePlugin = async (slug) => {
      if (!confirm(`确定要更新插件 "${slug}" 吗？`)) {
        return
      }

      updating[slug] = true
      try {
        await api.post(`/marketplace/plugins/${slug}/update`)
        alert('更新成功！')
        await loadInstalledPlugins()
        await checkAllUpdates()
      } catch (error) {
        console.error('Failed to update plugin:', error)
        alert(`更新失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        updating[slug] = false
      }
    }

    const activatePlugin = async (slug) => {
      activating[slug] = true
      try {
        // TODO: 调用激活API
        await new Promise(resolve => setTimeout(resolve, 1000))
        alert('插件已激活')
        await loadInstalledPlugins()
      } catch (error) {
        console.error('Failed to activate plugin:', error)
        alert('激活失败')
      } finally {
        activating[slug] = false
      }
    }

    const deactivatePlugin = async (slug) => {
      deactivating[slug] = true
      try {
        // TODO: 调用停用API
        await new Promise(resolve => setTimeout(resolve, 1000))
        alert('插件已停用')
        await loadInstalledPlugins()
      } catch (error) {
        console.error('Failed to deactivate plugin:', error)
        alert('停用失败')
      } finally {
        deactivating[slug] = false
      }
    }

    const uninstallPlugin = async (slug) => {
      if (!confirm(`确定要卸载插件 "${slug}" 吗？此操作不可恢复。`)) {
        return
      }

      uninstalling[slug] = true
      try {
        await api.post(`/marketplace/plugins/${slug}/uninstall`)
        alert('卸载成功！')
        await loadInstalledPlugins()
      } catch (error) {
        console.error('Failed to uninstall plugin:', error)
        alert(`卸载失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        uninstalling[slug] = false
      }
    }

    const viewDetails = (slug) => {
      router.push(`/plugins/${slug}`)
    }

    const getUpdateVersion = (slug) => {
      return availableUpdates.value[slug] || '未知'
    }

    const getPluginIcon = (category) => {
      const icons = {
        'agent': 'fas fa-robot',
        'llm': 'fas fa-brain',
        'code-quality': 'fas fa-check-circle',
        'integration': 'fas fa-plug',
        'tool': 'fas fa-tools'
      }
      return icons[category] || 'fas fa-puzzle-piece'
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadInstalledPlugins()
      checkAllUpdates()
    })

    return {
      loading,
      checking,
      searchQuery,
      filterCategory,
      installedPlugins,
      availableUpdates,
      activePlugins,
      pluginsWithUpdates,
      filteredPlugins,
      updating,
      activating,
      deactivating,
      uninstalling,
      checkAllUpdates,
      updatePlugin,
      activatePlugin,
      deactivatePlugin,
      uninstallPlugin,
      viewDetails,
      getUpdateVersion,
      getPluginIcon,
      formatDate
    }
  }
}
</script>

<style scoped>
.installed-plugins {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-card i {
  font-size: 32px;
  color: #2196F3;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s;
}

.btn-lg {
  padding: 12px 32px;
  font-size: 16px;
}

.btn-primary {
  background: #2196F3;
  color: white;
}

.btn-primary:hover {
  background: #1976D2;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover {
  background: #616161;
}

.btn-success {
  background: #4CAF50;
  color: white;
}

.btn-success:hover {
  background: #45a049;
}

.btn-warning {
  background: #FF9800;
  color: white;
}

.btn-warning:hover {
  background: #F57C00;
}

.btn-danger {
  background: #F44336;
  color: white;
}

.btn-danger:hover {
  background: #D32F2F;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 加载和空状态 */
.loading,
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}

.loading i,
.empty-state i {
  color: #2196F3;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #333;
}

.empty-state p {
  margin-bottom: 20px;
}

/* 插件区域 */
.plugins-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.update-section h2,
.installed-section h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 20px;
}

/* 筛选 */
.filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.search-input,
.filter-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input {
  flex: 1;
}

.filter-select {
  min-width: 200px;
}

/* 插件列表 */
.plugins-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.plugin-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
}

.plugin-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.plugin-item.update-available {
  border-left: 4px solid #FF9800;
}

.plugin-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.plugin-icon i {
  font-size: 28px;
  color: white;
}

.plugin-info {
  flex: 1;
}

.plugin-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.plugin-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: #4CAF50;
  color: white;
}

.status-badge.inactive {
  background: #999;
  color: white;
}

.update-badge {
  background: #FF9800;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.plugin-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
}

.plugin-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #666;
}

.plugin-meta i {
  margin-right: 5px;
}

.plugin-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .plugin-item {
    flex-direction: column;
    align-items: stretch;
  }

  .plugin-actions {
    flex-direction: column;
  }

  .plugin-actions button {
    width: 100%;
  }

  .filters {
    flex-direction: column;
  }
}
</style>
