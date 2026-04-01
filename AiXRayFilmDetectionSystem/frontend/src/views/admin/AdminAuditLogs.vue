<template>
  <div class="admin-audit-logs">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">审计日志</h2>
        <p class="page-desc">查看系统操作记录与用户行为追踪</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleRefresh" :icon="Refresh" :loading="loading">刷新</el-button>
        <el-button type="danger" plain @click="handleExport" :icon="Download">导出日志</el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="用户ID">
          <el-input v-model="filters.user_id" placeholder="输入用户ID" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select v-model="filters.action" placeholder="全部" clearable style="width: 160px">
            <el-option v-for="item in actionOptions" :key="item" :label="actionLabels[item] || item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 260px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search">查询</el-button>
          <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 日志表格 -->
    <div class="table-card">
      <el-table :data="logs" v-loading="loading" class="audit-table" row-key="id">
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column prop="user_id" label="操作人ID" width="100" align="center" />
        <el-table-column prop="user_name" label="操作人" width="120" align="center">
          <template #default="{ row }">
            {{ row.user_name || `用户${row.user_id}` }}
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="150" align="center">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)" size="small" effect="light">
              {{ actionLabels[row.action] || row.action }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="目标类型" width="100" align="center">
          <template #default="{ row }">
            {{ row.target_type || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="target_id" label="目标ID" width="90" align="center">
          <template #default="{ row }">
            {{ row.target_id || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="detail" label="操作详情" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.detail || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" align="center">
          <template #default="{ row }">
            {{ row.ip_address || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="170" align="center">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.per_page"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { systemApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Search, Refresh, RefreshLeft, Download } from '@element-plus/icons-vue'

const loading = ref(false)
const logs = ref([])

const filters = reactive({
  user_id: '',
  action: '',
  dateRange: null
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const actionOptions = [
  'login', 'logout', 'create_user', 'update_user', 'delete_user',
  'upload_diagnosis', 'review_diagnosis', 'generate_report',
  'create_patient', 'update_patient',
  'create_config', 'update_config', 'delete_config'
]

const actionLabels = {
  login: '登录',
  logout: '登出',
  create_user: '创建用户',
  update_user: '更新用户',
  delete_user: '删除用户',
  upload_diagnosis: '上传诊断',
  review_diagnosis: '审核诊断',
  generate_report: '生成报告',
  create_patient: '创建患者',
  update_patient: '更新患者',
  create_config: '创建配置',
  update_config: '更新配置',
  delete_config: '删除配置'
}

function getActionTagType(action) {
  const map = {
    login: 'success', logout: 'info',
    create_user: 'primary', update_user: 'warning', delete_user: 'danger',
    upload_diagnosis: 'primary', review_diagnosis: 'warning',
    generate_report: 'success',
    create_patient: 'primary', update_patient: 'warning',
    create_config: 'primary', update_config: 'warning', delete_config: 'danger'
  }
  return map[action] || 'info'
}

function formatTime(time) {
  if (!time) return '-'
  const d = new Date(time)
  return d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

async function fetchLogs() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    if (filters.user_id) params.user_id = filters.user_id
    if (filters.action) params.action = filters.action
    if (filters.dateRange?.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }
    const res = await systemApi.getAuditLogs(params)
    logs.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchLogs()
}

function handleReset() {
  filters.user_id = ''
  filters.action = ''
  filters.dateRange = null
  pagination.page = 1
  fetchLogs()
}

function handleRefresh() {
  fetchLogs()
}

function handleExport() {
  ElMessage.info('日志导出功能开发中')
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped lang="scss">
.admin-audit-logs {
  .page-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 20px;
  }

  .header-info {
    .page-title {
      font-size: 22px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .page-desc {
      color: var(--text-muted);
      font-size: 13px;
    }
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.filter-card {
  background: var(--card-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: 20px;

  .filter-form {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0;

    :deep(.el-form-item) {
      margin-bottom: 0;
      margin-right: 16px;
      display: flex;
      align-items: center;
    }

    :deep(.el-form-item__label) {
      display: flex;
      align-items: center;
      height: 32px;
      line-height: 32px;
    }

    :deep(.el-form-item__content) {
      display: flex;
      align-items: center;
      line-height: 32px;
    }

    // 统一所有输入类组件高度为 32px
    :deep(.el-input__wrapper) {
      height: 32px;
      padding: 0 12px;
    }

    :deep(.el-select .el-select__wrapper) {
      height: 32px;
      min-height: 32px;
    }

    :deep(.el-date-editor) {
      height: 32px;

      .el-input__wrapper {
        height: 32px;
        padding: 0 12px;
      }
    }

    :deep(.el-button) {
      height: 32px;
      padding: 0 16px;
    }
  }
}

.table-card {
  background: var(--card-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px;

  .audit-table {
    width: 100%;
    background: transparent;

    :deep(.el-table__inner-wrapper::before) {
      display: none;
    }

    :deep(.el-table__header th) {
      background: rgba(239, 68, 68, 0.08);
      color: var(--text-primary);
      font-weight: 600;
      font-size: 13px;
      border-bottom: 1px solid rgba(239, 68, 68, 0.15);
    }

    :deep(.el-table__body tr) {
      background: rgba(255, 255, 255, 0.03);

      td {
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        color: var(--text-primary);
      }

      &:hover > td {
        background: rgba(239, 68, 68, 0.06) !important;
      }
    }

    :deep(.el-table__empty-block) {
      background: transparent;
    }
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;

  :deep(.el-pagination) {
    .el-pager li {
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);

      &.is-active {
        background: linear-gradient(135deg, #EF4444, #F59E0B);
        border-color: transparent;
        color: white;
      }
    }

    .btn-prev, .btn-next {
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);
    }
  }
}
</style>
