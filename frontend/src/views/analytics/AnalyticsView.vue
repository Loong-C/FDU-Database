<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import LineTrend from '@/components/charts/LineTrend.vue'
import BarRank from '@/components/charts/BarRank.vue'
import PieCategory from '@/components/charts/PieCategory.vue'
import EmptyState from '@/components/common/EmptyState.vue'
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
const productRows = ref<ProductRankRow[]>([])
const memberRows = ref<MemberRankRow[]>([])
const categoryRows = ref<CategorySummaryRow[]>([])

function params() {
  const [date_from, date_to] = filters.date_range
  return { date_from, date_to }
}

async function loadActive() {
  loading.value = true
  try {
    if (activeTab.value === 'store') {
      storeRows.value = await analyticsStoresDaily({
        ...params(),
        store_id: filters.store_id ?? undefined,
      })
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
      categoryRows.value = await analyticsCategoriesSummary(params())
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

// Chart data per tab
const storeTrend = computed(() => {
  const dates = new Set<string>()
  const series = new Map<string, Map<string, number>>() // store -> date -> value
  storeRows.value.forEach((row) => {
    // 防御性过滤：后端 TruncDate 理论上始终返回有效日期，但任何 null/解析失败都
    // 会让 dayjs().format() 吐出 "Invalid Date"，进而污染 ECharts 的类目轴。
    if (!row.sale_date) return
    const parsed = dayjs(row.sale_date)
    if (!parsed.isValid()) return
    const key = parsed.format('YYYY-MM-DD')
    dates.add(key)
    if (!series.has(row.store_name)) series.set(row.store_name, new Map())
    series.get(row.store_name)!.set(key, Number(row.actual_amount_sum || 0))
  })
  const sorted = Array.from(dates).sort((a, b) => dayjs(a).valueOf() - dayjs(b).valueOf())
  return {
    categories: sorted,
    series: Array.from(series.entries()).map(([name, values]) => ({
      name,
      data: sorted.map((d) => Number((values.get(d) ?? 0).toFixed(2))),
    })),
  }
})

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
      storeRows.value as unknown as Array<Record<string, unknown>>,
      [
        { key: 'sale_date', label: '日期' },
        { key: 'store_name', label: '门店' },
        { key: 'order_count', label: '订单数' },
        { key: 'total_amount_sum', label: '原始总额' },
        { key: 'discount_amount_sum', label: '折扣合计' },
        { key: 'actual_amount_sum', label: '实付总额' },
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
      <el-form-item v-if="activeTab === 'store' || activeTab === 'product'" label="门店">
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
        <article v-if="storeTrend.series.length" class="app-card">
          <h3 class="section-title"><el-icon><TrendCharts /></el-icon>门店实付趋势</h3>
          <LineTrend
            :categories="storeTrend.categories.map((d) => dayjs(d).format('MM-DD'))"
            :series="storeTrend.series"
            y-axis-name="金额(元)"
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
            <el-table-column label="原始总额" width="140" align="right">
              <template #default="{ row }"><span class="money">{{ formatCurrency(row.total_amount_sum) }}</span></template>
            </el-table-column>
            <el-table-column label="折扣" width="120" align="right">
              <template #default="{ row }"><span class="money" style="color: var(--warning)">-{{ formatCurrency(row.discount_amount_sum) }}</span></template>
            </el-table-column>
            <el-table-column label="实付" width="140" align="right">
              <template #default="{ row }"><strong class="money" style="color: var(--brand)">{{ formatCurrency(row.actual_amount_sum) }}</strong></template>
            </el-table-column>
            <el-table-column label="明细" width="90" align="right">
              <template #default="{ row }">
                <router-link :to="salesQuery({ store_id: row.store_id, date_from: dayjs(row.sale_date).format('YYYY-MM-DD'), date_to: dayjs(row.sale_date).format('YYYY-MM-DD') })">查看</router-link>
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
                <router-link :to="salesQuery()">时段</router-link>
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
</style>
