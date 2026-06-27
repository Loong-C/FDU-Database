<script setup lang="ts">
import { computed, ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useChart, type EChartsCoreOption } from './useChart'

const props = withDefaults(defineProps<{
  title?: string
  categories: string[]
  values: Array<number | string>
  height?: number
  color?: string
  loading?: boolean
  valueFormatter?: (v: number) => string
}>(), { height: 320 })

const container = ref<HTMLElement | null>(null)
const ui = useUiStore()

const option = computed<EChartsCoreOption | null>(() => {
  if (!props.categories.length) return null
  const axisColor = ui.isDark ? '#b7b7b0' : '#5f5f5f'
  const gridColor = ui.isDark ? 'rgba(244, 244, 242, 0.14)' : 'rgba(17, 17, 17, 0.12)'
  const barColor = props.color ?? (ui.isDark ? '#f4f4f2' : '#111111')
  return {
    title: props.title ? { text: props.title, left: 8, top: 4, textStyle: { fontSize: 14 } } : undefined,
    grid: { left: 140, right: 24, top: props.title ? 40 : 16, bottom: 24 },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (v: unknown) => {
        const n = typeof v === 'number' ? v : Number(v)
        if (props.valueFormatter) return props.valueFormatter(n)
        return n.toLocaleString('zh-CN')
      },
    },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: axisColor },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: gridColor } },
    },
    yAxis: {
      type: 'category',
      data: props.categories,
      inverse: true,
      axisLine: { show: false },
      axisLabel: { color: axisColor },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        data: props.values,
        barMaxWidth: 18,
        itemStyle: {
          color: barColor,
          borderRadius: 0,
        },
      },
    ],
  }
})

useChart(container, option)
</script>

<template>
  <div class="bar-rank" v-loading="loading">
    <div ref="container" :style="{ height: height + 'px' }" />
  </div>
</template>
