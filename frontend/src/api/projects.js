import apiClient from './client'

export const projectsApi = {
  // 获取项目列表
  getProjects() {
    return apiClient.get('/projects')
  },

  // 创建项目
  createProject(data) {
    return apiClient.post('/projects', data)
  },

  // 获取项目详情
  getProject(id) {
    return apiClient.get(`/projects/${id}`)
  },

  // 获取项目状态
  getProjectStatus(id) {
    return apiClient.get(`/projects/${id}/status`)
  },

  // 获取项目任务
  getProjectTasks(id) {
    return apiClient.get(`/projects/${id}/tasks`)
  },

  // 获取项目文档
  getProjectArtifacts(id) {
    return apiClient.get(`/projects/${id}/artifacts`)
  },

  // 更新项目
  updateProject(id, data) {
    return apiClient.put(`/projects/${id}`, data)
  },

  // 删除项目
  deleteProject(id) {
    return apiClient.delete(`/projects/${id}`)
  },
}
