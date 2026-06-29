<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { createPublisher, deletePublisher, listPublishers, updatePublisher } from '@/api/publishers'
import type { Publisher } from '@/api/types'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'

const rows = ref<Publisher[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ search: '' })

async function fetchList() {
  loading.value = true
  try {
    const data = await listPublishers({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
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
const form = reactive<Partial<Publisher>>({
  publisher_name: '',
  contact_name: '',
  phone: '',
  email: '',
  address: '',
  country: '',
  website: '',
})

const rules: FormRules = {
  publisher_name: [{ required: true, message: '请输入出版社名称', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, {
    publisher_id: undefined,
    publisher_name: '',
    contact_name: '',
    phone: '',
    email: '',
    address: '',
    country: '',
    website: '',
  })
  dialogVisible.value = true
}

function openEdit(row: Publisher) {
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
    const payload: Partial<Publisher> = {
      publisher_name: form.publisher_name,
      contact_name: form.contact_name || null,
      phone: form.phone || null,
      email: form.email || null,
      address: form.address || null,
      country: form.country || null,
      website: form.website || null,
    }
    if (dialogMode.value === 'create') {
      await createPublisher(payload)
      ElMessage.success('出版社新增成功')
    } else if (form.publisher_id) {
      await updatePublisher(form.publisher_id, payload)
      ElMessage.success('出版社已更新')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: Publisher) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.publisher_name}」？若存在关联图书将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deletePublisher(row.publisher_id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 */
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="出版社管理">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增出版社
        </el-button>
      </template>
    </PageHeader>

    <FilterBar :loading="loading" @submit="() => { page = 1; fetchList() }" @reset="() => { filters.search=''; page=1; fetchList() }">
      <el-form-item label="名称">
        <el-input v-model="filters.search" placeholder="按名称搜索" clearable style="width: 240px" />
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="publisher_id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="publisher_id" label="#" width="70" />
      <el-table-column prop="publisher_name" label="名称" min-width="200" />
      <el-table-column prop="contact_name" label="联系人" width="120" />
      <el-table-column prop="phone" label="电话" width="140" />
      <el-table-column prop="country" label="国家" width="100" />
      <el-table-column prop="website" label="网址" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <a v-if="row.website" :href="row.website" target="_blank" rel="noopener">{{ row.website }}</a>
          <span v-else class="text-muted">-</span>
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

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增出版社' : '编辑出版社'" width="560" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="publisher_name">
          <el-input v-model="form.publisher_name" />
        </el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.contact_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="国家"><el-input v-model="form.country" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="网址"><el-input v-model="form.website" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
