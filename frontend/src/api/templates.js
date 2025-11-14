import apiClient from './client'

/**
 * Get all templates
 * @param {Object} [params]
 * @param {string} [params.category] - Filter by category
 * @param {Array<string>} [params.tags] - Filter by tags
 * @returns {Promise}
 */
export function getTemplates(params = {}) {
  return apiClient.get('/v1/templates', { params })
}

/**
 * Get template by ID
 * @param {string} id - Template ID
 * @returns {Promise}
 */
export function getTemplate(id) {
  return apiClient.get(`/v1/templates/${id}`)
}

/**
 * Get template preview
 * @param {string} id - Template ID
 * @returns {Promise}
 */
export function getTemplatePreview(id) {
  return apiClient.get(`/v1/templates/${id}/preview`)
}

/**
 * Apply template to create project
 * @param {Object} params
 * @param {string} params.template_id - Template ID
 * @param {string} params.project_name - Project name
 * @param {Object} params.variables - Template variables
 * @param {string} [params.output_path] - Output directory path
 * @returns {Promise}
 */
export function applyTemplate(params) {
  return apiClient.post('/v1/templates/apply', params)
}

/**
 * Get template categories
 * @returns {Promise}
 */
export function getTemplateCategories() {
  return apiClient.get('/v1/templates/categories')
}
