<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import StatCard from '@/components/common/StatCard.vue'
import BarRank from '@/components/charts/BarRank.vue'
import PieCategory from '@/components/charts/PieCategory.vue'
import SalesTrendCombo from '@/components/charts/SalesTrendCombo.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { listInventory } from '@/api/inventory'
import {
  analyticsCategoriesSummary,
  analyticsMembersRank,
  analyticsProductsRank,
  analyticsStoresDaily,
} from '@/api/analytics'
import type {
  CategorySummaryRow,
  MemberRankRow,
  ProductRankRow,
  StoreDailyRow,
} from '@/api/types'
import { formatCurrency, formatDate, memberLevelLabel } from '@/utils/format'
import { downloadCsv } from '@/utils/download'
import { useDictsStore } from '@/stores/dicts'

const dicts = useDictsStore()

type TabName = 'store' | 'product' | 'member' | 'category'

const activeTab = ref<TabName>('store')

const filters = reactive<{
  date_range: [string, string]
  store_id: number | null
  category_id: number | null
  level: string | null
  limit: number
}>({
  date_range: [
    dayjs().subtract(29, 'day').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD'),
  ],
  store_id: null,
  category_id: null,
  level: null,
  limit: 10,
})

const loading = ref(false)
const storeRows = ref<StoreDailyRow[]>([])
const previousStoreRows = ref<StoreDailyRow[]>([])
const storeProductRows = ref<ProductRankRow[]>([])
const storeWarningCount = ref(0)
const productRows = ref<ProductRankRow[]>([])
const memberRows = ref<MemberRankRow[]>([])
const categoryRows = ref<CategorySummaryRow[]>([])

const selectedStoreName = computed(() => {
  if (!filters.store_id) return '全部门店'
  return dicts.stores.find((store) => store.store_id === filters.store_id)?.store_name || '当前门店'
})

function params() {
  const [date_from, date_to] = filters.date_range
  return { date_from, date_to }
}

function previousParams() {
  const start = dayjs(filters.date_range[0])
  const end = dayjs(filters.date_range[1])
  const days = Math.max(end.diff(start, 'day') + 1, 1)
  return {
    date_from: start.subtract(days, 'day').format('YYYY-MM-DD'),
    date_to: start.subtract(1, 'day').format('YYYY-MM-DD'),
  }
}

async function loadActive() {
  loading.value = true
  try {
    if (activeTab.value === 'store') {
      const storeId = filters.store_id ?? undefined
      const [currentRows, previousRows] = await Promise.all([
        analyticsStoresDaily({ ...params(), store_id: storeId }),
        analyticsStoresDaily({ ...previousParams(), store_id: storeId }),
      ])
      storeRows.value = currentRows
      previousStoreRows.value = previousRows
      if (storeId) {
        const [hotProducts, warnings] = await Promise.all([
          analyticsProductsRank({ ...params(), store_id: storeId, limit: 10 }),
          listInventory({ page: 1, page_size: 1, store_id: storeId, warning: true }),
        ])
        storeProductRows.value = hotProducts
        storeWarningCount.value = warnings.total
      } else {
        storeProductRows.value = []
        storeWarningCount.value = 0
      }
    } else if (activeTab.value === 'product') {
      productRows.value = await analyticsProductsRank({
        ...params(),
        store_id: filters.store_id ?? undefined,
        category_id: filters.category_id ?? undefined,
        limit: filters.limit,
      })
    } else if (activeTab.value === 'member') {
      memberRows.value = await analyticsMembersRank({
        ...params(),
        level: (filters.level ?? undefined) as never,
        limit: filters.limit,
      })
    } else if (activeTab.value === 'category') {
      categoryRows.value = await analyticsCategoriesSummary({
        ...params(),
        store_id: filters.store_id ?? undefined,
      })
    }
  } finally {
    loading.value = false
  }
}

function onReset() {
  filters.date_range = [
    dayjs().subtract(29, 'day').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD'),
  ]
  filters.store_id = null
  filters.category_id = null
  filters.level = null
  filters.limit = 10
  loadActive()
}

function salesQuery(extra: Record<string, string | number | undefined> = {}) {
  return {
    path: '/sales',
    query: {
      date_from: filters.date_range[0],
      date_to: filters.date_range[1],
      ...extra,
    },
  }
}

function saleDateKey(value: string | null | undefined) {
  const parsed = dayjs(value)
  return parsed.isValid() ? parsed.format('YYYY-MM-DD') : filters.date_range[0]
}

function dateRangeKeys() {
  const start = dayjs(filters.date_range[0])
  const end = dayjs(filters.date_range[1])
  if (!start.isValid() || !end.isValid() || end.isBefore(start)) return []
  const days = Math.min(end.diff(start, 'day'), 366)
  return Array.from({ length: days + 1 }, (_, index) => start.add(index, 'day').format('YYYY-MM-DD'))
}

function sumStoreRows(rows: StoreDailyRow[]) {
  const totalSales = rows.reduce((sum, row) => sum + Number(row.actual_amount_sum || 0), 0)
  const orderCount = rows.reduce((sum, row) => sum + Number(row.order_count || 0), 0)
  const soldQty = rows.reduce((sum, row) => sum + Number(row.sold_qty_sum || 0), 0)
  return {
    totalSales,
    orderCount,
    soldQty,
    avgOrder: orderCount ? totalSales / orderCount : 0,
  }
}

function percentChange(current: number, previous: number) {
  if (!previous) return current ? null : 0
  return ((current - previous) / previous) * 100
}

function formatDelta(value: number | null) {
  if (value === null) return '无上期基准'
  const prefix = value > 0 ? '+' : ''
  return `较前期 ${prefix}${value.toFixed(1)}%`
}

function formatQty(value: number) {
  return Math.round(value).toLocaleString('zh-CN')
}

function avgOrder(row: StoreDailyRow) {
  return row.order_count ? Number(row.actual_amount_sum || 0) / row.order_count : 0
}

function movingAverage(values: number[], windowSize = 7) {
  return values.map((_, index) => {
    const start = Math.max(0, index - windowSize + 1)
    const slice = values.slice(start, index + 1)
    return Number((slice.reduce((sum, value) => sum + value, 0) / slice.length).toFixed(2))
  })
}

// Chart data per tab
const storeTrend = computed(() => {
  const dateKeys = dateRangeKeys()
  const sales = new Map<string, number>()
  const orders = new Map<string, number>()
  dateKeys.forEach((date) => {
    sales.set(date, 0)
    orders.set(date, 0)
  })
  storeRows.value.forEach((row) => {
    if (!row.sale_date) return
    const parsed = dayjs(row.sale_date)
    if (!parsed.isValid()) return
    const key = parsed.format('YYYY-MM-DD')
    if (sales.has(key)) {
      sales.set(key, (sales.get(key) || 0) + Number(row.actual_amount_sum || 0))
      orders.set(key, (orders.get(key) || 0) + Number(row.order_count || 0))
    }
  })
  const salesData = dateKeys.map((date) => Number((sales.get(date) || 0).toFixed(2)))
  return {
    categories: dateKeys,
    sales: salesData,
    orders: dateKeys.map((date) => orders.get(date) || 0),
    movingAverage: movingAverage(salesData),
  }
})

const currentStoreMetrics = computed(() => sumStoreRows(storeRows.value))
const previousStoreMetrics = computed(() => sumStoreRows(previousStoreRows.value))

const storeMetricDeltas = computed(() => ({
  sales: percentChange(currentStoreMetrics.value.totalSales, previousStoreMetrics.value.totalSales),
  orders: percentChange(currentStoreMetrics.value.orderCount, previousStoreMetrics.value.orderCount),
  avgOrder: percentChange(currentStoreMetrics.value.avgOrder, previousStoreMetrics.value.avgOrder),
  soldQty: percentChange(currentStoreMetrics.value.soldQty, previousStoreMetrics.value.soldQty),
}))

const storeTrendSummary = computed(() => {
  const values = storeTrend.value.sales
  const max = values.length ? Math.max(...values) : 0
  const maxIndex = values.indexOf(max)
  return {
    max,
    maxDate: maxIndex >= 0 ? storeTrend.value.categories[maxIndex] : '',
  }
})

const storeRankRows = computed(() => {
  const grouped = new Map<number, { store_name: string; totalSales: number; orderCount: number; soldQty: number }>()
  storeRows.value.forEach((row) => {
    const current = grouped.get(row.store_id) || {
      store_name: row.store_name,
      totalSales: 0,
      orderCount: 0,
      soldQty: 0,
    }
    current.totalSales += Number(row.actual_amount_sum || 0)
    current.orderCount += Number(row.order_count || 0)
    current.soldQty += Number(row.sold_qty_sum || 0)
    grouped.set(row.store_id, current)
  })
  return Array.from(grouped.values())
    .map((row) => ({ ...row, avgOrder: row.orderCount ? row.totalSales / row.orderCount : 0 }))
    .sort((a, b) => b.totalSales - a.totalSales)
    .slice(0, 10)
})

const storeRankBar = computed(() => ({
  categories: storeRankRows.value.map((row) => row.store_name),
  values: storeRankRows.value.map((row) => Number(row.totalSales.toFixed(2))),
}))

const storeProductBar = computed(() => ({
  categories: storeProductRows.value.map((row) => row.product_name),
  values: storeProductRows.value.map((row) => Number(row.total_sales_amount || 0)),
}))

const storeDailyCompareMap = computed(() => {
  const map = new Map<string, number>()
  ;[...previousStoreRows.value, ...storeRows.value].forEach((row) => {
    const date = saleDateKey(row.sale_date)
    map.set(`${row.store_id}:${date}`, Number(row.actual_amount_sum || 0))
  })
  return map
})

function rowDayDelta(row: StoreDailyRow) {
  const previousDate = dayjs(row.sale_date).subtract(1, 'day').format('YYYY-MM-DD')
  const previous = storeDailyCompareMap.value.get(`${row.store_id}:${previousDate}`) || 0
  return percentChange(Number(row.actual_amount_sum || 0), previous)
}

const productBar = computed(() => ({
  categories: productRows.value.map((r) => r.product_name),
  values: productRows.value.map((r) => Number(r.total_sales_amount || 0)),
}))

const categoryPie = computed(() =>
  categoryRows.value.map((c) => ({ name: c.category_name, value: Number(c.total_sales_amount || 0) })),
)

// Export CSV
function exportCurrent() {
  if (activeTab.value === 'store') {
    downloadCsv(
      storeRows.value.map((row) => ({
        ...row,
        avg_order: avgOrder(row).toFixed(2),
        day_delta: formatDelta(rowDayDelta(row)).replace('较前期 ', ''),
      })) as unknown as Array<Record<string, unknown>>,
      [
        { key: 'sale_date', label: '日期' },
        { key: 'store_name', label: '门店' },
        { key: 'order_count', label: '订单数' },
        { key: 'sold_qty_sum', label: '销售商品数' },
        { key: 'actual_amount_sum', label: '实付总额' },
        { key: 'avg_order', label: '客单价' },
        { key: 'day_delta', label: '环比' },
      ],
      `门店日销_${filters.date_range[0]}_${filters.date_range[1]}`,
    )
  } else if (activeTab.value === 'product') {
    downloadCsv(
      productRows.value as unknown as Array<Record<string, unknown>>,
      [
        { key: 'product_id', label: '商品ID' },
        { key: 'product_name', label: '商品名称' },
        { key: 'status', label: '状态' },
        { key: 'total_qty', label: '销量' },
        { key: 'total_sales_amount', label: '销售额' },
      ],
      `商品销售排行_${filters.date_range[0]}_${filters.date_range[1]}`,
    )
  } else if (activeTab.value === 'member') {
    downloadCsv(
      memberRows.value as unknown as Array<Record<string, unknown>>,
      [
        { key: 'member_no', label: '会员编号' },
        { key: 'customer_name', label: '姓名' },
        { key: 'level', label: '等级' },
        { key: 'order_count', label: '订单数' },
        { key: 'total_spending', label: '累计消费' },
      ],
      `会员消费排行_${filters.date_range[0]}_${filters.date_range[1]}`,
    )
  } else {
    downloadCsv(
      categoryRows.value as unknown as Array<Record<string, unknown>>,
      [
        { key: 'category_id', label: '分类ID' },
        { key: 'category_name', label: '分类名称' },
        { key: 'total_qty', label: '销量' },
        { key: 'total_sales_amount', label: '销售额' },
      ],
      `分类销售汇总_${filters.date_range[0]}_${filters.date_range[1]}`,
    )
  }
}

watch(activeTab, () => loadActive())

onMounted(() => {
  dicts.ensureStores()
  dicts.ensureCategories()
  loadActive()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="销售分析" subtitle="按门店、商品、会员、分类四个维度钻取销售数据">
      <template #extra>
        <el-button @click="exportCurrent">
          <el-icon><Download /></el-icon>导出当前视图
        </el-button>
      </template>
    </PageHeader>

    <FilterBar :loading="loading" @submit="loadActive" @reset="onReset">
      <el-form-item label="日期">
        <el-date-picker
          v-model="filters.date_range"
          type="daterange"
          value-format="YYYY-MM-DD"
          start-placeholder="开始"
          end-placeholder="结束"
          range-separator="—"
          style="width: 260px"
        />
      </el-form-item>
      <el-form-item v-if="activeTab === 'store' || activeTab === 'product' || activeTab === 'category'" label="门店">
        <el-select v-model="filters.store_id" clearable placeholder="全部门店" style="width: 180px">
          <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="activeTab === 'product'" label="分类">
        <el-select v-model="filters.category_id" clearable filterable placeholder="全部分类" style="width: 200px">
          <el-option
            v-for="c in dicts.categories"
            :key="c.category_id"
            :label="c.parent_category_name ? `${c.parent_category_name} / ${c.category_name}` : c.category_name"
            :value="c.category_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item v-if="activeTab === 'member'" label="等级">
        <el-select v-model="filters.level" clearable placeholder="全部等级" style="width: 140px">
          <el-option label="青铜" value="bronze" />
          <el-option label="白银" value="silver" />
          <el-option label="黄金" value="gold" />
          <el-option label="铂金" value="platinum" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="activeTab === 'product' || activeTab === 'member'" label="Top N">
        <el-input-number v-model="filters.limit" :min="1" :max="100" :step="1" :step-strictly="true" style="width: 132px" />
      </el-form-item>
    </FilterBar>

    <el-tabs v-model="activeTab" class="analytics-tabs" type="card">
      <el-tab-pane label="门店日报" name="store">
        <section class="stat-grid analytics-stat-grid">
          <StatCard
            :label="filters.store_id ? '该门店销售额' : '总销售额'"
            :value="formatCurrency(currentStoreMetrics.totalSales)"
            :hint="formatDelta(storeMetricDeltas.sales)"
            icon="Money"
            tone="brand"
            :loading="loading"
          />
          <StatCard
            :label="filters.store_id ? '该门店订单数' : '订单数'"
            :value="formatQty(currentStoreMetrics.orderCount)"
            :hint="formatDelta(storeMetricDeltas.orders)"
            icon="Tickets"
            tone="accent"
            :loading="loading"
          />
          <StatCard
            label="客单价"
            :value="formatCurrency(currentStoreMetrics.avgOrder)"
            :hint="formatDelta(storeMetricDeltas.avgOrder)"
            icon="TrendCharts"
            tone="warning"
            :loading="loading"
          />
          <StatCard
            v-if="filters.store_id"
            label="库存预警商品数"
            :value="storeWarningCount"
            hint="当前门店库存小于等于安全库存"
            icon="WarningFilled"
            tone="danger"
            :loading="loading"
          />
          <StatCard
            v-else
            label="销售商品数"
            :value="formatQty(currentStoreMetrics.soldQty)"
            :hint="formatDelta(storeMetricDeltas.soldQty)"
            icon="Goods"
            tone="success"
            :loading="loading"
          />
        </section>

        <article v-if="storeTrend.categories.length" class="app-card">
          <h3 class="section-title">
            <el-icon><TrendCharts /></el-icon>{{ selectedStoreName }}每日销售额与订单数
          </h3>
          <div class="trend-summary">
            <span>峰值 {{ saleDateKey(storeTrendSummary.maxDate) }} {{ formatCurrency(storeTrendSummary.max) }}</span>
            <span>销售额柱状展示，订单数与 7 日移动平均使用折线展示</span>
          </div>
          <SalesTrendCombo
            :categories="storeTrend.categories.map((d) => dayjs(d).format('MM-DD'))"
            :sales="storeTrend.sales"
            :orders="storeTrend.orders"
            :moving-average="storeTrend.movingAverage"
            :height="330"
            :loading="loading"
          />
        </article>

        <article v-if="!filters.store_id && storeRankBar.categories.length" class="app-card analytics-section">
          <h3 class="section-title"><el-icon><Trophy /></el-icon>门店销售额 Top 10</h3>
          <BarRank
            :categories="storeRankBar.categories"
            :values="storeRankBar.values"
            :height="Math.max(300, storeRankBar.categories.length * 30 + 90)"
            :value-formatter="(v) => formatCurrency(v)"
            :loading="loading"
          />
        </article>

        <article v-if="filters.store_id && storeProductBar.categories.length" class="app-card analytics-section">
          <h3 class="section-title"><el-icon><Trophy /></el-icon>{{ selectedStoreName }}热销商品 Top 10</h3>
          <BarRank
            :categories="storeProductBar.categories"
            :values="storeProductBar.values"
            :height="Math.max(300, storeProductBar.categories.length * 30 + 90)"
            :value-formatter="(v) => formatCurrency(v)"
            :loading="loading"
          />
        </article>

        <article class="app-card" style="margin-top: 12px">
          <h3 class="section-title"><el-icon><Tickets /></el-icon>明细</h3>
          <el-table :data="storeRows" border stripe v-loading="loading">
            <el-table-column label="日期" width="140">
              <template #default="{ row }">{{ formatDate(row.sale_date) }}</template>
            </el-table-column>
            <el-table-column prop="store_name" label="门店" min-width="160" />
            <el-table-column prop="order_count" label="订单数" width="100" align="right" />
            <el-table-column label="销售商品数" width="120" align="right">
              <template #default="{ row }">{{ formatQty(row.sold_qty_sum) }}</template>
            </el-table-column>
            <el-table-column label="实付" width="140" align="right">
              <template #default="{ row }"><strong class="money" style="color: var(--brand)">{{ formatCurrency(row.actual_amount_sum) }}</strong></template>
            </el-table-column>
            <el-table-column label="客单价" width="130" align="right">
              <template #default="{ row }"><span class="money">{{ formatCurrency(avgOrder(row)) }}</span></template>
            </el-table-column>
            <el-table-column label="环比" width="110" align="right">
              <template #default="{ row }">{{ formatDelta(rowDayDelta(row)).replace('较前期 ', '') }}</template>
            </el-table-column>
            <el-table-column label="明细" width="90" align="right">
              <template #default="{ row }">
                <router-link :to="salesQuery({ store_id: row.store_id, date_from: saleDateKey(row.sale_date), date_to: saleDateKey(row.sale_date) })">查看</router-link>
              </template>
            </el-table-column>
          </el-table>
          <EmptyState v-if="!loading && !storeRows.length" icon="TrendCharts" title="暂无数据" description="调整日期范围或门店再试" />
        </article>
      </el-tab-pane>

      <el-tab-pane label="商品排行" name="product">
        <article v-if="productBar.categories.length" class="app-card">
          <h3 class="section-title"><el-icon><Trophy /></el-icon>销售额 Top {{ filters.limit }}</h3>
          <BarRank
            :categories="productBar.categories"
            :values="productBar.values"
            :height="Math.max(300, productBar.categories.length * 28 + 80)"
            :value-formatter="(v) => formatCurrency(v)"
            :loading="loading"
          />
        </article>
        <article class="app-card" style="margin-top: 12px">
          <el-table :data="productRows" border stripe v-loading="loading">
            <el-table-column prop="product_id" label="ID" width="90" />
            <el-table-column prop="product_name" label="商品" min-width="220" />
            <el-table-column prop="status" label="状态" width="100" />
            <el-table-column prop="total_qty" label="销量" width="120" align="right" />
            <el-table-column label="销售额" width="160" align="right">
              <template #default="{ row }"><span class="money">{{ formatCurrency(row.total_sales_amount) }}</span></template>
            </el-table-column>
            <el-table-column label="明细" width="90" align="right">
              <template #default>
                <router-link :to="salesQuery({ store_id: filters.store_id ?? undefined })">时段</router-link>
              </template>
            </el-table-column>
          </el-table>
          <EmptyState v-if="!loading && !productRows.length" icon="Goods" title="无销售记录" />
        </article>
      </el-tab-pane>

      <el-tab-pane label="会员消费" name="member">
        <article class="app-card">
          <el-table :data="memberRows" border stripe v-loading="loading">
            <el-table-column prop="member_no" label="会员编号" width="160" />
            <el-table-column prop="customer_name" label="姓名" min-width="140" />
            <el-table-column label="等级" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="light">{{ memberLevelLabel(row.level) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="order_count" label="订单数" width="100" align="right" />
            <el-table-column label="累计消费" width="160" align="right">
              <template #default="{ row }"><strong class="money" style="color: var(--brand)">{{ formatCurrency(row.total_spending) }}</strong></template>
            </el-table-column>
            <el-table-column label="明细" width="90" align="right">
              <template #default="{ row }">
                <router-link :to="salesQuery({ customer_id: row.customer_id })">查看</router-link>
              </template>
            </el-table-column>
          </el-table>
          <EmptyState v-if="!loading && !memberRows.length" icon="Medal" title="无会员消费记录" />
        </article>
      </el-tab-pane>

      <el-tab-pane label="分类汇总" name="category">
        <article v-if="categoryPie.length" class="app-card">
          <h3 class="section-title"><el-icon><PieChart /></el-icon>分类销售占比</h3>
          <PieCategory :data="categoryPie" :loading="loading" :height="320" />
        </article>
        <article class="app-card" style="margin-top: 12px">
          <el-table :data="categoryRows" border stripe v-loading="loading">
            <el-table-column prop="category_id" label="ID" width="90" />
            <el-table-column prop="category_name" label="分类" min-width="180" />
            <el-table-column prop="total_qty" label="销量" width="120" align="right" />
            <el-table-column label="销售额" width="160" align="right">
              <template #default="{ row }"><span class="money">{{ formatCurrency(row.total_sales_amount) }}</span></template>
            </el-table-column>
            <el-table-column label="明细" width="90" align="right">
              <template #default>
                <router-link :to="salesQuery({ store_id: filters.store_id ?? undefined })">时段</router-link>
              </template>
            </el-table-column>
          </el-table>
          <EmptyState v-if="!loading && !categoryRows.length" icon="Menu" title="无分类销售记录" />
        </article>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.analytics-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--app-border);
}

.analytics-stat-grid {
  margin: 0 0 12px;
}

.analytics-section {
  margin-top: 12px;
}

.trend-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin: -2px 0 10px;
  color: var(--app-text-muted);
  font-size: 13px;
}
</style>
