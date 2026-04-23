<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import ProductFormDrawer from './ProductFormDrawer.vue'
import BookFormDrawer from '../book/BookFormDrawer.vue'
import { deleteProduct, listProducts, type ProductQuery } from '@/api/products'
import { deleteBook } from '@/api/books'
import type { Product, ProductStatus } from '@/api/types'
import { formatCurrency, statusLabel } from '@/utils/format'
import { useDictsStore } from '@/stores/dicts'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'
const dicts = useDictsStore()

const rows = ref<Product[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive<ProductQuery>({ search: '', category_id: undefined, status: undefined })

async function fetchList() {
  loading.value = true
  try {
    const data = await listProducts({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      category_id: filters.category_id ?? undefined,
      status: filters.status ?? undefined,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

// drawer control
const productDrawer = ref(false)
const bookDrawer = ref(false)
const editingId = ref<number | null>(null)

function openCreateProduct() {
  editingId.value = null
  productDrawer.value = true
}
function openCreateBook() {
  editingId.value = null
  bookDrawer.value = true
}
function openEdit(row: Product) {
  editingId.value = row.product_id
  if (row.is_book) bookDrawer.value = true
  else productDrawer.value = true
}

async function onDelete(row: Product) {
  try {
    await ElMessageBox.confirm(
      row.is_book
        ? `删除图书「${row.product_name}」？若存在销售记录将返回冲突。`
        : `删除商品「${row.product_name}」？若存在销售记录将返回冲突。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    if (row.is_book) await deleteBook(row.product_id)
    else await deleteProduct(row.product_id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 */
  }
}

const statusTagType = (s: ProductStatus) =>
  s === 'onsale' ? 'success' : s === 'offsale' ? 'info' : 'danger'

onMounted(() => {
  dicts.ensureCategories()
  fetchList()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="商品管理" subtitle="管理全部商品，图书类商品用图书抽屉编辑">
      <template #extra>
        <el-dropdown v-if="canWrite()" trigger="click">
          <el-button type="primary">
            <el-icon><Plus /></el-icon>新增商品<el-icon style="margin-left: 4px"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="openCreateProduct">
                <el-icon><Goods /></el-icon>普通商品
              </el-dropdown-item>
              <el-dropdown-item @click="openCreateBook">
                <el-icon><Reading /></el-icon>图书商品
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
    </PageHeader>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="() => { filters.search=''; filters.category_id=undefined; filters.status=undefined; page=1; fetchList() }"
    >
      <el-form-item label="名称">
        <el-input v-model="filters.search" placeholder="按名称搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="filters.category_id" placeholder="全部" clearable style="width: 200px" filterable>
          <el-option
            v-for="c in dicts.categories"
            :key="c.category_id"
            :label="c.parent_category_name ? `${c.parent_category_name} / ${c.category_name}` : c.category_name"
            :value="c.category_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" placeholder="全部" clearable style="width: 140px">
          <el-option label="在售" value="onsale" />
          <el-option label="下架" value="offsale" />
          <el-option label="停产" value="discontinued" />
        </el-select>
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="product_id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="product_id" label="#" width="70" />
      <el-table-column label="名称" min-width="220">
        <template #default="{ row }">
          <div class="product-name">
            <el-tag v-if="row.is_book" type="primary" size="small" effect="light" round>图书</el-tag>
            <span>{{ row.product_name }}</span>
          </div>
          <div class="text-muted" style="font-size: 12px">{{ row.barcode || '无条码' }}</div>
        </template>
      </el-table-column>
      <el-table-column prop="category_name" label="分类" width="140" />
      <el-table-column label="售价" width="130" align="right">
        <template #default="{ row }"><span class="money">{{ formatCurrency(row.unit_price) }}</span></template>
      </el-table-column>
      <el-table-column label="成本" width="130" align="right">
        <template #default="{ row }"><span class="money text-muted">{{ formatCurrency(row.cost_price) }}</span></template>
      </el-table-column>
      <el-table-column label="库存" width="100" align="right">
        <template #default="{ row }">
          <el-tag v-if="row.stock_qty === 0" type="danger" size="small">缺货</el-tag>
          <el-tag v-else-if="row.stock_qty < 10" type="warning" size="small">低</el-tag>
          <span v-else class="money">{{ row.stock_qty }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="unit" label="单位" width="70" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button v-if="canWrite()" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="canWrite()" text type="danger" @click="onDelete(row)">删除</el-button>
            <span v-if="!canWrite()" class="text-muted">—</span>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <ProductFormDrawer
      v-model="productDrawer"
      :product-id="editingId"
      @success="fetchList"
    />
    <BookFormDrawer
      v-model="bookDrawer"
      :product-id="editingId"
      @success="fetchList"
    />
  </div>
</template>

<style scoped>
.product-name {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  font-weight: 500;
}
</style>
