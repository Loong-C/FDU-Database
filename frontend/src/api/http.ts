import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ApiResult, PageResult } from './types'

// 后端响应永远是 { code, message, data, errors? }，我们统一解包到 data。
// 同时在拦截器处区分 422(字段级)/409(冲突)/401(刷新)/其他(Message 提示)。

const BASE_URL = import.meta.env.VITE_API_BASE || '/api/v1'

export class ApiError extends Error {
  public status: number
  public errors: Record<string, string[] | string> | null
  public raw: unknown

  constructor(status: number, message: string, errors: Record<string, string[] | string> | null, raw: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.errors = errors
    this.raw = raw
  }

  get isValidation() {
    return this.status === 422
  }

  get isConflict() {
    return this.status === 409
  }

  get isNotFound() {
    return this.status === 404
  }

  get isForbidden() {
    return this.status === 403
  }

  get isUnauthorized() {
    return this.status === 401
  }
}

type TokenProvider = () => string | null
type TokenRefresher = () => Promise<string>
type UnauthorizedHandler = () => void

interface HttpOptions {
  skipAuth?: boolean
  silent?: boolean // 抑制 ElMessage 全局提示
  rawResponse?: boolean // 返回完整 ApiResult 而非仅 data
}

let accessTokenProvider: TokenProvider = () => null
let tokenRefresher: TokenRefresher | null = null
let onUnauthorized: UnauthorizedHandler | null = null

let refreshPromise: Promise<string> | null = null
const pendingQueue: Array<(token: string) => void> = []

export function configureHttp(options: {
  getAccessToken: TokenProvider
  refreshAccessToken: TokenRefresher
  onAuthExpired: UnauthorizedHandler
}) {
  accessTokenProvider = options.getAccessToken
  tokenRefresher = options.refreshAccessToken
  onUnauthorized = options.onAuthExpired
}

const instance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 20000,
})

instance.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const skipAuth = (config as AxiosRequestConfig & HttpOptions).skipAuth
  if (!skipAuth) {
    const token = accessTokenProvider()
    if (token) {
      config.headers.set('Authorization', `Bearer ${token}`)
    }
  }
  return config
})

instance.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiResult>) => {
    const originalConfig = error.config as (AxiosRequestConfig & HttpOptions & { _retried?: boolean }) | undefined
    const response = error.response
    const silent = originalConfig?.silent

    if (!response) {
      if (!silent) ElMessage.error(error.message || '网络异常，请稍后重试')
      return Promise.reject(new ApiError(0, error.message || 'Network error', null, error))
    }

    const status = response.status
    const payload = response.data || ({} as ApiResult)
    const message = payload.message || response.statusText || `请求失败 (${status})`
    const errors = payload.errors || null

    // 401: 尝试走刷新队列
    if (status === 401 && originalConfig && !originalConfig._retried && !originalConfig.skipAuth && tokenRefresher) {
      originalConfig._retried = true
      try {
        const newToken = await (refreshPromise ??= runRefresh())
        refreshPromise = null
        originalConfig.headers = originalConfig.headers ?? {}
        ;(originalConfig.headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`
        return instance.request(originalConfig)
      } catch (refreshError) {
        refreshPromise = null
        if (onUnauthorized) onUnauthorized()
        return Promise.reject(new ApiError(401, '登录状态已失效，请重新登录', null, refreshError))
      }
    }

    if (status === 401 && onUnauthorized) {
      onUnauthorized()
    }

    // 409 业务冲突：弹窗明确提示（除非 silent）
    if (status === 409 && !silent) {
      ElMessageBox.alert(message, '业务冲突', {
        type: 'warning',
        confirmButtonText: '我知道了',
        draggable: true,
      }).catch(() => undefined)
    } else if (status === 422) {
      if (!silent) {
        const firstMsg = pickFirstErrorMessage(errors) || message || '表单校验失败'
        ElMessage.error(firstMsg)
      }
    } else if (status !== 401 && !silent) {
      ElMessage.error(message)
    }

    return Promise.reject(new ApiError(status, message, errors, response.data))
  },
)

function pickFirstErrorMessage(errors: Record<string, string[] | string> | null): string | null {
  if (!errors) return null
  for (const value of Object.values(errors)) {
    if (Array.isArray(value) && value.length) return String(value[0])
    if (typeof value === 'string' && value) return value
  }
  return null
}

function runRefresh(): Promise<string> {
  if (!tokenRefresher) return Promise.reject(new Error('No refresher configured'))
  return tokenRefresher()
    .then((token) => {
      pendingQueue.forEach((resolve) => resolve(token))
      pendingQueue.length = 0
      return token
    })
    .catch((err) => {
      pendingQueue.length = 0
      throw err
    })
}

async function request<T>(config: AxiosRequestConfig & HttpOptions): Promise<T> {
  const response = await instance.request<ApiResult<T>>(config)
  const payload = response.data
  if (payload && typeof payload === 'object' && 'code' in payload) {
    if (payload.code !== 0) {
      // 非 0 视为业务错误
      throw new ApiError(response.status || 500, payload.message || '业务错误', payload.errors ?? null, payload)
    }
    if (config.rawResponse) {
      return payload as unknown as T
    }
    return payload.data as T
  }
  return payload as T
}

type QueryParams = Record<string, unknown> | object

export const http = {
  request,
  get: <T>(url: string, params?: QueryParams, options?: HttpOptions) =>
    request<T>({ method: 'GET', url, params: params as Record<string, unknown> | undefined, ...options }),
  delete: <T>(url: string, params?: QueryParams, options?: HttpOptions) =>
    request<T>({ method: 'DELETE', url, params: params as Record<string, unknown> | undefined, ...options }),
  post: <T>(url: string, data?: unknown, options?: HttpOptions) =>
    request<T>({ method: 'POST', url, data, ...options }),
  put: <T>(url: string, data?: unknown, options?: HttpOptions) =>
    request<T>({ method: 'PUT', url, data, ...options }),
  patch: <T>(url: string, data?: unknown, options?: HttpOptions) =>
    request<T>({ method: 'PATCH', url, data, ...options }),
}

export type { HttpOptions, PageResult }
