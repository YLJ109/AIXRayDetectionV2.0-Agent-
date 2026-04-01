import { defineStore } from 'pinia'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 导出诊断状态 store
export { useDiagnosisStore } from './diagnosis'

// 导出咨询状态 store
export { useConsultationStore } from './consultation'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
    isDoctor: (state) => state.user?.role === 'doctor',
    isNurse: (state) => state.user?.role === 'nurse',
    userName: (state) => state.user?.real_name || '',
    userRole: (state) => state.user?.role || '',
    userAvatar: (state) => state.user?.avatar || '',
    roleLabel: (state) => {
      const map = { admin: '管理员', doctor: '医生', nurse: '护士' }
      return map[state.user?.role] || state.user?.role || '未知'
    },
    homeRoute: (state) => {
      return state.user?.role === 'admin' ? '/admin/overview' : '/dashboard'
    }
  },

  actions: {
    async login(credentials) {
      const res = await authApi.login(credentials)
      this.token = res.data.access_token
      this.user = res.data.user
      localStorage.setItem('access_token', res.data.access_token)
      if (res.data.refresh_token) {
        localStorage.setItem('refresh_token', res.data.refresh_token)
      }
      localStorage.setItem('user', JSON.stringify(res.data.user))
      ElMessage.success('登录成功')
      // 根据角色返回首页路由
      return this.homeRoute
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      router.push('/login')
    },

    async fetchUserInfo() {
      try {
        const res = await authApi.getUserInfo()
        this.user = res.data
        localStorage.setItem('user', JSON.stringify(res.data))
      } catch (e) {
        this.logout()
      }
    }
  }
})
