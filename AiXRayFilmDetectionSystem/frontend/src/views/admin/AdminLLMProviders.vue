<template>
  <div class="admin-llm-providers">
    <!-- 顶部 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">大模型API管理</h2>
        <p class="page-desc">统一管理多种大模型API（豆包、DeepSeek、ChatGPT等），提供安全的密钥存储和统一调用接口</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog" :icon="Plus">添加提供商</el-button>
        <el-button @click="fetchData" :icon="Refresh" :loading="loading">刷新</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="glass-card stat-card">
        <div class="stat-icon providers">
          <el-icon :size="24"><Connection /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ providers.length }}</div>
          <div class="stat-label">已配置提供商</div>
        </div>
      </div>
      <div class="glass-card stat-card">
        <div class="stat-icon active">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ activeCount }}</div>
          <div class="stat-label">启用中</div>
        </div>
      </div>
      <div class="glass-card stat-card">
        <div class="stat-icon calls">
          <el-icon :size="24"><ChatDotRound /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalCalls }}</div>
          <div class="stat-label">累计调用</div>
        </div>
      </div>
    </div>

    <!-- 提供商列表 -->
    <div class="glass-card providers-panel">
      <div class="panel-header">
        <h3 class="panel-title">提供商列表</h3>
      </div>
      <el-table :data="providers" v-loading="loading" class="providers-table">
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="provider_type" label="类型" width="130">
          <template #default="{ row }">
            <el-tag :type="getProviderTypeTag(row.provider_type)" size="small" effect="light">
              {{ getProviderTypeName(row.provider_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="default_model" label="默认模型" width="180" show-overflow-tooltip />
        <el-table-column prop="api_endpoint" label="API端点" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="endpoint-code">{{ row.api_endpoint }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="handleToggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="90" align="center" sortable />
        <el-table-column prop="total_calls" label="调用次数" width="100" align="center" sortable />
        <el-table-column prop="last_used_at" label="最后使用" width="160" align="center">
          <template #default="{ row }">
            {{ row.last_used_at || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleTest(row)" :loading="row.testing">
              <el-icon><Connection /></el-icon> 测试
            </el-button>
            <el-button type="warning" link size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-popconfirm title="确定删除此提供商？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small">
                  <el-icon><Delete /></el-icon> 删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '添加LLM提供商' : '编辑LLM提供商'"
               width="600px" destroy-on-close @close="resetForm">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="提供商名称" prop="name">
          <el-input v-model="formData.name" placeholder="例如：OpenAI官方" />
        </el-form-item>
        <el-form-item label="提供商类型" prop="provider_type">
          <el-select v-model="formData.provider_type" placeholder="选择提供商类型" style="width: 100%"
                     @change="handleProviderTypeChange">
            <el-option v-for="t in providerTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="formData.api_key" type="password" show-password
                    placeholder="输入API密钥（加密存储）" />
        </el-form-item>
        <el-form-item label="API端点" prop="api_endpoint">
          <el-input v-model="formData.api_endpoint" placeholder="例如：https://api.openai.com/v1/chat/completions" />
        </el-form-item>
        <el-form-item label="默认模型" prop="default_model">
          <el-input v-model="formData.default_model" placeholder="例如：gpt-3.5-turbo" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="formData.priority" :min="0" :max="100" />
          <span class="form-hint">数字越大优先级越高</span>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="formData.is_active" />
        </el-form-item>
        <el-form-item label="其他配置">
          <el-input v-model="formData.config_json_str" type="textarea" :rows="3"
                    placeholder='例如：{"temperature": 0.7, "max_tokens": 2000}' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 调用日志对话框 -->
    <el-dialog v-model="logsDialogVisible" title="LLM调用日志" width="900px">
      <el-table :data="logs" v-loading="logsLoading" max-height="500">
        <el-table-column prop="provider_name" label="提供商" width="120" />
        <el-table-column prop="user_name" label="调用者" width="100" />
        <el-table-column prop="model_name" label="模型" width="150" />
        <el-table-column prop="total_tokens" label="Token数" width="100" align="center" />
        <el-table-column prop="response_time" label="响应时间" width="100" align="center">
          <template #default="{ row }">{{ row.response_time }}s</template>
        </el-table-column>
        <el-table-column prop="is_success" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_success ? 'success' : 'danger'" size="small">
              {{ row.is_success ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="160" />
      </el-table>
      <div class="pagination-wrap">
        <el-pagination v-model:current-page="logsPagination.page" v-model:page-size="logsPagination.per_page"
                       :total="logsPagination.total" :page-sizes="[10, 20, 50]"
                       layout="total, sizes, prev, pager, next" @size-change="fetchLogs" @current-change="fetchLogs" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { llmApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Connection, CircleCheck, ChatDotRound, Edit, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const submitting = ref(false)
const logsLoading = ref(false)
const dialogVisible = ref(false)
const logsDialogVisible = ref(false)
const dialogMode = ref('create')
const editId = ref(null)
const formRef = ref(null)

const providers = ref([])
const providerTypes = ref([])
const logs = ref([])

const formData = reactive({
  name: '',
  provider_type: '',
  api_key: '',
  api_endpoint: '',
  default_model: '',
  priority: 0,
  is_active: true,
  config_json_str: '{}'
})

const formRules = {
  name: [{ required: true, message: '请输入提供商名称', trigger: 'blur' }],
  provider_type: [{ required: true, message: '请选择提供商类型', trigger: 'change' }],
  api_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }],
  api_endpoint: [{ required: true, message: '请输入API端点', trigger: 'blur' }]
}

const logsPagination = reactive({ page: 1, per_page: 20, total: 0 })

// 统计
const activeCount = computed(() => providers.value.filter(p => p.is_active).length)
const totalCalls = computed(() => providers.value.reduce((sum, p) => sum + p.total_calls, 0))

function getProviderTypeTag(type) {
  const map = { openai: 'success', anthropic: 'warning', doubao: 'danger', deepseek: 'primary', custom: 'info' }
  return map[type] || 'info'
}

function getProviderTypeName(type) {
  const names = { openai: 'OpenAI', anthropic: 'Anthropic', doubao: '豆包', deepseek: 'DeepSeek', custom: '自定义' }
  return names[type] || type
}

async function fetchData() {
  loading.value = true
  try {
    const [providersRes, typesRes] = await Promise.all([
      llmApi.getProviders(),
      llmApi.getProviderTypes()
    ])
    providers.value = providersRes.data.providers.map(p => ({ ...p, testing: false }))
    providerTypes.value = typesRes.data.types
  } catch (e) {} finally {
    loading.value = false
  }
}

function handleProviderTypeChange(type) {
  const selected = providerTypes.value.find(t => t.value === type)
  if (selected) {
    if (!formData.api_endpoint) formData.api_endpoint = selected.default_endpoint
    if (!formData.default_model) formData.default_model = selected.default_model
  }
}

function showCreateDialog() {
  dialogMode.value = 'create'
  editId.value = null
  Object.assign(formData, {
    name: '', provider_type: '', api_key: '', api_endpoint: '',
    default_model: '', priority: 0, is_active: true, config_json_str: '{}'
  })
  dialogVisible.value = true
}

function handleEdit(row) {
  dialogMode.value = 'edit'
  editId.value = row.id
  Object.assign(formData, {
    name: row.name,
    provider_type: row.provider_type,
    api_key: '',
    api_endpoint: row.api_endpoint,
    default_model: row.default_model,
    priority: row.priority,
    is_active: row.is_active,
    config_json_str: '{}'
  })
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const data = {
      name: formData.name,
      provider_type: formData.provider_type,
      api_key: formData.api_key,
      api_endpoint: formData.api_endpoint,
      default_model: formData.default_model,
      priority: formData.priority,
      is_active: formData.is_active
    }
    if (formData.config_json_str) {
      try { data.config_json = JSON.parse(formData.config_json_str) } catch (e) {}
    }
    
    if (dialogMode.value === 'create') {
      await llmApi.createProvider(data)
      ElMessage.success('提供商创建成功')
    } else {
      await llmApi.updateProvider(editId.value, data)
      ElMessage.success('提供商更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {} finally {
    submitting.value = false
  }
}

async function handleToggleActive(row) {
  try {
    await llmApi.updateProvider(row.id, { is_active: row.is_active })
    ElMessage.success(row.is_active ? '已启用' : '已禁用')
  } catch (e) {
    row.is_active = !row.is_active
  }
}

async function handleTest(row) {
  row.testing = true
  try {
    const res = await llmApi.testProvider(row.id)
    if (res.data.success) {
      ElMessage.success(`连接测试成功 (${res.data.response_time.toFixed(2)}s)`)
    } else {
      ElMessage.error(res.data.message || '连接测试失败')
    }
  } catch (e) {} finally {
    row.testing = false
  }
}

async function handleDelete(row) {
  try {
    await llmApi.deleteProvider(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {}
}

function resetForm() {
  formRef.value?.resetFields()
}

async function fetchLogs() {
  logsLoading.value = true
  try {
    const res = await llmApi.getLogs({
      page: logsPagination.page,
      per_page: logsPagination.per_page
    })
    logs.value = res.data.items
    logsPagination.total = res.data.total
  } catch (e) {} finally {
    logsLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.admin-llm-providers {
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px;
    .header-info { .page-title { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; } .page-desc { color: var(--text-muted); font-size: 13px; } }
    .header-actions { display: flex; gap: 10px; }
  }

  .stats-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px;
  }

  .stat-card {
    display: flex; align-items: center; gap: 16px; padding: 20px;
    .stat-icon {
      width: 56px; height: 56px; border-radius: var(--radius-md);
      display: flex; align-items: center; justify-content: center;
      &.providers { background: rgba(239, 68, 68, 0.15); color: #EF4444; }
      &.active { background: rgba(16, 185, 129, 0.15); color: #10B981; }
      &.calls { background: rgba(139, 92, 246, 0.15); color: #8B5CF6; }
    }
    .stat-value { font-size: 28px; font-weight: 700; color: var(--text-primary); }
    .stat-label { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
  }

  .panel-header { margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid var(--glass-border);
    .panel-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
  }

  .providers-table {
    background: transparent;
    :deep(.el-table__inner-wrapper::before) { display: none; }
    :deep(.el-table__header th) { background: rgba(239, 68, 68, 0.08); color: var(--text-primary); font-weight: 600; }
    :deep(.el-table__body tr) { background: rgba(255, 255, 255, 0.02);
      td { color: var(--text-primary); border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
      &:hover > td { background: rgba(239, 68, 68, 0.06); }
    }
  }

  .endpoint-code {
    font-size: 12px; font-family: 'Courier New', monospace;
    background: rgba(255, 255, 255, 0.05); padding: 2px 8px; border-radius: 4px;
    color: #10B981;
  }

  .form-hint {
    font-size: 12px; color: var(--text-muted); margin-left: 12px;
  }

  .pagination-wrap {
    display: flex; justify-content: flex-end; margin-top: 16px;
  }
}
</style>
