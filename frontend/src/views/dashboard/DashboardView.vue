<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/common/PageHeader.vue'
import StatCard from '@/components/common/StatCard.vue'
import LineTrend from '@/components/charts/LineTrend.vue'
import BarRank from '@/components/charts/BarRank.vue'
import PieCategory from '@/components/charts/PieCategory.vue'
import {
  analyticsCategoriesSummary,
  analyticsMembersRank,
  analyticsProductsRank,
  analyticsStoresDaily,
} from '@/api/analytics'
import { listProducts } from '@/api/products'
import type {
  CategorySummaryRow,
  MemberRankRow,
  ProductRankRow,
  StoreDailyRow,
} from '@/api/types'
import { formatCurrency, memberLevelLabel } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const loadingDaily = ref(false)
const loadingProduct = ref(false)
const loadingCategory = ref(false)
const loadingMember = ref(false)
const loadingStock = ref(false)

const dailyRows = ref<StoreDailyRow[]>([])
const productRank = ref<ProductRankRow[]>([])
const categorySummary = ref<CategorySummaryRow[]>([])
const memberRank = ref<MemberRankRow[]>([])
const lowStockCount = ref(0)

const last7Days = computed(() => {
  const arr: string[] = []
  for (let i = 6; i >= 0; i--) arr.push(dayjs().subtract(i, 'day').format('YYYY-MM-DD'))
  return arr
})

const todayKey = dayjs().format('YYYY-MM-DD')

const todayStat = computed(() => {
  let sales = 0
  let orders = 0
  dailyRows.value.forEach((row) => {
    if (dayjs(row.sale_date).format('YYYY-MM-DD') === todayKey) {
      sales += Number(row.actual_amount_sum || 0)
      orders += row.order_count
    }
  })
  return { sales, orders }
})

const topMember = computed(() => memberRank.value[0] || null)

const lineChartCategories = computed(() => last7Days.value.map((d) => dayjs(d).format('MM-DD')))
const lineChartData = computed(() => {
  // group by date summing actual_amount_sum across stores
  const map = new Map<string, number>()
  last7Days.value.forEach((d) => map.set(d, 0))
  dailyRows.value.forEach((row) => {
    const key = dayjs(row.sale_date).format('YYYY-MM-DD')
    if (map.has(key)) map.set(key, (map.get(key) || 0) + Number(row.actual_amount_sum || 0))
  })
  return [
    {
      name: '实付金额',
      data: last7Days.value.map((d) => Number(map.get(d) || 0).toFixed(2)),
    },
  ]
})

const productBarCategories = computed(() => productRank.value.map((r) => r.product_name))
const productBarValues = computed(() => productRank.value.map((r) => Number(r.total_sales_amount || 0)))

const pieData = computed(() =>
  categorySummary.value.map((c) => ({
    name: c.category_name,
    value: Number(c.total_sales_amount || 0),
  })),
)

async function fetchAll() {
  const dateFrom = last7Days.value[0]
  const dateTo = dayjs().format('YYYY-MM-DD')
  loadingDaily.value = true
  loadingProduct.value = true
  loadingCategory.value = true
  loadingMember.value = true
  loadingStock.value = true
  try {
    const [daily, prod, cat, members] = await Promise.all([
      analyticsStoresDaily({ date_from: dateFrom, date_to: dateTo }),
      analyticsProductsRank({ limit: 10, date_from: dateFrom, date_to: dateTo }),
      analyticsCategoriesSummary({ date_from: dateFrom, date_to: dateTo }),
      analyticsMembersRank({ limit: 5, date_from: dateFrom, date_to: dateTo }),
    ])
    dailyRows.value = daily
    productRank.value = prod
    categorySummary.value = cat
    memberRank.value = members
  } finally {
    loadingDaily.value = false
    loadingProduct.value = false
    loadingCategory.value = false
    loadingMember.value = false
  }

  // 库存预警（客户端过滤，避免再造接口）
  try {
    const data = await listProducts({ page: 1, page_size: 100, status: 'onsale' })
    lowStockCount.value = data.items.filter((p) => p.stock_qty < 10).length
  } finally {
    loadingStock.value = false
  }
}

onMounted(fetchAll)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader :title="`你好，${auth.user?.display_name || auth.user?.username}`" subtitle="今日业务概况与近 7 天趋势一览">
      <template #extra>
        <el-button @click="fetchAll">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </template>
    </PageHeader>

    <section class="stat-grid">
      <StatCard
        label="今日销售额"
        :value="formatCurrency(todayStat.sales)"
        tone="brand"
        icon="Money"
        :loading="loadingDaily"
        hint="来自所有门店当日实付总额"
      />
      <StatCard
        label="今日订单数"
        :value="todayStat.orders.toLocaleString('zh-CN')"
        tone="accent"
        icon="Tickets"
        :loading="loadingDaily"
        hint="所有门店销售单数量"
      />
      <StatCard
        label="最高消费会员（近 7 日）"
        :value="topMember ? `${topMember.customer_name} · ${memberLevelLabel(topMember.level)}` : '暂无'"
        tone="warning"
        icon="Medal"
        :loading="loadingMember"
      >
        <template #hint>
          <span v-if="topMember">累计 {{ formatCurrency(topMember.total_spending) }}，{{ topMember.order_count }} 单</span>
          <span v-else>近 7 日无会员消费</span>
        </template>
      </StatCard>
      <StatCard
        label="低库存预警"
        :value="lowStockCount"
        tone="danger"
        icon="WarningFilled"
        :loading="loadingStock"
        hint="在售商品中库存 < 10 的 SKU 数量"
      />
    </section>

    <section class="chart-grid">
      <article class="app-card">
        <h3 class="section-title">
          <el-icon><TrendCharts /></el-icon>近 7 日销售趋势
        </h3>
        <LineTrend
          :categories="lineChartCategories"
          :series="lineChartData"
          :loading="loadingDaily"
          y-axis-name="金额(元)"
        />
      </article>
      <article class="app-card">
        <h3 class="section-title">
          <el-icon><PieChart /></el-icon>分类销售占比
        </h3>
        <PieCategory :data="pieData" :loading="loadingCategory" />
      </article>
    </section>

    <article class="app-card">
      <h3 class="section-title">
        <el-icon><Crown /></el-icon>热销商品 TOP 10（近 7 日）
      </h3>
      <BarRank
        :categories="productBarCategories"
        :values="productBarValues"
        :loading="loadingProduct"
        :value-formatter="(v) => formatCurrency(v)"
        :height="Math.max(280, productBarCategories.length * 28 + 80)"
      />
    </article>
  </div>
</template>
