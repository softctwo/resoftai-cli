import client from './client'

/**
 * Performance Monitoring API Client
 */

export default {
  /**
   * Get performance metrics
   */
  getMetrics(params = {}) {
    return client.get('/api/performance/metrics', { params })
  },

  /**
   * Get system statistics
   */
  getSystemStats() {
    return client.get('/api/performance/system')
  },

  /**
   * Get API endpoint statistics
   */
  getEndpointStats(params = {}) {
    return client.get('/api/performance/endpoints', { params })
  },

  /**
   * Get real-time metrics
   */
  getRealtime() {
    return client.get('/api/performance/realtime')
  },

  /**
   * Get active alerts
   */
  getAlerts() {
    return client.get('/api/performance/alerts')
  },

  /**
   * Get historical data
   */
  getHistoricalData(timeRange = '24h') {
    return client.get('/api/performance/historical', {
      params: { time_range: timeRange }
    })
  },

  /**
   * Export performance data
   */
  exportData(format = 'json') {
    return client.get('/api/performance/export', {
      params: { format },
      responseType: 'blob'
    })
  },

  /**
   * Get resource usage
   */
  getResourceUsage() {
    return client.get('/api/performance/resources')
  },

  /**
   * Get request trends
   */
  getRequestTrends(params = {}) {
    return client.get('/api/performance/trends/requests', { params })
  },

  /**
   * Get response time distribution
   */
  getResponseTimeDistribution() {
    return client.get('/api/performance/distribution/response-time')
  }
}
