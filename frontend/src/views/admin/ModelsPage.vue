/** 管理员-权重文件管理页面 */
<template>
  <div class="models-page">
    <div class="glass-card">
      <!-- 搜索筛选栏 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="版本号/架构/数据集" clearable @keyup.enter="search"
            class="filter-input">
            <template #prefix><el-icon>
                <Search />
              </el-icon></template>
          </el-input>
        </div>
        <div class="filter-item">
          <el-select v-model="filters.status" placeholder="状态" clearable>
            <el-option label="已激活" value="active" />
            <el-option label="未激活" value="inactive" />
          </el-select>
        </div>
        <div class="filter-actions">
          <el-button type="primary" @click="search">
            <el-icon>
              <Search />
            </el-icon> 搜索
          </el-button>
          <el-button @click="resetFilters">
            <el-icon>
              <Refresh />
            </el-icon> 重置
          </el-button>
        </div>
        <div class="filter-actions" style="margin-left: auto;">
          <el-button type="primary" @click="openUploadDialog">
            <el-icon>
              <Upload />
            </el-icon> 上传权重
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table :data="filteredWeights" v-loading="loading" empty-text="暂无权重文件" class="glass-table">
        <el-table-column prop="version_name" label="版本号" width="250" />
        <el-table-column prop="architecture" label="架构" width="130">
          <template #default="{ row }">
            <span class="arch-badge">{{ row.architecture || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="training_dataset" label="训练数据集" min-width="160" show-overflow-tooltip />
        <el-table-column label="文件" width="120">
          <template #default="{ row }">
            <div class="file-info">
              <span class="file-ext" :class="getFileExt(row.file_path)">{{ getFileExt(row.file_path) }}</span>
              <span class="file-size">{{ formatSize(row.file_size) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="性能指标" min-width="180">
          <template #default="{ row }">
            <div v-if="row.metrics" class="metrics-cell">
              <span v-for="(val, key) in row.metrics" :key="key" class="metric-tag">
                {{ key }}: {{ typeof val === 'number' ? val.toFixed(4) : val }}
              </span>
            </div>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="status-dot" :class="row.is_active ? 'active' : 'inactive'"></span>
            <span class="status-text">{{ row.is_active ? '已激活' : '未激活' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="uploaded_at" label="上传时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" class="action-link" :disabled="row.is_active"
              @click="handleActivate(row)">激活</el-button>
            <el-button type="primary" link size="small" class="action-link"
              @click="openDetailDialog(row)">详情</el-button>
            <el-popconfirm title="确定删除此权重文件？" @confirm="handleDelete(row)">
              <template #reference>
                <el-button type="danger" link size="small" class="action-link" :disabled="row.is_active">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="showUpload" title="上传模型权重" width="540px">
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="90px" size="default">
        <el-form-item label="版本号" prop="version_name">
          <el-input v-model="uploadForm.version_name" placeholder="如 v2.1.0" />
        </el-form-item>
        <el-form-item label="架构">
          <el-input v-model="uploadForm.architecture" placeholder="如 DenseNet-121" />
        </el-form-item>
        <el-form-item label="训练数据集">
          <el-input v-model="uploadForm.training_dataset" placeholder="如 NIH ChestX-ray14" />
        </el-form-item>
        <el-form-item label="权重文件" required>
          <el-upload ref="uploadRef" :auto-upload="false" :limit="1" accept=".pth,.pt,.onnx"
            :on-change="handleFileChange" :on-remove="handleFileRemove">
            <el-button>选择文件</el-button>
            <template #tip>
              <div class="upload-tip">支持 .pth / .pt / .onnx 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="性能指标">
          <el-input v-model="uploadForm.metrics" placeholder='如 {"auc": 0.85, "f1": 0.82}' />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUpload = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="showDetail" title="权重文件详情" width="550px">
      <el-descriptions :column="2" border size="default" v-if="detailRow">
        <el-descriptions-item label="版本号">{{ detailRow.version_name }}</el-descriptions-item>
        <el-descriptions-item label="架构">{{ detailRow.architecture || '-' }}</el-descriptions-item>
        <el-descriptions-item label="训练数据集">{{ detailRow.training_dataset || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <span class="status-dot" :class="detailRow.is_active ? 'active' : 'inactive'"></span>
          {{ detailRow.is_active ? '已激活' : '未激活' }}
        </el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatSize(detailRow.file_size) }}</el-descriptions-item>
        <el-descriptions-item label="文件格式">{{ getFileExt(detailRow.file_path)?.toUpperCase() || '-'
        }}</el-descriptions-item>
        <el-descriptions-item label="文件哈希" :span="2">
          <span class="hash-text">{{ detailRow.file_hash || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="性能指标" :span="2">
          <div v-if="detailRow.metrics" class="metrics-cell">
            <span v-for="(val, key) in detailRow.metrics" :key="key" class="metric-tag">
              {{ key }}: {{ typeof val === 'number' ? val.toFixed(4) : val }}
            </span>
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ detailRow.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="上传时间" :span="2">{{ detailRow.uploaded_at || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetail = false">关闭</el-button>
        <el-button type="primary" :disabled="detailRow?.is_active"
          @click="handleActivate(detailRow); showDetail = false">激活此版本</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Upload } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import {
  getModelWeightsApi, uploadModelWeightApi, activateModelWeightApi,
  deleteModelWeightApi,
} from '@/api/model-weights'

const loading = ref(false)
const uploading = ref(false)
const weights = ref<any[]>([])
const showUpload = ref(false)
const showDetail = ref(false)
const detailRow = ref<any>(null)
const selectedFile = ref<File | null>(null)
const uploadFormRef = ref<any>(null)

const filters = reactive({ keyword: '', status: '' })
const uploadForm = reactive({
  version_name: '', architecture: 'DenseNet-121', training_dataset: 'NIH ChestX-ray14',
  metrics: '', description: '',
})

const uploadRules = {
  version_name: [{ required: true, message: '请输入版本号', trigger: 'blur' }],
}

const filteredWeights = computed(() => {
  let list = weights.value
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase()
    list = list.filter(w =>
      w.version_name?.toLowerCase().includes(kw) ||
      w.architecture?.toLowerCase().includes(kw) ||
      w.training_dataset?.toLowerCase().includes(kw)
    )
  }
  if (filters.status === 'active') {
    list = list.filter(w => w.is_active)
  } else if (filters.status === 'inactive') {
    list = list.filter(w => !w.is_active)
  }
  return list
})

function formatSize(bytes: number | null | undefined) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileExt(path: string | null | undefined) {
  if (!path) return ''
  const parts = path.split('.')
  const ext = parts.length > 1 ? parts.pop() : ''
  return ext?.toLowerCase() || ''
}

function handleFileChange(file: UploadFile) { if (file.raw) selectedFile.value = file.raw }
function handleFileRemove() { selectedFile.value = null }

function openUploadDialog() {
  Object.assign(uploadForm, {
    version_name: '', architecture: 'DenseNet-121', training_dataset: 'NIH ChestX-ray14',
    metrics: '', description: '',
  })
  selectedFile.value = null
  showUpload.value = true
}

function openDetailDialog(row: any) {
  detailRow.value = row
  showDetail.value = true
}

async function loadWeights() {
  loading.value = true
  try {
    const res: any = await getModelWeightsApi()
    weights.value = res.data
  } catch { /* handled */ } finally { loading.value = false }
}

function search() { /* filteredWeights is computed */ }
function resetFilters() { filters.keyword = ''; filters.status = '' }

async function handleUpload() {
  try {
    await uploadFormRef.value?.validate()
  } catch { return }
  if (!selectedFile.value) { ElMessage.warning('请选择权重文件'); return }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    Object.entries(uploadForm).forEach(([k, v]) => { if (v) formData.append(k, v) })
    await uploadModelWeightApi(formData)
    ElMessage.success('上传成功')
    showUpload.value = false
    loadWeights()
  } catch { /* handled */ } finally { uploading.value = false }
}

async function handleActivate(w: any) {
  if (!w || w.is_active) return
  try {
    await activateModelWeightApi(w.id)
    ElMessage.success('模型已激活')
    loadWeights()
  } catch { /* handled */ }
}

async function handleDelete(w: any) {
  try {
    await deleteModelWeightApi(w.id)
    ElMessage.success('删除成功')
    loadWeights()
  } catch { /* handled */ }
}

onMounted(() => loadWeights())
</script>

<style scoped lang="scss">
.models-page {

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
        width: 240px;
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

  // 架构徽标
  .arch-badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 600;
    background: rgba(139, 92, 246, 0.12);
    color: #A78BFA;
  }

  // 文件信息
  .file-info {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .file-ext {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: fit-content;
      padding: 1px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;

      &.pth {
        background: rgba(34, 211, 238, 0.15);
        color: var(--primary);
      }

      &.pt {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
      }

      &.onnx {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
      }
    }

    .file-size {
      font-size: 11px;
      color: var(--text-muted);
    }
  }

  // 指标标签
  .metrics-cell {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .metric-tag {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 500;
    background: rgba(34, 211, 238, 0.12);
    color: var(--primary);
  }

  .text-muted {
    color: var(--text-muted);
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

  // 详情对话框
  .hash-text {
    font-family: monospace;
    font-size: 12px;
    word-break: break-all;
    color: var(--text-secondary);
  }

  // 上传提示
  .upload-tip {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
  }

  // 表格
  :deep(.el-table__cell) {
    display: table-cell !important;
    vertical-align: middle !important;
    text-align: center !important;
  }

  :deep(.el-table__header th .cell) {
    justify-content: center;
  }

  :deep(.el-table__body tr td) {
    .cell {

      &:has(.arch-badge),
      &:has(.status-dot),
      &:has(.file-info),
      &:has(.metrics-cell) {
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
  }
}


:deep(.el-table__body tr td) {
  .cell {

    &:has(.arch-badge),
    &:has(.status-dot),
    &:has(.file-info) {
      justify-content: center;
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
