/** 审计日志API */
import http from './index'

export const getAuditLogsApi = (params?: any) =>
  http.get('/audit/logs', { params })

export const getAuditActionTypesApi = () =>
  http.get('/audit/actions')
