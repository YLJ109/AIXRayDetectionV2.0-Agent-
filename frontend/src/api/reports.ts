/** 报告管理API */
import http from './index'

export const getPendingReportsApi = (params?: any) =>
  http.get('/reports/pending', { params })

export const getReportApi = (id: number) =>
  http.get(`/reports/${id}`)

export const updateReportApi = (id: number, data: any) =>
  http.put(`/reports/${id}`, data)

export const approveReportApi = (id: number) =>
  http.post(`/reports/${id}/approve`)

export const rejectReportApi = (id: number, data: { reason: string }) =>
  http.post(`/reports/${id}/reject`, data)

export const regenerateReportApi = (id: number) =>
  http.post(`/reports/${id}/regenerate`)
