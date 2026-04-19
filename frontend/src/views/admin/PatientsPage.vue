/** 管理员-患者管理页面 */
<template>
  <div class="patients-page">
    <div class="glass-card">
      <!-- 搜索筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="姓名/编号/手机/身份证" clearable
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
        <div class="filter-actions" style="margin-left: auto;">
          <el-button type="primary" @click="openDialog('create')">
            <el-icon><Plus /></el-icon> 新增患者
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" empty-text="暂无患者数据" class="glass-table">
        <el-table-column prop="patient_no" label="患者编号" width="130" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column label="性别" width="80">
          <template #default="{ row }">
            <span class="gender-badge" :class="row.gender">
              {{ row.gender === 'male' ? '男' : row.gender === 'female' ? '女' : '未知' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" width="70">
          <template #default="{ row }">{{ row.age != null ? row.age + '岁' : '-' }}</template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="blood_type" label="血型" width="70" />
        <el-table-column prop="medical_history" label="既往病史" min-width="160" show-overflow-tooltip />
        <el-table-column prop="allergy_history" label="过敏史" min-width="120" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" class="action-link" @click="openDialog('edit', row)">编辑</el-button>
            <el-popconfirm title="确定删除此患者？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small" class="action-link">删除</el-button>
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
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增患者' : '编辑患者'" width="550px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="80px" size="default">
        <el-form-item label="患者编号" prop="patient_no">
          <el-input v-model="formData.patient_no" placeholder="请输入患者编号" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="formData.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="formData.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="formData.phone" placeholder="联系电话" />
        </el-form-item>
        <el-form-item label="血型">
          <el-select v-model="formData.blood_type" style="width: 120px" clearable>
            <el-option label="A型" value="A" />
            <el-option label="B型" value="B" />
            <el-option label="AB型" value="AB" />
            <el-option label="O型" value="O" />
          </el-select>
        </el-form-item>
        <el-form-item label="既往病史">
          <el-input v-model="formData.medical_history" type="textarea" :rows="2" placeholder="既往病史" />
        </el-form-item>
        <el-form-item label="过敏史">
          <el-input v-model="formData.allergy_history" placeholder="过敏史" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getPatientsApi, createPatientApi, updatePatientApi, deletePatientApi } from '@/api/patients'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref<any[]>([])
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editId = ref<number | null>(null)
const formRef = ref<any>(null)

const filters = reactive({ keyword: '', gender: '' })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const formData = reactive({
  patient_no: '', name: '', gender: 'male', age: undefined as number | undefined,
  phone: '', blood_type: '', medical_history: '', allergy_history: '',
})

const formRules = {
  patient_no: [{ required: true, message: '请输入患者编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
}

function defaultForm() {
  return { patient_no: '', name: '', gender: 'male', age: undefined, phone: '', blood_type: '', medical_history: '', allergy_history: '' }
}

async function fetchData() {
  loading.value = true
  try {
    const params: any = { page: pagination.page, per_page: pagination.per_page }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.gender) params.gender = filters.gender
    const res: any = await getPatientsApi(params)
    tableData.value = res.data.items
    pagination.total = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

function search() { pagination.page = 1; fetchData() }
function resetFilters() { filters.keyword = ''; filters.gender = ''; search() }

function openDialog(mode: 'create' | 'edit', row?: any) {
  dialogMode.value = mode
  editId.value = row?.id || null
  if (mode === 'edit' && row) {
    Object.assign(formData, {
      patient_no: row.patient_no,
      name: row.name,
      gender: row.gender || 'male',
      age: row.age,
      phone: row.phone || '',
      blood_type: row.blood_type || '',
      medical_history: row.medical_history || '',
      allergy_history: row.allergy_history || '',
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
      await createPatientApi(formData)
      ElMessage.success('患者创建成功')
    } else {
      await updatePatientApi(editId.value!, formData)
      ElMessage.success('更新成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch { /* handled */ } finally { submitting.value = false }
}

async function handleDelete(row: any) {
  try {
    await deletePatientApi(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* handled */ }
}

onMounted(() => fetchData())
</script>

<style scoped lang="scss">
.patients-page {
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
        width: 260px;
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

  // 性别徽标
  .gender-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 3px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    min-width: 40px;

    &.male { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }
    &.female { background: rgba(244, 114, 182, 0.15); color: #F472B6; }
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
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
      &:has(.gender-badge) {
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
