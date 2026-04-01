<template>
  <div class="admin-overview">
    <div class="page-header">
      <h1 class="page-title">
        <span class="title-secondary">Admin</span>
        <span class="title-sep">/</span>
        <span class="title-main">系统概览</span>
      </h1>
      <p class="page-subtitle">全局视角，实时掌控系统运行状态</p>
    </div>

    <!-- 核心指标卡片 -->
    <div class="stats-grid">
      <div class="stat-card" v-for="item in statCards" :key="item.key">
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
    <div class="charts-grid">
      <!-- 用户增长趋势 -->
      <div class="glass-card chart-card">
        <div class="card-header">
          <h3 class="card-title">用户增长趋势（近7天）</h3>
        </div>
        <v-chart class="chart" :option="userTrendOption" autoresize />
      </div>

      <!-- 诊断结果分布 -->
      <div class="glass-card chart-card">
        <div class="card-header">
          <h3 class="card-title">诊断结果分布</h3>
        </div>
        <v-chart class="chart" :option="resultPieOption" autoresize />
      </div>

      <!-- 诊断状态统计 -->
      <div class="glass-card chart-card">
        <div class="card-header">
          <h3 class="card-title">诊断审核状态</h3>
        </div>
        <v-chart class="chart" :option="statusBarOption" autoresize />
      </div>

      <!-- 操作日志分布 -->
      <div class="glass-card chart-card">
        <div class="card-header">
          <h3 class="card-title">操作日志统计</h3>
        </div>
        <v-chart class="chart" :option="actionBarOption" autoresize />
      </div>
    </div>

    <!-- 底部信息 -->
    <div class="bottom-section">
      <!-- 角色分布 -->
      <div class="glass-card">
        <div class="card-header">
          <h3 class="card-title">用户角色分布</h3>
        </div>
        <div class="role-distribution">
          <div class="role-item" v-for="(count, role) in overview.role_distribution" :key="role">
            <div class="role-icon" :class="role">
              {{ roleMap[role]?.charAt(0) || '?' }}
            </div>
            <div class="role-info">
              <div class="role-name">{{ roleMap[role] || role }}</div>
              <div class="role-count">{{ count }} 人</div>
            </div>
            <el-progress :percentage="getRolePercentage(count)" :stroke-width="8"
              :color="roleColorMap[role]" :show-text="false" style="flex: 1;" />
          </div>
        </div>
      </div>

      <!-- 快捷入口 -->
      <div class="glass-card">
        <div class="card-header">
          <h3 class="card-title">管理快捷入口</h3>
        </div>
        <div class="quick-grid">
          <div class="quick-item" @click="$router.push('/admin/users')">
            <div class="quick-icon" style="background: rgba(59, 130, 246, 0.2);">
              <el-icon :size="24" color="#3B82F6"><User /></el-icon>
            </div>
            <span class="quick-label">用户管理</span>
          </div>
          <div class="quick-item" @click="$router.push('/admin/audit-logs')">
            <div class="quick-icon" style="background: rgba(139, 92, 246, 0.2);">
              <el-icon :size="24" color="#8B5CF6"><Document /></el-icon>
            </div>
            <span class="quick-label">审计日志</span>
          </div>
          <div class="quick-item" @click="$router.push('/admin/settings')">
            <div class="quick-icon" style="background: rgba(245, 158, 11, 0.2);">
              <el-icon :size="24" color="#F59E0B"><Setting /></el-icon>
            </div>
            <span class="quick-label">系统设置</span>
          </div>
          <div class="quick-item" @click="$router.push('/dashboard')">
            <div class="quick-icon" style="background: rgba(16, 185, 129, 0.2);">
              <el-icon :size="24" color="#10B981"><Monitor /></el-icon>
            </div>
            <span class="quick-label">业务端</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { systemApi } from '@/api'
import { DataAnalysis, Calendar, UserFilled, Avatar, CircleCheck, Warning, TrendCharts, Unlock } from '@element-plus/icons-vue'

use([CanvasRenderer, LineChart, PieChart, BarChart,
  TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const overview = ref({ overview: {}, role_distribution: {}, result_distribution: {}, daily_stats: [] })
const statistics = ref({ user_trend: [], diagnosis_status: {}, action_distribution: {} })

const roleMap = { admin: '管理员', doctor: '医生', nurse: '护士' }
const roleColorMap = { admin: '#EF4444', doctor: '#10B981', nurse: '#3B82F6' }

const statCards = computed(() => [
  { key: 'diagnoses', label: '总诊断数', value: overview.value.overview.total_diagnoses || 0, icon: DataAnalysis, color: '#3B82F6', bgColor: 'rgba(59, 130, 246, 0.2)' },
  { key: 'today', label: '今日诊断', value: overview.value.overview.today_diagnoses || 0, icon: Calendar, color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.2)' },
  { key: 'patients', label: '患者总数', value: overview.value.overview.total_patients || 0, icon: UserFilled, color: '#8B5CF6', bgColor: 'rgba(139, 92, 246, 0.2)' },
  { key: 'users', label: '总用户数', value: overview.value.overview.total_users || 0, icon: Avatar, color: '#F59E0B', bgColor: 'rgba(245, 158, 11, 0.2)' },
  { key: 'active', label: '活跃用户', value: overview.value.overview.active_users || 0, icon: CircleCheck, color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.15)' },
  { key: 'pending', label: '待审核', value: overview.value.overview.pending_reviews || 0, icon: Warning, color: '#EF4444', bgColor: 'rgba(239, 68, 68, 0.2)' },
  { key: 'week', label: '本周诊断', value: overview.value.overview.week_diagnoses || 0, icon: TrendCharts, color: '#8B5CF6', bgColor: 'rgba(139, 92, 246, 0.15)' },
  { key: 'logins', label: '今日登录', value: overview.value.overview.today_logins || 0, icon: Unlock, color: '#3B82F6', bgColor: 'rgba(59, 130, 246, 0.15)' }
])

function getRolePercentage(count) {
  const total = Object.values(overview.value.role_distribution).reduce((a, b) => a + b, 0)
  return total ? Math.round((count / total) * 100) : 0
}

const resultCn = { normal: '正常', pneumonia: '肺炎', tuberculosis: '肺结核' }
const statusCn = { pending: '待审核', confirmed: '已确认', revised: '已修正' }
const actionCn = {
  login: '登录',
  logout: '登出',
  diagnosis: '诊断',
  patient_create: '新建患者',
  patient_update: '更新患者',
  user_create: '创建用户',
  user_update: '更新用户',
  user_delete: '删除用户',
  user_reset_password: '重置密码',
  model_params: '模型参数',
  update_model_params: '更新模型参数',
  user_update_model_params: '更新模型参数',
  model_load: '模型加载',
  report_generate: '报告生成',
  settings_update: '设置更新',
  view: '查看',
  create: '创建',
  update: '更新',
  delete: '删除'
}

const userTrendOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(30,41,59,0.95)', borderColor: 'rgba(16,185,129,0.3)', textStyle: { color: '#F3F4F6' } },
  grid: { left: 50, right: 20, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: statistics.value.user_trend.map(i => i.date), axisLabel: { color: '#9CA3AF' }, axisLine: { show: false }, axisTick: { show: false } },
  yAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#9CA3AF' }, axisLine: { show: false }, axisTick: { show: false }, splitLine: { lineStyle: { color: 'rgba(16,185,129,0.1)', type: 'dashed' } } },
  series: [{ data: statistics.value.user_trend.map(i => i.count), type: 'line', smooth: true, areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(59,130,246,0.3)' }, { offset: 1, color: 'rgba(59,130,246,0.02)' }] } }, lineStyle: { color: '#3B82F6', width: 3 }, itemStyle: { color: '#3B82F6', borderColor: '#0F172A', borderWidth: 2 } }]
}))

const resultPieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: 'rgba(30,41,59,0.95)', textStyle: { color: '#F3F4F6' } },
  legend: { bottom: 0, textStyle: { color: '#9CA3AF' }, itemWidth: 12, itemHeight: 12 },
  series: [{ type: 'pie', radius: ['45%', '70%'], center: ['50%', '42%'], data: Object.entries(overview.value.result_distribution).map(([k, v]) => ({ name: resultCn[k] || k, value: v })), label: { show: false }, itemStyle: { borderRadius: 8, borderColor: '#0F172A', borderWidth: 3 }, color: ['#10B981', '#F59E0B', '#8B5CF6'] }]
}))

const statusBarOption = computed(() => ({
  tooltip: { trigger: 'axis', backgroundColor: 'rgba(30,41,59,0.95)', textStyle: { color: '#F3F4F6' } },
  grid: { left: 80, right: 20, top: 10, bottom: 30 },
  xAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#9CA3AF' }, axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(16,185,129,0.1)', type: 'dashed' } } },
  yAxis: { type: 'category', data: Object.keys(statistics.value.diagnosis_status).map(k => statusCn[k] || k), axisLabel: { color: '#9CA3AF' }, axisLine: { show: false } },
  series: [{ type: 'bar', barWidth: 20, data: Object.values(statistics.value.diagnosis_status), itemStyle: { borderRadius: [0, 6, 6, 0], color: (p) => ['#F59E0B', '#10B981', '#3B82F6'][p.dataIndex] || '#10B981' } }]
}))

const actionBarOption = computed(() => {
  const entries = Object.entries(statistics.value.action_distribution).sort((a, b) => b[1] - a[1]).slice(0, 8)
  return {
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(30,41,59,0.95)', textStyle: { color: '#F3F4F6' } },
    grid: { left: 110, right: 20, top: 10, bottom: 30 },
    xAxis: { type: 'value', minInterval: 1, axisLabel: { color: '#9CA3AF' }, axisLine: { show: false }, splitLine: { lineStyle: { color: 'rgba(16,185,129,0.1)', type: 'dashed' } } },
    yAxis: { type: 'category', data: entries.map(([k]) => actionCn[k] || k).reverse(), axisLabel: { color: '#9CA3AF', width: 100, overflow: 'truncate' }, axisLine: { show: false } },
    series: [{ type: 'bar', barWidth: 20, data: entries.map(([, v]) => v).reverse(), itemStyle: { borderRadius: [0, 6, 6, 0], color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0, colorStops: [{ offset: 0, color: '#8B5CF6' }, { offset: 1, color: '#8B5CF644' }] } } }]
  }
})

onMounted(async () => {
  try {
    const [overviewRes, statsRes] = await Promise.all([
      systemApi.getAdminOverview(),
      systemApi.getAdminStatistics()
    ])
    overview.value = overviewRes.data
    statistics.value = statsRes.data
  } catch (e) {}
})
</script>

<style scoped lang="scss">
.admin-overview {
  .page-header {
    margin-bottom: 24px;
    .page-title { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; font-size: 28px; font-weight: 700; .title-secondary { color: var(--text-secondary); font-weight: 400; font-size: 20px; } .title-sep { color: var(--glass-border); font-weight: 300; } .title-main { color: var(--text-primary); } }
    .page-subtitle { font-size: 14px; color: var(--text-secondary); }
  }

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
    &:hover { transform: translateY(-3px); border-color: var(--glass-border-hover); box-shadow: 0 12px 40px rgba(0,0,0,0.2); }
    .stat-icon { width: 48px; height: 48px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .stat-value { font-size: 22px; font-weight: 700; color: var(--text-primary); line-height: 1.2; }
    .stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
  }

  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 24px;
    .chart { height: 280px; }
  }

  .bottom-section {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  .role-distribution {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .role-item {
    display: flex;
    align-items: center;
    gap: 12px;
    .role-icon { width: 36px; height: 36px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; color: white; flex-shrink: 0; &.admin { background: rgba(239,68,68,0.2); color: #EF4444; } &.doctor { background: rgba(16,185,129,0.2); color: #10B981; } &.nurse { background: rgba(59,130,246,0.2); color: #3B82F6; } }
    .role-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }
    .role-count { font-size: 12px; color: var(--text-secondary); }
    .role-info { width: 80px; flex-shrink: 0; }
  }

  .quick-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .quick-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 24px 16px;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all var(--transition-normal);
    &:hover { background: var(--glass-bg); transform: translateY(-2px); }
    .quick-icon { width: 52px; height: 52px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; }
    .quick-label { font-size: 14px; font-weight: 500; color: var(--text-primary); }
  }
}
</style>
