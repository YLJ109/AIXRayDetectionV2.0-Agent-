<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

function applyTheme(theme: 'light' | 'dark') {
  const html = document.documentElement
  html.classList.remove('light', 'dark')
  html.classList.add(theme)
}

onMounted(() => {
  const stored = localStorage.getItem('theme') as 'light' | 'dark' | null
  if (stored) {
    applyTheme(stored)
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    applyTheme('dark')
  } else {
    applyTheme('light')
  }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      applyTheme(e.matches ? 'dark' : 'light')
    }
  })
})
</script>
