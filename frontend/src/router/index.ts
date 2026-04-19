/** Vue Router 路由配置 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/LoginPage.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardPage.vue'),
        meta: { title: '数据看板', icon: 'DataBoard' },
      },
      {
        path: 'diagnose',
        name: 'Diagnose',
        component: () => import('@/views/diagnose/DiagnosePage.vue'),
        meta: { title: '诊断中心', icon: 'FirstAidKit' },
      },
      {
        path: 'triage',
        name: 'Triage',
        component: () => import('@/views/triage/TriagePage.vue'),
        meta: { title: '智能分诊', icon: 'Triage' },
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('@/views/chat/ChatPage.vue'),
        meta: { title: 'AI咨询', icon: 'ChatDotRound' },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/history/HistoryPage.vue'),
        meta: { title: '诊断历史', icon: 'Clock' },
      },
      {
        path: 'approval',
        name: 'Approval',
        component: () => import('@/views/approval/ApprovalPage.vue'),
        meta: { title: '诊断审批', icon: 'Stamp' },
      },
      {
        path: 'batch',
        name: 'BatchDiagnose',
        component: () => import('@/views/batch/BatchPage.vue'),
        meta: { title: '批量诊断', icon: 'Files' },
      },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    redirect: '/admin/overview',
    meta: { role: 'admin' },
    children: [
      {
        path: 'overview',
        name: 'AdminOverview',
        component: () => import('@/views/admin/OverviewPage.vue'),
        meta: { title: '系统概览', icon: 'Monitor', role: 'admin' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersPage.vue'),
        meta: { title: '用户管理', icon: 'User', role: 'admin' },
      },
      {
        path: 'patients',
        name: 'AdminPatients',
        component: () => import('@/views/admin/PatientsPage.vue'),
        meta: { title: '患者管理', icon: 'UserFilled', role: 'admin' },
      },
      {
        path: 'models',
        name: 'AdminModels',
        component: () => import('@/views/admin/ModelsPage.vue'),
        meta: { title: '权重文件管理', icon: 'Cpu', role: 'admin' },
      },
      {
        path: 'llm',
        name: 'AdminLlm',
        component: () => import('@/views/admin/LlmPage.vue'),
        meta: { title: '大模型API管理', icon: 'Connection', role: 'admin' },
      },
      {
        path: 'audit',
        name: 'AdminAudit',
        component: () => import('@/views/admin/AuditPage.vue'),
        meta: { title: '审计日志', icon: 'Document', role: 'admin' },
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/SettingsPage.vue'),
        meta: { title: '系统设置', icon: 'Setting', role: 'admin' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const userStr = localStorage.getItem('user')
  let userRole = ''

  if (userStr) {
    try { userRole = JSON.parse(userStr).role } catch { /* ignore */ }
  }

  // 设置页面标题
  document.title = `${to.meta.title || '胸影智诊V3.0'} - 胸影智诊`

  // 公开页面不需要认证
  if (to.meta.public) {
    if (token) {
      next('/dashboard')
      return
    }
    next()
    return
  }

  // 未登录跳转登录页
  if (!token) {
    next('/login')
    return
  }

  // 管理员页面权限检查
  if (to.meta.role === 'admin' && userRole !== 'admin') {
    next('/dashboard')
    return
  }

  next()
})

export default router
