/** 管理员-大模型API管理页面 */
<template>
  <div class="llm-page">
    <div class="glass-card">
      <!-- 搜索筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="模型名称/提供商" clearable
            @keyup.enter="search" class="filter-input">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.status" placeholder="状态" clearable>
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
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
          <el-button type="primary" @click="openDialog()">
            <el-icon><Plus /></el-icon> 新增配置
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table :data="filteredConfigs" v-loading="loading" empty-text="暂无大模型配置" class="glass-table">
        <el-table-column prop="model_name" label="模型名称" width="160" />
        <el-table-column label="提供商" width="110">
          <template #default="{ row }">
            <span class="provider-badge" :class="getProviderClass(row.provider)">
              {{ row.provider || '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="api_endpoint" label="API地址" min-width="250" show-overflow-tooltip />
        <el-table-column label="默认" width="70">
          <template #default="{ row }">
            <span class="status-dot" :class="row.is_default ? 'active' : 'inactive'"></span>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="70" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <span class="status-dot" :class="row.status === 'active' ? 'active' : 'inactive'"></span>
            <span class="status-text">{{ row.status === 'active' ? '启用' : '停用' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" class="action-link" @click="handleTest(row)" :loading="row._testing">测试</el-button>
            <el-button type="primary" link size="small" class="action-link" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm title="确定删除此配置？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small" class="action-link" :disabled="row.is_default">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑配置' : '新增配置'" width="550px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px" size="default">
        <el-form-item label="模型名称" prop="model_name">
          <el-input v-model="formData.model_name" placeholder="如 qwen-plus" :disabled="!!editingId" />
        </el-form-item>
        <el-form-item label="提供商" prop="provider">
          <el-input v-model="formData.provider" placeholder="如 qwen/deepseek/openai" />
        </el-form-item>
        <el-form-item label="API地址" prop="api_endpoint">
          <el-input v-model="formData.api_endpoint" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="API Key" prop="api_key">
          <el-input v-model="formData.api_key" type="password" show-password
            :placeholder="editingId ? '留空则不修改' : '请输入API Key'" />
        </el-form-item>
        <el-form-item label="Temperature">
          <el-input-number v-model="formData.temperature" :min="0" :max="2" :step="0.1" :precision="1" />
        </el-form-item>
        <el-form-item label="Max Tokens">
          <el-input-number v-model="formData.max_tokens" :min="100" :max="8192" :step="100" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" active-text="是" inactive-text="否" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="formData.priority" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="状态" v-if="!!editingId">
          <el-radio-group v-model="formData.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getLlmConfigsApi, createLlmConfigApi, updateLlmConfigApi, deleteLlmConfigApi, testLlmConnectionApi } from '@/api/llm-configs'

const loading = ref(false)
const submitting = ref(false)
const configs = ref<any[]>([])
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<any>(null)

const filters = reactive({ keyword: '', status: '' })

const formData = reactive({
  model_name: '', provider: '', api_endpoint: '', api_key: '',
  temperature: 0.3, max_tokens: 2048, is_default: false, priority: 1, status: 'active',
})

const formRules = {
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  api_endpoint: [{ required: true, message: '请输入API地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }],
}

const filteredConfigs = computed(() => {
  let list = configs.value
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase()
    list = list.filter(c =>
      c.model_name?.toLowerCase().includes(kw) ||
      c.provider?.toLowerCase().includes(kw)
    )
  }
  if (filters.status) {
    list = list.filter(c => c.status === filters.status)
  }
  return list
})

function getProviderClass(provider: string) {
  if (!provider) return ''
  const p = provider.toLowerCase()
  if (p.includes('qwen') || p.includes('ali')) return 'qwen'
  if (p.includes('deepseek')) return 'deepseek'
  if (p.includes('openai') || p.includes('gpt')) return 'openai'
  if (p.includes('zhipu') || p.includes('glm')) return 'zhipu'
  return 'other'
}

async function loadConfigs() {
  loading.value = true
  try {
    const res: any = await getLlmConfigsApi()
    configs.value = res.data.map((c: any) => ({ ...c, _testing: false }))
  } catch { /* handled */ } finally { loading.value = false }
}

function search() { /* filteredConfigs is computed */ }
function resetFilters() { filters.keyword = ''; filters.status = '' }

function openDialog(row?: any) {
  editingId.value = row?.id || null
  if (row) {
    Object.assign(formData, {
      model_name: row.model_name,
      provider: row.provider || '',
      api_endpoint: row.api_endpoint || '',
      api_key: '',
      temperature: row.default_params?.temperature ?? 0.3,
      max_tokens: row.default_params?.max_tokens ?? 2048,
      is_default: row.is_default,
      priority: row.priority,
      status: row.status || 'active',
    })
  } else {
    Object.assign(formData, {
      model_name: '', provider: '', api_endpoint: '', api_key: '',
      temperature: 0.3, max_tokens: 2048, is_default: false, priority: 1, status: 'active',
    })
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
  } catch { return }
  submitting.value = true
  try {
    const data: any = {
      ...formData,
      default_params: { temperature: formData.temperature, max_tokens: formData.max_tokens },
    }
    // 编辑时如果不填API Key则不提交
    if (editingId.value && !data.api_key) delete data.api_key
    if (editingId.value) {
      await updateLlmConfigApi(editingId.value, data)
    } else {
      await createLlmConfigApi(data)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadConfigs()
  } catch { /* handled */ } finally { submitting.value = false }
}

async function handleTest(row: any) {
  row._testing = true
  try {
    const res: any = await testLlmConnectionApi(row.id)
    if (res.data.success) {
      ElMessage.success('连通性测试成功')
    } else {
      ElMessage.error(`连通失败: ${res.data.error}`)
    }
  } catch { /* handled */ } finally { row._testing = false }
}

async function handleDelete(row: any) {
  try {
    await deleteLlmConfigApi(row.id)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch { /* handled */ }
}

onMounted(() => loadConfigs())
</script>

<style scoped lang="scss">
.llm-page {
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

  // 提供商徽标
  .provider-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;

    &.qwen { background: rgba(249, 115, 22, 0.15); color: #FB923C; }
    &.deepseek { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
    &.openai { background: rgba(34, 211, 238, 0.2); color: var(--primary); }
    &.zhipu { background: rgba(139, 92, 246, 0.15); color: #A78BFA; }
    &.other { background: rgba(107, 114, 128, 0.15); color: #9CA3AF; }
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

  // 表格
  :deep(.el-table__cell) {
    display: table-cell !important;
    vertical-align: middle !important;
  }

  :deep(.el-table__row) {
    td {
      .cell {
        display: flex;
        align-items: center;
        justify-content: flex-start;
      }
    }
  }

  :deep(.el-table__body tr td) {
    .cell {
      &:has(.provider-badge),
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
