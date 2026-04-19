/** 管理员布局 - 扁平风格 */
<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M914.28 950.86H109.72c-20.2 0-36.57 16.37-36.57 36.57S89.52 1024 109.72 1024h804.57c20.2 0 36.57-16.37 36.57-36.57s-16.38-36.57-36.58-36.57zM877.71 0H146.28C65.6 0.24 0.24 65.6 0 146.28v585.14c0.24 80.69 65.6 146.04 146.28 146.28h731.43c80.69-0.24 146.05-65.59 146.29-146.28V146.28C1023.76 65.6 958.4 0.24 877.71 0z m-97.13 643.88l-2.12 3.07a43.515 43.515 0 0 1-18.21 15.21c-2.8 1.5-5.74 2.73-8.78 3.66-1.82 0.54-3.68 0.98-5.56 1.32-31.84 5.23-64.51 0.16-93.25-14.48a129.312 129.312 0 0 1-74.02-73.88c-0.57-2.27-1.31-4.49-2.19-6.65-1.19-2.88-2.24-5.8-3.15-8.78a51.962 51.962 0 0 1 4.9-41.18c8.08-15.27 12.2-32.32 12-49.59a89.324 89.324 0 0 0-23.4-64.59 57.278 57.278 0 0 1-17.48-32.91v-1.17a51.326 51.326 0 0 1 4.1-29.99l-39.86-25.82-1.39-0.95-1.24 0.95-39.94 25.75a51.326 51.326 0 0 1 4.1 29.99c-0.17 0.41-0.25 0.86-0.22 1.32A57.06 57.06 0 0 1 457.54 408a89.389 89.389 0 0 0-23.34 64.59c-0.25 17.26 3.83 34.3 11.85 49.59a52.15 52.15 0 0 1 4.6 41.26c-0.9 2.97-1.95 5.9-3.14 8.78-0.89 2.14-1.62 4.34-2.19 6.58a129.504 129.504 0 0 1-73.88 73.88 152.238 152.238 0 0 1-93.33 14.55c-1.9-0.33-3.78-0.77-5.64-1.32-3.03-0.95-5.97-2.17-8.78-3.66a43.883 43.883 0 0 1-18.21-15.22 53.96 53.96 0 0 0-2.12-3.07 319.63 319.63 0 0 1 1.61-250.01c42.86-133.12 124.49-226.96 182.57-209.77a56.324 56.324 0 0 1 30.21 23.48 50.978 50.978 0 0 1 5.63 46.08 112.791 112.791 0 0 0-5.7 47.84l22.67-60.85V165.3c0.81-16.88 14.73-30.15 31.64-30.15 16.9 0 30.82 13.27 31.64 30.15v75.34l22.16 60.71h0.51c0.46-3.52 0.65-7.06 0.59-10.61 0.07-12.65-2.03-25.22-6.22-37.15a50.974 50.974 0 0 1 5.63-46.08 56.238 56.238 0 0 1 30.28-23.4c57.86-17.19 139.7 76.65 182.49 209.7a319.369 319.369 0 0 1 1.53 250.01v0.06z"
              fill="#22d3ee" />
          </svg>
        </div>
        <div class="logo-text-wrap">
          <span class="logo-text">后台管理</span>
          <span class="logo-badge">ADMIN</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label">系统管理</div>
        <router-link v-for="item in adminMenuGroup1" :key="item.path" :to="item.path" class="nav-item"
          :class="{ active: isActive(item.path) }">
          <div class="nav-icon"><el-icon :size="18">
              <component :is="item.icon" />
            </el-icon></div>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>

        <div class="nav-divider"></div>
        <div class="nav-section-label">AI配置</div>
        <router-link v-for="item in adminMenuGroup2" :key="item.path" :to="item.path" class="nav-item"
          :class="{ active: isActive(item.path) }">
          <div class="nav-icon"><el-icon :size="18">
              <component :is="item.icon" />
            </el-icon></div>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>

        <div class="nav-divider"></div>
        <div class="nav-section-label">合规与配置</div>
        <router-link v-for="item in adminMenuGroup3" :key="item.path" :to="item.path" class="nav-item"
          :class="{ active: isActive(item.path) }">
          <div class="nav-icon"><el-icon :size="18">
              <component :is="item.icon" />
            </el-icon></div>
          <span class="nav-label">{{ item.label }}</span>
        </router-link>

        <div class="nav-divider"></div>
        <router-link to="/dashboard" class="nav-item">
          <div class="nav-icon"><el-icon :size="18">
              <Back />
            </el-icon></div>
          <span class="nav-label">返回业务端</span>
        </router-link>
      </nav>
    </aside>

    <div class="admin-content">
      <header class="admin-header">
        <div class="header-left">
          <h2 class="page-title">
            <span class="title-secondary">{{ currentTitleEn }}</span>
            <span class="title-sep">/</span>
            <span class="title-main">{{ currentTitle }}</span>
          </h2>
        </div>
        <div class="header-right">
          <el-switch v-model="isDark" :active-action-icon="Moon" :inactive-action-icon="Sunny"
            @change="handleThemeChange"
            style="--el-switch-on-color: var(--purple); --el-switch-off-color: var(--orange);" />
          <el-tag effect="dark" type="danger" size="small" round>管理员模式</el-tag>
        </div>
      </header>
      <main class="admin-main">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Back, Monitor, User, UserFilled, Cpu, Connection, Document, Setting, Moon, Sunny } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const titleEnMap: Record<string, string> = {
  '系统概览': 'Overview', '用户管理': 'Users', '患者管理': 'Patients',
  '权重文件管理': 'Model Weights', '大模型API管理': 'LLM API', '审计日志': 'Audit Logs', '系统设置': 'Settings',
}

const adminMenuGroup1 = [
  { path: '/admin/overview', label: '系统概览', icon: Monitor },
  { path: '/admin/users', label: '用户管理', icon: User },
  { path: '/admin/patients', label: '患者管理', icon: UserFilled },
]
const adminMenuGroup2 = [
  { path: '/admin/models', label: '权重文件管理', icon: Cpu },
  { path: '/admin/llm', label: '大模型API管理', icon: Connection },
]
const adminMenuGroup3 = [
  { path: '/admin/audit', label: '审计日志', icon: Document },
  { path: '/admin/settings', label: '系统设置', icon: Setting },
]

const currentTitle = computed(() => (route.meta.title as string) || '')
const currentTitleEn = computed(() => titleEnMap[currentTitle.value] || currentTitle.value)
const isDark = computed({ get: () => authStore.theme === 'dark', set: () => { } })

function isActive(path: string) { return route.path === path }
function handleThemeChange(val: boolean | string | number) { authStore.setTheme(val ? 'dark' : 'light') }
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

.admin-sidebar {
  width: 240px;
  background: var(--admin-sidebar-bg);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-right: 1px solid var(--admin-accent-light);
  position: relative;
  z-index: 10;
}

.admin-sidebar::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--admin-accent-light);
}

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid var(--admin-accent-light);
}

.logo-icon svg {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.logo-text-wrap {
  display: flex;
  flex-direction: column;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--sidebar-text-active);
}

.logo-badge {
  font-size: 10px;
  font-weight: 600;
  color: var(--admin-accent);
  letter-spacing: 2px;
  margin-top: 2px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
}

.nav-section-label {
  font-size: 11px;
  color: var(--text-muted);
  padding: 16px 14px 6px;
  letter-spacing: 2px;
  text-transform: uppercase;
  white-space: nowrap;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
  position: relative;
}

.nav-item:hover {
  background: var(--admin-accent-light);
  color: var(--sidebar-text-active);
}

.nav-item.active {
  background: var(--admin-accent-light);
  color: var(--sidebar-text-active);
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--admin-accent);
  border-radius: 0 3px 3px 0;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-label {
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.nav-divider {
  height: 1px;
  background: var(--admin-accent-light);
  margin: 8px 14px;
}

.admin-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.admin-header {
  height: 64px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
}

.title-secondary {
  font-size: 13px;
  font-weight: 400;
  color: var(--text-muted);
  letter-spacing: 1px;
}

.title-sep {
  color: var(--admin-accent);
  font-weight: 300;
}

.title-main {
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--bg-primary);
}
</style>
