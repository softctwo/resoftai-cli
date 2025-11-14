import client from './client'

/**
 * Organization API Client
 */

export default {
  /**
   * Get all organizations
   */
  getOrganizations(params = {}) {
    return client.get('/api/organizations', { params })
  },

  /**
   * Get organization by ID
   */
  getOrganization(id) {
    return client.get(`/api/organizations/${id}`)
  },

  /**
   * Create organization
   */
  createOrganization(data) {
    return client.post('/api/organizations', data)
  },

  /**
   * Update organization
   */
  updateOrganization(id, data) {
    return client.put(`/api/organizations/${id}`, data)
  },

  /**
   * Delete organization
   */
  deleteOrganization(id) {
    return client.delete(`/api/organizations/${id}`)
  },

  /**
   * Get organization members
   */
  getMembers(id) {
    return client.get(`/api/organizations/${id}/members`)
  },

  /**
   * Add member to organization
   */
  addMember(id, data) {
    return client.post(`/api/organizations/${id}/members`, data)
  },

  /**
   * Update member role
   */
  updateMemberRole(id, memberId, data) {
    return client.put(`/api/organizations/${id}/members/${memberId}`, data)
  },

  /**
   * Remove member from organization
   */
  removeMember(id, memberId) {
    return client.delete(`/api/organizations/${id}/members/${memberId}`)
  },

  /**
   * Get organization teams
   */
  getTeams(id) {
    return client.get(`/api/organizations/${id}/teams`)
  },

  /**
   * Get organization settings
   */
  getSettings(id) {
    return client.get(`/api/organizations/${id}/settings`)
  },

  /**
   * Update organization settings
   */
  updateSettings(id, data) {
    return client.put(`/api/organizations/${id}/settings`, data)
  },

  /**
   * Get organization statistics
   */
  getStatistics(id) {
    return client.get(`/api/organizations/${id}/statistics`)
  }
}
