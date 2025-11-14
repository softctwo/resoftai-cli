/**
 * Notifications API
 * API functions for notification management
 */

import apiClient from '../client'
import type {
  Notification,
  NotificationPreference,
  ApiResponse
} from '@/types/api'

/**
 * List user notifications
 */
export function listNotifications(params?: {
  unread_only?: boolean
  limit?: number
  skip?: number
}) {
  return apiClient.get<ApiResponse<Notification[]>>('/notifications', { params })
}

/**
 * Get unread notification count
 */
export function getUnreadCount() {
  return apiClient.get<ApiResponse<{ count: number }>>('/notifications/unread-count')
}

/**
 * Mark notification as read
 */
export function markAsRead(notificationId: number) {
  return apiClient.post(`/notifications/${notificationId}/read`)
}

/**
 * Mark all notifications as read
 */
export function markAllAsRead() {
  return apiClient.post<ApiResponse<{ count: number }>>('/notifications/mark-all-read')
}

/**
 * Delete notification
 */
export function deleteNotification(notificationId: number) {
  return apiClient.delete(`/notifications/${notificationId}`)
}

/**
 * Get notification preferences
 */
export function getPreferences() {
  return apiClient.get<ApiResponse<NotificationPreference>>('/notifications/preferences')
}

/**
 * Update notification preferences
 */
export function updatePreferences(data: Partial<NotificationPreference>) {
  return apiClient.put<ApiResponse<NotificationPreference>>('/notifications/preferences', data)
}

/**
 * Send test notification
 */
export function sendTestNotification() {
  return apiClient.post('/notifications/test')
}

/**
 * Get notification by ID
 */
export function getNotification(notificationId: number) {
  return apiClient.get<ApiResponse<Notification>>(`/notifications/${notificationId}`)
}

/**
 * Batch mark notifications as read
 */
export function batchMarkAsRead(notificationIds: number[]) {
  return apiClient.post('/notifications/batch-read', { notification_ids: notificationIds })
}

/**
 * Batch delete notifications
 */
export function batchDelete(notificationIds: number[]) {
  return apiClient.post('/notifications/batch-delete', { notification_ids: notificationIds })
}

// Export as notificationApi for component usage
export const notificationApi = {
  listNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  getPreferences,
  updatePreferences,
  sendTestNotification,
  getNotification,
  batchMarkAsRead,
  batchDelete
}

export default notificationApi
