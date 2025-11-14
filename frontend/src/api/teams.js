import client from './client'

/**
 * Team API Client
 */

export default {
  /**
   * Get all teams
   */
  getTeams(params = {}) {
    return client.get('/api/teams', { params })
  },

  /**
   * Get team by ID
   */
  getTeam(id) {
    return client.get(`/api/teams/${id}`)
  },

  /**
   * Create team
   */
  createTeam(data) {
    return client.post('/api/teams', data)
  },

  /**
   * Update team
   */
  updateTeam(id, data) {
    return client.put(`/api/teams/${id}`, data)
  },

  /**
   * Delete team
   */
  deleteTeam(id) {
    return client.delete(`/api/teams/${id}`)
  },

  /**
   * Get team members
   */
  getMembers(id) {
    return client.get(`/api/teams/${id}/members`)
  },

  /**
   * Add member to team
   */
  addMember(id, data) {
    return client.post(`/api/teams/${id}/members`, data)
  },

  /**
   * Update member role
   */
  updateMemberRole(id, memberId, data) {
    return client.put(`/api/teams/${id}/members/${memberId}`, data)
  },

  /**
   * Remove member from team
   */
  removeMember(id, memberId) {
    return client.delete(`/api/teams/${id}/members/${memberId}`)
  },

  /**
   * Get team projects
   */
  getProjects(id) {
    return client.get(`/api/teams/${id}/projects`)
  },

  /**
   * Assign project to team
   */
  assignProject(id, projectId) {
    return client.post(`/api/teams/${id}/projects`, { project_id: projectId })
  },

  /**
   * Unassign project from team
   */
  unassignProject(id, projectId) {
    return client.delete(`/api/teams/${id}/projects/${projectId}`)
  },

  /**
   * Get team activities
   */
  getActivities(id, params = {}) {
    return client.get(`/api/teams/${id}/activities`, { params })
  },

  /**
   * Get team settings
   */
  getSettings(id) {
    return client.get(`/api/teams/${id}/settings`)
  },

  /**
   * Update team settings
   */
  updateSettings(id, data) {
    return client.put(`/api/teams/${id}/settings`, data)
  },

  /**
   * Get team statistics
   */
  getStatistics(id) {
    return client.get(`/api/teams/${id}/statistics`)
  }
}
