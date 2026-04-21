<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDictsStore } from '@/stores/dicts'
import type { SupplierLink } from '@/api/types'

const props = defineProps<{ modelValue: SupplierLink[] }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: SupplierLink[]): void }>()

const dicts = useDictsStore()
const supplierOptions = computed(() => dicts.suppliers)

onMounted(() => {
  dicts.ensureSuppliers().catch(() => undefined)
})

const rows = ref<SupplierLink[]>([])

watch(
  () => props.modelValue,
  (val) => {
    rows.value = (val || []).map((x) => ({ ...x }))
  },
  { immediate: true, deep: true },
)

function emitChange() {
  emit('update:modelValue', rows.value.map((r) => ({ ...r })))
}

function addRow() {
  rows.value.push({
    supplier_id: 0,
    supply_price: '0',
    min_order_qty: 1,
    is_primary: rows.value.length === 0,
  })
  emitChange()
}

function removeRow(index: number) {
  rows.value.splice(index, 1)
  emitChange()
}

function onPrimaryChange(index: number) {
  rows.value.forEach((r, i) => {
    r.is_primary = i === index ? !!r.is_primary : false
  })
  emitChange()
}
</script>

<template>
  <div class="sup-links">
    <div class="sup-links__head">
      <span class="section-title">供应商关联</span>
      <el-button text type="primary" @click="addRow">
        <el-icon><Plus /></el-icon>添加供应商
      </el-button>
    </div>
    <el-table :data="rows" size="small" border empty-text="尚未配置供应商">
      <el-table-column label="供应商" min-width="220">
        <template #default="{ $index, row }">
          <el-select
            v-model="row.supplier_id"
            placeholder="选择供应商"
            filterable
            style="width: 100%"
            @change="emitChange"
          >
            <el-option
              v-for="s in supplierOptions"
              :key="s.supplier_id"
              :label="s.supplier_name"
              :value="s.supplier_id"
            />
          </el-select>
          <span v-if="false">{{ $index }}</span>
        </template>
      </el-table-column>
      <el-table-column label="供货价" width="130">
        <template #default="{ row }">
          <el-input-number v-model="row.supply_price" :min="0" :precision="2" :step="0.5" style="width: 100%" @change="emitChange" />
        </template>
      </el-table-column>
      <el-table-column label="起订量" width="110">
        <template #default="{ row }">
          <el-input-number v-model="row.min_order_qty" :min="1" :step="1" style="width: 100%" @change="emitChange" />
        </template>
      </el-table-column>
      <el-table-column label="主供" width="80" align="center">
        <template #default="{ row, $index }">
          <el-checkbox v-model="row.is_primary" @change="onPrimaryChange($index)" />
        </template>
      </el-table-column>
      <el-table-column label="" width="60" align="center">
        <template #default="{ $index }">
          <el-button text type="danger" @click="removeRow($index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.sup-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sup-links__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
