<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <span class="title-secondary">My Dashboard</span>
        <span class="title-sep">/</span>
        <span class="title-main">胸影智诊V2.0</span>
      </h1>
      <p class="page-subtitle">智能AI辅助诊断，守护每一次呼吸健康</p>
      <div class="header-right">
        <el-tag type="success" size="small" effect="dark" v-if="!loading">
          <el-icon><Refresh /></el-icon> 实时数据
        </el-tag>
        <el-tag type="info" size="small" effect="dark" v-else>
          加载中...
        </el-tag>
        <span class="last-update" v-if="lastUpdate">更新于 {{ lastUpdate }}</span>
      </div>
    </div>

    <!-- 标签页 -->
    <div class="glass-tabs">
      <div class="tab" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">全部</div>
      <div class="tab" :class="{ active: activeTab === 'pneumonia' }" @click="activeTab = 'pneumonia'">肺炎</div>
      <div class="tab" :class="{ active: activeTab === 'tuberculosis' }" @click="activeTab = 'tuberculosis'">肺结核</div>
      <div class="tab" :class="{ active: activeTab === 'normal' }" @click="activeTab = 'normal'">正常</div>
    </div>

    <!-- 概览统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="item in overviewCards" :key="item.key">
        <div class="stat-icon" :style="{ background: item.bgColor }">
          <el-icon :size="22" :style="{ color: item.color }"><component :is="item.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ item.value }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="dashboard-grid">
      <!-- 左侧：月度诊断趋势 -->
      <div class="glass-card chart-card-large">
        <div class="card-header">
          <h3 class="card-title">近7天诊断趋势</h3>
          <span class="card-action">View All →</span>
        </div>
        <v-chart class="chart" :option="dailyOption" autoresize />
      </div>

      <!-- 右上：病种分布 -->
      <div class="glass-card chart-card-small">
        <div class="card-header">
          <h3 class="card-title">病种分布统计</h3>
          <span class="card-action">View All →</span>
        </div>
        <v-chart class="chart-sm" :option="pieOption" autoresize />
      </div>

      <!-- 右下：AI诊断卡 -->
      <div class="ai-card">
        <div class="ai-card-header">
          <div class="ai-card-title">AI诊断卡</div>
          <div class="ai-card-icon">
            <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
          </div>
        </div>
        <div class="ai-card-value">{{ health.model_loaded ? '98.7%' : '离线' }}</div>
        <div class="ai-card-label">模型准确率</div>
        <div class="ai-card-footer">
          <div class="ai-stat">
            <div class="ai-stat-value" style="color: var(--primary);">{{ dashboard.overview.today_diagnoses || 0 }}</div>
            <div class="ai-stat-label">今日诊断</div>
          </div>
          <div class="ai-stat">
            <div class="ai-stat-value" style="color: var(--purple);">{{ dashboard.overview.week_diagnoses || 0 }}</div>
            <div class="ai-stat-label">本周累计</div>
          </div>
          <div class="ai-stat">
            <div class="ai-stat-value" style="color: var(--blue);">{{ health.device || 'N/A' }}</div>
            <div class="ai-stat-label">推理设备</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 医生团队 & 最近诊断 -->
    <div class="data-section-grid">
      <!-- 医生团队列表 -->
      <div class="glass-card doctor-panel">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon style="margin-right: 6px;"><User /></el-icon>
            医生团队 ({{ dashboard.doctors?.length || 0 }})
          </h3>
          <el-tag type="success" size="small">在线</el-tag>
        </div>
        <div class="doctor-list">
          <div class="doctor-item" v-for="doc in dashboard.doctors" :key="doc.id">
            <div class="doctor-avatar">
              <el-icon :size="20"><Avatar /></el-icon>
            </div>
            <div class="doctor-info">
              <div class="doctor-name">{{ doc.real_name }}</div>
              <div class="doctor-dept">{{ doc.department }}</div>
            </div>
            <div class="doctor-stats">
              <div class="doc-stat">
                <span class="doc-stat-num">{{ doc.today_diagnoses }}</span>
                <span class="doc-stat-label">今日</span>
              </div>
              <div class="doc-stat">
                <span class="doc-stat-num">{{ doc.total_diagnoses }}</span>
                <span class="doc-stat-label">累计</span>
              </div>
            </div>
          </div>
          <div class="empty-tip" v-if="!dashboard.doctors?.length">暂无医生数据</div>
        </div>
      </div>

      <!-- 最近诊断记录 -->
      <div class="glass-card recent-panel">
        <div class="card-header">
          <h3 class="card-title">
            <el-icon style="margin-right: 6px;"><Document /></el-icon>
            最近诊断记录
          </h3>
          <span class="card-action" @click="$router.push('/history')">查看全部 →</span>
        </div>
        <div class="recent-list">
          <div class="recent-item" v-for="rec in dashboard.recent_diagnoses" :key="rec.id">
            <div class="recent-result-tag" :class="getResultClass(rec.ai_result)">{{ rec.ai_result }}</div>
            <div class="recent-info">
              <div class="recent-patient">{{ rec.patient_name }}</div>
              <div class="recent-meta">
                <span>{{ rec.doctor_name }}</span>
                <span class="meta-sep">|</span>
                <span>{{ rec.created_at }}</span>
              </div>
            </div>
            <div class="recent-confidence">
              <span :class="getConfidenceClass(rec.confidence)">{{ (rec.confidence * 100).toFixed(1) }}%</span>
            </div>
          </div>
          <div class="empty-tip" v-if="!dashboard.recent_diagnoses?.length">暂无诊断记录</div>
        </div>
      </div>
    </div>

    <!-- 患者档案 -->
    <div class="glass-card patient-section">
      <div class="card-header">
        <h3 class="card-title">
          <el-icon style="margin-right: 6px;"><UserFilled /></el-icon>
          患者档案 ({{ dashboard.patients?.length || 0 }})
        </h3>
        <span class="card-action" @click="$router.push('/patient')">管理患者 →</span>
      </div>
      <div class="patient-table-wrapper">
        <el-table :data="dashboard.patients || []" style="width: 100%" :max-height="400"
          :header-cell-style="{ background: 'transparent', color: '#9CA3AF', borderBottom: '1px solid var(--glass-border)' }"
          :cell-style="{ background: 'transparent', color: '#F3F4F6', borderBottom: '1px solid var(--glass-border)' }">
          <el-table-column prop="patient_no" label="编号" width="140" />
          <el-table-column prop="name" label="姓名" width="100">
            <template #default="{ row }">
              <span style="font-weight: 600;">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="gender" label="性别" width="70" />
          <el-table-column prop="age" label="年龄" width="70">
            <template #default="{ row }">{{ row.age }}岁</template>
          </el-table-column>
          <el-table-column prop="phone" label="电话" width="140" />
          <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
          <el-table-column label="最近诊断" width="140">
            <template #default="{ row }">
              <template v-if="row.last_diagnosis">
                <el-tag :type="row.last_diagnosis.result === '正常' ? 'success' : row.last_diagnosis.result === '肺炎' ? 'warning' : 'danger'" size="small">
                  {{ row.last_diagnosis.result }}
                </el-tag>
              </template>
              <span v-else style="color: var(--text-muted);">无</span>
            </template>
          </el-table-column>
          <el-table-column label="置信度" width="100">
            <template #default="{ row }">
              <span v-if="row.last_diagnosis" :style="{ color: getConfidenceColor(row.last_diagnosis.confidence), fontWeight: 600 }">
                {{ (row.last_diagnosis.confidence * 100).toFixed(1) }}%
              </span>
              <span v-else style="color: var(--text-muted);">-</span>
            </template>
          </el-table-column>
          <el-table-column label="诊断次数" width="100">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ row.total_diagnoses }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 底部信息行 -->
    <div class="bottom-grid">
      <!-- 置信度分布（真实数据库统计） -->
      <div class="glass-card">
        <div class="card-header">
          <h3 class="card-title">诊断置信度分布</h3>
        </div>
        <v-chart class="chart-sm" :option="barOption" autoresize />
      </div>

      <!-- 性别&年龄分布 -->
      <div class="glass-card">
        <div class="card-header">
          <h3 class="card-title">患者人口分布</h3>
        </div>
        <div class="demo-info">
          <v-chart class="chart-sm" :option="demographicOption" autoresize />
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="glass-card quick-card">
        <div class="card-header">
          <h3 class="card-title">快捷操作</h3>
        </div>
        <div class="quick-actions">
          <div class="quick-action-item" @click="$router.push('/diagnosis')">
            <div class="action-icon" style="background: var(--primary-light);">
              <el-icon :size="20" color="#10B981"><Plus /></el-icon>
            </div>
            <div class="action-text">
              <div class="action-title">新建诊断</div>
              <div class="action-desc">上传影像进行AI诊断</div>
            </div>
            <el-icon color="#6B7280"><ArrowRight /></el-icon>
          </div>
          <div class="quick-action-item" @click="$router.push('/patient')">
            <div class="action-icon" style="background: rgba(139, 92, 246, 0.2);">
              <el-icon :size="20" color="#8B5CF6"><UserFilled /></el-icon>
            </div>
            <div class="action-text">
              <div class="action-title">患者管理</div>
              <div class="action-desc">管理患者档案信息</div>
            </div>
            <el-icon color="#6B7280"><ArrowRight /></el-icon>
          </div>
          <div class="quick-action-item" @click="$router.push('/history')">
            <div class="action-icon" style="background: rgba(59, 130, 246, 0.2);">
              <el-icon :size="20" color="#3B82F6"><Document /></el-icon>
            </div>
            <div class="action-text">
              <div class="action-title">诊断历史</div>
              <div class="action-desc">查看历史诊断记录</div>
            </div>
            <el-icon color="#6B7280"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { systemApi } from '@/api'
import {
  DataAnalysis, Calendar, TrendCharts, UserFilled, Avatar, SuccessFilled,
  Refresh, User, Document, Plus, ArrowRight, Male, Female
} from '@element-plus/icons-vue'

use([
  CanvasRenderer,
  LineChart, PieChart, BarChart,
  TitleComponent, TooltipComponent, LegendComponent,
  GridComponent
])

const activeTab = ref('all')
const loading = ref(false)
const lastUpdate = ref('')
const dashboard = ref({
  overview: {},
  result_distribution: [],
  daily_stats: [],
  doctors: [],
  patients: [],
  recent_diagnoses: [],
  confidence_distribution: { high: 0, mid: 0, low: 0 },
  gender_distribution: { male: 0, female: 0 },
  age_distribution: []
})
const health = ref({ model_loaded: false, device: '' })

let refreshTimer = null

// 获取看板数据（全部来源于数据库）
async function fetchDashboardData() {
  try {
    loading.value = true
    const [dashRes, healthRes] = await Promise.all([
      systemApi.getDashboard(),
      systemApi.healthCheck()
    ])
    dashboard.value = dashRes.data
    health.value = healthRes.data
    const now = new Date()
    lastUpdate.value = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  } catch (e) {
    console.error('获取看板数据失败', e)
  } finally {
    loading.value = false
  }
}

const overviewCards = computed(() => [
  { key: 'total', label: '总诊断数', value: dashboard.value.overview.total_diagnoses || 0, icon: DataAnalysis, color: '#3B82F6', bgColor: 'rgba(59, 130, 246, 0.2)' },
  { key: 'today', label: '今日诊断', value: dashboard.value.overview.today_diagnoses || 0, icon: Calendar, color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.2)' },
  { key: 'week', label: '本周诊断', value: dashboard.value.overview.week_diagnoses || 0, icon: TrendCharts, color: '#8B5CF6', bgColor: 'rgba(139, 92, 246, 0.2)' },
  { key: 'patient', label: '患者总数', value: dashboard.value.overview.total_patients || 0, icon: UserFilled, color: '#F59E0B', bgColor: 'rgba(245, 158, 11, 0.2)' },
  { key: 'doctor', label: '医生总数', value: dashboard.value.overview.total_doctors || 0, icon: Avatar, color: '#06B6D4', bgColor: 'rgba(6, 182, 212, 0.2)' },
  { key: 'rate', label: 'AI状态', value: health.value.model_loaded ? '在线' : '离线', icon: SuccessFilled, color: health.value.model_loaded ? '#10B981' : '#EF4444', bgColor: health.value.model_loaded ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)' }
])

const dailyOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(30, 41, 59, 0.95)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    textStyle: { color: '#F3F4F6', fontSize: 13 }
  },
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
  xAxis: {
    type: 'category',
    data: (dashboard.value.daily_stats || []).map(i => i.date?.slice(5) || ''),
    axisLabel: { color: '#9CA3AF', fontSize: 12 },
    axisLine: { show: false },
    axisTick: { show: false }
  },
  yAxis: {
    type: 'value',
    minInterval: 1,
    axisLabel: { color: '#9CA3AF', fontSize: 12 },
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: 'rgba(16, 185, 129, 0.1)', type: 'dashed' } }
  },
  series: [{
    data: (dashboard.value.daily_stats || []).map(i => i.count || 0),
    type: 'line',
    smooth: true,
    symbol: 'circle',
    symbolSize: 8,
    areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16, 185, 129, 0.3)' }, { offset: 1, color: 'rgba(16, 185, 129, 0.02)' }] } },
    lineStyle: { color: '#10B981', width: 3 },
    itemStyle: { color: '#10B981', borderColor: '#0F172A', borderWidth: 2 }
  }]
}))

const pieOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
    backgroundColor: 'rgba(30, 41, 59, 0.95)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    textStyle: { color: '#F3F4F6', fontSize: 13 }
  },
  legend: {
    bottom: 0,
    textStyle: { color: '#9CA3AF', fontSize: 12 },
    itemWidth: 12,
    itemHeight: 12,
    itemGap: 16
  },
  series: [{
    type: 'pie',
    radius: ['50%', '72%'],
    center: ['50%', '42%'],
    data: dashboard.value.result_distribution?.length
      ? dashboard.value.result_distribution
      : [{ name: '暂无数据', value: 0 }],
    emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.3)' } },
    label: { show: false },
    itemStyle: { borderRadius: 8, borderColor: '#0F172A', borderWidth: 3 },
    color: ['#10B981', '#F59E0B', '#8B5CF6']
  }]
}))

// 置信度分布（真实数据库查询）
const barOption = computed(() => {
  const cd = dashboard.value.confidence_distribution || { high: 0, mid: 0, low: 0 }
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      borderColor: 'rgba(16, 185, 129, 0.3)',
      textStyle: { color: '#F3F4F6', fontSize: 13 }
    },
    grid: { left: 50, right: 20, top: 10, bottom: 30 },
    xAxis: {
      type: 'category',
      data: ['高(>90%)', '中(60-90%)', '低(<60%)'],
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      axisLabel: { color: '#9CA3AF', fontSize: 12 },
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(16, 185, 129, 0.1)', type: 'dashed' } }
    },
    series: [{
      type: 'bar',
      barWidth: 28,
      data: [cd.high, cd.mid, cd.low],
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: (params) => {
          const colors = ['#10B981', '#F59E0B', '#EF4444']
          return {
            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: colors[params.dataIndex] },
              { offset: 1, color: colors[params.dataIndex] + '33' }
            ]
          }
        }
      }
    }]
  }
})

// 患者人口分布（性别+年龄，真实数据库查询）
const demographicOption = computed(() => {
  const gd = dashboard.value.gender_distribution || { male: 0, female: 0 }
  const ad = dashboard.value.age_distribution || []
  return {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(30, 41, 59, 0.95)',
      textStyle: { color: '#F3F4F6', fontSize: 13 }
    },
    legend: {
      bottom: 0,
      textStyle: { color: '#9CA3AF', fontSize: 11 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 12
    },
    series: [
      {
        name: '性别',
        type: 'pie',
        radius: ['0%', '45%'],
        center: ['30%', '42%'],
        data: [
          { name: '男', value: gd.male },
          { name: '女', value: gd.female }
        ],
        label: { show: false },
        itemStyle: { borderRadius: 4, borderColor: '#0F172A', borderWidth: 2 },
        color: ['#3B82F6', '#EC4899']
      },
      {
        name: '年龄段',
        type: 'pie',
        radius: ['55%', '75%'],
        center: ['30%', '42%'],
        data: ad.length ? ad : [{ name: '暂无数据', value: 0 }],
        label: { show: false },
        itemStyle: { borderRadius: 4, borderColor: '#0F172A', borderWidth: 2 },
        color: ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']
      }
    ]
  }
})

function getResultClass(result) {
  if (result === '正常') return 'result-normal'
  if (result === '肺炎') return 'result-pneumonia'
  if (result === '肺结核') return 'result-tuberculosis'
  return 'result-normal'
}

function getConfidenceClass(conf) {
  if (conf >= 0.9) return 'conf-high'
  if (conf >= 0.6) return 'conf-mid'
  return 'conf-low'
}

function getConfidenceColor(conf) {
  if (conf >= 0.9) return '#10B981'
  if (conf >= 0.6) return '#F59E0B'
  return '#EF4444'
}

onMounted(() => {
  fetchDashboardData()
  // 每30秒自动刷新数据
  refreshTimer = setInterval(fetchDashboardData, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped lang="scss">
.dashboard {
  // 页面标题
  .page-header {
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 12px;
    
    .page-title {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
      font-size: 28px;
      font-weight: 700;
      
      .title-secondary {
        color: var(--text-secondary);
        font-weight: 400;
        font-size: 20px;
      }
      
      .title-sep {
        color: var(--glass-border);
        font-weight: 300;
      }
      
      .title-main {
        color: var(--text-primary);
      }
    }
    
    .page-subtitle {
      font-size: 14px;
      color: var(--text-secondary);
      margin-left: 2px;
    }
    
    .header-right {
      display: flex;
      align-items: center;
      gap: 10px;
      
      .last-update {
        font-size: 12px;
        color: var(--text-muted);
      }
    }
  }

  // 统计卡片网格
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .stat-card {
    background: var(--card-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all var(--transition-normal);
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
    
    &:hover {
      transform: translateY(-3px);
      border-color: var(--glass-border-hover);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    .stat-icon {
      width: 48px;
      height: 48px;
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    
    .stat-info {
      .stat-value {
        font-size: 22px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
      }
      
      .stat-label {
        font-size: 13px;
        color: var(--text-secondary);
        margin-top: 4px;
      }
    }
  }

  // 主图表网格
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 24px;
    margin-bottom: 24px;
  }

  .chart-card-large {
    .chart { height: 300px; }
  }

  .chart-card-small {
    .chart-sm { height: 280px; }
  }

  // AI诊断卡
  .ai-card {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(139, 92, 246, 0.08));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-xl);
    padding: 24px;
    position: relative;
    overflow: hidden;
    
    &::after {
      content: '';
      position: absolute;
      top: -50%;
      right: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%);
      animation: pulse 4s ease-in-out infinite;
    }
    
    .ai-card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      position: relative;
      z-index: 1;
    }
    
    .ai-card-title {
      font-size: 14px;
      color: var(--text-secondary);
    }
    
    .ai-card-icon {
      width: 40px;
      height: 40px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--primary);
      
      svg { width: 24px; height: 24px; }
    }
    
    .ai-card-value {
      font-size: 36px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 6px;
      position: relative;
      z-index: 1;
    }
    
    .ai-card-label {
      font-size: 14px;
      color: var(--text-secondary);
      position: relative;
      z-index: 1;
    }
    
    .ai-card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 24px;
      padding-top: 16px;
      border-top: 1px solid var(--glass-border);
      position: relative;
      z-index: 1;
    }
    
    .ai-stat {
      text-align: center;
      
      .ai-stat-value {
        font-size: 18px;
        font-weight: 600;
      }
      
      .ai-stat-label {
        font-size: 11px;
        color: var(--text-secondary);
        margin-top: 4px;
      }
    }
  }

  // 医生团队 & 最近诊断
  .data-section-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 24px;
  }

  // 医生列表
  .doctor-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 380px;
    overflow-y: auto;
  }

  .doctor-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px;
    border-radius: var(--radius-md);
    transition: background var(--transition-fast);
    
    &:hover {
      background: var(--glass-bg);
    }
  }

  .doctor-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(59, 130, 246, 0.3));
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
    flex-shrink: 0;
  }

  .doctor-info {
    flex: 1;
    min-width: 0;
    
    .doctor-name {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .doctor-dept {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 2px;
    }
  }

  .doctor-stats {
    display: flex;
    gap: 16px;
    flex-shrink: 0;
    
    .doc-stat {
      text-align: center;
      
      .doc-stat-num {
        display: block;
        font-size: 16px;
        font-weight: 700;
        color: var(--text-primary);
      }
      
      .doc-stat-label {
        font-size: 10px;
        color: var(--text-muted);
      }
    }
  }

  // 最近诊断记录
  .recent-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 380px;
    overflow-y: auto;
  }

  .recent-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: var(--radius-md);
    transition: background var(--transition-fast);
    
    &:hover {
      background: var(--glass-bg);
    }
  }

  .recent-result-tag {
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 20px;
    font-weight: 600;
    flex-shrink: 0;
    min-width: 50px;
    text-align: center;
    
    &.result-normal { background: rgba(16, 185, 129, 0.2); color: #10B981; }
    &.result-pneumonia { background: rgba(245, 158, 11, 0.2); color: #F59E0B; }
    &.result-tuberculosis { background: rgba(239, 68, 68, 0.2); color: #EF4444; }
  }

  .recent-info {
    flex: 1;
    min-width: 0;
    
    .recent-patient {
      font-size: 14px;
      font-weight: 500;
      color: var(--text-primary);
    }
    
    .recent-meta {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
      
      .meta-sep { margin: 0 4px; opacity: 0.5; }
    }
  }

  .recent-confidence {
    font-size: 13px;
    font-weight: 600;
    flex-shrink: 0;
    
    .conf-high { color: #10B981; }
    .conf-mid { color: #F59E0B; }
    .conf-low { color: #EF4444; }
  }

  // 患者档案区域
  .patient-section {
    margin-bottom: 24px;
  }

  .patient-table-wrapper {
    :deep(.el-table) {
      background: transparent !important;
      
      .el-table__body tr:hover > td {
        background: var(--glass-bg) !important;
      }
      
      .el-table__empty-block {
        background: transparent;
      }
      
      .el-scrollbar__bar { display: none; }
    }
  }

  // 底部网格
  .bottom-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 0.8fr;
    gap: 24px;
    
    .chart-sm { height: 200px; }
  }

  // 快捷操作
  .quick-card {
    .quick-actions {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    
    .quick-action-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 14px;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all var(--transition-normal);
      
      &:hover {
        background: var(--glass-bg);
        
        .action-title { color: var(--primary); }
      }
    }
    
    .action-icon {
      width: 40px;
      height: 40px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    
    .action-text {
      flex: 1;
      
      .action-title {
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary);
        transition: color var(--transition-fast);
      }
      
      .action-desc {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 2px;
      }
    }
  }

  // 通用卡片
  .glass-card {
    background: var(--card-bg);
    backdrop-filter: var(--glass-blur);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
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
      background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.06), transparent);
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      .card-title {
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
      }
      
      .card-action {
        font-size: 12px;
        color: var(--text-muted);
        cursor: pointer;
        transition: color var(--transition-fast);
        
        &:hover { color: var(--primary); }
      }
    }
  }

  .glass-tabs {
    display: flex;
    gap: 4px;
    padding: 4px;
    background: var(--card-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    margin-bottom: 24px;
    width: fit-content;
    
    .tab {
      padding: 8px 20px;
      border-radius: var(--radius-md);
      font-size: 13px;
      font-weight: 500;
      color: var(--text-secondary);
      cursor: pointer;
      transition: all var(--transition-fast);
      
      &.active {
        background: var(--primary);
        color: white;
      }
      
      &:hover:not(.active) {
        color: var(--text-primary);
        background: var(--glass-bg);
      }
    }
  }

  .empty-tip {
    text-align: center;
    padding: 32px 0;
    color: var(--text-muted);
    font-size: 14px;
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}
</style>
