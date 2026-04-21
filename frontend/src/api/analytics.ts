import { http } from './http'
import type {
  CategorySummaryRow,
  MemberLevel,
  MemberRankRow,
  ProductRankRow,
  StoreDailyRow,
} from './types'

export interface StoreDailyQuery {
  store_id?: number
  date_from?: string
  date_to?: string
}

export interface ProductRankQuery extends StoreDailyQuery {
  category_id?: number
  limit?: number
}

export interface MemberRankQuery {
  level?: MemberLevel
  date_from?: string
  date_to?: string
  limit?: number
}

export interface CategorySummaryQuery {
  date_from?: string
  date_to?: string
}

export function analyticsStoresDaily(params: StoreDailyQuery = {}) {
  return http.get<StoreDailyRow[]>('/analytics/stores/daily', params)
}

export function analyticsProductsRank(params: ProductRankQuery = {}) {
  return http.get<ProductRankRow[]>('/analytics/products/rank', params)
}

export function analyticsMembersRank(params: MemberRankQuery = {}) {
  return http.get<MemberRankRow[]>('/analytics/members/rank', params)
}

export function analyticsCategoriesSummary(params: CategorySummaryQuery = {}) {
  return http.get<CategorySummaryRow[]>('/analytics/categories/summary', params)
}
