import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'

type Theme = 'light' | 'dark'
type Density = 'compact' | 'comfortable' | 'cozy'

const THEME_KEY = 'bookstore.ui.theme'
const DENSITY_KEY = 'bookstore.ui.density'
const SIDEBAR_KEY = 'bookstore.ui.sidebar'

export const useUiStore = defineStore('ui', () => {
  const theme = ref<Theme>((localStorage.getItem(THEME_KEY) as Theme) || 'light')
  const density = ref<Density>((localStorage.getItem(DENSITY_KEY) as Density) || 'comfortable')
  const sidebarCollapsed = ref<boolean>(localStorage.getItem(SIDEBAR_KEY) === '1')

  function applyTheme(value: Theme) {
    const html = document.documentElement
    if (value === 'dark') html.classList.add('dark')
    else html.classList.remove('dark')
    html.setAttribute('data-theme', value)
  }

  function applyDensity(value: Density) {
    document.documentElement.setAttribute('data-density', value)
  }

  applyTheme(theme.value)
  applyDensity(density.value)

  watch(theme, (v) => {
    localStorage.setItem(THEME_KEY, v)
    applyTheme(v)
  })

  watch(density, (v) => {
    localStorage.setItem(DENSITY_KEY, v)
    applyDensity(v)
  })

  watch(sidebarCollapsed, (v) => {
    localStorage.setItem(SIDEBAR_KEY, v ? '1' : '0')
  })

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const isDark = computed(() => theme.value === 'dark')

  return { theme, density, sidebarCollapsed, isDark, toggleTheme, toggleSidebar }
})
