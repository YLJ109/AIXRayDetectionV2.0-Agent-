/** 智能分诊API */
import http from './index'

export const triageAnalyzeApi = (data: any) =>
  http.post('/triage/analyze', data)

export const getTriageRecordsApi = (params?: any) =>
  http.get('/triage/records', { params })

export const confirmTriageApi = (id: number, data?: any) =>
  http.post(`/triage/${id}/confirm`, data)
