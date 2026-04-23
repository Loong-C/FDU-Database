import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { Role } from '@/api/types'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    roles?: Role[]
    hidden?: boolean
    menuGroup?: string
    order?: number
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', hidden: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '数据总览', icon: 'Odometer', roles: ['admin', 'operator', 'viewer'], order: 0 },
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/analytics/AnalyticsView.vue'),
        meta: { title: '销售分析', icon: 'TrendCharts', roles: ['admin', 'operator', 'viewer'], order: 1 },
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('@/views/sales/SalesListView.vue'),
        meta: { title: '销售订单', icon: 'Tickets', roles: ['admin', 'operator'], menuGroup: '交易', order: 10 },
      },
      {
        path: 'sales/new',
        name: 'SalesCreate',
        component: () => import('@/views/sales/SalesCreateView.vue'),
        meta: { title: '新开销售单', icon: 'Plus', roles: ['admin', 'operator'], menuGroup: '交易', order: 11 },
      },
      {
        path: 'sales/:id',
        name: 'SalesDetail',
        component: () => import('@/views/sales/SalesDetailView.vue'),
        meta: { title: '销售单详情', roles: ['admin', 'operator'], hidden: true },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/ProductListView.vue'),
        meta: { title: '商品管理', icon: 'Goods', roles: ['admin', 'operator'], menuGroup: '商品', order: 20 },
      },
      {
        path: 'books',
        name: 'Books',
        component: () => import('@/views/book/BookListView.vue'),
        meta: { title: '图书管理', icon: 'Reading', roles: ['admin', 'operator'], menuGroup: '商品', order: 21 },
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/category/CategoryTreeView.vue'),
        meta: { title: '分类管理', icon: 'Menu', roles: ['admin', 'operator'], menuGroup: '商品', order: 22 },
      },
      {
        path: 'publishers',
        name: 'Publishers',
        component: () => import('@/views/publisher/PublisherListView.vue'),
        meta: { title: '出版社', icon: 'OfficeBuilding', roles: ['admin', 'operator'], menuGroup: '商品', order: 23 },
      },
      {
        path: 'authors',
        name: 'Authors',
        component: () => import('@/views/author/AuthorListView.vue'),
        meta: { title: '作者', icon: 'User', roles: ['admin', 'operator'], menuGroup: '商品', order: 24 },
      },
      {
        path: 'translators',
        name: 'Translators',
        component: () => import('@/views/translator/TranslatorListView.vue'),
        meta: { title: '译者', icon: 'Avatar', roles: ['admin', 'operator'], menuGroup: '商品', order: 25 },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customer/CustomerListView.vue'),
        meta: { title: '客户管理', icon: 'UserFilled', roles: ['admin', 'operator'], menuGroup: '客户', order: 30 },
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('@/views/member/MemberListView.vue'),
        meta: { title: '会员管理', icon: 'Medal', roles: ['admin', 'operator'], menuGroup: '客户', order: 31 },
      },
      {
        path: 'stores',
        name: 'Stores',
        component: () => import('@/views/store/StoreListView.vue'),
        meta: { title: '门店管理', icon: 'Shop', roles: ['admin', 'operator'], menuGroup: '组织', order: 40 },
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/supplier/SupplierListView.vue'),
        meta: { title: '供应商', icon: 'Van', roles: ['admin', 'operator'], menuGroup: '组织', order: 41 },
      },
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('@/views/system/UserListView.vue'),
        meta: { title: '账号管理', icon: 'Lock', roles: ['admin'], menuGroup: '系统', order: 90 },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { hidden: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(_to, _from, saved) {
    return saved || { top: 0 }
  },
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const requiresAuth = to.path !== '/login'

  if (!requiresAuth) {
    if (auth.isAuthenticated) return { path: '/dashboard' }
    return true
  }

  if (!auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  const roles = to.meta.roles
  if (roles && roles.length && !auth.hasAnyRole(roles)) {
    // 对无权限访问的路由，重定向到首页
    return { path: '/dashboard' }
  }

  if (to.meta.title) {
    document.title = `${to.meta.title} · ${import.meta.env.VITE_APP_TITLE || '网上综合书店'}`
  }
  return true
})

export default router
