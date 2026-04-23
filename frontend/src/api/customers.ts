import { http } from './http'
import type { ActiveStatus, Customer, PageResult } from './types'

export interface CustomerQuery {
  page?: number
  page_size?: number
  search?: string
  status?: ActiveStatus
}

export function listCustomers(params: CustomerQuery = {}) {
  return http.get<PageResult<Customer>>('/customers', params)
}

export function getCustomer(id: number) {
  return http.get<Customer>(`/customers/${id}`)
}

export function createCustomer(data: Partial<Customer>) {
  return http.post<Customer>('/customers', data)
}

export function updateCustomer(id: number, data: Partial<Customer>) {
  return http.patch<Customer>(`/customers/${id}`, data)
}

export function deleteCustomer(id: number) {
  return http.delete<null>(`/customers/${id}`)
}
