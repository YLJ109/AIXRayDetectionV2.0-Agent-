/** 数据看板页面 */
<template>
  <div class="dashboard-page">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card" @click="$router.push('/diagnose')">
        <div class="stat-icon stat-icon-primary"><el-icon :size="22">
            <Document />
          </el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.today_count }}</div>
          <div class="stat-label">今日诊断</div>
        </div>
      </div>
      <div class="stat-card" @click="$router.push('/history')">
        <div class="stat-icon stat-icon-blue"><el-icon :size="22">
            <Calendar />
          </el-icon></div>
        <div class="stat-body">
          <div class="stat-value">{{ stats.month_count }}</div>
          <div class="stat-label">本月累计</div>
        </div>
      </div>
      <div class="stat-card" @click="$router.push('/approval')">
        <div class="stat-icon stat-icon-orange"><el-icon :size="22">
            <Bell />
          </el-icon></div>
        <div class="stat-body">
          <div class="stat-value stat-warn">{{ stats.pending_count }}</div>
          <div class="stat-label">待审核报告</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-red"><el-icon :size="22">
            <Warning />
          </el-icon></div>
        <div class="stat-body">
          <div class="stat-value stat-danger">{{ stats.high_risk_count }}</div>
          <div class="stat-label">高危病例</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="glass-card chart-card">
        <div class="card-header">
          <span class="card-title">疾病分布（近30天）</span>
        </div>
        <v-chart v-if="diseaseData.length" :option="diseaseOption" style="height: 300px;" autoresize />
        <div v-else class="empty-chart">暂无数据</div>
      </div>
      <div class="glass-card chart-card">
        <div class="card-header">
          <span class="card-title">诊断趋势（近30天）</span>
        </div>
        <v-chart v-if="trendData.length" :option="trendOption" style="height: 300px;" autoresize />
        <div v-else class="empty-chart">暂无数据</div>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="glass-card">
      <div class="card-header">
        <span class="card-title">快捷入口</span>
      </div>
      <div class="quick-links">
        <div class="quick-item" @click="$router.push('/diagnose')">
          <div class="quick-icon quick-icon-cyan"><el-icon :size="24">
              <Cpu />
            </el-icon></div>
          <div class="quick-label">AI 辅助诊断</div>
          <div class="quick-desc">上传影像 · 智能分析</div>
        </div>
        <div class="quick-item" @click="$router.push('/approval')">
          <div class="quick-icon quick-icon-orange"><el-icon :size="24">
              <Bell />
            </el-icon></div>
          <div class="quick-label">诊断审核</div>
          <div class="quick-desc">{{ stats.pending_count }} 份待处理</div>
        </div>
        <div class="quick-item" @click="$router.push('/chat')">
          <div class="quick-icon quick-icon-purple"><el-icon :size="24">
              <ChatDotRound />
            </el-icon></div>
          <div class="quick-label">AI 医学咨询</div>
          <div class="quick-desc">智能问答助手</div>
        </div>
        <div class="quick-item" @click="$router.push('/triage')">
          <div class="quick-icon quick-icon-blue"><el-icon :size="24">
              <FirstAidKit />
            </el-icon></div>
          <div class="quick-label">智能分诊</div>
          <div class="quick-desc">症状分析推荐</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { Document, Calendar, Bell, Warning, Cpu, ChatDotRound, FirstAidKit } from '@element-plus/icons-vue'
import { getDashboardStatsApi, getDiseaseDistributionApi, getDiagnosisTrendApi } from '@/api/dashboard'

use([CanvasRenderer, PieChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

// 主题色常量（避免运行时读取 CSS 变量的性能开销）
const PRIMARY = '#22D3EE'
const PRIMARY_RGB = '34, 211, 238'

function cssVar(name: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim()
}

const stats = ref({ today_count: 0, month_count: 0, pending_count: 0, high_risk_count: 0 })
const diseaseData = ref<any[]>([])
const trendData = ref<any[]>([])

const diseaseOption = computed(() => {
  const bg = cssVar('--bg-secondary')
  const tp = cssVar('--text-primary')
  const ts = cssVar('--text-secondary')
  const bp = cssVar('--bg-primary')
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: bg,
      borderColor: `rgba(${PRIMARY_RGB}, 0.3)`,
      textStyle: { color: tp },
    },
    legend: {
      orient: 'vertical', left: 'left',
      textStyle: { color: ts, fontSize: 12 },
      itemWidth: 10, itemHeight: 10, itemGap: 10,
    },
    series: [{
      type: 'pie',
      radius: ['38%', '62%'],
      center: ['58%', '50%'],
      data: diseaseData.value.map(d => ({ name: d.disease_name_zh, value: d.count })),
      itemStyle: { borderRadius: 6, borderColor: bp, borderWidth: 2 },
      label: { color: ts, fontSize: 11 },
      emphasis: {
        itemStyle: { shadowBlur: 16, shadowColor: `rgba(${PRIMARY_RGB}, 0.4)` }
      },
    }],
  }
})

const trendOption = computed(() => {
  const bg = cssVar('--bg-secondary')
  const tp = cssVar('--text-primary')
  const tm = cssVar('--text-muted')
  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: bg,
      borderColor: `rgba(${PRIMARY_RGB}, 0.3)`,
      textStyle: { color: tp },
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trendData.value.map(d => d.date),
      axisLabel: { color: tm, fontSize: 11 },
      axisLine: { lineStyle: { color: `rgba(${PRIMARY_RGB}, 0.15)` } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: tm },
      splitLine: { lineStyle: { color: `rgba(${PRIMARY_RGB}, 0.06)` } },
    },
    series: [{
      data: trendData.value.map(d => d.count),
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: PRIMARY, width: 2.5 },
      itemStyle: { color: PRIMARY },
      areaStyle: {
        color: {
          type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: `rgba(${PRIMARY_RGB}, 0.25)` },
            { offset: 1, color: `rgba(${PRIMARY_RGB}, 0)` },
          ],
        },
      },
    }],
  }
})

onMounted(async () => {
  try {
    const [statsRes, distRes, trendRes]: any[] = await Promise.all([
      getDashboardStatsApi(),
      getDiseaseDistributionApi(),
      getDiagnosisTrendApi(),
    ])
    stats.value = statsRes.data || statsRes
    diseaseData.value = distRes.data || distRes
    trendData.value = trendRes.data || trendRes
  } catch { /* ok */ }
})
</script>

<style scoped>
.dashboard-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ===== 统计卡片 ===== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: border-color 0.2s;
}

.stat-card:hover {
  border-color: var(--glass-border-hover);
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

.stat-icon-primary {
  background: rgba(34, 211, 238, 0.12);
  color: #22D3EE;
}

.stat-icon-blue {
  background: rgba(59, 130, 246, 0.12);
  color: #60A5FA;
}

.stat-icon-orange {
  background: rgba(245, 158, 11, 0.12);
  color: #FBBF24;
}

.stat-icon-red {
  background: rgba(239, 68, 68, 0.12);
  color: #F87171;
}

.stat-body {
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-warn {
  color: #FBBF24;
}

.stat-danger {
  color: #F87171;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* ===== 图表区域 ===== */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.chart-card {
  min-height: 360px;
}

.empty-chart {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

/* ===== 快捷入口 ===== */
.quick-links {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px 16px;
  border-radius: var(--radius-lg);
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: transform 0.2s, border-color 0.2s;
}

.quick-item:hover {
  transform: translateY(-3px);
  border-color: var(--glass-border-hover);
}

.quick-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.quick-icon-cyan {
  background: rgba(34, 211, 238, 0.12);
  color: #22D3EE;
}

.quick-icon-orange {
  background: rgba(245, 158, 11, 0.12);
  color: #FBBF24;
}

.quick-icon-purple {
  background: rgba(139, 92, 246, 0.12);
  color: #A78BFA;
}

.quick-icon-blue {
  background: rgba(59, 130, 246, 0.12);
  color: #60A5FA;
}

.quick-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.quick-desc {
  font-size: 12px;
  color: var(--text-muted);
}

/* ===== 响应式 ===== */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .quick-links {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
