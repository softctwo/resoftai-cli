<template>
  <div class="plugin-marketplace">
    <div class="page-header">
      <h1>插件市场</h1>
      <div class="header-actions">
        <button @click="$router.push('/plugins/installed')" class="btn btn-secondary">
          <i class="fas fa-box"></i>
          已安装插件
        </button>
        <button @click="checkUpdates" class="btn btn-primary" :disabled="checkingUpdates">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': checkingUpdates }"></i>
          检查更新
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="搜索插件名称、标签或作者..."
          class="search-input"
        />
      </div>

      <div class="filters">
        <select v-model="selectedCategory" @change="applyFilters" class="filter-select">
          <option value="">所有分类</option>
          <option value="agent">智能体插件</option>
          <option value="llm">LLM提供商</option>
          <option value="code-quality">代码质量</option>
          <option value="integration">集成插件</option>
          <option value="tool">工具插件</option>
        </select>

        <select v-model="sortBy" @change="applyFilters" class="filter-select">
          <option value="popular">最受欢迎</option>
          <option value="recent">最新发布</option>
          <option value="rating">最高评分</option>
          <option value="downloads">下载最多</option>
        </select>
      </div>
    </div>

    <!-- 标签页 -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id; loadPlugins()">
        <i :class="tab.icon"></i>
        {{ tab.label }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
      <p>加载中...</p>
    </div>

    <!-- 插件列表 -->
    <div v-else-if="displayedPlugins.length > 0" class="plugins-grid">
      <div
        v-for="plugin in displayedPlugins"
        :key="plugin.slug"
        class="plugin-card"
        @click="viewPluginDetail(plugin.slug)">

        <div class="plugin-icon">
          <i :class="getPluginIcon(plugin.category)"></i>
        </div>

        <div class="plugin-info">
          <div class="plugin-header">
            <h3>{{ plugin.name }}</h3>
            <span v-if="isInstalled(plugin.slug)" class="installed-badge">
              <i class="fas fa-check"></i> 已安装
            </span>
          </div>

          <p class="plugin-description">{{ plugin.description }}</p>

          <div class="plugin-meta">
            <span class="author">
              <i class="fas fa-user"></i>
              {{ plugin.author }}
            </span>
            <span class="version">
              <i class="fas fa-code-branch"></i>
              {{ plugin.version }}
            </span>
          </div>

          <div class="plugin-stats">
            <span class="rating">
              <i class="fas fa-star" style="color: #FFD700;"></i>
              {{ plugin.rating.toFixed(1) }}
              <small>({{ plugin.review_count }})</small>
            </span>
            <span class="downloads">
              <i class="fas fa-download"></i>
              {{ formatNumber(plugin.downloads) }}
            </span>
          </div>

          <div class="plugin-tags">
            <span v-for="tag in plugin.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="plugin-actions" @click.stop>
          <button
            v-if="!isInstalled(plugin.slug)"
            @click="installPlugin(plugin.slug)"
            class="btn btn-primary btn-sm"
            :disabled="installing[plugin.slug]">
            <i class="fas fa-download"></i>
            {{ installing[plugin.slug] ? '安装中...' : '安装' }}
          </button>
          <button
            v-else
            @click="uninstallPlugin(plugin.slug)"
            class="btn btn-danger btn-sm"
            :disabled="uninstalling[plugin.slug]">
            <i class="fas fa-trash"></i>
            {{ uninstalling[plugin.slug] ? '卸载中...' : '卸载' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <i class="fas fa-puzzle-piece fa-4x"></i>
      <h3>未找到插件</h3>
      <p>尝试调整搜索条件或浏览其他分类</p>
    </div>

    <!-- 更新通知 -->
    <div v-if="updates.length > 0" class="update-banner">
      <i class="fas fa-exclamation-circle"></i>
      <span>有 {{ updates.length }} 个插件可以更新</span>
      <button @click="$router.push('/plugins/installed')" class="btn btn-sm">
        查看更新
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

export default {
  name: 'PluginMarketplace',

  setup() {
    const router = useRouter()

    const loading = ref(false)
    const checkingUpdates = ref(false)
    const searchQuery = ref('')
    const selectedCategory = ref('')
    const sortBy = ref('popular')
    const activeTab = ref('all')

    const allPlugins = ref([])
    const installedPlugins = ref([])
    const featuredPlugins = ref([])
    const popularPlugins = ref([])
    const updates = ref([])

    const installing = reactive({})
    const uninstalling = reactive({})

    const tabs = [
      { id: 'all', label: '全部插件', icon: 'fas fa-th' },
      { id: 'featured', label: '精选推荐', icon: 'fas fa-star' },
      { id: 'popular', label: '热门插件', icon: 'fas fa-fire' }
    ]

    const displayedPlugins = computed(() => {
      let plugins = []

      if (activeTab.value === 'featured') {
        plugins = featuredPlugins.value
      } else if (activeTab.value === 'popular') {
        plugins = popularPlugins.value
      } else {
        plugins = allPlugins.value
      }

      // 应用搜索
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        plugins = plugins.filter(p =>
          p.name.toLowerCase().includes(query) ||
          p.description.toLowerCase().includes(query) ||
          p.author.toLowerCase().includes(query) ||
          (p.tags && p.tags.some(tag => tag.toLowerCase().includes(query)))
        )
      }

      // 应用分类筛选
      if (selectedCategory.value) {
        plugins = plugins.filter(p => p.category === selectedCategory.value)
      }

      // 排序
      return sortPlugins(plugins, sortBy.value)
    })

    const sortPlugins = (plugins, sortKey) => {
      const sorted = [...plugins]
      switch (sortKey) {
        case 'popular':
          return sorted.sort((a, b) => b.downloads - a.downloads)
        case 'rating':
          return sorted.sort((a, b) => b.rating - a.rating)
        case 'recent':
          return sorted.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        case 'downloads':
          return sorted.sort((a, b) => b.downloads - a.downloads)
        default:
          return sorted
      }
    }

    const loadPlugins = async () => {
      loading.value = true
      try {
        // 根据活动tab加载不同的插件列表
        if (activeTab.value === 'all') {
          const response = await api.get('/marketplace/plugins')
          allPlugins.value = response.data
        } else if (activeTab.value === 'featured') {
          const response = await api.get('/marketplace/plugins/featured')
          featuredPlugins.value = response.data
        } else if (activeTab.value === 'popular') {
          const response = await api.get('/marketplace/plugins/popular?limit=20')
          popularPlugins.value = response.data
        }

        // 加载已安装插件
        await loadInstalledPlugins()
      } catch (error) {
        console.error('Failed to load plugins:', error)
      } finally {
        loading.value = false
      }
    }

    const loadInstalledPlugins = async () => {
      try {
        const response = await api.get('/marketplace/plugins/installed')
        installedPlugins.value = response.data
      } catch (error) {
        console.error('Failed to load installed plugins:', error)
      }
    }

    const handleSearch = () => {
      // 搜索会自动通过computed属性触发
    }

    const applyFilters = () => {
      // 筛选会自动通过computed属性触发
    }

    const checkUpdates = async () => {
      checkingUpdates.value = true
      try {
        const response = await api.get('/marketplace/updates/check')
        updates.value = Object.entries(response.data.updates_available).map(
          ([slug, version]) => ({ slug, version })
        )

        if (updates.value.length > 0) {
          alert(`发现 ${updates.value.length} 个可用更新！`)
        } else {
          alert('所有插件都是最新版本')
        }
      } catch (error) {
        console.error('Failed to check updates:', error)
        alert('检查更新失败')
      } finally {
        checkingUpdates.value = false
      }
    }

    const installPlugin = async (slug) => {
      if (!confirm(`确定要安装插件 "${slug}" 吗？`)) {
        return
      }

      installing[slug] = true
      try {
        await api.post(`/marketplace/plugins/${slug}/install`, {
          slug: slug,
          auto_dependencies: true
        })

        alert(`插件 "${slug}" 安装成功！`)
        await loadInstalledPlugins()
      } catch (error) {
        console.error('Failed to install plugin:', error)
        alert(`安装失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        installing[slug] = false
      }
    }

    const uninstallPlugin = async (slug) => {
      if (!confirm(`确定要卸载插件 "${slug}" 吗？此操作不可恢复。`)) {
        return
      }

      uninstalling[slug] = true
      try {
        await api.post(`/marketplace/plugins/${slug}/uninstall`)

        alert(`插件 "${slug}" 已成功卸载`)
        await loadInstalledPlugins()
      } catch (error) {
        console.error('Failed to uninstall plugin:', error)
        alert(`卸载失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        uninstalling[slug] = false
      }
    }

    const viewPluginDetail = (slug) => {
      router.push(`/plugins/${slug}`)
    }

    const isInstalled = (slug) => {
      return installedPlugins.value.some(p => p.slug === slug)
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

    const formatNumber = (num) => {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    }

    onMounted(() => {
      loadPlugins()
    })

    return {
      loading,
      checkingUpdates,
      searchQuery,
      selectedCategory,
      sortBy,
      activeTab,
      tabs,
      displayedPlugins,
      installing,
      uninstalling,
      updates,
      loadPlugins,
      handleSearch,
      applyFilters,
      checkUpdates,
      installPlugin,
      uninstallPlugin,
      viewPluginDetail,
      isInstalled,
      getPluginIcon,
      formatNumber
    }
  }
}
</script>

<style scoped>
.plugin-marketplace {
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

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

/* 搜索和筛选 */
.search-filters {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.search-box {
  position: relative;
  margin-bottom: 15px;
}

.search-box i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 45px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #2196F3;
}

.filters {
  display: flex;
  gap: 15px;
}

.filter-select {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

/* 标签页 */
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  padding: 12px 24px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 3px solid transparent;
}

.tab:hover {
  color: #2196F3;
}

.tab.active {
  color: #2196F3;
  border-bottom-color: #2196F3;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.loading i {
  color: #2196F3;
  margin-bottom: 20px;
}

/* 插件网格 */
.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.plugin-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
}

.plugin-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.plugin-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 15px;
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
  justify-content: space-between;
  align-items: start;
  margin-bottom: 10px;
}

.plugin-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.installed-badge {
  background: #4CAF50;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.plugin-description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.plugin-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #666;
}

.plugin-meta i {
  margin-right: 5px;
}

.plugin-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  font-size: 13px;
}

.rating,
.downloads {
  display: flex;
  align-items: center;
  gap: 5px;
}

.rating small {
  color: #999;
}

.plugin-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.tag {
  background: #f0f0f0;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
}

.plugin-actions {
  margin-top: auto;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.plugin-actions button {
  width: 100%;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
}

.empty-state i {
  margin-bottom: 20px;
  color: #ddd;
}

.empty-state h3 {
  color: #666;
  margin-bottom: 10px;
}

/* 更新横幅 */
.update-banner {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #FF9800;
  color: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.update-banner i {
  font-size: 20px;
}

.update-banner button {
  background: white;
  color: #FF9800;
  font-weight: 600;
}

.update-banner button:hover {
  background: #f5f5f5;
}

/* 响应式 */
@media (max-width: 768px) {
  .plugins-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }

  .filters {
    flex-direction: column;
  }

  .update-banner {
    left: 20px;
    right: 20px;
  }
}
</style>
