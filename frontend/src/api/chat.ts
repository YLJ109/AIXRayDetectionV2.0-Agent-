/** AI咨询API */
import http from './index'

export const getChatSessionsApi = () =>
  http.get('/chat/sessions')

export const createChatSessionApi = (data: any) =>
  http.post('/chat/sessions', data)

export const deleteChatSessionApi = (id: number) =>
  http.delete(`/chat/sessions/${id}`)

export const getChatMessagesApi = (sessionId: number) =>
  http.get(`/chat/sessions/${sessionId}/messages`)

export const sendMessageApi = (sessionId: number, content: string) =>
  http.post(`/chat/sessions/${sessionId}/send`, { content })

// 流式消息URL
export const getStreamUrl = (sessionId: number) =>
  `/api/v1/chat/sessions/${sessionId}/send`
