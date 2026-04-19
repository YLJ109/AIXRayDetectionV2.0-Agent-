/** 大模型配置API */
import http from './index'

export const getLlmConfigsApi = () =>
  http.get('/llm-configs/')

export const createLlmConfigApi = (data: any) =>
  http.post('/llm-configs/', data)

export const updateLlmConfigApi = (id: number, data: any) =>
  http.put(`/llm-configs/${id}`, data)

export const deleteLlmConfigApi = (id: number) =>
  http.delete(`/llm-configs/${id}`)

export const testLlmConnectionApi = (id: number) =>
  http.post(`/llm-configs/${id}/test`)
