# ESLint Integration Plugin

ESLint代码质量检查集成插件，自动运行lint并修复问题。

## 功能特性

- **自动代码检查** - 保存时自动运行ESLint
- **自动修复** - 一键修复可自动修复的问题
- **Git Hook集成** - 提交前自动检查代码
- **CI/CD支持** - 轻松集成到CI/CD流程
- **详细报告** - 清晰的问题分类和统计

## 前置要求

需要在项目中安装ESLint：

```bash
# npm
npm install --save-dev eslint

# yarn
yarn add --dev eslint

# pnpm
pnpm add -D eslint
```

## 安装

```bash
resoftai plugin install eslint-integration
```

## 配置

### 基础配置

```json
{
  "eslint_path": "eslint",
  "config_file": ".eslintrc.js",
  "auto_fix": false,
  "run_on_save": true,
  "run_on_commit": true
}
```

### 高级配置

```json
{
  "eslint_path": "./node_modules/.bin/eslint",
  "config_file": ".eslintrc.json",
  "file_patterns": [
    "src/**/*.js",
    "src/**/*.ts",
    "src/**/*.jsx",
    "src/**/*.tsx"
  ],
  "ignore_patterns": [
    "node_modules/**",
    "dist/**",
    "build/**",
    "coverage/**"
  ],
  "auto_fix": true,
  "max_warnings": 0,
  "run_on_save": true,
  "run_on_commit": true
}
```

## 使用方法

### API调用

```python
from resoftai.plugins.manager import PluginManager

# 获取插件
plugin = plugin_manager.get_plugin("eslint-integration")

# 检查所有文件
result = await plugin.run_lint()

print(f"发现 {result['summary']['total_errors']} 个错误")
print(f"发现 {result['summary']['total_warnings']} 个警告")
```

### 检查特定文件

```python
# 检查单个文件
result = await plugin.run_lint(files=["src/index.js"])

# 检查多个文件
result = await plugin.run_lint(files=[
    "src/components/Header.jsx",
    "src/utils/api.ts"
])
```

### 自动修复

```python
# 检查并自动修复
result = await plugin.run_lint(fix=True)

# 修复单个文件
result = await plugin.fix_file("src/index.js")
```

### 检查整个项目

```python
result = await plugin.check_project("/path/to/project")
```

## 输出示例

### JSON格式

```json
{
  "summary": {
    "total_files": 15,
    "files_with_issues": 3,
    "total_errors": 5,
    "total_warnings": 8
  },
  "files": [
    {
      "file": "/project/src/index.js",
      "errors": 2,
      "warnings": 3,
      "messages": [
        {
          "line": 10,
          "column": 5,
          "severity": "error",
          "message": "Unexpected console statement",
          "rule": "no-console",
          "fix": null
        },
        {
          "line": 15,
          "column": 12,
          "severity": "warning",
          "message": "Missing semicolon",
          "rule": "semi",
          "fix": {
            "range": [234, 234],
            "text": ";"
          }
        }
      ]
    }
  ]
}
```

## Git Hook集成

### 使用Husky

在 `package.json` 中配置：

```json
{
  "husky": {
    "hooks": {
      "pre-commit": "resoftai plugin run eslint-integration lint"
    }
  }
}
```

### 使用lint-staged

```json
{
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": [
      "resoftai plugin run eslint-integration fix",
      "git add"
    ]
  }
}
```

## CI/CD集成

### GitHub Actions

```yaml
name: Lint

on: [push, pull_request]

jobs:
  eslint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: resoftai plugin run eslint-integration lint
```

### GitLab CI

```yaml
eslint:
  script:
    - npm install
    - resoftai plugin run eslint-integration lint
  only:
    - merge_requests
    - main
```

## ESLint配置示例

### JavaScript项目

```js
// .eslintrc.js
module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: 'eslint:recommended',
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'module'
  },
  rules: {
    'no-console': 'warn',
    'semi': ['error', 'always'],
    'quotes': ['error', 'single']
  }
};
```

### TypeScript项目

```js
// .eslintrc.js
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    project: './tsconfig.json'
  },
  rules: {
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/no-explicit-any': 'warn'
  }
};
```

### React项目

```js
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended'
  ],
  parserOptions: {
    ecmaFeatures: {
      jsx: true
    }
  },
  settings: {
    react: {
      version: 'detect'
    }
  },
  rules: {
    'react/prop-types': 'error',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn'
  }
};
```

## 常见问题

### ESLint未找到

确保ESLint已安装：
```bash
npm install -D eslint
```

或在配置中指定ESLint路径：
```json
{
  "eslint_path": "./node_modules/.bin/eslint"
}
```

### 配置文件未找到

指定配置文件路径：
```json
{
  "config_file": "./.eslintrc.json"
}
```

### 检查速度慢

限制检查的文件范围：
```json
{
  "file_patterns": ["src/**/*.js"],
  "ignore_patterns": ["node_modules/**", "dist/**"]
}
```

## 配置选项参考

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `eslint_path` | string | "eslint" | ESLint可执行文件路径 |
| `config_file` | string | - | ESLint配置文件路径 |
| `file_patterns` | array | ["**/*.js", "**/*.ts"] | 要检查的文件模式 |
| `ignore_patterns` | array | ["node_modules/**"] | 要忽略的文件模式 |
| `auto_fix` | boolean | false | 是否自动修复问题 |
| `max_warnings` | integer | 0 | 允许的最大警告数 |
| `run_on_save` | boolean | true | 保存时自动运行 |
| `run_on_commit` | boolean | true | 提交时运行 |

## 许可证

MIT License

## 相关链接

- [ESLint官方文档](https://eslint.org/docs/latest/)
- [ESLint规则列表](https://eslint.org/docs/latest/rules/)
- [创建自定义规则](https://eslint.org/docs/latest/developer-guide/working-with-rules)
