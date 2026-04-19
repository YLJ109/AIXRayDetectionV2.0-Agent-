/** 数据看板API */
import http from './index'

export const getDashboardStatsApi = () =>
  http.get('/dashboard/stats')

export const getDiseaseDistributionApi = () =>
  http.get('/dashboard/disease-distribution')

export const getDiagnosisTrendApi = () =>
  http.get('/dashboard/trend')

export const getSystemOverviewApi = () =>
  http.get('/dashboard/system-overview')
