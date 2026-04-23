<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import { deleteSale, getSale } from '@/api/sales'
import type { Sale } from '@/api/types'
import { formatCurrency, formatDateTime, paymentLabel } from '@/utils/format'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const canWrite = () => auth.role === 'admin' || auth.role === 'operator'

const loading = ref(false)
const detail = ref<Sale | null>(null)

const id = computed(() => Number(route.params.id))

async function fetchDetail() {
  loading.value = true
  try {
    detail.value = await getSale(id.value)
  } finally {
    loading.value = false
  }
}

async function onDelete() {
  if (!detail.value) return
  try {
    await ElMessageBox.confirm(`确定删除销售单 #${detail.value.sale_id}？对应库存会自动回滚。`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteSale(detail.value.sale_id)
    ElMessage.success('销售单已删除')
    router.replace('/sales')
  } catch {
    /* noop */
  }
}

onMounted(fetchDetail)
</script>

<template>
  <div class="page-wrapper">
    <PageHeader :title="`销售单 #${id}`" subtitle="查看订单明细、金额与支付方式">
      <template #extra>
        <el-button @click="router.push('/sales')">
          <el-icon><ArrowLeft /></el-icon>返回列表
        </el-button>
        <el-button v-if="canWrite() && detail" type="danger" @click="onDelete">
          <el-icon><Delete /></el-icon>删除订单
        </el-button>
      </template>
    </PageHeader>

    <el-skeleton v-if="loading" :rows="6" animated />

    <template v-else-if="detail">
      <section class="sale-summary stat-grid">
        <article class="app-card">
          <div class="text-muted" style="font-size: 12px">门店</div>
          <div class="summary-value">{{ detail.store_name }}</div>
        </article>
        <article class="app-card">
          <div class="text-muted" style="font-size: 12px">客户</div>
          <div class="summary-value">{{ detail.customer_name || '游客' }}</div>
        </article>
        <article class="app-card">
          <div class="text-muted" style="font-size: 12px">支付方式</div>
          <div class="summary-value">
            <el-tag effect="plain" round>{{ paymentLabel(detail.payment_method) }}</el-tag>
          </div>
        </article>
        <article class="app-card">
          <div class="text-muted" style="font-size: 12px">开单时间</div>
          <div class="summary-value">{{ formatDateTime(detail.sale_time) }}</div>
        </article>
      </section>

      <section class="app-card">
        <h3 class="section-title">
          <el-icon><Document /></el-icon>销售明细
        </h3>
        <el-table :data="detail.items" border stripe>
          <el-table-column prop="line_no" label="#" width="60" />
          <el-table-column prop="product_name" label="商品" min-width="240" />
          <el-table-column label="单价" width="140" align="right">
            <template #default="{ row }"><span class="money">{{ formatCurrency(row.unit_price) }}</span></template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="100" align="right" />
          <el-table-column label="小计" width="150" align="right">
            <template #default="{ row }"><strong class="money">{{ formatCurrency(row.line_amount) }}</strong></template>
          </el-table-column>
        </el-table>
      </section>

      <section class="sale-totals app-card">
        <div class="sale-totals__item">
          <span class="text-muted">商品总额</span>
          <span class="money">{{ formatCurrency(detail.total_amount) }}</span>
        </div>
        <div class="sale-totals__item">
          <span class="text-muted">优惠</span>
          <span class="money" style="color: var(--warning)">-{{ formatCurrency(detail.discount_amount) }}</span>
        </div>
        <el-divider />
        <div class="sale-totals__item sale-totals__item--final">
          <span>实付金额</span>
          <span class="money" style="color: var(--brand)">{{ formatCurrency(detail.actual_amount) }}</span>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.summary-value {
  font-size: 16px;
  font-weight: 600;
  margin-top: 4px;
}

.sale-totals {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 480px;
  margin-left: auto;
}

.sale-totals__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.sale-totals__item--final {
  font-size: 18px;
  font-weight: 700;
}
</style>
