import { http } from './http'
import type { Member, MemberLevel, PageResult } from './types'

export interface MemberQuery {
  page?: number
  page_size?: number
  search?: string
  level?: MemberLevel
}

export interface MemberWritePayload {
  customer_id: number
  member_no: string
  level: MemberLevel
  points?: number
  join_date: string
}

export function listMembers(params: MemberQuery = {}) {
  return http.get<PageResult<Member>>('/members', params)
}

export function getMember(customerId: number) {
  return http.get<Member>(`/members/${customerId}`)
}

export function createMember(data: MemberWritePayload) {
  return http.post<Member>('/members', data)
}

export function updateMember(customerId: number, data: Partial<MemberWritePayload>) {
  return http.patch<Member>(`/members/${customerId}`, data)
}

export function deleteMember(customerId: number) {
  return http.delete<null>(`/members/${customerId}`)
}
