import { http } from './http'
import type { ActiveStatus, PageResult, Supplier } from './types'

export interface SupplierQuery {
  page?: number
  page_size?: number
  search?: string
  status?: ActiveStatus
}

export function listSuppliers(params: SupplierQuery = {}) {
  return http.get<PageResult<Supplier>>('/suppliers', params)
}

export function getSupplier(id: number) {
  return http.get<Supplier>(`/suppliers/${id}`)
}

export function createSupplier(data: Partial<Supplier>) {
  return http.post<Supplier>('/suppliers', data)
}

export function updateSupplier(id: number, data: Partial<Supplier>) {
  return http.patch<Supplier>(`/suppliers/${id}`, data)
}

export function deleteSupplier(id: number) {
  return http.delete<null>(`/suppliers/${id}`)
}
