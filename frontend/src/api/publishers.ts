import { http } from './http'
import type { PageResult, Publisher } from './types'

export interface PublisherQuery {
  page?: number
  page_size?: number
  search?: string
}

export function listPublishers(params: PublisherQuery = {}) {
  return http.get<PageResult<Publisher>>('/publishers', params)
}

export function createPublisher(data: Partial<Publisher>) {
  return http.post<Publisher>('/publishers', data)
}

export function updatePublisher(id: number, data: Partial<Publisher>) {
  return http.patch<Publisher>(`/publishers/${id}`, data)
}

export function deletePublisher(id: number) {
  return http.delete<null>(`/publishers/${id}`)
}
