import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as apiLogin, refresh as apiRefresh, logout as apiLogout, fetchMe } from '@/api/auth'
import type { AuthUser, Role, TokenPair, User } from '@/api/types'

const STORAGE_KEY = 'bookstore.auth.v1'

interface PersistedAuth {
  accessToken: string | null
  refreshToken: string | null
  user: AuthUser | null
}

function loadPersisted(): PersistedAuth {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { accessToken: null, refreshToken: null, user: null }
    const parsed = JSON.parse(raw) as PersistedAuth
    return {
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      user: parsed.user ?? null,
    }
  } catch {
    return { accessToken: null, refreshToken: null, user: null }
  }
}

export const useAuthStore = defineStore('auth', () => {
  const persisted = loadPersisted()
  const accessToken = ref<string | null>(persisted.accessToken)
  const refreshToken = ref<string | null>(persisted.refreshToken)
  const user = ref<AuthUser | null>(persisted.user)
  const profile = ref<User | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const role = computed<Role | null>(() => user.value?.role ?? null)

  function persist() {
    const payload: PersistedAuth = {
      accessToken: accessToken.value,
      refreshToken: refreshToken.value,
      user: user.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  }

  function setTokens(tokens: TokenPair) {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    user.value = tokens.user
    persist()
  }

  async function login(username: string, password: string) {
    const tokens = await apiLogin(username, password)
    setTokens(tokens)
    return tokens
  }

  async function refresh(): Promise<string> {
    if (!refreshToken.value) throw new Error('No refresh token')
    const tokens = await apiRefresh(refreshToken.value)
    setTokens(tokens)
    return tokens.access_token
  }

  async function loadProfile() {
    if (!accessToken.value) return null
    const me = await fetchMe()
    profile.value = me
    // sync role/display_name in case admin updated them elsewhere
    user.value = {
      id: me.id,
      username: me.username,
      role: me.role,
      display_name: me.display_name || me.username,
    }
    persist()
    return me
  }

  function clear() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    profile.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  async function logout() {
    const token = refreshToken.value
    clear()
    if (token) {
      try {
        await apiLogout(token)
      } catch {
        /* 本地已清，忽略服务端错误 */
      }
    }
  }

  function hasAnyRole(roles: Role[] | undefined | null): boolean {
    if (!roles || roles.length === 0) return true
    return !!role.value && roles.includes(role.value)
  }

  return {
    accessToken,
    refreshToken,
    user,
    profile,
    isAuthenticated,
    role,
    login,
    refresh,
    logout,
    clear,
    loadProfile,
    hasAnyRole,
  }
})
