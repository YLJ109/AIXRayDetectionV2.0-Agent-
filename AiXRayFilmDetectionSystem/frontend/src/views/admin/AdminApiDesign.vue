<template>
  <div class="admin-api-design">
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">API管理</h2>
        <p class="page-desc">查看系统所有已注册的API接口，支持按方法、路径搜索筛选</p>
      </div>
      <div class="header-actions">
        <el-button @click="fetchRoutes" :icon="Refresh" :loading="loading">刷新</el-button>
        <el-button type="success" plain @click="handleExportSwagger" :icon="Download">导出OpenAPI</el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="请求方法">
          <el-select v-model="filter.method" placeholder="全部" clearable style="width: 130px">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="路径搜索">
          <el-input v-model="filter.keyword" placeholder="输入路径关键词" clearable style="width: 220px"
            prefix-icon="Search" @input="handleFilter" />
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 统计摘要 -->
    <div class="summary-bar">
      <span class="summary-item" v-for="m in methodStats" :key="m.method">
        <span class="method-dot" :class="m.method.toLowerCase()"></span>
        {{ m.method }}
        <strong>{{ m.count }}</strong>
      </span>
      <span class="summary-item total">共 <strong>{{ filteredRoutes.length }}</strong> 个接口</span>
    </div>

    <!-- API路由表格 -->
    <div class="table-card">
      <el-table :data="filteredRoutes" v-loading="loading" class="api-table" row-key="path"
        :default-sort="{ prop: 'path', order: 'ascending' }">
        <el-table-column label="方法" width="100" align="center" sortable sort-by="methods[0]">
          <template #default="{ row }">
            <el-tag v-for="m in row.methods" :key="m" :type="methodTagType(m)" size="small" effect="dark"
              class="method-tag">
              {{ m }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路径" min-width="300" sortable>
          <template #default="{ row }">
            <code class="path-code">{{ row.path }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="endpoint" label="端点" width="220">
          <template #default="{ row }">
            <span class="endpoint-text">{{ row.endpoint }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleCopyPath(row.path)">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { systemApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'

const loading = ref(false)
const routes = ref([])

const filter = reactive({ method: '', keyword: '' })

const filteredRoutes = computed(() => {
  let result = routes.value
  if (filter.method) {
    result = result.filter(r => r.methods.includes(filter.method))
  }
  if (filter.keyword) {
    const kw = filter.keyword.toLowerCase()
    result = result.filter(r => r.path.toLowerCase().includes(kw) || r.endpoint.toLowerCase().includes(kw))
  }
  return result
})

const methodStats = computed(() => {
  const counts = {}
  for (const r of routes.value) {
    for (const m of r.methods) {
      counts[m] = (counts[m] || 0) + 1
    }
  }
  return Object.entries(counts).map(([method, count]) => ({ method, count })).sort((a, b) => b.count - a.count)
})

function methodTagType(method) {
  const map = { GET: 'success', POST: 'primary', PUT: 'warning', DELETE: 'danger', PATCH: 'info' }
  return map[method] || 'info'
}

function handleFilter() {}

function resetFilter() {
  filter.method = ''
  filter.keyword = ''
}

async function fetchRoutes() {
  loading.value = true
  try {
    const res = await systemApi.listApiRoutes()
    routes.value = res.data || []
  } catch (e) {} finally {
    loading.value = false
  }
}

function handleCopyPath(path) {
  navigator.clipboard.writeText(path).then(() => {
    ElMessage.success('路径已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

function handleExportSwagger() {
  const openapi = {
    openapi: '3.0.0',
    info: { title: '胸影智诊V2.0 API', version: '2.0.0' },
    paths: {}
  }
  for (const r of routes.value) {
    const key = r.path.replace('<', '{').replace('>', '}')
    if (!openapi.paths[key]) openapi.paths[key] = {}
    for (const m of r.methods) {
      openapi.paths[key][m.toLowerCase()] = {
        operationId: r.endpoint,
        responses: { '200': { description: 'Success' } }
      }
    }
  }
  const blob = new Blob([JSON.stringify(openapi, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'openapi.json'
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('OpenAPI文档已导出')
}

onMounted(() => { fetchRoutes() })
</script>

<style scoped lang="scss">
.admin-api-design {
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px;
    .header-info { .page-title { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; } .page-desc { color: var(--text-muted); font-size: 13px; } }
    .header-actions { display: flex; gap: 10px; }
  }

  .filter-card {
    background: var(--card-bg); backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border); border-radius: var(--radius-lg);
    padding: 16px 24px; margin-bottom: 16px;
    .filter-form { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 0;
      :deep(.el-form-item) { margin-bottom: 0; margin-right: 16px; display: flex; align-items: center; }
      :deep(.el-form-item__label) { display: flex; align-items: center; height: 32px; line-height: 32px; }
      :deep(.el-form-item__content) { display: flex; align-items: center; line-height: 32px; }
      :deep(.el-input__wrapper) { height: 32px; padding: 0 12px; }
      :deep(.el-select .el-select__wrapper) { height: 32px; min-height: 32px; }
      :deep(.el-date-editor) { height: 32px; .el-input__wrapper { height: 32px; padding: 0 12px; } }
      :deep(.el-button) { height: 32px; padding: 0 16px; }
    }
  }

  .summary-bar {
    display: flex; align-items: center; gap: 20px; padding: 12px 24px;
    background: var(--card-bg); backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border); border-radius: var(--radius-lg);
    margin-bottom: 16px;
    .summary-item { font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 6px;
      strong { color: var(--text-primary); }
      &.total { margin-left: auto; }
    }
    .method-dot { width: 8px; height: 8px; border-radius: 50%;
      &.get { background: #10B981; } &.post { background: #3B82F6; } &.put { background: #F59E0B; } &.delete { background: #EF4444; }
    }
  }

  .table-card {
    background: var(--card-bg); backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border); border-radius: var(--radius-lg);
    padding: 20px 24px;
    .api-table { width: 100%; background: transparent;
      :deep(.el-table__inner-wrapper::before) { display: none; }
      :deep(.el-table__header th) { background: rgba(239, 68, 68, 0.08); color: var(--text-primary); font-weight: 600; font-size: 13px; border-bottom: 1px solid rgba(239, 68, 68, 0.15); }
      :deep(.el-table__body tr) { background: rgba(255, 255, 255, 0.03);
        td { border-bottom: 1px solid rgba(255, 255, 255, 0.06); color: var(--text-primary); }
        &:hover > td { background: rgba(239, 68, 68, 0.06) !important; }
      }
    }
    .method-tag { margin-right: 2px; min-width: 42px; text-align: center; }
    .path-code { font-size: 13px; font-family: 'Courier New', monospace; background: var(--glass-bg); padding: 2px 8px; border-radius: 4px; color: #10B981; }
    .endpoint-text { font-size: 13px; color: var(--text-secondary); }
  }
}
</style>
