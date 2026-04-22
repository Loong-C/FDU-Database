<script setup lang="ts">
import { computed, ref } from 'vue'
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
const option = computed<EChartsCoreOption | null>(() => {
  if (!props.categories.length) return null
  return {
    title: props.title ? { text: props.title, left: 8, top: 4, textStyle: { fontSize: 14 } } : undefined,
    grid: { left: 48, right: 24, top: props.title ? 40 : 16, bottom: 36 },
    tooltip: { trigger: 'axis', valueFormatter: (v: unknown) => (typeof v === 'number' ? v.toLocaleString('zh-CN') : String(v)) },
    legend: { bottom: 0, itemGap: 16 },
    xAxis: {
      type: 'category',
      data: props.categories,
      axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.4)' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      name: props.yAxisName,
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.18)' } },
    },
    series: props.series.map((s, index) => ({
      name: s.name,
      data: s.data,
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2.5 },
      areaStyle: index === 0 ? { opacity: 0.12 } : undefined,
      emphasis: { focus: 'series' },
    })),
    color: ['#0969da', '#1a7f37', '#8250df', '#bf8700', '#cf222e', '#176f64'],
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
