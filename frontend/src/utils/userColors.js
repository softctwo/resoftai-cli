/**
 * User color utilities for collaborative editing
 * Provides consistent color assignment across all components
 */

// User color palette
export const userColors = [
  '#409EFF', // blue
  '#67C23A', // green
  '#E6A23C', // orange
  '#F56C6C', // red
  '#c71585', // purple
  '#20b2aa', // teal
  '#ff69b4', // pink
  '#ffa500', // orange-yellow
]

/**
 * Get consistent color for a user based on their ID
 * @param {number} userId - User ID
 * @returns {string} Hex color code
 */
export function getUserColor(userId) {
  if (userId === null || userId === undefined) {
    return userColors[0]
  }
  return userColors[userId % userColors.length]
}

/**
 * Get user initials for avatar display
 * @param {string} username - Username
 * @returns {string} User initials (1-2 characters)
 */
export function getUserInitials(username) {
  if (!username) return '?'

  const parts = username.trim().split(/\s+/)

  if (parts.length >= 2) {
    // Use first letter of first two words
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }

  // Use first two characters of single word
  return username.substring(0, 2).toUpperCase()
}

/**
 * Generate lighter version of a color for backgrounds
 * @param {string} color - Hex color code
 * @param {number} alpha - Opacity (0-1)
 * @returns {string} RGBA color
 */
export function getLightColor(color, alpha = 0.2) {
  // Convert hex to RGB
  const r = parseInt(color.slice(1, 3), 16)
  const g = parseInt(color.slice(3, 5), 16)
  const b = parseInt(color.slice(5, 7), 16)

  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/**
 * Get all available colors
 * @returns {string[]} Array of color codes
 */
export function getAllColors() {
  return [...userColors]
}

/**
 * Get color name for display
 * @param {number} userId - User ID
 * @returns {string} Color name
 */
export function getColorName(userId) {
  const colorNames = [
    '蓝色',
    '绿色',
    '橙色',
    '红色',
    '紫色',
    '青色',
    '粉色',
    '橙黄色',
  ]

  if (userId === null || userId === undefined) {
    return colorNames[0]
  }
  return colorNames[userId % colorNames.length]
}
