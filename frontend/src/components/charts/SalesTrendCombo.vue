<script setup lang="ts">
import { computed, ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useChart, type EChartsCoreOption } from './useChart'

const props = withDefaults(defineProps<{
  categories: string[]
  sales: number[]
  orders: number[]
  movingAverage?: number[]
  height?: number
  loading?: boolean
}>(), { height: 320 })

const container = ref<HTMLElement | null>(null)
const ui = useUiStore()

const option = computed<EChartsCoreOption | null>(() => {
  if (!props.categories.length) return null
  const axisColor = ui.isDark ? '#b7b7b0' : '#5f5f5f'
  const gridColor = ui.isDark ? 'rgba(244, 244, 242, 0.14)' : 'rgba(17, 17, 17, 0.12)'
  const labelInterval = Math.max(Math.ceil(props.categories.length / 12) - 1, 0)
  return {
    grid: { left: 72, right: 72, top: 48, bottom: 90 },
    legend: {
      bottom: 8,
      itemGap: 22,
      textStyle: { color: axisColor },
    },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value: unknown) => {
        const numeric = typeof value === 'number' ? value : Number(value)
        return Number.isFinite(numeric) ? numeric.toLocaleString('zh-CN') : String(value)
      },
    },
    xAxis: {
      type: 'category',
      data: props.categories,
      axisLine: { lineStyle: { color: gridColor } },
      axisLabel: { color: axisColor, interval: labelInterval },
      axisTick: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: '销售额 / 元',
        nameGap: 18,
        axisLine: { show: false },
        axisLabel: { color: axisColor },
        nameTextStyle: { color: axisColor },
        axisTick: { show: false },
        splitLine: { lineStyle: { color: gridColor } },
      },
      {
        type: 'value',
        name: '订单数',
        nameGap: 18,
        axisLine: { show: false },
        axisLabel: { color: axisColor },
        nameTextStyle: { color: axisColor },
        axisTick: { show: false },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '每日销售额',
        type: 'bar',
        data: props.sales,
        yAxisIndex: 0,
        barMaxWidth: 18,
        itemStyle: { color: ui.isDark ? '#ff4b42' : '#e10600', opacity: 0.72 },
      },
      {
        name: '7日移动平均',
        type: 'line',
        data: props.movingAverage || [],
        yAxisIndex: 0,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2.5, type: 'dashed' },
      },
      {
        name: '每日订单数',
        type: 'line',
        data: props.orders,
        yAxisIndex: 1,
        smooth: true,
        showSymbol: false,
        lineStyle: { width: 2.5 },
      },
    ],
    color: ui.isDark ? ['#ff4b42', '#f4f4f2', '#9ca3af'] : ['#e10600', '#111111', '#6f6f6f'],
  }
})

useChart(container, option)
</script>

<template>
  <div class="sales-trend-combo" v-loading="loading">
    <div ref="container" :style="{ height: height + 'px' }" />
  </div>
</template>

<style scoped>
.sales-trend-combo {
  width: 100%;
}
</style>
