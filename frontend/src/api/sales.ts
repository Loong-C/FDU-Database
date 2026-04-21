import { http } from './http'
import type { PageResult, PaymentMethod, Sale } from './types'

export interface SaleQuery {
  page?: number
  page_size?: number
  store_id?: number
  customer_id?: number
  payment_method?: PaymentMethod
  date_from?: string
  date_to?: string
}

export interface SaleItemPayload {
  product_id: number
  quantity: number
}

export interface SaleWritePayload {
  store_id: number
  customer_id?: number | null
  sale_time: string
  payment_method: PaymentMethod
  discount_amount?: number | string
  items: SaleItemPayload[]
}

export function listSales(params: SaleQuery = {}) {
  return http.get<PageResult<Sale>>('/sales', params)
}

export function getSale(id: number) {
  return http.get<Sale>(`/sales/${id}`)
}

export function createSale(data: SaleWritePayload) {
  return http.post<Sale>('/sales', data)
}

export function updateSale(id: number, data: Partial<SaleWritePayload>) {
  return http.patch<Sale>(`/sales/${id}`, data)
}

export function deleteSale(id: number) {
  return http.delete<null>(`/sales/${id}`)
}
