<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import FilterBar from '@/components/common/FilterBar.vue'
import CrudTable from '@/components/common/CrudTable.vue'
import {
  deleteMember,
  listMembers,
  updateMember,
  type MemberQuery,
  type MemberWritePayload,
} from '@/api/members'
import type { Member, MemberLevel } from '@/api/types'
import { formatDate, memberLevelLabel } from '@/utils/format'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'

const rows = ref<Member[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filters = reactive<MemberQuery>({ search: '', level: undefined })

// Stats
const levelCounts = computed(() => {
  const base: Record<MemberLevel, number> = { bronze: 0, silver: 0, gold: 0, platinum: 0 }
  rows.value.forEach((m) => (base[m.level] = (base[m.level] ?? 0) + 1))
  return base
})

const pointsSum = computed(() => rows.value.reduce((acc, m) => acc + (m.points || 0), 0))

async function fetchList() {
  loading.value = true
  try {
    const data = await listMembers({
      page: page.value,
      page_size: pageSize.value,
      search: filters.search || undefined,
      level: filters.level,
    })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

const dialogVisible = ref(false)
const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const editingId = ref<number | null>(null)
const form = reactive<MemberWritePayload>({
  customer_id: 0,
  member_no: '',
  level: 'bronze',
  points: 0,
  join_date: '',
})
const rules: FormRules = {
  member_no: [{ required: true, message: '请输入会员编号', trigger: 'blur' }],
  level: [{ required: true, message: '请选择等级', trigger: 'change' }],
  join_date: [{ required: true, message: '请选择入会日期', trigger: 'change' }],
}

function openEdit(row: Member) {
  editingId.value = row.customer_id
  form.customer_id = row.customer_id
  form.member_no = row.member_no
  form.level = row.level
  form.points = row.points
  form.join_date = row.join_date
  dialogVisible.value = true
}

async function onSubmit() {
  if (!formRef.value || !editingId.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    await updateMember(editingId.value, {
      member_no: form.member_no,
      level: form.level,
      points: form.points,
      join_date: form.join_date,
    })
    ElMessage.success('会员信息已更新')
    dialogVisible.value = false
    fetchList()
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}

async function onDelete(row: Member) {
  try {
    await ElMessageBox.confirm(`确定取消「${row.customer_name}」的会员身份？客户资料仍保留。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '取消会员',
      cancelButtonText: '返回',
    })
  } catch {
    return
  }
  try {
    await deleteMember(row.customer_id)
    ElMessage.success('已取消会员身份')
    fetchList()
  } catch {
    /* 409 */
  }
}

const levelTag = (l: MemberLevel) =>
  l === 'platinum' ? 'success' : l === 'gold' ? 'warning' : l === 'silver' ? 'info' : 'danger'

onMounted(fetchList)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="会员管理" subtitle="会员等级、积分与消费追踪">
      <template #extra>
        <el-button @click="fetchList">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </template>
    </PageHeader>

    <div class="member-stats stat-grid">
      <article class="app-card member-stat-card" v-for="level in (['bronze','silver','gold','platinum'] as MemberLevel[])" :key="level">
        <div class="member-stat-card__head">
          <div class="member-stat-card__badge" :data-level="level">
            <el-icon :size="18"><Medal /></el-icon>
          </div>
          <span class="member-stat-card__label">{{ memberLevelLabel(level) }}</span>
        </div>
        <div class="member-stat-card__value money">{{ levelCounts[level] }}</div>
        <div class="text-muted" style="font-size: 12px">位会员</div>
      </article>
      <article class="app-card member-stat-card member-stat-card--points">
        <div class="member-stat-card__head">
          <div class="member-stat-card__badge" data-level="points">
            <el-icon :size="18"><Coin /></el-icon>
          </div>
          <span class="member-stat-card__label">当前页累计积分</span>
        </div>
        <div class="member-stat-card__value money">{{ pointsSum.toLocaleString('zh-CN') }}</div>
        <div class="text-muted" style="font-size: 12px">积分可用于折扣</div>
      </article>
    </div>

    <FilterBar
      :loading="loading"
      @submit="() => { page = 1; fetchList() }"
      @reset="() => { filters.search=''; filters.level=undefined; page=1; fetchList() }"
    >
      <el-form-item label="姓名">
        <el-input v-model="filters.search" placeholder="按客户姓名搜索" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item label="等级">
        <el-select v-model="filters.level" placeholder="全部" clearable style="width: 140px">
          <el-option label="青铜" value="bronze" />
          <el-option label="白银" value="silver" />
          <el-option label="黄金" value="gold" />
          <el-option label="铂金" value="platinum" />
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
      empty-icon="Medal"
      empty-title="尚未有会员"
      empty-description="可以在客户页面把已有客户升级为会员"
      @page-change="(p) => { page = p; fetchList() }"
      @size-change="(s) => { pageSize = s; page = 1; fetchList() }"
    >
      <el-table-column prop="customer_id" label="#" width="70" />
      <el-table-column prop="member_no" label="会员编号" width="160" />
      <el-table-column prop="customer_name" label="姓名" min-width="140" />
      <el-table-column label="等级" width="110">
        <template #default="{ row }">
          <el-tag :type="levelTag(row.level)" size="small" effect="light">
            {{ memberLevelLabel(row.level) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="积分" width="140">
        <template #default="{ row }">
          <div class="points-cell">
            <span class="money">{{ row.points.toLocaleString('zh-CN') }}</span>
            <el-progress
              :percentage="Math.min(100, Math.round((row.points / 2000) * 100))"
              :show-text="false"
              :stroke-width="6"
              :color="'#f59e0b'"
              style="width: 80px"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="电话" width="150" />
      <el-table-column label="入会日期" width="120">
        <template #default="{ row }">{{ formatDate(row.join_date) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.customer_status === 'active' ? 'success' : 'info'" size="small">
            {{ row.customer_status === 'active' ? '启用' : '停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="170" fixed="right" align="right">
        <template #default="{ row }">
          <div class="table-actions">
            <el-button v-if="canWrite()" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="canWrite()" text type="danger" @click="onDelete(row)">取消会员</el-button>
            <span v-if="!canWrite()" class="text-muted">—</span>
          </div>
        </template>
      </el-table-column>
    </CrudTable>

    <el-dialog v-model="dialogVisible" title="编辑会员" width="480" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="会员编号" prop="member_no"><el-input v-model="form.member_no" /></el-form-item>
        <el-form-item label="等级" prop="level">
          <el-radio-group v-model="form.level">
            <el-radio value="bronze">青铜</el-radio>
            <el-radio value="silver">白银</el-radio>
            <el-radio value="gold">黄金</el-radio>
            <el-radio value="platinum">铂金</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="积分"><el-input-number v-model="form.points" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="入会日期" prop="join_date">
          <el-date-picker v-model="form.join_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
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
.member-stat-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 110px;
}
.member-stat-card__head {
  display: flex;
  align-items: center;
  gap: 10px;
}
.member-stat-card__badge {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}
.member-stat-card__badge[data-level='bronze'] { background: linear-gradient(135deg, #b45309, #92400e); }
.member-stat-card__badge[data-level='silver'] { background: linear-gradient(135deg, #94a3b8, #64748b); }
.member-stat-card__badge[data-level='gold'] { background: linear-gradient(135deg, #f59e0b, #d97706); }
.member-stat-card__badge[data-level='platinum'] { background: linear-gradient(135deg, #14b8a6, #0d9488); }
.member-stat-card__badge[data-level='points'] { background: linear-gradient(135deg, var(--brand), var(--accent)); }

.member-stat-card__label {
  font-size: 13px;
  color: var(--app-text-muted);
}
.member-stat-card__value {
  font-size: 26px;
  font-weight: 700;
}
.points-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
