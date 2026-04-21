import { http } from './http'
import type { PageResult, Store } from './types'

export interface StoreQuery {
  page?: number
  page_size?: number
  search?: string
  city?: string
}

export function listStores(params: StoreQuery = {}) {
  return http.get<PageResult<Store>>('/stores', params)
}

export function getStore(id: number) {
  return http.get<Store>(`/stores/${id}`)
}

export function createStore(data: Partial<Store>) {
  return http.post<Store>('/stores', data)
}

export function updateStore(id: number, data: Partial<Store>) {
  return http.patch<Store>(`/stores/${id}`, data)
}

export function deleteStore(id: number) {
  return http.delete<null>(`/stores/${id}`)
}
