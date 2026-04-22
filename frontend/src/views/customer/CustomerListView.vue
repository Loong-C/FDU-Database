<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import {
  createCustomer,
  deleteCustomer,
  listCustomers,
  updateCustomer,
  type CustomerQuery,
} from '@/api/customers'
import { createMember } from '@/api/members'
import type { Customer, MemberLevel } from '@/api/types'
import { formatDateTime } from '@/utils/format'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'

const rows = ref<Customer[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<CustomerQuery>({ search: '', status: undefined })

async function fetchList() {
  loading.value = true
  try {
    const data = await listCustomers({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      status: filters.status,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

// Main form
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const form = reactive<Partial<Customer>>({
  customer_name: '',
  phone: '',
  email: '',
  address: '',
  status: 'active',
})
const rules: FormRules = {
  customer_name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

function openCreate() {
  dialogMode.value = 'create'
  Object.assign(form, { customer_id: undefined, customer_name: '', phone: '', email: '', address: '', status: 'active' })
  dialogVisible.value = true
}
function openEdit(row: Customer) {
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
    const payload: Partial<Customer> = {
      customer_name: form.customer_name,
      phone: form.phone || null,
      email: form.email || null,
      address: form.address || null,
      status: form.status,
    }
    if (dialogMode.value === 'create') {
      await createCustomer(payload)
      ElMessage.success('客户新增成功')
    } else if (form.customer_id) {
      await updateCustomer(form.customer_id, payload)
      ElMessage.success('客户已更新')
    }
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: Customer) {
  try {
    await ElMessageBox.confirm(`删除客户「${row.customer_name}」？若已是会员或存在销售记录将无法删除。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteCustomer(row.customer_id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    /* 409 */
  }
}

// Upgrade to member
const memberDialogVisible = ref(false)
const memberFormRef = ref<FormInstance | null>(null)
const memberSubmitting = ref(false)
const memberForm = reactive<{
  customer_id: number | null
  customer_name: string
  member_no: string
  level: MemberLevel
  points: number
  join_date: string
}>({
  customer_id: null,
  customer_name: '',
  member_no: '',
  level: 'bronze',
  points: 0,
  join_date: dayjs().format('YYYY-MM-DD'),
})

const memberRules: FormRules = {
  member_no: [{ required: true, message: '请输入会员编号', trigger: 'blur' }],
  level: [{ required: true, message: '请选择等级', trigger: 'change' }],
  join_date: [{ required: true, message: '请选择入会日期', trigger: 'change' }],
}

function openUpgrade(row: Customer) {
  memberForm.customer_id = row.customer_id
  memberForm.customer_name = row.customer_name
  memberForm.member_no = `M${dayjs().format('YYYYMMDD')}${String(row.customer_id).padStart(3, '0')}`
  memberForm.level = 'bronze'
  memberForm.points = 0
  memberForm.join_date = dayjs().format('YYYY-MM-DD')
  memberDialogVisible.value = true
}

async function onUpgradeSubmit() {
  if (!memberFormRef.value) return
  const valid = await memberFormRef.value.validate().catch(() => false)
  if (!valid || !memberForm.customer_id) return
  memberSubmitting.value = true
  try {
    await createMember({
      customer_id: memberForm.customer_id,
      member_no: memberForm.member_no,
      level: memberForm.level,
      points: memberForm.points,
      join_date: memberForm.join_date,
    })
    ElMessage.success(`${memberForm.customer_name} 已升级为会员`)
    memberDialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(memberFormRef.value, error)
  } finally {
    memberSubmitting.value = false
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="客户管理" subtitle="维护顾客基础信息，并可一键升级为会员">
      <template #extra>
        <el-button v-if="canWrite()" type="primary" @click="openCreate">
          <el-icon><Plus /></el-icon>新增客户
        </el-button>
      </template>
    </PageHeader>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="() => { filters.search=''; filters.status=undefined; page=1; fetchList() }"
    >
      <el-form-item label="名称">
        <el-input v-model="filters.search" placeholder="按姓名搜索" clearable style="width: 200px" />
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
      row-key="customer_id"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="customer_id" label="#" width="60" />
      <el-table-column label="姓名" min-width="130">
        <template #default="{ row }">
          <div class="name-cell">
            <span>{{ row.customer_name }}</span>
            <el-tag v-if="row.is_member" size="small" type="warning" effect="light" round>会员</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="电话" width="130" />
      <el-table-column prop="email" label="邮箱" min-width="170" show-overflow-tooltip />
      <el-table-column prop="address" label="地址" min-width="170" show-overflow-tooltip />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
            {{ row.status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="注册时间" width="140">
        <template #default="{ row }">{{ formatDateTime(row.register_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="170" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button v-if="canWrite() && !row.is_member" text type="warning" @click="openUpgrade(row)">
              升级
            </el-button>
            <el-button v-if="canWrite()" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="canWrite()" text type="danger" @click="onDelete(row)">删除</el-button>
            <span v-if="!canWrite()" class="text-muted">—</span>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? '新增客户' : '编辑客户'" width="520" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="姓名" prop="customer_name"><el-input v-model="form.customer_name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱" prop="email"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" type="textarea" :rows="2" /></el-form-item>
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

    <el-dialog v-model="memberDialogVisible" title="升级为会员" width="480" destroy-on-close>
      <el-form ref="memberFormRef" :model="memberForm" :rules="memberRules" label-width="90px">
        <el-form-item label="客户">
          <el-input :model-value="memberForm.customer_name" disabled />
        </el-form-item>
        <el-form-item label="会员编号" prop="member_no"><el-input v-model="memberForm.member_no" /></el-form-item>
        <el-form-item label="等级" prop="level">
          <el-radio-group v-model="memberForm.level">
            <el-radio value="bronze">青铜</el-radio>
            <el-radio value="silver">白银</el-radio>
            <el-radio value="gold">黄金</el-radio>
            <el-radio value="platinum">铂金</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="初始积分"><el-input-number v-model="memberForm.points" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="入会日期" prop="join_date">
          <el-date-picker v-model="memberForm.join_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="memberDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="memberSubmitting" @click="onUpgradeSubmit">升级</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.name-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
</style>
