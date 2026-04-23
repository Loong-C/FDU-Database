import { http } from './http'
import type { PageResult, Role, User } from './types'

export interface UserQuery {
  page?: number
  page_size?: number
  search?: string
  role?: Role
}

export interface UserWritePayload {
  username: string
  password?: string
  email?: string
  first_name?: string
  last_name?: string
  display_name?: string
  role: Role
  is_active?: boolean
}

export function listUsers(params: UserQuery = {}) {
  return http.get<PageResult<User>>('/users', params)
}

export function createUser(data: UserWritePayload) {
  return http.post<User>('/users', data)
}

export function updateUser(id: number, data: Partial<UserWritePayload>) {
  return http.patch<User>(`/users/${id}`, data)
}

export function deleteUser(id: number) {
  return http.delete<null>(`/users/${id}`)
}
