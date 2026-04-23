import { http } from './http'
import type { Category, PageResult } from './types'

export function listCategories(params: { page?: number; page_size?: number } = {}) {
  return http.get<PageResult<Category>>('/categories', { page: 1, page_size: 100, ...params })
}

export function getCategory(id: number) {
  return http.get<Category>(`/categories/${id}`)
}

export interface CategoryPayload {
  category_name: string
  parent_category_id?: number | null
}

export function createCategory(data: CategoryPayload) {
  return http.post<Category>('/categories', data)
}

export function updateCategory(id: number, data: Partial<CategoryPayload>) {
  return http.patch<Category>(`/categories/${id}`, data)
}

export function deleteCategory(id: number) {
  return http.delete<null>(`/categories/${id}`)
}
