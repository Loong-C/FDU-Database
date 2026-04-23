<script setup lang="ts">
defineProps<{ loading?: boolean }>()
defineEmits<{
  (e: 'submit'): void
  (e: 'reset'): void
}>()
</script>

<template>
  <form class="filter-bar" @submit.prevent="$emit('submit')">
    <div class="filter-bar__fields">
      <slot />
    </div>
    <div class="filter-bar__actions">
      <el-button type="primary" :loading="loading" native-type="submit">
        <el-icon style="margin-right: 4px"><Search /></el-icon>
        查询
      </el-button>
      <el-button @click="$emit('reset')">重置</el-button>
      <slot name="extra" />
    </div>
  </form>
</template>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  flex-wrap: wrap;
  justify-content: space-between;
}

.filter-bar__fields {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
  flex: 1 1 auto;
}

.filter-bar__fields :deep(.el-form-item) {
  margin: 0;
}

.filter-bar__actions {
  display: flex;
  gap: 8px;
}
</style>
