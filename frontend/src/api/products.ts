import { http } from './http'
import type { PageResult, Product, ProductStatus, SupplierLink } from './types'

export interface ProductQuery {
  page?: number
  page_size?: number
  search?: string
  category_id?: number
  status?: ProductStatus
  is_book?: boolean
}

export interface ProductWritePayload {
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
}

export function listProducts(params: ProductQuery = {}) {
  return http.get<PageResult<Product>>('/products', params)
}

export function getProduct(id: number) {
  return http.get<Product>(`/products/${id}`)
}

export function createProduct(data: ProductWritePayload) {
  return http.post<Product>('/products', data)
}

export function updateProduct(id: number, data: Partial<ProductWritePayload>) {
  return http.patch<Product>(`/products/${id}`, data)
}

export function deleteProduct(id: number) {
  return http.delete<null>(`/products/${id}`)
}
