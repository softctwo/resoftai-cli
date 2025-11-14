/**
 * Template Marketplace API
 * API functions for template marketplace operations
 */

import apiClient from '../client'
import type {
  Template,
  TemplateDetail,
  TemplateVersion,
  TemplateReview,
  TemplateMarketplaceParams,
  PublishTemplateRequest,
  ApiResponse
} from '@/types/api'

/**
 * List templates in marketplace
 */
export function listMarketplace(params?: TemplateMarketplaceParams) {
  return apiClient.get<ApiResponse<Template[]>>('/templates/marketplace', { params })
}

/**
 * Search templates
 */
export function searchTemplates(query: string, params?: Omit<TemplateMarketplaceParams, 'search'>) {
  return apiClient.get<ApiResponse<Template[]>>('/templates/marketplace/search', {
    params: { q: query, ...params }
  })
}

/**
 * Get template details
 */
export function getTemplate(id: number) {
  return apiClient.get<ApiResponse<TemplateDetail>>(`/templates/marketplace/${id}`)
}

/**
 * Get trending templates
 */
export function getTrendingTemplates(days: number = 7, limit: number = 10) {
  return apiClient.get<ApiResponse<Template[]>>('/templates/marketplace/trending', {
    params: { days, limit }
  })
}

/**
 * Get featured templates
 */
export function getFeaturedTemplates(limit: number = 10) {
  return apiClient.get<ApiResponse<Template[]>>('/templates/marketplace/featured', {
    params: { limit }
  })
}

/**
 * Publish a new template
 */
export function publishTemplate(data: PublishTemplateRequest) {
  return apiClient.post<ApiResponse<Template>>('/templates/marketplace', data)
}

/**
 * Get template versions
 */
export function getTemplateVersions(templateId: number) {
  return apiClient.get<ApiResponse<TemplateVersion[]>>(`/templates/marketplace/${templateId}/versions`)
}

/**
 * Publish template version
 */
export function publishTemplateVersion(
  templateId: number,
  data: {
    version: string
    changelog?: string
    template_data: any
  }
) {
  return apiClient.post<ApiResponse<TemplateVersion>>(
    `/templates/marketplace/${templateId}/versions`,
    data
  )
}

/**
 * Track template usage/installation
 */
export function trackTemplateUsage(
  templateId: number,
  data: {
    project_id?: number
    variables_used?: Record<string, any>
  }
) {
  return apiClient.post(`/templates/marketplace/${templateId}/track-usage`, data)
}

/**
 * Download template
 */
export function downloadTemplate(templateId: number, version?: string) {
  return apiClient.get(`/templates/marketplace/${templateId}/download`, {
    params: { version },
    responseType: 'blob'
  })
}

/**
 * Get template reviews
 */
export function getTemplateReviews(templateId: number, limit: number = 20, skip: number = 0) {
  return apiClient.get<ApiResponse<TemplateReview[]>>(
    `/templates/marketplace/${templateId}/reviews`,
    { params: { limit, skip } }
  )
}

/**
 * Submit template review
 */
export function submitTemplateReview(
  templateId: number,
  data: {
    rating: number
    comment?: string
  }
) {
  return apiClient.post<ApiResponse<TemplateReview>>(
    `/templates/marketplace/${templateId}/reviews`,
    data
  )
}

/**
 * Update template review
 */
export function updateTemplateReview(
  templateId: number,
  reviewId: number,
  data: {
    rating?: number
    comment?: string
  }
) {
  return apiClient.put<ApiResponse<TemplateReview>>(
    `/templates/marketplace/${templateId}/reviews/${reviewId}`,
    data
  )
}

/**
 * Delete template review
 */
export function deleteTemplateReview(templateId: number, reviewId: number) {
  return apiClient.delete(`/templates/marketplace/${templateId}/reviews/${reviewId}`)
}

/**
 * Get template statistics
 */
export function getTemplateStats(templateId: number) {
  return apiClient.get<ApiResponse<{
    downloads_count: number
    installs_count: number
    rating_average: number
    rating_count: number
    recent_downloads: number
    trend: string
  }>>(`/templates/marketplace/${templateId}/stats`)
}

// Export as templateApi for component usage
export const templateApi = {
  listMarketplace,
  searchTemplates,
  getTemplate,
  getTrendingTemplates,
  getFeaturedTemplates,
  publishTemplate,
  getTemplateVersions,
  publishTemplateVersion,
  trackTemplateUsage,
  downloadTemplate,
  getTemplateReviews,
  submitTemplateReview,
  updateTemplateReview,
  deleteTemplateReview,
  getTemplateStats
}

export default templateApi
