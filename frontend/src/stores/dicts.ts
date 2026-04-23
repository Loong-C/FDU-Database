import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listStores } from '@/api/stores'
import { listSuppliers } from '@/api/suppliers'
import { listCategories } from '@/api/categories'
import { listPublishers } from '@/api/publishers'
import { listAuthors } from '@/api/authors'
import { listTranslators } from '@/api/translators'
import type { Author, Category, Publisher, Store, Supplier, Translator } from '@/api/types'

// 统一的"下拉字典"缓存，避免每个页面重复请求。调用 ensureXxx() 后使用 refs。
export const useDictsStore = defineStore('dicts', () => {
  const stores = ref<Store[]>([])
  const suppliers = ref<Supplier[]>([])
  const categories = ref<Category[]>([])
  const publishers = ref<Publisher[]>([])
  const authors = ref<Author[]>([])
  const translators = ref<Translator[]>([])

  const loaded = {
    stores: false,
    suppliers: false,
    categories: false,
    publishers: false,
    authors: false,
    translators: false,
  }

  async function ensureStores(force = false) {
    if (loaded.stores && !force) return stores.value
    const res = await listStores({ page: 1, page_size: 100 })
    stores.value = res.items
    loaded.stores = true
    return stores.value
  }

  async function ensureSuppliers(force = false) {
    if (loaded.suppliers && !force) return suppliers.value
    const res = await listSuppliers({ page: 1, page_size: 100 })
    suppliers.value = res.items
    loaded.suppliers = true
    return suppliers.value
  }

  async function ensureCategories(force = false) {
    if (loaded.categories && !force) return categories.value
    const res = await listCategories({ page: 1, page_size: 200 })
    categories.value = res.items
    loaded.categories = true
    return categories.value
  }

  async function ensurePublishers(force = false) {
    if (loaded.publishers && !force) return publishers.value
    const res = await listPublishers({ page: 1, page_size: 100 })
    publishers.value = res.items
    loaded.publishers = true
    return publishers.value
  }

  async function ensureAuthors(force = false) {
    if (loaded.authors && !force) return authors.value
    const res = await listAuthors({ page: 1, page_size: 200 })
    authors.value = res.items
    loaded.authors = true
    return authors.value
  }

  async function ensureTranslators(force = false) {
    if (loaded.translators && !force) return translators.value
    const res = await listTranslators({ page: 1, page_size: 200 })
    translators.value = res.items
    loaded.translators = true
    return translators.value
  }

  function invalidate(kind: keyof typeof loaded) {
    loaded[kind] = false
  }

  function invalidateAll() {
    Object.keys(loaded).forEach((k) => {
      loaded[k as keyof typeof loaded] = false
    })
  }

  return {
    stores,
    suppliers,
    categories,
    publishers,
    authors,
    translators,
    ensureStores,
    ensureSuppliers,
    ensureCategories,
    ensurePublishers,
    ensureAuthors,
    ensureTranslators,
    invalidate,
    invalidateAll,
  }
})
