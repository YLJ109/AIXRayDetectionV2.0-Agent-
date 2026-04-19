<template>
  <div class="diagnosis-page">
    <!-- 流程步骤指示器 -->
    <div class="flow-steps">
      <div class="step" :class="{ active: currentStep >= 1, done: currentStep > 1 }">
        <div class="step-dot"><span>1</span></div>
        <div class="step-info">
          <span class="step-title">患者挂号</span>
          <span class="step-desc">选择患者并登记信息</span>
        </div>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 2 }"></div>
      <div class="step" :class="{ active: currentStep >= 2, done: currentStep > 2 }">
        <div class="step-dot"><span>2</span></div>
        <div class="step-info">
          <span class="step-title">影像检查</span>
          <span class="step-desc">上传X光影像</span>
        </div>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 3 }"></div>
      <div class="step" :class="{ active: currentStep >= 3, done: currentStep > 3 }">
        <div class="step-dot"><span>3</span></div>
        <div class="step-info">
          <span class="step-title">AI诊断</span>
          <span class="step-desc">智能分析与结果</span>
        </div>
      </div>
      <div class="step-line" :class="{ active: currentStep >= 4 }"></div>
      <div class="step" :class="{ active: currentStep >= 4 }">
        <div class="step-dot"><span>4</span></div>
        <div class="step-info">
          <span class="step-title">报告输出</span>
          <span class="step-desc">审核确认与取报告</span>
        </div>
      </div>
    </div>

    <!-- ===== 第一区：患者挂号 + 影像检查 ===== -->
    <div class="zone-grid">
      <!-- 左区：患者挂号 -->
      <div class="zone-card registration-zone" :class="{ active: currentStep === 1 }">
        <div class="zone-header">
          <div class="zone-badge">
            <el-icon>
              <User />
            </el-icon>
          </div>
          <div class="zone-title-group">
            <h3 class="zone-title">患者挂号</h3>
            <span class="zone-subtitle">Registration</span>
          </div>
          <div class="zone-status">
            <el-tag :type="selectedPatientId ? 'success' : 'info'" size="small" effect="dark">
              {{ selectedPatientId ? '已登记' : '待登记' }}
            </el-tag>
          </div>
        </div>
        <div class="zone-body">
          <!-- 患者信息摘要卡（选中后显示） -->
          <div class="patient-brief" v-if="currentPatient">
            <div class="brief-avatar">{{ currentPatient.name?.charAt(0) }}</div>
            <div class="brief-info">
              <div class="brief-name">{{ currentPatient.name }}
                <span class="brief-gender" :class="currentPatient.gender">
                  {{ currentPatient.gender === 'male' ? '男' : '女' }}
                </span>
                <span class="brief-age">{{ currentPatient.age }}岁</span>
              </div>
              <div class="brief-no">{{ currentPatient.patient_no }}</div>
              <div class="brief-history" v-if="currentPatient.medical_history">
                既往史: {{ currentPatient.medical_history }}
              </div>
            </div>
          </div>

          <el-form :model="form" :rules="rules" ref="formRef" label-width="80px" size="default">
            <el-form-item label="选择患者" prop="patient_id">
              <el-select v-model="selectedPatientId" placeholder="请选择患者" filterable style="width:100%"
                @change="onPatientChange">
                <el-option v-for="p in patientList" :key="p.id" :label="`${p.patient_no} - ${p.name}`" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="症状描述">
              <el-input v-model="form.symptoms" type="textarea" :rows="2" placeholder="请输入患者症状" />
            </el-form-item>
            <el-form-item label="临床信息">
              <el-input v-model="form.clinical_info" type="textarea" :rows="2" placeholder="补充临床信息" />
            </el-form-item>
          </el-form>
        </div>
      </div>

      <!-- 右区：影像检查 -->
      <div class="zone-card examination-zone" :class="{ active: currentStep === 2 }">
        <div class="zone-header">
          <div class="zone-badge">
            <el-icon>
              <Picture />
            </el-icon>
          </div>
          <div class="zone-title-group">
            <h3 class="zone-title">影像检查</h3>
            <span class="zone-subtitle">Examination</span>
          </div>
          <div class="zone-status">
            <el-tag :type="selectedFile ? 'success' : 'info'" size="small" effect="dark">
              {{ selectedFile ? '已上传' : '待上传' }}
            </el-tag>
          </div>
        </div>
        <div class="zone-body">
          <div class="upload-area">
            <div class="glass-upload-area" :class="{ 'has-file': selectedFile }">
              <el-upload ref="uploadRef" drag :auto-upload="false" :show-file-list="false" :limit="1"
                accept=".png,.jpg,.jpeg,.bmp,.gif,.webp" :on-change="onFileChange" class="upload-inner">
                <div class="upload-placeholder" v-if="!selectedFile">
                  <div class="upload-icon">
                    <el-icon :size="36">
                      <Upload />
                    </el-icon>
                  </div>
                  <div class="upload-text">拖拽胸部X光影像到此处</div>
                  <div class="upload-hint">或 <em>点击上传</em></div>
                  <div class="upload-formats">PNG / JPG / JPEG / BMP / WEBP，最大50MB</div>
                </div>
              </el-upload>
              <div class="upload-preview" v-if="selectedFile">
                <img :src="imagePreviewUrl" alt="preview" />
                <div class="preview-overlay" @click="onFileRemove">
                  <el-icon :size="20">
                    <Delete />
                  </el-icon>
                  <span>移除影像</span>
                </div>
              </div>
            </div>
          </div>
          <el-button type="primary" size="large" class="diagnose-btn" :loading="diagnosing" @click="handleDiagnose"
            :disabled="!selectedFile || !selectedPatientId" style="width:100%; margin-top:16px;">
            <el-icon>
              <SetUp />
            </el-icon> 开始AI诊断
          </el-button>
        </div>
      </div>
    </div>

    <!-- ===== 第二区：AI诊断结果 ===== -->
    <div class="zone-card result-zone" v-if="result" :class="{ active: currentStep === 3 }">
      <div class="zone-header">
        <div class="zone-badge result-badge">
          <el-icon>
            <Cpu />
          </el-icon>
        </div>
        <div class="zone-title-group">
          <h3 class="zone-title">AI诊断结果</h3>
          <span class="zone-subtitle">Diagnosis Result</span>
        </div>
        <div class="zone-status">
          <el-tag :type="resultTagType" size="small" effect="dark">{{ resultTagLabel }}</el-tag>
        </div>
      </div>
      <div class="zone-body">
        <div class="result-layout">
          <!-- 左：影像分析 -->
          <div class="result-images">
            <div class="image-box">
              <div class="image-label">原始影像</div>
              <div class="preview-img-wrapper" :class="{ 'has-image': imagePreviewUrl || result?.image_url }">
                <el-image v-if="imagePreviewUrl || result?.image_url" :src="imagePreviewUrl || result.image_url"
                  fit="contain" class="preview-img" :preview-src-list="[imagePreviewUrl || result.image_url]">
                  <template #error>
                    <div class="image-error"><el-icon :size="28">
                        <Picture></Picture>
                      </el-icon><span>影像加载失败</span></div>
                  </template>
                </el-image>
                <div v-else class="image-placeholder"><el-icon :size="28">
                    <Picture></Picture>
                  </el-icon><span>暂无影像</span></div>
              </div>
            </div>
            <div class="image-box" v-if="result?.heatmap_url">
              <div class="image-label">Grad-CAM 热力图</div>
              <div class="preview-img-wrapper has-image">
                <el-image :src="result.heatmap_url" fit="contain" class="preview-img"
                  :preview-src-list="[result.heatmap_url]">
                  <template #error>
                    <div class="image-error"><el-icon :size="28">
                        <Picture />
                      </el-icon><span>热力图加载失败</span></div>
                  </template>
                </el-image>
              </div>
            </div>
          </div>

          <!-- 中：诊断详情 -->
          <div class="result-detail">
            <!-- 主结果 -->
            <div class="result-hero" :class="topResult === 'normal' ? 'normal' : 'abnormal'">
              <div class="result-hero-icon">
                <el-icon v-if="topResult === 'normal'">
                  <CircleCheck />
                </el-icon>
                <el-icon v-else>
                  <Warning />
                </el-icon>
              </div>
              <div class="result-hero-text">
                <div class="result-hero-label">{{ resultLabel }}</div>
                <div class="result-hero-conf">置信度 {{ topConfidence }}%</div>
              </div>
            </div>

            <!-- 患者信息 -->
            <div class="patient-info-section" v-if="currentPatient">
              <div class="section-title">患者信息</div>
              <div class="patient-info-grid">
                <div class="info-row">
                  <span class="info-label">姓名</span>
                  <span class="info-value">{{ currentPatient.name }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">性别</span>
                  <span class="info-value">{{ currentPatient.gender === 'male' ? '男' : '女' }}</span>
                </div>
                <div class="info-row">
                  <span class="info-label">年龄</span>
                  <span class="info-value">{{ currentPatient.age }}岁</span>
                </div>
                <div class="info-row">
                  <span class="info-label">患者编号</span>
                  <span class="info-value mono">{{ currentPatient.patient_no }}</span>
                </div>
                <div class="info-row" v-if="currentPatient.phone">
                  <span class="info-label">联系电话</span>
                  <span class="info-value">{{ currentPatient.phone }}</span>
                </div>
                <div class="info-row" v-if="currentPatient.id_card">
                  <span class="info-label">身份证号</span>
                  <span class="info-value mono">{{ currentPatient.id_card }}</span>
                </div>
                <div class="info-row full-width" v-if="currentPatient.medical_history">
                  <span class="info-label">既往病史</span>
                  <span class="info-value">{{ currentPatient.medical_history }}</span>
                </div>
                <div class="info-row full-width" v-if="currentPatient.allergy_history">
                  <span class="info-label">过敏史</span>
                  <span class="info-value">{{ currentPatient.allergy_history }}</span>
                </div>
              </div>
            </div>

            <!-- 概率分布 -->
            <div class="prob-section">
              <div class="prob-item" v-for="p in top5Probs" :key="p.disease_code">
                <div class="prob-header">
                  <span class="prob-dot" :style="{ background: probColor(p.disease_code) }"></span>
                  <span class="prob-label">{{ p.disease_name_zh }}</span>
                  <span class="prob-value">{{ (p.probability * 100).toFixed(1) }}%</span>
                </div>
                <div class="prob-bar">
                  <div class="prob-fill"
                    :style="{ width: p.probability * 100 + '%', background: probColor(p.disease_code) }">
                  </div>
                </div>
              </div>
            </div>

            <!-- 附加信息 -->
            <div class="result-meta">
              <div class="meta-item">
                <span class="meta-label">记录编号</span>
                <span class="meta-value mono">{{ result.diagnosis_no }}</span>
              </div>
              <div class="meta-item" v-if="result.ai_report?.ai_model_used">
                <span class="meta-label">AI模型</span>
                <span class="meta-value">{{ result.ai_report.ai_model_used }}</span>
              </div>
            </div>
          </div>

          <!-- 右：操作面板 -->
          <div class="result-actions-panel">
            <div class="action-title">医生审核</div>
            <div class="action-buttons">
              <el-button size="large" @click="handleReview(true)" :loading="reviewing" class="action-btn confirm">
                <el-icon><Select /></el-icon> 确认诊断
              </el-button>
              <el-button size="large" @click="showReviseDialog" class="action-btn revise">
                <el-icon>
                  <Edit />
                </el-icon> 修正诊断
              </el-button>
              <el-button size="large" @click="handleGenerateReport" :loading="generatingReport"
                class="action-btn report" :type="!reportContent ? 'primary' : 'default'" :class="{ 'report-pending': !reportContent }">
                <el-icon>
                  <Document />
                </el-icon> {{ reportContent ? '重新生成' : '生成报告' }}
              </el-button>
            </div>
            <div class="action-note">{{ reportContent ? '确认或修正诊断结果后，可重新生成报告' : '检测完成！点击"生成报告"获取AI诊断报告' }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态（无结果时显示） -->
    <div class="zone-card empty-zone" v-else>
      <div class="zone-body">
        <div class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" />
            </svg>
          </div>
          <h3>等待影像上传与AI诊断</h3>
          <p>请先选择患者、上传胸部X光影像后开始诊断</p>
        </div>
      </div>
    </div>

    <!-- ===== 第三区：诊断报告 ===== -->
    <div class="zone-card report-zone" v-if="result && reportContent" :class="{ active: currentStep === 4 }">
      <div class="zone-header">
        <div class="zone-badge report-badge">
          <el-icon>
            <Document />
          </el-icon>
        </div>
        <div class="zone-title-group">
          <h3 class="zone-title">诊断报告</h3>
          <span class="zone-subtitle">Diagnosis Report</span>
        </div>
        <div class="zone-status">
          <div class="report-toolbar">
            <el-button size="small" @click="handlePrintReport">
              <el-icon>
                <Printer />
              </el-icon> 打印报告
            </el-button>
            <el-button type="primary" size="small" @click="handleGenerateReport" :loading="generatingReport">
              <el-icon>
                <Refresh />
              </el-icon> 重新生成
            </el-button>
          </div>
        </div>
      </div>
      <div class="zone-body">
        <div class="report-content-wrapper" id="print-report">
          <div class="report-header">
            <h2 class="report-title">胸部X光AI辅助诊断报告</h2>
          </div>
          <div class="report-body">
            <div class="report-text-content">
              <pre class="report-pre">{{ reportContent }}</pre>
            </div>
          </div>
          <div class="report-footer">
            <div class="report-footer-item">本报告由AI辅助诊断系统生成，仅供临床医生参考</div>
            <div class="report-footer-item">最终诊断以临床医生意见为准</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修正诊断对话框 -->
    <el-dialog v-model="reviseDialogVisible" title="修正诊断结果" width="500px">
      <el-form label-width="80px">
        <el-form-item label="修正结果">
          <el-select v-model="revisedResult" placeholder="选择修正结果" style="width:100%">
            <el-option v-for="p in top5Probs" :key="p.disease_code" :label="p.disease_name_zh"
              :value="p.disease_code" />
          </el-select>
        </el-form-item>
        <el-form-item label="医生备注">
          <el-input v-model="reviseRemark" type="textarea" :rows="3" placeholder="请输入修正说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleReview(false)">确认修正</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { diagnoseSingleApi } from '@/api/diagnose'
import { getPatientsApi } from '@/api/patients'
import { approveReportApi, updateReportApi, regenerateReportApi } from '@/api/reports'
import { ElMessage } from 'element-plus'
import { User, Upload, Delete, Picture, Refresh, Printer, Cpu, CircleCheck, Warning, Select, Edit, Document, SetUp } from '@element-plus/icons-vue'
import type { UploadFile } from 'element-plus'

const formRef = ref()
const uploadRef = ref()
const patientList = ref<any[]>([])
const selectedPatientId = ref<number | undefined>()
const diagnosing = ref(false)
const reviewing = ref(false)
const generatingReport = ref(false)
const selectedFile = ref<File | null>(null)
const imagePreviewUrl = ref('')
const result = ref<any>(null)
const reportContent = ref('')
const reviseDialogVisible = ref(false)
const revisedResult = ref('')
const reviseRemark = ref('')

const form = ref({ patient_id: undefined as number | undefined, symptoms: '', clinical_info: '' })

const currentPatient = computed(() => {
  if (!selectedPatientId.value || !patientList.value.length) return null
  return patientList.value.find((p: any) => p.id === selectedPatientId.value)
})

// 流程步骤
const currentStep = computed(() => {
  if (result.value && reportContent.value) return 4
  if (result.value) return 3
  if (selectedFile.value) return 2
  if (selectedPatientId.value) return 1
  return 0
})

const rules = { patient_id: [{ required: true, message: '请选择患者', trigger: 'change' }] }

// 从概率数组推导主结果（最高概率 < 0.3 视为正常）
const sortedProbs = computed(() => {
  if (!result.value?.probabilities?.length) return []
  return [...result.value.probabilities].sort((a: any, b: any) => b.probability - a.probability)
})

const topResult = computed(() => {
  if (!sortedProbs.value.length) return 'normal'
  if (sortedProbs.value[0].probability < 0.3) return 'normal'
  return sortedProbs.value[0].disease_code
})

const topResultName = computed(() => {
  if (topResult.value === 'normal') return '正常'
  return sortedProbs.value[0]?.disease_name_zh || topResult.value
})

const topConfidence = computed(() => {
  if (!sortedProbs.value.length) return '0.0'
  return (sortedProbs.value[0].probability * 100).toFixed(1)
})

// 前5种概率
const top5Probs = computed(() => sortedProbs.value.slice(0, 5))

const resultTypeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = { normal: 'success' }

const resultLabel = computed(() => topResultName.value)
const resultTagType = computed(() => resultTypeMap[topResult.value] || 'warning')
const resultTagLabel = computed(() => resultLabel.value)

function probColor(code: string): string {
  const map: Record<string, string> = {
    Atelectasis: '#F59E0B',
    Cardiomegaly: '#EF4444',
    Effusion: '#3B82F6',
    Infiltration: '#8B5CF6',
    Mass: '#EC4899',
    Nodule: '#6366F1',
    Pneumonia: '#F97316',
    Pneumothorax: '#EF4444',
    Consolidation: '#F59E0B',
    Edema: '#06B6D4',
    Emphysema: '#14B8A6',
    Fibrosis: '#8B5CF6',
    Pleural_Thickening: '#64748B',
    Hernia: '#A855F7',
  }
  return map[code] || '#60A5FA'
}

function onPatientChange(id: number) {
  form.value.patient_id = id
  const p = patientList.value.find((i: any) => i.id === id)
  if (p) {
    form.value.symptoms = p.medical_history || ''
  }
}

function onFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
    imagePreviewUrl.value = URL.createObjectURL(file.raw)
  }
}

function onFileRemove() {
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  selectedFile.value = null
  imagePreviewUrl.value = ''
  result.value = null
  reportContent.value = ''
  if (uploadRef.value) { uploadRef.value.clearFiles() }
}

async function handleDiagnose() {
  if (!selectedFile.value || !selectedPatientId.value) return
  diagnosing.value = true
  result.value = null
  reportContent.value = ''
  try {
    const formData = new FormData()
    formData.append('image', selectedFile.value)
    formData.append('patient_id', String(selectedPatientId.value))
    if (form.value.symptoms) formData.append('symptoms', form.value.symptoms)
    if (form.value.clinical_info) formData.append('clinical_info', form.value.clinical_info)
    // 先检测，不自动生成报告（用户点击"生成报告"时才生成）
    formData.append('skip_report', 'true')
    const res: any = await diagnoseSingleApi(formData)
    result.value = res.data
    ElMessage.success('检测完成，请点击"生成报告"获取诊断报告')
  } catch {
    // error handled by interceptor
  } finally {
    diagnosing.value = false
  }
}

async function handleReview(confirm: boolean) {
  reviewing.value = true
  try {
    const reportId = result.value?.report_id
    if (!reportId) {
      ElMessage.error('未找到报告记录')
      return
    }
    if (confirm) {
      await approveReportApi(reportId)
      ElMessage.success('诊断已确认')
    } else {
      await updateReportApi(reportId, {
        findings: revisedResult.value ? `修正诊断: ${top5Probs.value.find((p: any) => p.disease_code === revisedResult.value)?.disease_name_zh || revisedResult.value}` : undefined,
        editor_notes: reviseRemark.value || undefined,
      })
      ElMessage.success('诊断已修正')
    }
    reviseDialogVisible.value = false
  } catch {
    // error handled by interceptor
  } finally {
    reviewing.value = false
  }
}

function showReviseDialog() {
  revisedResult.value = ''
  reviseRemark.value = ''
  reviseDialogVisible.value = true
}

async function handleGenerateReport() {
  const reportId = result.value?.report_id
  if (!reportId) {
    ElMessage.error('未找到报告记录')
    return
  }
  generatingReport.value = true
  try {
    const res: any = await regenerateReportApi(reportId)
    if (res.data?.ai_generated_content) {
      reportContent.value = res.data.ai_generated_content
    } else if (res.data?.findings || res.data?.impression) {
      const parts: string[] = []
      if (res.data.findings) parts.push('【检查所见】\n' + res.data.findings)
      if (res.data.impression) parts.push('【诊断意见】\n' + res.data.impression)
      if (res.data.recommendations) parts.push('【建议】\n' + res.data.recommendations)
      reportContent.value = parts.join('\n\n')
    }
    ElMessage.success('报告生成成功')
  } catch {
    // error handled by interceptor
  } finally {
    generatingReport.value = false
  }
}

// 图片转Base64（确保打印时图片正常显示）
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
  } catch {
    return ''
  }
}

async function handlePrintReport() {
  const r = result.value
  if (!r) return

  const patientInfo = currentPatient.value
  const patientName = patientInfo?.name || '-'
  const patientGender = patientInfo?.gender === 'male' ? '男' : (patientInfo?.gender === 'female' ? '女' : '-')
  const patientAge = patientInfo?.age ? `${patientInfo.age}岁` : '-'
  const patientNo = patientInfo?.patient_no || '-'
  const imageSrc = imagePreviewUrl.value || r.image_url || ''
  const heatmapSrc = r.heatmap_url || ''
  const resultCn = resultLabel.value
  const confidence = topConfidence.value
  const recordNo = r.diagnosis_no || '-'
  const reportText = reportContent.value || ''

  const resultColor = topResult.value === 'normal' ? '#06B6D4' : '#D97706'
  const resultBg = topResult.value === 'normal' ? '#ECFDF5' : '#FFFBEB'
  const resultIcon = topResult.value === 'normal' ? '&#10003;' : '&#9888;'

  const now = new Date()
  const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  // 概率条HTML（前5种）
  const probBarsHtml = top5Probs.value.map((p: any) => {
    const pct = (p.probability * 100).toFixed(1)
    const color = probColor(p.disease_code)
    return `<div class="pr">
      <span class="pl">${p.disease_name_zh}</span>
      <div class="pw"><div class="pf" style="background:${color};width:${pct}%"></div></div>
      <span class="pv">${pct}%</span>
    </div>`
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
      ${heatmapBase64 ? `<div class="ib">
        <div class="il">Grad-CAM 热力图</div>
        <div class="iw"><img src="${heatmapBase64}" /></div>
      </div>` : ''}
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
</div>
</body></html>`)
  printWin.document.close()
  setTimeout(() => printWin.print(), 500)
}

onMounted(async () => {
  // 重置状态
  selectedFile.value = null
  if (imagePreviewUrl.value && imagePreviewUrl.value.startsWith('blob:')) {
    URL.revokeObjectURL(imagePreviewUrl.value)
  }
  imagePreviewUrl.value = ''
  result.value = null
  reportContent.value = ''

  // 加载患者列表
  try {
    const res: any = await getPatientsApi({ per_page: 200 })
    patientList.value = res.data.items
  } catch { /* handled */ }
})
</script>

<style scoped lang="scss">
.diagnosis-page {

  // ========== 流程步骤指示器 ==========
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
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 1px;
      background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.3), transparent);
    }

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
          background: rgba(34, 211, 238, 0.15);
          border-color: var(--primary);
          box-shadow: 0 0 20px rgba(34, 211, 238, 0.2);

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

  // ========== 分区卡片通用样式 ==========
  .zone-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }

  .zone-card {
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    overflow: hidden;
    transition: all 0.4s ease;
    position: relative;

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
      border-color: rgba(34, 211, 238, 0.3);
      box-shadow: 0 0 30px rgba(34, 211, 238, 0.08);
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
        background: rgba(34, 211, 238, 0.15);
        border: 1px solid rgba(34, 211, 238, 0.3);
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

        &.report-badge {
          background: rgba(139, 92, 246, 0.15);
          border-color: rgba(139, 92, 246, 0.3);
          color: var(--purple);
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

  .empty-zone,
  .result-zone,
  .report-zone {
    margin-bottom: 20px;
  }

  // ========== 患者挂号区 ==========
  .patient-brief {
    display: flex;
    gap: 14px;
    padding: 14px 16px;
    background: rgba(34, 211, 238, 0.06);
    border: 1px solid rgba(34, 211, 238, 0.15);
    border-radius: var(--radius-lg);
    margin-bottom: 16px;

    .brief-avatar {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(34, 211, 238, 0.2), rgba(34, 211, 238, 0.1));
      border: 1px solid rgba(34, 211, 238, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 18px;
      color: var(--primary);
      flex-shrink: 0;
    }

    .brief-info {
      flex: 1;
      min-width: 0;

      .brief-name {
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;

        .brief-gender {
          font-size: 11px;
          padding: 2px 8px;
          border-radius: 10px;
          font-weight: 600;

          &.male {
            background: rgba(59, 130, 246, 0.2);
            color: var(--blue);
          }

          &.female {
            background: rgba(236, 72, 153, 0.2);
            color: #F472B6;
          }
        }

        .brief-age {
          font-size: 13px;
          color: var(--text-secondary);
          font-weight: 400;
        }
      }

      .brief-no {
        font-size: 12px;
        color: var(--text-muted);
        font-family: 'Courier New', monospace;
      }

      .brief-history {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }

  // ========== 影像检查区 ==========
  .upload-area {
    margin-bottom: 4px;
  }

  .upload-inner {
    width: 100%;
  }

  .diagnose-btn {
    height: 44px;
    font-size: 15px;
    font-weight: 600;
    border-radius: var(--radius-md) !important;
    background: linear-gradient(135deg, var(--primary), #06B6D4) !important;
    border: none !important;
    letter-spacing: 1px;

    &:hover {
      box-shadow: 0 8px 24px rgba(34, 211, 238, 0.4) !important;
    }

    &:disabled {
      opacity: 0.5;
    }
  }

  .glass-upload-area {
    width: 100%;
    min-height: 200px;
    background: var(--bg-tertiary);
    // border: 2px dashed var(--glass-border);
    border-radius: var(--radius-lg);
    transition: all 0.3s ease;
    overflow: hidden;

    &:hover {
      border-color: var(--glass-border-hover);
      background: var(--bg-tertiary);
    }

    &.has-file {
      border-style: solid;
      border-color: var(--primary);
    }

    :deep(.el-upload) {
      width: 100%;
    }

    :deep(.el-upload-dragger) {
      background: transparent;
      border: none;
      border-radius: var(--radius-lg);
      padding: 0;
    }
  }

  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60px 20px;

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

    .upload-formats {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 10px;
      opacity: 0.7;
    }
  }

  .upload-preview {
    position: relative;

    img {
      width: 100%;
      height: 200px;
      object-fit: contain;
      display: block;
    }

    .preview-overlay {
      position: absolute;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 6px;
      opacity: 0;
      transition: opacity 0.3s ease;
      cursor: pointer;
      color: var(--text-primary);

      span {
        font-size: 12px;
      }
    }

    &:hover .preview-overlay {
      opacity: 1;
    }
  }

  // ========== 诊断结果区 ==========
  .result-layout {
    display: grid;
    grid-template-columns: 240px 1fr 200px;
    gap: 16px;
    align-items: start;
  }

  .result-images {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .image-box {
      .image-label {
        font-size: 12px;
        color: var(--text-secondary);
        margin-bottom: 6px;
        font-weight: 600;
      }

      .preview-img-wrapper {
        width: 100%;
        height: 160px;
        border-radius: var(--radius-md);
        background: var(--bg-tertiary);
        border: 1px solid var(--glass-border);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;

        &.has-image {
          background: var(--card-bg);
        }

        .preview-img {
          width: 100%;
          height: 100%;
        }

        .image-placeholder,
        .image-error {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
          color: var(--text-muted);
          font-size: 11px;
        }

        .image-error {
          color: var(--orange);
        }
      }
    }
  }

  .result-hero {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 18px 20px;
    border-radius: var(--radius-lg);
    margin-bottom: 16px;
    text-align: center;
    border: 2px solid;

    &.normal {
      background: linear-gradient(135deg, rgba(34, 211, 238, 0.12), rgba(34, 211, 238, 0.05));
      border-color: rgba(34, 211, 238, 0.3);
    }

    &.abnormal {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.05));
      border-color: rgba(245, 158, 11, 0.3);
    }

    .result-hero-icon {
      font-size: 40px;
      flex-shrink: 0;
    }

    &.normal .result-hero-icon {
      color: var(--primary);
    }

    &.abnormal .result-hero-icon {
      color: var(--orange);
    }

    .result-hero-text {
      .result-hero-label {
        font-size: 20px;
        font-weight: 700;
      }

      .result-hero-conf {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 3px;
      }
    }

    &.normal .result-hero-label {
      color: var(--primary);
    }

    &.abnormal .result-hero-label {
      color: var(--orange);
    }
  }

  // 患者信息区域
  .patient-info-section {
    background: rgba(34, 211, 238, 0.04);
    border: 1px solid rgba(34, 211, 238, 0.12);
    border-radius: var(--radius-md);
    padding: 14px;
    margin-bottom: 14px;

    .section-title {
      font-size: 12px;
      font-weight: 600;
      color: var(--primary);
      margin-bottom: 10px;
      padding-bottom: 6px;
      border-bottom: 1px solid rgba(34, 211, 238, 0.15);
    }

    .patient-info-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 16px;

      .info-row {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;

        &.full-width {
          grid-column: 1 / -1;
        }

        .info-label {
          color: var(--text-muted);
          flex-shrink: 0;
          min-width: 60px;
        }

        .info-value {
          color: var(--text-primary);
          font-weight: 500;

          &.mono {
            font-family: 'Courier New', monospace;
            font-size: 11px;
          }
        }
      }
    }
  }

  .prob-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 14px;

    .prob-item {
      .prob-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 5px;

        .prob-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          flex-shrink: 0;
        }

        .prob-label {
          font-size: 12px;
          color: var(--text-secondary);
          flex: 1;
        }

        .prob-value {
          font-size: 12px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }

      .prob-bar {
        height: 5px;
        background: var(--bg-tertiary);
        border-radius: 3px;
        overflow: hidden;

        .prob-fill {
          height: 100%;
          border-radius: 3px;
          transition: width 0.6s ease;
        }
      }
    }
  }

  .result-meta {
    display: flex;
    gap: 16px;
    padding-top: 10px;
    border-top: 1px solid var(--glass-border);

    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;

      .meta-label {
        font-size: 11px;
        color: var(--text-muted);
      }

      .meta-value {
        font-size: 12px;
        color: var(--text-secondary);
        font-weight: 500;

        &.mono {
          font-family: 'Courier New', monospace;
        }
      }
    }
  }

  // 操作面板
  .result-actions-panel {
    background: var(--card-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 16px;
    display: flex;
    flex-direction: column;

    .action-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-secondary);
      margin-bottom: 12px;
    }

    .action-buttons {
      display: flex;
      flex-direction: column;
      gap: 8px;
      width: 100%;

      .action-btn {
        width: 100%;
        height: 38px;
        border-radius: var(--radius-md) !important;
        font-size: 13px;
        font-weight: 500;
        padding: 0;
        margin: 0;
        box-sizing: border-box;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;

        &.confirm {
          background: linear-gradient(135deg, var(--primary), #06B6D4) !important;
          border: none !important;
          color: #fff !important;
        }

        &.revise {
          background: rgba(245, 158, 11, 0.15) !important;
          border: 1px solid rgba(245, 158, 11, 0.3) !important;
          color: var(--orange) !important;
        }

        &.report {
          background: linear-gradient(135deg, var(--purple), #7C3AED) !important;
          border: none !important;
          color: #fff !important;

          &.report-pending {
            background: linear-gradient(135deg, var(--primary), #06B6D4) !important;
            animation: reportPulse 2s ease-in-out infinite;
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.4) !important;
          }
        }
      }
    }

    .action-note {
      font-size: 10px;
      color: var(--text-muted);
      text-align: center;
      margin-top: 12px;
      line-height: 1.5;
      padding: 0 4px;
    }
  }

  // ========== 空状态 ==========
  .empty-zone .empty-state {
    text-align: center;
    padding: 60px 20px;

    .empty-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 20px;
      background: var(--glass-bg);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);

      svg {
        width: 40px;
        height: 40px;
      }
    }

    h3 {
      font-size: 18px;
      color: var(--text-secondary);
      font-weight: 600;
      margin-bottom: 8px;
    }

    p {
      font-size: 14px;
      color: var(--text-muted);
    }
  }

  // ========== 诊断报告区 ==========
  .report-zone {
    margin-bottom: 20px;

    .report-toolbar {
      display: flex;
      gap: 8px;
    }
  }

  .report-content-wrapper {
    .report-header {
      text-align: center;
      padding-bottom: 16px;
      margin-bottom: 20px;
      border-bottom: 2px solid var(--glass-border);

      .report-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: 2px;
      }
    }

    .report-body {
      margin-bottom: 20px;

      .report-text-content {
        flex: 1;

        .report-pre {
          font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
          font-size: 13px;
          line-height: 2;
          color: var(--text-secondary);
          white-space: pre-wrap;
          word-break: break-all;
          margin: 0;
          padding: 20px;
          background: var(--bg-tertiary);
          border: 1px solid var(--glass-border);
          border-radius: var(--radius-lg);
        }
      }
    }

    .report-footer {
      text-align: center;
      padding-top: 16px;
      border-top: 1px solid var(--glass-border);
      color: var(--text-muted);
      font-size: 12px;

      .report-footer-item {
        margin-bottom: 3px;
      }
    }
  }

  // ========== 响应式 ==========
  @media (max-width: 1200px) {
    .result-layout {
      grid-template-columns: 220px 1fr 180px;
      gap: 12px;
    }
  }

  @media (max-width: 1024px) {
    .result-layout {
      grid-template-columns: 1fr 1fr;
    }

    .result-actions-panel {
      grid-column: 1 / -1;

      .action-buttons {
        flex-direction: row;
      }
    }
  }

  @media (max-width: 768px) {
    .flow-steps {
      flex-wrap: wrap;
      padding: 16px;
      gap: 8px;

      .step-line {
        display: none;
      }

      .step {
        flex: 1;
        min-width: 140px;

        .step-info .step-desc {
          display: none;
        }
      }
    }

    .zone-grid {
      grid-template-columns: 1fr;
    }

    .result-layout {
      grid-template-columns: 1fr;
    }

    .result-actions-panel .action-buttons {
      flex-direction: column;
    }
  }
}

@keyframes reportPulse {
  0%, 100% { box-shadow: 0 0 12px rgba(16, 185, 129, 0.4); }
  50% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.7); }
}
</style>
