/** 患者管理API */
import http from './index'

export const getPatientsApi = (params?: any) =>
  http.get('/patients/', { params })

export const getPatientApi = (id: number) =>
  http.get(`/patients/${id}`)

export const createPatientApi = (data: any) =>
  http.post('/patients/', data)

export const updatePatientApi = (id: number, data: any) =>
  http.put(`/patients/${id}`, data)

export const deletePatientApi = (id: number) =>
  http.delete(`/patients/${id}`)
