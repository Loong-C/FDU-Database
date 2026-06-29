import type { Store } from '@/api/types'

export const DEFAULT_STORE_ID = 1
export const DEFAULT_STORE_NAME = '上海五角场店'

export function defaultStoreId(stores: Store[]): number {
  return stores.find((store) => store.store_name === DEFAULT_STORE_NAME)?.store_id ?? stores[0]?.store_id ?? DEFAULT_STORE_ID
}
