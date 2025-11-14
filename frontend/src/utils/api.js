/**
 * API utilities for ResoftAI frontend
 *
 * Provides HTTP methods for communicating with the backend API
 */

import axios from 'axios'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const message = error.response.data?.detail || error.message

      if (status === 401) {
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('access_token')
        window.location.href = '/login'
      } else if (status === 403) {
        console.error('Access forbidden:', message)
      } else if (status === 404) {
        console.error('Resource not found:', message)
      } else if (status >= 500) {
        console.error('Server error:', message)
      }
    }
    return Promise.reject(error)
  }
)

// ==================== Auth API ====================

export const authAPI = {
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),

  register: (userData) =>
    apiClient.post('/auth/register', userData),

  logout: () =>
    apiClient.post('/auth/logout'),

  refreshToken: (refreshToken) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),

  getCurrentUser: () =>
    apiClient.get('/auth/me')
}

// ==================== Plugin API ====================

export const pluginAPI = {
  // Get all plugins from marketplace
  list: (params = {}) =>
    apiClient.get('/plugins/marketplace', { params }),

  // Get plugin details by slug
  getBySlug: (slug) =>
    apiClient.get(`/plugins/marketplace/${slug}`),

  // Search plugins
  search: (query, params = {}) =>
    apiClient.get('/plugins/marketplace/search', { params: { q: query, ...params } }),

  // Get installed plugins
  getInstalled: (params = {}) =>
    apiClient.get('/plugins/installed', { params }),

  // Install plugin
  install: (slug, version = null) =>
    apiClient.post('/plugins/install', { slug, version }),

  // Uninstall plugin
  uninstall: (pluginId) =>
    apiClient.delete(`/plugins/${pluginId}`),

  // Update plugin
  update: (pluginId, version) =>
    apiClient.post(`/plugins/${pluginId}/update`, { version }),

  // Activate plugin
  activate: (pluginId) =>
    apiClient.post(`/plugins/${pluginId}/activate`),

  // Deactivate plugin
  deactivate: (pluginId) =>
    apiClient.post(`/plugins/${pluginId}/deactivate`),

  // Check for updates
  checkUpdates: (pluginId) =>
    apiClient.get(`/plugins/${pluginId}/check-update`),

  // Get plugin configuration
  getConfig: (pluginId) =>
    apiClient.get(`/plugins/${pluginId}/config`),

  // Update plugin configuration
  updateConfig: (pluginId, config) =>
    apiClient.put(`/plugins/${pluginId}/config`, config),

  // Get plugin reviews
  getReviews: (slug, params = {}) =>
    apiClient.get(`/plugins/marketplace/${slug}/reviews`, { params }),

  // Submit review
  submitReview: (slug, review) =>
    apiClient.post(`/plugins/marketplace/${slug}/reviews`, review),

  // Get plugin statistics
  getStats: (slug) =>
    apiClient.get(`/plugins/marketplace/${slug}/stats`)
}

// ==================== Organization API ====================

export const organizationAPI = {
  // List organizations
  list: (params = {}) =>
    apiClient.get('/organizations', { params }),

  // Get organization by ID
  get: (orgId) =>
    apiClient.get(`/organizations/${orgId}`),

  // Create organization
  create: (data) =>
    apiClient.post('/organizations', data),

  // Update organization
  update: (orgId, data) =>
    apiClient.put(`/organizations/${orgId}`, data),

  // Delete organization
  delete: (orgId) =>
    apiClient.delete(`/organizations/${orgId}`),

  // Get organization members
  getMembers: (orgId, params = {}) =>
    apiClient.get(`/organizations/${orgId}/members`, { params }),

  // Add member to organization
  addMember: (orgId, userId, role = 'MEMBER') =>
    apiClient.post(`/organizations/${orgId}/members`, { user_id: userId, role }),

  // Remove member from organization
  removeMember: (orgId, userId) =>
    apiClient.delete(`/organizations/${orgId}/members/${userId}`),

  // Update member role
  updateMemberRole: (orgId, userId, role) =>
    apiClient.put(`/organizations/${orgId}/members/${userId}/role`, { role }),

  // Get organization statistics
  getStats: (orgId) =>
    apiClient.get(`/organizations/${orgId}/stats`),

  // Get organization quotas
  getQuotas: (orgId) =>
    apiClient.get(`/organizations/${orgId}/quotas`),

  // Update organization tier
  updateTier: (orgId, tier) =>
    apiClient.put(`/organizations/${orgId}/tier`, { tier }),

  // Configure SSO
  configureSso: (orgId, ssoConfig) =>
    apiClient.post(`/organizations/${orgId}/sso`, ssoConfig),

  // Get SSO configuration
  getSsoConfig: (orgId) =>
    apiClient.get(`/organizations/${orgId}/sso`)
}

// ==================== Team API ====================

export const teamAPI = {
  // List teams
  list: (params = {}) =>
    apiClient.get('/teams', { params }),

  // Get team by ID
  get: (teamId) =>
    apiClient.get(`/teams/${teamId}`),

  // Create team
  create: (data) =>
    apiClient.post('/teams', data),

  // Update team
  update: (teamId, data) =>
    apiClient.put(`/teams/${teamId}`, data),

  // Delete team
  delete: (teamId) =>
    apiClient.delete(`/teams/${teamId}`),

  // Get team members
  getMembers: (teamId, params = {}) =>
    apiClient.get(`/teams/${teamId}/members`, { params }),

  // Add member to team
  addMember: (teamId, userId, role = 'MEMBER') =>
    apiClient.post(`/teams/${teamId}/members`, { user_id: userId, role }),

  // Remove member from team
  removeMember: (teamId, userId) =>
    apiClient.delete(`/teams/${teamId}/members/${userId}`),

  // Update member role
  updateMemberRole: (teamId, userId, role) =>
    apiClient.put(`/teams/${teamId}/members/${userId}/role`, { role }),

  // Get team statistics
  getStats: (teamId) =>
    apiClient.get(`/teams/${teamId}/stats`),

  // Get team projects
  getProjects: (teamId, params = {}) =>
    apiClient.get(`/teams/${teamId}/projects`, { params }),

  // Assign project to team
  assignProject: (teamId, projectId) =>
    apiClient.post(`/teams/${teamId}/projects`, { project_id: projectId }),

  // Unassign project from team
  unassignProject: (teamId, projectId) =>
    apiClient.delete(`/teams/${teamId}/projects/${projectId}`)
}

// ==================== Quota API ====================

export const quotaAPI = {
  // Get quota information for current user/organization
  get: (organizationId = null) => {
    const url = organizationId
      ? `/quotas/organizations/${organizationId}`
      : '/quotas/me'
    return apiClient.get(url)
  },

  // Get quota usage
  getUsage: (organizationId = null) => {
    const url = organizationId
      ? `/quotas/organizations/${organizationId}/usage`
      : '/quotas/me/usage'
    return apiClient.get(url)
  },

  // Get quota alerts
  getAlerts: (organizationId = null) => {
    const url = organizationId
      ? `/quotas/organizations/${organizationId}/alerts`
      : '/quotas/me/alerts'
    return apiClient.get(url)
  },

  // Update quota limits (admin only)
  updateLimits: (organizationId, quotaType, limit) =>
    apiClient.put(`/quotas/organizations/${organizationId}/${quotaType}`, { limit }),

  // Reset quota usage (admin only)
  resetUsage: (organizationId, quotaType) =>
    apiClient.post(`/quotas/organizations/${organizationId}/${quotaType}/reset`)
}

// ==================== Project API ====================

export const projectAPI = {
  list: (params = {}) =>
    apiClient.get('/projects', { params }),

  get: (projectId) =>
    apiClient.get(`/projects/${projectId}`),

  create: (data) =>
    apiClient.post('/projects', data),

  update: (projectId, data) =>
    apiClient.put(`/projects/${projectId}`, data),

  delete: (projectId) =>
    apiClient.delete(`/projects/${projectId}`),

  execute: (projectId) =>
    apiClient.post(`/projects/${projectId}/execute`),

  getStatus: (projectId) =>
    apiClient.get(`/projects/${projectId}/status`),

  getFiles: (projectId, params = {}) =>
    apiClient.get(`/projects/${projectId}/files`, { params })
}

// ==================== File API ====================

export const fileAPI = {
  list: (params = {}) =>
    apiClient.get('/files', { params }),

  get: (fileId) =>
    apiClient.get(`/files/${fileId}`),

  upload: (formData, onProgress) =>
    apiClient.post('/files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress
    }),

  download: (fileId) =>
    apiClient.get(`/files/${fileId}/download`, { responseType: 'blob' }),

  delete: (fileId) =>
    apiClient.delete(`/files/${fileId}`)
}

// ==================== Performance Monitoring API ====================

export const performanceAPI = {
  // Get system metrics
  getMetrics: (params = {}) =>
    apiClient.get('/performance/metrics', { params }),

  // Get agent performance
  getAgentPerformance: (params = {}) =>
    apiClient.get('/performance/agents', { params }),

  // Get LLM performance
  getLLMPerformance: (params = {}) =>
    apiClient.get('/performance/llm', { params }),

  // Get workflow performance
  getWorkflowPerformance: (params = {}) =>
    apiClient.get('/performance/workflows', { params }),

  // Get real-time metrics
  getRealTimeMetrics: () =>
    apiClient.get('/performance/realtime')
}

// ==================== Template API ====================

export const templateAPI = {
  list: (params = {}) =>
    apiClient.get('/templates', { params }),

  get: (templateId) =>
    apiClient.get(`/templates/${templateId}`),

  create: (data) =>
    apiClient.post('/templates', data),

  update: (templateId, data) =>
    apiClient.put(`/templates/${templateId}`, data),

  delete: (templateId) =>
    apiClient.delete(`/templates/${templateId}`),

  apply: (templateId, projectId, variables = {}) =>
    apiClient.post(`/templates/${templateId}/apply`, { project_id: projectId, variables })
}

// Export the configured axios instance for custom requests
export default apiClient
