<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import ProductFormDrawer from './ProductFormDrawer.vue'
import BookFormDrawer from '@/views/book/BookFormDrawer.vue'
import { deleteProduct, listProducts, type ProductQuery } from '@/api/products'
import { deleteBook } from '@/api/books'
import type { Product, ProductStatus } from '@/api/types'
import { formatCurrency, statusLabel } from '@/utils/format'
import { categoryFullOptionLabel, displayCategoryName } from '@/utils/categories'
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
const productCategories = computed(() => {
  const officeRoot = dicts.categories.find((category) => category.category_name === '办公文具')
  if (!officeRoot) {
    return []
  }
  const allowed = new Set<number>([officeRoot.category_id])
  let changed = true
  while (changed) {
    changed = false
    for (const category of dicts.categories) {
      if (category.parent_category_id && allowed.has(category.parent_category_id) && !allowed.has(category.category_id)) {
        allowed.add(category.category_id)
        changed = true
      }
    }
  }
  return dicts.categories.filter((category) => allowed.has(category.category_id))
})

async function fetchList() {
  loading.value = true
  try {
    const data = await listProducts({
      page: page.value,
      page_size: pageSize.value,
      is_book: false,
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
function openEdit(row: Product) {
  editingId.value = row.product_id
  if (row.is_book) {
    bookDrawer.value = true
    return
  }
  productDrawer.value = true
}

async function onDelete(row: Product) {
  try {
    await ElMessageBox.confirm(
      `删除商品「${row.product_name}」？若存在销售记录将返回冲突。`,
      '删除确认',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  try {
    if (row.is_book) {
      await deleteBook(row.product_id)
    } else {
      await deleteProduct(row.product_id)
    }
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 */
  }
}

const statusTagType = (s: ProductStatus) =>
  s === 'onsale' ? 'success' : s === 'offsale' ? 'info' : 'danger'

function warningStoreCount(row: Product) {
  return row.inventory?.filter((item) => item.stock_qty <= item.safety_stock_qty).length ?? 0
}

onMounted(() => {
  dicts.ensureCategories()
  fetchList()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="得力办公文具专区" subtitle="品牌专柜商品、独家供货关系与门店库存">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreateProduct">
          <el-icon><Plus /></el-icon>新增商品
        </el-button>
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
            v-for="c in productCategories"
            :key="c.category_id"
            :label="categoryFullOptionLabel(c, dicts.categories)"
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
            <span>{{ row.product_name }}</span>
          </div>
          <div class="text-muted" style="font-size: 12px">{{ row.barcode || '无条码' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.is_book ? 'danger' : 'info'" size="small" effect="plain">
            {{ row.is_book ? '图书' : '得力文具' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="分类" width="150">
        <template #default="{ row }">{{ displayCategoryName(row.category_name) }}</template>
      </el-table-column>
      <el-table-column label="售价" width="130" align="right">
        <template #default="{ row }"><span class="money">{{ formatCurrency(row.unit_price) }}</span></template>
      </el-table-column>
      <el-table-column label="成本" width="130" align="right">
        <template #default="{ row }"><span class="money text-muted">{{ formatCurrency(row.cost_price) }}</span></template>
      </el-table-column>
      <el-table-column label="库存" width="130" align="right">
        <template #default="{ row }">
          <div class="stock-summary">
            <span class="money">{{ row.stock_qty }}</span>
            <el-tag v-if="row.stock_qty === 0" type="danger" size="small">缺货</el-tag>
            <el-tag v-else-if="warningStoreCount(row)" type="warning" size="small">
              {{ warningStoreCount(row) }} 店预警
            </el-tag>
          </div>
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

.stock-summary {
  display: inline-flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
}
</style>
