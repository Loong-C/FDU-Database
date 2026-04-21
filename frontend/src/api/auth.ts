import { http } from './http'
import type { TokenPair, User } from './types'

export function login(username: string, password: string) {
  return http.post<TokenPair>('/auth/login', { username, password }, { skipAuth: true })
}

export function refresh(refreshToken: string) {
  return http.post<TokenPair>('/auth/refresh', { refresh_token: refreshToken }, { skipAuth: true, silent: true })
}

export function logout(refreshToken: string) {
  return http.post<null>('/auth/logout', { refresh_token: refreshToken }, { silent: true })
}

export function fetchMe() {
  return http.get<User>('/auth/me')
}
