<template>
  <div class="patient-page">
    <div class="page-header">
      <h1 class="page-title">
        <span class="title-secondary">Patients</span>
        <span class="title-sep">/</span>
        <span class="title-main">患者管理</span>
      </h1>
      <p class="page-subtitle">管理患者档案信息，支持快速检索</p>
    </div>

    <div class="glass-card">
      <!-- 搜索筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="姓名/编号/电话" clearable
                    @keyup.enter="search" class="filter-input">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.gender" placeholder="性别" clearable>
            <el-option label="男" value="male" />
            <el-option label="女" value="female" />
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
        <div class="filter-actions">
          <el-button type="primary" @click="openDialog('create')">
            <el-icon><Plus /></el-icon> 新增患者
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" empty-text="暂无患者数据" class="glass-table">
        <el-table-column prop="patient_no" label="患者编号" width="130" show-overflow-tooltip />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="70">
          <template #default="{ row }">
            <span class="gender-badge" :class="row.gender">
              {{ row.gender === 'male' ? '男' : '女' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="medical_history" label="病史" min-width="180" show-overflow-tooltip />
        <el-table-column prop="created_at" label="建档时间" width="170" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <button class="action-btn edit" @click="openDialog('edit', row)" title="编辑">
                <el-icon><Edit /></el-icon>
              </button>
              <button class="action-btn view" @click="viewDetail(row)" title="查看详情">
                <el-icon><View /></el-icon>
              </button>
              <el-popconfirm title="确定删除此患者？" @confirm="handleDelete(row)">
                <template #reference>
                  <button class="action-btn delete" title="删除">
                    <el-icon><Delete /></el-icon>
                  </button>
                </template>
              </el-popconfirm>
            </div>
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
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增患者' : '编辑患者'" width="600px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="90px" size="default">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="患者编号" prop="patient_no">
              <el-input v-model="formData.patient_no" placeholder="如 P20260331001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="formData.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-radio-group v-model="formData.gender">
                <el-radio value="male">男</el-radio>
                <el-radio value="female">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input-number v-model="formData.age" :min="0" :max="150" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="formData.phone" placeholder="请输入电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="formData.id_card" placeholder="选填" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址">
          <el-input v-model="formData.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="病史记录">
          <el-input v-model="formData.medical_history" type="textarea" :rows="2" placeholder="请输入病史" />
        </el-form-item>
        <el-form-item label="过敏史">
          <el-input v-model="formData.allergy_history" type="textarea" :rows="2" placeholder="请输入过敏史" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remarks" type="textarea" :rows="2" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="患者详情" width="600px">
      <el-descriptions :column="2" border size="default" v-if="currentPatient">
        <el-descriptions-item label="患者编号">{{ currentPatient.patient_no }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ currentPatient.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">
          <span class="gender-badge" :class="currentPatient.gender">
            {{ currentPatient.gender === 'male' ? '男' : '女' }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="年龄">{{ currentPatient.age }}岁</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentPatient.phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="建档时间">{{ currentPatient.created_at }}</el-descriptions-item>
        <el-descriptions-item label="地址" :span="2">{{ currentPatient.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="病史记录" :span="2">{{ currentPatient.medical_history || '无' }}</el-descriptions-item>
        <el-descriptions-item label="过敏史" :span="2">{{ currentPatient.allergy_history || '无' }}</el-descriptions-item>
      </el-descriptions>
      <el-divider>近期诊断记录</el-divider>
      <el-table :data="currentPatientDiagnoses" size="small" max-height="250" empty-text="暂无诊断记录">
        <el-table-column prop="record_no" label="记录编号" width="180" />
        <el-table-column prop="ai_result" label="诊断结果" width="100">
          <template #default="{ row }">
            <span class="result-badge" :class="row.ai_result">{{ resultMap[row.ai_result] }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="置信度" width="100">
          <template #default="{ row }">{{ (row.confidence * 100).toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { patientApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Edit, View, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const dialogMode = ref('create')
const currentPatient = ref(null)
const currentPatientDiagnoses = ref([])
const formRef = ref(null)
const editId = ref(null)

const filters = reactive({ keyword: '', gender: '' })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const formData = reactive({
  patient_no: '', name: '', gender: 'male', age: 30,
  phone: '', id_card: '', address: '',
  medical_history: '', allergy_history: '', remarks: ''
})

const formRules = {
  patient_no: [{ required: true, message: '请输入患者编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }]
}

const resultMap = { normal: '正常', pneumonia: '肺炎', tuberculosis: '肺结核' }

const defaultForm = () => ({
  patient_no: '', name: '', gender: 'male', age: 30,
  phone: '', id_card: '', address: '',
  medical_history: '', allergy_history: '', remarks: ''
})

async function fetchData() {
  loading.value = true
  try {
    const params = { page: pagination.page, per_page: pagination.per_page }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.gender) params.gender = filters.gender
    const res = await patientApi.getList(params)
    tableData.value = res.data.items
    pagination.total = res.data.total
  } catch (e) {} finally { loading.value = false }
}

function search() { pagination.page = 1; fetchData() }
function resetFilters() { filters.keyword = ''; filters.gender = ''; search() }

function openDialog(mode, row = null) {
  dialogMode.value = mode
  editId.value = row?.id || null
  if (mode === 'edit' && row) {
    Object.assign(formData, { ...row })
  } else {
    Object.assign(formData, defaultForm())
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await patientApi.create({ ...formData })
      ElMessage.success('患者档案创建成功')
    } else {
      const { patient_no, created_at, updated_at, is_deleted, recent_diagnoses, ...updateData } = formData
      await patientApi.update(editId.value, updateData)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e) {} finally { submitting.value = false }
}

async function handleDelete(row) {
  try {
    await patientApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) {}
}

async function viewDetail(row) {
  currentPatient.value = row
  try {
    const res = await patientApi.getDetail(row.id)
    currentPatient.value = res.data
    currentPatientDiagnoses.value = res.data.recent_diagnoses?.items || []
  } catch (e) {
    currentPatientDiagnoses.value = []
  }
  detailVisible.value = true
}

onMounted(() => fetchData())
</script>

<style scoped lang="scss">
.patient-page {
  .page-header {
    margin-bottom: 24px;

    .page-title {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
      font-size: 28px;
      font-weight: 700;

      .title-secondary { color: var(--text-secondary); font-weight: 400; font-size: 20px; }
      .title-sep { color: var(--glass-border); font-weight: 300; }
      .title-main { color: var(--text-primary); }
    }

    .page-subtitle { font-size: 14px; color: var(--text-secondary); }
  }

  // 玻璃态卡片
  .glass-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.6), rgba(30, 41, 59, 0.4));
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 24px;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.08), transparent);
    }
  }

  // 筛选栏
  .filter-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;

    .filter-item {
      .filter-input { width: 220px; }
    }

    .filter-actions {
      display: flex;
      gap: 8px;
      margin-left: auto;

      &:last-child { margin-left: 0; }
    }
  }

  // 玻璃态表格
  .glass-table {
    --el-table-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
    --el-table-header-bg-color: rgba(15, 23, 42, 0.4);
    --el-table-row-hover-bg-color: rgba(16, 185, 129, 0.08);
    --el-table-border-color: rgba(255, 255, 255, 0.06);
    --el-table-text-color: var(--text-primary);
    --el-table-header-text-color: var(--text-secondary);

    :deep(th.el-table__cell) {
      font-weight: 600;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      background: rgba(15, 23, 42, 0.6) !important;
    }

    :deep(td.el-table__cell) {
      transition: all 0.3s ease;
    }

    :deep(.el-table__inner-wrapper::before) {
      display: none;
    }
  }

  // 性别徽标
  .gender-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;

    &.male {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(59, 130, 246, 0.1));
      color: #60A5FA;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }
    &.female {
      background: linear-gradient(135deg, rgba(236, 72, 153, 0.2), rgba(236, 72, 153, 0.1));
      color: #F472B6;
      border: 1px solid rgba(236, 72, 153, 0.3);
    }
  }

  // 结果徽标
  .result-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;

    &.normal {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
      color: var(--primary);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    &.pneumonia {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));
      color: var(--orange);
      border: 1px solid rgba(245, 158, 11, 0.3);
    }
    &.tuberculosis {
      background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(139, 92, 246, 0.1));
      color: var(--purple);
      border: 1px solid rgba(139, 92, 246, 0.3);
    }
  }

  // 操作按钮组
  .action-buttons {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .action-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.25s ease;
    background: rgba(255, 255, 255, 0.04);
    color: var(--text-secondary);

    &:hover {
      transform: translateY(-2px);
    }

    &.edit {
      &:hover {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
      }
    }

    &.view {
      &:hover {
        background: rgba(16, 185, 129, 0.15);
        color: var(--primary);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
      }
    }

    &.delete {
      &:hover {
        background: rgba(239, 68, 68, 0.15);
        color: #F87171;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
      }
    }

    .el-icon {
      font-size: 16px;
    }
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }
}

// 患者详情弹窗样式
:deep(.el-dialog) {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  overflow: hidden;

  .el-dialog__header {
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-right: 0;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .el-dialog__headerbtn {
      top: 20px;
      right: 20px;

      .el-dialog__close {
        color: var(--text-secondary);
        font-size: 18px;
        transition: all 0.3s ease;

        &:hover {
          color: var(--primary);
          transform: rotate(90deg);
        }
      }
    }
  }

  .el-dialog__body {
    padding: 24px;
    color: var(--text-primary);
  }

  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
  }

  .el-descriptions {
    .el-descriptions__body {
      background: transparent !important;
    }

    .el-descriptions__cell {
      border: 1px solid rgba(255, 255, 255, 0.08) !important;
      padding: 12px 16px !important;
    }

    .el-descriptions__label {
      color: var(--text-secondary) !important;
      font-weight: 500 !important;
      background: rgba(15, 23, 42, 0.7) !important;
    }

    .el-descriptions__content {
      color: var(--text-primary) !important;
      background: rgba(30, 41, 59, 0.5) !important;
    }
  }
}

// 描述列表样式
:deep(.el-descriptions) {
  .el-descriptions__label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    background: rgba(15, 23, 42, 0.6) !important;
  }

  .el-descriptions__content {
    color: var(--text-primary) !important;
    background: rgba(30, 41, 59, 0.4) !important;
  }

  .el-descriptions__cell {
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    padding: 12px 16px !important;
  }
}

::deep(.el-descriptions.is-bordered) {
  .el-descriptions__cell {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
  }

  .el-descriptions__label {
    background: rgba(15, 23, 42, 0.7) !important;
  }

  .el-descriptions__content {
    background: rgba(30, 41, 59, 0.5) !important;
  }
}

// 分隔线样式
:deep(.el-divider) {
  border-color: rgba(255, 255, 255, 0.1);

  .el-divider__text {
    background: transparent;
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 14px;
  }
}

// 表单样式
:deep(.el-form) {
  .el-form-item__label {
    color: var(--text-secondary);
    font-weight: 500;
  }

  .el-input__wrapper,
  .el-select__wrapper,
  .el-textarea__inner {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: none;
    transition: all 0.3s ease;

    &:hover {
      border-color: rgba(255, 255, 255, 0.2);
    }

    &.is-focus,
    &:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
    }
  }

  .el-input__inner,
  .el-textarea__inner {
    color: var(--text-primary);

    &::placeholder {
      color: var(--text-muted);
    }
  }

  .el-radio-group {
    .el-radio {
      margin-right: 20px;

      .el-radio__input.is-checked .el-radio__inner {
        border-color: var(--primary);
        background: var(--primary);
      }

      .el-radio__input.is-checked + .el-radio__label {
        color: var(--primary);
      }

      .el-radio__label {
        color: var(--text-secondary);
      }
    }
  }

  .el-input-number {
    .el-input-number__decrease,
    .el-input-number__increase {
      background: rgba(15, 23, 42, 0.6);
      border-color: rgba(255, 255, 255, 0.1);
      color: var(--text-secondary);

      &:hover {
        color: var(--primary);
      }
    }
  }
}

// 按钮样式
:deep(.el-button) {
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, var(--primary), #059669);
  border: none;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
  }
}

:deep(.el-button--default) {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);

  &:hover {
    border-color: rgba(255, 255, 255, 0.2);
    color: var(--text-primary);
    background: rgba(30, 41, 59, 0.8);
  }
}

:deep(.el-button--success) {
  background: linear-gradient(135deg, #10B981, #059669);
  border: none;

  &:hover {
    transform: translateY(-1px);
  }
}

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  border: none;
}

:deep(.el-button.is-link) {
  font-weight: 500;
}

:deep(.el-button.is-link.el-button--primary) {
  color: var(--primary);

  &:hover {
    color: #34D399;
  }
}

:deep(.el-button.is-link.el-button--success) {
  color: var(--primary);

  &:hover {
    color: #34D399;
  }
}

:deep(.el-button.is-link.el-button--danger) {
  color: #F87171;

  &:hover {
    color: #EF4444;
  }
}

// 下拉选择框
:deep(.el-select) {
  .el-select__wrapper {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);

    .el-select__placeholder {
      color: var(--text-muted);
    }

    .el-select__selected-item {
      color: var(--text-primary);
    }
  }
}

// 分页样式
:deep(.el-pagination) {
  --el-pagination-bg-color: rgba(15, 23, 42, 0.6);
  --el-pagination-text-color: var(--text-secondary);
  --el-pagination-button-bg-color: transparent;
  --el-pagination-hover-color: var(--primary);

  .el-pagination__total,
  .el-pagination__jump {
    color: var(--text-secondary);
  }

  .el-pager li {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    margin: 0 3px;

    &.is-active {
      background: linear-gradient(135deg, var(--primary), #059669);
      border-color: var(--primary);
      color: white;
    }

    &:hover:not(.is-active) {
      border-color: var(--primary);
      color: var(--primary);
    }
  }

  .btn-prev,
  .btn-next {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;

    &:hover:not(:disabled) {
      color: var(--primary);
      border-color: var(--primary);
    }
  }

  .el-pagination__sizes {
    .el-select__wrapper {
      background: rgba(15, 23, 42, 0.6);
    }
  }
}

// Popconfirm 样式
:deep(.el-popconfirm) {
  .el-popconfirm__main {
    color: var(--text-primary);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .patient-page {
    .filter-bar {
      flex-direction: column;
      align-items: stretch;

      .filter-item {
        width: 100%;
        .filter-input { width: 100%; }
      }

      .filter-actions {
        margin-left: 0;
        justify-content: flex-end;
      }
    }
  }
}
</style>
