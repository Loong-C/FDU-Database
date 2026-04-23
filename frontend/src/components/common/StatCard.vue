<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  label: string
  value: string | number
  hint?: string
  icon?: string
  tone?: 'brand' | 'success' | 'warning' | 'danger' | 'accent'
  loading?: boolean
}>(), {
  tone: 'brand',
  loading: false,
})

const toneColor = computed(() => {
  switch (props.tone) {
    case 'success':
      return 'var(--success)'
    case 'warning':
      return 'var(--warning)'
    case 'danger':
      return 'var(--danger)'
    case 'accent':
      return 'var(--accent)'
    case 'brand':
    default:
      return 'var(--brand)'
  }
})
</script>

<template>
  <article class="stat-card app-card app-card--hover">
    <div class="stat-card__top">
      <span class="stat-card__label">{{ label }}</span>
      <span v-if="icon" class="stat-card__icon" :style="{ color: toneColor, background: `color-mix(in srgb, ${toneColor} 12%, transparent)` }">
        <el-icon :size="18"><component :is="icon" /></el-icon>
      </span>
    </div>
    <div class="stat-card__value money" :style="{ color: toneColor }">
      <el-skeleton v-if="loading" animated>
        <template #template>
          <el-skeleton-item variant="h1" style="width: 60%; height: 30px" />
        </template>
      </el-skeleton>
      <span v-else>{{ value }}</span>
    </div>
    <div v-if="hint || $slots.hint" class="stat-card__hint text-muted">
      <slot name="hint">{{ hint }}</slot>
    </div>
  </article>
</template>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 120px;
  position: relative;
  overflow: hidden;
}

.stat-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: var(--app-text-muted);
}

.stat-card__label {
  font-weight: 500;
  letter-spacing: 0.02em;
}

.stat-card__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.stat-card__value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.stat-card__hint {
  font-size: 12px;
}
</style>
