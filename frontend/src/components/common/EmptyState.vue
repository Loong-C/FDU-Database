<script setup lang="ts">
withDefaults(defineProps<{
  title?: string
  description?: string
  icon?: string
}>(), {
  title: '暂无数据',
  description: '试着调整筛选条件或先去新增一条数据',
  icon: 'Box',
})
</script>

<template>
  <div class="empty-state">
    <el-icon :size="44" class="empty-state__icon"><component :is="icon" /></el-icon>
    <h3 class="empty-state__title">{{ title }}</h3>
    <p class="empty-state__desc text-muted">{{ description }}</p>
    <div class="empty-state__extra">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 56px 20px;
  border: 1px dashed var(--app-border-strong);
  border-radius: var(--app-radius);
  background: var(--app-surface-alt);
  color: var(--app-text-muted);
}

.empty-state__icon {
  color: var(--brand);
  opacity: 0.7;
}

.empty-state__title {
  margin: 6px 0 0;
  font-size: 16px;
  color: var(--app-text);
}

.empty-state__desc {
  margin: 0;
  font-size: 13px;
}

.empty-state__extra {
  margin-top: 12px;
}
</style>
