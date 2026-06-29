<script setup lang="ts">
import { computed, ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useChart, type EChartsCoreOption } from './useChart'

const props = withDefaults(defineProps<{
  title?: string
  categories: string[]
  series: Array<{ name: string; data: Array<number | string> }>
  height?: number
  yAxisName?: string
  loading?: boolean
}>(), { height: 300 })

const container = ref<HTMLElement | null>(null)
const ui = useUiStore()

const option = computed<EChartsCoreOption | null>(() => {
  if (!props.categories.length) return null
  const axisColor = ui.isDark ? '#b7b7b0' : '#5f5f5f'
  const gridColor = ui.isDark ? 'rgba(244, 244, 242, 0.14)' : 'rgba(17, 17, 17, 0.12)'
  return {
    title: props.title ? { text: props.title, left: 8, top: 4, textStyle: { fontSize: 14 } } : undefined,
    grid: { left: 48, right: 24, top: props.title ? 40 : 16, bottom: 64 },
    tooltip: { trigger: 'axis', valueFormatter: (v: unknown) => (typeof v === 'number' ? v.toLocaleString('zh-CN') : String(v)) },
    legend: { bottom: 4, itemGap: 18, textStyle: { color: axisColor } },
    xAxis: {
      type: 'category',
      data: props.categories,
      axisLine: { lineStyle: { color: gridColor } },
      axisLabel: { color: axisColor },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      name: props.yAxisName,
      axisLine: { show: false },
      axisLabel: { color: axisColor },
      nameTextStyle: { color: axisColor },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: gridColor } },
    },
    series: props.series.map((s, index) => ({
      name: s.name,
      data: s.data,
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2.5 },
      areaStyle: index === 0 ? { color: 'rgba(225, 6, 0, 0.1)' } : undefined,
      emphasis: { focus: 'series' },
    })),
    color: ui.isDark
      ? ['#ff2a1f', '#f4f4f2', '#a0a0a0', '#ff8a80']
      : ['#e10600', '#111111', '#6f6f6f', '#b00000'],
  }
})

useChart(container, option)
</script>

<template>
  <div class="line-trend" v-loading="loading">
    <div ref="container" :style="{ height: height + 'px' }" />
  </div>
</template>

<style scoped>
.line-trend {
  width: 100%;
}
</style>
