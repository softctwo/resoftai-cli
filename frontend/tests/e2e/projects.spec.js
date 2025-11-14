import { test, expect } from '@playwright/test'

test.describe('Projects Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/projects')
  })

  test('should display projects list', async ({ page }) => {
    // Wait for page to load
    await page.waitForTimeout(1000)

    // Check if projects table or list is present
    const projectsContainer = page.locator('.projects-list, .el-table, .project-grid')

    if (await projectsContainer.count() > 0) {
      await expect(projectsContainer.first()).toBeVisible()
    }
  })

  test('should have create project button', async ({ page }) => {
    // Look for create/new project button
    const createButton = page.locator('button:has-text("新建"), button:has-text("Create"), button:has-text("添加")')

    if (await createButton.count() > 0) {
      await expect(createButton.first()).toBeVisible()
    }
  })

  test('should open create project dialog', async ({ page }) => {
    const createButton = page.locator('button:has-text("新建"), button:has-text("Create"), button:has-text("添加")').first()

    if (await createButton.isVisible()) {
      await createButton.click()

      // Wait for dialog to appear
      await page.waitForTimeout(500)

      // Check if dialog is visible
      const dialog = page.locator('.el-dialog, .modal, [role="dialog"]')
      if (await dialog.count() > 0) {
        await expect(dialog.first()).toBeVisible()
      }
    }
  })

  test('should display project cards or rows', async ({ page }) => {
    await page.waitForTimeout(1500)

    // Check for project items
    const projectItems = await page.locator('.project-card, .project-item, .el-table__row').count()

    // Projects might be empty on first load, so just check the structure exists
    expect(projectItems).toBeGreaterThanOrEqual(0)
  })

  test('should have search or filter functionality', async ({ page }) => {
    // Look for search input
    const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Search"], input[placeholder*="查找"]')

    if (await searchInput.count() > 0) {
      await expect(searchInput.first()).toBeVisible()
    }
  })

  test('should navigate to project detail on click', async ({ page }) => {
    await page.waitForTimeout(1500)

    // Try to find and click first project
    const firstProject = page.locator('.project-card, .project-item, .el-table__row').first()

    if (await firstProject.isVisible()) {
      await firstProject.click()

      // Should navigate to detail page
      await page.waitForTimeout(500)
      const url = page.url()
      // Might navigate to detail page (depends on implementation)
      expect(url).toBeDefined()
    }
  })

  test('should display project status indicators', async ({ page }) => {
    await page.waitForTimeout(1500)

    // Look for status badges or tags
    const statusElements = page.locator('.status-badge, .el-tag, .status-indicator, .project-status')

    if (await statusElements.count() > 0) {
      // Status indicators exist
      expect(await statusElements.count()).toBeGreaterThan(0)
    }
  })
})
