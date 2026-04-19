/** 诊断审批API */
import http from './index'

export const getApprovalsApi = (params?: any) =>
  http.get('/approvals/', { params })

export const getApprovalApi = (id: number) =>
  http.get(`/approvals/${id}`)

export const createApprovalApi = (data: any) =>
  http.post('/approvals/', data)

export const updateApprovalApi = (id: number, data: any) =>
  http.put(`/approvals/${id}`, data)

export const deleteApprovalApi = (id: number) =>
  http.delete(`/approvals/${id}`)

export const approveApprovalApi = (id: number, data?: any) =>
  http.post(`/approvals/${id}/approve`, data)

export const rejectApprovalApi = (id: number, data: any) =>
  http.post(`/approvals/${id}/reject`, data)

export const requestRevisionApi = (id: number, data: any) =>
  http.post(`/approvals/${id}/revise`, data)

export const getApprovalStatsApi = () =>
  http.get('/approvals/stats')

export const syncMissingApprovalsApi = () =>
  http.post('/approvals/sync-missing')
