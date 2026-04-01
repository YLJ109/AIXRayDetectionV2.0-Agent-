<template>
  <div class="layout-container">
    <!-- 背景光效 -->
    <div class="bg-glow glow-1"></div>
    <div class="bg-glow glow-2"></div>

    <el-container class="main-layout">
      <!-- 玻璃拟态侧边栏 -->
      <el-aside :width="isCollapse ? '80px' : '240px'" class="glass-sidebar">
        <div class="sidebar-header">
          <div class="logo-container">
            <div class="logo-icon">
              <svg viewBox="0 0 1287 1024" fill="none">
                <path
                  d="M594.446629 412.8768c30.837029-9.654857 63.429486-12.024686 95.378285-1.930971 6.9632 2.194286 13.780114 4.973714 20.2752 8.338285l6.407315 3.510857 170.569142 99.240229a36.571429 36.571429 0 0 1-33.206857 65.038629l-3.540114-1.813943-170.8032-99.357257a56.407771 56.407771 0 0 0-11.761371-5.207772c-13.750857-4.388571-29.666743-3.803429-45.524115 0.292572l-5.968457 1.696914c-5.061486 1.579886-8.835657 3.101257-9.596343 3.335314h-0.117028l-169.515886 99.035429a36.571429 36.571429 0 0 1-40.228571-60.942629l3.335314-2.194286 171.446857-100.059428c4.973714-2.545371 12.756114-5.851429 22.820571-8.981943z"
                  fill="#10b981" />
                <path
                  d="M708.900571 22.410971a36.571429 36.571429 0 0 1 34.962286 38.0928l-6.378057 158.281143a2386.885486 2386.885486 0 0 0-1.404343 47.279543v1.8432c0 32.446171 15.652571 57.899886 81.1008 90.229029l7.489829 3.627885 122.88 67.876572a36.571429 36.571429 0 0 1-31.773257 65.770057l-3.598629-1.755429-120.861257-66.823314c-92.072229-43.651657-126.244571-93.535086-128.292572-153.131886l-0.117028-5.792914c0-6.875429 0.438857-22.1184 1.2288-44.529371l4.5056-115.273143 2.135771-50.731886A36.571429 36.571429 0 0 1 708.900571 22.410971z"
                  fill="#10b981" />
                <path
                  d="M578.413714 22.410971a36.571429 36.571429 0 0 1 37.741715 31.217372l0.4096 4.798171 5.880685 145.086172a2520.502857 2520.502857 0 0 1 1.930972 64.394971c0 60.123429-31.246629 110.504229-117.5552 153.6l-8.835657 4.271543-122.850743 67.876571a36.571429 36.571429 0 0 1-38.765715-61.878857l3.393829-2.135771 124.869486-68.900572c67.262171-31.890286 85.313829-57.344 86.542628-89.234285v-7.753143c-0.087771-5.851429-0.351086-15.213714-0.760685-27.501714l-3.072-81.627429-3.8912-94.120229A36.571429 36.571429 0 0 1 578.413714 22.410971z"
                  fill="#10b981" />
                <path
                  d="M306.7904 159.071086c73.874286-51.287771 144.618057-46.460343 202.430171-1.170286a36.571429 36.571429 0 0 1-45.114514 57.578057c-32.007314-25.102629-66.121143-28.379429-109.714286-0.292571l-5.705142 3.861943a194.062629 194.062629 0 0 0-9.362286 7.255771c-8.279771 6.729143-17.6128 15.008914-27.765029 24.751543a639.707429 639.707429 0 0 0-86.250057 103.6288C133.266286 491.52 84.611657 663.669029 102.517029 876.251429l1.462857 16.032914c0.117029 2.633143 1.609143 9.303771 5.149257 15.418514 5.500343 9.450057 14.218971 14.628571 32.446171 14.043429l1.784686-0.087772 327.211886-87.332571c6.582857-1.901714 18.373486-7.7824 30.895543-18.724572l4.183771-3.861942c20.158171-19.309714 33.704229-45.904457 37.653943-80.574172l0.731428-8.133486V473.380571a36.571429 36.571429 0 0 1 72.938058-3.744914l0.2048 3.744914-0.087772 252.021029c-3.8912 59.684571-26.155886 105.969371-60.854857 139.176229-21.650286 20.714057-43.534629 32.738743-61.293714 38.736457l-4.739657 1.462857L155.326171 994.157714l-3.364571 0.263315c-49.737143 3.832686-86.074514-15.623314-106.027886-49.912686-10.532571-18.080914-14.453029-35.605943-14.891885-47.045486-23.3472-235.461486 30.047086-429.699657 133.588114-583.592228A712.528457 712.528457 0 0 1 260.827429 198.363429c20.0704-19.338971 36.0448-32.3584 45.962971-39.3216z"
                  fill="#10b981" />
                <path
                  d="M778.064457 157.9008c57.841371-45.290057 128.585143-50.117486 202.576457 1.287314l6.612115 4.856686c9.713371 7.460571 23.1424 18.870857 39.204571 34.347886a712.528457 712.528457 0 0 1 96.197486 115.477943c103.570286 153.892571 156.964571 348.16 133.7344 581.573485a107.871086 107.871086 0 0 1-15.008915 49.064229c-19.017143 32.650971-52.867657 51.872914-99.035428 50.322286l-7.021714-0.4096-3.364572-0.263315-335.637943-89.614628c-17.759086-5.149257-41.662171-17.408-65.243428-39.994515-32.797257-31.363657-54.447543-74.400914-60.123429-131.364571l-0.8192-10.181486V473.380571a36.571429 36.571429 0 0 1 72.938057-3.744914l0.2048 3.744914-0.087771 247.222858c2.691657 41.106286 16.735086 70.363429 38.443886 91.106742 12.639086 12.112457 25.014857 19.017143 32.1536 21.650286l2.165028 0.731429 327.943314 87.566628 1.813943 0.087772c16.735086 0.526629 25.453714-3.774171 31.012572-11.790629l1.462857-2.2528c2.837943-4.885943 4.330057-10.122971 4.973714-14.423771l0.292572-3.013486c21.650286-217.965714-27.121371-395.351771-121.475658-535.581257a639.707429 639.707429 0 0 0-86.250057-103.6288c-8.104229-7.811657-15.711086-14.628571-22.674285-20.538514l-10.0352-8.162743a119.778743 119.778743 0 0 0-4.242286-3.218286c-46.518857-32.270629-82.183314-29.842286-115.624229-3.657143a36.571429 36.571429 0 0 1-45.056-57.578057z"
                  fill="#10b981" />
              </svg>
            </div>
            <transition name="fade">
              <h1 v-if="!isCollapse" class="logo-title">胸影智诊V2.0</h1>
            </transition>
          </div>
        </div>

        <el-menu :default-active="activeMenu" :collapse="isCollapse" :collapse-transition="false" class="glass-menu"
          router>
          <el-menu-item index="/dashboard">
            <el-icon>
              <DataAnalysis />
            </el-icon>
            <template #title>数据看板</template>
          </el-menu-item>
          <el-menu-item index="/diagnosis">
            <el-icon>
              <SetUp />
            </el-icon>
            <template #title>诊断中心</template>
          </el-menu-item>
          <el-menu-item index="/triage">
            <el-icon>
              <Guide />
            </el-icon>
            <template #title>智能分诊</template>
          </el-menu-item>
          <el-menu-item index="/consultation">
            <el-icon>
              <ChatDotRound />
            </el-icon>
            <template #title>AI咨询</template>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon>
              <Document />
            </el-icon>
            <template #title>诊断历史</template>
          </el-menu-item>
          <el-menu-item index="/admin/overview" v-if="userStore.isAdmin">
            <el-icon>
              <Monitor />
            </el-icon>
            <template #title>管理后台</template>
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
        <!-- 玻璃拟态顶部栏 -->
        <el-header class="glass-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRoute?.meta?.title">
                {{ currentRoute.meta.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-right">
            <el-dropdown @command="handleCommand" trigger="click">
              <div class="user-section">
                <div class="user-avatar">
                  {{ userStore.userName?.charAt(0) || 'U' }}
                </div>
                <div class="user-info-inline">
                  <span class="user-name">{{ userStore.userName }}</span>
                  <span class="user-role">{{ roleLabel }}</span>
                </div>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
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
        <el-main class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="slide-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="440px" class="glass-dialog">
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
const roleLabel = computed(() => {
  const roleMap = { admin: '管理员', doctor: '医生', nurse: '护士' }
  return roleMap[userStore.user?.role] || '用户'
})

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
  } catch (e) { }
}

onMounted(() => {
  if (userStore.token && !userStore.user) {
    userStore.fetchUserInfo()
  }
})
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  overflow: hidden;
}

.main-layout {
  height: 100%;
  background: var(--bg-primary);
}

// 玻璃拟态侧边栏
.glass-sidebar {
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
    background: linear-gradient(180deg, transparent, rgba(16, 185, 129, 0.3), transparent);
  }

  .sidebar-header {
    padding: 20px;
    border-bottom: 1px solid var(--glass-border);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .logo-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
  }

  .logo-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    svg {
      width: 32px;
      height: 32px;
    }
  }

  .logo-title {
    font-size: 16px;
    font-weight: 700;
    color: #10b981;
    white-space: nowrap;
  }
}

// 玻璃菜单
.glass-menu {
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
      background: var(--primary-light);
      color: var(--primary);
      position: relative;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 24px;
        background: var(--primary);
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

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: center;

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

    &:hover {
      background: var(--glass-bg-hover);
      border-color: var(--glass-border-hover);
    }

    .el-icon {
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
}

// 玻璃拟态顶部栏
.glass-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--glass-border);
  padding: 0 24px;
  z-index: 10;
  height: 64px;

  .header-left {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex: 1;
  }

  .header-right {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    flex: 1;
  }

  .user-section {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    padding: 6px 12px;
    border-radius: var(--radius-lg);
    transition: all var(--transition-normal);

    &:hover {
      background: var(--glass-bg);
    }
  }

  .user-info-inline {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .user-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .user-role {
      font-size: 12px;
      color: var(--text-muted);
    }
  }

  .dropdown-icon {
    color: var(--text-secondary);
    font-size: 12px;
    transition: transform 0.3s ease;
  }

  .user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
    border: 1px solid rgba(16, 185, 129, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    color: var(--primary);
    flex-shrink: 0;
  }
}

// 主内容区
.main-content {
  background: var(--bg-primary);
  padding: 24px;
  overflow-y: auto;
}

// 过渡动画
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
