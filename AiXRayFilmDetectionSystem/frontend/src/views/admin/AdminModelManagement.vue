<template>
  <div class="admin-model-management">
    <!-- 顶部 -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">模型管理</h2>
        <p class="page-desc">管理AI模型文件、切换模型版本、调整推理参数</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showUploadDialog" :icon="Upload">上传模型</el-button>
        <el-button @click="fetchData" :icon="Refresh" :loading="loading">刷新</el-button>
      </div>
    </div>

    <!-- 模型状态卡片 -->
    <div class="status-grid">
      <div class="glass-card status-card">
        <div class="status-icon" :class="{ active: modelStatus.model_loaded }">
          <el-icon :size="28"><Cpu /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">模型状态</div>
          <div class="status-value">
            <el-tag :type="modelStatus.model_loaded ? 'success' : 'danger'" effect="dark" size="small">
              {{ modelStatus.model_loaded ? '已加载' : '未加载' }}
            </el-tag>
          </div>
        </div>
      </div>
      <div class="glass-card status-card">
        <div class="status-icon gpu">
          <el-icon :size="28"><Monitor /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">计算设备</div>
          <div class="status-value">{{ formatDevice(modelStatus.device) }}</div>
        </div>
      </div>
      <div class="glass-card status-card">
        <div class="status-icon arch">
          <el-icon :size="28"><Grid /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">模型架构</div>
          <div class="status-value">{{ modelStatus.architecture }}</div>
        </div>
      </div>
      <div class="glass-card status-card">
        <div class="status-icon size">
          <el-icon :size="28"><PictureFilled /></el-icon>
        </div>
        <div class="status-info">
          <div class="status-label">推理模式</div>
          <div class="status-value">
            <el-tag :type="modelStatus.inference_mode === 'ONNX' ? 'success' : 'primary'" size="small" effect="plain">
              {{ modelStatus.inference_mode || 'PyTorch' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <!-- 模型文件列表 -->
      <div class="glass-card models-panel">
        <div class="panel-header">
          <h3 class="panel-title">可用模型文件</h3>
          <span class="panel-count">{{ models.length }} 个文件</span>
        </div>
        <div class="models-list" v-loading="loading">
          <div v-if="models.length === 0 && !loading" class="empty-hint">暂无模型文件</div>
          <div v-for="m in models" :key="m.filename" class="model-item" :class="{ active: m.is_active }">
            <div class="model-icon">
              <el-icon :size="22"><Document /></el-icon>
            </div>
            <div class="model-info">
              <div class="model-name">{{ m.filename }}</div>
              <div class="model-meta">
                <el-tag :type="formatTagType(m.format)" size="small" effect="light">{{ m.format.toUpperCase() }}</el-tag>
                <span class="model-size">{{ m.size_mb }} MB</span>
              </div>
            </div>
            <div class="model-actions">
              <el-tag v-if="m.is_active" type="success" size="small" effect="dark">当前使用</el-tag>
              <el-button v-else type="primary" link size="small" @click="handleSwitch(m)">
                <el-icon><Switch /></el-icon> 切换
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 核心 ML 参数配置 -->
      <div class="glass-card params-panel">
        <div class="panel-header">
          <h3 class="panel-title">核心 ML 参数配置</h3>
          <el-button link type="danger" size="small" @click="handleResetParams" :loading="resetting">
            <el-icon><RefreshLeft /></el-icon> 恢复默认
          </el-button>
        </div>
        <div class="params-form">
          <!-- 置信度阈值 -->
          <div class="param-group">
            <label class="param-label">置信度阈值</label>
            <div class="param-control">
              <el-slider v-model="paramsForm.confidence_threshold" :min="0" :max="1" :step="0.05"
                :format-tooltip="(v) => `${(v * 100).toFixed(0)}%`" />
              <span class="param-value">{{ (paramsForm.confidence_threshold * 100).toFixed(0) }}%</span>
            </div>
            <p class="param-desc">低于此阈值的诊断结果将标记为低置信度</p>
          </div>

          <!-- 图像输入尺寸 -->
          <div class="param-group">
            <label class="param-label">图像输入尺寸</label>
            <div class="param-control">
              <el-select v-model="paramsForm.image_size" style="width: 160px">
                <el-option v-for="s in imageSizes" :key="s" :label="`${s}x${s}`" :value="s" />
              </el-select>
              <span class="param-value">像素</span>
            </div>
            <p class="param-desc">模型输入图像尺寸，修改后将重建预处理管道</p>
          </div>

          <!-- 分类数量（只读） -->
          <div class="param-group">
            <label class="param-label">分类数量</label>
            <div class="param-control readonly-field">
              <div class="readonly-value">3 类</div>
              <el-tag type="info" size="small" effect="plain">只读</el-tag>
            </div>
            <p class="param-desc">模型输出分类数量（固定为3类：正常、肺炎、肺结核）</p>
          </div>

          <!-- Dropout 比例 -->
          <div class="param-group">
            <label class="param-label">Dropout 比例</label>
            <div class="param-control">
              <el-slider v-model="paramsForm.dropout_rate" :min="0" :max="1" :step="0.05"
                :format-tooltip="(v) => `${(v * 100).toFixed(0)}%`" />
              <span class="param-value">{{ (paramsForm.dropout_rate * 100).toFixed(0) }}%</span>
            </div>
            <p class="param-desc">全连接层 Dropout 比例，防止过拟合</p>
          </div>

          <!-- 热力图尺寸 -->
          <div class="param-group">
            <label class="param-label">热力图输出尺寸</label>
            <div class="param-control">
              <el-select v-model="paramsForm.heatmap_size" style="width: 160px">
                <el-option :label="`${s}x${s}`" :value="s" v-for="s in [256, 512, 768, 1024, 1536, 2048]" :key="s" />
              </el-select>
              <span class="param-value">像素</span>
            </div>
            <p class="param-desc">Grad-CAM 热力图输出分辨率</p>
          </div>

          <!-- 热力图叠加透明度 -->
          <div class="param-group">
            <label class="param-label">热力图叠加透明度</label>
            <div class="param-control">
              <div class="alpha-inputs">
                <div class="alpha-item">
                  <span class="alpha-label">原图</span>
                  <el-slider v-model="paramsForm.gradcam_alpha" :min="0" :max="1" :step="0.05" style="width:120px"
                    :format-tooltip="(v) => (v * 100).toFixed(0) + '%'" />
                </div>
                <div class="alpha-item">
                  <span class="alpha-label">热力图</span>
                  <el-slider v-model="paramsForm.gradcam_beta" :min="0" :max="1" :step="0.05" style="width:120px"
                    :format-tooltip="(v) => (v * 100).toFixed(0) + '%'" />
                </div>
              </div>
            </div>
            <p class="param-desc">Grad-CAM 热力图与原图的叠加权重比例</p>
          </div>

          <!-- 分类类别（只读） -->
          <div class="param-group">
            <label class="param-label">分类类别</label>
            <div class="class-tags">
              <el-tag v-for="cls in modelStatus.classes" :key="cls" size="small" effect="plain">{{ cls }}</el-tag>
            </div>
          </div>

          <!-- GPU 信息（只读） -->
          <div class="param-group" v-if="modelStatus.gpu_available">
            <label class="param-label">GPU 信息</label>
            <div class="gpu-info">
              <span>{{ modelStatus.gpu_name }}</span>
              <span class="gpu-mem">{{ modelStatus.gpu_memory_gb }} GB</span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="param-actions">
            <el-button type="primary" @click="handleUpdateParams" :loading="savingParams">
              <el-icon><Check /></el-icon> 保存参数配置
            </el-button>
            <el-button @click="handleResetParams" :loading="resetting">
              <el-icon><RefreshLeft /></el-icon> 恢复默认值
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传模型文件" width="650px" destroy-on-close
               class="dark-dialog">
      <el-form label-width="100px">
        <el-form-item label="模型文件">
          <el-upload ref="uploadRef" drag :auto-upload="false" :limit="1"
            :accept="'.pth,.pt,.onnx,.pkl,.bin'"
            :on-change="onFileChange" :on-remove="onFileRemove">
            <div class="upload-area" v-if="!uploadFile">
              <el-icon :size="40"><UploadFilled /></el-icon>
              <div class="upload-text">将模型文件拖到此处，或<em>点击上传</em></div>
              <div class="upload-hint">支持 .pth / .pt / .onnx / .pkl / .bin 格式</div>
            </div>
            <div class="upload-area uploaded" v-else>
              <el-icon :size="36" color="#10B981"><CircleCheckFilled /></el-icon>
              <div class="upload-text">已选择文件，可拖入新文件替换</div>
              <div class="upload-hint">{{ uploadFileName }}</div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading" :disabled="!uploadFile">
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { systemApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Refresh, UploadFilled, CircleCheckFilled, Cpu, Monitor, Grid, PictureFilled, Document, Switch, RefreshLeft } from '@element-plus/icons-vue'

const loading = ref(false)
const savingParams = ref(false)
const resetting = ref(false)
const uploading = ref(false)
const uploadDialogVisible = ref(false)
const uploadFile = ref(null)
const uploadFileName = ref('')
const models = ref([])
const modelStatus = ref({})

const imageSizes = [128, 224, 256, 299, 384, 512, 1024]

// 核心 ML 参数（含热力图参数）
const paramsForm = reactive({
  confidence_threshold: 0.5,
  image_size: 1024,
  num_classes: 3,
  dropout_rate: 0.2,
  heatmap_size: 1024,
  gradcam_alpha: 0.4,
  gradcam_beta: 0.6,
})

function formatTagType(fmt) {
  const map = { pth: 'primary', pt: 'primary', onnx: 'success', pkl: 'warning', bin: 'info' }
  return map[fmt] || 'info'
}

// 格式化设备名称为大写
function formatDevice(device) {
  if (!device) return 'N/A'
  const deviceStr = String(device).toLowerCase()
  if (deviceStr.includes('cuda')) return 'GPU'
  if (deviceStr.includes('cpu')) return 'CPU'
  return device.toUpperCase()
}

async function fetchData() {
  loading.value = true
  try {
    const res = await systemApi.listModels()
    models.value = res.data.models || []
    const status = res.data.status || {}
    modelStatus.value = status
    // 从 params 子对象恢复（持久化参数）
    if (status.params) {
      Object.assign(paramsForm, status.params)
    } else {
      paramsForm.confidence_threshold = status.confidence_threshold || 0.5
      paramsForm.image_size = status.image_size || 224
    }
  } catch (e) { /* handled by interceptor */ }
  finally { loading.value = false }
}

async function handleSwitch(m) {
  try {
    await ElMessageBox.confirm(
      `确定切换到模型 "${m.filename}" 吗？切换期间将暂停诊断服务。`,
      '切换模型',
      { confirmButtonText: '确定切换', cancelButtonText: '取消', type: 'warning' }
    )
    loading.value = true
    await systemApi.switchModel({ filename: m.filename })
    ElMessage.success('模型切换成功')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') { /* handled */ }
    loading.value = false
  }
}

async function handleUpdateParams() {
  savingParams.value = true
  try {
    await systemApi.updateModelParams(paramsForm)
    ElMessage.success('参数保存成功')
    fetchData()
  } catch (e) { /* handled */ }
  finally { savingParams.value = false }
}

async function handleResetParams() {
  try {
    await ElMessageBox.confirm(
      '确定将所有模型参数恢复为默认值吗？',
      '恢复默认参数',
      { confirmButtonText: '确定恢复', cancelButtonText: '取消', type: 'warning' }
    )
    resetting.value = true
    await systemApi.resetModelParams()
    ElMessage.success('参数已恢复为默认值')
    fetchData()
  } catch (e) {
    if (e !== 'cancel') { /* handled */ }
  } finally { resetting.value = false }
}

function showUploadDialog() {
  uploadFile.value = null
  uploadFileName.value = ''
  uploadDialogVisible.value = true
}

function onFileChange(file) {
  uploadFile.value = file.raw
  uploadFileName.value = file.name
}

function onFileRemove() {
  uploadFile.value = null
  uploadFileName.value = ''
}

async function handleUpload() {
  if (!uploadFile.value) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadFile.value)
    await systemApi.uploadModel(formData)
    ElMessage.success('模型上传成功')
    uploadDialogVisible.value = false
    fetchData()
  } catch (e) { /* handled */ }
  finally { uploading.value = false }
}

onMounted(() => { fetchData() })
</script>

<style scoped lang="scss">
.admin-model-management {
  .page-header {
    display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px;
    .header-info { .page-title { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; } .page-desc { color: var(--text-muted); font-size: 13px; } }
    .header-actions { display: flex; gap: 10px; }
  }

  .status-grid {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px;
  }

  .status-card {
    display: flex; align-items: center; gap: 14px; padding: 18px 20px;
    .status-icon {
      width: 48px; height: 48px; border-radius: var(--radius-md);
      display: flex; align-items: center; justify-content: center;
      background: rgba(139, 92, 246, 0.15); color: #8B5CF6; flex-shrink: 0;
      &.active { background: rgba(16, 185, 129, 0.15); color: #10B981; }
      &.gpu { background: rgba(59, 130, 246, 0.15); color: #3B82F6; }
      &.arch { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }
      &.size { background: rgba(236, 72, 153, 0.15); color: #EC4899; }
    }
    .status-label { font-size: 12px; color: var(--text-muted); margin-bottom: 4px; }
    .status-value { font-size: 15px; font-weight: 600; color: var(--text-primary); }
  }

  .content-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  }

  .panel-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 16px; border-bottom: 1px solid var(--glass-border); margin-bottom: 16px;
    .panel-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }
    .panel-count { font-size: 12px; color: var(--text-muted); background: var(--glass-bg); padding: 2px 10px; border-radius: 10px; }
  }

  .models-list { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }
  .empty-hint { text-align: center; color: var(--text-muted); padding: 40px 0; }

  .model-item {
    display: flex; align-items: center; gap: 14px; padding: 14px 16px;
    border-radius: var(--radius-md); border: 1px solid transparent;
    transition: all var(--transition-normal); cursor: default;
    &:hover { background: var(--glass-bg); border-color: var(--glass-border); }
    &.active { background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.3); }
    .model-icon { width: 40px; height: 40px; border-radius: var(--radius-sm); background: var(--glass-bg); display: flex; align-items: center; justify-content: center; color: var(--text-secondary); flex-shrink: 0; }
    .model-name { font-size: 14px; font-weight: 500; color: var(--text-primary); margin-bottom: 4px; }
    .model-meta { display: flex; align-items: center; gap: 8px; }
    .model-size { font-size: 12px; color: var(--text-muted); }
    .model-info { flex: 1; min-width: 0; }
    .model-actions { flex-shrink: 0; }
  }

  .params-form { display: flex; flex-direction: column; gap: 22px; }
  .param-label { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 10px; display: block; }
  .param-control { display: flex; align-items: center; gap: 12px; }
  .param-value { font-size: 13px; color: var(--text-secondary); font-weight: 500; min-width: 40px; text-align: right; }
  .param-desc { font-size: 12px; color: var(--text-muted); margin-top: 6px; }
  .class-tags { display: flex; gap: 8px; flex-wrap: wrap; }
  .gpu-info { display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--text-secondary); .gpu-mem { color: var(--text-primary); font-weight: 500; } }

  .param-actions {
    display: flex; gap: 12px; padding-top: 8px; border-top: 1px solid var(--glass-border);
  }

  .readonly-field {
    display: flex;
    align-items: center;
    gap: 12px;
    .readonly-value {
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      padding: 8px 16px;
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);
      min-width: 80px;
      text-align: center;
    }
  }

  .alpha-inputs {
    display: flex; flex-direction: column; gap: 8px;
    .alpha-item {
      display: flex; align-items: center; gap: 8px;
      .alpha-label { font-size: 12px; color: var(--text-secondary); min-width: 48px; }
    }
  }
}

.upload-area { text-align: center; padding: 20px; .upload-text { margin-top: 8px; font-size: 14px; color: var(--text-secondary); em { color: #EF4444; font-style: normal; } } .upload-hint { font-size: 12px; color: var(--text-muted); margin-top: 4px; } }

// 暗色对话框样式
:deep(.dark-dialog) {
  .el-dialog {
    background: var(--card-bg) !important;
    border: 1px solid var(--glass-border) !important;
  }
  .el-dialog__header {
    background: var(--glass-bg) !important;
    border-bottom: 1px solid var(--glass-border) !important;
    padding: 16px 20px !important;
    .el-dialog__title {
      color: var(--text-primary) !important;
      font-weight: 600 !important;
    }
  }
  .el-dialog__body {
    background: var(--card-bg) !important;
    color: var(--text-primary) !important;
    padding: 20px !important;
  }
  .el-dialog__footer {
    background: var(--glass-bg) !important;
    border-top: 1px solid var(--glass-border) !important;
    padding: 16px 20px !important;
  }
  .el-form-item__label {
    color: var(--text-secondary) !important;
  }
}

  :deep(.el-form-item__content) { display: block !important; }
  :deep(.el-upload) { width: 100%; }
  :deep(.el-upload-dragger) {
    width: 100% !important;
    background: rgba(30, 41, 59, 0.6) !important;
    border: 2px dashed rgba(239, 68, 68, 0.3) !important;
    border-radius: var(--radius-md) !important;
    transition: all var(--transition-normal) !important;
    &:hover { border-color: rgba(239, 68, 68, 0.5) !important; background: rgba(239, 68, 68, 0.05) !important; }
    .el-icon--upload { color: #EF4444 !important; }
  }
  :deep(.el-upload-list) {
    background: var(--card-bg); border-radius: var(--radius-sm); padding: 8px;
    .el-upload-list__item { background: var(--glass-bg); border-radius: var(--radius-sm); color: var(--text-primary); &:hover { background: var(--glass-bg-hover); }
      .el-icon--close { color: var(--text-secondary); &:hover { color: #EF4444; } }
    }
  }
</style>
