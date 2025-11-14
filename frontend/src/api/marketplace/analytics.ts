/**
 * Analytics API
 * API functions for analytics and reporting
 */

import apiClient from '../client'
import type {
  OverviewStats,
  DownloadTrendData,
  CategoryDistributionData,
  TopItem,
  Activity,
  AnalyticsParams,
  ExportReportRequest,
  ContributorProfile,
  ApiResponse
} from '@/types/api'

/**
 * Get overview statistics
 */
export function getOverviewStats(params?: {
  start_date?: string
  end_date?: string
}) {
  return apiClient.get<ApiResponse<OverviewStats>>('/analytics/overview', { params })
}

/**
 * Get downloads trend data
 */
export function getDownloadsTrend(params?: {
  period?: '7d' | '30d' | '90d'
}) {
  return apiClient.get<ApiResponse<DownloadTrendData>>('/analytics/downloads-trend', { params })
}

/**
 * Get category distribution data
 */
export function getCategoryDistribution() {
  return apiClient.get<ApiResponse<CategoryDistributionData>>('/analytics/category-distribution')
}

/**
 * Get top plugins
 */
export function getTopPlugins(params?: {
  metric?: 'downloads' | 'installs' | 'rating'
  limit?: number
}) {
  return apiClient.get<ApiResponse<TopItem[]>>('/analytics/top-plugins', { params })
}

/**
 * Get top templates
 */
export function getTopTemplates(params?: {
  metric?: 'downloads' | 'installs' | 'rating'
  limit?: number
}) {
  return apiClient.get<ApiResponse<TopItem[]>>('/analytics/top-templates', { params })
}

/**
 * Get top contributors
 */
export function getTopContributors(params?: {
  limit?: number
}) {
  return apiClient.get<ApiResponse<ContributorProfile[]>>('/analytics/top-contributors', { params })
}

/**
 * Get recent activity
 */
export function getRecentActivity(params?: {
  limit?: number
}) {
  return apiClient.get<ApiResponse<Activity[]>>('/analytics/recent-activity', { params })
}

/**
 * Export analytics report
 */
export function exportReport(data: ExportReportRequest) {
  return apiClient.post('/analytics/export', data, {
    responseType: 'blob'
  })
}

/**
 * Get plugin analytics
 */
export function getPluginAnalytics(pluginId: number, params?: AnalyticsParams) {
  return apiClient.get(`/analytics/plugins/${pluginId}`, { params })
}

/**
 * Get template analytics
 */
export function getTemplateAnalytics(templateId: number, params?: AnalyticsParams) {
  return apiClient.get(`/analytics/templates/${templateId}`, { params })
}

/**
 * Get contributor analytics
 */
export function getContributorAnalytics(userId: number, params?: AnalyticsParams) {
  return apiClient.get(`/analytics/contributors/${userId}`, { params })
}

/**
 * Get marketplace health metrics
 */
export function getMarketplaceHealth() {
  return apiClient.get<ApiResponse<{
    total_plugins: number
    total_templates: number
    active_contributors: number
    total_downloads: number
    total_installs: number
    avg_rating: number
    growth_rate: number
    health_score: number
  }>>('/analytics/marketplace-health')
}

/**
 * Get user engagement metrics
 */
export function getUserEngagement(params?: {
  start_date?: string
  end_date?: string
}) {
  return apiClient.get<ApiResponse<{
    daily_active_users: number
    weekly_active_users: number
    monthly_active_users: number
    retention_rate: number
    avg_session_duration: number
  }>>('/analytics/user-engagement', { params })
}

// Export as analyticsApi for component usage
export const analyticsApi = {
  getOverviewStats,
  getDownloadsTrend,
  getCategoryDistribution,
  getTopPlugins,
  getTopTemplates,
  getTopContributors,
  getRecentActivity,
  exportReport,
  getPluginAnalytics,
  getTemplateAnalytics,
  getContributorAnalytics,
  getMarketplaceHealth,
  getUserEngagement
}

export default analyticsApi
