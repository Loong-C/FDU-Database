<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import { createTranslator, deleteTranslator, listTranslators, updateTranslator } from '@/api/translators'
import type { Translator } from '@/api/types'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin'

const rows = ref<Translator[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive({ search: '' })

async function fetchList() {
  loading.value = true
  try {
    const data = await listTranslators({
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
const form = reactive<Partial<Translator>>({ translator_name: '', country: '' })
const rules: FormRules = {
  translator_name: [{ required: true, message: '请输入译者姓名', trigger: 'blur' }],
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, { translator_id: undefined, translator_name: '', country: '' })
  dialogVisible.value = true
}
function openEdit(row: Translator) {
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
    const payload = { translator_name: form.translator_name, country: form.country || null }
    if (dialogMode.value === 'create') {
      await createTranslator(payload)
      ElMessage.success('译者新增成功')
    } else if (form.translator_id) {
      await updateTranslator(form.translator_id, payload)
      ElMessage.success('译者已更新')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: Translator) {
  try {
    await ElMessageBox.confirm(`确定删除译者「${row.translator_name}」？若存在关联图书将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteTranslator(row.translator_id)
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
    <PageHeader title="译者管理" subtitle="图书译者信息">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增译者
        </el-button>
      </template>
    </PageHeader>

    <FilterBar :loading="loading" @submit="() => { page = 1; fetchList() }" @reset="() => { filters.search=''; page=1; fetchList() }">
      <el-form-item label="姓名">
        <el-input v-model="filters.search" placeholder="按姓名搜索" clearable style="width: 240px" />
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="translator_id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="translator_id" label="#" width="70" />
      <el-table-column prop="translator_name" label="姓名" min-width="180" />
      <el-table-column prop="country" label="国家" min-width="140" />
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

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增译者' : '编辑译者'" width="440" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="姓名" prop="translator_name"><el-input v-model="form.translator_name" /></el-form-item>
        <el-form-item label="国家"><el-input v-model="form.country" placeholder="选填" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
