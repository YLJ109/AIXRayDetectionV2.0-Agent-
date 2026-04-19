/** 模型权重管理API */
import http from './index'

export const getModelWeightsApi = () =>
  http.get('/model-weights/')

export const uploadModelWeightApi = (formData: FormData) =>
  http.post('/model-weights/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  })

export const activateModelWeightApi = (id: number) =>
  http.post(`/model-weights/${id}/activate`)

export const deleteModelWeightApi = (id: number) =>
  http.delete(`/model-weights/${id}`)

export const getActiveModelInfoApi = () =>
  http.get('/model-weights/active-info')

export const updateModelParamsApi = (data: any) =>
  http.put('/model-weights/params', data)
