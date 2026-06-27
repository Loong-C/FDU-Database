<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { listInventory, updateInventory, type InventoryQuery } from '@/api/inventory'
import { listProducts } from '@/api/products'
import type { InventoryRow, Product, ProductStatus } from '@/api/types'
import { formatDateTime, statusLabel } from '@/utils/format'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'
import { useDictsStore } from '@/stores/dicts'

const auth = useAuthStore()
const dicts = useDictsStore()
const canWrite = () => auth.role === 'admin'
const canProcure = () => auth.role === 'admin' || auth.role === 'operator'
const route = useRoute()
const router = useRouter()

const rows = ref<InventoryRow[]>([])
const tableRows = computed(() =>
  rows.value.map((row) => ({
    ...row,
    inventory_key: `${row.store_id}-${row.product_id}`,
  })),
)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const productOptions = ref<Product[]>([])
const productLoading = ref(false)

const filters = reactive<InventoryQuery>({
  store_id: undefined,
  product_id: undefined,
  warning: false,
})

async function fetchList() {
  loading.value = true
  try {
    const data = await listInventory({
      page: page.value,
      page_size: pageSize.value,
      store_id: filters.store_id,
      product_id: filters.product_id,
      warning: filters.warning || undefined,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  fetchList()
}

function onReset() {
  filters.store_id = undefined
  filters.product_id = undefined
  filters.warning = false
  onSearch()
}

async function searchProducts(query = '') {
  productLoading.value = true
  try {
    const data = await listProducts({ page: 1, page_size: 30, search: query || undefined })
    productOptions.value = data.items
  } finally {
    productLoading.value = false
  }
}

const dialogVisible = ref(false)
const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const editing = ref<InventoryRow | null>(null)
const form = reactive({
  stock_qty: 0,
  safety_stock_qty: 0,
})

const rules: FormRules = {
  stock_qty: [{ required: true, message: '请输入当前库存', trigger: 'blur' }],
  safety_stock_qty: [{ required: true, message: '请输入安全库存', trigger: 'blur' }],
}

function openEdit(row: InventoryRow) {
  editing.value = row
  form.stock_qty = row.stock_qty
  form.safety_stock_qty = row.safety_stock_qty
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value || !editing.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await updateInventory(editing.value.store_id, editing.value.product_id, {
      stock_qty: Number(form.stock_qty),
      safety_stock_qty: Number(form.safety_stock_qty),
    })
    ElMessage.success('库存已更新')
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

const statusTagType = (s: ProductStatus) =>
  s === 'onsale' ? 'success' : s === 'offsale' ? 'info' : 'danger'

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

onMounted(() => {
  filters.warning = route.query.warning === '1' || route.query.warning === 'true'
  dicts.ensureStores()
  searchProducts()
  fetchList()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="门店库存" subtitle="按门店和商品维护当前库存、安全库存，并查看低库存预警">
      <template #extra>
        <el-button @click="fetchList">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </template>
    </PageHeader>

    <FilterBar :loading="loading" @submit="onSearch" @reset="onReset">
      <el-form-item label="门店">
        <el-select v-model="filters.store_id" clearable placeholder="全部门店" style="width: 180px">
          <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
        </el-select>
      </el-form-item>
      <el-form-item label="商品">
        <el-select
          v-model="filters.product_id"
          clearable
          filterable
          remote
          reserve-keyword
          placeholder="搜索商品"
          :remote-method="searchProducts"
          :loading="productLoading"
          style="width: 240px"
        >
          <el-option
            v-for="p in productOptions"
            :key="p.product_id"
            :label="`${p.product_name} #${p.product_id}`"
            :value="p.product_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="预警">
        <el-switch v-model="filters.warning" active-text="仅看预警" />
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="tableRows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="inventory_key"
      empty-icon="Box"
      empty-title="暂无库存记录"
      empty-description="库存行由商品初始化或入库流程产生"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="store_name" label="门店" min-width="150" />
      <el-table-column label="商品" min-width="220">
        <template #default="{ row }">
          <div class="inventory-product">{{ row.product_name }}</div>
          <div class="text-muted" style="font-size: 12px">#{{ row.product_id }}</div>
        </template>
      </el-table-column>
      <el-table-column label="商品状态" width="110">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.product_status)" size="small">{{ statusLabel(row.product_status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="当前库存" width="120" align="right">
        <template #default="{ row }">
          <el-tag v-if="row.stock_qty <= row.safety_stock_qty" type="warning" size="small">
            {{ row.stock_qty }}
          </el-tag>
          <span v-else class="money">{{ row.stock_qty }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="safety_stock_qty" label="安全库存" width="120" align="right" />
      <el-table-column label="更新时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button v-if="canProcure()" text type="primary" @click="openReplenish(row)">补货采购</el-button>
            <el-button v-if="canWrite()" text type="primary" @click="openEdit(row)">调整</el-button>
            <span v-if="!canProcure() && !canWrite()" class="text-muted">—</span>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <el-dialog v-model="dialogVisible" title="调整库存" width="480" destroy-on-close>
      <div v-if="editing" class="edit-summary">
        <div>{{ editing.store_name }}</div>
        <strong>{{ editing.product_name }}</strong>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="当前库存" prop="stock_qty">
          <el-input-number v-model="form.stock_qty" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="安全库存" prop="safety_stock_qty">
          <el-input-number v-model="form.safety_stock_qty" :min="0" :step="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.inventory-product {
  font-weight: 500;
}

.edit-summary {
  padding: 10px 12px;
  margin-bottom: 12px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius);
  background: var(--app-surface-alt);
}
</style>
