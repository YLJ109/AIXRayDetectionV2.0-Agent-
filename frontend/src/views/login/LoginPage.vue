/** 登录页面 - 玻璃拟态深色科技风 */
<template>
  <div class="login-page">
    <div class="bg-glow glow-1"></div>
    <div class="bg-glow glow-2"></div>

    <div class="login-container">
      <div class="login-card glass-card">
        <!-- Logo区域 -->
        <div class="login-brand">
          <div class="brand-logo">
            <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M914.28 950.86H109.72c-20.2 0-36.57 16.37-36.57 36.57S89.52 1024 109.72 1024h804.57c20.2 0 36.57-16.37 36.57-36.57s-16.38-36.57-36.58-36.57zM877.71 0H146.28C65.6 0.24 0.24 65.6 0 146.28v585.14c0.24 80.69 65.6 146.04 146.28 146.28h731.43c80.69-0.24 146.05-65.59 146.29-146.28V146.28C1023.76 65.6 958.4 0.24 877.71 0z m-97.13 643.88l-2.12 3.07a43.515 43.515 0 0 1-18.21 15.21c-2.8 1.5-5.74 2.73-8.78 3.66-1.82 0.54-3.68 0.98-5.56 1.32-31.84 5.23-64.51 0.16-93.25-14.48a129.312 129.312 0 0 1-74.02-73.88c-0.57-2.27-1.31-4.49-2.19-6.65-1.19-2.88-2.24-5.8-3.15-8.78a51.962 51.962 0 0 1 4.9-41.18c8.08-15.27 12.2-32.32 12-49.59a89.324 89.324 0 0 0-23.4-64.59 57.278 57.278 0 0 1-17.48-32.91v-1.17a51.326 51.326 0 0 1 4.1-29.99l-39.86-25.82-1.39-0.95-1.24 0.95-39.94 25.75a51.326 51.326 0 0 1 4.1 29.99c-0.17 0.41-0.25 0.86-0.22 1.32A57.06 57.06 0 0 1 457.54 408a89.389 89.389 0 0 0-23.34 64.59c-0.25 17.26 3.83 34.3 11.85 49.59a52.15 52.15 0 0 1 4.6 41.26c-0.9 2.97-1.95 5.9-3.14 8.78-0.89 2.14-1.62 4.34-2.19 6.58a129.504 129.504 0 0 1-73.88 73.88 152.238 152.238 0 0 1-93.33 14.55c-1.9-0.33-3.78-0.77-5.64-1.32-3.03-0.95-5.97-2.17-8.78-3.66a43.883 43.883 0 0 1-18.21-15.22 53.96 53.96 0 0 0-2.12-3.07 319.63 319.63 0 0 1 1.61-250.01c42.86-133.12 124.49-226.96 182.57-209.77a56.324 56.324 0 0 1 30.21 23.48 50.978 50.978 0 0 1 5.63 46.08 112.791 112.791 0 0 0-5.7 47.84l22.67-60.85V165.3c0.81-16.88 14.73-30.15 31.64-30.15 16.9 0 30.82 13.27 31.64 30.15v75.34l22.16 60.71h0.51c0.46-3.52 0.65-7.06 0.59-10.61 0.07-12.65-2.03-25.22-6.22-37.15a50.974 50.974 0 0 1 5.63-46.08 56.238 56.238 0 0 1 30.28-23.4c57.86-17.19 139.7 76.65 182.49 209.7a319.369 319.369 0 0 1 1.53 250.01v0.06z"
                fill="#22d3ee" />
            </svg>
          </div>
          <h1 class="login-title">胸影智诊<span class="title-version">V3.0</span></h1>
          <p class="login-subtitle">胸部X光AI智能辅助诊断系统</p>
          <p class="login-subtitle-en">Chest X-ray AI Intelligent Diagnosis System</p>
        </div>

        <!-- 表单区域 -->
        <el-form ref="formRef" :model="loginForm" :rules="rules" class="login-form">
          <el-form-item prop="username">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" size="large"
              @keyup.enter="handleLogin" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large"
              show-password @keyup.enter="handleLogin" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleLogin">
              <span v-if="!loading">登 录</span>
              <span v-else>正在验证...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 底部信息 -->
        <div class="login-footer">
          <div class="footer-disclaimer">
            <el-icon :size="14">
              <Warning />
            </el-icon>
            <span>AI诊断结果仅供参考，最终诊断以执业医师审核为准</span>
          </div>
          <div class="footer-tech">
            <span>Powered by CheXNet + LLM</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'
import type { FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const loginForm = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await authStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
  overflow: hidden;
}

.login-page .bg-glow.glow-1 {
  top: -100px;
  left: -100px;
}

.login-page .bg-glow.glow-2 {
  bottom: -100px;
  right: -100px;
}

.login-container {
  width: 440px;
  position: relative;
  z-index: 1;
}

.login-card {
  padding: 48px 40px !important;
}

.login-brand {
  text-align: center;
  margin-bottom: 36px;
}

.brand-logo {
  margin-bottom: 20px;
}

.brand-logo svg {
  width: 72px;
  height: 72px;
}

.login-title {
  font-size: 30px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: 2px;
}

.title-version {
  font-size: 16px;
  font-weight: 400;
  color: var(--primary);
  margin-left: 4px;
  opacity: 0.8;
}

.login-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.login-subtitle-en {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.5px;
}

.login-form {
  margin-top: 32px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 6px;
  border-radius: var(--radius-md) !important;
}

.login-footer {
  margin-top: 32px;
  text-align: center;
}

.footer-disclaimer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  color: var(--orange);
  margin-bottom: 8px;
}

.footer-tech {
  font-size: 11px;
  color: var(--text-muted);
  letter-spacing: 1px;
}
</style>
