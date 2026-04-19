/** 管理员-系统概览页面 */
<template>
  <div class="overview-page">
    <!-- 系统资源 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-cyan">
          <el-icon :size="22">
            <Cpu />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ system.cpu_percent ?? '-' }}<span class="stat-unit">%</span></div>
          <div class="stat-label">CPU 使用率</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-blue">
          <el-icon :size="22">
            <Monitor />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ system.memory_percent ?? '-' }}<span class="stat-unit">%</span></div>
          <div class="stat-label">内存 {{ system.memory_used_gb ?? '-' }}/{{ system.memory_total_gb ?? '-' }} GB</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-orange">
          <el-icon :size="22">
            <Coin />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ system.disk_percent ?? '-' }}<span class="stat-unit">%</span></div>
          <div class="stat-label">磁盘 {{ system.disk_used_gb ?? '-' }}/{{ system.disk_total_gb ?? '-' }} GB</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-green">
          <el-icon :size="22">
            <User />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ users.active }}<span class="stat-divider">/</span>{{ users.total }}</div>
          <div class="stat-label">活跃用户 / 总数</div>
        </div>
      </div>
    </div>

    <!-- 业务统计 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-purple">
          <el-icon :size="22">
            <Document />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ diagnoses.total }}</div>
          <div class="stat-label">累计诊断</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-primary">
          <el-icon :size="22">
            <Calendar />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ diagnoses.today }}</div>
          <div class="stat-label">今日诊断</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-red">
          <el-icon :size="22">
            <Warning />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ model.loaded ? '已加载' : '未加载' }}</div>
          <div class="stat-label">AI 模型状态</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-teal">
          <el-icon :size="22">
            <DataLine />
          </el-icon>
        </div>
        <div class="stat-body">
          <div class="stat-value">{{ approvals.pending ?? '-' }}</div>
          <div class="stat-label">待审核报告</div>
        </div>
      </div>
    </div>

    <!-- 模型信息 -->
    <div class="glass-card" v-if="modelInfo.version_name || modelInfo.architecture">
      <h3 class="card-title">当前激活模型</h3>
      <el-descriptions :column="3" border size="default">
        <el-descriptions-item label="版本号">{{ modelInfo.version_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="架构">{{ modelInfo.architecture || '-' }}</el-descriptions-item>
        <el-descriptions-item label="训练数据集">{{ modelInfo.training_dataset || '-' }}</el-descriptions-item>
        <el-descriptions-item label="文件大小">{{ formatSize(modelInfo.file_size) }}</el-descriptions-item>
        <el-descriptions-item label="AUC">
          <span v-if="modelInfo.metrics?.auc">{{ Number(modelInfo.metrics.auc).toFixed(4) }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="激活时间">{{ modelInfo.activated_at || '-' }}</el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { Cpu, Monitor, Coin, User, Document, Calendar, Warning, DataLine } from '@element-plus/icons-vue'
import { getSystemOverviewApi } from '@/api/dashboard'
import { getActiveModelInfoApi } from '@/api/model-weights'

const system = reactive({
  cpu_percent: null as number | null, memory_percent: null as number | null,
  memory_total_gb: null as number | null, memory_used_gb: null as number | null,
  disk_percent: null as number | null, disk_total_gb: null as number | null, disk_used_gb: null as number | null,
})
const users = reactive({ total: 0, active: 0 })
const diagnoses = reactive({ total: 0, today: 0 })
const model = reactive({ loaded: false })
const approvals = reactive({ pending: null as number | null })
const modelInfo = reactive({
  version_name: '', architecture: '', training_dataset: '',
  file_size: null as number | null, metrics: null as any, activated_at: '',
})

function formatSize(bytes: number | null | undefined) {
  if (!bytes) return '-'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(async () => {
  try {
    const res: any = await getSystemOverviewApi()
    const d = res.data
    if (d.system) Object.assign(system, d.system)
    if (d.users) Object.assign(users, d.users)
    if (d.diagnoses) Object.assign(diagnoses, d.diagnoses)
    if (d.model) Object.assign(model, d.model)
  } catch { /* ok */ }

  try {
    const mRes: any = await getActiveModelInfoApi()
    const m = mRes.data || mRes
    if (m) {
      Object.assign(modelInfo, m)
      // fetch pending count from approval
      if (m.pending_count !== undefined) approvals.pending = m.pending_count
    }
  } catch { /* ok */ }
})
</script>

<style scoped>
.overview-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

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

.stat-icon-cyan {
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

.stat-icon-green {
  background: rgba(34, 197, 94, 0.12);
  color: #22C55E;
}

.stat-icon-purple {
  background: rgba(139, 92, 246, 0.12);
  color: #A78BFA;
}

.stat-icon-primary {
  background: rgba(34, 211, 238, 0.12);
  color: var(--primary);
}

.stat-icon-red {
  background: rgba(239, 68, 68, 0.12);
  color: #F87171;
}

.stat-icon-teal {
  background: rgba(20, 184, 166, 0.12);
  color: #14B8A6;
}

.stat-body {
  min-width: 0;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.stat-unit {
  font-size: 14px;
  font-weight: 500;
  margin-left: 2px;
}

.stat-divider {
  font-size: 14px;
  font-weight: 400;
  color: var(--text-muted);
  margin: 0 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-title {
  margin-bottom: 14px;
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
