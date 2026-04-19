/** 主布局 - 业务端 扁平科技风 */
<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: appStore.sidebarCollapsed }">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M914.28 950.86H109.72c-20.2 0-36.57 16.37-36.57 36.57S89.52 1024 109.72 1024h804.57c20.2 0 36.57-16.37 36.57-36.57s-16.38-36.57-36.58-36.57zM877.71 0H146.28C65.6 0.24 0.24 65.6 0 146.28v585.14c0.24 80.69 65.6 146.04 146.28 146.28h731.43c80.69-0.24 146.05-65.59 146.29-146.28V146.28C1023.76 65.6 958.4 0.24 877.71 0z m-97.13 643.88l-2.12 3.07a43.515 43.515 0 0 1-18.21 15.21c-2.8 1.5-5.74 2.73-8.78 3.66-1.82 0.54-3.68 0.98-5.56 1.32-31.84 5.23-64.51 0.16-93.25-14.48a129.312 129.312 0 0 1-74.02-73.88c-0.57-2.27-1.31-4.49-2.19-6.65-1.19-2.88-2.24-5.8-3.15-8.78a51.962 51.962 0 0 1 4.9-41.18c8.08-15.27 12.2-32.32 12-49.59a89.324 89.324 0 0 0-23.4-64.59 57.278 57.278 0 0 1-17.48-32.91v-1.17a51.326 51.326 0 0 1 4.1-29.99l-39.86-25.82-1.39-0.95-1.24 0.95-39.94 25.75a51.326 51.326 0 0 1 4.1 29.99c-0.17 0.41-0.25 0.86-0.22 1.32A57.06 57.06 0 0 1 457.54 408a89.389 89.389 0 0 0-23.34 64.59c-0.25 17.26 3.83 34.3 11.85 49.59a52.15 52.15 0 0 1 4.6 41.26c-0.9 2.97-1.95 5.9-3.14 8.78-0.89 2.14-1.62 4.34-2.19 6.58a129.504 129.504 0 0 1-73.88 73.88 152.238 152.238 0 0 1-93.33 14.55c-1.9-0.33-3.78-0.77-5.64-1.32-3.03-0.95-5.97-2.17-8.78-3.66a43.883 43.883 0 0 1-18.21-15.22 53.96 53.96 0 0 0-2.12-3.07 319.63 319.63 0 0 1 1.61-250.01c42.86-133.12 124.49-226.96 182.57-209.77a56.324 56.324 0 0 1 30.21 23.48 50.978 50.978 0 0 1 5.63 46.08 112.791 112.791 0 0 0-5.7 47.84l22.67-60.85V165.3c0.81-16.88 14.73-30.15 31.64-30.15 16.9 0 30.82 13.27 31.64 30.15v75.34l22.16 60.71h0.51c0.46-3.52 0.65-7.06 0.59-10.61 0.07-12.65-2.03-25.22-6.22-37.15a50.974 50.974 0 0 1 5.63-46.08 56.238 56.238 0 0 1 30.28-23.4c57.86-17.19 139.7 76.65 182.49 209.7a319.369 319.369 0 0 1 1.53 250.01v0.06z"
              fill="#22d3ee" />
          </svg>
        </div>
        <transition name="fade">
          <span v-if="!appStore.sidebarCollapsed" class="logo-text">胸影智诊<span class="logo-version">V3.0</span></span>
        </transition>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-label" v-if="!appStore.sidebarCollapsed">业务端</div>
        <router-link v-for="item in businessMenus" :key="item.path" :to="item.path" class="nav-item"
          :class="{ active: isActive(item.path) }">
          <div class="nav-icon"><el-icon :size="18">
              <component :is="item.icon" />
            </el-icon></div>
          <transition name="fade">
            <span v-if="!appStore.sidebarCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
        </router-link>

        <template v-if="authStore.isAdmin">
          <div class="nav-divider"></div>
          <div class="nav-section-label" v-if="!appStore.sidebarCollapsed">管理端</div>
          <router-link to="/admin/overview" class="nav-item" :class="{ active: isAdminActive }">
            <div class="nav-icon"><el-icon :size="18">
                <Setting />
              </el-icon></div>
            <transition name="fade">
              <span v-if="!appStore.sidebarCollapsed" class="nav-label">后台管理</span>
            </transition>
          </router-link>
        </template>
      </nav>

      <!-- 侧边栏底部 -->
      <div class="sidebar-footer">
        <div class="sidebar-line"></div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 顶部导航 -->
      <header class="top-header">
        <div class="header-left">
          <el-icon class="collapse-btn" :size="20" @click="appStore.toggleSidebar()">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <div class="header-breadcrumb">
            <span class="title-secondary">{{ currentTitleEn }}</span>
            <span class="title-sep">/</span>
            <span class="breadcrumb-main">{{ currentTitle }}</span>
          </div>
        </div>
        <div class="header-right">
          <el-switch v-model="isDark" :active-action-icon="Moon" :inactive-action-icon="Sunny"
            @change="handleThemeChange"
            style="--el-switch-on-color: var(--purple); --el-switch-off-color: var(--orange);" />
          <el-badge :value="pendingCount" :hidden="pendingCount === 0" :max="99">
            <el-icon :size="18" class="header-icon" @click="$router.push('/history')">
              <Bell />
            </el-icon>
          </el-badge>
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-info">
              <el-avatar :size="34" style="background: var(--gradient-primary);">
                {{ authStore.user?.real_name?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="user-name">{{ authStore.user?.real_name }}</span>
              <span class="user-role">{{ roleLabel }}</span>
              <el-icon class="user-arrow">
                <ArrowDown />
              </el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile"><el-icon>
                    <User />
                  </el-icon>个人信息</el-dropdown-item>
                <el-dropdown-item command="password"><el-icon>
                    <Lock />
                  </el-icon>修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout"><el-icon>
                    <SwitchButton />
                  </el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="420px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="原密码"><el-input v-model="passwordForm.old_password" type="password"
            show-password /></el-form-item>
        <el-form-item label="新密码"><el-input v-model="passwordForm.new_password" type="password"
            show-password /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Fold, Expand, ArrowDown, Setting, Bell, User, Lock, SwitchButton,
  DataBoard, FirstAidKit, Compass, ChatDotRound, Clock, Files, Stamp, Moon, Sunny,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { changePasswordApi, logoutApi } from '@/api/auth'
import { updatePreferencesApi } from '@/api/users'
import { getDashboardStatsApi } from '@/api/dashboard'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const appStore = useAppStore()

const pendingCount = ref(0)

const businessMenus = [
  { path: '/dashboard', label: '数据看板', icon: DataBoard },
  { path: '/diagnose', label: '诊断中心', icon: FirstAidKit },
  { path: '/batch', label: '批量诊断', icon: Files },
  { path: '/triage', label: '智能分诊', icon: Compass },
  { path: '/chat', label: 'AI咨询', icon: ChatDotRound },
  { path: '/history', label: '诊断历史', icon: Clock },
  { path: '/approval', label: '诊断审批', icon: Stamp },
]

const currentTitle = computed(() => (route.meta.title as string) || '')
const titleEnMap: Record<string, string> = {
  '数据看板': 'Dashboard', '诊断中心': 'Diagnose', '智能分诊': 'Smart Triage',
  'AI咨询': 'AI Chat', '诊断历史': 'Records', '批量诊断': 'Batch', '诊断审批': 'Approval',
}
const currentTitleEn = computed(() => titleEnMap[currentTitle.value] || currentTitle.value)
const isAdminActive = computed(() => route.path.startsWith('/admin'))

const roleMap: Record<string, string> = { admin: '管理员', doctor: '医生', nurse: '护士' }
const roleLabel = computed(() => roleMap[authStore.userRole] || '')

const isDark = computed({
  get: () => authStore.theme === 'dark',
  set: () => { },
})

function isActive(path: string) {
  return route.path === path
}

function handleThemeChange(val: boolean | string | number) {
  const theme = val ? 'dark' : 'light'
  authStore.setTheme(theme)
  if (authStore.user?.id) {
    updatePreferencesApi(authStore.user.id, { theme }).catch(() => { })
  }
}

const passwordDialogVisible = ref(false)
const passwordForm = ref({ old_password: '', new_password: '' })

function handleCommand(command: string) {
  if (command === 'logout') {
    logoutApi().catch(() => { })
    authStore.logout()
    router.push('/login')
  } else if (command === 'password') {
    passwordForm.value = { old_password: '', new_password: '' }
    passwordDialogVisible.value = true
  }
}

async function handleChangePassword() {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    ElMessage.warning('请填写完整')
    return
  }
  try {
    await changePasswordApi(passwordForm.value)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch { /* handled */ }
}

onMounted(async () => {
  try {
    const res: any = await getDashboardStatsApi()
    pendingCount.value = res.data?.pending_count || 0
  } catch { /* ok */ }
})
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* 侧边栏 */
.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  border-right: 1px solid var(--glass-border);
  position: relative;
  z-index: 10;
}

.sidebar::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.2), rgba(34, 211, 238, 0.05), rgba(34, 211, 238, 0.2));
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid var(--glass-border);
}

.logo-icon svg {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--sidebar-text-active);
  white-space: nowrap;
  letter-spacing: 1px;
}

.logo-version {
  font-size: 11px;
  font-weight: 400;
  color: var(--primary);
  margin-left: 4px;
  opacity: 0.8;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
  overflow-x: hidden;
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
  background: var(--sidebar-active-bg);
  color: var(--sidebar-text-active);
}

.nav-item.active {
  background: var(--sidebar-active-bg);
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
  background: var(--sidebar-active-border);
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
  background: var(--glass-border);
  margin: 8px 14px;
}

.sidebar-footer {
  padding: 0 10px;
}

.sidebar-line {
  height: 1px;
  background: var(--glass-border);
  margin: 0 4px;
}

/* 主内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.top-header {
  height: 64px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  z-index: 5;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
  padding: 4px;
  border-radius: var(--radius-sm);
}

.collapse-btn:hover {
  color: var(--primary);
  background: var(--glass-bg);
}

.breadcrumb-main {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-primary);
}

.header-breadcrumb .title-secondary {
  font-size: 13px;
  font-weight: 400;
  color: var(--text-muted);
  letter-spacing: 1px;
  margin-right: 2px;
}

.header-breadcrumb .title-sep {
  color: var(--primary);
  font-weight: 300;
  margin-right: 6px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.header-icon {
  cursor: pointer;
  color: var(--text-secondary);
  transition: color var(--transition-fast);
}

.header-icon:hover {
  color: var(--primary);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast);
}

.user-info:hover {
  background: var(--glass-bg);
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--primary-light);
  color: var(--primary);
}

.user-arrow {
  color: var(--text-muted);
  font-size: 12px;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: var(--bg-primary);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
