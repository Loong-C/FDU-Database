<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { createStore, deleteStore, listStores, updateStore, type StoreQuery } from '@/api/stores'
import type { Store } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'

const rows = ref<Store[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive<StoreQuery>({ search: '', city: '' })

async function fetchList() {
  loading.value = true
  try {
    const data = await listStores({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      city: filters.city || undefined,
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
  filters.search = ''
  filters.city = ''
  onSearch()
}

// Dialog
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const form = reactive<Partial<Store>>({
  store_name: '',
  city: '',
  address: '',
  phone: '',
  manager_name: '',
})

const rules: FormRules = {
  store_name: [{ required: true, message: '请输入门店名称', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  address: [{ required: true, message: '请输入地址', trigger: 'blur' }],
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, { store_id: undefined, store_name: '', city: '', address: '', phone: '', manager_name: '' })
  dialogVisible.value = true
}

function openEdit(row: Store) {
  dialogMode.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: Partial<Store> = {
      store_name: form.store_name,
      city: form.city,
      address: form.address,
      phone: form.phone || null,
      manager_name: form.manager_name || null,
    }
    if (dialogMode.value === 'create') {
      await createStore(payload)
      ElMessage.success('门店新增成功')
    } else if (form.store_id) {
      await updateStore(form.store_id, payload)
      ElMessage.success('门店更新成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) {
      applyServerErrors(formRef.value, error)
    }
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: Store) {
  try {
    await ElMessageBox.confirm(`确定删除门店「${row.store_name}」？若存在关联销售记录将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteStore(row.store_id)
    ElMessage.success('门店已删除')
    fetchList()
  } catch {
    /* 409 由 http 层弹窗 */
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="门店管理" subtitle="维护全国门店基础信息，供销售开单与报表分析使用">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增门店
        </el-button>
      </template>
    </PageHeader>

    <FilterBar :loading="loading" @submit="onSearch" @reset="onReset">
      <el-form-item label="名称">
        <el-input v-model="filters.search" placeholder="按门店名称搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="城市">
        <el-input v-model="filters.city" placeholder="按城市筛选" clearable style="width: 160px" />
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="store_id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="store_id" label="#" width="70" />
      <el-table-column prop="store_name" label="门店名称" min-width="160" />
      <el-table-column prop="city" label="城市" width="120" />
      <el-table-column prop="address" label="地址" min-width="220" show-overflow-tooltip />
      <el-table-column prop="manager_name" label="店长" width="120" />
      <el-table-column prop="phone" label="电话" width="160" />
      <el-table-column label="创建时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="170" fixed="right" align="right">
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
      :title="dialogMode === 'create' ? '新增门店' : '编辑门店'"
      width="520"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="门店名称" prop="store_name">
          <el-input v-model="form.store_name" placeholder="例如：北京朝阳店" />
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input v-model="form.city" placeholder="例如：北京" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input v-model="form.address" type="textarea" :rows="2" placeholder="详细地址" />
        </el-form-item>
        <el-form-item label="店长">
          <el-input v-model="form.manager_name" placeholder="选填" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
