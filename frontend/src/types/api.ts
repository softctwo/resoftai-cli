/**
 * API Type Definitions
 * Type definitions for all API requests and responses
 */

// ============================================================================
// Common Types
// ============================================================================

export interface PaginationParams {
  skip?: number
  limit?: number
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  skip: number
  limit: number
}

export interface ApiResponse<T> {
  data: T
}

// ============================================================================
// Template Types
// ============================================================================

export enum TemplateCategory {
  WEB_APP = 'web_app',
  REST_API = 'rest_api',
  CLI_TOOL = 'cli_tool',
  MICROSERVICE = 'microservice',
  DATA_PIPELINE = 'data_pipeline',
  ML_PROJECT = 'ml_project',
  MOBILE_APP = 'mobile_app',
  OTHER = 'other'
}

export enum TemplateStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived'
}

export interface Template {
  id: number
  name: string
  slug: string
  category: TemplateCategory
  version: string
  description: string
  author_id: number
  author_name: string
  is_official: boolean
  is_featured: boolean
  downloads_count: number
  installs_count: number
  rating_average: number
  rating_count: number
  tags: string[]
  created_at: string
  updated_at: string
}

export interface TemplateDetail extends Template {
  template_data: any
  license: string | null
  documentation_url: string | null
  source_url: string | null
}

export interface TemplateVersion {
  id: number
  template_id: number
  version: string
  changelog: string | null
  template_data: any
  created_at: string
}

export interface TemplateReview {
  id: number
  template_id: number
  user_id: number
  user_name: string
  rating: number
  comment: string | null
  created_at: string
}

export interface TemplateMarketplaceParams extends PaginationParams {
  search?: string
  category?: TemplateCategory
  is_featured?: boolean
  is_official?: boolean
  tags?: string[]
  sort_by?: 'created_at' | 'downloads' | 'rating' | 'installs'
}

export interface PublishTemplateRequest {
  name: string
  slug: string
  category: TemplateCategory
  version: string
  description: string
  template_data: any
  tags?: string[]
  license?: string
  documentation_url?: string
  source_url?: string
}

// ============================================================================
// Plugin Types
// ============================================================================

export enum PluginCategory {
  AGENT_EXTENSION = 'agent_extension',
  LLM_PROVIDER = 'llm_provider',
  CODE_QUALITY = 'code_quality',
  INTEGRATION = 'integration',
  WORKFLOW = 'workflow',
  OTHER = 'other'
}

export enum PluginStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  ARCHIVED = 'archived'
}

export interface Plugin {
  id: number
  name: string
  slug: string
  category: PluginCategory
  version: string
  description: string
  author_id: number
  author_name: string
  is_official: boolean
  is_featured: boolean
  downloads_count: number
  installs_count: number
  rating_average: number
  rating_count: number
  tags: string[]
  created_at: string
  updated_at: string
}

export interface PluginVersion {
  id: number
  plugin_id: number
  version: string
  changelog: string | null
  package_url: string
  package_checksum: string
  min_platform_version: string | null
  max_platform_version: string | null
  is_stable: boolean
  is_deprecated: boolean
  download_count: number
  created_at: string
}

// ============================================================================
// Contributor Types
// ============================================================================

export interface ContributorProfile {
  id: number
  user_id: number
  display_name: string
  bio: string | null
  avatar_url: string | null
  github_username: string | null
  website_url: string | null
  is_verified: boolean
  plugins_count: number
  templates_count: number
  total_downloads: number
  total_installs: number
  average_rating: number
  badges: string[]
  created_at: string
}

export interface ContributorBadge {
  id: number
  name: string
  description: string
  icon: string
  type: 'achievement' | 'milestone' | 'special'
  criteria: any
}

export interface Leaderboard {
  rank: number
  contributor: ContributorProfile
  score: number
}

// ============================================================================
// Notification Types
// ============================================================================

export enum NotificationType {
  PLUGIN_APPROVED = 'plugin_approved',
  PLUGIN_REJECTED = 'plugin_rejected',
  TEMPLATE_APPROVED = 'template_approved',
  TEMPLATE_REJECTED = 'template_rejected',
  NEW_REVIEW = 'new_review',
  NEW_COMMENT = 'new_comment',
  BADGE_AWARDED = 'badge_awarded',
  VERSION_PUBLISHED = 'version_published',
  SYSTEM_ANNOUNCEMENT = 'system_announcement'
}

export enum NotificationPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent'
}

export interface Notification {
  id: number
  type: NotificationType
  priority: NotificationPriority
  title: string
  message: string
  data: any
  action_url: string | null
  action_text: string | null
  is_read: boolean
  created_at: string
  expires_at: string | null
}

export interface NotificationPreference {
  id: number
  user_id: number
  email_enabled: boolean
  in_app_enabled: boolean
  webhook_enabled: boolean
  webhook_url: string | null
  plugin_updates: boolean
  template_updates: boolean
  review_notifications: boolean
  comment_notifications: boolean
  badge_notifications: boolean
  quiet_hours_start: string | null
  quiet_hours_end: string | null
}

// ============================================================================
// Admin Review Types
// ============================================================================

export interface ReviewItem {
  id: number
  type: 'plugin' | 'template'
  name: string
  slug: string
  category: string
  version: string
  description: string
  author_id: number
  author_name: string
  status: PluginStatus | TemplateStatus
  package_url?: string
  source_url?: string
  submitted_at: string
  license?: string
}

export interface ReviewStats {
  pending_plugins: number
  pending_templates: number
  approved_plugins: number
  approved_templates: number
  rejected_plugins: number
  rejected_templates: number
  total_contributors: number
  total_downloads: number
  total_installs: number
}

export interface ApproveRequest {
  status: 'approved'
  is_featured?: boolean
}

export interface RejectRequest {
  status: 'rejected'
  feedback: string
}

// ============================================================================
// Analytics Types
// ============================================================================

export interface OverviewStats {
  total_downloads: number
  downloads_trend: number
  total_installs: number
  installs_trend: number
  active_contributors: number
  contributors_trend: number
  average_rating: number
  rating_trend: number
}

export interface DownloadTrendData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor?: string
    backgroundColor?: string
  }[]
}

export interface CategoryDistributionData {
  labels: string[]
  datasets: {
    data: number[]
    backgroundColor?: string[]
  }[]
}

export interface TopItem {
  id: number
  name: string
  value: number
}

export interface Activity {
  id: number
  type: 'plugin_published' | 'template_published' | 'review_added' | 'badge_awarded'
  text: string
  created_at: string
}

export interface AnalyticsParams {
  start_date?: string
  end_date?: string
  period?: '7d' | '30d' | '90d'
  metric?: 'downloads' | 'installs' | 'rating'
  limit?: number
}

export interface ExportReportRequest {
  start_date: string
  end_date: string
  format: 'csv' | 'json' | 'excel'
}
