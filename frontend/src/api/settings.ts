/** 系统设置API */
import http from './index'

export const getSettingsApi = () =>
  http.get('/settings/')

export const updateSettingApi = (key: string, data: any) =>
  http.put(`/settings/${key}`, data)

export const batchUpdateSettingsApi = (settings: Record<string, any>) =>
  http.put('/settings/batch', { settings })
