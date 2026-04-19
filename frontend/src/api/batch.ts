/** 批量诊断API */
import http from './index'

export const batchDiagnoseApi = (formData: FormData) =>
  http.post('/batch/diagnose', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  })

export const getBatchProgressApi = (batchId: number) =>
  http.get(`/batch/${batchId}/progress`)

export const cancelBatchApi = (batchId: number) =>
  http.post(`/batch/${batchId}/cancel`)

export const batchGenerateReportsApi = (batchId: number, clinicalFindings?: Record<string, string>) =>
  http.post(`/batch/${batchId}/generate-reports`, { clinical_findings: clinicalFindings || {} })

export const batchUploadApi = (formData: FormData) =>
  http.post('/batch/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
  })

export const getBatchListApi = (params?: any) =>
  http.get('/batch/list', { params })

export const getBatchDetailApi = (id: number) =>
  http.get(`/batch/${id}`)
