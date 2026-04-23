<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/api/types'

const props = defineProps<{
  roles: Role | Role[]
}>()

const auth = useAuthStore()
const visible = computed(() => {
  const roles = Array.isArray(props.roles) ? props.roles : [props.roles]
  return !!auth.role && roles.includes(auth.role)
})
</script>

<template>
  <template v-if="visible">
    <slot />
  </template>
</template>
