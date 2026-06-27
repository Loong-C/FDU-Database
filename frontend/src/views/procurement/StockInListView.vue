<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { listProducts } from '@/api/products'
import {
  createStockIn,
  deleteStockIn,
  listPurchaseOrders,
  listStockIns,
  updateStockIn,
  type StockInQuery,
  type StockInWritePayload,
} from '@/api/procurement'
import type { Product, PurchaseOrder, StockIn, StockInStatus } from '@/api/types'
import { formatCurrency, formatDateTime, statusLabel } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'
import { useDictsStore } from '@/stores/dicts'

interface EditableLine {
  product_id: number | null
  product_name?: string
  quantity: number
  unit_cost: number
}

const auth = useAuthStore()
const dicts = useDictsStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'
const route = useRoute()

const rows = ref<StockIn[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const productOptions = ref<Product[]>([])
const purchaseOrderOptions = ref<PurchaseOrder[]>([])
const productLoading = ref(false)
const purchaseOrderLoading = ref(false)

const filters = reactive<StockInQuery>({
  purchase_order_id: undefined,
  store_id: undefined,
  status: undefined,
})

async function fetchList() {
  loading.value = true
  try {
    const data = await listStockIns({
      page: page.value,
      page_size: pageSize.value,
      purchase_order_id: filters.purchase_order_id,
      store_id: filters.store_id,
      status: filters.status,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function onReset() {
  filters.purchase_order_id = undefined
  filters.store_id = undefined
  filters.status = undefined
  page.value = 1
  fetchList()
}

async function searchProducts(query = '') {
  productLoading.value = true
  try {
    const data = await listProducts({ page: 1, page_size: 100, search: query || undefined })
    productOptions.value = data.items
  } finally {
    productLoading.value = false
  }
}

function ensureProductOptionsFromItems(items: Array<{ product_id: number; product_name: string; unit_cost?: string; purchase_price?: string }>) {
  items.forEach((item) => {
    if (productOptions.value.some((product) => product.product_id === item.product_id)) return
    productOptions.value.unshift({
      product_id: item.product_id,
      product_name: item.product_name,
      category_id: 0,
      category_name: '采购明细',
      unit: '件',
      unit_price: item.purchase_price || item.unit_cost || '0',
      cost_price: item.purchase_price || item.unit_cost || '0',
      stock_qty: 0,
      barcode: null,
      status: 'onsale',
      created_at: '',
      is_book: false,
      inventory: [],
      supplier_links: [],
    })
  })
}

async function loadPurchaseOrders() {
  purchaseOrderLoading.value = true
  try {
    const data = await listPurchaseOrders({ page: 1, page_size: 100 })
    purchaseOrderOptions.value = data.items
  } finally {
    purchaseOrderLoading.value = false
  }
}

const dialogVisible = ref(false)
const submitting = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const form = reactive<{
  purchase_order_id: number | null
  store_id: number | null
  inbound_time: string
  status: StockInStatus
  items: EditableLine[]
}>({
  purchase_order_id: null,
  store_id: null,
  inbound_time: dayjs().format('YYYY-MM-DDTHH:mm:ss'),
  status: 'pending',
  items: [],
})

const formTotal = computed(() =>
  form.items.reduce((sum, item) => sum + Number(item.quantity || 0) * Number(item.unit_cost || 0), 0),
)

function emptyLine(): EditableLine {
  return { product_id: null, quantity: 1, unit_cost: 0 }
}

function resetForm() {
  Object.assign(form, {
    purchase_order_id: null,
    store_id: dicts.stores[0]?.store_id ?? null,
    inbound_time: dayjs().format('YYYY-MM-DDTHH:mm:ss'),
    status: 'pending' as StockInStatus,
    items: [emptyLine()],
  })
}

async function openCreate(purchaseOrderId?: number) {
  dialogMode.value = 'create'
  editingId.value = null
  await Promise.all([dicts.ensureStores(), loadPurchaseOrders(), searchProducts()])
  resetForm()
  if (purchaseOrderId) {
    form.purchase_order_id = purchaseOrderId
    onPurchaseOrderChange(purchaseOrderId)
  }
  dialogVisible.value = true
}

async function openEdit(row: StockIn) {
  dialogMode.value = 'edit'
  editingId.value = row.stock_in_id
  await Promise.all([dicts.ensureStores(), loadPurchaseOrders(), searchProducts()])
  Object.assign(form, {
    purchase_order_id: row.purchase_order_id,
    store_id: row.store_id,
    inbound_time: dayjs(row.inbound_time).format('YYYY-MM-DDTHH:mm:ss'),
    status: row.status,
    items: row.items.map((item) => ({
      product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      unit_cost: Number(item.unit_cost),
    })),
  })
  ensureProductOptionsFromItems(row.items)
  dialogVisible.value = true
}

function onPurchaseOrderChange(id: number | string | null) {
  const numericId = id === null ? null : Number(id)
  const order = purchaseOrderOptions.value.find((item) => item.purchase_order_id === numericId)
  if (!order) return
  form.store_id = order.store_id
  ensureProductOptionsFromItems(order.items)
  form.items = order.items.map((item) => ({
    product_id: item.product_id,
    product_name: item.product_name,
    quantity: item.quantity,
    unit_cost: Number(item.purchase_price),
  }))
}

function addLine() {
  form.items.push(emptyLine())
}

function removeLine(index: number) {
  form.items.splice(index, 1)
  if (!form.items.length) form.items.push(emptyLine())
}

function validateForm(): boolean {
  if (!form.purchase_order_id) {
    ElMessage.warning('请选择采购单')
    return false
  }
  if (!form.store_id) {
    ElMessage.warning('请选择入库门店')
    return false
  }
  if (!form.inbound_time) {
    ElMessage.warning('请选择入库时间')
    return false
  }
  const productIds = form.items.map((item) => item.product_id).filter(Boolean)
  if (!productIds.length) {
    ElMessage.warning('请至少添加一条入库明细')
    return false
  }
  if (productIds.length !== new Set(productIds).size) {
    ElMessage.warning('同一入库单中商品不能重复')
    return false
  }
  const invalid = form.items.some((item) => !item.product_id || item.quantity <= 0 || item.unit_cost <= 0)
  if (invalid) {
    ElMessage.warning('请填写完整的商品、数量和入库成本')
    return false
  }
  return true
}

async function onSubmit() {
  if (!validateForm()) return
  const payload: StockInWritePayload = {
    purchase_order_id: form.purchase_order_id as number,
    store_id: form.store_id as number,
    inbound_time: dayjs(form.inbound_time).toISOString(),
    status: form.status,
    items: form.items.map((item) => ({
      product_id: item.product_id as number,
      quantity: Number(item.quantity),
      unit_cost: Number(item.unit_cost),
    })),
  }
  submitting.value = true
  try {
    if (dialogMode.value === 'edit' && editingId.value) {
      await updateStockIn(editingId.value, payload)
      ElMessage.success('入库单已更新')
    } else {
      await createStockIn(payload)
      ElMessage.success(form.status === 'approved' ? '入库单已审核，库存已增加' : '入库单已创建')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: StockIn) {
  try {
    await ElMessageBox.confirm(`确定删除入库单 #${row.stock_in_id}？已审核入库单将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteStockIn(row.stock_in_id)
    ElMessage.success('入库单已删除')
    fetchList()
  } catch {
    /* 409/422 由 http 层提示 */
  }
}

const statusTagType = (status: StockInStatus) => {
  if (status === 'approved') return 'success'
  if (status === 'rejected') return 'danger'
  return 'warning'
}

const stockFlow: StockInStatus[] = ['pending', 'approved']

function stockStepClass(rowStatus: StockInStatus, step: StockInStatus) {
  if (rowStatus === 'rejected') return ''
  const current = stockFlow.indexOf(rowStatus)
  const target = stockFlow.indexOf(step)
  return target < current ? 'is-done' : target === current ? 'is-current' : ''
}

async function approveStockIn(row: StockIn) {
  await updateStockIn(row.stock_in_id, { status: 'approved' })
  ElMessage.success(`入库单 #${row.stock_in_id} 已审核，库存已增加`)
  fetchList()
}

async function rejectStockIn(row: StockIn) {
  await updateStockIn(row.stock_in_id, { status: 'rejected' })
  ElMessage.success(`入库单 #${row.stock_in_id} 已驳回`)
  fetchList()
}

function stockInAmount(row: StockIn) {
  return row.items?.reduce((sum, item) => sum + Number(item.line_amount || 0), 0) || 0
}

onMounted(async () => {
  await Promise.all([dicts.ensureStores(), loadPurchaseOrders(), searchProducts()])
  await fetchList()
  const purchaseOrderId = Number(route.query.purchase_order_id || 0)
  if (purchaseOrderId) await openCreate(purchaseOrderId)
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="入库单" subtitle="记录采购到货验收；审核通过后自动增加对应门店库存">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate()">
          <el-icon><Plus /></el-icon>新增入库单
        </el-button>
      </template>
    </PageHeader>

    <section class="process-rail">
      <article class="process-rail__step">
        <div class="process-rail__number">01</div>
        <div class="process-rail__title">选择采购单</div>
        <div class="process-rail__body">从已审核采购单带入门店和明细。</div>
      </article>
      <article class="process-rail__step">
        <div class="process-rail__number">02</div>
        <div class="process-rail__title">到货验收</div>
        <div class="process-rail__body">核对实际入库数量和入库成本。</div>
      </article>
      <article class="process-rail__step">
        <div class="process-rail__number">03</div>
        <div class="process-rail__title">审核入库</div>
        <div class="process-rail__body">通过后服务端写入入库事实。</div>
      </article>
      <article class="process-rail__step">
        <div class="process-rail__number">04</div>
        <div class="process-rail__title">更新库存</div>
        <div class="process-rail__body">按门店和商品组合增加库存。</div>
      </article>
    </section>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="onReset"
    >
      <el-form-item label="采购单">
        <el-select v-model="filters.purchase_order_id" clearable filterable placeholder="全部" style="width: 170px">
          <el-option
            v-for="p in purchaseOrderOptions"
            :key="p.purchase_order_id"
            :label="`#${p.purchase_order_id} · ${p.supplier_name}`"
            :value="p.purchase_order_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="门店">
        <el-select v-model="filters.store_id" clearable placeholder="全部" style="width: 170px">
          <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" clearable placeholder="全部" style="width: 140px">
          <el-option label="待审核" value="pending" />
          <el-option label="已审核" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="stock_in_id"
      empty-icon="Box"
      empty-title="暂无入库单"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="stock_in_id" label="#" width="80" />
      <el-table-column label="采购单" width="100">
        <template #default="{ row }">#{{ row.purchase_order_id }}</template>
      </el-table-column>
      <el-table-column prop="store_name" label="门店" min-width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="流程" width="120">
        <template #default="{ row }">
          <span class="status-stepper" :title="statusLabel(row.status)">
            <span
              v-for="step in stockFlow"
              :key="step"
              class="status-stepper__dot"
              :class="stockStepClass(row.status, step)"
            />
          </span>
        </template>
      </el-table-column>
      <el-table-column label="明细" width="90" align="right">
        <template #default="{ row }">{{ row.items?.length ?? 0 }} 项</template>
      </el-table-column>
      <el-table-column label="入库金额" width="130" align="right">
        <template #default="{ row }">
          <span class="money">{{ formatCurrency(stockInAmount(row)) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="operator_name" label="操作人" width="120" />
      <el-table-column label="入库时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.inbound_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button v-if="canWrite() && row.status === 'pending'" text type="primary" @click="approveStockIn(row)">审核入库</el-button>
            <el-button v-if="canWrite() && row.status === 'pending'" text type="danger" @click="rejectStockIn(row)">驳回</el-button>
            <el-button v-if="canWrite() && row.status !== 'approved'" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="canWrite() && row.status !== 'approved'" text type="danger" @click="onDelete(row)">删除</el-button>
            <span v-if="!canWrite()" class="text-muted">—</span>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增入库单' : `编辑入库单 #${editingId}`"
      width="860"
      destroy-on-close
    >
      <el-alert
        v-if="form.status === 'approved'"
        type="warning"
        show-icon
        :closable="false"
        title="保存为已审核状态后，服务端会增加对应门店商品库存。"
        style="margin-bottom: 12px"
      />
      <el-form label-width="90px">
        <div class="form-grid">
          <el-form-item label="采购单" required>
            <el-select
              v-model="form.purchase_order_id"
              filterable
              placeholder="请选择采购单"
              :loading="purchaseOrderLoading"
              style="width: 100%"
              @change="onPurchaseOrderChange"
            >
              <el-option
                v-for="p in purchaseOrderOptions"
                :key="p.purchase_order_id"
                :label="`#${p.purchase_order_id} · ${p.supplier_name} · ${formatCurrency(p.total_amount)}`"
                :value="p.purchase_order_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="门店" required>
            <el-select v-model="form.store_id" placeholder="请选择门店" style="width: 100%">
              <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
            </el-select>
          </el-form-item>
          <el-form-item label="入库时间" required>
            <el-date-picker
              v-model="form.inbound_time"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option label="待审核" value="pending" />
              <el-option label="已审核" value="approved" />
              <el-option label="已驳回" value="rejected" />
            </el-select>
          </el-form-item>
        </div>

        <div class="line-toolbar">
          <span class="section-title"><el-icon><Box /></el-icon>入库明细</span>
          <el-button text type="primary" @click="addLine">
            <el-icon><Plus /></el-icon>添加商品
          </el-button>
        </div>

        <el-table :data="form.items" border size="small">
          <el-table-column label="商品" min-width="260">
            <template #default="{ row }">
              <el-select
                v-model="row.product_id"
                filterable
                remote
                reserve-keyword
                placeholder="搜索商品"
                :remote-method="searchProducts"
                :loading="productLoading"
                style="width: 100%"
              >
                <el-option
                  v-for="p in productOptions"
                  :key="p.product_id"
                  :label="`${p.product_name} #${p.product_id}`"
                  :value="p.product_id"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="130" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.quantity" :min="1" :step="1" controls-position="right" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="入库成本" width="150" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.unit_cost" :min="0.01" :precision="2" :step="1" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="行金额" width="130" align="right">
            <template #default="{ row }">
              <span class="money">{{ formatCurrency(Number(row.quantity || 0) * Number(row.unit_cost || 0)) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="right">
            <template #default="{ $index }">
              <el-button text type="danger" @click="removeLine($index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="form-total">
          客户端估算合计：<strong class="money">{{ formatCurrency(formTotal) }}</strong>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 12px;
}

.line-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 4px 0 10px;
}

.form-total {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 12px;
}

@media (max-width: 720px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
