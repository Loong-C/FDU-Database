import type { Category } from '@/api/types'

const GENERAL_ROOT_ALIASES = new Set(['通用商品', '非书商品'])

export function displayCategoryName(name: string | null | undefined): string {
  return name && GENERAL_ROOT_ALIASES.has(name) ? '通用商品' : name || ''
}

function isRootName(category: Category, rootName: string): boolean {
  return displayCategoryName(category.category_name) === rootName
}

export function categoryRootId(categories: Category[], rootName: '图书' | '通用商品'): number | null {
  return categories.find((item) => item.parent_category_id === null && isRootName(item, rootName))?.category_id ?? null
}

export function categoryDescendants(categories: Category[], rootName: '图书' | '通用商品'): Category[] {
  const rootId = categoryRootId(categories, rootName)
  if (rootId === null) return []
  const children = new Map<number | null, Category[]>()
  categories.forEach((category) => {
    const parentId = category.parent_category_id ?? null
    if (!children.has(parentId)) children.set(parentId, [])
    children.get(parentId)!.push(category)
  })

  const result: Category[] = []
  const pending = [...(children.get(rootId) || [])]
  while (pending.length) {
    const current = pending.shift()!
    result.push(current)
    pending.push(...(children.get(current.category_id) || []))
  }
  return result
}

export function categoryOptionLabel(category: Category, categories: Category[], rootName: '图书' | '通用商品'): string {
  const rootId = categoryRootId(categories, rootName)
  const byId = new Map(categories.map((item) => [item.category_id, item]))
  const path: string[] = []
  let current: Category | undefined = category

  while (current && current.category_id !== rootId) {
    path.unshift(displayCategoryName(current.category_name))
    current = current.parent_category_id === null ? undefined : byId.get(current.parent_category_id)
  }

  return path.join(' / ') || displayCategoryName(category.category_name)
}

export function categoryFullOptionLabel(category: Category, categories: Category[]): string {
  const byId = new Map(categories.map((item) => [item.category_id, item]))
  const path: string[] = []
  let current: Category | undefined = category

  while (current) {
    path.unshift(displayCategoryName(current.category_name))
    current = current.parent_category_id === null ? undefined : byId.get(current.parent_category_id)
  }

  return path.join(' / ') || displayCategoryName(category.category_name)
}
