import { http } from './http'
import type { PageResult, PurchaseOrder, PurchaseOrderStatus, StockIn, StockInStatus } from './types'

export interface PurchaseOrderQuery {
  page?: number
  page_size?: number
  supplier_id?: number
  store_id?: number
  status?: PurchaseOrderStatus
}

export interface PurchaseOrderItemPayload {
  product_id: number
  quantity: number
  purchase_price: number | string
}

export interface PurchaseOrderWritePayload {
  supplier_id?: number
  store_id?: number
  created_by?: number
  order_time?: string
  status?: PurchaseOrderStatus
  items?: PurchaseOrderItemPayload[]
}

export interface StockInQuery {
  page?: number
  page_size?: number
  purchase_order_id?: number
  store_id?: number
  status?: StockInStatus
}

export interface StockInItemPayload {
  product_id: number
  quantity: number
  unit_cost: number | string
}

export interface StockInWritePayload {
  purchase_order_id?: number
  store_id?: number
  operator_id?: number
  inbound_time?: string
  status?: StockInStatus
  items?: StockInItemPayload[]
}

export function listPurchaseOrders(params: PurchaseOrderQuery = {}) {
  return http.get<PageResult<PurchaseOrder>>('/purchase-orders', params)
}

export function getPurchaseOrder(id: number) {
  return http.get<PurchaseOrder>(`/purchase-orders/${id}`)
}

export function createPurchaseOrder(data: PurchaseOrderWritePayload) {
  return http.post<PurchaseOrder>('/purchase-orders', data)
}

export function updatePurchaseOrder(id: number, data: Partial<PurchaseOrderWritePayload>) {
  return http.patch<PurchaseOrder>(`/purchase-orders/${id}`, data)
}

export function deletePurchaseOrder(id: number) {
  return http.delete<null>(`/purchase-orders/${id}`)
}

export function listStockIns(params: StockInQuery = {}) {
  return http.get<PageResult<StockIn>>('/stock-ins', params)
}

export function getStockIn(id: number) {
  return http.get<StockIn>(`/stock-ins/${id}`)
}

export function createStockIn(data: StockInWritePayload) {
  return http.post<StockIn>('/stock-ins', data)
}

export function updateStockIn(id: number, data: Partial<StockInWritePayload>) {
  return http.patch<StockIn>(`/stock-ins/${id}`, data)
}

export function deleteStockIn(id: number) {
  return http.delete<null>(`/stock-ins/${id}`)
}
