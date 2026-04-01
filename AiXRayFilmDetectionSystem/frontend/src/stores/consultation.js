import { defineStore } from 'pinia'

const STORAGE_KEY = 'consultation-store'

// 从 localStorage 读取持久化数据
function loadPersistedState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    return saved ? JSON.parse(saved) : null
  } catch {
    return null
  }
}

// 保存到 localStorage
function savePersistedState(state) {
  try {
    const toSave = {
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
 * 用于管理会话列表和消息历史
 */
export const useConsultationStore = defineStore('consultation', {
  state: () => {
    const persisted = loadPersistedState()
    return {
      // 会话列表
      sessions: persisted?.sessions || [
        { id: 1, title: '肺部X光异常咨询', time: '今天 14:30' },
        { id: 2, title: '肺炎预防建议', time: '今天 10:15' },
        { id: 3, title: '影像学检查对比', time: '昨天 16:42' },
        { id: 4, title: '肺结核早期症状', time: '03-28' }
      ],
      // 当前活跃会话ID
      activeSessionId: persisted?.activeSessionId || 1,
      // 各会话的消息历史 { sessionId: [messages] }
      sessionMessages: persisted?.sessionMessages || {
        1: [
          { role: 'user', content: '我最近拍了一张胸部X光片，医生说肺部有斑片状阴影，这是什么意思？', time: '14:28' },
          { role: 'assistant', content: '肺部斑片状阴影是X光片中常见的异常表现之一，通常提示以下可能：\n\n1. **肺炎**（最常见）- 细菌性或病毒性感染\n2. **肺结核** - 需结合其他检查鉴别\n3. **肺部感染** - 真菌或其他病原体\n\n建议您：\n- 进行痰培养和药敏试验\n- 完善血常规、CRP等炎症指标\n- 必要时做胸部CT进一步明确\n- 可使用本系统「诊断中心」上传影像进行AI辅助筛查\n\n⚠️ AI回复仅供参考，如有不适请及时就医。', time: '14:30' }
        ]
      }
    }
  },

  getters: {
    // 当前会话的消息列表
    currentMessages: (state) => {
      return state.sessionMessages[state.activeSessionId] || []
    },
    // 当前会话信息
    currentSession: (state) => {
      return state.sessions.find(s => s.id === state.activeSessionId) || null
    }
  },

  actions: {
    // 切换会话
    switchSession(sessionId) {
      this.activeSessionId = sessionId
      savePersistedState(this.$state)
    },

    // 新建会话
    createSession(title = '新咨询会话') {
      const id = Date.now()
      this.sessions.unshift({
        id,
        title,
        time: '刚刚'
      })
      this.sessionMessages[id] = []
      this.activeSessionId = id
      savePersistedState(this.$state)
      return id
    },

    // 添加消息到当前会话
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
          session.title = message.content.slice(0, 20) + (message.content.length > 20 ? '...' : '')
        }
      }
      savePersistedState(this.$state)
    },

    // 清空当前会话消息
    clearCurrentMessages() {
      this.sessionMessages[this.activeSessionId] = []
      savePersistedState(this.$state)
    },

    // 删除会话
    deleteSession(sessionId) {
      const index = this.sessions.findIndex(s => s.id === sessionId)
      if (index > -1) {
        this.sessions.splice(index, 1)
        delete this.sessionMessages[sessionId]
        // 如果删除的是当前会话，切换到第一个
        if (this.activeSessionId === sessionId && this.sessions.length > 0) {
          this.activeSessionId = this.sessions[0].id
        }
        savePersistedState(this.$state)
      }
    },

    // 更新会话时间
    updateSessionTime(sessionId) {
      const session = this.sessions.find(s => s.id === sessionId)
      if (session) {
        session.time = '刚刚'
        savePersistedState(this.$state)
      }
    }
  }
})
