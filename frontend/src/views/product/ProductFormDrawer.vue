<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import SupplierLinksEditor from '@/components/common/SupplierLinksEditor.vue'
import { useDictsStore } from '@/stores/dicts'
import { createProduct, getProduct, updateProduct, type ProductWritePayload } from '@/api/products'
import type { InventoryRow, Product, ProductStatus, SupplierLink } from '@/api/types'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'
import { categoryDescendants, categoryOptionLabel } from '@/utils/categories'

const props = defineProps<{
  modelValue: boolean
  productId?: number | null
}>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'success'): void
}>()

const dicts = useDictsStore()

const formRef = ref<FormInstance | null>(null)
const submitting = ref(false)
const loading = ref(false)

const form = reactive<{
  product_name: string
  category_id: number | null
  unit: string
  unit_price: number | string
  cost_price: number | string
  store_id: number | null
  stock_qty: number
  safety_stock_qty: number
  barcode: string
  status: ProductStatus
  supplier_links: SupplierLink[]
}>({
  product_name: '',
  category_id: null,
  unit: '件',
  unit_price: 0,
  cost_price: 0,
  store_id: null,
  stock_qty: 0,
  safety_stock_qty: 0,
  barcode: '',
  status: 'onsale',
  supplier_links: [],
})
const inventoryRows = ref<InventoryRow[]>([])
const generalCategories = computed(() => categoryDescendants(dicts.categories, '办公文具'))

const rules: FormRules = {
  product_name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  store_id: [{ required: true, message: '请选择库存门店', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
}

const visible = computed<boolean>({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const isEdit = computed(() => !!props.productId)

watch(
  () => props.modelValue,
  async (v) => {
    if (!v) return
    await Promise.all([dicts.ensureCategories(), dicts.ensureSuppliers(), dicts.ensureStores()])
    if (props.productId) {
      await loadDetail(props.productId)
    } else {
      reset()
    }
  },
  { immediate: false },
)

function reset() {
  Object.assign(form, {
    product_name: '',
    category_id: null,
    unit: '件',
    unit_price: 0,
    cost_price: 0,
    store_id: dicts.stores[0]?.store_id ?? null,
    stock_qty: 0,
    safety_stock_qty: 0,
    barcode: '',
    status: 'onsale' as ProductStatus,
    supplier_links: [] as SupplierLink[],
  })
  inventoryRows.value = []
}

async function loadDetail(id: number) {
  loading.value = true
  try {
    const detail = await getProduct(id)
    applyDetail(detail)
  } finally {
    loading.value = false
  }
}

function applyDetail(detail: Product) {
  form.product_name = detail.product_name
  form.category_id = detail.category_id
  form.unit = detail.unit
  form.unit_price = Number(detail.unit_price)
  form.cost_price = Number(detail.cost_price)
  inventoryRows.value = detail.inventory || []
  const firstInventory = inventoryRows.value[0] || null
  form.store_id = firstInventory?.store_id ?? dicts.stores[0]?.store_id ?? null
  form.stock_qty = firstInventory?.stock_qty ?? 0
  form.safety_stock_qty = firstInventory?.safety_stock_qty ?? 0
  form.barcode = detail.barcode ?? ''
  form.status = detail.status
  form.supplier_links = (detail.supplier_links || []).map((x) => ({
    supplier_id: x.supplier_id,
    supply_price: Number(x.supply_price),
    min_order_qty: x.min_order_qty ?? null,
    is_primary: !!x.is_primary,
  }))
}

function onStoreChange(storeId: number | string | null) {
  const numericStoreId = storeId === null ? null : Number(storeId)
  const row = inventoryRows.value.find((item) => item.store_id === numericStoreId)
  form.stock_qty = row?.stock_qty ?? 0
  form.safety_stock_qty = row?.safety_stock_qty ?? 0
}

onMounted(() => {
  if (props.modelValue) {
    dicts.ensureCategories()
    dicts.ensureSuppliers()
    dicts.ensureStores()
    if (props.productId) loadDetail(props.productId)
  }
})

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  const payload: ProductWritePayload = {
    product_name: form.product_name,
    category_id: form.category_id as number,
    unit: form.unit,
    unit_price: Number(form.unit_price),
    cost_price: Number(form.cost_price),
    store_id: form.store_id as number,
    stock_qty: Number(form.stock_qty),
    safety_stock_qty: Number(form.safety_stock_qty),
    barcode: form.barcode || null,
    status: form.status,
    supplier_links: form.supplier_links.filter((x) => x.supplier_id).map((x) => ({
      supplier_id: x.supplier_id,
      supply_price: Number(x.supply_price),
      min_order_qty: x.min_order_qty ?? null,
      is_primary: !!x.is_primary,
    })),
  }
  submitting.value = true
  try {
    if (isEdit.value && props.productId) {
      await updateProduct(props.productId, payload)
      ElMessage.success('商品已更新')
    } else {
      await createProduct(payload)
      ElMessage.success('商品已新增')
    }
    visible.value = false
    emit('success')
  } catch (error) {
    if (error instanceof ApiError && error.isValidation) applyServerErrors(formRef.value, error)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <el-drawer v-model="visible" :title="isEdit ? '编辑商品' : '新增商品'" size="640px" destroy-on-close>
    <el-skeleton v-if="loading" :rows="6" animated />
    <el-form v-else ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-form-item label="名称" prop="product_name">
        <el-input v-model="form.product_name" />
      </el-form-item>
      <el-form-item label="分类" prop="category_id">
        <el-select v-model="form.category_id" filterable placeholder="请选择分类" style="width: 100%">
          <el-option
            v-for="c in generalCategories"
            :key="c.category_id"
            :label="categoryOptionLabel(c, dicts.categories, '办公文具')"
            :value="c.category_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="单位" prop="unit">
        <el-input v-model="form.unit" placeholder="例如：件、本、支" />
      </el-form-item>
      <el-form-item label="售价" prop="unit_price">
        <el-input-number v-model="form.unit_price" :min="0.01" :precision="2" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="成本价">
        <el-input-number v-model="form.cost_price" :min="0" :precision="2" :step="1" style="width: 100%" />
      </el-form-item>
      <el-divider content-position="left">门店库存</el-divider>
      <el-form-item label="库存门店" prop="store_id">
        <el-select v-model="form.store_id" placeholder="选择门店" style="width: 100%" @change="onStoreChange">
          <el-option v-for="s in dicts.stores" :key="s.store_id" :label="s.store_name" :value="s.store_id" />
        </el-select>
      </el-form-item>
      <el-form-item label="当前库存">
        <el-input-number v-model="form.stock_qty" :min="0" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="安全库存">
        <el-input-number v-model="form.safety_stock_qty" :min="0" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item v-if="isEdit && inventoryRows.length" label="库存明细">
        <el-table :data="inventoryRows" border size="small" style="width: 100%">
          <el-table-column prop="store_name" label="门店" min-width="130" />
          <el-table-column prop="stock_qty" label="库存" width="80" align="right" />
          <el-table-column prop="safety_stock_qty" label="安全线" width="90" align="right" />
        </el-table>
      </el-form-item>
      <el-form-item label="条码">
        <el-input v-model="form.barcode" placeholder="选填，唯一" />
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio value="onsale">在售</el-radio>
          <el-radio value="offsale">下架</el-radio>
          <el-radio value="discontinued">停产</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="">
        <SupplierLinksEditor v-model="form.supplier_links" />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">保存</el-button>
    </template>
  </el-drawer>
</template>
