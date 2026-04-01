<template>
  <div class="consultation-page">
    <div class="page-header">
      <h1 class="page-title">
        <span class="title-secondary">AI Chat</span>
        <span class="title-sep">/</span>
        <span class="title-main">AI咨询</span>
      </h1>
      <p class="page-subtitle">基于通义千问大模型的智能医疗咨询助手</p>
    </div>

    <div class="chat-layout">
      <!-- 左侧会话列表 -->
      <div class="glass-card session-panel">
        <div class="session-header">
          <h3 class="card-title">会话列表</h3>
          <el-button type="primary" size="small" @click="newSession">
            <el-icon><Plus /></el-icon> 新建
          </el-button>
        </div>
        <div class="session-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            class="session-item"
            :class="{ active: session.id === activeSessionId }"
            @click="switchSession(session.id)"
          >
            <div class="session-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
              </svg>
            </div>
            <div class="session-info">
              <div class="session-title">{{ session.title }}</div>
              <div class="session-time">{{ session.time }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区域 -->
      <div class="glass-card chat-panel">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="chat-bot-info">
            <div class="bot-avatar">
              <svg viewBox="0 0 24 24" fill="white" width="20" height="20">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <div>
              <div class="bot-name">智诊AI助手</div>
              <div class="bot-status">
                <span class="status-dot online"></span> 在线 · 基于通义千问
              </div>
            </div>
          </div>
          <div class="chat-actions">
            <el-tooltip content="清空会话" placement="bottom">
              <el-button circle size="small" @click="clearMessages">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- 消息区域 -->
        <div class="chat-messages" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div class="message welcome-message" v-if="messages.length === 0">
            <div class="message-avatar bot">
              <svg viewBox="0 0 24 24" fill="white" width="18" height="18">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <div class="message-content">
              <div class="message-bubble bot">
                <p>您好，我是<strong>智诊AI助手</strong>，基于通义千问大模型为您提供专业的医疗咨询服务。</p>
                <p>您可以向我咨询以下内容：</p>
                <div class="quick-questions">
                  <div class="quick-q" @click="sendQuickQ('肺部X光片显示异常，可能是什么疾病？')">肺部X光异常解读</div>
                  <div class="quick-q" @click="sendQuickQ('肺炎和肺结核的症状区别是什么？')">肺炎vs肺结核区别</div>
                  <div class="quick-q" @click="sendQuickQ('胸部X光检查有哪些注意事项？')">X光检查注意事项</div>
                  <div class="quick-q" @click="sendQuickQ('肺部结节需要做哪些进一步检查？')">肺结节后续检查</div>
                </div>
                <p class="disclaimer">⚠️ AI回复仅供参考，不能替代专业医生诊断。</p>
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <div
            v-for="(msg, index) in messages"
            :key="index"
            class="message"
            :class="msg.role"
          >
            <!-- AI消息 -->
            <template v-if="msg.role === 'assistant'">
              <div class="message-avatar bot">
                <svg viewBox="0 0 24 24" fill="white" width="18" height="18">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div class="message-content">
                <div class="message-bubble bot" v-html="formatMessage(msg.content)"></div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
            </template>
            <!-- 用户消息 -->
            <template v-else>
              <div class="message-content user-content">
                <div class="message-bubble user">{{ msg.content }}</div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
              <div class="message-avatar user">{{ userName.charAt(0) }}</div>
            </template>
          </div>

          <!-- AI正在输入 -->
          <div class="message assistant" v-if="isTyping">
            <div class="message-avatar bot">
              <svg viewBox="0 0 24 24" fill="white" width="18" height="18">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <div class="message-content">
              <div class="message-bubble bot typing-bubble">
                <div class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <el-input
            v-model="inputText"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="输入您的医疗咨询问题..."
            @keydown.enter.exact="handleSend"
            :disabled="isTyping"
            class="chat-input"
          />
          <el-button
            type="primary"
            class="send-btn"
            @click="handleSend"
            :disabled="!inputText.trim() || isTyping"
            :loading="isTyping"
          >
            <el-icon v-if="!isTyping"><Promotion /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useUserStore, useConsultationStore } from '@/stores'
import { llmApi } from '@/api'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const consultationStore = useConsultationStore()
const userName = computed(() => userStore.userName || '用户')

// 使用 store 管理的状态
const sessions = computed(() => consultationStore.sessions)
const activeSessionId = computed(() => consultationStore.activeSessionId)
const messages = computed(() => consultationStore.currentMessages)

// 本地 UI 状态
const inputText = ref('')
const isTyping = ref(false)
const messagesContainer = ref(null)

// AbortController 用于取消请求
let abortController = null

const SYSTEM_PROMPT = `你是一位专业的医疗AI咨询助手——"智诊AI助手"，基于通义千问大模型，专为胸部X光影像诊断系统提供咨询服务。
你的职责：
1. 解答用户关于肺部疾病（正常、肺炎、肺结核等）的问题
2. 提供胸部X光影像相关的医学知识
3. 给出合理的就医建议和健康指导
回答要求：
- 语言简洁专业，使用中文
- 适当使用 **粗体** 强调重点
- 使用列表或表格对比时保持清晰
- 每次回答末尾提醒：AI回复仅供参考，如有不适请及时就医
- 不做确定性诊断，始终建议用户结合临床检查`


function formatMessage(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
    .replace(/^(#{1,3})\s(.+)$/gm, (m, h, t) => `<strong>${t}</strong>`)
}

function getCurrentTime() {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

function sendQuickQ(text) {
  inputText.value = text
  handleSend()
}

// 取消当前请求
function cancelCurrentRequest() {
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  isTyping.value = false
}

async function handleSend(e) {
  if (e && e.type === 'keydown' && e.shiftKey) return
  const text = inputText.value.trim()
  if (!text || isTyping.value) return

  // 取消之前的请求
  cancelCurrentRequest()

  // 添加用户消息
  consultationStore.addMessage({ role: 'user', content: text, time: getCurrentTime() })
  consultationStore.updateSessionTime(activeSessionId.value)
  inputText.value = ''
  scrollToBottom()

  // 创建新的 AbortController
  abortController = new AbortController()
  isTyping.value = true

  try {
    const chatMessages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...messages.value.map(m => ({ role: m.role, content: m.content }))
    ]
    const res = await llmApi.chat({
      messages: chatMessages,
      temperature: 0.7,
      max_tokens: 2000
    }, { signal: abortController.signal })

    const aiContent = res.data?.content || '抱歉，服务暂时不可用，请稍后重试。'
    consultationStore.addMessage({ role: 'assistant', content: aiContent, time: getCurrentTime() })
  } catch (err) {
    // 如果是取消导致的错误，不显示提示
    if (err.name !== 'AbortError' && err.code !== 'ERR_CANCELED') {
      consultationStore.addMessage({
        role: 'assistant',
        content: '抱歉，AI服务调用失败，请检查网络或稍后重试。',
        time: getCurrentTime()
      })
      ElMessage.error('AI回复失败，请重试')
    }
  } finally {
    isTyping.value = false
    abortController = null
    scrollToBottom()
  }
}

function newSession() {
  cancelCurrentRequest()
  consultationStore.createSession()
  scrollToBottom()
}

function switchSession(id) {
  // 取消当前请求
  cancelCurrentRequest()
  // 切换会话
  consultationStore.switchSession(id)
  // 滚动到底部
  nextTick(() => scrollToBottom())
}

function clearMessages() {
  cancelCurrentRequest()
  consultationStore.clearCurrentMessages()
}

// 监听会话切换，滚动到底部
watch(activeSessionId, () => {
  nextTick(() => scrollToBottom())
})

// 组件卸载时清理
onBeforeUnmount(() => {
  cancelCurrentRequest()
})

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped lang="scss">
.consultation-page {
  .page-header {
    margin-bottom: 24px;
    .page-title {
      display: flex; align-items: center; gap: 12px;
      margin-bottom: 8px; font-size: 28px; font-weight: 700;
      .title-secondary { color: var(--text-secondary); font-weight: 400; font-size: 20px; }
      .title-sep { color: var(--glass-border); font-weight: 300; }
      .title-main { color: var(--text-primary); }
    }
    .page-subtitle { font-size: 14px; color: var(--text-secondary); }
  }

  .chat-layout {
    display: grid;
    grid-template-columns: 260px 1fr;
    gap: 20px;
    height: calc(100vh - 180px);
    min-height: 500px;
  }
}

// 会话列表面板
.session-panel {
  display: flex;
  flex-direction: column;
  padding: 0 !important;
  overflow: hidden;

  .session-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid var(--glass-border);
  }

  .session-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  .session-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-normal);
    margin-bottom: 4px;

    &:hover { background: var(--glass-bg); }
    &.active {
      background: var(--primary-light);
    }

    .session-icon {
      width: 36px; height: 36px;
      background: var(--glass-bg);
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      color: var(--text-secondary);
      flex-shrink: 0;
    }

    .session-info { flex: 1; overflow: hidden; }
    .session-title {
      font-size: 13px; font-weight: 500; color: var(--text-primary);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .session-time { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
  }
}

// 聊天面板
.chat-panel {
  display: flex;
  flex-direction: column;
  padding: 0 !important;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--glass-border);
  flex-shrink: 0;

  .chat-bot-info { display: flex; align-items: center; gap: 12px; }

  .bot-avatar {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--primary), var(--purple));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
  }

  .bot-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }

  .bot-status {
    font-size: 12px; color: var(--text-muted);
    display: flex; align-items: center; gap: 4px;
    margin-top: 2px;
  }

  .status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    &.online { background: var(--primary); box-shadow: 0 0 6px rgba(16, 185, 129, 0.6); }
  }
}

// 消息区域
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
  animation: msgEnter 0.3s ease;

  &.user {
    align-self: flex-end;
    flex-direction: row-reverse;
  }

  &.assistant { align-self: flex-start; }
}

@keyframes msgEnter {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-avatar {
  width: 36px; height: 36px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  font-size: 14px; font-weight: 600;

  &.bot {
    background: linear-gradient(135deg, var(--primary), var(--purple));
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
  }

  &.user {
    background: linear-gradient(135deg, var(--blue), var(--primary));
    color: white;
  }
}

.message-content { display: flex; flex-direction: column; gap: 4px; }
.user-content { align-items: flex-end; }

.message-bubble {
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;

  &.bot {
    background: var(--card-bg);
    border: 1px solid var(--glass-border);
    color: var(--text-primary);
    border-top-left-radius: 4px;
  }

  &.user {
    background: var(--primary);
    color: white;
    border-top-right-radius: 4px;
  }
}

.message-time {
  font-size: 11px;
  color: var(--text-muted);
  padding: 0 4px;
}

// 快捷问题
.quick-questions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 12px 0;
}

.quick-q {
  padding: 10px 14px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--primary);
  cursor: pointer;
  transition: all var(--transition-normal);
  text-align: center;

  &:hover {
    background: var(--glass-bg-hover);
    border-color: var(--glass-border-hover);
    transform: translateY(-1px);
  }
}

.disclaimer {
  font-size: 12px !important;
  color: var(--orange) !important;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--glass-border);
}

// 打字动画
.typing-bubble { padding: 16px 20px; }

.typing-indicator {
  display: flex; gap: 5px; align-items: center;

  span {
    width: 8px; height: 8px;
    background: var(--text-secondary);
    border-radius: 50%;
    animation: typingBounce 1.4s ease-in-out infinite;
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes typingBounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

// 输入区域
.chat-input-area {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--glass-border);
  flex-shrink: 0;

  .chat-input {
    flex: 1;
    :deep(.el-textarea__inner) {
      background: var(--glass-bg) !important;
      border: 1px solid var(--glass-border) !important;
      color: var(--text-primary) !important;
      border-radius: var(--radius-md) !important;
      padding: 12px 16px !important;
      resize: none;
      font-size: 14px;

      &::placeholder { color: var(--text-muted); }
      &:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
      }
    }
  }

  .send-btn {
    width: 48px; height: 48px;
    border-radius: var(--radius-md) !important;
    flex-shrink: 0;
  }
}

// 欢迎消息样式
.welcome-message .message-bubble.bot p {
  margin-bottom: 8px;
  &:last-child { margin-bottom: 0; }
  strong { color: var(--primary); }
}
</style>
