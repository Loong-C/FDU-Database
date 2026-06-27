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
    redirect: '/welcome',
    children: [
      {
        path: 'welcome',
        name: 'Welcome',
        component: () => import('@/views/welcome/WelcomeView.vue'),
        meta: { title: '欢迎页', icon: 'House', roles: ['admin', 'operator', 'viewer'], menuGroup: '首页', order: -10 },
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '经营总览', icon: 'Odometer', roles: ['admin', 'viewer'], menuGroup: '经营', order: 0 },
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/analytics/AnalyticsView.vue'),
        meta: { title: '统计分析', icon: 'TrendCharts', roles: ['admin', 'viewer'], menuGroup: '经营', order: 1 },
      },
      {
        path: 'sales',
        name: 'Sales',
        component: () => import('@/views/sales/SalesListView.vue'),
        meta: { title: '销售订单', icon: 'Tickets', roles: ['admin', 'operator'], menuGroup: '门店销售', order: 10 },
      },
      {
        path: 'sales/new',
        name: 'SalesCreate',
        component: () => import('@/views/sales/SalesCreateView.vue'),
        meta: { title: '新开销售单', icon: 'Plus', roles: ['admin', 'operator'], menuGroup: '门店销售', order: 11 },
      },
      {
        path: 'sales/:id',
        name: 'SalesDetail',
        component: () => import('@/views/sales/SalesDetailView.vue'),
        meta: { title: '销售单详情', roles: ['admin', 'operator'], hidden: true },
      },
      {
        path: 'purchase-orders',
        name: 'PurchaseOrders',
        component: () => import('@/views/procurement/PurchaseOrderListView.vue'),
        meta: { title: '采购单', icon: 'Van', roles: ['admin', 'operator'], menuGroup: '采购入库', order: 12 },
      },
      {
        path: 'stock-ins',
        name: 'StockIns',
        component: () => import('@/views/procurement/StockInListView.vue'),
        meta: { title: '入库单', icon: 'Box', roles: ['admin', 'operator'], menuGroup: '采购入库', order: 13 },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/product/ProductListView.vue'),
        meta: { title: '商品中心', icon: 'Goods', roles: ['admin'], menuGroup: '商品中心', order: 20 },
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/category/CategoryTreeView.vue'),
        meta: { title: '分类体系', icon: 'Menu', roles: ['admin'], menuGroup: '商品中心', order: 22 },
      },
      {
        path: 'publishers',
        name: 'Publishers',
        component: () => import('@/views/publisher/PublisherListView.vue'),
        meta: { title: '出版社', icon: 'OfficeBuilding', roles: ['admin'], menuGroup: '商品中心', order: 23 },
      },
      {
        path: 'authors',
        name: 'Authors',
        component: () => import('@/views/author/AuthorListView.vue'),
        meta: { title: '作者', icon: 'User', roles: ['admin'], menuGroup: '商品中心', order: 24 },
      },
      {
        path: 'translators',
        name: 'Translators',
        component: () => import('@/views/translator/TranslatorListView.vue'),
        meta: { title: '译者', icon: 'Avatar', roles: ['admin'], menuGroup: '商品中心', order: 25 },
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/InventoryListView.vue'),
        meta: { title: '门店库存', icon: 'Box', roles: ['admin', 'operator'], menuGroup: '库存补货', order: 26 },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customer/CustomerListView.vue'),
        meta: { title: '客户管理', icon: 'UserFilled', roles: ['admin', 'operator'], menuGroup: '客户会员', order: 30 },
      },
      {
        path: 'members',
        name: 'Members',
        component: () => import('@/views/member/MemberListView.vue'),
        meta: { title: '会员管理', icon: 'Medal', roles: ['admin', 'operator'], menuGroup: '客户会员', order: 31 },
      },
      {
        path: 'stores',
        name: 'Stores',
        component: () => import('@/views/store/StoreListView.vue'),
        meta: { title: '门店管理', icon: 'Shop', roles: ['admin'], menuGroup: '基础资料', order: 40 },
      },
      {
        path: 'suppliers',
        name: 'Suppliers',
        component: () => import('@/views/supplier/SupplierListView.vue'),
        meta: { title: '供应商', icon: 'Van', roles: ['admin'], menuGroup: '基础资料', order: 41 },
      },
      {
        path: 'system/users',
        name: 'Users',
        component: () => import('@/views/system/UserListView.vue'),
        meta: { title: '账号管理', icon: 'Lock', roles: ['admin'], menuGroup: '系统权限', order: 90 },
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
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, saved) {
    return saved || { top: 0 }
  },
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const requiresAuth = to.path !== '/login'

  if (!requiresAuth) {
    if (auth.isAuthenticated) return { path: '/welcome' }
    return true
  }

  if (!auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  const roles = to.meta.roles
  if (roles && roles.length && !auth.hasAnyRole(roles)) {
    return { path: '/welcome' }
  }

  if (to.meta.title) {
    document.title = `${to.meta.title} · ${import.meta.env.VITE_APP_TITLE || '网上综合书店'}`
  }
  return true
})

export default router
