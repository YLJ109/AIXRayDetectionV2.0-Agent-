/** 用户管理API */
import http from './index'

export const getUsersApi = (params?: any) =>
  http.get('/users/', { params })

export const getUserApi = (id: number) =>
  http.get(`/users/${id}`)

export const updateUserApi = (id: number, data: any) =>
  http.put(`/users/${id}`, data)

export const deleteUserApi = (id: number) =>
  http.delete(`/users/${id}`)

export const resetPasswordApi = (id: number, data?: any) =>
  http.post(`/users/${id}/reset-password`, data)

export const updatePreferencesApi = (userId: number, data: any) =>
  http.put(`/users/${userId}/preferences`, data)
