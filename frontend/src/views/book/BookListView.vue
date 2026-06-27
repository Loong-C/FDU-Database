<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import CatalogTabs from '@/components/common/CatalogTabs.vue'
import BookFormDrawer from './BookFormDrawer.vue'
import { deleteBook, listBooks, type BookQuery } from '@/api/books'
import type { Book, ProductStatus } from '@/api/types'
import { formatCurrency, formatDate, statusLabel } from '@/utils/format'
import { categoryDescendants, categoryOptionLabel } from '@/utils/categories'
import { useDictsStore } from '@/stores/dicts'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'
const dicts = useDictsStore()

const rows = ref<Book[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<BookQuery>({ search: '', publisher_id: undefined, category_id: undefined })
const bookCategories = computed(() => categoryDescendants(dicts.categories, '图书'))

async function fetchList() {
  loading.value = true
  try {
    const data = await listBooks({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      publisher_id: filters.publisher_id ?? undefined,
      category_id: filters.category_id ?? undefined,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const drawer = ref(false)
const editingId = ref<number | null>(null)

function openCreate() {
  editingId.value = null
  drawer.value = true
}
function openEdit(row: Book) {
  editingId.value = row.product_id
  drawer.value = true
}

async function onDelete(row: Book) {
  try {
    await ElMessageBox.confirm(`删除图书「${row.product_name}」？若存在销售记录将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteBook(row.product_id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 */
  }
}

const statusTagType = (s: ProductStatus) =>
  s === 'onsale' ? 'success' : s === 'offsale' ? 'info' : 'danger'

function warningStoreCount(row: Book) {
  return row.inventory?.filter((item) => item.stock_qty <= item.safety_stock_qty).length ?? 0
}

onMounted(() => {
  dicts.ensurePublishers()
  dicts.ensureCategories()
  fetchList()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="商品中心" subtitle="图书档案维护：ISBN、出版社、作者、译者与门店库存">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增图书
        </el-button>
      </template>
    </PageHeader>

    <CatalogTabs />

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="() => { filters.search=''; filters.publisher_id=undefined; filters.category_id=undefined; page=1; fetchList() }"
    >
      <el-form-item label="名称">
        <el-input v-model="filters.search" placeholder="按图书名称/ISBN" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="出版社">
        <el-select v-model="filters.publisher_id" placeholder="全部" clearable filterable style="width: 200px">
          <el-option
            v-for="p in dicts.publishers"
            :key="p.publisher_id"
            :label="p.publisher_name"
            :value="p.publisher_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="分类">
        <el-select v-model="filters.category_id" placeholder="全部" clearable filterable style="width: 200px">
          <el-option
            v-for="c in bookCategories"
            :key="c.category_id"
            :label="categoryOptionLabel(c, dicts.categories, '图书')"
            :value="c.category_id"
          />
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
      <el-table-column label="书名" min-width="240">
        <template #default="{ row }">
          <div class="book-title">{{ row.product_name }}</div>
          <div class="text-muted" style="font-size: 12px">ISBN {{ row.isbn }}</div>
        </template>
      </el-table-column>
      <el-table-column label="作者" min-width="180">
        <template #default="{ row }">
          <span v-if="row.authors?.length" class="person-tags">
          <el-tag
            v-for="a in row.authors"
            :key="a.author_id"
            size="small"
            effect="plain"
            class="person-tag"
          >
            {{ a.author_name }}
          </el-tag>
          </span>
          <span v-if="!row.authors?.length" class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="译者" min-width="140">
        <template #default="{ row }">
          <span v-if="row.translators?.length" class="person-tags">
            <el-tag
              v-for="t in row.translators"
              :key="t.translator_id"
              size="small"
              type="info"
              effect="plain"
              class="person-tag person-tag--muted"
            >
              {{ t.translator_name }}
            </el-tag>
          </span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="publisher_name" label="出版社" min-width="140" />
      <el-table-column label="出版日期" width="120">
        <template #default="{ row }">{{ formatDate(row.publish_date) }}</template>
      </el-table-column>
      <el-table-column label="售价" width="110" align="right">
        <template #default="{ row }"><span class="money">{{ formatCurrency(row.unit_price) }}</span></template>
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

    <BookFormDrawer v-model="drawer" :product-id="editingId" @success="fetchList" />
  </div>
</template>

<style scoped>
.book-title {
  font-weight: 500;
}

.person-tags {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
}

.person-tag {
  max-width: 132px;
}

.person-tag :deep(.el-tag__content) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.person-tag--muted {
  --el-tag-text-color: var(--app-text-muted);
}

.stock-summary {
  display: inline-flex;
  justify-content: flex-end;
  align-items: center;
  gap: 6px;
}
</style>
