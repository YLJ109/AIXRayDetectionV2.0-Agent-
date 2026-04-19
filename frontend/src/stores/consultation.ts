import { defineStore } from 'pinia'

const STORAGE_KEY = 'consultation-store'
const STORAGE_VERSION = 'v2'

function loadPersistedState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) return null
    const parsed = JSON.parse(saved)
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

function savePersistedState(state: { sessions: any[]; activeSessionId: number | null; sessionMessages: Record<number, any[]> }) {
  try {
    const toSave = {
      _version: STORAGE_VERSION,
      sessions: state.sessions,
      activeSessionId: state.activeSessionId,
      sessionMessages: state.sessionMessages,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  } catch {
    // ignore
  }
}

export const useConsultationStore = defineStore('consultation', {
  state: () => {
    const persisted = loadPersistedState()
    return {
      sessions: persisted?.sessions || [] as any[],
      activeSessionId: persisted?.activeSessionId || null as number | null,
      sessionMessages: persisted?.sessionMessages || {} as Record<number, any[]>,
    }
  },

  getters: {
    currentMessages: (state) => {
      return state.sessionMessages[state.activeSessionId as number] || []
    },
    currentSession: (state) => {
      return state.sessions.find((s: any) => s.id === state.activeSessionId) || null
    },
  },

  actions: {
    switchSession(sessionId: number) {
      this.activeSessionId = sessionId
      savePersistedState(this.$state as any)
    },

    createSession({ expertId, expertName }: { expertId?: string; expertName?: string } = {}) {
      const id = Date.now()
      const now = new Date()
      this.sessions.unshift({
        id,
        title: `与${expertName || 'AI专家'}的对话`,
        expertId: expertId || 'general',
        time: now.toISOString(),
        createdAt: now.toISOString(),
      })
      ;(this.sessionMessages as any)[id] = []
      this.activeSessionId = id
      savePersistedState(this.$state as any)
      return id
    },

    addMessage(message: { role: string; content: string; time: string }) {
      const sessionId = this.activeSessionId as number
      if (!(this.sessionMessages as any)[sessionId]) {
        ;(this.sessionMessages as any)[sessionId] = []
      }
      ;(this.sessionMessages as any)[sessionId].push(message)
      if (message.role === 'user' && (this.sessionMessages as any)[sessionId].length === 1) {
        const session = this.sessions.find((s: any) => s.id === sessionId)
        if (session) {
          session.title = message.content.slice(0, 16) + (message.content.length > 16 ? '...' : '')
        }
      }
      savePersistedState(this.$state as any)
    },

    clearCurrentMessages() {
      ;(this.sessionMessages as any)[this.activeSessionId as number] = []
      savePersistedState(this.$state as any)
    },

    deleteSession(sessionId: number) {
      const index = this.sessions.findIndex((s: any) => s.id === sessionId)
      if (index > -1) {
        this.sessions.splice(index, 1)
        delete (this.sessionMessages as any)[sessionId]
        if (this.activeSessionId === sessionId && this.sessions.length > 0) {
          this.activeSessionId = this.sessions[0].id
        } else if (this.sessions.length === 0) {
          this.activeSessionId = null
        }
        savePersistedState(this.$state as any)
      }
    },

    updateSessionTime(sessionId: number) {
      const session = this.sessions.find((s: any) => s.id === sessionId)
      if (session) {
        session.time = new Date().toISOString()
        savePersistedState(this.$state as any)
      }
    },
  },
})
