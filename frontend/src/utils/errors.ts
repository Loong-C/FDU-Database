import type { FormInstance } from 'element-plus'
import { ApiError } from '@/api/http'

// 将后端 422 errors 字段数组映射到 Element Plus 表单的字段级错误。
// 后端 errors 形如 { field: ["msg1", "msg2"] } 或 { field: "msg" }。
export function applyServerErrors(form: FormInstance | null | undefined, error: unknown): boolean {
  if (!form || !(error instanceof ApiError) || !error.errors) return false
  const payload = error.errors
  let matched = false
  const fieldsToSet: Array<{ prop: string; message: string }> = []
  const nonFieldMessages: string[] = []

  Object.entries(payload).forEach(([key, value]) => {
    const msg = Array.isArray(value) ? String(value[0]) : String(value)
    if (key === 'non_field_errors' || key === 'detail') {
      nonFieldMessages.push(msg)
      return
    }
    matched = true
    fieldsToSet.push({ prop: key, message: msg })
  })

  fieldsToSet.forEach(({ prop, message }) => {
    try {
      ;(form as unknown as { setFields?: (f: Record<string, { message: string }>) => void }).setFields?.({
        [prop]: { message },
      })
    } catch {
      // ignore
    }
  })

  if (fieldsToSet.length) {
    fieldsToSet.forEach(({ prop }) => {
      try {
        form.validateField?.(prop)
      } catch {
        /* noop */
      }
    })
  }

  return matched || nonFieldMessages.length > 0
}

export function firstErrorMessage(error: unknown): string | null {
  if (!(error instanceof ApiError) || !error.errors) return null
  for (const value of Object.values(error.errors)) {
    if (Array.isArray(value) && value[0]) return String(value[0])
    if (typeof value === 'string' && value) return value
  }
  return null
}
