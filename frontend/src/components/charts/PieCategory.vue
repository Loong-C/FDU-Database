<script setup lang="ts">
import { computed, ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useChart, type EChartsCoreOption } from './useChart'

const props = withDefaults(defineProps<{
  title?: string
  data: Array<{ name: string; value: number }>
  height?: number
  loading?: boolean
}>(), { height: 300 })

const container = ref<HTMLElement | null>(null)
const ui = useUiStore()

// 圆环扇区分隔与图例色块描边使用同一种"衬色"，让两者视觉统一。
// 浅色模式用 GitHub 风的浅灰边框；深色模式用白色细边，与图例 marker 的亮边一致。
const separatorColor = computed(() => (ui.isDark ? '#ffffff' : '#d0d7de'))
const legendTextColor = computed(() => (ui.isDark ? '#e6edf3' : '#1f2328'))

const option = computed<EChartsCoreOption | null>(() => {
  if (!props.data.length) return null
  return {
    title: props.title ? { text: props.title, left: 8, top: 4, textStyle: { fontSize: 14 } } : undefined,
    tooltip: {
      trigger: 'item',
      valueFormatter: (v: unknown) =>
        typeof v === 'number' ? v.toLocaleString('zh-CN', { style: 'currency', currency: 'CNY' }) : String(v),
    },
    legend: {
      bottom: 0,
      itemGap: 12,
      type: 'scroll',
      icon: 'roundRect',
      textStyle: { color: legendTextColor.value, fontSize: 12 },
      itemStyle: {
        borderColor: separatorColor.value,
        borderWidth: 1,
      },
    },
    series: [
      {
        type: 'pie',
        radius: ['50%', '76%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: separatorColor.value,
          borderWidth: 2,
        },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: props.data,
      },
    ],
    color: ['#0969da', '#1a7f37', '#8250df', '#bf8700', '#cf222e', '#176f64', '#6639ba', '#953800'],
  }
})

useChart(container, option)
</script>

<template>
  <div class="pie-category" v-loading="loading">
    <div ref="container" :style="{ height: height + 'px' }" />
  </div>
</template>
