<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import router from '@/router'
import type { RouteRecordRaw } from 'vue-router'

const auth = useAuthStore()
const ui = useUiStore()
const route = useRoute()
const routerInst = useRouter()
const { sidebarCollapsed, isDark, density } = storeToRefs(ui)

interface MenuItem {
  path: string
  title: string
  icon?: string
  group: string
  order: number
}

function flattenRoutes(records: RouteRecordRaw[], prefix = ''): MenuItem[] {
  const items: MenuItem[] = []
  records.forEach((record) => {
    const fullPath = record.path.startsWith('/')
      ? record.path
      : `${prefix.replace(/\/$/, '')}/${record.path}`.replace(/\/+/, '/')
    if (record.children?.length) {
      items.push(...flattenRoutes(record.children, fullPath))
    }
    if (
      record.meta?.hidden ||
      !record.meta?.title ||
      !record.meta?.roles ||
      record.path.includes(':')
    ) {
      return
    }
    if (!auth.hasAnyRole(record.meta.roles)) return
    items.push({
      path: fullPath.startsWith('/') ? fullPath : `/${fullPath}`,
      title: record.meta.title,
      icon: record.meta.icon,
      group: record.meta.menuGroup || '概览',
      order: record.meta.order ?? 0,
    })
  })
  return items
}

const menuGroups = computed(() => {
  const flat = flattenRoutes(routerInst.options.routes as RouteRecordRaw[])
  flat.sort((a, b) => a.order - b.order)
  const grouped = new Map<string, MenuItem[]>()
  flat.forEach((item) => {
    if (!grouped.has(item.group)) grouped.set(item.group, [])
    grouped.get(item.group)!.push(item)
  })
  const orderedGroups = ['概览', '交易', '商品', '客户', '组织', '系统']
  const result: Array<{ name: string; items: MenuItem[] }> = []
  orderedGroups.forEach((g) => {
    if (grouped.has(g)) result.push({ name: g, items: grouped.get(g)! })
  })
  grouped.forEach((items, name) => {
    if (!orderedGroups.includes(name)) result.push({ name, items })
  })
  return result
})

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const segments = route.matched.filter((m) => m.meta?.title)
  return segments.map((m) => ({
    title: m.meta.title as string,
    path: m.path,
  }))
})

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '确认', {
      type: 'warning',
      confirmButtonText: '退出',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  await auth.logout()
  router.replace({ path: '/login' })
}

function handleUserMenu(command: string) {
  if (command === 'logout') return handleLogout()
  if (command === 'toggle-theme') return ui.toggleTheme()
  if (command === 'toggle-density') {
    ui.density = ui.density === 'compact' ? 'comfortable' : ui.density === 'comfortable' ? 'cozy' : 'compact'
  }
}

onMounted(() => {
  if (auth.isAuthenticated && !auth.profile) {
    auth.loadProfile().catch(() => undefined)
  }
})

const densityLabel = computed(() => ({
  compact: '紧凑',
  comfortable: '舒适',
  cozy: '宽松',
}[density.value]))

const roleLabel = computed(() => ({
  admin: '管理员',
  operator: '操作员',
  viewer: '查询用户',
}[auth.user?.role || 'viewer'] || '未知'))

const userInitial = computed(() => {
  const n = auth.user?.display_name || auth.user?.username || 'U'
  return n.slice(0, 1).toUpperCase()
})
</script>

<template>
  <el-container class="app-shell">
    <el-aside :width="sidebarCollapsed ? 'var(--sidebar-collapsed-width)' : 'var(--sidebar-width)'" class="app-sidebar">
      <div class="brand" :class="{ 'brand--collapsed': sidebarCollapsed }">
        <div class="brand__mark">
          <el-icon :size="22"><Reading /></el-icon>
        </div>
        <transition name="fade">
          <div v-if="!sidebarCollapsed" class="brand__text">
            <div class="brand__name">Bookstore</div>
            <div class="brand__sub">网上综合书店</div>
          </div>
        </transition>
      </div>

      <nav class="app-nav">
        <template v-for="group in menuGroups" :key="group.name">
          <div v-if="!sidebarCollapsed" class="app-nav__group">{{ group.name }}</div>
          <el-menu
            :default-active="activeMenu"
            :collapse="sidebarCollapsed"
            :unique-opened="false"
            router
            class="app-menu"
          >
            <el-menu-item v-for="item in group.items" :key="item.path" :index="item.path">
              <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
              <template #title>{{ item.title }}</template>
            </el-menu-item>
          </el-menu>
        </template>
      </nav>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="app-header__left">
          <el-button text circle @click="ui.toggleSidebar()">
            <el-icon :size="18"><component :is="sidebarCollapsed ? 'Expand' : 'Fold'" /></el-icon>
          </el-button>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="crumb in breadcrumbs" :key="crumb.path" :to="{ path: crumb.path }">
              {{ crumb.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="app-header__right">
          <el-tooltip :content="isDark ? '切换浅色主题' : '切换深色主题'" placement="bottom">
            <el-button text circle @click="ui.toggleTheme()">
              <el-icon :size="18"><component :is="isDark ? 'Sunny' : 'Moon'" /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip :content="`当前密度：${densityLabel}`" placement="bottom">
            <el-button text circle @click="handleUserMenu('toggle-density')">
              <el-icon :size="18"><Grid /></el-icon>
            </el-button>
          </el-tooltip>
          <el-dropdown trigger="click" @command="handleUserMenu">
            <div class="user-chip">
              <div class="user-chip__avatar">{{ userInitial }}</div>
              <div class="user-chip__meta">
                <div class="user-chip__name">{{ auth.user?.display_name || auth.user?.username }}</div>
                <div class="user-chip__role">{{ roleLabel }}</div>
              </div>
              <el-icon :size="14"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <span class="text-muted">账号：{{ auth.user?.username }}</span>
                </el-dropdown-item>
                <el-dropdown-item command="toggle-theme">
                  <el-icon><component :is="isDark ? 'Sunny' : 'Moon'" /></el-icon>
                  切换{{ isDark ? '浅色' : '深色' }}主题
                </el-dropdown-item>
                <el-dropdown-item command="toggle-density">
                  <el-icon><Grid /></el-icon>
                  切换密度（当前：{{ densityLabel }}）
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <RouterView v-slot="{ Component, route: r }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="r.fullPath" />
          </transition>
        </RouterView>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--app-bg);
}

.app-sidebar {
  background: var(--app-surface);
  border-right: 1px solid var(--app-border);
  padding: 12px 0;
  transition: width 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: hidden;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 18px 8px;
}

.brand--collapsed {
  padding: 4px 12px 8px;
  justify-content: center;
}

.brand__mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  color: #fff;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px -12px color-mix(in srgb, var(--brand) 70%, transparent);
}

.brand__name {
  font-weight: 700;
  letter-spacing: -0.01em;
  font-size: 15px;
}

.brand__sub {
  font-size: 11px;
  color: var(--app-text-muted);
}

.app-nav {
  flex: 1 1 auto;
  overflow-y: auto;
  padding: 0 0 16px;
}

.app-nav__group {
  padding: 14px 20px 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--app-text-muted);
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: var(--header-height);
  padding: 0 20px;
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
}

.app-header__left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-header__right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 10px 4px 4px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.user-chip:hover {
  background: var(--app-surface-alt);
}

.user-chip__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  color: #fff;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.user-chip__meta {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.user-chip__name {
  font-weight: 600;
  font-size: 13px;
}

.user-chip__role {
  font-size: 11px;
  color: var(--app-text-muted);
}

.app-main {
  padding: 20px 24px 40px;
}
</style>
