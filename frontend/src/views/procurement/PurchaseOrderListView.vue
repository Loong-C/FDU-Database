<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { getProduct, listProducts } from '@/api/products'
import {
  createPurchaseOrder,
  deletePurchaseOrder,
  listPurchaseOrders,
  updatePurchaseOrder,
  type PurchaseOrderQuery,
  type PurchaseOrderWritePayload,
} from '@/api/procurement'
import type { Product, PurchaseOrder, PurchaseOrderStatus } from '@/api/types'
import { formatCurrency, formatDateTime, statusLabel } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'
import { useDictsStore } from '@/stores/dicts'

interface EditableLine {
  product_id: number | null
  product_name?: string
  quantity: number
  purchase_price: number
}

interface CreatePrefill {
  product_id?: number
  store_id?: number
  quantity?: number
}

const auth = useAuthStore()
const dicts = useDictsStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'
const route = useRoute()
const router = useRouter()

const rows = ref<PurchaseOrder[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const productOptions = ref<Product[]>([])
const productLoading = ref(false)

const filters = reactive<PurchaseOrderQuery>({
  supplier_id: undefined,
  store_id: undefined,
  status: undefined,
})

async function fetchList() {
  loading.value = true
  try {
    const data = await listPurchaseOrders({
      page: page.value,
      page_size: pageSize.value,
      supplier_id: filters.supplier_id,
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
  filters.supplier_id = undefined
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

function ensureProductOptionsFromItems(items: Array<{ product_id: number; product_name: string; purchase_price?: string }>) {
  items.forEach((item) => {
    if (productOptions.value.some((product) => product.product_id === item.product_id)) return
    productOptions.value.unshift({
      product_id: item.product_id,
      product_name: item.product_name,
      category_id: 0,
      category_name: '采购明细',
      unit: '件',
      unit_price: item.purchase_price || '0',
      cost_price: item.purchase_price || '0',
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

const dialogVisible = ref(false)
const submitting = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const form = reactive<{
  supplier_id: number | null
  store_id: number | null
  order_time: string
  status: PurchaseOrderStatus
  items: EditableLine[]
}>({
  supplier_id: null,
  store_id: null,
  order_time: dayjs().format('YYYY-MM-DDTHH:mm:ss'),
  status: 'draft',
  items: [],
})

const formTotal = computed(() =>
  form.items.reduce((sum, item) => sum + Number(item.quantity || 0) * Number(item.purchase_price || 0), 0),
)

function emptyLine(): EditableLine {
  return { product_id: null, quantity: 1, purchase_price: 0 }
}

function resetForm() {
  Object.assign(form, {
    supplier_id: null,
    store_id: dicts.stores[0]?.store_id ?? null,
    order_time: dayjs().format('YYYY-MM-DDTHH:mm:ss'),
    status: 'draft' as PurchaseOrderStatus,
    items: [emptyLine()],
  })
}

async function openCreate(prefill: CreatePrefill = {}) {
  dialogMode.value = 'create'
  editingId.value = null
  await Promise.all([dicts.ensureStores(), dicts.ensureSuppliers(), searchProducts()])
  resetForm()
  if (prefill.store_id) form.store_id = prefill.store_id
  if (prefill.product_id) {
    try {
      const product = await getProduct(prefill.product_id)
      if (!productOptions.value.some((item) => item.product_id === product.product_id)) {
        productOptions.value.unshift(product)
      }
      const primaryLink = product.supplier_links?.find((item) => item.is_primary) || product.supplier_links?.[0]
      if (primaryLink?.supplier_id) {
        form.supplier_id = primaryLink.supplier_id
      } else {
        ElMessage.info('该商品尚未配置供应商，请在采购单中手动选择供应商')
      }
      form.items = [{
        product_id: product.product_id,
        product_name: product.product_name,
        quantity: prefill.quantity || 1,
        purchase_price: Number(primaryLink?.supply_price || product.cost_price || product.unit_price || 0),
      }]
    } catch {
      ElMessage.warning('未能读取预警商品，请手动选择采购明细')
    }
  }
  dialogVisible.value = true
}

async function openEdit(row: PurchaseOrder) {
  dialogMode.value = 'edit'
  editingId.value = row.purchase_order_id
  await Promise.all([dicts.ensureStores(), dicts.ensureSuppliers(), searchProducts()])
  Object.assign(form, {
    supplier_id: row.supplier_id,
    store_id: row.store_id,
    order_time: dayjs(row.order_time).format('YYYY-MM-DDTHH:mm:ss'),
    status: row.status,
    items: row.items.map((item) => ({
      product_id: item.product_id,
      product_name: item.product_name,
      quantity: item.quantity,
      purchase_price: Number(item.purchase_price),
    })),
  })
  ensureProductOptionsFromItems(row.items)
  dialogVisible.value = true
}

function addLine() {
  form.items.push(emptyLine())
}

function removeLine(index: number) {
  form.items.splice(index, 1)
  if (!form.items.length) form.items.push(emptyLine())
}

function validateForm(): boolean {
  if (!form.supplier_id) {
    ElMessage.warning('请选择供应商')
    return false
  }
  if (!form.store_id) {
    ElMessage.warning('请选择门店')
    return false
  }
  if (!form.order_time) {
    ElMessage.warning('请选择下单时间')
    return false
  }
  const productIds = form.items.map((item) => item.product_id).filter(Boolean)
  if (!productIds.length) {
    ElMessage.warning('请至少添加一条采购明细')
    return false
  }
  if (productIds.length !== new Set(productIds).size) {
    ElMessage.warning('同一采购单中商品不能重复')
    return false
  }
  const invalid = form.items.some((item) => !item.product_id || item.quantity <= 0 || item.purchase_price <= 0)
  if (invalid) {
    ElMessage.warning('请填写完整的商品、数量和采购价')
    return false
  }
  return true
}

async function onSubmit() {
  if (!validateForm()) return
  const payload: PurchaseOrderWritePayload = {
    supplier_id: form.supplier_id as number,
    store_id: form.store_id as number,
    order_time: dayjs(form.order_time).toISOString(),
    status: form.status,
    items: form.items.map((item) => ({
      product_id: item.product_id as number,
      quantity: Number(item.quantity),
      purchase_price: Number(item.purchase_price),
    })),
  }
  submitting.value = true
  try {
    if (dialogMode.value === 'edit' && editingId.value) {
      await updatePurchaseOrder(editingId.value, payload)
      ElMessage.success('采购单已更新')
    } else {
      await createPurchaseOrder(payload)
      ElMessage.success('采购单已创建')
    }
    dialogVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: PurchaseOrder) {
  try {
    await ElMessageBox.confirm(`确定删除采购单 #${row.purchase_order_id}？已生成入库单时将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deletePurchaseOrder(row.purchase_order_id)
    ElMessage.success('采购单已删除')
    fetchList()
  } catch {
    /* 409/422 由 http 层提示 */
  }
}

const statusTagType = (status: PurchaseOrderStatus) => {
  if (status === 'approved' || status === 'received') return 'success'
  if (status === 'submitted') return 'warning'
  if (status === 'cancelled') return 'info'
  return ''
}

const purchaseFlow: PurchaseOrderStatus[] = ['draft', 'submitted', 'approved', 'received']

function stepClass(rowStatus: PurchaseOrderStatus, step: PurchaseOrderStatus) {
  if (rowStatus === 'cancelled') return ''
  const current = purchaseFlow.indexOf(rowStatus)
  const target = purchaseFlow.indexOf(step)
  return target < current ? 'is-done' : target === current ? 'is-current' : ''
}

function nextPurchaseStatus(status: PurchaseOrderStatus): { label: string; value: PurchaseOrderStatus } | null {
  if (status === 'draft') return { label: '提交', value: 'submitted' }
  if (status === 'submitted') return { label: '审核', value: 'approved' }
  if (status === 'approved') return { label: '标记收货', value: 'received' }
  return null
}

async function advancePurchaseOrder(row: PurchaseOrder) {
  const next = nextPurchaseStatus(row.status)
  if (!next) return
  await updatePurchaseOrder(row.purchase_order_id, { status: next.value })
  ElMessage.success(`采购单 #${row.purchase_order_id} 已${next.label}`)
  fetchList()
}

function createStockInFromOrder(row: PurchaseOrder) {
  router.push({
    path: '/stock-ins',
    query: { purchase_order_id: String(row.purchase_order_id) },
  })
}

onMounted(async () => {
  await Promise.all([dicts.ensureStores(), dicts.ensureSuppliers(), searchProducts()])
  await fetchList()
  const productId = Number(route.query.replenish_product_id || 0)
  if (productId) {
    await openCreate({
      product_id: productId,
      store_id: Number(route.query.store_id || 0) || undefined,
      quantity: Number(route.query.qty || 1) || 1,
    })
  }
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="采购单" subtitle="记录向供应商采购商品的下单过程，入库单可基于采购单生成">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate()">
          <el-icon><Plus /></el-icon>新增采购单
        </el-button>
      </template>
    </PageHeader>

    <section class="process-rail">
      <article class="process-rail__step">
        <div class="process-rail__number">01</div>
        <div class="process-rail__title">草稿</div>
        <div class="process-rail__body">选择供应商、门店与采购明细。</div>
      </article>
      <article class="process-rail__step">
        <div class="process-rail__number">02</div>
        <div class="process-rail__title">提交审核</div>
        <div class="process-rail__body">确认采购需求，进入审核状态。</div>
      </article>
      <article class="process-rail__step">
        <div class="process-rail__number">03</div>
        <div class="process-rail__title">生成入库</div>
        <div class="process-rail__body">采购通过后，按到货情况生成入库单。</div>
      </article>
      <article class="process-rail__step">
        <div class="process-rail__number">04</div>
        <div class="process-rail__title">库存恢复</div>
        <div class="process-rail__body">入库审核通过后增加门店库存。</div>
      </article>
    </section>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="onReset"
    >
      <el-form-item label="供应商">
        <el-select v-model="filters.supplier_id" clearable filterable placeholder="全部" style="width: 190px">
          <el-option
            v-for="s in dicts.suppliers"
            :key="s.supplier_id"
            :label="s.supplier_name"
            :value="s.supplier_id"
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
          <el-option label="草稿" value="draft" />
          <el-option label="已提交" value="submitted" />
          <el-option label="已审核" value="approved" />
          <el-option label="已收货" value="received" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="purchase_order_id"
      empty-icon="Tickets"
      empty-title="暂无采购单"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="purchase_order_id" label="#" width="80" />
      <el-table-column prop="supplier_name" label="供应商" min-width="170" />
      <el-table-column prop="store_name" label="门店" min-width="140" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="流程" width="150">
        <template #default="{ row }">
          <span class="status-stepper" :title="statusLabel(row.status)">
            <span
              v-for="step in purchaseFlow"
              :key="step"
              class="status-stepper__dot"
              :class="stepClass(row.status, step)"
            />
          </span>
        </template>
      </el-table-column>
      <el-table-column label="明细" width="90" align="right">
        <template #default="{ row }">{{ row.items?.length ?? 0 }} 项</template>
      </el-table-column>
      <el-table-column label="总额" width="130" align="right">
        <template #default="{ row }"><span class="money">{{ formatCurrency(row.total_amount) }}</span></template>
      </el-table-column>
      <el-table-column label="创建人" width="120" prop="created_by_name" />
      <el-table-column label="下单时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.order_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="260" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button
              v-if="canWrite() && nextPurchaseStatus(row.status)"
              text
              type="primary"
              @click="advancePurchaseOrder(row)"
            >
              {{ nextPurchaseStatus(row.status)?.label }}
            </el-button>
            <el-button
              v-if="canWrite() && row.status === 'approved'"
              text
              type="primary"
              @click="createStockInFromOrder(row)"
            >
              生成入库
            </el-button>
            <el-button v-if="canWrite()" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="canWrite()" text type="danger" @click="onDelete(row)">删除</el-button>
            <span v-if="!canWrite()" class="text-muted">—</span>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增采购单' : `编辑采购单 #${editingId}`"
      width="860"
      destroy-on-close
    >
      <el-form label-width="90px">
        <div class="form-grid">
          <el-form-item label="供应商" required>
            <el-select v-model="form.supplier_id" filterable placeholder="请选择供应商" style="width: 100%">
              <el-option
                v-for="s in dicts.suppliers"
                :key="s.supplier_id"
                :label="s.supplier_name"
                :value="s.supplier_id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="门店" required>
            <el-select v-model="form.store_id" placeholder="请选择门店" style="width: 100%">
              <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
            </el-select>
          </el-form-item>
          <el-form-item label="下单时间" required>
            <el-date-picker
              v-model="form.order_time"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" style="width: 100%">
              <el-option label="草稿" value="draft" />
              <el-option label="已提交" value="submitted" />
              <el-option label="已审核" value="approved" />
              <el-option label="已收货" value="received" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
        </div>

        <div class="line-toolbar">
          <span class="section-title"><el-icon><Goods /></el-icon>采购明细</span>
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
          <el-table-column label="采购价" width="150" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.purchase_price" :min="0.01" :precision="2" :step="1" style="width: 100%" />
            </template>
          </el-table-column>
          <el-table-column label="行金额" width="130" align="right">
            <template #default="{ row }">
              <span class="money">{{ formatCurrency(Number(row.quantity || 0) * Number(row.purchase_price || 0)) }}</span>
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
