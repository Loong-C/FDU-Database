import type { Directive, DirectiveBinding } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/api/types'

// v-perm="'admin'" 或 v-perm="['admin','operator']"
// 若当前角色不在允许集合中则从 DOM 中移除元素。
export const permissionDirective: Directive<HTMLElement, Role | Role[]> = {
  mounted(el, binding: DirectiveBinding<Role | Role[]>) {
    apply(el, binding.value)
  },
  updated(el, binding: DirectiveBinding<Role | Role[]>) {
    apply(el, binding.value)
  },
}

function apply(el: HTMLElement, value: Role | Role[]) {
  const auth = useAuthStore()
  const roles = Array.isArray(value) ? value : [value]
  const ok = !!auth.role && roles.includes(auth.role)
  if (!ok) {
    el.style.display = 'none'
  } else {
    el.style.display = ''
  }
}
