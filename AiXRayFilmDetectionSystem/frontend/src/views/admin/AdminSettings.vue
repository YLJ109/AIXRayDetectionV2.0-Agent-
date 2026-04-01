<template>
  <div class="admin-settings">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">系统设置</h2>
        <p class="page-desc">管理系统配置参数，控制核心功能行为</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleAdd" :icon="Plus">新增配置</el-button>
        <el-button @click="fetchConfigs" :icon="Refresh" :loading="loading">刷新</el-button>
      </div>
    </div>

    <!-- 配置分组展示 -->
    <div v-loading="loading" class="config-groups">
      <div v-for="(configs, group) in groupedConfigs" :key="group" class="config-group">
        <div class="group-header">
          <div class="group-icon">
            <el-icon :size="18"><component :is="groupIcons[group] || Setting" /></el-icon>
          </div>
          <h3 class="group-title">{{ groupLabels[group] || group }}</h3>
          <span class="group-count">{{ configs.length }} 项</span>
        </div>

        <div class="config-list">
          <div v-for="item in configs" :key="item.id" class="config-item">
            <div class="config-info">
              <div class="config-key">{{ item.key }}</div>
              <div class="config-desc">{{ item.description || '暂无描述' }}</div>
            </div>

            <div class="config-value-area">
              <!-- 布尔类型 -->
              <el-switch
                v-if="item.type === 'boolean'"
                v-model="item.value"
                @change="(val) => handleToggle(item, val)"
                active-color="#EF4444"
              />
              <!-- 数字类型 -->
              <el-input-number
                v-else-if="item.type === 'number'"
                v-model="item.value"
                :controls="false"
                size="small"
                style="width: 140px"
                @change="(val) => handleUpdate(item, val)"
              />
              <!-- 文本类型 -->
              <el-input
                v-else
                v-model="item.value"
                size="small"
                style="width: 200px"
                @blur="(e) => handleUpdate(item, e.target.value)"
              />
            </div>

            <div class="config-actions">
              <el-tag :type="typeTagMap[item.type] || 'info'" size="small" effect="light">
                {{ typeLabels[item.type] || item.type }}
              </el-tag>
              <el-button type="danger" link size="small" @click="handleDelete(item)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && Object.keys(groupedConfigs).length === 0" class="empty-state">
        <el-empty description="暂无系统配置">
          <el-button type="primary" @click="handleAdd">添加配置</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 新增/编辑配置对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="configForm" :rules="formRules" label-width="90px">
        <el-form-item label="配置键" prop="key">
          <el-input v-model="configForm.key" placeholder="如: max_upload_size" :disabled="!!configForm.id" />
        </el-form-item>
        <el-form-item label="配置值" prop="value">
          <el-input
            v-model="configForm.value"
            placeholder="请输入配置值"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
        <el-form-item label="值类型" prop="type">
          <el-select v-model="configForm.type" style="width: 100%">
            <el-option label="字符串" value="string" />
            <el-option label="数字" value="number" />
            <el-option label="布尔值" value="boolean" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属分组" prop="group">
          <el-select v-model="configForm.group" style="width: 100%" allow-create filterable>
            <el-option label="通用设置" value="general" />
            <el-option label="AI模型" value="model" />
            <el-option label="安全设置" value="security" />
            <el-option label="通知设置" value="notification" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configForm.description" placeholder="配置项说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { systemApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Delete, Setting, Cpu, Lock, Bell } from '@element-plus/icons-vue'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const rawConfigs = ref({})

const groupedConfigs = computed(() => rawConfigs.value)

const dialogTitle = computed(() => configForm.id ? '编辑配置' : '新增配置')

const configForm = reactive({
  id: null,
  key: '',
  value: '',
  type: 'string',
  group: 'general',
  description: ''
})

const formRules = {
  key: [{ required: true, message: '请输入配置键', trigger: 'blur' }],
  value: [{ required: true, message: '请输入配置值', trigger: 'blur' }],
  type: [{ required: true, message: '请选择值类型', trigger: 'change' }],
  group: [{ required: true, message: '请选择分组', trigger: 'change' }]
}

const groupLabels = {
  general: '通用设置',
  model: 'AI模型配置',
  security: '安全设置',
  notification: '通知设置'
}

const groupIcons = {
  general: Setting,
  model: Cpu,
  security: Lock,
  notification: Bell
}

const typeLabels = {
  string: '字符串',
  number: '数字',
  boolean: '开关',
  json: 'JSON'
}

const typeTagMap = {
  string: '',
  number: 'success',
  boolean: 'warning',
  json: 'danger'
}

async function fetchConfigs() {
  loading.value = true
  try {
    const res = await systemApi.getConfigs()
    rawConfigs.value = res.data || {}
  } catch (e) {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  configForm.id = null
  configForm.key = ''
  configForm.value = ''
  configForm.type = 'string'
  configForm.group = 'general'
  configForm.description = ''
  dialogVisible.value = true
}

async function handleUpdate(item, value) {
  try {
    await systemApi.updateConfig(item.id, { value })
    ElMessage.success('配置已更新')
  } catch (e) {
    // revert on error
    fetchConfigs()
  }
}

async function handleToggle(item, value) {
  try {
    await systemApi.updateConfig(item.id, { value: value ? 'true' : 'false' })
    ElMessage.success('配置已更新')
  } catch (e) {
    item.value = !value
  }
}

function handleDelete(item) {
  ElMessageBox.confirm(`确定删除配置 "${item.key}" 吗？`, '确认删除', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await systemApi.deleteConfig(item.id)
      ElMessage.success('配置已删除')
      fetchConfigs()
    } catch (e) {}
  }).catch(() => {})
}

async function submitForm() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (configForm.id) {
      await systemApi.updateConfig(configForm.id, {
        value: configForm.value,
        type: configForm.type,
        group: configForm.group,
        description: configForm.description
      })
      ElMessage.success('配置更新成功')
    } else {
      await systemApi.createConfig({
        key: configForm.key,
        value: configForm.value,
        type: configForm.type,
        group: configForm.group,
        description: configForm.description
      })
      ElMessage.success('配置创建成功')
    }
    dialogVisible.value = false
    fetchConfigs()
  } catch (e) {
    // handled by interceptor
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchConfigs()
})
</script>

<style scoped lang="scss">
.admin-settings {
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

.config-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-group {
  background: var(--card-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--glass-border);
  background: var(--glass-bg);

  .group-icon {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(245, 158, 11, 0.15));
    display: flex;
    align-items: center;
    justify-content: center;
    color: #EF4444;
  }

  .group-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .group-count {
    font-size: 12px;
    color: var(--text-muted);
    background: var(--glass-bg);
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: auto;
  }
}

.config-list {
  padding: 8px 0;
}

.config-item {
  display: flex;
  align-items: center;
  padding: 14px 24px;
  gap: 20px;
  transition: background var(--transition-normal);

  &:hover {
    background: var(--glass-bg);
  }

  + .config-item {
    border-top: 1px solid rgba(255, 255, 255, 0.03);
  }
}

.config-info {
  flex: 1;
  min-width: 0;

  .config-key {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    font-family: 'Courier New', monospace;
    margin-bottom: 2px;
  }

  .config-desc {
    font-size: 12px;
    color: var(--text-muted);
  }
}

.config-value-area {
  flex-shrink: 0;
}

.config-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.empty-state {
  padding: 60px 0;
}
</style>
