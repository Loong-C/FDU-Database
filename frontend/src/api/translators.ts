import { http } from './http'
import type { PageResult, Translator } from './types'

export interface TranslatorQuery {
  page?: number
  page_size?: number
  search?: string
}

export function listTranslators(params: TranslatorQuery = {}) {
  return http.get<PageResult<Translator>>('/translators', params)
}

export function createTranslator(data: Partial<Translator>) {
  return http.post<Translator>('/translators', data)
}

export function updateTranslator(id: number, data: Partial<Translator>) {
  return http.patch<Translator>(`/translators/${id}`, data)
}

export function deleteTranslator(id: number) {
  return http.delete<null>(`/translators/${id}`)
}
