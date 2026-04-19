/** 批量诊断页面 - 选择图片→自动关联患者→异步批量检测→生成报告 */
<template>
  <div class="batch-page">
    <!-- 流程步骤 -->
    <div class="flow-steps">
      <div class="step" :class="{ active: currentStep >= 1, done: currentStep > 1 }">
        <div class="step-dot"><span>1</span></div>
        <div class="step-info">
          <span class="step-title">选择影像</span>
          <span class="step-desc">上传并关联患者</span>
        </div>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
      <div class="step" :class="{ active: currentStep >= 2, done: currentStep > 2 }">
        <div class="step-dot"><span>2</span></div>
        <div class="step-info">
          <span class="step-title">AI检测</span>
          <span class="step-desc">批量智能分析</span>
        </div>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
      <div class="step" :class="{ active: currentStep >= 3 }">
        <div class="step-dot"><span>3</span></div>
        <div class="step-info">
          <span class="step-title">报告生成</span>
          <span class="step-desc">查看结果与报告</span>
        </div>
      </div>
    </div>

    <!-- 顶部操作栏（检测完成后显示全部清空） -->
    <div v-if="(imageItems.length > 0 || diagnoses.length > 0) && !diagnosing" class="top-actions">
      <el-button type="danger" plain @click="resetAll">
        <el-icon>
          <Delete />
        </el-icon> 全部清空
      </el-button>
    </div>

    <!-- ===== 第一步：选择影像（有诊断结果后隐藏）===== -->
    <div class="zone-card" :class="{ active: currentStep === 1 && !diagnosing }" v-if="diagnoses.length === 0">
      <div class="zone-header">
        <div class="zone-badge">
          <el-icon>
            <Upload />
          </el-icon>
        </div>
        <div class="zone-title-group">
          <h3 class="zone-title">选择影像</h3>
          <span class="zone-subtitle">Select Images</span>
        </div>
        <div class="zone-status">
          <el-tag :type="imageItems.length > 0 ? 'success' : 'info'" size="small">
            {{ imageItems.length > 0 ? `已选 ${imageItems.length} 张` : '待选择' }}
          </el-tag>
        </div>
      </div>
      <div class="zone-body">
        <!-- 上传区域 - 有图片后隐藏 -->
        <el-upload v-if="imageItems.length === 0" drag multiple :auto-upload="false" accept=".png,.jpg,.jpeg,.dcm"
          :on-change="handleFilesChange" :show-file-list="false" ref="uploadRef">
          <div class="upload-placeholder">
            <el-icon class="upload-icon" :size="40">
              <Upload />
            </el-icon>
            <div class="upload-text">拖拽或点击选择X光影像文件</div>
            <div class="upload-hint">支持 <em>PNG / JPG / JPEG / DCM</em>，可多选或选择整个文件夹</div>
            <div class="upload-hint" style="margin-top: 4px;">
              文件名格式: <em>P患者ID-姓名-性别-年龄-临床发现-图片ID.扩展名</em>
            </div>
          </div>
        </el-upload>

        <!-- 图片列表 - 两列网格，左图右信息 -->
        <div v-if="imageItems.length > 0" class="image-grid">
          <div v-for="(item, idx) in imageItems" :key="idx" class="image-card">
            <el-button class="image-card-close" type="danger" :icon="Close" circle size="small" @click="removeImage(idx)" />
            <div class="image-card-left">
              <img v-if="item.previewUrl" :src="item.previewUrl" class="image-thumb" />
              <div v-else class="image-thumb-placeholder">
                <el-icon :size="24">
                  <Upload />
                </el-icon>
              </div>
              <el-button class="image-card-del" type="danger" link size="small" @click="removeImage(idx)">
                <el-icon>
                  <Delete />
                </el-icon>
              </el-button>
            </div>
            <div class="image-card-right">
              <div class="image-card-name" :title="item.filename">{{ item.filename }}</div>
              <div class="image-card-meta">
                <span>{{ item.fileSize }}</span>
                <span class="meta-sep">|</span>
                <span>{{ item.fileType }}</span>
              </div>
              <div v-if="item.parsedInfo" class="patient-auto">
                <div class="patient-auto-row">
                  <span class="patient-avatar">{{ item.parsedInfo.name?.charAt(0) || '?' }}</span>
                  <span class="patient-name">{{ item.parsedInfo.name }}</span>
                  <span class="patient-info">{{ item.parsedInfo.gender === 'male' ? '男' : '女' }} / {{
                    item.parsedInfo.age }}岁</span>
                </div>
                <div class="patient-auto-row secondary">
                  <span class="patient-no">{{ item.parsedInfo.patient_no }}</span>
                  <span v-if="item.parsedInfo.finding_zh" class="patient-finding">{{ item.parsedInfo.finding_zh
                  }}</span>
                  <span class="patient-imgid">图片#{{ item.parsedInfo.image_id }}</span>
                </div>
                <div v-if="item.patientId" class="patient-matched">
                  <el-icon>
                    <CircleCheckFilled />
                  </el-icon> 已匹配患者
                </div>
                <div v-else class="patient-unmatched">
                  <el-icon>
                    <WarningFilled />
                  </el-icon> 新患者，检测时自动创建
                </div>
              </div>
              <div v-else class="patient-manual">
                <el-select v-model="item.patientId" placeholder="选择关联患者" filterable clearable size="small"
                  style="width: 100%;">
                  <el-option v-for="p in patientList" :key="p.id" :label="`${p.patient_no} - ${p.name}`"
                    :value="p.id" />
                </el-select>
                <el-button type="primary" link size="small" class="action-link" @click="openNewPatientDialog(idx)"
                  style="margin-top: 4px;">
                  <el-icon>
                    <Plus />
                  </el-icon> 新建患者
                </el-button>
              </div>
              <div class="clinical-finding">
                <el-input v-model="item.clinicalFinding" placeholder="临床症状，如：咳嗽、胸痛、发热" size="small" />
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="upload-actions">
          <el-button v-if="!diagnosing && imageItems.length > 0" @click="triggerAddImages">
            <el-icon><Plus /></el-icon> 继续添加
          </el-button>
          <el-button v-if="!diagnosing" type="primary" :disabled="hasNoRealFiles" @click="startDiagnosis">
            <el-icon><Cpu /></el-icon> 开始检测 ({{ imageItems.length }}张)
          </el-button>
          <el-button v-else type="danger" @click="stopDiagnosis">
            <el-icon><VideoPause /></el-icon> 停止检测
          </el-button>
          <el-button v-if="!diagnosing && imageItems.length > 0" type="danger" plain @click="imageItems = []">
            <el-icon><Delete /></el-icon> 清空
          </el-button>
        </div>
      </div>
    </div>

    <!-- 隐藏的继续添加上传 -->
    <el-upload v-show="false" multiple :auto-upload="false" accept=".png,.jpg,.jpeg,.dcm" :on-change="handleFilesChange"
      :show-file-list="false" ref="uploadRefHidden" />

    <!-- ===== 第二步：检测中/检测结果 ===== -->
    <div v-if="diagnosing || diagnoses.length > 0" class="zone-card">
      <div class="zone-header">
        <div class="zone-badge result-badge">
          <el-icon>
            <Cpu />
          </el-icon>
        </div>
        <div class="zone-title-group">
          <h3 class="zone-title">检测结果</h3>
          <span class="zone-subtitle">Results</span>
        </div>
        <div class="zone-status">
          <template v-if="diagnosing">
            <el-tag type="warning" size="small">检测中 {{ completedCount }}/{{ totalDiagnoseCount }}</el-tag>
            <el-button type="danger" size="small" @click="stopDiagnosis" style="margin-left: 8px;">
              <el-icon><VideoPause /></el-icon> 停止检测
            </el-button>
          </template>
          <template v-else>
            <el-tag type="success" size="small">完成 {{ completedCount }}/{{ totalDiagnoseCount }}</el-tag>
            <el-button v-if="diagnoses.length > 0" type="danger" plain size="small" style="margin-left: 8px;" @click="resetAll">
              <el-icon><Delete /></el-icon> 全部清空
            </el-button>
          </template>
        </div>
      </div>
      <div class="zone-body">
        <el-progress v-if="diagnosing" :percentage="progressPercent" :stroke-width="6" style="margin-bottom: 16px;" />
        <div class="result-grid">
          <template v-for="(d, idx) in diagnoses" :key="idx">
            <div v-if="d" class="result-item">
              <div class="result-item-header">
                <div class="result-item-index">{{ idx + 1 }}</div>
                <div class="result-item-info">
                  <span class="result-item-name">{{ d.filename }}</span>
                  <span v-if="d.patientName" class="result-item-patient">{{ d.patientName }}</span>
                </div>
                <div class="result-item-right">
                  <el-tag v-if="d.status === 'diagnosing'" type="warning" size="small">
                    <el-icon class="is-loading">
                      <Loading />
                    </el-icon> 检测中
                  </el-tag>
                  <el-tag v-else-if="d.status === 'reporting'" type="primary" size="small">
                    <el-icon class="is-loading">
                      <Loading />
                    </el-icon> 生成报告中
                  </el-tag>
                  <el-tag v-else-if="d.status === 'done'" type="success" size="small">已完成</el-tag>
                  <el-tag v-else-if="d.status === 'error'" type="danger" size="small">失败</el-tag>
                  <span v-if="d.status === 'reporting' || d.status === 'done'" class="result-badge"
                    :class="d.topResult === 'normal' ? 'normal' : 'abnormal'">
                    {{ d.topResult === 'normal' ? '正常' : d.topResultName }}
                  </span>
                </div>
              </div>
              <!-- 患者/医生信息栏 -->
              <div v-if="(d.status === 'reporting' || d.status === 'done') && d.data" class="result-meta">
                <div class="meta-row">
                  <span class="meta-item" v-if="d.data.patient_name || d.patientName">
                    <el-icon>
                      <User />
                    </el-icon> {{ d.data.patient_name || d.patientName.split('(')[0].trim() }}
                  </span>
                  <span class="meta-item" v-if="displayGender(d)">{{ displayGender(d) === 'male' ? '男' : '女' }}</span>
                  <span class="meta-item" v-if="displayAge(d)">{{ displayAge(d) }}岁</span>
                  <span class="meta-divider"
                    v-if="(d.data.patient_name || d.patientName) || displayGender(d) || displayAge(d)"></span>
                  <span class="meta-item meta-clinical" v-if="d.data.clinical_finding || d.localClinicalFinding">
                    <el-icon>
                      <WarningFilled />
                    </el-icon> {{ d.data.clinical_finding || d.localClinicalFinding }}
                  </span>
                </div>
                <div class="meta-row meta-doctor">
                  <span class="meta-item" v-if="d.data.doctor_name">
                    诊断医生: {{ d.data.doctor_name }}
                    <template v-if="d.data.doctor_department"> ({{ d.data.doctor_department }})</template>
                  </span>
                  <span class="meta-item" v-if="d.data.diagnosed_at">{{ d.data.diagnosed_at }}</span>
                </div>
              </div>
              <!-- 检测结果详情：reporting/done 都显示概率条 -->
              <div v-if="(d.status === 'reporting' || d.status === 'done') && d.data" class="result-detail">
                <div class="result-detail-grid">
                  <div class="result-images">
                    <div v-if="d.previewUrl || d.data.image_url" class="result-thumb-box">
                      <img :src="d.previewUrl || d.data.image_url" class="result-thumb" />
                      <span class="result-thumb-label">原始图</span>
                    </div>
                    <div v-if="d.data.heatmap_url" class="result-thumb-box">
                      <img :src="d.data.heatmap_url" class="result-thumb" />
                      <span class="result-thumb-label">热力图</span>
                    </div>
                  </div>
                  <div class="result-probs">
                    <div v-for="p in d.top5Probs" :key="p.disease_code" class="prob-row">
                      <span class="prob-label">{{ p.disease_name_zh }}</span>
                      <div class="prob-bar-wrap">
                        <div class="prob-bar"
                          :style="{ width: (p.probability * 100) + '%', background: probColor(p.disease_code) }">
                        </div>
                      </div>
                      <span class="prob-val">{{ (p.probability * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- 报告内容：直接显示在该患者卡片下方 -->
              <div v-if="d.status === 'done' && d.reportContent" class="result-report">
                <div class="result-report-header">
                  <span class="result-report-title">
                    <el-icon>
                      <Document />
                    </el-icon> AI诊断报告
                  </span>
                  <el-button type="primary" link size="small" class="action-link"
                    @click="viewReport(d)">打印报告</el-button>
                </div>
                <pre class="result-report-text">{{ d.reportContent }}</pre>
              </div>
              <div v-if="d.status === 'error'" class="result-error">
                <el-icon>
                  <WarningFilled />
                </el-icon> {{ d.errorMsg || '检测失败' }}
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 新建患者对话框 -->
    <el-dialog v-model="newPatientDialogVisible" title="新建患者" width="500px">
      <el-form :model="newPatientForm" label-width="80px" size="default">
        <el-form-item label="患者编号" required>
          <el-input v-model="newPatientForm.patient_no" placeholder="如 P20260315001" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="newPatientForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="newPatientForm.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="年龄">
          <el-input-number v-model="newPatientForm.age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="临床症状">
          <el-input v-model="newPatientForm.finding" placeholder="如 咳嗽、胸痛、发热等" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="newPatientForm.phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="病史">
          <el-input v-model="newPatientForm.medical_history" type="textarea" :rows="2" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newPatientDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createNewPatient" :loading="creatingPatient">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Cpu, Document, Loading, WarningFilled, Plus, Delete, VideoPause, CircleCheckFilled, User, Close } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'
import { batchDiagnoseApi, getBatchProgressApi, cancelBatchApi, batchGenerateReportsApi } from '@/api/batch'
import { regenerateReportApi } from '@/api/reports'
import { getPatientsApi, createPatientApi } from '@/api/patients'

// 文件名解析正则: P患者ID-姓名-性别-年龄-临床发现-图片ID.扩展名
const FILENAME_RE = /^(P\d+)-(.+)-(male|female)-(\d+)-([A-Za-z]+)-(\d+)\.(\w+)$/

const FINDING_ZH: Record<string, string> = {
  Cough: '咳嗽', ChestPain: '胸痛', Fever: '发热',
  Dyspnea: '呼吸困难', Hemoptysis: '咯血', Routine: '体检',
  FollowUp: '复查', Fatigue: '乏力', Wheeze: '喘息', Other: '其他',
}

interface ParsedInfo {
  patient_no: string
  name: string
  gender: string
  age: number
  finding: string
  finding_zh: string
  image_id: string
}

interface ImageItem {
  filename: string
  file: File | null
  previewUrl: string
  fileSize: string
  fileType: string
  patientId: number | null
  parsedInfo: ParsedInfo | null
  clinicalFinding: string
}

interface DiagItem {
  filename: string
  previewUrl: string
  patientId: number | null
  patientName: string
  status: 'diagnosing' | 'reporting' | 'done' | 'error'
  data: any
  topResult: string
  topResultName: string
  top5Probs: any[]
  reportStatus: 'pending' | 'generating' | 'done' | 'error'
  reportContent: string
  errorMsg: string
  // 本地备用患者信息（来自文件名解析，后端数据缺失时使用）
  localGender: string
  localAge: number | null
  localClinicalFinding: string
}

const uploadRef = ref<any>(null)
const uploadRefHidden = ref<any>(null)
const imageItems = ref<ImageItem[]>([])
const patientList = ref<any[]>([])
const diagnosing = ref(false)
const generatingReports = ref(false)
const diagnoses = ref<DiagItem[]>([])
const activeBatchId = ref<number | null>(null)
const newPatientDialogVisible = ref(false)
const creatingPatient = ref(false)
const newPatientTargetIdx = ref<number>(-1)
const newPatientForm = ref({
  patient_no: '',
  name: '',
  gender: 'male',
  age: 30,
  finding: '',
  phone: '',
  medical_history: '',
})
let pollTimer: ReturnType<typeof setInterval> | null = null

const currentStep = computed(() => {
  if (completedDiagnoses.value.some(d => d.reportStatus === 'done')) return 3
  if (diagnoses.value.length > 0) return 2
  if (imageItems.value.length > 0) return 1
  return 0
})

const completedCount = computed(() => diagnoses.value.filter(d => d.status === 'done' || d.status === 'error').length)
const totalDiagnoseCount = computed(() => diagnoses.value.length)
const progressPercent = computed(() => totalDiagnoseCount.value > 0
  ? Math.round((completedCount.value / totalDiagnoseCount.value) * 100) : 0)
const completedDiagnoses = computed(() => diagnoses.value.filter(d => d.status === 'done'))

/** 是否有真实的文件（排除从 localStorage 恢复的空壳数据） */
const hasNoRealFiles = computed(() => imageItems.value.length === 0 || !imageItems.value.some(i => i.file))

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileType(name: string): string {
  const ext = name.split('.').pop()?.toUpperCase() || ''
  return ext === 'DCM' ? 'DICOM' : ext
}

/** 解析文件名提取患者信息 */
function parseFilename(filename: string): ParsedInfo | null {
  const m = filename.match(FILENAME_RE)
  if (!m) return null
  const finding = m[5]
  return {
    patient_no: m[1],
    name: m[2],
    gender: m[3],
    age: parseInt(m[4]),
    finding,
    finding_zh: FINDING_ZH[finding] || finding,
    image_id: m[6],
  }
}

/** 根据patient_no在已加载的患者列表中查找 */
function findPatientByNo(patientNo: string) {
  return patientList.value.find((p: any) => p.patient_no === patientNo)
}

function getPatient(id: number | null) {
  if (!id) return null
  return patientList.value.find((p: any) => p.id === id)
}

function handleFilesChange(file: UploadFile) {
  if (!file.raw) return
  const parsed = parseFilename(file.name)
  // 尝试自动匹配已有患者
  let patientId: number | null = null
  if (parsed) {
    const existing = findPatientByNo(parsed.patient_no)
    if (existing) patientId = existing.id
  }
  imageItems.value.push({
    filename: file.name,
    file: file.raw,
    previewUrl: URL.createObjectURL(file.raw),
    fileSize: formatFileSize(file.raw.size),
    fileType: getFileType(file.name),
    patientId,
    parsedInfo: parsed,
    clinicalFinding: parsed ? parsed.finding_zh : '',
  })
}

function removeImage(idx: number) {
  const item = imageItems.value[idx]
  if (item.previewUrl.startsWith('blob:')) URL.revokeObjectURL(item.previewUrl)
  imageItems.value.splice(idx, 1)
}

function triggerAddImages() {
  uploadRefHidden.value?.$el?.querySelector('input')?.click()
}

/** 打开新建患者对话框 */
function openNewPatientDialog(idx: number) {
  newPatientTargetIdx.value = idx
  newPatientForm.value = {
    patient_no: '',
    name: '',
    gender: 'male',
    age: 30,
    finding: '',
    phone: '',
    medical_history: '',
  }
  newPatientDialogVisible.value = true
}

/** 创建新患者并绑定 */
async function createNewPatient() {
  const form = newPatientForm.value
  if (!form.patient_no.trim() || !form.name.trim()) {
    ElMessage.warning('患者编号和姓名不能为空')
    return
  }
  creatingPatient.value = true
  try {
    // 组装提交数据，临床症状拼入病史
    const submitData: any = {
      patient_no: form.patient_no,
      name: form.name,
      gender: form.gender,
      age: form.age,
      phone: form.phone,
      medical_history: [form.finding ? `临床症状: ${form.finding}` : '', form.medical_history].filter(Boolean).join('; ') || '',
    }
    const res: any = await createPatientApi(submitData)
    const newPatient = res.data
    // 刷新患者列表
    patientList.value.push(newPatient)
    // 绑定到当前图片
    if (newPatientTargetIdx.value >= 0) {
      imageItems.value[newPatientTargetIdx.value].patientId = newPatient.id
    }
    newPatientDialogVisible.value = false
    ElMessage.success('患者创建成功')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '创建患者失败')
  } finally {
    creatingPatient.value = false
  }
}

function probColor(code: string): string {
  const map: Record<string, string> = {
    Atelectasis: '#F59E0B', Cardiomegaly: '#EF4444', Effusion: '#3B82F6',
    Infiltration: '#8B5CF6', Mass: '#EC4899', Nodule: '#6366F1',
    Pneumonia: '#F97316', Pneumothorax: '#EF4444', Consolidation: '#F59E0B',
    Edema: '#06B6D4', Emphysema: '#14B8A6', Fibrosis: '#8B5CF6',
    Pleural_Thickening: '#64748B', Hernia: '#A855F7',
  }
  return map[code] || '#60A5FA'
}

/** 显示性别：优先后端数据，回退本地解析 */
function displayGender(d: DiagItem): string {
  return d.data?.patient_gender || d.localGender || ''
}

/** 显示年龄：优先后端数据，回退本地解析 */
function displayAge(d: DiagItem): number | null {
  return d.data?.patient_age ?? d.localAge ?? null
}

async function loadPatients() {
  try {
    const res: any = await getPatientsApi({ page: 1, per_page: 500 })
    patientList.value = res.data.items || []
  } catch { /* handled */ }
}

/** 开始批量检测 - 异步提交 */
async function startDiagnosis() {
  if (imageItems.value.length === 0) return
  const hasFiles = imageItems.value.some(i => i.file)
  if (!hasFiles) {
    ElMessage.warning('图片文件已失效，请重新上传影像')
    return
  }
  diagnosing.value = true

  // 初始化 diagnoses 占位
  diagnoses.value = imageItems.value.map(item => {
    const patient = item.parsedInfo
      ? (item.patientId ? getPatient(item.patientId) : null)
      : getPatient(item.patientId)
    return {
      filename: item.filename,
      previewUrl: item.previewUrl,
      patientId: item.patientId,
      patientName: patient ? `${patient.name} (${patient.patient_no})` : (item.parsedInfo ? `${item.parsedInfo.name} (新患者)` : ''),
      status: 'diagnosing' as const,
      data: null,
      topResult: 'normal',
      topResultName: '正常',
      top5Probs: [],
      reportStatus: 'pending' as const,
      reportContent: '',
      errorMsg: '',
      localGender: item.parsedInfo?.gender || '',
      localAge: item.parsedInfo?.age || null,
      localClinicalFinding: item.clinicalFinding || '',
    }
  })

  try {
    const formData = new FormData()
    for (const item of imageItems.value) {
      if (item.file) formData.append('images', item.file)
    }
    // patient_ids 映射
    const patientIdsMap: Record<string, number> = {}
    imageItems.value.forEach(item => {
      if (item.patientId && item.file) {
        patientIdsMap[item.filename] = item.patientId
      }
    })
    formData.append('patient_ids', JSON.stringify(patientIdsMap))
    // 临床症状映射 { filename: finding }
    const clinicalFindingsMap: Record<string, string> = {}
    imageItems.value.forEach(item => {
      if (item.clinicalFinding && item.file) {
        clinicalFindingsMap[item.filename] = item.clinicalFinding
      }
    })
    formData.append('clinical_findings', JSON.stringify(clinicalFindingsMap))
    formData.append('skip_heatmap', 'false')

    const res: any = await batchDiagnoseApi(formData)
    activeBatchId.value = res.data.batch_id
    // 保存完整状态到 localStorage，用于切换页面/刷新恢复
    localStorage.setItem('batch_active_id', String(res.data.batch_id))
    localStorage.setItem('batch_image_items', JSON.stringify(imageItems.value.map(i => ({
      filename: i.filename,
      fileSize: i.fileSize,
      fileType: i.fileType,
      patientId: i.patientId,
      parsedInfo: i.parsedInfo,
      clinicalFinding: i.clinicalFinding,
    }))))
    localStorage.setItem('batch_diagnoses', JSON.stringify(diagnoses.value))

    // 开始轮询进度
    startPolling()
  } catch (e: any) {
    diagnosing.value = false
    for (const d of diagnoses.value) {
      d.status = 'error'
      d.errorMsg = e?.response?.data?.message || '批量检测请求失败'
    }
    ElMessage.error('批量检测请求失败')
  }
}

/** 停止检测 */
async function stopDiagnosis() {
  if (!activeBatchId.value) return
  try {
    await cancelBatchApi(activeBatchId.value)
    ElMessage.warning('正在停止检测...')
  } catch { /* handled */ }
}

/** 轮询进度 */
function startPolling() {
  stopPolling()
  pollTimer = setInterval(pollProgress, 1500)
  // 立即查一次
  pollProgress()
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

async function pollProgress() {
  if (!activeBatchId.value) { stopPolling(); return }
  try {
    const res: any = await getBatchProgressApi(activeBatchId.value)
    const data = res.data

    // 根据进度更新 diagnoses
    for (const r of data.results || []) {
      const match = diagnoses.value.find(d => d.filename === r.original_filename)
      if (!match) continue
      applyResultToDiag(match, r)
    }

    // 同步更新 imageItems 缩略图（blob URL 失效后用服务端 URL）
    for (const r of data.results || []) {
      if (r.status !== 'done' || !r.data?.image_url) continue
      const imgItem = imageItems.value.find(i => i.filename === r.original_filename)
      if (imgItem && !imgItem.previewUrl) {
        imgItem.previewUrl = r.data.image_url
      }
    }

    // 检查是否完成（所有项目都必须是 done 或 error 才算真正完成）
    const hasReporting = (data.results || []).some((r: any) => r.status === 'reporting')
    if (!hasReporting && ['completed', 'partial_failed', 'failed', 'cancelled'].includes(data.status)) {
      diagnosing.value = false
      stopPolling()
      localStorage.removeItem('batch_active_id')
      // 检测完成：清除 imageItems（结果已保存在 diagnoses 中）
      imageItems.value = []
      localStorage.removeItem('batch_image_items')
      localStorage.setItem('batch_diagnoses', JSON.stringify(diagnoses.value))
      const successCount = diagnoses.value.filter(d => d.status === 'done').length
      const failCount = diagnoses.value.filter(d => d.status === 'error').length
      const reportingCount = diagnoses.value.filter(d => d.status === 'reporting').length
      if (data.cancelled) {
        ElMessage.warning(`检测已停止：成功${successCount}，失败${failCount}`)
      } else {
        ElMessage.success(`批量诊断完成：成功${successCount}，失败${failCount}${reportingCount ? `，生成中${reportingCount}` : ''}`)
      }
    } else {
      // 还在进行中，持续更新 localStorage
      localStorage.setItem('batch_diagnoses', JSON.stringify(diagnoses.value))
    }
  } catch {
    // 网络错误时继续轮询
  }
}

/** 从 localStorage 和后端恢复批量诊断状态 */
async function resumeIfActive() {
  const savedId = localStorage.getItem('batch_active_id')
  const savedDiagnoses = localStorage.getItem('batch_diagnoses')
  const savedImageItems = localStorage.getItem('batch_image_items')

  // 恢复 imageItems（只读元数据，不含 file/blob）
  if (savedImageItems) {
    try {
      const items = JSON.parse(savedImageItems)
      imageItems.value = items.map((i: any) => ({
        ...i,
        file: null,
        previewUrl: '',
      }))
    } catch { /* ignore */ }
  }

  // 恢复 diagnoses 快照（过滤掉无效条目）
  if (savedDiagnoses) {
    try {
      const saved = JSON.parse(savedDiagnoses)
      diagnoses.value = (Array.isArray(saved) ? saved : []).filter((d: any) => d && d.filename)
    } catch { /* ignore */ }
  }

  // 有活跃的批次 → 轮询获取最新进度
  if (savedId) {
    const batchId = parseInt(savedId)
    activeBatchId.value = batchId
    diagnosing.value = true
    // 先查一次，如果已完成则立即停止
    try {
      const res: any = await getBatchProgressApi(batchId)
      const data = res.data
      // 用后端数据重建 diagnoses
      rebuildDiagnosesFromProgress(data)
      if (['completed', 'partial_failed', 'failed', 'cancelled'].includes(data.status)) {
        diagnosing.value = false
        localStorage.removeItem('batch_active_id')
        // 批次已结束，清除无文件的空壳图片项
        if (!imageItems.value.some(i => i.file)) {
          imageItems.value = []
          localStorage.removeItem('batch_image_items')
        }
        localStorage.setItem('batch_diagnoses', JSON.stringify(diagnoses.value))
      } else {
        startPolling()
      }
    } catch {
      diagnosing.value = false
      localStorage.removeItem('batch_active_id')
    }
    return
  }

  // 没有活跃批次但有历史结果 → 直接显示（清除无文件的空壳图片）
  if (savedDiagnoses && diagnoses.value.length > 0) {
    // 清除无法重新提交的空壳图片项
    if (imageItems.value.length > 0 && !imageItems.value.some(i => i.file)) {
      imageItems.value = []
      localStorage.removeItem('batch_image_items')
    }
  }
}

/** 用后端进度数据重建 diagnoses，同时更新 imageItems 的缩略图 */
function rebuildDiagnosesFromProgress(data: any) {
  // 构建 filename → result 映射
  const resultMap = new Map<string, any>()
  for (const r of data.results || []) {
    resultMap.set(r.original_filename, r)
  }

  // 如果已有 diagnoses 快照，更新之
  for (const d of diagnoses.value) {
    const r = resultMap.get(d.filename)
    if (!r) continue
    applyResultToDiag(d, r)
  }

  // 对于没有快照的，从 progress 结果创建
  const existingFilenames = new Set(diagnoses.value.map(d => d.filename))
  for (const r of data.results || []) {
    if (existingFilenames.has(r.original_filename)) continue
    const d: DiagItem = {
      filename: r.original_filename,
      previewUrl: '',
      patientId: null,
      patientName: '',
      status: 'diagnosing' as const,
      data: null,
      topResult: 'normal',
      topResultName: '正常',
      top5Probs: [],
      reportStatus: 'pending' as const,
      reportContent: '',
      errorMsg: '',
      // 尝试从文件名解析备用信息
      localGender: parseFilename(r.original_filename)?.gender || '',
      localAge: parseFilename(r.original_filename)?.age || null,
      localClinicalFinding: '',
    }
    applyResultToDiag(d, r)
    diagnoses.value.push(d)
  }

  // 用服务端图片URL更新 imageItems 的缩略图
  for (const r of data.results || []) {
    if (r.status !== 'done' || !r.data?.image_url) continue
    const imgItem = imageItems.value.find(i => i.filename === r.original_filename)
    if (imgItem && !imgItem.previewUrl) {
      imgItem.previewUrl = r.data.image_url
    }
  }
}

/** 将单个 progress result 应用到 DiagItem */
function applyResultToDiag(d: DiagItem, r: any) {
  if ((r.status === 'done' || r.status === 'reporting') && r.data) {
    d.data = r.data
    d.topResult = r.data.top_result
    d.topResultName = r.data.top_result_name
    d.top5Probs = r.data.top5 || []
    // 用服务端图片URL替代 blob: URL
    d.previewUrl = r.data.image_url || d.previewUrl
    if (r.data.patient_name) d.patientName = r.data.patient_name + (r.data.patient_no ? ` (${r.data.patient_no})` : '')

    // 报告内容（流水线完成时自动携带）
    if (r.data.ai_report) {
      const parts: string[] = []
      if (r.data.ai_report.findings) parts.push('【检查所见】\n' + r.data.ai_report.findings)
      if (r.data.ai_report.impression) parts.push('【诊断意见】\n' + r.data.ai_report.impression)
      if (r.data.ai_report.recommendations) parts.push('【建议】\n' + r.data.ai_report.recommendations)
      d.reportContent = parts.join('\n\n') || r.data.ai_report.full_text || ''
      d.reportStatus = 'done'
    }

    d.status = r.status  // 'reporting' 或 'done'
  } else if (r.status === 'error') {
    d.status = 'error'
    d.errorMsg = r.error_msg || '检测失败'
  }
}

async function generateSingleReport(item: DiagItem) {
  // 单张重新生成（已有report_id时使用）
  const reportId = item.data?.report_id
  if (reportId) {
    item.reportStatus = 'generating'
    try {
      const res: any = await regenerateReportApi(reportId)
      const parts: string[] = []
      if (res.data?.findings) parts.push('【检查所见】\n' + res.data.findings)
      if (res.data?.impression) parts.push('【诊断意见】\n' + res.data.impression)
      if (res.data?.recommendations) parts.push('【建议】\n' + res.data.recommendations)
      item.reportContent = parts.join('\n\n') || res.data?.ai_generated_content || ''
      item.reportStatus = 'done'
    } catch { item.reportStatus = 'error' }
  } else if (activeBatchId.value) {
    // 无report_id时走批量接口单独处理
    await generateAllReports()
  }
}

async function generateAllReports() {
  if (!activeBatchId.value) { ElMessage.error('批次信息丢失，请重新检测'); return }
  generatingReports.value = true

  // 收集临床发现映射
  const clinicalFindingsMap: Record<string, string> = {}
  for (const d of diagnoses.value) {
    if (d.status === 'done' && d.data && imageItems.value.length > 0) {
      const imgItem = imageItems.value.find(ii => ii.filename === d.data.original_filename)
      if (imgItem?.clinicalFinding) {
        clinicalFindingsMap[d.data.original_filename] = imgItem.clinicalFinding
      }
    }
  }

  // 标记所有pending项为generating
  const pending = completedDiagnoses.value.filter(d => d.reportStatus !== 'done')
  pending.forEach(d => { d.reportStatus = 'generating' })

  try {
    const res: any = await batchGenerateReportsApi(activeBatchId.value, clinicalFindingsMap)
    const data = res.data || {}

    // 用返回的结果更新各条目
    if (data.results && Array.isArray(data.results)) {
      for (const r of data.results) {
        const item = completedDiagnoses.value.find(d => d.data?.diagnosis_id === r.diagnosis_id)
        if (item && item.data) {
          // 更新热力图URL
          if (r.heatmap_url) {
            item.data.heatmapUrl = r.heatmap_url
          }
          // 更新报告ID和内容
          if (r.report_id) {
            item.data.report_id = r.report_id
          }
          if (r.ai_report) {
            const parts: string[] = []
            if (r.ai_report.findings) parts.push('【检查所见】\n' + r.ai_report.findings)
            if (r.ai_report.impression) parts.push('【诊断意见】\n' + r.ai_report.impression)
            if (r.ai_report.recommendations) parts.push('【建议】\n' + r.ai_report.recommendations)
            item.reportContent = parts.join('\n\n') || r.ai_report.full_text || ''
          }
          item.reportStatus = 'done'
        }
      }
    }

    // 标记未在结果中返回的为error
    pending.forEach(d => {
      if (d.reportStatus === 'generating') d.reportStatus = 'error'
    })

    ElMessage.success(`报告生成完成：成功${data.generated || 0}张${data.failed ? `，失败${data.failed}张` : ''}`)
  } catch (e: any) {
    pending.forEach(d => { if (d.reportStatus === 'generating') d.reportStatus = 'error' })
    ElMessage.error('报告生成失败: ' + (e.response?.data?.message || e.message))
  }

  generatingReports.value = false
}

/** 图片转Base64（确保打印时图片正常显示） */
async function imageToBase64(url: string): Promise<string> {
  try {
    const response = await fetch(url)
    const blob = await response.blob()
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  } catch { return '' }
}

/** 查看专业打印报告（与诊断中心格式一致） */
async function viewReport(item: DiagItem) {
  if (!item.data && !item.reportContent) return

  const d = item.data
  // 患者信息
  const patientName = d?.patient_name || item.patientName.split('(')[0].trim() || '-'
  const patientGender = d?.patient_gender === 'male' ? '男' : (d?.patient_gender === 'female' ? '女' : '-')
  const patientAge = d?.patient_age ? `${d.patient_age}岁` : '-'
  const patientNo = d?.patient_no || item.patientName.match(/P\d+/)?.[0] || '-'
  const recordNo = d?.diagnosis_no || item.filename || '-'
  // 影像
  const imageSrc = item.previewUrl || d?.image_url || ''
  const heatmapSrc = d?.heatmap_url || ''
  // 结果
  const topResult = item.topResult || d?.top_result || 'normal'
  const resultCn = item.topResultName || d?.top_result_name || '正常'
  const confidence = item.top5Probs?.length ? (item.top5Probs[0].probability * 100).toFixed(1) : '0.0'
  const reportText = item.reportContent || ''

  const resultColor = topResult === 'normal' ? '#06B6D4' : '#D97706'
  const resultBg = topResult === 'normal' ? '#ECFDF5' : '#FFFBEB'
  const resultIcon = topResult === 'normal' ? '&#10003;' : '&#9888;'

  const now = new Date()
  const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  // 概率条HTML
  const probs = item.top5Probs || []
  const probBarsHtml = probs.map((p: any) => {
    const pct = (p.probability * 100).toFixed(1)
    const color = probColor(p.disease_code)
    return `<div class="pr"><span class="pl">${p.disease_name_zh}</span><div class="pw"><div class="pf" style="background:${color};width:${pct}%"></div></div><span class="pv">${pct}%</span></div>`
  }).join('')

  // 转换图片为base64
  const [imgBase64, heatmapBase64] = await Promise.all([
    imageSrc ? imageToBase64(imageSrc) : Promise.resolve(''),
    heatmapSrc ? imageToBase64(heatmapSrc) : Promise.resolve('')
  ])

  const printWin = window.open('', '_blank')
  if (!printWin) return
  printWin.document.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><title>诊断报告-${recordNo}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
@page{size:A4;margin:10mm}
body{font-family:'Microsoft YaHei','PingFang SC',sans-serif;background:#fff;color:#1e293b;font-size:11px;line-height:1.5}
.page{padding:8mm 10mm;max-height:100vh;overflow:hidden;display:flex;flex-direction:column}
.hd{text-align:center;padding-bottom:10px;margin-bottom:12px;border-bottom:2px solid #0f172a;position:relative}
.hd::after{content:'';position:absolute;bottom:-4px;left:50%;transform:translateX(-50%);width:50px;height:2.5px;background:#22D3EE;border-radius:2px}
.hd h1{font-size:24px;font-weight:800;color:#0f172a;letter-spacing:3px}
.hd .sub{font-size:11px;color:#94a3b8;letter-spacing:1px;margin-top:3px}
.main{display:grid;grid-template-columns:1fr 1fr;gap:12px;flex:1;min-height:0}
.col-img{display:flex;flex-direction:column;gap:8px}
.ib{border:1px solid #e2e8f0;border-radius:4px;overflow:hidden;background:#f8fafc}
.ib .il{font-size:10px;font-weight:600;color:#475569;padding:4px 8px;background:#f1f5f9;border-bottom:1px solid #e2e8f0}
.ib .iw{height:150px;display:flex;align-items:center;justify-content:center;padding:4px}
.ib img{max-width:100%;max-height:100%;object-fit:contain}
.col-res{display:flex;flex-direction:column;gap:8px}
.pat-info{background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;padding:12px 14px}
.pat-info .pat-header{display:flex;align-items:baseline;gap:10px;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #e2e8f0}
.pat-info .pat-name{font-size:16px;font-weight:700;color:#0f172a}
.pat-info .pat-ga{font-size:11px;color:#64748b}
.pat-info .pat-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px 20px;font-size:10px}
.pat-info .pi-row{display:flex;justify-content:space-between}
.pat-info .pi-lb{color:#94a3b8}
.pat-info .pi-vl{color:#0f172a;font-weight:600}
.rb{display:flex;align-items:center;gap:12px;padding:10px 14px;border-radius:6px;border:2px solid ${resultColor};background:${resultBg}}
.ri{font-size:28px;color:${resultColor};font-weight:700;line-height:1}
.rt .rl{font-size:17px;font-weight:700;color:${resultColor}}
.rt .rc{font-size:10px;color:#64748b;margin-top:2px}
.pg{display:flex;flex-direction:column;gap:4px}
.pr{display:flex;align-items:center;gap:8px;font-size:10px}
.pr .pl{width:50px;color:#475569;font-weight:500;text-align:right;flex-shrink:0}
.pr .pw{flex:1;height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden}
.pr .pf{height:100%;border-radius:3px}
.pr .pv{width:48px;color:#0f172a;font-weight:600;text-align:right;flex-shrink:0}
.rtx{background:#f8fafc;border:1px solid #e2e8f0;border-radius:4px;padding:10px;font-size:10.5px;line-height:1.7;color:#334155;white-space:pre-wrap;word-break:break-all;margin-top:8px}
.ft{display:flex;justify-content:space-between;align-items:center;padding-top:8px;margin-top:8px;border-top:1px solid #e2e8f0;font-size:9px;color:#94a3b8}
@media print{body{-webkit-print-color-adjust:exact;print-color-adjust:exact}.page{padding:0;max-height:none;overflow:visible}}
</style></head><body>
<div class="page">
  <div class="hd">
    <h1>胸部X光AI辅助诊断报告</h1>
    <div class="sub">AI-assisted Chest X-ray Diagnosis Report</div>
  </div>
  <div class="main">
    <div class="col-img">
      <div class="ib">
        <div class="il">原始胸部X光片</div>
        <div class="iw">${imgBase64 ? `<img src="${imgBase64}" />` : '<span style="color:#94a3b8">暂无影像</span>'}</div>
      </div>
      ${heatmapBase64 ? `<div class="ib"><div class="il">Grad-CAM 热力图</div><div class="iw"><img src="${heatmapBase64}" /></div></div>` : ''}
    </div>
    <div class="col-res">
      <div class="pat-info">
        <div class="pat-header">
          <span class="pat-name">${patientName}</span>
          <span class="pat-ga">${patientGender} | ${patientAge}</span>
        </div>
        <div class="pat-grid">
          <div class="pi-row"><span class="pi-lb">患者编号</span><span class="pi-vl">${patientNo}</span></div>
          <div class="pi-row"><span class="pi-lb">记录编号</span><span class="pi-vl">${recordNo}</span></div>
          <div class="pi-row"><span class="pi-lb">报告日期</span><span class="pi-vl">${dateStr}</span></div>
          <div class="pi-row"><span class="pi-lb">诊断时间</span><span class="pi-vl">${now.toLocaleString('zh-CN')}</span></div>
        </div>
      </div>
      <div class="rb">
        <div class="ri">${resultIcon}</div>
        <div class="rt">
          <div class="rl">${resultCn}</div>
          <div class="rc">置信度 ${confidence}%</div>
        </div>
      </div>
      <div class="pg">${probBarsHtml}</div>
    </div>
  </div>
  ${reportText ? `<div class="rtx">${reportText.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</div>` : ''}
  <div class="ft">
    <span>本报告由AI辅助诊断系统生成，仅供临床医生参考</span>
    <span>打印时间: ${now.toLocaleString('zh-CN')}</span>
          </div>
          </template>
        </div>
</body></html>`)
  printWin.document.close()
  setTimeout(() => printWin.print(), 500)
}

function resetAll() {
  imageItems.value.forEach(item => {
    if (item.previewUrl.startsWith('blob:')) URL.revokeObjectURL(item.previewUrl)
  })
  imageItems.value = []
  diagnoses.value = []
  activeBatchId.value = null
  localStorage.removeItem('batch_active_id')
  localStorage.removeItem('batch_image_items')
  localStorage.removeItem('batch_diagnoses')
  localStorage.removeItem('batch_filenames')
}

onMounted(() => {
  loadPatients()
  resumeIfActive()
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped lang="scss">
.batch-page {
  .flow-steps {
    display: flex;
    align-items: center;
    gap: 0;
    margin-bottom: 24px;
    padding: 20px 28px;
    background: var(--card-bg);
    backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);

    .step {
      display: flex;
      align-items: center;
      gap: 14px;
      flex-shrink: 0;

      .step-dot {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        background: var(--glass-bg);
        border: 2px solid var(--glass-border);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.4s ease;
        flex-shrink: 0;

        span {
          font-size: 15px;
          font-weight: 700;
          color: var(--text-muted);
          transition: color 0.4s ease;
        }
      }

      .step-info {
        display: flex;
        flex-direction: column;
        gap: 2px;

        .step-title {
          font-size: 14px;
          font-weight: 600;
          color: var(--text-muted);
          transition: color 0.4s ease;
        }

        .step-desc {
          font-size: 12px;
          color: var(--text-muted);
          opacity: 0.6;
        }
      }

      &.active {
        .step-dot {
          background: rgba(16, 185, 129, 0.15);
          border-color: var(--primary);
          box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);

          span {
            color: var(--primary);
          }
        }

        .step-title {
          color: var(--text-primary);
        }

        .step-desc {
          opacity: 1;
          color: var(--text-secondary);
        }
      }

      &.done {
        .step-dot {
          background: var(--primary);
          border-color: var(--primary);

          span {
            color: #fff;
          }
        }

        .step-title {
          color: var(--primary);
        }
      }
    }

    .step-line {
      flex: 1;
      height: 2px;
      background: var(--glass-border);
      margin: 0 8px;
      border-radius: 1px;
      transition: background 0.4s ease;

      &.active {
        background: var(--primary);
      }
    }
  }

  .zone-card {
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    overflow: hidden;
    transition: all 0.4s ease;
    position: relative;
    margin-bottom: 20px;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--glass-bg-hover), transparent);
    }

    &.active {
      border-color: rgba(16, 185, 129, 0.3);
      box-shadow: 0 0 30px rgba(16, 185, 129, 0.08);
    }

    .zone-header {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 20px 24px 16px;
      border-bottom: 1px solid var(--glass-border);

      .zone-badge {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--primary);
        flex-shrink: 0;

        &.result-badge {
          background: rgba(59, 130, 246, 0.15);
          border-color: rgba(59, 130, 246, 0.3);
          color: var(--blue);
        }
      }

      .zone-title-group {
        flex: 1;

        .zone-title {
          font-size: 16px;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0;
        }

        .zone-subtitle {
          font-size: 12px;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      }

      .zone-status {
        flex-shrink: 0;
      }
    }

    .zone-body {
      padding: 20px 24px 24px;
    }
  }

  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 40px 20px;

    .upload-icon {
      color: var(--text-muted);
      margin-bottom: 10px;
      opacity: 0.6;
    }

    .upload-text {
      font-size: 14px;
      color: var(--text-secondary);
      margin-bottom: 4px;
    }

    .upload-hint {
      font-size: 13px;
      color: var(--text-muted);

      em {
        color: var(--primary);
        font-style: normal;
        font-weight: 500;
      }
    }
  }

  // 图片网格 - 两列
  .image-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .image-card {
    display: flex;
    align-items: stretch;
    gap: 0;
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    background: var(--glass-bg);
    overflow: hidden;
    transition: border-color 0.3s;
    position: relative;

    &:hover {
      border-color: var(--primary);
    }

    // 关闭按钮（右上角）
    .image-card-close {
      position: absolute;
      top: 6px;
      right: 6px;
      z-index: 10;
      opacity: 0;
      transform: scale(0.8);
      transition: all 0.2s;

      .el-icon {
        font-size: 12px;
      }
    }

    &:hover .image-card-close {
      opacity: 1;
      transform: scale(1);
    }

    // 左侧缩略图
    .image-card-left {
      position: relative;
      width: 110px;
      flex-shrink: 0;
      background: var(--bg-tertiary);

      .image-thumb {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .image-thumb-placeholder {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-muted);
        opacity: 0.4;
      }

      .image-card-del {
        position: absolute;
        top: 4px;
        right: 4px;
        background: rgba(0, 0, 0, 0.4);
        border-radius: 4px;
        padding: 2px;
      }
    }

    // 右侧信息
    .image-card-right {
      flex: 1;
      min-width: 0;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;

      .image-card-name {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-primary);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .image-card-meta {
        font-size: 11px;
        color: var(--text-muted);

        .meta-sep {
          margin: 0 4px;
          opacity: 0.4;
        }
      }
    }
  }

  .patient-auto {
    .patient-auto-row {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 12px;

      &.secondary {
        color: var(--text-muted);
        font-size: 11px;
      }

      .patient-avatar {
        width: 20px;
        height: 20px;
        border-radius: 6px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid rgba(16, 185, 129, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: 700;
        color: var(--primary);
        flex-shrink: 0;
      }

      .patient-name {
        font-weight: 600;
        color: var(--text-primary);
      }

      .patient-info {
        color: var(--text-muted);
      }

      .patient-no {
        color: var(--text-muted);
        font-family: 'Courier New', monospace;
      }

      .patient-finding {
        background: rgba(59, 130, 246, 0.15);
        color: var(--blue);
        padding: 0 6px;
        border-radius: 4px;
      }

      .patient-imgid {
        color: var(--text-muted);
      }
    }

    .patient-matched {
      font-size: 11px;
      color: var(--primary);
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 2px;
    }

    .patient-unmatched {
      font-size: 11px;
      color: var(--orange);
      display: flex;
      align-items: center;
      gap: 4px;
      margin-top: 2px;
    }
  }

  .patient-manual {
    margin-top: 2px;
  }

  .clinical-finding {
    margin-top: 4px;
  }

  .upload-actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
    align-items: center;
  }

  .top-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    align-items: center;
    justify-content: center;
    padding: 10px 20px;
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
  }

  // 检测结果 - 单列（含图片和概率条）
  .result-grid {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .result-item {
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    overflow: hidden;
    background: var(--glass-bg);

    .result-item-header {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;

      .result-item-index {
        width: 24px;
        height: 24px;
        border-radius: 6px;
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: var(--text-muted);
        flex-shrink: 0;
      }

      .result-item-info {
        flex: 1;
        min-width: 0;
        display: flex;
        flex-direction: column;

        .result-item-name {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-primary);
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .result-item-patient {
          font-size: 11px;
          color: var(--primary);
          font-weight: 500;
        }
      }

      .result-item-right {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;
      }
    }

    // 患者/医生信息栏
    .result-meta {
      padding: 8px 14px;
      background: var(--bg-tertiary);
      border-top: 1px solid var(--glass-border);
      border-bottom: 1px solid var(--glass-border);

      .meta-row {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;

        &.meta-doctor {
          margin-top: 4px;
          padding-top: 6px;
          border-top: 1px dashed var(--glass-border);
          font-size: 11px;
        }
      }

      .meta-item {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        font-size: 12px;
        color: var(--text-secondary);

        .el-icon {
          font-size: 13px;
          color: var(--primary);
        }

        &.meta-clinical {
          background: rgba(245, 158, 11, 0.1);
          color: var(--orange);
          padding: 1px 8px;
          border-radius: 10px;
          font-size: 11px;

          .el-icon {
            color: var(--orange);
          }
        }
      }

      .meta-divider {
        width: 1px;
        height: 14px;
        background: var(--glass-border);
        flex-shrink: 0;
      }
    }

    .result-detail {
      padding: 14px 12px;

      .result-detail-grid {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 14px;
        align-items: start;
      }
    }

    .result-images {
      display: flex;
      gap: 8px;

      .result-thumb-box {
        position: relative;
        width: 100px;
        height: 100px;
        border-radius: var(--radius-sm);
        overflow: hidden;
        border: 1px solid var(--glass-border);
        background: var(--bg-tertiary);

        .result-thumb {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .result-thumb-label {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          text-align: center;
          font-size: 10px;
          color: #fff;
          background: rgba(0, 0, 0, 0.5);
          padding: 2px 0;
        }
      }
    }

    .result-probs {
      display: flex;
      flex-direction: column;
      gap: 4px;

      .prob-row {
        display: flex;
        align-items: center;
        gap: 6px;

        .prob-label {
          width: 52px;
          font-size: 11px;
          color: var(--text-muted);
          text-align: right;
          flex-shrink: 0;
        }

        .prob-bar-wrap {
          flex: 1;
          height: 5px;
          background: var(--bg-tertiary);
          border-radius: 3px;
          overflow: hidden;

          .prob-bar {
            height: 100%;
            border-radius: 3px;
            transition: width 0.6s ease;
          }
        }

        .prob-val {
          width: 40px;
          font-size: 11px;
          font-weight: 600;
          color: var(--text-primary);
          text-align: right;
          flex-shrink: 0;
        }
      }
    }

    .result-error {
      padding: 0 14px 10px;
      font-size: 11px;
      color: var(--red);
      display: flex;
      align-items: center;
      gap: 4px;
    }

    // 内联报告 - 显示在每个患者卡片下方
    .result-report {
      margin: 0 14px 12px;
      border-top: 1px dashed var(--glass-border);
      padding-top: 12px;

      .result-report-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 8px;

        .result-report-title {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          font-weight: 600;
          color: var(--purple);
        }
      }

      .result-report-text {
        white-space: pre-wrap;
        font-family: 'Microsoft YaHei', sans-serif;
        font-size: 12.5px;
        line-height: 1.8;
        color: var(--text-secondary);
        margin: 0;
        background: var(--bg-tertiary);
        padding: 12px 14px;
        border-radius: 8px;
        border: 1px solid var(--glass-border);
      }
    }
  }

  .result-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;

    &.normal {
      background: rgba(16, 185, 129, 0.2);
      color: var(--primary);
    }

    &.abnormal {
      background: rgba(245, 158, 11, 0.2);
      color: var(--orange);
    }
  }

}
</style>

<style lang="scss">
/* 非scoped - link按钮去掉背景，避免暗色主题下绿色文字+绿色背景冲突 */
.action-link {
  background: transparent !important;
  padding: 2px 6px !important;

  &:hover {
    background: transparent !important;
    opacity: 0.8;
  }
}
</style>
