/**
 * Admin Review API
 * API functions for admin review and moderation
 */

import apiClient from '../client'
import type {
  ReviewItem,
  ReviewStats,
  ApproveRequest,
  RejectRequest,
  ApiResponse
} from '@/types/api'

/**
 * Get admin dashboard statistics
 */
export function getStats() {
  return apiClient.get<ApiResponse<ReviewStats>>('/admin/stats')
}

/**
 * Get pending plugins
 */
export function getPendingPlugins(limit: number = 50, skip: number = 0) {
  return apiClient.get<ApiResponse<ReviewItem[]>>('/admin/plugins/pending', {
    params: { limit, skip }
  })
}

/**
 * Get pending templates
 */
export function getPendingTemplates(limit: number = 50, skip: number = 0) {
  return apiClient.get<ApiResponse<ReviewItem[]>>('/admin/templates/pending', {
    params: { limit, skip }
  })
}

/**
 * Get all plugins with status filter
 */
export function getAllPlugins(params?: {
  status?: 'approved' | 'rejected' | 'pending_review'
  limit?: number
  skip?: number
}) {
  return apiClient.get<ApiResponse<ReviewItem[]>>('/admin/plugins', { params })
}

/**
 * Get all templates with status filter
 */
export function getAllTemplates(params?: {
  status?: 'approved' | 'rejected' | 'pending_review'
  limit?: number
  skip?: number
}) {
  return apiClient.get<ApiResponse<ReviewItem[]>>('/admin/templates', { params })
}

/**
 * Approve plugin
 */
export function approvePlugin(pluginId: number, data: ApproveRequest) {
  return apiClient.post(`/admin/plugins/${pluginId}/approve`, data)
}

/**
 * Reject plugin
 */
export function rejectPlugin(pluginId: number, data: RejectRequest) {
  return apiClient.post(`/admin/plugins/${pluginId}/reject`, data)
}

/**
 * Approve template
 */
export function approveTemplate(templateId: number, data: ApproveRequest) {
  return apiClient.post(`/admin/templates/${templateId}/approve`, data)
}

/**
 * Reject template
 */
export function rejectTemplate(templateId: number, data: RejectRequest) {
  return apiClient.post(`/admin/templates/${templateId}/reject`, data)
}

/**
 * Feature plugin
 */
export function featurePlugin(pluginId: number, featured: boolean) {
  return apiClient.post(`/admin/plugins/${pluginId}/feature`, { is_featured: featured })
}

/**
 * Feature template
 */
export function featureTemplate(templateId: number, featured: boolean) {
  return apiClient.post(`/admin/templates/${templateId}/feature`, { is_featured: featured })
}

/**
 * Get plugin details for review
 */
export function getPluginForReview(pluginId: number) {
  return apiClient.get<ApiResponse<ReviewItem>>(`/admin/plugins/${pluginId}`)
}

/**
 * Get template details for review
 */
export function getTemplateForReview(templateId: number) {
  return apiClient.get<ApiResponse<ReviewItem>>(`/admin/templates/${templateId}`)
}

/**
 * Archive plugin
 */
export function archivePlugin(pluginId: number) {
  return apiClient.post(`/admin/plugins/${pluginId}/archive`)
}

/**
 * Archive template
 */
export function archiveTemplate(templateId: number) {
  return apiClient.post(`/admin/templates/${templateId}/archive`)
}

// Export as adminApi for component usage
export const adminApi = {
  getStats,
  getPendingPlugins,
  getPendingTemplates,
  getAllPlugins,
  getAllTemplates,
  approvePlugin,
  rejectPlugin,
  approveTemplate,
  rejectTemplate,
  featurePlugin,
  featureTemplate,
  getPluginForReview,
  getTemplateForReview,
  archivePlugin,
  archiveTemplate
}

export default adminApi
