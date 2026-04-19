/** 管理员 - 审计日志页面 */
<template>
  <div class="audit-page">
    <div class="glass-card">
      <!-- 搜索筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="搜索操作人" clearable @keyup.enter="search" class="filter-input">
            <template #prefix><el-icon>
                <Search />
              </el-icon></template>
          </el-input>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.action" placeholder="操作类型" clearable>
            <el-option v-for="a in actionTypes" :key="a.value" :label="a.label" :value="a.value" />
          </el-select>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.resource_type" placeholder="资源类型" clearable>
            <el-option label="全部" value="" />
            <el-option v-for="opt in resourceTypeOptions" :key="opt[1]" :label="opt[0]" :value="opt[1]" />
          </el-select>
        </div>
        <div class="filter-item">
          <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
            end-placeholder="结束日期" value-format="YYYY-MM-DD" :shortcuts="dateShortcuts" style="width: 240px;" />
        </div>
        <div class="filter-actions">
          <el-button type="primary" @click="search"><el-icon>
              <Search />
            </el-icon> 搜索</el-button>
          <el-button @click="resetFilters"><el-icon>
              <Refresh />
            </el-icon> 重置</el-button>
        </div>
      </div>

      <!-- 统计条 -->
      <div class="stats-bar" v-if="pagination.total > 0">
        <span class="stat-item">共 <b>{{ pagination.total }}</b> 条记录</span>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" empty-text="暂无审计日志" class="audit-table"
        row-class-name="audit-row">
        <!-- 序号 -->
        <el-table-column type="index" label="#" width="50" align="center" :index="getRowIndex" />

        <!-- 操作人 -->
        <el-table-column prop="username" label="操作人" width="110" align="center">
          <template #default="{ row }">
            <span class="user-name">{{ row.username || '系统' }}</span>
          </template>
        </el-table-column>

        <!-- 操作类型 -->
        <el-table-column label="操作类型" width="150" align="center">
          <template #default="{ row }">
            <span class="action-tag" :class="getActionClass(row.action)">
              {{ getActionLabel(row.action) }}
            </span>
          </template>
        </el-table-column>

        <!-- 资源类型 -->
        <el-table-column label="资源类型" width="100" align="center">
          <template #default="{ row }">
            <span class="resource-tag" v-if="row.resource_type">{{ getResourceLabel(row.resource_type) }}</span>
            <span v-else class="text-dim">-</span>
          </template>
        </el-table-column>

        <!-- IP 地址 -->
        <el-table-column prop="ip_address" label="IP 地址" width="140" align="center">
          <template #default="{ row }">
            <span class="ip-text">{{ row.ip_address || '-' }}</span>
          </template>
        </el-table-column>

        <!-- 详情 -->
        <el-table-column label="详情" min-width="220">
          <template #default="{ row }">
            <div class="detail-cell" v-if="row.details">
              <template v-if="typeof row.details === 'object' && !Array.isArray(row.details)">
                <span v-for="(val, key) in row.details" :key="key" class="detail-kv">
                  <em>{{ key }}:</em>
                  <span>{{ typeof val === 'object' ? JSON.stringify(val) : val }}</span>
                </span>
              </template>
              <template v-else>
                <span class="detail-text">{{ formatDetails(row.details) }}</span>
              </template>
            </div>
            <span v-else class="text-dim">-</span>
          </template>
        </el-table-column>

        <!-- 时间 -->
        <el-table-column prop="created_at" label="时间" width="165" align="center" sortable>
          <template #default="{ row }">
            <span class="time-text">{{ formatTime(row.created_at) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.per_page"
          :total="pagination.total" :page-sizes="[20, 50, 100]" layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData" @current-change="fetchData" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { Search, Refresh } from '@element-plus/icons-vue'
import { getAuditLogsApi, getAuditActionTypesApi } from '@/api/audit'

const loading = ref(false)
const tableData = ref<any[]>([])
const actionTypes = ref<{ value: string; label: string }[]>([])

const filters = reactive({ keyword: '', action: '', resource_type: '', dateRange: null as [string, string] | null })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const dateShortcuts = [
  { text: '最近一周', value: () => { const e = new Date(); const s = new Date(); s.setDate(s.getDate() - 7); return [s, e] } },
  { text: '最近一月', value: () => { const e = new Date(); const s = new Date(); s.setMonth(s.getMonth() - 1); return [s, e] } },
  { text: '最近三月', value: () => { const e = new Date(); const s = new Date(); s.setMonth(s.getMonth() - 3); return [s, e] } },
]

// ====== 中文映射 ======

/** 资源类型中文 */
const resourceTypeOptions: [string, string][] = [
  ['诊断', 'diagnosis'], ['患者', 'patient'], ['报告', 'report'],
  ['用户', 'user'], ['模型', 'model_weight'], ['LLM配置', 'llm_config'],
  ['设置', 'setting'], ['审批', 'approval'], ['批量', 'batch'],
]
const resourceLabelMap: Record<string, string> = Object.fromEntries(resourceTypeOptions)
function getResourceLabel(val: string): string { return resourceLabelMap[val] || val }

/** 操作类型中文映射（覆盖所有后端 action 值） */
const actionLabelMap: Record<string, string> = {
  // 认证
  LOGIN: '登录', LOGOUT: '登出', LOGIN_FAILED: '登录失败',
  // 用户管理
  CREATE_USER: '创建用户', UPDATE_USER: '修改用户', DELETE_USER: '删除用户',
  CHANGE_PASSWORD: '修改密码', RESET_PASSWORD: '重置密码',
  // 患者
  CREATE_PATIENT: '新增患者', UPDATE_PATIENT: '修改患者', DELETE_PATIENT: '删除患者',
  // 诊断
  CREATE_DIAGNOSIS: '新建诊断', EDIT_REPORT: '编辑报告',
  APPROVE_DIAGNOSIS: '通过诊断', REJECT_DIAGNOSIS: '驳回诊断',
  REQUEST_REVISION: '要求复诊',
  // 报告
  APPROVE_REPORT: '通过报告', REJECT_REPORT: '驳回报告',
  // 审批
  CREATE_APPROVAL: '提交审批', DELETE_APPROVAL: '撤销审批',
  SYNC_MISSING_APPROVALS: '同步审批数据',
  // 批量
  BATCH_DIAGNOSE: '批量诊断', BATCH_GENERATE_REPORTS: '批量生成报告',
  BATCH_UPLOAD: '批量上传', BATCH_CANCEL: '取消批量检测',
  // 模型
  UPLOAD_MODEL: '上传模型', ACTIVATE_MODEL: '激活模型', DELETE_MODEL: '删除模型',
  UPDATE_MODEL_PARAMS: '更新模型参数',
  // LLM配置
  CREATE_LLM_CONFIG: '添加LLM配置', UPDATE_LLM_CONFIG: '修改LLM配置', DELETE_LLM_CONFIG: '删除LLM配置',
  // 设置
  UPDATE_SETTING: '修改设置', BATCH_UPDATE_SETTINGS: '批量修改设置',
}
function getActionLabel(action: string): string {
  if (!action || typeof action !== 'string') return String(action || '-')
  return actionLabelMap[action] || action
}

/** 操作类型颜色分类 */
function getActionClass(action: string): string {
  if (!action) return ''
  const a = action.toUpperCase()
  if (a.includes('DELETE') || a.includes('REMOVE') || a.includes('REJECT')) return 'danger'
  if (a.includes('CREATE') || a.includes('UPLOAD') || a.includes('REGISTER') || a.includes('APPROVE') || a.includes('ACTIVATE'))
    return 'success'
  if (a.includes('UPDATE') || a.includes('EDIT') || a.includes('BATCH') || a.includes('CHANGE') || a.includes('REQUEST'))
    return 'warning'
  if (a.includes('LOGIN') || a.includes('LOGOUT')) return 'info'
  return ''
}

/** 详情格式化 */
function formatDetails(details: any): string {
  if (!details) return '-'
  if (typeof details === 'string') {
    try { const obj = JSON.parse(details); return JSON.stringify(obj, null, 2) }
    catch { return details }
  }
  try { return JSON.stringify(details, null, 2) }
  catch { return String(details) }
}

/** 时间格式化 */
function formatTime(time: string): string {
  if (!time) return '-'
  return time.replace('T', ' ').substring(0, 19)
}

/** 行号（考虑分页） */
function getRowIndex(index: number): number {
  return (pagination.page - 1) * pagination.per_page + index + 1
}

// ====== 数据获取 ======
async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: pagination.page, per_page: pagination.per_page }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.action) params.action = filters.action
    if (filters.resource_type) params.resource_type = filters.resource_type
    if (filters.dateRange?.[0] && filters.dateRange?.[1]) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }
    const res: any = await getAuditLogsApi(params)
    // 过滤不完整数据：必须有操作人和操作时间
    tableData.value = (res.data.items || []).filter((item: any) => item.action && item.created_at)
    pagination.total = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

function search() { pagination.page = 1; fetchData() }

function resetFilters() {
  filters.keyword = ''
  filters.action = ''
  filters.resource_type = ''
  filters.dateRange = null
  search()
}

onMounted(() => {
  fetchData()
  getAuditActionTypesApi().then((res: any) => {
    const raw = res.data
    // 兼容多种返回格式：数组 或 对象包裹的数组
    let rawActions: any[] = []
    if (Array.isArray(raw)) {
      rawActions = raw
    } else if (raw && typeof raw === 'object' && Array.isArray(raw.items)) {
      rawActions = raw.items
    } else if (raw && typeof raw === 'object' && Array.isArray(raw.data)) {
      rawActions = raw.data
    }
    // 过滤：只保留有效字符串，转中文标签
    actionTypes.value = rawActions
      .filter((a: any) => a !== null && a !== undefined && a !== '' && typeof a === 'string')
      .map((a: string) => ({
        value: a,
        label: getActionLabel(a) || a,
      }))
  }).catch(() => { })
})
</script>

<style scoped lang="scss">
.audit-page {

  .filter-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;

    .filter-item {
      display: flex;
      align-items: center;

      .filter-input {
        width: 200px;
      }

      :deep(.el-input__wrapper) {
        height: 36px !important;
        padding: 0 12px !important;
      }

      :deep(.el-select .el-select__wrapper) {
        height: 36px !important;
        min-height: 36px !important;
      }

      :deep(.date-editor) {
        height: 36px;
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

  .stats-bar {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    padding: 6px 14px;
    background: var(--glass-bg);
    border-radius: var(--radius-md);
    font-size: 13px;
    color: var(--text-secondary);

    b {
      color: var(--primary);
      font-weight: 600;
    }
  }

  // ===== 表格 =====
  .audit-table {
    --td-padding-y: 10px;

    :deep(th .cell) {
      font-weight: 600;
      font-size: 13px;
      color: var(--text-primary);
      background: var(--bg-tertiary);
    }

    :deep(td .cell) {
      font-size: 13px;
      vertical-align: middle;
    }

    .audit-row:hover>td {
      background: rgba(var(--primary-rgb), 0.03);
    }
  }

  // ===== 单元格样式 =====
  .user-name {
    font-weight: 600;
    color: var(--text-primary);
  }

  .ip-text {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
    color: var(--text-muted);
    letter-spacing: 0.3px;
  }

  .time-text {
    font-size: 12.5px;
    color: var(--text-secondary);
    white-space: nowrap;
  }

  .text-dim {
    color: var(--text-placeholder);
  }

  // ===== 操作类型标签 =====
  .action-tag {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.3px;
    line-height: 1.6;

    &.danger {
      background: rgba(239, 68, 68, 0.10);
      color: #EF4444;
    }

    &.success {
      background: rgba(34, 197, 94, 0.10);
      color: #22C55E;
    }

    &.warning {
      background: rgba(245, 158, 11, 0.10);
      color: #F59E0B;
    }

    &.info {
      background: rgba(59, 130, 246, 0.10);
      color: #3B82F6;
    }
  }

  // ===== 资源类型标签 =====
  .resource-tag {
    display: inline-flex;
    align-items: center;
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 11.5px;
    font-weight: 500;
    background: rgba(139, 92, 246, 0.08);
    color: #8B5CF6;
  }

  // ===== 详情列 =====
  .detail-cell {
    max-height: 120px;
    overflow-y: auto;
    line-height: 1.7;

    .detail-kv {
      display: inline-block;
      margin-right: 12px;
      margin-bottom: 2px;

      .detail-key {
        font-style: normal;
        color: var(--text-muted);
        font-size: 11.5px;
        margin-right: 3px;
      }

      .detail-val {
        color: var(--text-primary);
        font-size: 12px;
        word-break: break-all;
        max-width: 180px;
        display: inline-block;
        vertical-align: middle;
      }
    }

    .detail-text {
      font-size: 12px;
      color: var(--text-secondary);
      word-break: break-all;
      line-height: 1.6;
      font-family: 'Consolas', 'Monaco', monospace;
    }
  }

  // ===== 分页 =====
  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style>
