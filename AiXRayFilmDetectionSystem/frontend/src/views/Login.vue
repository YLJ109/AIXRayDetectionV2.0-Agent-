<template>
  <div class="login-container">
    <!-- 背景光效 -->
    <div class="bg-glow glow-1"></div>
    <div class="bg-glow glow-2"></div>
    <div class="bg-glow glow-3"></div>

    <div class="login-card">
      <!-- 顶部光线条 -->
      <div class="card-glow-line"></div>
      
      <div class="login-header">
        <div class="login-logo">
          <svg viewBox="0 0 1024 1024" fill="none">
            <path d="M420.27 298.84L256 725.33h69.29l40.02-109.91h183.38l40.02 109.91h69.89L494.35 298.84H420.27zM385.02 561.66l71.08-192.94h2.39l70.49 192.94H385.02z" fill="#10b981"/>
            <path d="M701.61 298.84V725.33h64.51V298.84z" fill="#10b981"/>
            <path d="M893.23 21.33c57.81 0 105.47 43.22 109.23 98.3l.21 6.96V256h-42.67V126.59c0-32.43-26.45-59.43-60.63-62.34l-6.14-.25H768v-42.67h125.23z" fill="#10b981"/>
            <path d="M1002.67 768v124.12c0 58.58-44.8 106.71-101.59 110.34l-6.87.21H768v-42.67h126.21c34.22 0 62.46-27.01 65.54-61.7l.25-6.18V768h42.67z" fill="#10b981"/>
            <path d="M64 768v127.57c0 32.85 31.57 61.27 73.13 64.17l7 .26H298.67v42.67H144.13c-64.51 0-118.49-43.52-122.54-100.23l-.26-6.82V768H64z" fill="#10b981"/>
            <path d="M298.67 21.33v42.67H143.02a79.36 79.36 0 0 0-78.76 73.56L64 143.79V256H21.33V143.79A122.11 122.11 0 0 1 135.85 21.55l7.17-.22H298.67z" fill="#10b981"/>
          </svg>
        </div>
        <h1 class="login-title">胸影智诊V2.0</h1>
        <p class="login-subtitle">AI胸部X光智能辅助诊断系统</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large"
                    prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" class="login-btn" :loading="loading"
                     @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <div class="footer-line"></div>
        <span>AI辅助诊断，仅供临床医生参考</span>
      </div>
    </div>

    <!-- 底部装饰 -->
    <div class="login-decoration">
      <div class="decoration-ring ring-1"></div>
      <div class="decoration-ring ring-2"></div>
      <div class="decoration-ring ring-3"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const homeRoute = await userStore.login(form)
    const redirect = route.query.redirect || homeRoute
    router.push(redirect)
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

// 背景光效
.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  
  &.glow-1 {
    width: 500px;
    height: 500px;
    top: -150px;
    left: -100px;
    background: var(--primary);
    opacity: 0.12;
  }
  
  &.glow-2 {
    width: 400px;
    height: 400px;
    bottom: -100px;
    right: -50px;
    background: var(--purple);
    opacity: 0.1;
  }
  
  &.glow-3 {
    width: 300px;
    height: 300px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: var(--blue);
    opacity: 0.06;
  }
}

// 登录卡片
.login-card {
  width: 440px;
  padding: 48px 40px;
  background: var(--card-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  position: relative;
  z-index: 10;
  animation: cardEnter 0.6s ease forwards;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.5), transparent);
  }
}

// 卡片顶部发光线
.card-glow-line {
  position: absolute;
  top: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--primary), transparent);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;

  svg {
    width: 72px;
    height: 72px;
  }
}

.login-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: 1px;
}

.login-subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  letter-spacing: 0.5px;
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
  }
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 8px;
  background: linear-gradient(135deg, var(--primary), #059669) !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  
  &:hover {
    box-shadow: 0 8px 30px rgba(16, 185, 129, 0.5) !important;
    transform: translateY(-2px);
  }
}

.login-footer {
  text-align: center;
  margin-top: 32px;
  
  .footer-line {
    width: 60px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
    margin: 0 auto 16px;
  }
  
  span {
    color: var(--text-muted);
    font-size: 12px;
    letter-spacing: 1px;
  }
}

// 底部装饰环
.login-decoration {
  position: absolute;
  bottom: -200px;
  right: -200px;
  pointer-events: none;
}

.decoration-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid;
  
  &.ring-1 {
    width: 300px;
    height: 300px;
    border-color: rgba(16, 185, 129, 0.08);
    animation: ringPulse 6s ease-in-out infinite;
  }
  
  &.ring-2 {
    width: 450px;
    height: 450px;
    border-color: rgba(139, 92, 246, 0.06);
    animation: ringPulse 8s ease-in-out infinite reverse;
  }
  
  &.ring-3 {
    width: 600px;
    height: 600px;
    border-color: rgba(59, 130, 246, 0.04);
    animation: ringPulse 10s ease-in-out infinite;
  }
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes ringPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.05); opacity: 1; }
}
</style>
