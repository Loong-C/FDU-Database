<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
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
import { listInventory } from '@/api/inventory'
import type {
  CategorySummaryRow,
  InventoryRow,
  MemberRankRow,
  ProductRankRow,
  StoreDailyRow,
} from '@/api/types'
import { formatCurrency, formatDateTime, memberLevelLabel } from '@/utils/format'
import { useDictsStore } from '@/stores/dicts'
import { DEFAULT_STORE_ID, defaultStoreId } from '@/utils/defaults'

const router = useRouter()
const dicts = useDictsStore()

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
const lowStockRows = ref<InventoryRow[]>([])
const selectedStoreId = ref<number>(DEFAULT_STORE_ID)

const selectedStoreName = computed(() =>
  dicts.stores.find((store) => store.store_id === selectedStoreId.value)?.store_name || '当前门店',
)

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
      data: last7Days.value.map((d) => Number((map.get(d) || 0).toFixed(2))),
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
  const storeId = selectedStoreId.value
  loadingDaily.value = true
  loadingProduct.value = true
  loadingCategory.value = true
  loadingMember.value = true
  loadingStock.value = true
  try {
    const [daily, prod, cat, members] = await Promise.all([
      analyticsStoresDaily({ store_id: storeId, date_from: dateFrom, date_to: dateTo }),
      analyticsProductsRank({ store_id: storeId, limit: 10, date_from: dateFrom, date_to: dateTo }),
      analyticsCategoriesSummary({ store_id: storeId, date_from: dateFrom, date_to: dateTo }),
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

  try {
    const warnings = await listInventory({ page: 1, page_size: 5, store_id: storeId, warning: true })
    lowStockRows.value = warnings.items
    lowStockCount.value = warnings.total
  } finally {
    loadingStock.value = false
  }
}

function openReplenish(row: InventoryRow) {
  const suggestQty = Math.max(row.safety_stock_qty - row.stock_qty + 1, 1)
  router.push({
    path: '/purchase-orders',
    query: {
      replenish_product_id: String(row.product_id),
      store_id: String(row.store_id),
      qty: String(suggestQty),
    },
  })
}

async function initialize() {
  await dicts.ensureStores()
  selectedStoreId.value = defaultStoreId(dicts.stores)
  await fetchAll()
}

onMounted(initialize)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="经营总览">
      <template #extra>
        <div class="dashboard-actions">
          <el-select v-model="selectedStoreId" placeholder="选择门店" style="width: 190px" @change="fetchAll">
            <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
          </el-select>
          <el-button @click="fetchAll">
            <el-icon><Refresh /></el-icon>刷新
          </el-button>
        </div>
      </template>
    </PageHeader>

    <section class="stat-grid">
      <StatCard
        label="今日销售额"
        :value="formatCurrency(todayStat.sales)"
        tone="brand"
        icon="Money"
        :loading="loadingDaily"
        :hint="`${selectedStoreName} 当日实付总额`"
      />
      <StatCard
        label="今日订单数"
        :value="todayStat.orders.toLocaleString('zh-CN')"
        tone="accent"
        icon="Tickets"
        :loading="loadingDaily"
        :hint="`${selectedStoreName} 当日销售单数量`"
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
        :hint="`${selectedStoreName} 库存小于等于安全库存的商品数`"
      />
    </section>

    <article v-if="lowStockRows.length" class="app-card">
      <h3 class="section-title">
        <el-icon><WarningFilled /></el-icon>库存预警
      </h3>
      <el-table :data="lowStockRows" border stripe size="small" v-loading="loadingStock">
        <el-table-column prop="store_name" label="门店" min-width="140" />
        <el-table-column prop="product_name" label="商品" min-width="220" />
        <el-table-column prop="stock_qty" label="当前库存" width="100" align="right" />
        <el-table-column prop="safety_stock_qty" label="安全库存" width="100" align="right" />
        <el-table-column label="更新时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="下一步" width="110" align="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openReplenish(row)">补货</el-button>
          </template>
        </el-table-column>
      </el-table>
    </article>

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
        <el-icon><Trophy /></el-icon>热销商品 TOP 10（近 7 日）
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

<style scoped>
.dashboard-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
