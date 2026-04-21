<script setup lang="ts">
import { computed, ref } from 'vue'
import { useChart, type EChartsCoreOption } from './useChart'

const props = withDefaults(defineProps<{
  title?: string
  categories: string[]
  values: Array<number | string>
  height?: number
  color?: string
  loading?: boolean
  valueFormatter?: (v: number) => string
}>(), { height: 320, color: '#4f46e5' })

const container = ref<HTMLElement | null>(null)

const option = computed<EChartsCoreOption | null>(() => {
  if (!props.categories.length) return null
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
      axisTick: { show: false },
      splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.18)' } },
    },
    yAxis: {
      type: 'category',
      data: props.categories,
      inverse: true,
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        type: 'bar',
        data: props.values,
        barMaxWidth: 18,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 1,
            y2: 0,
            colorStops: [
              { offset: 0, color: `${props.color}33` },
              { offset: 1, color: props.color },
            ],
          },
          borderRadius: [0, 6, 6, 0],
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
