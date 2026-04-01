import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  // ===== 管理员路由 =====
  {
    path: '/admin',
    component: () => import('@/components/AdminLayout.vue'),
    redirect: '/admin/overview',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'overview',
        name: 'AdminOverview',
        component: () => import('@/views/admin/AdminOverview.vue'),
        meta: { title: '系统概览', icon: 'DataAnalysis' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'patients',
        name: 'AdminPatients',
        component: () => import('@/views/PatientManagement.vue'),
        meta: { title: '患者管理', icon: 'UserFilled' }
      },
      {
        path: 'audit-logs',
        name: 'AdminAuditLogs',
        component: () => import('@/views/admin/AdminAuditLogs.vue'),
        meta: { title: '审计日志', icon: 'Document' }
      },
      {
        path: 'model-management',
        name: 'AdminModelManagement',
        component: () => import('@/views/admin/AdminModelManagement.vue'),
        meta: { title: '模型管理', icon: 'Cpu' }
      },
      {
        path: 'llm-providers',
        name: 'AdminLLMProviders',
        component: () => import('@/views/admin/AdminLLMProviders.vue'),
        meta: { title: '大模型API', icon: 'Connection' }
      },
      {
        path: 'api-design',
        name: 'AdminApiDesign',
        component: () => import('@/views/admin/AdminApiDesign.vue'),
        meta: { title: 'API文档', icon: 'Document' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/AdminSettings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      }
    ]
  },
  // ===== 业务端路由 =====
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '数据看板', icon: 'DataAnalysis' }
      },
      {
        path: 'diagnosis',
        name: 'Diagnosis',
        component: () => import('@/views/Diagnosis.vue'),
        meta: { title: '诊断中心', icon: 'Microscope' }
      },
      {
        path: 'triage',
        name: 'Triage',
        component: () => import('@/views/Triage.vue'),
        meta: { title: '智能分诊', icon: 'DataAnalysis' }
      },
      {
        path: 'consultation',
        name: 'Consultation',
        component: () => import('@/views/Consultation.vue'),
        meta: { title: 'AI咨询', icon: 'ChatDotRound' }
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '诊断历史', icon: 'Document' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

function getUserFromStorage() {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    return {}
  }
}

function getRole() {
  const user = getUserFromStorage()
  return user.role || ''
}

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '胸影智诊V2.0'} - 胸影智诊V2.0`

  const token = localStorage.getItem('access_token')
  const role = getRole()

  // 无需认证的页面
  if (to.meta.requiresAuth === false) {
    if (token && to.name === 'Login') {
      // 已登录用户访问登录页，按角色分流
      next(role === 'admin' ? '/admin/overview' : '/dashboard')
      return
    }
    next()
    return
  }

  // 需要认证但无 token
  if (!token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 管理员权限检查
  if (to.matched.some(record => record.meta.requiresAdmin)) {
    if (role !== 'admin') {
      next({ name: 'Dashboard' })
      return
    }
    next()
    return
  }

  // 根路径重定向：按角色分流
  if (to.path === '/') {
    next(role === 'admin' ? '/admin/overview' : '/dashboard')
    return
  }

  next()
})

export default router
