# ResoftAI 前端管理界面

基于 Vue 3 + Element Plus 的现代化管理界面。

## 功能模块

### 1. 仪表板 (Dashboard)
- 项目总览统计
- 智能体工作状态
- 实时进度监控
- 系统资源使用情况

### 2. 项目管理 (Projects)
- 创建新项目
- 项目列表查看
- 项目详情展示
- 任务进度追踪
- 文档生成记录

### 3. 智能体管理 (Agents)
- 智能体状态监控
- 实时工作日志
- 性能指标统计
- 智能体配置管理

### 4. 文件管理 (Files)
- 项目文件浏览
- 源码查看编辑
- 版本历史记录
- 文件下载导出

### 5. 模型配置 (Models)
- LLM模型选择
- API密钥配置
- 参数调优设置
- 模型切换管理

## 技术栈

- **框架**: Vue 3.4 (Composition API)
- **UI库**: Element Plus 2.5
- **状态管理**: Pinia 2.1
- **路由**: Vue Router 4.2
- **HTTP客户端**: Axios 1.6
- **实时通信**: Socket.io-client 4.6
- **图表**: ECharts 5.4
- **构建工具**: Vite 5.0

## 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物在 `dist/` 目录。

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口封装
│   │   ├── client.js      # Axios 客户端
│   │   ├── projects.js    # 项目API
│   │   ├── agents.js      # 智能体API
│   │   └── files.js       # 文件API
│   ├── components/        # 公共组件
│   │   ├── ProjectCard.vue
│   │   ├── AgentStatus.vue
│   │   ├── TaskList.vue
│   │   └── FileTree.vue
│   ├── views/             # 页面视图
│   │   ├── Layout.vue     # 主布局
│   │   ├── Dashboard.vue  # 仪表板
│   │   ├── Projects.vue   # 项目列表
│   │   ├── ProjectDetail.vue  # 项目详情
│   │   ├── Agents.vue     # 智能体管理
│   │   ├── Files.vue      # 文件管理
│   │   └── Models.vue     # 模型配置
│   ├── router/            # 路由配置
│   ├── store/             # 状态管理
│   │   ├── project.js
│   │   ├── agent.js
│   │   └── user.js
│   ├── utils/             # 工具函数
│   │   ├── websocket.js
│   │   └── format.js
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html
├── vite.config.js         # Vite 配置
└── package.json
```

## API 接口

前端通过 `/api` 代理访问后端API：

```javascript
// 示例：创建项目
import { projectsApi } from '@/api/projects'

const createProject = async () => {
  const data = {
    name: '项目名称',
    requirements: '项目需求描述'
  }

  try {
    const result = await projectsApi.createProject(data)
    console.log('项目创建成功:', result)
  } catch (error) {
    console.error('创建失败:', error)
  }
}
```

## WebSocket 实时通信

```javascript
import { io } from 'socket.io-client'

const socket = io('ws://localhost:8000/ws')

// 监听项目进度
socket.on('project:progress', (data) => {
  console.log('项目进度更新:', data)
})

// 监听智能体状态
socket.on('agent:status', (data) => {
  console.log('智能体状态:', data)
})
```

## 主要功能实现

### 1. 项目创建

```vue
<template>
  <el-button type="primary" @click="showDialog = true">
    创建新项目
  </el-button>

  <el-dialog v-model="showDialog" title="创建项目">
    <el-form :model="form" label-width="100px">
      <el-form-item label="项目名称">
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="需求描述">
        <el-input
          v-model="form.requirements"
          type="textarea"
          :rows="6"
        />
      </el-form-item>
      <el-form-item label="AI模型">
        <el-select v-model="form.provider">
          <el-option label="Claude" value="anthropic" />
          <el-option label="智谱GLM-4" value="zhipu" />
          <el-option label="DeepSeek" value="deepseek" />
          <el-option label="Kimi" value="moonshot" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showDialog = false">取消</el-button>
      <el-button type="primary" @click="handleCreate">
        创建
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { projectsApi } from '@/api/projects'
import { ElMessage } from 'element-plus'

const showDialog = ref(false)
const form = ref({
  name: '',
  requirements: '',
  provider: 'anthropic'
})

const handleCreate = async () => {
  try {
    await projectsApi.createProject(form.value)
    ElMessage.success('项目创建成功')
    showDialog.value = false
  } catch (error) {
    ElMessage.error('创建失败')
  }
}
</script>
```

### 2. 实时进度监控

```vue
<template>
  <div class="progress-monitor">
    <el-progress
      :percentage="progress"
      :status="status"
    />
    <div class="stage-info">
      当前阶段: {{ currentStage }}
    </div>
    <el-timeline>
      <el-timeline-item
        v-for="log in logs"
        :key="log.id"
        :timestamp="log.timestamp"
      >
        {{ log.message }}
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

const progress = ref(0)
const status = ref('success')
const currentStage = ref('')
const logs = ref([])

let socket

onMounted(() => {
  socket = io('ws://localhost:8000/ws')

  socket.on('progress', (data) => {
    progress.value = data.percentage
    currentStage.value = data.stage
  })

  socket.on('log', (data) => {
    logs.value.unshift(data)
  })
})

onUnmounted(() => {
  socket?.disconnect()
})
</script>
```

### 3. 智能体状态监控

```vue
<template>
  <el-row :gutter="20">
    <el-col
      v-for="agent in agents"
      :key="agent.id"
      :span="8"
    >
      <el-card class="agent-card">
        <template #header>
          <div class="card-header">
            <span>{{ agent.name }}</span>
            <el-tag
              :type="agent.status === 'active' ? 'success' : 'info'"
            >
              {{ agent.status }}
            </el-tag>
          </div>
        </template>
        <div class="agent-info">
          <div class="info-item">
            <span>当前任务:</span>
            <span>{{ agent.currentTask }}</span>
          </div>
          <div class="info-item">
            <span>已完成:</span>
            <span>{{ agent.completedTasks }}</span>
          </div>
          <div class="info-item">
            <span>Token使用:</span>
            <span>{{ agent.tokensUsed }}</span>
          </div>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { agentsApi } from '@/api/agents'

const agents = ref([])

onMounted(async () => {
  agents.value = await agentsApi.getAgents()
})
</script>
```

## 环境变量

创建 `.env.local` 文件：

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api

# WebSocket URL
VITE_WS_URL=ws://localhost:8000/ws
```

## 开发指南

### 添加新页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.js` 添加路由
3. 在 `Layout.vue` 添加菜单项

### 添加新API

1. 在 `src/api/` 创建API文件
2. 使用 `apiClient` 封装接口
3. 在组件中导入使用

### 状态管理

使用 Pinia 管理全局状态：

```javascript
// stores/project.js
import { defineStore } from 'pinia'

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [],
    currentProject: null
  }),

  actions: {
    async fetchProjects() {
      this.projects = await projectsApi.getProjects()
    }
  }
})
```

## 部署

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/resoftai-frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 注意事项

1. **API代理**: 开发环境通过Vite代理，生产环境需配置Nginx
2. **WebSocket**: 确保后端支持WebSocket连接
3. **认证**: 实现完整的用户认证和权限管理
4. **错误处理**: 所有API调用都应有错误处理
5. **性能优化**: 大数据量场景使用虚拟滚动和分页

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 许可证

MIT
