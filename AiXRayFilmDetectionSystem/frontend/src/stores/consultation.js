import { defineStore } from 'pinia'

const STORAGE_KEY = 'consultation-store'
const STORAGE_VERSION = 'v2'

// 从 localStorage 读取持久化数据（带版本检查，旧版数据自动清除）
function loadPersistedState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return null
    const parsed = JSON.parse(saved)
    // 版本不兼容时清除旧数据
    if (parsed._version !== STORAGE_VERSION) {
      localStorage.removeItem(STORAGE_KEY)
      return null
    }
    return parsed
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return null
  }
}

// 保存到 localStorage
function savePersistedState(state) {
  try {
    const toSave = {
      _version: STORAGE_VERSION,
      sessions: state.sessions,
      activeSessionId: state.activeSessionId,
      sessionMessages: state.sessionMessages
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  } catch {
    // ignore
  }
}

/**
 * AI咨询状态持久化 Store
 * 管理会话列表、消息历史、专家绑定
 */
export const useConsultationStore = defineStore('consultation', {
  state: () => {
    const persisted = loadPersistedState()
    return {
      sessions: persisted?.sessions || [],
      activeSessionId: persisted?.activeSessionId || null,
      sessionMessages: persisted?.sessionMessages || {}
    }
  },

  getters: {
    currentMessages: (state) => {
      return state.sessionMessages[state.activeSessionId] || []
    },
    currentSession: (state) => {
      return state.sessions.find(s => s.id === state.activeSessionId) || null
    }
  },

  actions: {
    switchSession(sessionId) {
      this.activeSessionId = sessionId
      savePersistedState(this.$state)
    },

    createSession({ expertId, expertName } = {}) {
      const id = Date.now()
      const now = new Date()
      this.sessions.unshift({
        id,
        title: `与${expertName || 'AI专家'}的对话`,
        expertId: expertId || 'general',
        time: now.toISOString(),
        createdAt: now.toISOString()
      })
      this.sessionMessages[id] = []
      this.activeSessionId = id
      savePersistedState(this.$state)
      return id
    },

    addMessage(message) {
      const sessionId = this.activeSessionId
      if (!this.sessionMessages[sessionId]) {
        this.sessionMessages[sessionId] = []
      }
      this.sessionMessages[sessionId].push(message)
      // 更新会话标题（使用第一条用户消息）
      if (message.role === 'user' && this.sessionMessages[sessionId].length === 1) {
        const session = this.sessions.find(s => s.id === sessionId)
        if (session) {
          session.title = message.content.slice(0, 16) + (message.content.length > 16 ? '...' : '')
        }
      }
      savePersistedState(this.$state)
    },

    clearCurrentMessages() {
      this.sessionMessages[this.activeSessionId] = []
      savePersistedState(this.$state)
    },

    deleteSession(sessionId) {
      const index = this.sessions.findIndex(s => s.id === sessionId)
      if (index > -1) {
        this.sessions.splice(index, 1)
        delete this.sessionMessages[sessionId]
        if (this.activeSessionId === sessionId && this.sessions.length > 0) {
          this.activeSessionId = this.sessions[0].id
        } else if (this.sessions.length === 0) {
          this.activeSessionId = null
        }
        savePersistedState(this.$state)
      }
    },

    updateSessionTime(sessionId) {
      const session = this.sessions.find(s => s.id === sessionId)
      if (session) {
        session.time = new Date().toISOString()
        savePersistedState(this.$state)
      }
    }
  }
})
