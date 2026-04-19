/** 认证API */
import http from './index'

export const loginApi = (data: { username: string; password: string }) =>
  http.post('/auth/login', data)

export const registerApi = (data: any) =>
  http.post('/auth/register', data)

export const getCurrentUserApi = () =>
  http.get('/auth/me')

export const changePasswordApi = (data: { old_password: string; new_password: string }) =>
  http.post('/auth/change-password', data)

export const logoutApi = () =>
  http.post('/auth/logout')
