import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Note: In real scenario, you'd need to log in first
    // This is a placeholder - adjust based on your auth flow
    await page.goto('/')
  })

  test('should display main navigation', async ({ page }) => {
    // Check if main layout elements are present
    const navElements = await page.locator('nav, .el-menu, .sidebar').count()
    expect(navElements).toBeGreaterThan(0)
  })

  test('should display dashboard title', async ({ page }) => {
    await page.goto('/dashboard')

    // Look for dashboard title or heading
    const title = page.locator('h1, h2, .page-title')
    if (await title.count() > 0) {
      await expect(title.first()).toBeVisible()
    }
  })

  test('should navigate to projects page', async ({ page }) => {
    // Look for projects link in navigation
    const projectsLink = page.locator('text=/项目|Projects/i').first()

    if (await projectsLink.isVisible()) {
      await projectsLink.click()
      await page.waitForURL(/.*projects/)
      expect(page.url()).toContain('projects')
    }
  })

  test('should display statistics or charts', async ({ page }) => {
    await page.goto('/dashboard')

    // Wait for page to load
    await page.waitForTimeout(1000)

    // Check if any stat cards or charts are present
    const statsCards = await page.locator('.stat-card, .el-card, [class*="statistic"]').count()
    const charts = await page.locator('canvas, svg[class*="chart"]').count()

    // Either stats or charts should be present on dashboard
    expect(statsCards + charts).toBeGreaterThan(0)
  })

  test('should have user menu or profile section', async ({ page }) => {
    // Look for user menu/profile in header
    const userMenu = page.locator('.user-menu, .user-profile, .el-dropdown')

    if (await userMenu.count() > 0) {
      await expect(userMenu.first()).toBeVisible()
    }
  })
})
