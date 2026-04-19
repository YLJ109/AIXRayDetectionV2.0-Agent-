/** 管理员-系统设置页面 */
<template>
  <div class="settings-page">
    <!-- AI诊断设置 -->
    <div class="glass-card">
      <div class="section-header">
        <span class="section-icon"><el-icon><Cpu /></el-icon></span>
        <span class="section-title">AI诊断设置</span>
        <span class="section-desc">实时生效，无需重启服务</span>
      </div>
      <div class="settings-grid">
        <div class="setting-item">
          <div class="setting-label">
            疾病概率告警阈值
            <span class="setting-hint">超过此阈值的疾病概率将标记为异常</span>
          </div>
          <div class="setting-control">
            <el-slider v-model="settings.disease_threshold" :min="0.1" :max="0.95" :step="0.05"
              style="flex: 1; max-width: 300px" @change="onSettingChange('disease_threshold')" />
            <el-input-number v-model="settings.disease_threshold" :min="0.1" :max="0.95"
              :step="0.05" :precision="2" size="small" style="width: 100px; margin-left: 12px"
              @change="onSettingChange('disease_threshold')" />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">
            热力图透明度
            <span class="setting-hint">Grad-CAM热力图叠加到原始图像的透明度</span>
          </div>
          <div class="setting-control">
            <el-slider v-model="settings.heatmap_alpha" :min="0.1" :max="0.9" :step="0.05"
              style="flex: 1; max-width: 300px" @change="onSettingChange('heatmap_alpha')" />
            <el-input-number v-model="settings.heatmap_alpha" :min="0.1" :max="0.9"
              :step="0.05" :precision="2" size="small" style="width: 100px; margin-left: 12px"
              @change="onSettingChange('heatmap_alpha')" />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">
            批量处理并发数
            <span class="setting-hint">批量诊断时的最大并发任务数</span>
          </div>
          <div class="setting-control">
            <el-input-number v-model="settings.batch_concurrency" :min="1" :max="10" />
          </div>
        </div>
      </div>
    </div>

    <!-- 通用设置 -->
    <div class="glass-card">
      <div class="section-header">
        <span class="section-icon"><el-icon><Setting /></el-icon></span>
        <span class="section-title">通用设置</span>
      </div>
      <div class="settings-grid">
        <div class="setting-item">
          <div class="setting-label">
            系统名称
            <span class="setting-hint">显示在页面标题和报告中的系统名称</span>
          </div>
          <div class="setting-control">
            <el-input v-model="settings.system_name" style="max-width: 300px" />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">
            会话超时时间（小时）
            <span class="setting-hint">用户登录会话的有效时长</span>
          </div>
          <div class="setting-control">
            <el-input-number v-model="settings.session_timeout" :min="1" :max="72" />
          </div>
        </div>
      </div>
    </div>

    <!-- 存储设置 -->
    <div class="glass-card">
      <div class="section-header">
        <span class="section-icon"><el-icon><FolderOpened /></el-icon></span>
        <span class="section-title">存储设置</span>
      </div>
      <div class="settings-grid">
        <div class="setting-item">
          <div class="setting-label">
            最大上传文件大小（MB）
            <span class="setting-hint">单次上传文件的大小限制</span>
          </div>
          <div class="setting-control">
            <el-input-number v-model="settings.max_upload_size" :min="5" :max="100" />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">
            审计日志保留天数
            <span class="setting-hint">超过保留期的日志将自动清理</span>
          </div>
          <div class="setting-control">
            <el-input-number v-model="settings.audit_retention_days" :min="30" :max="365" />
          </div>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="save-bar">
      <el-button type="primary" :loading="saving" @click="handleSave">
        <el-icon><Check /></el-icon> 保存设置
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Cpu, Setting, FolderOpened, Check } from '@element-plus/icons-vue'
import { getSettingsApi, batchUpdateSettingsApi } from '@/api/settings'
import { updateModelParamsApi, getActiveModelInfoApi } from '@/api/model-weights'

const saving = ref(false)
const settings = reactive({
  system_name: '胸影智诊V3.0',
  session_timeout: 12,
  disease_threshold: 0.7,
  heatmap_alpha: 0.4,
  batch_concurrency: 2,
  max_upload_size: 20,
  audit_retention_days: 180,
})

async function loadSettings() {
  try {
    const res: any = await getSettingsApi()
    Object.assign(settings, res.data)
  } catch { /* handled */ }
  // Also load runtime AI params
  try {
    const res: any = await getActiveModelInfoApi()
    if (res.data?.runtime) {
      settings.disease_threshold = res.data.runtime.disease_threshold ?? 0.7
      settings.heatmap_alpha = res.data.runtime.heatmap_alpha ?? 0.4
    }
  } catch { /* handled */ }
}

let paramTimer: ReturnType<typeof setTimeout> | null = null
function onSettingChange(key: string) {
  if (key === 'disease_threshold' || key === 'heatmap_alpha') {
    if (paramTimer) clearTimeout(paramTimer)
    paramTimer = setTimeout(async () => {
      try {
        const res: any = await updateModelParamsApi({
          disease_threshold: settings.disease_threshold,
          heatmap_alpha: settings.heatmap_alpha,
        })
        if (res.data) {
          settings.disease_threshold = res.data.disease_threshold
          settings.heatmap_alpha = res.data.heatmap_alpha
        }
        ElMessage.success('AI参数已同步')
      } catch { /* handled */ }
    }, 500)
  }
}

async function handleSave() {
  saving.value = true
  try {
    await batchUpdateSettingsApi({ ...settings })
    ElMessage.success('设置已保存')
  } catch { /* handled */ } finally { saving.value = false }
}

onMounted(() => loadSettings())
</script>

<style scoped lang="scss">
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 16px;

  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;

    .section-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: rgba(34, 211, 238, 0.12);
      color: var(--primary);
      font-size: 16px;
    }

    .section-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--text-primary);
    }

    .section-desc {
      font-size: 12px;
      color: var(--text-muted);
      margin-left: auto;
    }
  }

  .settings-grid {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  .setting-item {
    .setting-label {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 8px;

      .setting-hint {
        display: block;
        font-size: 12px;
        font-weight: 400;
        color: var(--text-muted);
        margin-top: 2px;
      }
    }

    .setting-control {
      display: flex;
      align-items: center;
    }
  }

  .save-bar {
    display: flex;
    justify-content: flex-end;
    padding: 8px 0;
  }
}
</style>
