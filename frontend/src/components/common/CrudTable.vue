<script setup lang="ts" generic="T extends Record<string, any>">
import { computed } from 'vue'
import EmptyState from './EmptyState.vue'

interface Props<Row> {
  rows: Row[]
  loading?: boolean
  total?: number
  page?: number
  pageSize?: number
  rowKey?: string
  emptyTitle?: string
  emptyDescription?: string
  emptyIcon?: string
  stripe?: boolean
  size?: 'large' | 'default' | 'small'
  showPagination?: boolean
}

const props = withDefaults(defineProps<Props<T>>(), {
  loading: false,
  total: 0,
  page: 1,
  pageSize: 20,
  rowKey: 'id',
  stripe: true,
  size: 'default',
  showPagination: true,
})

const emit = defineEmits<{
  (e: 'page-change', page: number): void
  (e: 'size-change', size: number): void
  (e: 'row-click', row: T): void
}>()

const effectiveTotal = computed(() => props.total ?? props.rows.length)
const hasRows = computed(() => (props.rows?.length ?? 0) > 0)
</script>

<template>
  <div class="crud-table">
    <el-table
      v-if="hasRows || loading"
      v-loading="loading"
      :data="rows"
      :row-key="rowKey as any"
      :stripe="stripe"
      :size="size"
      border
      style="width: 100%"
      @row-click="(row: T) => emit('row-click', row)"
    >
      <slot />
    </el-table>
    <EmptyState
      v-else
      :title="emptyTitle || '暂无数据'"
      :description="emptyDescription || '试着调整筛选条件或先去新增一条数据'"
      :icon="emptyIcon || 'Box'"
    >
      <slot name="empty-extra" />
    </EmptyState>

    <div v-if="showPagination && effectiveTotal > 0" class="crud-table__pagination">
      <el-pagination
        background
        layout="total, sizes, prev, pager, next, jumper"
        :total="effectiveTotal"
        :current-page="page"
        :page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        @current-change="(p: number) => emit('page-change', p)"
        @size-change="(s: number) => emit('size-change', s)"
      />
    </div>
  </div>
</template>

<style scoped>
.crud-table {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--app-surface);
  border-radius: var(--app-radius);
  border: 1px solid var(--app-border);
  padding: 16px;
}

.crud-table__pagination {
  display: flex;
  justify-content: flex-end;
}
</style>
