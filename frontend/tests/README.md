# Frontend Testing Guide

本文档介绍ResoftAI前端项目的测试套件和使用方法。

## 📋 目录

- [测试框架](#测试框架)
- [测试结构](#测试结构)
- [运行测试](#运行测试)
- [编写测试](#编写测试)
- [测试覆盖率](#测试覆盖率)

## 🛠 测试框架

### 单元测试
- **Vitest**: 快速的单元测试框架，与Vite深度集成
- **@vue/test-utils**: Vue官方测试工具库
- **happy-dom**: 轻量级DOM实现，用于测试环境

### E2E测试
- **Playwright**: 跨浏览器端到端测试框架
- 支持Chrome、Firefox、Safari浏览器

## 📁 测试结构

```
tests/
├── setup.js                          # 单元测试全局配置
├── unit/                             # 单元测试
│   ├── ActiveUsers.spec.js           # ActiveUsers组件测试
│   ├── MonacoEditor.spec.js          # Monaco编辑器测试
│   ├── FilesEnhanced.spec.js         # FilesEnhanced组件测试
│   └── useCollaborativeEditing.spec.js # 协作编辑Hook测试
├── e2e/                              # E2E测试
│   ├── login.spec.js                 # 登录功能测试
│   ├── dashboard.spec.js             # 仪表板测试
│   ├── projects.spec.js              # 项目管理测试
│   └── collaborative-editing.spec.js # 协作编辑E2E测试
└── README.md                         # 本文档
```

## 🚀 运行测试

### 单元测试

```bash
# 运行所有单元测试
npm run test:unit

# 监听模式（开发时推荐）
npm test

# 使用UI界面运行
npm run test:unit:ui

# 生成覆盖率报告
npm run test:coverage
```

### E2E测试

```bash
# 运行所有E2E测试
npm run test:e2e

# 使用UI模式运行
npm run test:e2e:ui

# 有头模式（查看浏览器）
npm run test:e2e:headed

# 调试模式
npm run test:e2e:debug
```

### 运行特定测试

```bash
# 运行特定单元测试文件
npx vitest run tests/unit/ActiveUsers.spec.js

# 运行特定E2E测试文件
npx playwright test tests/e2e/collaborative-editing.spec.js

# 运行匹配模式的测试
npx vitest run -t "ActiveUsers"
```

## ✍️ 编写测试

### 单元测试示例

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: {
        message: 'Hello'
      }
    })

    expect(wrapper.text()).toContain('Hello')
  })

  it('emits event on button click', async () => {
    const wrapper = mount(MyComponent)

    await wrapper.find('button').trigger('click')

    expect(wrapper.emitted('click')).toBeTruthy()
  })
})
```

### E2E测试示例

```javascript
import { test, expect } from '@playwright/test'

test('user can login', async ({ page }) => {
  await page.goto('/login')

  await page.locator('input[type="text"]').fill('username')
  await page.locator('input[type="password"]').fill('password')
  await page.locator('button[type="submit"]').click()

  await expect(page).toHaveURL(/.*dashboard/)
})
```

## 📊 测试覆盖范围

### ActiveUsers组件 (tests/unit/ActiveUsers.spec.js)

✅ 测试覆盖：
- 空用户列表渲染
- 用户数量徽章显示
- 用户列表正确渲染
- 当前用户高亮
- 用户缩写生成（单名/全名）
- 空用户名处理
- 基于用户ID的颜色一致性
- 状态指示器显示

### MonacoEditor组件 (tests/unit/MonacoEditor.spec.js)

✅ 测试覆盖：
- 编辑器容器渲染
- 初始化配置正确性
- 内容变更事件
- 光标位置变更事件
- Props响应式更新（modelValue、language、theme、readonly）
- 远程光标渲染
- 远程选择区域渲染
- 装饰器清理
- 自定义选项应用
- 组件卸载清理
- getEditor方法暴露
- 空内容处理
- 用户颜色一致性

### useCollaborativeEditing Hook (tests/unit/useCollaborativeEditing.spec.js)

✅ 测试覆盖：
- 初始状态
- 方法暴露
- 加入/离开文件会话
- 发送文件编辑
- 发送光标位置
- 远程编辑处理
- 远程光标处理
- 用户加入/离开通知
- 在线用户计数
- 其他用户过滤

### FilesEnhanced组件 (tests/unit/FilesEnhanced.spec.js)

✅ 测试覆盖：
- 组件结构渲染
- 初始加载状态
- 文件树和编辑器区域
- 数据属性初始化
- 协作编辑功能集成
- 文件选择处理
- MonacoEditor集成
- ActiveUsers集成
- 编辑状态管理
- 编辑器内容变更处理
- 光标位置变更处理
- 项目选择管理
- 文件操作（创建、保存、删除）
- 组件卸载清理

### 协作编辑E2E测试 (tests/e2e/collaborative-editing.spec.js)

✅ 测试覆盖：
- 文件页面显示
- 文件树显示
- Monaco编辑器显示
- 在线用户面板
- 项目选择器
- 文件树节点选择
- 文件操作工具栏
- 创建/保存文件按钮
- 协作状态显示
- 在线用户数量
- 文件内容编辑
- 版本历史
- 文件元数据
- 键盘快捷键
- 语言选择器
- 协作通知
- 文件夹展开/折叠
- 远程光标（多用户场景）
- 多用户同时编辑
- 用户加入通知
- 动态用户列表更新

## 🎯 测试覆盖率

覆盖率报告会在运行 `npm run test:coverage` 后生成。

查看覆盖率报告：
```bash
# 生成覆盖率报告
npm run test:coverage

# 在浏览器中查看HTML报告
open coverage/index.html
```

## 🔧 Mock配置

### 全局Mock (tests/setup.js)

项目已配置以下全局mock：

- **Element Plus**: `$message` 和 `$notify` API
- **Monaco Editor**: 编辑器实例和API
- **Socket.IO**: WebSocket客户端
- **ECharts**: 图表库
- **window.matchMedia**: 媒体查询API

### 自定义Mock

在单个测试文件中mock模块：

```javascript
vi.mock('@/api/users', () => ({
  default: {
    getUsers: vi.fn(() => Promise.resolve({ data: [] }))
  }
}))
```

## 🐛 调试测试

### Vitest调试

```bash
# 使用UI界面调试
npm run test:unit:ui

# 在测试中使用调试器
import { test } from 'vitest'

test('debug test', () => {
  debugger // 在浏览器DevTools中暂停
  // ... 测试代码
})
```

### Playwright调试

```bash
# 调试模式运行
npm run test:e2e:debug

# 或使用Playwright Inspector
npx playwright test --debug
```

## 📝 最佳实践

### 单元测试

1. **保持测试独立**: 每个测试应该独立运行
2. **使用描述性名称**: 测试名称应该清楚说明测试内容
3. **遵循AAA模式**: Arrange（准备）、Act（执行）、Assert（断言）
4. **Mock外部依赖**: 隔离被测单元
5. **测试边界情况**: 不仅测试正常流程，也测试异常情况

### E2E测试

1. **测试用户流程**: 模拟真实用户操作
2. **使用有意义的选择器**: 优先使用语义化选择器
3. **等待异步操作**: 使用适当的等待策略
4. **保持测试稳定**: 避免脆弱的测试
5. **清理测试数据**: 确保测试环境干净

## 🔄 持续集成

测试应该在CI/CD流程中自动运行：

```yaml
# .github/workflows/test.yml 示例
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm run test:unit
      - run: npm run test:e2e
```

## 📚 参考资料

- [Vitest文档](https://vitest.dev/)
- [Vue Test Utils文档](https://test-utils.vuejs.org/)
- [Playwright文档](https://playwright.dev/)
- [Testing Library最佳实践](https://testing-library.com/docs/guiding-principles)

## ❓ 常见问题

### Q: 测试运行很慢怎么办？

A:
- 使用 `vitest run` 而不是 watch 模式
- 并行运行测试（Vitest默认支持）
- 考虑使用测试分片

### Q: Monaco Editor mock不工作？

A: 确保在 `tests/setup.js` 中正确配置了Monaco mock。

### Q: E2E测试超时？

A: 增加超时时间或优化页面加载速度：
```javascript
test('my test', async ({ page }) => {
  await page.goto('/path', { timeout: 30000 })
})
```

### Q: 如何测试WebSocket功能？

A: 使用mock的Socket.IO客户端（已在setup.js中配置），或使用真实的WebSocket服务器进行E2E测试。

## 🎓 学习资源

- **Vitest课程**: [官方教程](https://vitest.dev/guide/)
- **Vue Testing**: [Vue Test Utils教程](https://lmiller1990.github.io/vue-testing-handbook/)
- **Playwright学习**: [Playwright University](https://playwright.dev/docs/intro)

---

**版本**: 1.0.0
**最后更新**: 2025-11-14
**维护者**: ResoftAI团队
