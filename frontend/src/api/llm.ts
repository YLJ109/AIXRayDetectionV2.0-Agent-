import http from './index'

export const llmApi = {
  chat: (data: { messages: Array<{ role: string; content: string }>; temperature?: number; max_tokens?: number }, config?: any) =>
    http.post('/llm/chat', data, config),
}
