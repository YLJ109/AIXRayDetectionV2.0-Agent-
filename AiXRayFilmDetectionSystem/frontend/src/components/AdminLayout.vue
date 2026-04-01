<template>
  <div class="admin-layout-container">
    <!-- 背景光效 -->
    <div class="bg-glow glow-1"></div>
    <div class="bg-glow glow-2"></div>

    <el-container class="admin-layout">
      <!-- 管理员侧边栏 -->
      <el-aside :width="isCollapse ? '80px' : '240px'" class="admin-sidebar">
        <div class="sidebar-header">
          <div class="logo-container">
            <div class="logo-icon admin-icon">
              <svg viewBox="0 0 1024 1024" fill="none">
                <path d="M420.27 298.84L256 725.33h69.29l40.02-109.91h183.38l40.02 109.91h69.89L494.35 298.84H420.27zM385.02 561.66l71.08-192.94h2.39l70.49 192.94H385.02z" fill="#10b981"/>
                <path d="M701.61 298.84V725.33h64.51V298.84z" fill="#10b981"/>
                <path d="M893.23 21.33c57.81 0 105.47 43.22 109.23 98.3l.21 6.96V256h-42.67V126.59c0-32.43-26.45-59.43-60.63-62.34l-6.14-.25H768v-42.67h125.23z" fill="#10b981"/>
                <path d="M1002.67 768v124.12c0 58.58-44.8 106.71-101.59 110.34l-6.87.21H768v-42.67h126.21c34.22 0 62.46-27.01 65.54-61.7l.25-6.18V768h42.67z" fill="#10b981"/>
                <path d="M64 768v127.57c0 32.85 31.57 61.27 73.13 64.17l7 .26H298.67v42.67H144.13c-64.51 0-118.49-43.52-122.54-100.23l-.26-6.82V768H64z" fill="#10b981"/>
                <path d="M298.67 21.33v42.67H143.02a79.36 79.36 0 0 0-78.76 73.56L64 143.79V256H21.33V143.79A122.11 122.11 0 0 1 135.85 21.55l7.17-.22H298.67z" fill="#10b981"/>
              </svg>
            </div>
            <transition name="fade">
              <div v-if="!isCollapse" class="logo-text">
                <h1 class="logo-title">管理后台</h1>
                <span class="logo-badge">ADMIN</span>
              </div>
            </transition>
          </div>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          class="admin-menu"
          router
        >
          <el-menu-item index="/admin/overview">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>系统概览</template>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/patients">
            <el-icon><UserFilled /></el-icon>
            <template #title>患者管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/model-management">
            <el-icon><Cpu /></el-icon>
            <template #title>模型管理</template>
          </el-menu-item>
          <el-menu-item index="/admin/llm-providers">
            <el-icon><Connection /></el-icon>
            <template #title>大模型API</template>
          </el-menu-item>

          <div class="menu-divider"></div>

          <el-menu-item index="/admin/audit-logs">
            <el-icon><Document /></el-icon>
            <template #title>审计日志</template>
          </el-menu-item>
          <el-menu-item index="/admin/settings">
            <el-icon><Setting /></el-icon>
            <template #title>系统设置</template>
          </el-menu-item>

          <div class="menu-divider"></div>

          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <template #title>返回业务端</template>
          </el-menu-item>
        </el-menu>

        <div class="sidebar-footer">
          <div class="collapse-btn" @click="isCollapse = !isCollapse">
            <el-icon :size="18">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </div>
        </div>
      </el-aside>

      <!-- 右侧主体 -->
      <el-container class="right-container">
        <!-- 顶部栏 -->
        <el-header class="admin-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/admin/overview' }">管理后台</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRoute?.meta?.title">
                {{ currentRoute.meta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-right">
            <el-tag type="danger" size="small" effect="dark" class="admin-badge">
              管理员
            </el-tag>

            <el-dropdown @command="handleCommand" trigger="click">
              <div class="user-info">
                <div class="user-avatar admin-avatar">
                  {{ userStore.userName?.charAt(0) || 'A' }}
                </div>
                <span class="user-name">{{ userStore.userName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="changePassword">
                    <el-icon><Lock /></el-icon>修改密码
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 主内容区 -->
        <el-main class="admin-main">
          <router-view v-slot="{ Component }">
            <transition name="slide-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="440px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitChangePassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { authApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isCollapse = ref(false)
const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)

const passwordForm = ref({ old_password: '', new_password: '' })
const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码不少于6位', trigger: 'blur' }
  ]
}

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

function handleCommand(command) {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
    })
  } else if (command === 'changePassword') {
    passwordForm.value = { old_password: '', new_password: '' }
    passwordDialogVisible.value = true
  }
}

async function submitChangePassword() {
  await passwordFormRef.value.validate()
  try {
    await authApi.changePassword(passwordForm.value)
    ElMessage.success('密码修改成功，请重新登录')
    passwordDialogVisible.value = false
    userStore.logout()
  } catch (e) {}
}

onMounted(() => {
  if (userStore.token && !userStore.user) {
    userStore.fetchUserInfo()
  }
})
</script>

<style scoped lang="scss">
.admin-layout-container {
  height: 100vh;
  overflow: hidden;
}

.admin-layout {
  height: 100%;
  background: var(--bg-primary);
}

// 管理员侧边栏（红橙色系）
.admin-sidebar {
  background: var(--card-bg);
  backdrop-filter: var(--glass-blur);
  border-right: 1px solid var(--glass-border);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  position: relative;
  z-index: 100;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 1px;
    height: 100%;
    background: linear-gradient(180deg, transparent, rgba(239, 68, 68, 0.3), transparent);
  }

  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid var(--glass-border);
  }

  .logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .admin-icon {
    background: linear-gradient(135deg, #EF4444, #F59E0B) !important;
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.3) !important;
  }

  .logo-text {
    display: flex;
    flex-direction: column;
  }

  .logo-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    white-space: nowrap;
  }

  .logo-badge {
    font-size: 10px;
    font-weight: 700;
    color: #EF4444;
    letter-spacing: 2px;
    background: rgba(239, 68, 68, 0.12);
    padding: 1px 6px;
    border-radius: 4px;
    margin-top: 2px;
    display: inline-block;
    width: fit-content;
  }
}

// 管理员菜单
.admin-menu {
  flex: 1;
  border-right: none;
  background: transparent;
  padding: 12px 8px;

  :deep(.el-menu-item) {
    height: 48px;
    line-height: 48px;
    border-radius: var(--radius-md);
    margin-bottom: 4px;
    color: var(--text-secondary);
    background: transparent;
    transition: all var(--transition-normal);
    display: flex;
    align-items: center;
    justify-content: flex-start;

    &:hover {
      background: var(--glass-bg);
      color: var(--text-primary);
    }

    &.is-active {
      background: rgba(239, 68, 68, 0.15);
      color: #EF4444;
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        background: #EF4444;
        border-radius: 0 4px 4px 0;
      }
    }

    .el-icon {
      font-size: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

.menu-divider {
  height: 1px;
  background: var(--glass-border);
  margin: 12px 16px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--glass-border);

  .collapse-btn {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-normal);
    margin: 0 auto;

    &:hover {
      background: var(--glass-bg-hover);
      border-color: var(--glass-border-hover);
    }
  }
}

// 管理员顶部栏
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--glass-border);
  padding: 0 24px;
  z-index: 10;
  height: 64px;

  .header-right {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .admin-badge {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(245, 158, 11, 0.2)) !important;
    border: 1px solid rgba(239, 68, 68, 0.3) !important;
    color: #F87171 !important;
    font-weight: 600;
    height: 22px;
    line-height: 20px;
    padding: 0 8px;
    font-size: 11px;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: var(--radius-md);
    transition: all var(--transition-normal);

    &:hover {
      background: var(--glass-bg);
    }
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    color: #10b981;
    flex-shrink: 0;
    background: transparent;
    border: 1.5px solid rgba(16, 185, 129, 0.4);
    transition: all var(--transition-normal);
  }

  .admin-avatar {
    background: rgba(16, 185, 129, 0.1) !important;
  }

  .user-info:hover .user-avatar {
    border-color: rgba(16, 185, 129, 0.7);
    background: rgba(16, 185, 129, 0.15) !important;
  }

  .user-name {
    color: var(--text-primary);
    font-size: 13px;
    font-weight: 500;
  }

  .el-icon {
    font-size: 12px;
    color: var(--text-secondary);
  }
}

.admin-main {
  background: var(--bg-primary);
  padding: 24px;
  overflow-y: auto;
}

// 过渡动画
.slide-fade-enter-active { transition: all 0.3s ease-out; }
.slide-fade-leave-active { transition: all 0.2s ease-in; }
.slide-fade-enter-from { transform: translateX(20px); opacity: 0; }
.slide-fade-leave-to { transform: translateX(-20px); opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
