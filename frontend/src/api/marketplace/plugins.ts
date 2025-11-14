/**
 * Plugin Marketplace API
 * API functions for plugin marketplace operations
 */

import apiClient from '../client'
import type {
  Plugin,
  PluginVersion,
  ApiResponse
} from '@/types/api'

/**
 * List plugins in marketplace
 */
export function listMarketplace(params?: {
  search?: string
  category?: string
  is_featured?: boolean
  is_official?: boolean
  tags?: string[]
  sort_by?: 'created_at' | 'downloads' | 'rating' | 'installs'
  skip?: number
  limit?: number
}) {
  return apiClient.get<ApiResponse<Plugin[]>>('/plugins/marketplace', { params })
}

/**
 * Search plugins
 */
export function searchPlugins(query: string, params?: {
  category?: string
  tags?: string[]
  limit?: number
}) {
  return apiClient.get<ApiResponse<Plugin[]>>('/plugins/marketplace/search', {
    params: { q: query, ...params }
  })
}

/**
 * Get plugin details
 */
export function getPlugin(id: number) {
  return apiClient.get<ApiResponse<Plugin>>(`/plugins/marketplace/${id}`)
}

/**
 * Get trending plugins
 */
export function getTrendingPlugins(days: number = 7, limit: number = 10) {
  return apiClient.get<ApiResponse<Plugin[]>>('/plugins/marketplace/trending', {
    params: { days, limit }
  })
}

/**
 * Get featured plugins
 */
export function getFeaturedPlugins(limit: number = 10) {
  return apiClient.get<ApiResponse<Plugin[]>>('/plugins/marketplace/featured', {
    params: { limit }
  })
}

/**
 * Publish a new plugin
 */
export function publishPlugin(data: {
  name: string
  slug: string
  category: string
  version: string
  description: string
  package_url: string
  package_checksum: string
  tags?: string[]
  license?: string
  documentation_url?: string
  source_url?: string
}) {
  return apiClient.post<ApiResponse<Plugin>>('/plugins/marketplace', data)
}

/**
 * Get plugin versions
 */
export function getPluginVersions(pluginId: number, stableOnly: boolean = false) {
  return apiClient.get<ApiResponse<PluginVersion[]>>(`/plugins/${pluginId}/versions`, {
    params: { stable_only: stableOnly }
  })
}

/**
 * Get specific plugin version
 */
export function getPluginVersion(pluginId: number, version: string) {
  return apiClient.get<ApiResponse<PluginVersion>>(`/plugins/${pluginId}/versions/${version}`)
}

/**
 * Publish plugin version
 */
export function publishPluginVersion(
  pluginId: number,
  data: {
    version: string
    changelog?: string
    package_url: string
    package_checksum: string
    min_platform_version?: string
    max_platform_version?: string
    is_stable?: boolean
  }
) {
  return apiClient.post<ApiResponse<PluginVersion>>(
    `/plugins/${pluginId}/versions`,
    data
  )
}

/**
 * Deprecate plugin version
 */
export function deprecatePluginVersion(pluginId: number, version: string) {
  return apiClient.post(`/plugins/${pluginId}/versions/${version}/deprecate`)
}

/**
 * Track plugin download
 */
export function trackPluginDownload(pluginId: number, version: string) {
  return apiClient.post<ApiResponse<{ download_url: string }>>(
    `/plugins/${pluginId}/versions/${version}/download`
  )
}

/**
 * Install plugin
 */
export function installPlugin(pluginId: number, version?: string) {
  return apiClient.post(`/plugins/${pluginId}/install`, { version })
}

/**
 * Uninstall plugin
 */
export function uninstallPlugin(pluginId: number) {
  return apiClient.post(`/plugins/${pluginId}/uninstall`)
}

/**
 * Get plugin reviews
 */
export function getPluginReviews(pluginId: number, limit: number = 20, skip: number = 0) {
  return apiClient.get(`/plugins/marketplace/${pluginId}/reviews`, {
    params: { limit, skip }
  })
}

/**
 * Submit plugin review
 */
export function submitPluginReview(
  pluginId: number,
  data: {
    rating: number
    comment?: string
  }
) {
  return apiClient.post(`/plugins/marketplace/${pluginId}/reviews`, data)
}

/**
 * Get plugin statistics
 */
export function getPluginStats(pluginId: number) {
  return apiClient.get<ApiResponse<{
    downloads_count: number
    installs_count: number
    rating_average: number
    rating_count: number
    recent_downloads: number
    trend: string
  }>>(`/plugins/marketplace/${pluginId}/stats`)
}

// Export as pluginApi for component usage
export const pluginApi = {
  listMarketplace,
  searchPlugins,
  getPlugin,
  getTrendingPlugins,
  getFeaturedPlugins,
  publishPlugin,
  getPluginVersions,
  getPluginVersion,
  publishPluginVersion,
  deprecatePluginVersion,
  trackPluginDownload,
  installPlugin,
  uninstallPlugin,
  getPluginReviews,
  submitPluginReview,
  getPluginStats
}

export default pluginApi
