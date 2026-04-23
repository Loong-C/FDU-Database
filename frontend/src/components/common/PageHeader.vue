<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<template>
  <header class="page-header">
    <div>
      <h1 class="page-header__title">{{ title }}</h1>
      <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
    </div>
    <div class="page-header__extra">
      <slot name="extra" />
    </div>
  </header>
</template>

<style scoped>
.page-header__extra {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
