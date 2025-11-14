/**
 * Contributors API
 * API functions for contributor profiles and leaderboards
 */

import apiClient from '../client'
import type {
  ContributorProfile,
  ContributorBadge,
  Leaderboard,
  ApiResponse
} from '@/types/api'

/**
 * Get contributor profile
 */
export function getContributorProfile(userId: number) {
  return apiClient.get<ApiResponse<ContributorProfile>>(`/contributors/${userId}`)
}

/**
 * Get current user's contributor profile
 */
export function getMyProfile() {
  return apiClient.get<ApiResponse<ContributorProfile>>('/contributors/me')
}

/**
 * Create or update contributor profile
 */
export function updateContributorProfile(data: {
  display_name?: string
  bio?: string
  avatar_url?: string
  github_username?: string
  website_url?: string
}) {
  return apiClient.put<ApiResponse<ContributorProfile>>('/contributors/me', data)
}

/**
 * Get contributor leaderboard
 */
export function getLeaderboard(params?: {
  sort_by?: 'downloads' | 'installs' | 'rating' | 'contributions'
  limit?: number
  skip?: number
}) {
  return apiClient.get<ApiResponse<Leaderboard[]>>('/contributors/leaderboard', { params })
}

/**
 * Get contributor badges
 */
export function getContributorBadges(userId: number) {
  return apiClient.get<ApiResponse<ContributorBadge[]>>(`/contributors/${userId}/badges`)
}

/**
 * Get all available badges
 */
export function getAllBadges() {
  return apiClient.get<ApiResponse<ContributorBadge[]>>('/contributors/badges')
}

/**
 * Get contributor's plugins
 */
export function getContributorPlugins(userId: number, params?: {
  status?: 'approved' | 'pending_review' | 'rejected'
  limit?: number
  skip?: number
}) {
  return apiClient.get(`/contributors/${userId}/plugins`, { params })
}

/**
 * Get contributor's templates
 */
export function getContributorTemplates(userId: number, params?: {
  status?: 'approved' | 'pending_review' | 'rejected'
  limit?: number
  skip?: number
}) {
  return apiClient.get(`/contributors/${userId}/templates`, { params })
}

/**
 * Get contributor statistics
 */
export function getContributorStats(userId: number) {
  return apiClient.get<ApiResponse<{
    total_plugins: number
    total_templates: number
    total_downloads: number
    total_installs: number
    average_rating: number
    total_reviews: number
    badges_count: number
    rank: number
  }>>(`/contributors/${userId}/stats`)
}

/**
 * Search contributors
 */
export function searchContributors(query: string, limit: number = 20) {
  return apiClient.get<ApiResponse<ContributorProfile[]>>('/contributors/search', {
    params: { q: query, limit }
  })
}

// Export as contributorApi for component usage
export const contributorApi = {
  getContributorProfile,
  getMyProfile,
  updateContributorProfile,
  getLeaderboard,
  getContributorBadges,
  getAllBadges,
  getContributorPlugins,
  getContributorTemplates,
  getContributorStats,
  searchContributors
}

export default contributorApi
