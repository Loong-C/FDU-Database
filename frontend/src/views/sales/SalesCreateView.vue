<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import dayjs from 'dayjs'
import PageHeader from '@/components/common/PageHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { listProducts } from '@/api/products'
import { listCustomers } from '@/api/customers'
import { createCustomer } from '@/api/customers'
import { createMember } from '@/api/members'
import { createSale, type SaleWritePayload } from '@/api/sales'
import type { Customer, MemberLevel, PaymentMethod, Product } from '@/api/types'
import { formatCurrency } from '@/utils/format'
import { ApiError } from '@/api/http'
import { firstErrorMessage } from '@/utils/errors'
import { useDictsStore } from '@/stores/dicts'
import { defaultStoreId } from '@/utils/defaults'

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
const productLoadingMore = ref(false)
const productResults = ref<Product[]>([])
const productTotalCount = ref(0)
let productSearchToken = 0
const productDisplayLimit = 1000
const productPageSize = 100
const customerSearch = ref('')
const customerOptions = ref<Customer[]>([])
const customerLoading = ref(false)

const cart = ref<CartLine[]>([])
const cartError = ref<string | null>(null)
const lineErrors = ref<Record<number, string>>({})
const customerDialogVisible = ref(false)
const customerFormRef = ref<FormInstance | null>(null)
const customerSubmitting = ref(false)

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
const selectedCustomer = computed(() => customerOptions.value.find((item) => item.customer_id === form.customer_id) || null)
const estimatedPoints = computed(() => (selectedCustomer.value?.is_member ? Math.floor(actualAmount.value) : 0))
const submitting = ref(false)

const customerForm = reactive<{
  customer_name: string
  phone: string
  email: string
  address: string
  make_member: boolean
  level: MemberLevel
}>({
  customer_name: '',
  phone: '',
  email: '',
  address: '',
  make_member: true,
  level: 'bronze',
})

const customerRules: FormRules = {
  customer_name: [{ required: true, message: '请输入客户姓名', trigger: 'blur' }],
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
}

async function onSearchProducts() {
  if (!form.store_id) {
    ElMessage.warning('请先选择销售门店')
    return
  }
  const storeId = form.store_id
  const search = productSearch.value || undefined
  const searchToken = ++productSearchToken
  productResults.value = []
  productTotalCount.value = 0
  productLoading.value = true
  productLoadingMore.value = false
  try {
    const first = await listProducts({
      page: 1,
      page_size: productPageSize,
      search,
      status: 'onsale',
      store_id: storeId,
    })
    if (searchToken !== productSearchToken || storeId !== form.store_id) return
    productTotalCount.value = first.total
    productResults.value = first.items
    productLoading.value = false

    const visibleTotal = Math.min(first.total, productDisplayLimit)
    const totalPages = Math.ceil(visibleTotal / first.page_size)
    if (totalPages <= 1) return
    productLoadingMore.value = true
    const pages = Array.from({ length: totalPages - 1 }, (_, index) => index + 2)
    const batchSize = 6
    for (let index = 0; index < pages.length; index += batchSize) {
      const batch = pages.slice(index, index + batchSize)
      const responses = await Promise.all(
        batch.map((page) =>
          listProducts({
            page,
            page_size: productPageSize,
            search,
            status: 'onsale',
            store_id: storeId,
          }),
        ),
      )
      if (searchToken !== productSearchToken || storeId !== form.store_id) return
      productResults.value = [
        ...productResults.value,
        ...responses.flatMap((data) => data.items),
      ].slice(0, productDisplayLimit)
    }
  } finally {
    if (searchToken === productSearchToken) {
      productLoading.value = false
      productLoadingMore.value = false
    }
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

function productStoreStockAt(product: Product, storeId: number | null): number {
  if (!storeId) return 0
  const row = product.inventory?.find((item) => item.store_id === storeId)
  return row?.stock_qty ?? 0
}

function productStoreStock(product: Product): number {
  return productStoreStockAt(product, form.store_id)
}

function isProductLowStock(product: Product): boolean {
  if (!form.store_id) return false
  const row = product.inventory?.find((item) => item.store_id === form.store_id)
  return !!row && row.stock_qty > 0 && row.stock_qty <= row.safety_stock_qty
}

function addToCart(product: Product) {
  if (!form.store_id) {
    ElMessage.warning('请先选择销售门店')
    return
  }
  if (product.status !== 'onsale') {
    ElMessage.warning('该商品当前不在售')
    return
  }
  const stockQty = productStoreStock(product)
  if (stockQty <= 0) {
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
      stock_qty: stockQty,
      quantity: 1,
    })
  }
  lineErrors.value[product.product_id] = ''
}

watch(
  () => form.store_id,
  (next, prev) => {
    if (prev && next !== prev && cart.value.length) {
      clearCart()
      ElMessage.info('已切换门店，购物车已清空')
    }
    if (next) {
      onSearchProducts()
    } else {
      productResults.value = []
    }
  },
)

function removeLine(productId: number) {
  cart.value = cart.value.filter((l) => l.product_id !== productId)
  delete lineErrors.value[productId]
}

function clearCart() {
  cart.value = []
  lineErrors.value = {}
}

function openCustomerDialog() {
  Object.assign(customerForm, {
    customer_name: '',
    phone: '',
    email: '',
    address: '',
    make_member: true,
    level: 'bronze' as MemberLevel,
  })
  customerDialogVisible.value = true
}

async function onCustomerSubmit() {
  if (!customerFormRef.value) return
  const valid = await customerFormRef.value.validate().catch(() => false)
  if (!valid) return
  customerSubmitting.value = true
  try {
    const created = await createCustomer({
      customer_name: customerForm.customer_name,
      phone: customerForm.phone || null,
      email: customerForm.email || null,
      address: customerForm.address || null,
      status: 'active',
    })
    let nextCustomer: Customer = created
    if (customerForm.make_member) {
      await createMember({
        customer_id: created.customer_id,
        member_no: `M${dayjs().format('YYYYMMDD')}${String(created.customer_id).padStart(3, '0')}`,
        level: customerForm.level,
        points: 0,
        join_date: dayjs().format('YYYY-MM-DD'),
      })
      nextCustomer = { ...created, is_member: true }
    }
    customerOptions.value = [nextCustomer, ...customerOptions.value.filter((item) => item.customer_id !== created.customer_id)]
    form.customer_id = created.customer_id
    ElMessage.success(customerForm.make_member ? '客户已新增并升级为会员' : '客户已新增')
    customerDialogVisible.value = false
  } finally {
    customerSubmitting.value = false
  }
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
      form.store_id = defaultStoreId(dicts.stores)
    } else if (form.store_id) {
      onSearchProducts()
    }
  })
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
          <el-select v-model="form.store_id" placeholder="销售门店" size="large" style="width: 190px">
            <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
          </el-select>
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
        <div v-if="productLoadingMore" class="pos-products__hint text-muted">
          正在加载商品（{{ productResults.length }} / {{ Math.min(productTotalCount, productDisplayLimit) }}）
        </div>
        <div v-else-if="productTotalCount > productDisplayLimit" class="pos-products__hint text-muted">
          当前仅显示前 {{ productDisplayLimit }} 个匹配商品，可输入名称、条码或作者继续精确搜索。
        </div>
        <div v-loading="productLoading" class="pos-products__grid">
          <button
            v-for="p in productResults"
            :key="p.product_id"
            type="button"
            class="product-card app-card app-card--hover"
            :class="{ 'product-card--out': productStoreStock(p) === 0 }"
            :disabled="productStoreStock(p) === 0"
            @click="addToCart(p)"
          >
            <div class="product-card__top">
              <el-tag v-if="p.is_book" type="primary" effect="light" size="small" round>图书</el-tag>
              <el-tag v-if="productStoreStock(p) === 0" type="danger" size="small">本店缺货</el-tag>
              <el-tag v-else-if="isProductLowStock(p)" type="warning" size="small">低库存</el-tag>
            </div>
            <div class="product-card__name">{{ p.product_name }}</div>
            <div class="product-card__meta text-muted">{{ p.category_name }} · 本店库存 {{ productStoreStock(p) }} {{ p.unit }}</div>
            <div class="product-card__price money">{{ formatCurrency(p.unit_price) }}</div>
          </button>
          <EmptyState
            v-if="!productLoading && !productLoadingMore && !productResults.length"
            icon="Search"
            title="无匹配商品"
            description="没有匹配商品，请调整搜索词"
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
          <el-icon :size="20"><ShoppingCart /></el-icon>
          <span>购物车空空如也，点击左侧商品加入</span>
        </div>

        <ul v-else class="pos-cart__list">
          <li v-for="line in cart" :key="line.product_id" class="pos-cart__line">
            <div class="pos-cart__line-row">
              <span
                class="pos-cart__name"
                :title="`${line.product_name} · 单价 ${formatCurrency(line.unit_price)}`"
              >
                {{ line.product_name }}
              </span>
              <el-input-number
                v-model="line.quantity"
                :min="1"
                :max="line.stock_qty"
                size="small"
                controls-position="right"
                class="pos-cart__qty"
              />
              <span class="money pos-cart__line-total">{{ formatCurrency(line.unit_price * line.quantity) }}</span>
              <el-button
                text
                type="danger"
                class="pos-cart__remove"
                @click="removeLine(line.product_id)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <div v-if="lineErrors[line.product_id]" class="pos-cart__line-error">
              <el-icon><WarningFilled /></el-icon>
              {{ lineErrors[line.product_id] }}
            </div>
          </li>
        </ul>

        <div class="pos-cart__meta">
          <el-form label-width="72px" size="small">
            <el-form-item label="客户">
              <div class="customer-pick">
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
                  <el-option
                    v-for="c in customerOptions"
                    :key="c.customer_id"
                    :label="c.customer_name + (c.phone ? ` · ${c.phone}` : '') + (c.is_member ? ' · 会员' : '')"
                    :value="c.customer_id"
                  />
                </el-select>
                <el-button @click="openCustomerDialog">新增</el-button>
              </div>
              <div v-if="selectedCustomer" class="customer-hint">
                <span>{{ selectedCustomer.is_member ? '会员消费' : '普通客户' }}</span>
                <span v-if="selectedCustomer.is_member">预计积分 +{{ estimatedPoints }}</span>
              </div>
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
              <el-radio-group v-model="form.payment_method" size="small">
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

    <el-dialog v-model="customerDialogVisible" title="快速新增客户" width="520" destroy-on-close>
      <el-form ref="customerFormRef" :model="customerForm" :rules="customerRules" label-width="90px">
        <el-form-item label="姓名" prop="customer_name">
          <el-input v-model="customerForm.customer_name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="customerForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="customerForm.email" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="customerForm.address" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="会员">
          <el-switch v-model="customerForm.make_member" active-text="同步升级" />
        </el-form-item>
        <el-form-item v-if="customerForm.make_member" label="等级">
          <el-radio-group v-model="customerForm.level">
            <el-radio value="bronze">青铜</el-radio>
            <el-radio value="silver">白银</el-radio>
            <el-radio value="gold">黄金</el-radio>
            <el-radio value="platinum">铂金</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customerDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="customerSubmitting" @click="onCustomerSubmit">保存并选中</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/*
  POS 页面在视口内一屏展示：用 calc 锁死总高度（减去 MainLayout 顶栏 52px +
  app-main padding 60px + PageHeader 约 80px + 栅格 gap 16px），两个 panel
  各自独立内部滚动，不再触发 app-main 外层滚动。
*/
.pos-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(340px, 1fr);
  gap: 12px;
  height: calc(100vh - 210px);
  min-height: 420px;
}

.pos-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow: hidden;
  padding: 12px;
}

.pos-products__head {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.pos-products__hint {
  flex-shrink: 0;
  font-size: 12px;
  line-height: 1.4;
}

.pos-products__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 8px;
  align-content: flex-start;
  overflow-y: auto;
  flex: 1 1 auto;
  min-height: 0;
  padding-right: 4px;
}

.product-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  cursor: pointer;
  text-align: left;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius);
  background: var(--app-surface-solid);
  transition: border-color 0.15s ease, background 0.15s ease;
}

.product-card:hover:not(:disabled) {
  border-color: var(--brand);
  background: var(--app-surface-alt);
}

.product-card:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.product-card--out {
  background: var(--app-surface-alt);
}

.product-card__top {
  display: flex;
  gap: 4px;
  min-height: 0;
  align-items: center;
}

.product-card__top:empty {
  display: none;
}

.product-card__name {
  font-weight: 600;
  font-size: 13px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-card__meta {
  font-size: 11px;
  line-height: 1.3;
}

.product-card__price {
  font-weight: 700;
  font-size: 14px;
  color: var(--brand);
  margin-top: 2px;
}

.pos-cart__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.pos-cart__empty {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 12px;
  border: 1px dashed var(--app-border-strong);
  border-radius: var(--app-radius);
  color: var(--app-text-muted);
  font-size: 13px;
  background: var(--app-surface-alt);
}

.pos-cart__list {
  list-style: none;
  margin: 0;
  padding: 0 4px 0 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1 1 auto;
  overflow-y: auto;
  min-height: 0;
}

/* 单行紧凑的购物车条目：名称(省略号) | 数量 | 小计 | 删除 */
.pos-cart__line {
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius);
  padding: 4px 8px;
  background: var(--app-surface-alt);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.pos-cart__line-row {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.pos-cart__name {
  flex: 1 1 auto;
  min-width: 0;
  font-weight: 500;
  font-size: 13px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.pos-cart__qty {
  flex-shrink: 0;
  width: 90px;
}

.pos-cart__line-total {
  flex-shrink: 0;
  font-weight: 600;
  color: var(--brand);
  min-width: 72px;
  text-align: right;
  font-size: 13px;
}

.pos-cart__remove {
  flex-shrink: 0;
  padding: 2px 4px !important;
  min-height: auto !important;
}

.pos-cart__line-error {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--danger);
  padding-left: 2px;
}

.pos-cart__totals {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 8px;
  border-top: 1px dashed var(--app-border);
  flex-shrink: 0;
}

.pos-cart__total-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.pos-cart__total-row--final {
  font-size: 16px;
  font-weight: 700;
  color: var(--brand);
}

.pos-cart__meta {
  flex-shrink: 0;
}

.pos-cart__meta :deep(.el-form-item) {
  margin-bottom: 8px;
}

.pos-cart__meta :deep(.el-form-item__label) {
  padding-right: 8px;
}

.customer-pick {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  width: 100%;
}

.customer-hint {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  margin-top: 4px;
  color: var(--app-text-muted);
  font-size: 12px;
}

.pos-cart__error {
  flex-shrink: 0;
}

.pos-cart .el-button--large {
  flex-shrink: 0;
}

/*
  宽屏（>1100px）：两栏并排，整个页面锁死一屏，每个面板内部滚动。
  窄屏 / 竖屏：改回单列瀑布布局，让页面自然滚动，各列表只做高度上限。
*/
@media (max-width: 1100px) {
  .pos-layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: 0;
  }

  .pos-panel {
    height: auto;
    overflow: visible;
  }

  .pos-products__grid {
    max-height: 48vh;
  }

  .pos-cart__list {
    max-height: 40vh;
  }
}

/* 矮屏（例如 13 寸笔记本竖排 / 横屏但分辨率小）：放宽高度限制，优先让内容可见 */
@media (max-height: 680px) {
  .pos-layout {
    height: auto;
    min-height: 0;
  }

  .pos-panel {
    height: auto;
    overflow: visible;
  }

  .pos-products__grid {
    max-height: 44vh;
  }

  .pos-cart__list {
    max-height: 36vh;
  }
}
</style>
