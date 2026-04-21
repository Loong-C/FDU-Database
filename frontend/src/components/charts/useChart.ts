import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  TransformComponent,
} from 'echarts/components'
import { onBeforeUnmount, onMounted, ref, watch, type Ref } from 'vue'
import { useUiStore } from '@/stores/ui'

echarts.use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  DatasetComponent,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  TransformComponent,
])

export type { EChartsCoreOption } from 'echarts/core'
export { echarts }

export function useChart(
  containerRef: Ref<HTMLElement | null>,
  optionRef: Ref<echarts.EChartsCoreOption | null>,
) {
  let instance: echarts.ECharts | null = null
  const ui = useUiStore()
  const ready = ref(false)

  function ensure() {
    if (!containerRef.value) return null
    if (!instance) {
      instance = echarts.init(containerRef.value, ui.isDark ? 'dark' : undefined, { renderer: 'canvas' })
      ready.value = true
    }
    return instance
  }

  function render() {
    const chart = ensure()
    if (!chart || !optionRef.value) return
    chart.setOption(optionRef.value, true)
    chart.resize()
  }

  function dispose() {
    instance?.dispose()
    instance = null
    ready.value = false
  }

  function resize() {
    instance?.resize()
  }

  onMounted(() => {
    render()
    window.addEventListener('resize', resize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', resize)
    dispose()
  })

  watch(optionRef, () => render(), { deep: true })
  watch(
    () => ui.isDark,
    () => {
      dispose()
      render()
    },
  )

  return { resize, dispose, ready }
}
