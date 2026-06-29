<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { deleteSale, listSales, type SaleQuery } from '@/api/sales'
import type { Sale } from '@/api/types'
import { formatCurrency, formatDateTime, paymentLabel } from '@/utils/format'
import { useDictsStore } from '@/stores/dicts'
import { useAuthStore } from '@/stores/auth'
import { defaultStoreId } from '@/utils/defaults'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'
const dicts = useDictsStore()

const rows = ref<Sale[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive<SaleQuery & { date_range: [string, string] | null }>({
  store_id: undefined,
  customer_id: undefined,
  payment_method: undefined,
  date_range: null,
})

function numericQueryValue(value: unknown): number | undefined {
  const raw = Array.isArray(value) ? value[0] : value
  const numeric = Number(raw || 0)
  return numeric || undefined
}

function applyRouteFilters() {
  const dateFrom = typeof route.query.date_from === 'string' ? route.query.date_from : undefined
  const dateTo = typeof route.query.date_to === 'string' ? route.query.date_to : undefined
  filters.store_id = numericQueryValue(route.query.store_id) ?? defaultStoreId(dicts.stores)
  filters.customer_id = numericQueryValue(route.query.customer_id)
  filters.payment_method = undefined
  filters.date_range = dateFrom && dateTo ? [dateFrom, dateTo] : null
}

async function fetchList() {
  loading.value = true
  try {
    const [dateFrom, dateTo] = filters.date_range ?? [undefined, undefined]
    const data = await listSales({
      page: page.value,
      page_size: pageSize.value,
      store_id: filters.store_id,
      customer_id: filters.customer_id,
      payment_method: filters.payment_method,
      date_from: dateFrom,
      date_to: dateTo,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function onDelete(row: Sale) {
  try {
    await ElMessageBox.confirm(`确定删除销售单 #${row.sale_id}？对应商品库存将自动回滚。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteSale(row.sale_id)
    ElMessage.success('销售单已删除，库存已回滚')
    fetchList()
  } catch {
    /* error shown by interceptor */
  }
}

watch(
  () => route.query,
  () => {
    applyRouteFilters()
    page.value = 1
    fetchList()
  },
)

onMounted(async () => {
  await dicts.ensureStores()
  applyRouteFilters()
  fetchList()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="销售订单" subtitle="查询并管理销售记录，支持按门店、支付方式、日期范围筛选">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="router.push('/sales/new')">
          <el-icon><Plus /></el-icon>新开销售单
        </el-button>
      </template>
    </PageHeader>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="() => { filters.store_id=defaultStoreId(dicts.stores); filters.customer_id=undefined; filters.payment_method=undefined; filters.date_range=null; page=1; fetchList() }"
    >
      <el-form-item label="门店">
        <el-select v-model="filters.store_id" placeholder="全部" clearable style="width: 180px">
          <el-option
            v-for="s in dicts.stores"
            :key="s.store_id"
            :label="s.store_name"
            :value="s.store_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="支付方式">
        <el-select v-model="filters.payment_method" placeholder="全部" clearable style="width: 160px">
          <el-option label="现金" value="cash" />
          <el-option label="银行卡" value="card" />
          <el-option label="微信" value="wechat" />
          <el-option label="支付宝" value="alipay" />
          <el-option label="混合" value="mixed" />
        </el-select>
      </el-form-item>
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="filters.date_range"
          type="daterange"
          range-separator="—"
          start-placeholder="开始"
          end-placeholder="结束"
          value-format="YYYY-MM-DD"
          style="width: 280px"
        />
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="sale_id"
      empty-icon="Tickets"
      empty-title="暂无销售单"
      empty-description="在此筛选条件下没有记录，或暂未开单"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column label="#" width="70">
        <template #default="{ row }">
          <router-link :to="`/sales/${row.sale_id}`" class="sale-id">#{{ row.sale_id }}</router-link>
        </template>
      </el-table-column>
      <el-table-column prop="store_name" label="门店" min-width="85" />
      <el-table-column label="客户" min-width="75">
        <template #default="{ row }">
          <span v-if="row.customer_name">{{ row.customer_name }}</span>
          <span v-else class="text-muted">游客</span>
        </template>
      </el-table-column>
      <el-table-column label="支付" width="112">
        <template #default="{ row }">
          <el-tag class="payment-tag" size="small" effect="plain" round>{{ paymentLabel(row.payment_method) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="数量" width="64" align="right">
        <template #default="{ row }">
          <span class="money">{{ row.items?.length ?? 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column label="原价" width="100" align="right">
        <template #default="{ row }">
          <span class="money text-muted">{{ formatCurrency(row.total_amount) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="优惠" width="100" align="right">
        <template #default="{ row }">
          <span class="money" :style="{ color: Number(row.discount_amount) > 0 ? 'var(--warning)' : undefined }">
            -{{ formatCurrency(row.discount_amount) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="实付" width="110" align="right">
        <template #default="{ row }">
          <strong class="money" style="color: var(--brand)">{{ formatCurrency(row.actual_amount) }}</strong>
        </template>
      </el-table-column>
      <el-table-column label="时间" width="140">
        <template #default="{ row }">{{ formatDateTime(row.sale_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button text type="primary" @click="router.push(`/sales/${row.sale_id}`)">查看</el-button>
            <el-button v-if="canWrite()" text type="danger" @click="onDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </CrudTable>
  </div>
</template>

<style scoped>
.sale-id {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.payment-tag :deep(.el-tag__content) {
  overflow: visible;
  text-overflow: clip;
}
</style>
