<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import {
  createSupplier,
  deleteSupplier,
  listSuppliers,
  updateSupplier,
  type SupplierQuery,
} from '@/api/suppliers'
import type { ActiveStatus, Supplier } from '@/api/types'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'

const rows = ref<Supplier[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filters = reactive<SupplierQuery>({ search: '', status: undefined })

async function fetchList() {
  loading.value = true
  try {
    const data = await listSuppliers({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      status: filters.status || undefined,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const form = reactive<Partial<Supplier>>({
  supplier_name: '',
  contact_name: '',
  phone: '',
  email: '',
  status: 'active' as ActiveStatus,
})

const rules: FormRules = {
  supplier_name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, {
    supplier_id: undefined,
    supplier_name: '',
    contact_name: '',
    phone: '',
    email: '',
    status: 'active',
  })
  dialogVisible.value = true
}

function openEdit(row: Supplier) {
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
    const payload: Partial<Supplier> = {
      supplier_name: form.supplier_name,
      contact_name: form.contact_name || null,
      phone: form.phone || null,
      email: form.email || null,
      status: form.status,
    }
    if (dialogMode.value === 'create') {
      await createSupplier(payload)
      ElMessage.success('供应商新增成功')
    } else if (form.supplier_id) {
      await updateSupplier(form.supplier_id, payload)
      ElMessage.success('供应商已更新')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: Supplier) {
  try {
    await ElMessageBox.confirm(`确定删除供应商「${row.supplier_name}」？若存在关联商品将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteSupplier(row.supplier_id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 由 http 层弹窗 */
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="供应商管理" subtitle="管理合作供应商及供货关系">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增供应商
        </el-button>
      </template>
    </PageHeader>

    <FilterBar :loading="loading" @submit="() => { page = 1; fetchList() }" @reset="() => { filters.search=''; filters.status=undefined; page=1; fetchList() }">
      <el-form-item label="名称">
        <el-input v-model="filters.search" placeholder="按供应商名称搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" placeholder="全部" clearable style="width: 120px">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="supplier_id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="supplier_id" label="#" width="70" />
      <el-table-column prop="supplier_name" label="供应商名称" min-width="180" />
      <el-table-column prop="contact_name" label="联系人" width="120" />
      <el-table-column prop="phone" label="电话" width="160" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
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

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增供应商' : '编辑供应商'" width="520" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="supplier_name">
          <el-input v-model="form.supplier_name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact_name" placeholder="选填" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="选填" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="选填" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
