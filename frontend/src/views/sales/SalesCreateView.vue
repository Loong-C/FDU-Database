<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { listProducts } from '@/api/products'
import { listCustomers } from '@/api/customers'
import { createSale, type SaleWritePayload } from '@/api/sales'
import type { Customer, PaymentMethod, Product } from '@/api/types'
import { formatCurrency } from '@/utils/format'
import { ApiError } from '@/api/http'
import { firstErrorMessage } from '@/utils/errors'
import { useDictsStore } from '@/stores/dicts'

interface CartLine {
  product_id: number
  product_name: string
  unit: string
  unit_price: number
  stock_qty: number
  quantity: number
}

const router = useRouter()
const dicts = useDictsStore()

const productSearch = ref('')
const productLoading = ref(false)
const productResults = ref<Product[]>([])
const customerSearch = ref('')
const customerOptions = ref<Customer[]>([])
const customerLoading = ref(false)

const cart = ref<CartLine[]>([])
const cartError = ref<string | null>(null)
const lineErrors = ref<Record<number, string>>({})

const form = reactive<{
  store_id: number | null
  customer_id: number | null
  sale_time: string
  payment_method: PaymentMethod
  discount_amount: number
}>({
  store_id: null,
  customer_id: null,
  sale_time: dayjs().format('YYYY-MM-DDTHH:mm:ss'),
  payment_method: 'wechat',
  discount_amount: 0,
})

const totalAmount = computed(() => cart.value.reduce((acc, l) => acc + l.unit_price * l.quantity, 0))
const actualAmount = computed(() => Math.max(0, totalAmount.value - (Number(form.discount_amount) || 0)))
const submitting = ref(false)

async function onSearchProducts() {
  productLoading.value = true
  try {
    const data = await listProducts({
      page: 1,
      page_size: 16,
      search: productSearch.value || undefined,
      status: 'onsale',
    })
    productResults.value = data.items
  } finally {
    productLoading.value = false
  }
}

async function onSearchCustomers(query: string) {
  customerSearch.value = query
  if (!query) {
    customerOptions.value = []
    return
  }
  customerLoading.value = true
  try {
    const data = await listCustomers({ page: 1, page_size: 20, search: query, status: 'active' })
    customerOptions.value = data.items
  } finally {
    customerLoading.value = false
  }
}

function addToCart(product: Product) {
  if (product.status !== 'onsale') {
    ElMessage.warning('该商品当前不在售')
    return
  }
  if (product.stock_qty <= 0) {
    ElMessage.warning('该商品暂无库存')
    return
  }
  const exist = cart.value.find((c) => c.product_id === product.product_id)
  if (exist) {
    if (exist.quantity + 1 > exist.stock_qty) {
      ElMessage.warning(`库存仅剩 ${exist.stock_qty}，无法再添加`)
      return
    }
    exist.quantity += 1
  } else {
    cart.value.push({
      product_id: product.product_id,
      product_name: product.product_name,
      unit: product.unit,
      unit_price: Number(product.unit_price),
      stock_qty: product.stock_qty,
      quantity: 1,
    })
  }
  lineErrors.value[product.product_id] = ''
}

function removeLine(productId: number) {
  cart.value = cart.value.filter((l) => l.product_id !== productId)
  delete lineErrors.value[productId]
}

function clearCart() {
  cart.value = []
  lineErrors.value = {}
}

async function onSubmit() {
  if (!form.store_id) {
    ElMessage.warning('请选择门店')
    return
  }
  if (!cart.value.length) {
    cartError.value = '购物车为空，请先添加商品'
    return
  }
  cartError.value = null
  lineErrors.value = {}

  const payload: SaleWritePayload = {
    store_id: form.store_id,
    customer_id: form.customer_id ?? null,
    sale_time: dayjs(form.sale_time).toISOString(),
    payment_method: form.payment_method,
    discount_amount: Number(form.discount_amount) || 0,
    items: cart.value.map((l) => ({ product_id: l.product_id, quantity: l.quantity })),
  }

  submitting.value = true
  try {
    const created = await createSale(payload)
    ElMessage.success(`销售单 #${created.sale_id} 已开立`)
    router.replace(`/sales/${created.sale_id}`)
  } catch (error) {
    if (error instanceof ApiError) {
      const itemsMsg = (error.errors?.items ?? null) as string | string[] | null
      const firstMsg = Array.isArray(itemsMsg) ? itemsMsg[0] : itemsMsg
      if (firstMsg) {
        // 尝试把 message 绑定到对应行
        cart.value.forEach((line) => {
          if (typeof firstMsg === 'string' && firstMsg.includes(line.product_name)) {
            lineErrors.value[line.product_id] = String(firstMsg)
          }
        })
        cartError.value = String(firstMsg)
      } else {
        const msg = firstErrorMessage(error)
        cartError.value = msg || error.message
      }
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  dicts.ensureStores().then(() => {
    if (dicts.stores.length && !form.store_id) {
      form.store_id = dicts.stores[0].store_id
    }
  })
  onSearchProducts()
})
</script>

<template>
  <div class="page-wrapper">
    <PageHeader title="新开销售单" subtitle="POS 风格下单：搜索商品 → 加入购物车 → 选择门店与支付方式 → 提交">
      <template #extra>
        <el-button @click="router.push('/sales')">
          <el-icon><ArrowLeft /></el-icon>返回列表
        </el-button>
      </template>
    </PageHeader>

    <div class="pos-layout">
      <!-- 左：商品搜索与卡片 -->
      <section class="pos-panel pos-panel--products app-card">
        <div class="pos-products__head">
          <el-input
            v-model="productSearch"
            placeholder="搜索商品名称 / 条码 / 作者"
            clearable
            size="large"
            :prefix-icon="'Search'"
            @keyup.enter="onSearchProducts"
            @clear="onSearchProducts"
            style="flex: 1"
          />
          <el-button type="primary" size="large" :loading="productLoading" @click="onSearchProducts">搜索</el-button>
        </div>
        <div v-loading="productLoading" class="pos-products__grid">
          <button
            v-for="p in productResults"
            :key="p.product_id"
            type="button"
            class="product-card app-card app-card--hover"
            :class="{ 'product-card--out': p.stock_qty === 0 }"
            :disabled="p.stock_qty === 0"
            @click="addToCart(p)"
          >
            <div class="product-card__top">
              <el-tag v-if="p.is_book" type="primary" effect="light" size="small" round>图书</el-tag>
              <el-tag v-if="p.stock_qty === 0" type="danger" size="small">缺货</el-tag>
              <el-tag v-else-if="p.stock_qty < 10" type="warning" size="small">低库存</el-tag>
            </div>
            <div class="product-card__name">{{ p.product_name }}</div>
            <div class="product-card__meta text-muted">{{ p.category_name }} · 库存 {{ p.stock_qty }} {{ p.unit }}</div>
            <div class="product-card__price money">{{ formatCurrency(p.unit_price) }}</div>
          </button>
          <EmptyState
            v-if="!productLoading && !productResults.length"
            icon="Search"
            title="无匹配商品"
            description="请更换关键词搜索"
          />
        </div>
      </section>

      <!-- 右：购物车与结算 -->
      <section class="pos-panel pos-panel--cart app-card">
        <header class="pos-cart__head">
          <h3 class="section-title">
            <el-icon><ShoppingCart /></el-icon>
            购物车（{{ cart.length }} 项）
          </h3>
          <el-button v-if="cart.length" text type="danger" @click="clearCart">清空</el-button>
        </header>

        <div v-if="!cart.length" class="pos-cart__empty">
          <EmptyState icon="ShoppingCart" title="购物车空空如也" description="点击左侧商品加入" />
        </div>

        <ul v-else class="pos-cart__list">
          <li v-for="line in cart" :key="line.product_id" class="pos-cart__line">
            <div class="pos-cart__line-top">
              <span class="pos-cart__name">{{ line.product_name }}</span>
              <el-button text type="danger" @click="removeLine(line.product_id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <div class="pos-cart__line-mid">
              <el-input-number
                v-model="line.quantity"
                :min="1"
                :max="line.stock_qty"
                size="small"
                controls-position="right"
              />
              <span class="text-muted money">× {{ formatCurrency(line.unit_price) }}</span>
              <span class="money pos-cart__line-total">{{ formatCurrency(line.unit_price * line.quantity) }}</span>
            </div>
            <div v-if="lineErrors[line.product_id]" class="pos-cart__line-error">
              <el-icon><WarningFilled /></el-icon>
              {{ lineErrors[line.product_id] }}
            </div>
          </li>
        </ul>

        <div class="pos-cart__meta">
          <el-form label-width="80px" size="default">
            <el-form-item label="门店" required>
              <el-select v-model="form.store_id" placeholder="请选择" style="width: 100%">
                <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
              </el-select>
            </el-form-item>
            <el-form-item label="客户">
              <el-select
                v-model="form.customer_id"
                placeholder="游客（可留空）"
                filterable
                remote
                clearable
                :remote-method="onSearchCustomers"
                :loading="customerLoading"
                style="width: 100%"
              >
                <el-option v-for="c in customerOptions" :key="c.customer_id" :label="c.customer_name + (c.phone ? ` · ${c.phone}` : '')" :value="c.customer_id" />
              </el-select>
            </el-form-item>
            <el-form-item label="开单时间">
              <el-date-picker
                v-model="form.sale_time"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="支付方式">
              <el-radio-group v-model="form.payment_method">
                <el-radio-button value="cash">现金</el-radio-button>
                <el-radio-button value="card">银行卡</el-radio-button>
                <el-radio-button value="wechat">微信</el-radio-button>
                <el-radio-button value="alipay">支付宝</el-radio-button>
                <el-radio-button value="mixed">混合</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="优惠金额">
              <el-input-number v-model="form.discount_amount" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-form>
        </div>

        <div v-if="cartError" class="pos-cart__error">
          <el-alert type="error" :title="cartError" :closable="false" show-icon />
        </div>

        <div class="pos-cart__totals">
          <div class="pos-cart__total-row">
            <span class="text-muted">商品原价</span>
            <span class="money">{{ formatCurrency(totalAmount) }}</span>
          </div>
          <div class="pos-cart__total-row">
            <span class="text-muted">优惠</span>
            <span class="money" style="color: var(--warning)">-{{ formatCurrency(form.discount_amount || 0) }}</span>
          </div>
          <div class="pos-cart__total-row pos-cart__total-row--final">
            <span>实付</span>
            <span class="money">{{ formatCurrency(actualAmount) }}</span>
          </div>
        </div>

        <el-button
          type="primary"
          size="large"
          style="width: 100%"
          :loading="submitting"
          :disabled="!cart.length || !form.store_id"
          @click="onSubmit"
        >
          <el-icon><Check /></el-icon>
          提交销售单
        </el-button>
      </section>
    </div>
  </div>
</template>

<style scoped>
.pos-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(360px, 1fr);
  gap: 16px;
}

.pos-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 70vh;
}

.pos-products__head {
  display: flex;
  gap: 8px;
}

.pos-products__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
  flex: 1;
}

.product-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 4px;
  cursor: pointer;
  text-align: left;
  padding: 14px;
  border: 1px solid var(--app-border);
  background: var(--app-surface);
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.product-card:hover:not(:disabled) {
  border-color: var(--brand);
  transform: translateY(-1px);
}

.product-card:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.product-card--out {
  background: var(--app-surface-alt);
}

.product-card__top {
  display: flex;
  gap: 4px;
  min-height: 22px;
}

.product-card__name {
  font-weight: 600;
  font-size: 14px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-card__meta {
  font-size: 12px;
}

.product-card__price {
  font-weight: 700;
  font-size: 18px;
  color: var(--brand);
}

.pos-cart__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.pos-cart__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  overflow-y: auto;
  max-height: 40vh;
}

.pos-cart__line {
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 10px 12px;
  background: var(--app-surface-alt);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pos-cart__line-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.pos-cart__name {
  font-weight: 600;
}

.pos-cart__line-mid {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.pos-cart__line-total {
  font-weight: 700;
  color: var(--brand);
}

.pos-cart__line-error {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--danger);
}

.pos-cart__totals {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 0;
  border-top: 1px dashed var(--app-border);
}

.pos-cart__total-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.pos-cart__total-row--final {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand);
  margin-top: 4px;
}

.pos-cart__meta :deep(.el-form-item) {
  margin-bottom: 12px;
}

@media (max-width: 1100px) {
  .pos-layout {
    grid-template-columns: 1fr;
  }
}
</style>
