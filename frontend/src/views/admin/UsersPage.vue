/** 管理员-用户管理页面 */
<template>
  <div class="users-page">
    <div class="glass-card">
      <!-- 搜索筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="用户名/姓名/科室" clearable
            @keyup.enter="search" class="filter-input">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.role" placeholder="角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="医生" value="doctor" />
            <el-option label="护士" value="nurse" />
          </el-select>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.status" placeholder="状态" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </div>
        <div class="filter-actions">
          <el-button type="primary" @click="search">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </div>
        <div class="filter-actions" style="margin-left: auto;">
          <el-button type="primary" @click="openDialog('create')">
            <el-icon><Plus /></el-icon> 新增用户
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" empty-text="暂无用户数据" class="glass-table">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="real_name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <span class="role-badge" :class="row.role">
              {{ roleMap[row.role] || row.role }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="department" label="科室" width="120" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="email" label="邮箱" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <span class="status-dot" :class="row.status === 'active' ? 'active' : 'inactive'"></span>
            <span class="status-text">{{ row.status === 'active' ? '启用' : '禁用' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="last_login_at" label="最后登录" width="170" />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" class="action-link" @click="openDialog('edit', row)">编辑</el-button>
            <el-button type="warning" link size="small" class="action-link" @click="openResetPassword(row)">重置密码</el-button>
            <el-popconfirm title="确定删除此用户？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small" class="action-link" :disabled="row.id === currentUserId">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.per_page"
          :total="pagination.total" :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper" @size-change="fetchData" @current-change="fetchData" />
      </div>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增用户' : '编辑用户'" width="500px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px" size="default">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="dialogMode === 'create'">
          <el-input v-model="formData.password" type="password" show-password placeholder="不少于6位" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="formData.real_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="formData.role" style="width:100%">
            <el-option label="管理员" value="admin" />
            <el-option label="医生" value="doctor" />
            <el-option label="护士" value="nurse" />
          </el-select>
        </el-form-item>
        <el-form-item label="科室">
          <el-input v-model="formData.department" placeholder="所属科室" />
        </el-form-item>
        <el-form-item label="执业证号" v-if="formData.role === 'doctor'">
          <el-input v-model="formData.license_number" placeholder="执业证号" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="formData.phone" placeholder="联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="formData.email" placeholder="电子邮箱" />
        </el-form-item>
        <el-form-item label="状态" v-if="dialogMode === 'edit'">
          <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog v-model="resetPwdVisible" title="重置密码" width="420px">
      <el-form label-width="90px" size="default">
        <el-form-item label="用户">
          <el-input :model-value="resetUser?.real_name + ' (' + resetUser?.username + ')'" disabled />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="newPassword" type="password" show-password placeholder="请输入新密码(>=6位)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPwdVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">确定重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getUsersApi, updateUserApi, deleteUserApi, resetPasswordApi } from '@/api/users'
import { registerApi } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

const roleMap: Record<string, string> = { admin: '管理员', doctor: '医生', nurse: '护士' }

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const resetPwdVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editId = ref<number | null>(null)
const formRef = ref<any>(null)
const resetUser = ref<any>(null)
const newPassword = ref('')

const filters = reactive({ keyword: '', role: '', status: '' })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const formData = reactive({
  username: '', password: '', real_name: '', role: 'doctor',
  department: '', license_number: '', phone: '', email: '', is_active: true
})

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码不少于6位', trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

function defaultForm() {
  return { username: '', password: '', real_name: '', role: 'doctor', department: '', license_number: '', phone: '', email: '', is_active: true }
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: pagination.page, per_page: pagination.per_page }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.role) params.role = filters.role
    if (filters.status) params.status = filters.status
    const res: any = await getUsersApi(params)
    tableData.value = res.data.items
    pagination.total = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

function search() { pagination.page = 1; fetchData() }
function resetFilters() { filters.keyword = ''; filters.role = ''; filters.status = ''; search() }

function openDialog(mode: 'create' | 'edit', row?: any) {
  dialogMode.value = mode
  editId.value = row?.id || null
  if (mode === 'edit' && row) {
    Object.assign(formData, {
      username: row.username,
      password: '',
      real_name: row.real_name,
      role: row.role,
      department: row.department || '',
      license_number: row.license_number || '',
      phone: row.phone || '',
      email: row.email || '',
      is_active: row.status === 'active'
    })
  } else {
    Object.assign(formData, defaultForm())
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch { return }
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await registerApi(formData)
      ElMessage.success('用户创建成功')
    } else {
      const updateData: any = {
        real_name: formData.real_name,
        role: formData.role,
        department: formData.department,
        license_number: formData.license_number,
        phone: formData.phone,
        email: formData.email,
        status: formData.is_active ? 'active' : 'disabled'
      }
      await updateUserApi(editId.value!, updateData)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled */ } finally { submitting.value = false }
}

async function handleDelete(row: any) {
  try {
    await deleteUserApi(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* handled */ }
}

function openResetPassword(row: any) {
  resetUser.value = row
  newPassword.value = ''
  resetPwdVisible.value = true
}

async function handleResetPassword() {
  if (!newPassword.value || newPassword.value.length < 6) {
    ElMessage.warning('密码不少于6位')
    return
  }
  try {
    await resetPasswordApi(resetUser.value.id, { new_password: newPassword.value })
    ElMessage.success('密码重置成功')
    resetPwdVisible.value = false
  } catch { /* handled */ }
}

onMounted(() => fetchData())
</script>

<style scoped lang="scss">
.users-page {
  // 筛选栏
  .filter-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;

    .filter-item {
      display: flex;
      align-items: center;

      .filter-input {
        width: 220px;
      }

      :deep(.el-input__wrapper) {
        height: 36px !important;
        padding: 0 12px !important;
      }

      :deep(.el-select .el-select__wrapper) {
        height: 36px !important;
        min-height: 36px !important;
      }
    }

    .filter-actions {
      display: flex;
      gap: 8px;

      :deep(.el-button) {
        height: 36px !important;
        padding: 0 16px !important;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
  }

  // 角色徽标
  .role-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    min-width: 60px;

    &.admin { background: rgba(239, 68, 68, 0.15); color: #F87171; }
    &.doctor { background: rgba(34, 211, 238, 0.2); color: var(--primary); }
    &.nurse { background: rgba(59, 130, 246, 0.15); color: var(--blue); }
  }

  // 状态指示
  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;

    &.active {
      background: var(--primary);
      box-shadow: 0 0 8px rgba(34, 211, 238, 0.6);
    }

    &.inactive {
      background: var(--text-muted);
    }
  }

  .status-text {
    font-size: 13px;
    color: var(--text-secondary);
    vertical-align: middle;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

  // 表格单元格垂直居中
  :deep(.el-table__cell) {
    display: table-cell !important;
    vertical-align: middle !important;
  }

  // 表格内容居中
  :deep(.el-table__row) {
    td {
      .cell {
        display: flex;
        align-items: center;
        justify-content: flex-start;
      }
    }
  }

  // 表格居中的列
  :deep(.el-table__body tr td) {
    .cell {
      &:has(.role-badge),
      &:has(.status-dot) {
        justify-content: center;
      }
    }
  }
}
</style>

<style lang="scss">
.action-link {
  background: transparent !important;
  padding: 2px 6px !important;
  &:hover {
    background: transparent !important;
    opacity: 0.8;
  }
}
</style>
