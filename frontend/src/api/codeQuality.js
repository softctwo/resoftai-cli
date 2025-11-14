import apiClient from './client'

/**
 * Check code quality
 * @param {Object} params
 * @param {string} params.code - Source code
 * @param {string} params.language - Programming language (python, javascript, typescript)
 * @param {string} [params.filename] - Optional filename
 * @param {Array<string>} [params.linters] - Specific linters to use
 * @returns {Promise}
 */
export function checkCodeQuality(params) {
  return apiClient.post('/code-quality/check', params)
}

/**
 * Get supported linters
 * @returns {Promise}
 */
export function getSupportedLinters() {
  return apiClient.get('/code-quality/linters')
}

/**
 * Get code quality tools health status
 * @returns {Promise}
 */
export function getHealthStatus() {
  return apiClient.get('/code-quality/health')
}
