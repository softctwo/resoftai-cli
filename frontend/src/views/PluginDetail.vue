<template>
  <div class="plugin-detail">
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin fa-3x"></i>
      <p>加载中...</p>
    </div>

    <div v-else-if="plugin" class="detail-container">
      <!-- 返回按钮 -->
      <button @click="$router.back()" class="btn-back">
        <i class="fas fa-arrow-left"></i>
        返回
      </button>

      <!-- 插件头部 -->
      <div class="plugin-header">
        <div class="plugin-icon-large">
          <i :class="getPluginIcon(plugin.category)"></i>
        </div>

        <div class="plugin-title-section">
          <h1>{{ plugin.name }}</h1>
          <p class="plugin-author">
            作者: <strong>{{ plugin.author }}</strong>
          </p>

          <div class="plugin-stats-row">
            <span class="stat">
              <i class="fas fa-star" style="color: #FFD700;"></i>
              {{ plugin.rating.toFixed(1) }}
              <small>({{ plugin.review_count }} 评价)</small>
            </span>
            <span class="stat">
              <i class="fas fa-download"></i>
              {{ formatNumber(plugin.downloads) }} 下载
            </span>
            <span class="stat">
              <i class="fas fa-code-branch"></i>
              v{{ plugin.version }}
            </span>
            <span v-if="plugin.min_platform_version" class="stat">
              <i class="fas fa-cube"></i>
              需要 v{{ plugin.min_platform_version }}+
            </span>
          </div>

          <div class="plugin-tags">
            <span class="category-badge">{{ getCategoryName(plugin.category) }}</span>
            <span v-for="tag in plugin.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
        </div>

        <div class="plugin-actions">
          <button
            v-if="!isInstalled"
            @click="installPlugin"
            class="btn btn-primary btn-lg"
            :disabled="installing">
            <i class="fas fa-download"></i>
            {{ installing ? '安装中...' : '安装插件' }}
          </button>

          <template v-else>
            <button
              @click="updatePlugin"
              class="btn btn-success btn-lg"
              :disabled="updating || !hasUpdate">
              <i class="fas fa-sync-alt"></i>
              {{ updating ? '更新中...' : hasUpdate ? '更新插件' : '已是最新' }}
            </button>
            <button
              @click="uninstallPlugin"
              class="btn btn-danger"
              :disabled="uninstalling">
              <i class="fas fa-trash"></i>
              {{ uninstalling ? '卸载中...' : '卸载' }}
            </button>
          </template>
        </div>
      </div>

      <!-- 内容标签页 -->
      <div class="content-tabs">
        <button
          v-for="tab in contentTabs"
          :key="tab.id"
          :class="['tab', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id">
          <i :class="tab.icon"></i>
          {{ tab.label }}
        </button>
      </div>

      <!-- 标签页内容 -->
      <div class="tab-content">
        <!-- 概述 -->
        <div v-show="activeTab === 'overview'" class="overview-tab">
          <section class="detail-section">
            <h2>插件描述</h2>
            <p class="description">{{ plugin.description }}</p>
          </section>

          <section v-if="plugin.dependencies && plugin.dependencies.length > 0" class="detail-section">
            <h2>依赖项</h2>
            <div class="dependencies">
              <span v-for="dep in plugin.dependencies" :key="dep" class="dependency-item">
                <i class="fas fa-puzzle-piece"></i>
                {{ dep }}
              </span>
            </div>
          </section>

          <section class="detail-section">
            <h2>链接</h2>
            <div class="links">
              <a v-if="plugin.homepage" :href="plugin.homepage" target="_blank" class="link-item">
                <i class="fas fa-home"></i>
                主页
              </a>
              <a v-if="plugin.repository" :href="plugin.repository" target="_blank" class="link-item">
                <i class="fab fa-github"></i>
                仓库
              </a>
            </div>
          </section>
        </div>

        <!-- 版本历史 -->
        <div v-show="activeTab === 'versions'" class="versions-tab">
          <section class="detail-section">
            <h2>版本历史</h2>
            <div v-if="loadingVersions" class="loading-small">
              <i class="fas fa-spinner fa-spin"></i> 加载中...
            </div>
            <div v-else-if="versions.length > 0" class="versions-list">
              <div v-for="version in versions" :key="version" class="version-item">
                <span class="version-number">v{{ version }}</span>
                <span v-if="version === plugin.version" class="current-badge">当前</span>
              </div>
            </div>
            <p v-else>暂无版本历史</p>
          </section>
        </div>

        <!-- 评价 -->
        <div v-show="activeTab === 'reviews'" class="reviews-tab">
          <section class="detail-section">
            <div class="reviews-header">
              <h2>用户评价</h2>
              <button @click="showReviewForm = !showReviewForm" class="btn btn-primary">
                <i class="fas fa-plus"></i>
                写评价
              </button>
            </div>

            <!-- 评价表单 -->
            <div v-if="showReviewForm" class="review-form">
              <h3>发表您的评价</h3>
              <div class="rating-input">
                <label>评分:</label>
                <div class="stars">
                  <i
                    v-for="star in 5"
                    :key="star"
                    :class="['fas fa-star', { active: star <= newReview.rating }]"
                    @click="newReview.rating = star"
                    @mouseover="hoverRating = star"
                    @mouseleave="hoverRating = 0"
                    :style="{ color: star <= (hoverRating || newReview.rating) ? '#FFD700' : '#ddd' }">
                  </i>
                </div>
              </div>
              <textarea
                v-model="newReview.comment"
                placeholder="分享您的使用体验..."
                class="review-textarea"
                rows="4">
              </textarea>
              <div class="form-actions">
                <button @click="submitReview" class="btn btn-primary" :disabled="submitting">
                  {{ submitting ? '提交中...' : '提交评价' }}
                </button>
                <button @click="showReviewForm = false" class="btn btn-secondary">
                  取消
                </button>
              </div>
            </div>

            <!-- 评价列表 -->
            <div v-if="loadingReviews" class="loading-small">
              <i class="fas fa-spinner fa-spin"></i> 加载评价中...
            </div>
            <div v-else-if="reviews.length > 0" class="reviews-list">
              <div v-for="review in reviews" :key="review.id" class="review-item">
                <div class="review-header">
                  <strong>{{ review.user_name }}</strong>
                  <div class="review-stars">
                    <i
                      v-for="star in 5"
                      :key="star"
                      :class="['fas fa-star', { active: star <= review.rating }]"
                      :style="{ color: star <= review.rating ? '#FFD700' : '#ddd' }">
                    </i>
                  </div>
                  <span class="review-date">{{ formatDate(review.created_at) }}</span>
                </div>
                <p class="review-comment">{{ review.comment }}</p>
                <div class="review-actions">
                  <button class="helpful-btn">
                    <i class="fas fa-thumbs-up"></i>
                    有帮助 ({{ review.helpful_count }})
                  </button>
                </div>
              </div>
            </div>
            <p v-else>暂无评价，成为第一个评价的人吧！</p>
          </section>
        </div>
      </div>
    </div>

    <div v-else class="error-state">
      <i class="fas fa-exclamation-triangle fa-3x"></i>
      <h3>插件未找到</h3>
      <button @click="$router.back()" class="btn btn-primary">
        返回插件市场
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/utils/api'

export default {
  name: 'PluginDetail',

  setup() {
    const route = useRoute()
    const router = useRouter()
    const slug = route.params.slug

    const loading = ref(true)
    const plugin = ref(null)
    const isInstalled = ref(false)
    const hasUpdate = ref(false)

    const installing = ref(false)
    const uninstalling = ref(false)
    const updating = ref(false)

    const activeTab = ref('overview')
    const contentTabs = [
      { id: 'overview', label: '概述', icon: 'fas fa-info-circle' },
      { id: 'versions', label: '版本历史', icon: 'fas fa-history' },
      { id: 'reviews', label: '评价', icon: 'fas fa-star' }
    ]

    const versions = ref([])
    const loadingVersions = ref(false)

    const reviews = ref([])
    const loadingReviews = ref(false)
    const showReviewForm = ref(false)
    const submitting = ref(false)
    const hoverRating = ref(0)

    const newReview = reactive({
      rating: 5,
      comment: ''
    })

    const loadPluginDetail = async () => {
      loading.value = true
      try {
        const response = await api.get(`/marketplace/plugins/${slug}`)
        plugin.value = response.data

        // 检查是否已安装
        await checkInstalled()

        // 加载版本和评价
        loadVersions()
        loadReviews()
      } catch (error) {
        console.error('Failed to load plugin detail:', error)
      } finally {
        loading.value = false
      }
    }

    const checkInstalled = async () => {
      try {
        const response = await api.get('/marketplace/plugins/installed')
        isInstalled.value = response.data.some(p => p.slug === slug)

        if (isInstalled.value) {
          // 检查是否有更新
          const updatesResponse = await api.get('/marketplace/updates/check')
          hasUpdate.value = slug in updatesResponse.data.updates_available
        }
      } catch (error) {
        console.error('Failed to check installation:', error)
      }
    }

    const loadVersions = async () => {
      loadingVersions.value = true
      try {
        const response = await api.get(`/marketplace/plugins/${slug}/versions`)
        versions.value = response.data
      } catch (error) {
        console.error('Failed to load versions:', error)
      } finally {
        loadingVersions.value = false
      }
    }

    const loadReviews = async () => {
      loadingReviews.value = true
      try {
        const response = await api.get(`/marketplace/plugins/${slug}/reviews`)
        reviews.value = response.data
      } catch (error) {
        console.error('Failed to load reviews:', error)
      } finally {
        loadingReviews.value = false
      }
    }

    const installPlugin = async () => {
      if (!confirm(`确定要安装 "${plugin.value.name}" 吗？`)) {
        return
      }

      installing.value = true
      try {
        await api.post(`/marketplace/plugins/${slug}/install`, {
          slug: slug,
          auto_dependencies: true
        })

        alert('安装成功！')
        await checkInstalled()
      } catch (error) {
        console.error('Failed to install:', error)
        alert(`安装失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        installing.value = false
      }
    }

    const uninstallPlugin = async () => {
      if (!confirm(`确定要卸载 "${plugin.value.name}" 吗？此操作不可恢复。`)) {
        return
      }

      uninstalling.value = true
      try {
        await api.post(`/marketplace/plugins/${slug}/uninstall`)

        alert('卸载成功！')
        await checkInstalled()
      } catch (error) {
        console.error('Failed to uninstall:', error)
        alert(`卸载失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        uninstalling.value = false
      }
    }

    const updatePlugin = async () => {
      if (!confirm(`确定要更新 "${plugin.value.name}" 吗？`)) {
        return
      }

      updating.value = true
      try {
        await api.post(`/marketplace/plugins/${slug}/update`)

        alert('更新成功！')
        await checkInstalled()
        await loadPluginDetail()
      } catch (error) {
        console.error('Failed to update:', error)
        alert(`更新失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        updating.value = false
      }
    }

    const submitReview = async () => {
      if (!newReview.comment.trim()) {
        alert('请填写评价内容')
        return
      }

      submitting.value = true
      try {
        await api.post(`/marketplace/plugins/${slug}/reviews`, {
          rating: newReview.rating,
          comment: newReview.comment
        })

        alert('评价提交成功！')
        showReviewForm.value = false
        newReview.rating = 5
        newReview.comment = ''
        await loadReviews()
      } catch (error) {
        console.error('Failed to submit review:', error)
        alert(`提交失败: ${error.response?.data?.detail || error.message}`)
      } finally {
        submitting.value = false
      }
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

    const getCategoryName = (category) => {
      const names = {
        'agent': '智能体插件',
        'llm': 'LLM提供商',
        'code-quality': '代码质量',
        'integration': '集成插件',
        'tool': '工具插件'
      }
      return names[category] || '其他'
    }

    const formatNumber = (num) => {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadPluginDetail()
    })

    return {
      loading,
      plugin,
      isInstalled,
      hasUpdate,
      installing,
      uninstalling,
      updating,
      activeTab,
      contentTabs,
      versions,
      loadingVersions,
      reviews,
      loadingReviews,
      showReviewForm,
      submitting,
      hoverRating,
      newReview,
      installPlugin,
      uninstallPlugin,
      updatePlugin,
      submitReview,
      getPluginIcon,
      getCategoryName,
      formatNumber,
      formatDate
    }
  }
}
</script>

<style scoped>
.plugin-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading,
.error-state {
  text-align: center;
  padding: 80px 20px;
  color: #666;
}

.loading i,
.error-state i {
  color: #2196F3;
  margin-bottom: 20px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f5f5f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background 0.3s;
}

.btn-back:hover {
  background: #e0e0e0;
}

/* 插件头部 */
.plugin-header {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 30px;
  align-items: start;
  margin-bottom: 20px;
}

.plugin-icon-large {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plugin-icon-large i {
  font-size: 48px;
  color: white;
}

.plugin-title-section h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
}

.plugin-author {
  color: #666;
  margin-bottom: 15px;
}

.plugin-stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #666;
}

.stat i {
  font-size: 16px;
}

.stat small {
  color: #999;
}

.plugin-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-badge {
  background: #2196F3;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.tag {
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
  color: #666;
}

.plugin-actions {
  display: flex;
  flex-direction: column;
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
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
  white-space: nowrap;
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

.btn-success {
  background: #4CAF50;
  color: white;
}

.btn-success:hover {
  background: #45a049;
}

.btn-danger {
  background: #F44336;
  color: white;
}

.btn-danger:hover {
  background: #D32F2F;
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover {
  background: #616161;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 内容标签页 */
.content-tabs {
  background: white;
  display: flex;
  gap: 10px;
  padding: 0 30px;
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 20px;
}

.tab {
  padding: 15px 25px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 15px;
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

/* 标签页内容 */
.tab-content {
  background: white;
  padding: 30px;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h2 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

.description {
  font-size: 16px;
  line-height: 1.8;
  color: #666;
}

.dependencies {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.dependency-item {
  background: #f5f5f5;
  padding: 8px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.links {
  display: flex;
  gap: 15px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f5f5f5;
  border-radius: 6px;
  text-decoration: none;
  color: #2196F3;
  transition: background 0.3s;
}

.link-item:hover {
  background: #e3f2fd;
}

/* 版本列表 */
.versions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.version-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.version-number {
  font-family: monospace;
  font-weight: 500;
}

.current-badge {
  background: #4CAF50;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 评价 */
.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.review-form {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.review-form h3 {
  margin-top: 0;
  margin-bottom: 15px;
}

.rating-input {
  margin-bottom: 15px;
}

.rating-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.stars {
  display: flex;
  gap: 5px;
}

.stars i {
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s;
}

.review-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 15px;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.review-stars {
  display: flex;
  gap: 2px;
}

.review-stars i {
  font-size: 14px;
}

.review-date {
  color: #999;
  font-size: 13px;
  margin-left: auto;
}

.review-comment {
  color: #666;
  line-height: 1.6;
  margin-bottom: 10px;
}

.review-actions {
  display: flex;
  gap: 10px;
}

.helpful-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.helpful-btn:hover {
  border-color: #2196F3;
  color: #2196F3;
}

.loading-small {
  text-align: center;
  padding: 20px;
  color: #666;
}

/* 响应式 */
@media (max-width: 768px) {
  .plugin-header {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .plugin-icon-large {
    margin: 0 auto;
  }

  .plugin-actions {
    width: 100%;
  }

  .plugin-stats-row {
    justify-content: center;
  }

  .plugin-tags {
    justify-content: center;
  }
}
</style>
