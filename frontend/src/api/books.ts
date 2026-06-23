import { http } from './http'
import type { Book, PageResult, ProductStatus, SupplierLink } from './types'

export interface BookQuery {
  page?: number
  page_size?: number
  search?: string
  publisher_id?: number
  category_id?: number
}

export interface BookWritePayload {
  product_name: string
  category_id: number
  unit: string
  unit_price: number | string
  cost_price?: number | string
  store_id?: number
  stock_qty?: number
  safety_stock_qty?: number
  barcode?: string | null
  status: ProductStatus
  supplier_links?: SupplierLink[]
  isbn: string
  publisher_id: number
  publish_date?: string | null
  edition?: string | null
  language?: string | null
  page_count?: number | null
  author_ids: number[]
  translator_ids?: number[]
}

export function listBooks(params: BookQuery = {}) {
  return http.get<PageResult<Book>>('/books', params)
}

export function getBook(productId: number) {
  return http.get<Book>(`/books/${productId}`)
}

export function createBook(data: BookWritePayload) {
  return http.post<Book>('/books', data)
}

export function updateBook(productId: number, data: Partial<BookWritePayload>) {
  return http.patch<Book>(`/books/${productId}`, data)
}

export function deleteBook(productId: number) {
  return http.delete<null>(`/books/${productId}`)
}
