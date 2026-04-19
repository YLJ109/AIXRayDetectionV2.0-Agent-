/** 诊断API */
import http from './index'

export const diagnoseSingleApi = (formData: FormData) =>
  http.post('/diagnose/single', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })

export const getDiagnosisApi = (id: number) =>
  http.get(`/diagnose/${id}`)

export const getDiagnosisListApi = (params?: any) =>
  http.get('/diagnose/list', { params })

export const deleteDiagnosisApi = (id: number) =>
  http.delete(`/diagnose/${id}`)
