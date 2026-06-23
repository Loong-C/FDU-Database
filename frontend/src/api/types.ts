// 统一响应与分页结构，与后端 common/response.py、common/pagination.py 对齐。

export interface ApiResult<T = unknown> {
  code: number
  message: string
  data: T
  errors?: Record<string, string[] | string> | null
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface PageQuery {
  page?: number
  page_size?: number
  search?: string
  [key: string]: unknown
}

// 业务实体

export type Role = 'admin' | 'operator' | 'viewer'
export type ActiveStatus = 'active' | 'inactive'
export type ProductStatus = 'onsale' | 'offsale' | 'discontinued'
export type MemberLevel = 'bronze' | 'silver' | 'gold' | 'platinum'
export type PaymentMethod = 'cash' | 'card' | 'wechat' | 'alipay' | 'mixed'
export type PurchaseOrderStatus = 'draft' | 'submitted' | 'approved' | 'received' | 'cancelled'
export type StockInStatus = 'pending' | 'approved' | 'rejected'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  display_name: string
  role: Role
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthUser {
  id: number
  username: string
  role: Role
  display_name: string
}

export interface TokenPair {
  access_token: string
  access_expires_at: string
  refresh_token: string
  refresh_expires_at: string
  token_type: 'Bearer'
  user: AuthUser
}

export interface Store {
  store_id: number
  store_name: string
  city: string
  address: string
  phone: string | null
  manager_name: string | null
  created_at: string
}

export interface Supplier {
  supplier_id: number
  supplier_name: string
  contact_name: string | null
  phone: string | null
  email: string | null
  status: ActiveStatus
}

export interface Category {
  category_id: number
  category_name: string
  parent_category_id: number | null
  parent_category_name: string | null
}

export interface Publisher {
  publisher_id: number
  publisher_name: string
  contact_name: string | null
  phone: string | null
  email: string | null
  address: string | null
  country: string | null
  website: string | null
}

export interface Author {
  author_id: number
  author_name: string
  country: string | null
}

export interface Translator {
  translator_id: number
  translator_name: string
  country: string | null
}

export interface SupplierLink {
  supplier_id: number
  supplier_name?: string
  supply_price: string | number
  min_order_qty?: number | null
  is_primary?: boolean
}

export interface InventoryRow {
  store_id: number
  store_name: string
  product_id: number
  product_name: string
  product_status: ProductStatus
  stock_qty: number
  safety_stock_qty: number
  updated_at: string
}

export interface Product {
  product_id: number
  product_name: string
  category_id: number
  category_name: string
  unit: string
  unit_price: string
  cost_price: string
  stock_qty: number
  barcode: string | null
  status: ProductStatus
  created_at: string
  is_book: boolean
  inventory: InventoryRow[]
  supplier_links: SupplierLink[]
}

export interface BookAuthor {
  author_id: number
  author_name: string
  author_order: number | null
}

export interface BookTranslatorItem {
  translator_id: number
  translator_name: string
}

export interface Book {
  product_id: number
  product_name: string
  category_id: number
  category_name: string
  unit: string
  unit_price: string
  cost_price: string
  stock_qty: number
  barcode: string | null
  status: ProductStatus
  created_at: string
  isbn: string
  publisher_id: number
  publisher_name: string
  publish_date: string | null
  edition: string | null
  language: string | null
  page_count: number | null
  authors: BookAuthor[]
  translators: BookTranslatorItem[]
  inventory: InventoryRow[]
  supplier_links: SupplierLink[]
}

export interface Customer {
  customer_id: number
  customer_name: string
  phone: string | null
  email: string | null
  address: string | null
  register_time: string
  status: ActiveStatus
  is_member: boolean
}

export interface Member {
  customer_id: number
  customer_name: string
  phone: string | null
  email: string | null
  address: string | null
  customer_status: ActiveStatus
  member_no: string
  level: MemberLevel
  points: number
  join_date: string
}

export interface SaleItem {
  line_no: number
  product_id: number
  product_name: string
  quantity: number
  unit_price: string
  line_amount: string
}

export interface Sale {
  sale_id: number
  store_id: number
  store_name: string
  customer_id: number | null
  customer_name: string | null
  sale_time: string
  payment_method: PaymentMethod
  total_amount: string
  discount_amount: string
  actual_amount: string
  items: SaleItem[]
}

export interface PurchaseOrderItem {
  line_no: number
  product_id: number
  product_name: string
  quantity: number
  purchase_price: string
  line_amount: string
}

export interface PurchaseOrder {
  purchase_order_id: number
  supplier_id: number
  supplier_name: string
  store_id: number
  store_name: string
  created_by: number
  created_by_name: string
  order_time: string
  status: PurchaseOrderStatus
  total_amount: string
  items: PurchaseOrderItem[]
}

export interface StockInItem {
  line_no: number
  product_id: number
  product_name: string
  quantity: number
  unit_cost: string
  line_amount: string
}

export interface StockIn {
  stock_in_id: number
  purchase_order_id: number
  store_id: number
  store_name: string
  operator_id: number
  operator_name: string
  inbound_time: string
  status: StockInStatus
  items: StockInItem[]
}

export interface StoreDailyRow {
  store_id: number
  store_name: string
  sale_date: string
  order_count: number
  total_amount_sum: string
  discount_amount_sum: string
  actual_amount_sum: string
}

export interface ProductRankRow {
  product_id: number
  product_name: string
  status: ProductStatus
  total_qty: number
  total_sales_amount: string
}

export interface MemberRankRow {
  customer_id: number
  customer_name: string
  member_no: string
  level: MemberLevel
  order_count: number
  total_spending: string
}

export interface CategorySummaryRow {
  category_id: number
  category_name: string
  total_qty: number
  total_sales_amount: string
}
