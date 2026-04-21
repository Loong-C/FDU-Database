<script setup lang="ts">
import { computed, ref } from 'vue'
import { useChart, type EChartsCoreOption } from './useChart'

const props = withDefaults(defineProps<{
  title?: string
  data: Array<{ name: string; value: number }>
  height?: number
  loading?: boolean
}>(), { height: 300 })

const container = ref<HTMLElement | null>(null)

const option = computed<EChartsCoreOption | null>(() => {
  if (!props.data.length) return null
  return {
    title: props.title ? { text: props.title, left: 8, top: 4, textStyle: { fontSize: 14 } } : undefined,
    tooltip: {
      trigger: 'item',
      valueFormatter: (v: unknown) =>
        typeof v === 'number' ? v.toLocaleString('zh-CN', { style: 'currency', currency: 'CNY' }) : String(v),
    },
    legend: { bottom: 0, itemGap: 12, type: 'scroll' },
    series: [
      {
        type: 'pie',
        radius: ['50%', '76%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: 'var(--app-surface)', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: props.data,
      },
    ],
    color: ['#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6', '#ec4899'],
  }
})

useChart(container, option)
</script>

<template>
  <div class="pie-category" v-loading="loading">
    <div ref="container" :style="{ height: height + 'px' }" />
  </div>
</template>
