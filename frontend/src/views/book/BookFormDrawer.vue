<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import SupplierLinksEditor from '@/components/common/SupplierLinksEditor.vue'
import { useDictsStore } from '@/stores/dicts'
import { createBook, getBook, updateBook, type BookWritePayload } from '@/api/books'
import type { Book, ProductStatus, SupplierLink } from '@/api/types'
import { ApiError } from '@/api/http'
import { applyServerErrors } from '@/utils/errors'

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
  stock_qty: number
  barcode: string
  status: ProductStatus
  isbn: string
  publisher_id: number | null
  publish_date: string | null
  edition: string
  language: string
  page_count: number | null
  author_ids: number[]
  translator_ids: number[]
  supplier_links: SupplierLink[]
}>({
  product_name: '',
  category_id: null,
  unit: '本',
  unit_price: 0,
  cost_price: 0,
  stock_qty: 0,
  barcode: '',
  status: 'onsale',
  isbn: '',
  publisher_id: null,
  publish_date: null,
  edition: '',
  language: '中文',
  page_count: null,
  author_ids: [],
  translator_ids: [],
  supplier_links: [],
})

const rules: FormRules = {
  product_name: [{ required: true, message: '请输入图书名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  unit: [{ required: true, message: '请输入单位', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  isbn: [{ required: true, message: '请输入 ISBN', trigger: 'blur' }],
  publisher_id: [{ required: true, message: '请选择出版社', trigger: 'change' }],
  author_ids: [{ required: true, message: '至少选择一位作者', trigger: 'change' }],
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
    await Promise.all([
      dicts.ensureCategories(),
      dicts.ensureSuppliers(),
      dicts.ensurePublishers(),
      dicts.ensureAuthors(),
      dicts.ensureTranslators(),
    ])
    if (props.productId) {
      await loadDetail(props.productId)
    } else {
      reset()
    }
  },
)

function reset() {
  Object.assign(form, {
    product_name: '',
    category_id: null,
    unit: '本',
    unit_price: 0,
    cost_price: 0,
    stock_qty: 0,
    barcode: '',
    status: 'onsale' as ProductStatus,
    isbn: '',
    publisher_id: null,
    publish_date: null,
    edition: '',
    language: '中文',
    page_count: null,
    author_ids: [] as number[],
    translator_ids: [] as number[],
    supplier_links: [] as SupplierLink[],
  })
}

async function loadDetail(id: number) {
  loading.value = true
  try {
    const detail = await getBook(id)
    applyDetail(detail)
  } finally {
    loading.value = false
  }
}

function applyDetail(d: Book) {
  form.product_name = d.product_name
  form.category_id = d.category_id
  form.unit = d.unit
  form.unit_price = Number(d.unit_price)
  form.cost_price = Number(d.cost_price)
  form.stock_qty = d.stock_qty
  form.barcode = d.barcode ?? ''
  form.status = d.status
  form.isbn = d.isbn
  form.publisher_id = d.publisher_id
  form.publish_date = d.publish_date
  form.edition = d.edition ?? ''
  form.language = d.language ?? ''
  form.page_count = d.page_count ?? null
  form.author_ids = d.authors.map((a) => a.author_id)
  form.translator_ids = d.translators.map((t) => t.translator_id)
  form.supplier_links = (d.supplier_links || []).map((x) => ({
    supplier_id: x.supplier_id,
    supply_price: Number(x.supply_price),
    min_order_qty: x.min_order_qty ?? null,
    is_primary: !!x.is_primary,
  }))
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  const payload: BookWritePayload = {
    product_name: form.product_name,
    category_id: form.category_id as number,
    unit: form.unit,
    unit_price: Number(form.unit_price),
    cost_price: Number(form.cost_price),
    stock_qty: Number(form.stock_qty),
    barcode: form.barcode || null,
    status: form.status,
    isbn: form.isbn,
    publisher_id: form.publisher_id as number,
    publish_date: form.publish_date || null,
    edition: form.edition || null,
    language: form.language || null,
    page_count: form.page_count ?? null,
    author_ids: form.author_ids,
    translator_ids: form.translator_ids,
    supplier_links: form.supplier_links
      .filter((x) => x.supplier_id)
      .map((x) => ({
        supplier_id: x.supplier_id,
        supply_price: Number(x.supply_price),
        min_order_qty: x.min_order_qty ?? null,
        is_primary: !!x.is_primary,
      })),
  }

  submitting.value = true
  try {
    if (isEdit.value && props.productId) {
      await updateBook(props.productId, payload)
      ElMessage.success('图书已更新')
    } else {
      await createBook(payload)
      ElMessage.success('图书已新增')
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
  <el-drawer v-model="visible" :title="isEdit ? '编辑图书' : '新增图书'" size="720px" destroy-on-close>
    <el-skeleton v-if="loading" :rows="8" animated />
    <el-form v-else ref="formRef" :model="form" :rules="rules" label-width="90px">
      <el-divider content-position="left">基础信息</el-divider>
      <el-form-item label="图书名称" prop="product_name">
        <el-input v-model="form.product_name" />
      </el-form-item>
      <el-form-item label="ISBN" prop="isbn">
        <el-input v-model="form.isbn" placeholder="例如：9787111000001" />
      </el-form-item>
      <el-form-item label="分类" prop="category_id">
        <el-select v-model="form.category_id" filterable placeholder="请选择" style="width: 100%">
          <el-option
            v-for="c in dicts.categories"
            :key="c.category_id"
            :label="c.parent_category_name ? `${c.parent_category_name} / ${c.category_name}` : c.category_name"
            :value="c.category_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="单位" prop="unit"><el-input v-model="form.unit" /></el-form-item>
      <el-form-item label="售价" prop="unit_price">
        <el-input-number v-model="form.unit_price" :min="0.01" :precision="2" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="成本价">
        <el-input-number v-model="form.cost_price" :min="0" :precision="2" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="库存"><el-input-number v-model="form.stock_qty" :min="0" style="width: 100%" /></el-form-item>
      <el-form-item label="条码"><el-input v-model="form.barcode" /></el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio value="onsale">在售</el-radio>
          <el-radio value="offsale">下架</el-radio>
          <el-radio value="discontinued">停产</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-divider content-position="left">图书属性</el-divider>
      <el-form-item label="出版社" prop="publisher_id">
        <el-select v-model="form.publisher_id" filterable placeholder="请选择出版社" style="width: 100%">
          <el-option
            v-for="p in dicts.publishers"
            :key="p.publisher_id"
            :label="p.publisher_name"
            :value="p.publisher_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="出版日期">
        <el-date-picker v-model="form.publish_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
      </el-form-item>
      <el-form-item label="版次"><el-input v-model="form.edition" placeholder="例如：第 1 版" /></el-form-item>
      <el-form-item label="语言"><el-input v-model="form.language" /></el-form-item>
      <el-form-item label="页数">
        <el-input-number v-model="form.page_count" :min="1" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="作者" prop="author_ids">
        <el-select v-model="form.author_ids" multiple filterable placeholder="选择作者" style="width: 100%">
          <el-option
            v-for="a in dicts.authors"
            :key="a.author_id"
            :label="a.country ? `${a.author_name}（${a.country}）` : a.author_name"
            :value="a.author_id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="译者">
        <el-select v-model="form.translator_ids" multiple filterable placeholder="选择译者（可空）" style="width: 100%">
          <el-option
            v-for="t in dicts.translators"
            :key="t.translator_id"
            :label="t.country ? `${t.translator_name}（${t.country}）` : t.translator_name"
            :value="t.translator_id"
          />
        </el-select>
      </el-form-item>

      <el-divider content-position="left">供货关系</el-divider>
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
