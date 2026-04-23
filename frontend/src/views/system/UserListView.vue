<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import {
  createUser,
  deleteUser,
  listUsers,
  updateUser,
  type UserQuery,
  type UserWritePayload,
} from '@/api/users'
import type { Role, User } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'

const rows = ref<User[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<UserQuery>({ search: '', role: undefined })

async function fetchList() {
  loading.value = true
  try {
    const data = await listUsers({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      role: filters.role,
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
const form = reactive<UserWritePayload & { id?: number }>({
  id: undefined,
  username: '',
  password: '',
  email: '',
  display_name: '',
  role: 'operator',
  is_active: true,
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [
    {
      validator: (_rule, value, cb) => {
        if (dialogMode.value === 'create' && !value) return cb(new Error('请输入密码'))
        if (value && String(value).length < 8) return cb(new Error('密码至少 8 位'))
        cb()
      },
      trigger: 'blur',
    },
  ],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, {
    id: undefined,
    username: '',
    password: '',
    email: '',
    display_name: '',
    role: 'operator' as Role,
    is_active: true,
  })
  dialogVisible.value = true
}

function openEdit(row: User) {
  dialogMode.value = 'edit'
  Object.assign(form, {
    id: row.id,
    username: row.username,
    password: '',
    email: row.email,
    display_name: row.display_name,
    role: row.role,
    is_active: row.is_active,
  })
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (dialogMode.value === 'create') {
      await createUser({
        username: form.username,
        password: form.password,
        email: form.email,
        display_name: form.display_name,
        role: form.role,
        is_active: form.is_active,
      })
      ElMessage.success('用户新增成功')
    } else if (form.id) {
      const payload: Partial<UserWritePayload> = {
        email: form.email,
        display_name: form.display_name,
        role: form.role,
        is_active: form.is_active,
      }
      if (form.password) payload.password = form.password
      await updateUser(form.id, payload)
      ElMessage.success('用户已更新')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: User) {
  try {
    await ElMessageBox.confirm(`确定删除用户「${row.username}」？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteUser(row.id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* noop */
  }
}

const roleLabel = (r: Role) =>
  r === 'admin' ? '管理员' : r === 'operator' ? '操作员' : '查询用户'
const roleTag = (r: Role) => (r === 'admin' ? 'danger' : r === 'operator' ? 'warning' : 'info')

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="账号管理" subtitle="维护系统用户及其角色权限（仅管理员可见）">
      <template #extra>
        <el-button type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增用户
        </el-button>
      </template>
    </PageHeader>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="() => { filters.search=''; filters.role=undefined; page=1; fetchList() }"
    >
      <el-form-item label="用户名">
        <el-input v-model="filters.search" placeholder="按用户名搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="filters.role" placeholder="全部" clearable style="width: 160px">
          <el-option label="管理员" value="admin" />
          <el-option label="操作员" value="operator" />
          <el-option label="查询用户" value="viewer" />
        </el-select>
      </el-form-item>
    </FilterBar>

    <CrudTable
      :rows="rows"
      :loading="loading"
      :total="total"
      :page="page"
      :page-size="pageSize"
      row-key="id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="id" label="#" width="70" />
      <el-table-column prop="username" label="用户名" min-width="140" />
      <el-table-column prop="display_name" label="显示名" min-width="140" />
      <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
      <el-table-column label="角色" width="110">
        <template #default="{ row }">
          <el-tag :type="roleTag(row.role)" size="small" effect="light">{{ roleLabel(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="170" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" @click="onDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增用户' : '编辑用户'" width="520" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="dialogMode === 'edit'" />
        </el-form-item>
        <el-form-item label="显示名"><el-input v-model="form.display_name" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            :placeholder="dialogMode === 'edit' ? '不修改请留空' : '至少 8 位'"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="form.role">
            <el-radio value="admin">管理员</el-radio>
            <el-radio value="operator">操作员</el-radio>
            <el-radio value="viewer">查询用户</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
