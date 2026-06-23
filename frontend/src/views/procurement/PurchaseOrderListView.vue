<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { listProducts } from '@/api/products'
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
  quantity: number
  purchase_price: number
}

const auth = useAuthStore()
const dicts = useDictsStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'

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

async function openCreate() {
  dialogMode.value = 'create'
  editingId.value = null
  await Promise.all([dicts.ensureStores(), dicts.ensureSuppliers(), searchProducts()])
  resetForm()
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
      quantity: item.quantity,
      purchase_price: Number(item.purchase_price),
    })),
  })
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

onMounted(() => {
  dicts.ensureStores()
  dicts.ensureSuppliers()
  searchProducts()
  fetchList()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="采购单" subtitle="记录向供应商采购商品的下单过程，入库单可基于采购单生成">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增采购单
        </el-button>
      </template>
    </PageHeader>

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
      <el-table-column label="操作" width="150" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
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
