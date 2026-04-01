import { defineStore } from 'pinia'

/**
 * 诊断中心状态 Store
 * 页面刷新后自动重置为空白状态
 */
export const useDiagnosisStore = defineStore('diagnosis', {
  state: () => ({
    // 表单数据
    form: { patient_id: '', symptoms: '', clinical_info: '' },
    // 诊断结果
    result: null,
    // 报告内容
    reportContent: '',
    // 图片预览 URL
    imagePreviewUrl: '',
    // 上次更新时间
    lastUpdated: null
  }),

  getters: {
    hasResult: (state) => !!state.result,
    hasFormData: (state) => !!state.form.patient_id
  },

  actions: {
    // 更新表单数据
    updateForm(formData) {
      this.form = { ...this.form, ...formData }
      this.lastUpdated = Date.now()
    },

    // 保存诊断结果
    setResult(result) {
      this.result = result
      this.lastUpdated = Date.now()
    },

    // 保存图片预览 URL
    setImagePreviewUrl(url) {
      this.imagePreviewUrl = url
    },

    // 保存报告内容
    setReportContent(content) {
      this.reportContent = content
      this.lastUpdated = Date.now()
    },

    // 清空所有数据
    clearAll() {
      this.form = { patient_id: '', symptoms: '', clinical_info: '' }
      this.result = null
      this.reportContent = ''
      this.imagePreviewUrl = ''
      this.lastUpdated = null
    },

    // 仅清空图片和结果（保留表单）
    clearImageAndResult() {
      this.result = null
      this.reportContent = ''
      this.imagePreviewUrl = ''
    }
  }
})
