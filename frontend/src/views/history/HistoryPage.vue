<template>
  <div class="history-page">
    <div class="glass-card">
      <!-- 搜索筛选 -->
      <div class="filter-bar">
        <div class="filter-item">
          <el-input v-model="filters.keyword" placeholder="患者姓名/编号/记录号" clearable @keyup.enter="search"
            class="filter-input">
            <template #prefix><el-icon>
                <Search />
              </el-icon></template>
          </el-input>
        </div>
        <div class="filter-item">
          <span class="filter-label">诊断结果</span>
          <el-select v-model="filters.result" placeholder="全部" clearable>
            <el-option v-for="d in diseaseOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
        </div>
        <div class="filter-item">
          <span class="filter-label">审核状态</span>
          <el-select v-model="filters.status" placeholder="全部" clearable>
            <el-option label="待审核" value="pending_review" />
            <el-option label="已审核" value="reviewed" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </div>
        <div class="filter-item">
          <span class="filter-label">诊断日期</span>
          <el-date-picker v-model="filters.dateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
            end-placeholder="结束日期" value-format="YYYY-MM-DD" />
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
      </div>

      <!-- 数据表格 -->
      <el-table :data="tableData" v-loading="loading" empty-text="暂无诊断记录" class="glass-table">
        <el-table-column prop="diagnosis_no" label="记录编号" width="180" show-overflow-tooltip />
        <el-table-column label="患者信息" width="160">
          <template #default="{ row }">
            <span>{{ row.patient_name || '-' }}</span>
            <span class="text-muted"> ({{ row.patient_age || '-' }}岁)</span>
          </template>
        </el-table-column>
        <el-table-column label="AI诊断结果" width="120">
          <template #default="{ row }">
            <span class="result-badge" :class="topResultClass(row)">{{ topResultName(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="置信度" width="100">
          <template #default="{ row }">
            <span
              :style="{ color: topConfidence(row) > 0.9 ? 'var(--primary)' : topConfidence(row) > 0.6 ? 'var(--orange)' : 'var(--red)' }">
              {{ (topConfidence(row) * 100).toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="审核状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.report_status]" size="small">{{ statusLabelMap[row.report_status]
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="诊断时间" width="170" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" class="action-link" @click="viewDetail(row)">详情</el-button>
            <el-button type="success" link size="small" class="action-link" @click="viewImage(row)">影像</el-button>
            <el-button type="warning" link size="small" class="action-link" @click="handlePrint(row)"
              :loading="printLoadingMap[row.id]">打印</el-button>
            <el-popconfirm title="确定删除此记录？" @confirm="handleDelete(row)">
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
          :total="pagination.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData" @current-change="fetchData" />
      </div>
    </div>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="" width="920px" top="3vh" custom-class="diagnosis-detail-dialog"
      class="dark-dialog">
      <div class="detail-content" v-if="currentRecord">
        <!-- 标题栏 -->
        <div class="detail-header">
          <div class="header-left">
            <div class="hospital-badge">
              <el-icon>
                <FirstAidKit />
              </el-icon>
              <span>胸影智诊系统</span>
            </div>
            <h2 class="detail-title">胸部X光诊断报告</h2>
            <div class="record-no">记录编号: {{ currentRecord.diagnosis_no }}</div>
          </div>
          <div class="header-right">
            <div class="status-indicator" :class="currentRecord.report_status">
              <el-icon v-if="currentRecord.report_status === 'reviewed'">
                <CircleCheck />
              </el-icon>
              <el-icon v-else-if="currentRecord.report_status === 'rejected'">
                <Edit />
              </el-icon>
              <el-icon v-else>
                <Clock />
              </el-icon>
              <span>{{ statusLabelMap[currentRecord.report_status] }}</span>
            </div>
          </div>
        </div>

        <!-- 患者信息横条 -->
        <div class="patient-strip" v-if="currentRecord.patient">
          <div class="strip-item">
            <div class="strip-avatar">{{ currentRecord.patient.name?.charAt(0) || '患' }}</div>
            <div class="strip-info">
              <div class="strip-name">{{ currentRecord.patient.name || '-' }}</div>
              <div class="strip-meta">
                {{ currentRecord.patient.gender === 'male' ? '男' : '女' }} &middot;
                {{ currentRecord.patient.age || '-' }}岁 &middot;
                编号: {{ currentRecord.patient.patient_no || '-' }}
              </div>
            </div>
          </div>
          <div class="strip-item" v-if="currentRecord.patient.medical_history">
            <span class="strip-label">既往史</span>
            <span class="strip-value text-ellipsis">{{ currentRecord.patient.medical_history }}</span>
          </div>
        </div>

        <!-- 影像 + AI结果 双栏 -->
        <div class="content-grid">
          <!-- 左：影像并排 -->
          <div class="images-col">
            <div class="img-box">
              <div class="img-label">原始胸部X光片</div>
              <div class="img-wrapper">
                <el-image :src="imgUrl(currentRecord.image_path)" fit="contain"
                  :preview-src-list="currentRecord.image_path ? [imgUrl(currentRecord.image_path)] : []">
                  <template #error>
                    <div class="img-error"><el-icon>
                        <Picture />
                      </el-icon><span>加载失败</span></div>
                  </template>
                </el-image>
              </div>
            </div>
            <div class="img-box" v-if="currentRecord.heatmap_path">
              <div class="img-label">Grad-CAM 热力图</div>
              <div class="img-wrapper">
                <el-image :src="imgUrl(currentRecord.heatmap_path)" fit="contain"
                  :preview-src-list="[imgUrl(currentRecord.heatmap_path)]">
                  <template #error>
                    <div class="img-error"><el-icon>
                        <Picture />
                      </el-icon><span>加载失败</span></div>
                  </template>
                </el-image>
              </div>
            </div>
          </div>

          <!-- 右：AI结果 + 概率 -->
          <div class="result-col">
            <div class="result-hero" :class="detailTopResult === 'normal' ? 'normal' : 'abnormal'">
              <div class="result-hero-icon">
                <el-icon v-if="detailTopResult === 'normal'">
                  <CircleCheck />
                </el-icon>
                <el-icon v-else>
                  <Warning />
                </el-icon>
              </div>
              <div class="result-hero-text">
                <div class="result-hero-label">{{ detailTopResultName }}</div>
                <div class="result-hero-conf">置信度 {{ detailTopConfidence }}%</div>
              </div>
            </div>

            <div class="prob-section">
              <div class="prob-row" v-for="p in detailTop5Probs" :key="p.disease_code">
                <span class="prob-label">{{ p.disease_name_zh }}</span>
                <div class="prob-bar-wrap">
                  <div class="prob-bar">
                    <div class="prob-fill"
                      :style="{ background: probColor(p.disease_code), width: p.probability * 100 + '%' }">
                    </div>
                  </div>
                </div>
                <span class="prob-val">{{ (p.probability * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <!-- 临床/审核信息 -->
            <div class="meta-section">
              <div class="meta-grid">
                <div class="meta-item">
                  <span class="meta-label">诊断时间</span>
                  <span class="meta-value">{{ currentRecord.created_at }}</span>
                </div>
                <div class="meta-item" v-if="currentRecord.reviewed_at">
                  <span class="meta-label">审核时间</span>
                  <span class="meta-value">{{ currentRecord.reviewed_at }}</span>
                </div>
              </div>
              <div class="meta-row" v-if="currentRecord.patient?.medical_history">
                <span class="meta-label">既往病史</span>
                <span class="meta-value">{{ currentRecord.patient.medical_history }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 诊断报告 -->
        <div class="report-block" v-if="detailReportContent">
          <div class="report-block-title">
            <el-icon>
              <Document />
            </el-icon>
            <span>诊断报告</span>
          </div>
          <pre class="report-pre">{{ detailReportContent }}</pre>
        </div>

        <!-- 底部 -->
        <div class="detail-footer">
          <span>本报告由AI辅助诊断系统生成，仅供临床医生参考</span>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" @click="handlePrintReport">
            <el-icon>
              <Printer />
            </el-icon>
            打印报告
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 影像预览对话框 -->
    <el-dialog v-model="imageVisible" title="影像预览" width="700px" top="5vh" class="dark-dialog">
      <div class="image-compare" v-if="currentRecord">
        <div class="image-box">
          <div class="image-label">原始影像</div>
          <el-image :src="imgUrl(currentRecord.image_path)" fit="contain" class="preview-img" />
        </div>
        <div class="image-box" v-if="currentRecord.heatmap_path">
          <div class="image-label">Grad-CAM热力图</div>
          <el-image :src="imgUrl(currentRecord.heatmap_path)" fit="contain" class="preview-img" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { getDiagnosisListApi, getDiagnosisApi, deleteDiagnosisApi } from '@/api/diagnose'
import { regenerateReportApi } from '@/api/reports'
import { ElMessage } from 'element-plus'

// 图片路径转URL：image_path="images/abc.png" → "/static/images/abc.png"
function imgUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('/static/') || path.startsWith('http')) return path
  return '/static/' + path
}

const loading = ref(false)
const tableData = ref<any[]>([])
const detailVisible = ref(false)
const imageVisible = ref(false)
const currentRecord = ref<any>(null)
const printLoadingMap = ref<Record<number, boolean>>({})

const filters = reactive({ keyword: '', result: '', status: '', dateRange: null as string[] | null })
const pagination = reactive({ page: 1, per_page: 20, total: 0 })

const statusLabelMap: Record<string, string> = {
  pending_review: '待审核',
  reviewed: '已审核',
  rejected: '已拒绝',
}
const statusTypeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
  pending_review: 'warning',
  reviewed: 'success',
  rejected: 'danger',
}

const diseaseOptions = [
  { label: '肺不张', value: 'Atelectasis' },
  { label: '心脏肥大', value: 'Cardiomegaly' },
  { label: '胸腔积液', value: 'Effusion' },
  { label: '浸润', value: 'Infiltration' },
  { label: '肿块', value: 'Mass' },
  { label: '结节', value: 'Nodule' },
  { label: '肺炎', value: 'Pneumonia' },
  { label: '气胸', value: 'Pneumothorax' },
  { label: '实变', value: 'Consolidation' },
  { label: '水肿', value: 'Edema' },
  { label: '肺气肿', value: 'Emphysema' },
  { label: '纤维化', value: 'Fibrosis' },
  { label: '胸膜增厚', value: 'Pleural_Thickening' },
  { label: '疝', value: 'Hernia' },
]

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

// 列表行的辅助函数
function topConfidence(row: any): number {
  if (!row.top_diseases?.length) return 0
  return row.top_diseases[0].probability
}

function topResultName(row: any): string {
  if (!row.top_diseases?.length || row.top_diseases[0].probability < 0.3) return '正常'
  return row.top_diseases[0].disease_name_zh
}

function topResultClass(row: any): string {
  if (!row.top_diseases?.length || row.top_diseases[0].probability < 0.3) return 'normal'
  return 'abnormal'
}

// 详情对话框的推导属性
const detailSortedProbs = computed(() => {
  if (!currentRecord.value?.probabilities?.length) return []
  return [...currentRecord.value.probabilities].sort((a: any, b: any) => b.probability - a.probability)
})

const detailTopResult = computed(() => {
  if (!detailSortedProbs.value.length || detailSortedProbs.value[0].probability < 0.3) return 'normal'
  return detailSortedProbs.value[0].disease_code
})

const detailTopResultName = computed(() => {
  if (detailTopResult.value === 'normal') return '正常'
  return detailSortedProbs.value[0]?.disease_name_zh || '-'
})

const detailTopConfidence = computed(() => {
  if (!detailSortedProbs.value.length) return '0.0'
  return (detailSortedProbs.value[0].probability * 100).toFixed(1)
})

const detailTop5Probs = computed(() => detailSortedProbs.value.slice(0, 5))

const detailReportContent = computed(() => {
  const reports = currentRecord.value?.reports
  if (!reports?.length) return ''
  const r = reports[0]
  const parts: string[] = []
  if (r.findings) parts.push('【检查所见】\n' + r.findings)
  if (r.impression) parts.push('【诊断意见】\n' + r.impression)
  if (r.recommendations) parts.push('【建议】\n' + r.recommendations)
  return parts.join('\n\n')
})

function buildParams() {
  const p: any = { page: pagination.page, per_page: pagination.per_page }
  if (filters.keyword) p.keyword = filters.keyword
  if (filters.result) p.disease = filters.result
  if (filters.status) p.status = filters.status
  if (filters.dateRange?.length === 2) {
    p.start_date = filters.dateRange[0]
    p.end_date = filters.dateRange[1]
  }
  return p
}

async function fetchData() {
  loading.value = true
  try {
    const res: any = await getDiagnosisListApi(buildParams())
    tableData.value = res.data.items
    pagination.total = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

function search() { pagination.page = 1; fetchData() }

function resetFilters() {
  filters.keyword = ''; filters.result = ''; filters.status = ''; filters.dateRange = null
  search()
}

async function viewDetail(row: any) {
  try {
    const res: any = await getDiagnosisApi(row.id)
    currentRecord.value = res.data
    detailVisible.value = true
  } catch { /* handled */ }
}

function viewImage(row: any) {
  currentRecord.value = row
  imageVisible.value = true
}

async function handleDelete(row: any) {
  try {
    await deleteDiagnosisApi(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch { /* handled */ }
}

// 将图片URL转为base64（用于打印窗口跨域渲染）
function imageToBase64(url: string): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.naturalWidth
      canvas.height = img.naturalHeight
      canvas.getContext('2d')!.drawImage(img, 0, 0)
      try { resolve(canvas.toDataURL('image/jpeg', 0.85)) }
      catch { resolve(url) }
    }
    img.onerror = () => resolve('')
    img.src = url
  })
}

// 从表格直接打印
async function handlePrint(row: any) {
  printLoadingMap.value[row.id] = true
  try {
    // 先加载详情
    const res: any = await getDiagnosisApi(row.id)
    currentRecord.value = res.data
    await printRecord(res.data)
  } catch {
    ElMessage.error('打印失败，请重试')
  } finally {
    printLoadingMap.value[row.id] = false
  }
}

// 从详情对话框打印
function handlePrintReport() {
  const r = currentRecord.value
  if (!r) return
  printRecord(r)
}

// 核心打印逻辑
async function printRecord(r: any) {
  const patient = r.patient || {}
  const patientName = patient.name || '-'
  const patientGender = patient.gender === 'male' ? '男' : (patient.gender === 'female' ? '女' : '-')
  const patientAge = patient.age ? `${patient.age}岁` : '-'
  const patientNo = patient.patient_no || '-'
  const imageSrc = imgUrl(r.image_path)
  const heatmapSrc = imgUrl(r.heatmap_path)

  // 推导主结果
  const probs = r.probabilities || []
  const sorted = [...probs].sort((a: any, b: any) => b.probability - a.probability)
  const isNormal = !sorted.length || sorted[0].probability < 0.3
  const resultCn = isNormal ? '正常' : (sorted[0].disease_name_zh || '-')
  const confidence = sorted.length ? (sorted[0].probability * 100).toFixed(1) : '0.0'
  const recordNo = r.diagnosis_no || '-'

  // 报告内容
  const reports = r.reports || []
  let reportText = ''
  if (reports.length) {
    const rp = reports[0]
    const parts: string[] = []
    if (rp.findings) parts.push('【检查所见】\n' + rp.findings)
    if (rp.impression) parts.push('【诊断意见】\n' + rp.impression)
    if (rp.recommendations) parts.push('【建议】\n' + rp.recommendations)
    reportText = parts.join('\n\n')
  }

  const resultColor = isNormal ? '#06B6D4' : '#D97706'
  const resultBg = isNormal ? '#ECFDF5' : '#FFFBEB'
  const resultIcon = isNormal ? '&#10003;' : '&#9888;'

  const now = new Date()
  const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  // 概率条HTML（前5种）
  const probBarsHtml = sorted.slice(0, 5).map((p: any) => {
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
  if (!printWin) {
    ElMessage.error('弹出窗口被浏览器拦截，请允许弹出窗口后重试')
    return
  }
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
</style>

<!-- 非 scoped 全局样式：Element Plus 对话框传送至 body，scoped 无法穿透 -->
<style lang="scss">
.dark-dialog {
  .el-dialog {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--glass-border);
    border-radius: 16px;
  }

  .el-dialog__header {
    background: transparent;
    border-bottom: 1px solid var(--glass-border);
    padding: 16px 20px;

    .el-dialog__title {
      color: var(--text-primary);
    }

    .el-dialog__headerbtn .el-dialog__close {
      color: var(--text-muted);
    }
  }

  .el-dialog__body {
    background: transparent;
    color: var(--text-secondary);
  }

  .el-dialog__footer {
    background: transparent;
    border-top: 1px solid var(--glass-border);
  }
}

.diagnosis-detail-dialog {
  background: var(--bg-secondary) !important;
  border: 1px solid var(--glass-border);
  border-radius: 16px;

  .el-dialog__header {
    display: none;
  }

  .el-dialog__body {
    padding: 20px;
    max-height: 80vh;
    overflow-y: auto;
    background: transparent;
    color: var(--text-secondary);
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid var(--glass-border);
    background: transparent;
  }
}

// 操作按钮去掉背景色，只保留文字颜色
.action-link {
  background: transparent !important;
  padding: 2px 6px !important;

  &:hover {
    background: transparent !important;
    opacity: 0.8;
  }
}
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
          <div class="pi-row"><span class="pi-lb">诊断时间</span><span class="pi-vl">${r.created_at || now.toLocaleString('zh-CN')}</span></div>
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

onMounted(() => fetchData())
</script>

<style scoped lang="scss">
.history-page {

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
      gap: 6px;

      .filter-label {
        font-size: 12px;
        color: var(--text-secondary);
        white-space: nowrap;
        flex-shrink: 0;
      }

      .filter-input {
        width: 200px;
      }
    }

    .filter-actions {
      margin-left: auto;
      display: flex;
      gap: 8px;
    }
  }

  // 诊断结果徽标
  .result-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 600;

    &.normal {
      background: rgba(34, 211, 238, 0.2);
      color: var(--primary);
    }

    &.abnormal {
      background: rgba(245, 158, 11, 0.2);
      color: var(--orange);
    }
  }

  .text-muted {
    color: var(--text-muted);
    font-size: 12px;
  }

  .text-ellipsis {
    display: -webkit-box;
    -webkit-line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

  // 影像预览对话框
  .image-compare {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;

    .image-label {
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 8px;
      font-weight: 500;
    }

    .preview-img {
      width: 100%;
      max-height: 450px;
      border-radius: var(--radius-md);
      background: var(--glass-bg);
      border: 1px solid var(--glass-border);
    }
  }
}

// ===== 详情对话框 =====
.detail-content {
  color: var(--text-secondary);

  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    background: linear-gradient(135deg, rgba(34, 211, 238, 0.08), rgba(59, 130, 246, 0.08));
    border-radius: 14px;
    margin-bottom: 16px;
    border: 1px solid var(--glass-border);

    .header-left {
      .hospital-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 4px;
      }

      .detail-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 4px;
      }

      .record-no {
        font-size: 12px;
        color: var(--text-muted);
        font-family: 'Courier New', monospace;
      }
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;

      &.reviewed {
        background: rgba(34, 211, 238, 0.15);
        color: var(--primary);
        border: 1px solid rgba(34, 211, 238, 0.3);
      }

      &.pending_review {
        background: rgba(59, 130, 246, 0.15);
        color: var(--blue);
        border: 1px solid rgba(59, 130, 246, 0.3);
      }

      &.rejected {
        background: rgba(245, 158, 11, 0.15);
        color: var(--orange);
        border: 1px solid rgba(245, 158, 11, 0.3);
      }
    }
  }

  // 患者信息横条
  .patient-strip {
    display: flex;
    align-items: center;
    gap: 24px;
    padding: 12px 20px;
    background: var(--card-bg);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    margin-bottom: 16px;
    backdrop-filter: blur(10px);

    .strip-item {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .strip-avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      background: linear-gradient(135deg, rgba(34, 211, 238, 0.2), rgba(34, 211, 238, 0.1));
      border: 1px solid rgba(34, 211, 238, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      font-weight: 700;
      color: var(--primary);
      flex-shrink: 0;
    }

    .strip-name {
      font-size: 15px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .strip-meta {
      font-size: 12px;
      color: var(--text-muted);
    }

    .strip-label {
      font-size: 11px;
      color: var(--text-muted);
      flex-shrink: 0;
    }

    .strip-value {
      font-size: 12px;
      color: var(--text-secondary);
      max-width: 260px;
    }
  }

  // 双栏内容
  .content-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }

  // 左列：影像
  .images-col {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .img-box {
      background: var(--card-bg);
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      overflow: hidden;
      transition: border-color 0.3s;

      &:hover {
        border-color: var(--primary);
      }

      .img-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-muted);
        padding: 8px 12px 0;
      }

      .img-wrapper {
        padding: 8px 12px 12px;
        height: 200px;

        :deep(.el-image) {
          width: 100%;
          height: 100%;
          border-radius: 8px;
        }
      }

      .img-error {
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        color: var(--text-muted);
        font-size: 12px;

        .el-icon {
          font-size: 32px;
        }
      }
    }
  }

  // 右列：AI结果
  .result-col {
    display: flex;
    flex-direction: column;
    gap: 12px;

    .result-hero {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 16px 20px;
      border-radius: 12px;
      border: 2px solid;

      &.normal {
        background: linear-gradient(135deg, rgba(34, 211, 238, 0.12), rgba(34, 211, 238, 0.04));
        border-color: rgba(34, 211, 238, 0.3);
      }

      &.abnormal {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0.04));
        border-color: rgba(245, 158, 11, 0.3);
      }

      .result-hero-icon {
        font-size: 36px;
        flex-shrink: 0;
      }

      &.normal .result-hero-icon {
        color: var(--primary);
      }

      &.abnormal .result-hero-icon {
        color: var(--orange);
      }

      .result-hero-label {
        font-size: 20px;
        font-weight: 700;
      }

      &.normal .result-hero-label {
        color: var(--primary);
      }

      &.abnormal .result-hero-label {
        color: var(--orange);
      }

      .result-hero-conf {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 2px;
      }
    }

    .prob-section {
      background: var(--card-bg);
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      padding: 14px 16px;

      .prob-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;

        &:last-child {
          margin-bottom: 0;
        }

        .prob-label {
          width: 56px;
          font-size: 12px;
          color: var(--text-muted);
          font-weight: 500;
          text-align: right;
          flex-shrink: 0;
        }

        .prob-bar-wrap {
          flex: 1;
          height: 6px;
          background: var(--bg-tertiary);
          border-radius: 3px;
          overflow: hidden;
        }

        .prob-bar {
          height: 100%;
          border-radius: 3px;
          transition: width 0.6s ease;
        }

        .prob-val {
          width: 50px;
          font-size: 12px;
          font-weight: 600;
          color: var(--text-primary);
          text-align: right;
          flex-shrink: 0;
        }
      }
    }

    .meta-section {
      background: var(--card-bg);
      border: 1px solid var(--glass-border);
      border-radius: 12px;
      padding: 14px 16px;
      flex: 1;

      .meta-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px 16px;
        margin-bottom: 10px;

        .meta-item {
          .meta-label {
            font-size: 11px;
            color: var(--text-muted);
            display: block;
            margin-bottom: 2px;
          }

          .meta-value {
            font-size: 13px;
            color: var(--text-primary);
            font-weight: 600;
          }
        }
      }

      .meta-row {
        display: flex;
        gap: 8px;
        margin-bottom: 6px;
        font-size: 12px;
        line-height: 1.6;

        &:last-child {
          margin-bottom: 0;
        }

        .meta-label {
          color: var(--text-muted);
          min-width: 56px;
          flex-shrink: 0;
          font-weight: 500;
        }

        .meta-value {
          color: var(--text-secondary);
          flex: 1;
        }
      }
    }
  }

  // 诊断报告
  .report-block {
    background: var(--card-bg);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;

    .report-block-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--glass-border);

      .el-icon {
        color: var(--primary);
        font-size: 18px;
      }
    }

    .report-pre {
      white-space: pre-wrap;
      font-family: 'Microsoft YaHei', sans-serif;
      font-size: 13px;
      line-height: 1.8;
      color: var(--text-secondary);
      margin: 0;
      background: var(--bg-tertiary);
      padding: 14px;
      border-radius: 8px;
      border: 1px solid var(--glass-border);
    }
  }

  // 底部签名
  .detail-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0 0;
    border-top: 1px solid var(--glass-border);
    font-size: 11px;
    color: var(--text-muted);
  }
}

// 对话框底部按钮
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
}

// 对话框样式覆盖（scoped :deep）
:deep(.dark-dialog) {
  .el-dialog {
    background: var(--bg-secondary);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
  }

  .el-dialog__header {
    background: transparent;
    border-bottom: 1px solid var(--glass-border);
    padding: 16px 20px;

    .el-dialog__title {
      color: var(--text-primary);
    }

    .el-dialog__headerbtn .el-dialog__close {
      color: var(--text-muted);
    }
  }

  .el-dialog__body {
    background: transparent;
  }
}

// 深度选择器覆盖Element Plus样式
::deep(.diagnosis-detail-dialog) {
  background: var(--bg-secondary);
  border: 1px solid var(--glass-border);
  border-radius: 16px;

  .el-dialog__header {
    display: none;
  }

  .el-dialog__body {
    padding: 20px;
    max-height: 80vh;
    overflow-y: auto;
    background: transparent;
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid var(--glass-border);
    background: transparent;
  }
}

// 响应式
@media (max-width: 768px) {
  .detail-content {
    .detail-header {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;
    }

    .patient-strip {
      flex-direction: column;
      gap: 8px;
    }

    .content-grid {
      grid-template-columns: 1fr;
    }

    .meta-section .meta-grid {
      grid-template-columns: 1fr;
    }

    .detail-footer {
      flex-direction: column;
      gap: 4px;
    }
  }
}

// 操作按钮去掉背景色，只保留文字颜色
.action-link {
  background: transparent !important;
  padding: 2px 6px !important;

  &:hover {
    background: transparent !important;
    opacity: 0.8;
  }
}
</style>

<!-- 非 scoped 全局样式：Element Plus 对话框传送至 body，scoped 无法穿透 -->
<style lang="scss">
.dark-dialog {
  .el-dialog {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--glass-border);
    border-radius: 16px;
  }

  .el-dialog__header {
    background: transparent;
    border-bottom: 1px solid var(--glass-border);
    padding: 16px 20px;

    .el-dialog__title {
      color: var(--text-primary);
    }

    .el-dialog__headerbtn .el-dialog__close {
      color: var(--text-muted);
    }
  }

  .el-dialog__body {
    background: transparent;
    color: var(--text-secondary);
  }

  .el-dialog__footer {
    background: transparent;
    border-top: 1px solid var(--glass-border);
  }
}

.diagnosis-detail-dialog {
  background: var(--bg-secondary) !important;
  border: 1px solid var(--glass-border);
  border-radius: 16px;

  .el-dialog__header {
    display: none;
  }

  .el-dialog__body {
    padding: 20px;
    max-height: 80vh;
    overflow-y: auto;
    background: transparent;
    color: var(--text-secondary);
  }

  .el-dialog__footer {
    padding: 16px 24px;
    border-top: 1px solid var(--glass-border);
    background: transparent;
  }
}

// 操作按钮去掉背景色，只保留文字颜色
.action-link {
  background: transparent !important;
  padding: 2px 6px !important;

  &:hover {
    background: transparent !important;
    opacity: 0.8;
  }
}
</style>
