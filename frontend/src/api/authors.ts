import { http } from './http'
import type { Author, PageResult } from './types'

export interface AuthorQuery {
  page?: number
  page_size?: number
  search?: string
}

export function listAuthors(params: AuthorQuery = {}) {
  return http.get<PageResult<Author>>('/authors', params)
}

export function createAuthor(data: Partial<Author>) {
  return http.post<Author>('/authors', data)
}

export function updateAuthor(id: number, data: Partial<Author>) {
  return http.patch<Author>(`/authors/${id}`, data)
}

export function deleteAuthor(id: number) {
  return http.delete<null>(`/authors/${id}`)
}
