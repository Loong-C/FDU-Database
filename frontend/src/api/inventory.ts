import { http } from './http'
import type { InventoryRow, PageQuery, PageResult } from './types'

export interface InventoryQuery extends PageQuery {
  store_id?: number
  product_id?: number
  warning?: boolean
}

export interface InventoryUpdatePayload {
  stock_qty?: number
  safety_stock_qty?: number
}

export function listInventory(params: InventoryQuery = {}) {
  return http.get<PageResult<InventoryRow>>('/inventory', params)
}

export function listInventoryWarnings() {
  return http.get<InventoryRow[]>('/inventory/warnings')
}

export function getInventory(storeId: number, productId: number) {
  return http.get<InventoryRow>(`/inventory/${storeId}/${productId}`)
}

export function updateInventory(storeId: number, productId: number, data: InventoryUpdatePayload) {
  return http.patch<InventoryRow>(`/inventory/${storeId}/${productId}`, data)
}
