import dayjs from 'dayjs'

const cnyFormatter = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const numberFormatter = new Intl.NumberFormat('zh-CN', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
})

export function formatCurrency(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') return cnyFormatter.format(0)
  const n = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(n)) return cnyFormatter.format(0)
  return cnyFormatter.format(n)
}

export function formatNumber(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === '') return '0'
  const n = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(n)) return '0'
  return numberFormatter.format(n)
}

export function formatDateTime(value: string | Date | null | undefined, pattern = 'YYYY-MM-DD HH:mm'): string {
  if (!value) return '-'
  const d = dayjs(value)
  return d.isValid() ? d.format(pattern) : '-'
}

export function formatDate(value: string | Date | null | undefined, pattern = 'YYYY-MM-DD'): string {
  if (!value) return '-'
  const d = dayjs(value)
  return d.isValid() ? d.format(pattern) : '-'
}

export function relativeTime(value: string | Date | null | undefined): string {
  if (!value) return '-'
  const d = dayjs(value)
  if (!d.isValid()) return '-'
  const diff = d.diff(dayjs(), 'minute')
  const abs = Math.abs(diff)
  if (abs < 1) return '刚刚'
  if (abs < 60) return `${abs} 分钟${diff < 0 ? '前' : '后'}`
  if (abs < 60 * 24) return `${Math.round(abs / 60)} 小时${diff < 0 ? '前' : '后'}`
  if (abs < 60 * 24 * 30) return `${Math.round(abs / 60 / 24)} 天${diff < 0 ? '前' : '后'}`
  return d.format('YYYY-MM-DD')
}

const paymentLabels: Record<string, string> = {
  cash: '现金',
  card: '银行卡',
  wechat: '微信',
  alipay: '支付宝',
  mixed: '混合支付',
}

export function paymentLabel(value: string | null | undefined): string {
  if (!value) return '-'
  return paymentLabels[value] ?? value
}

const levelLabels: Record<string, string> = {
  bronze: '青铜',
  silver: '白银',
  gold: '黄金',
  platinum: '铂金',
}

export function memberLevelLabel(value: string | null | undefined): string {
  if (!value) return '-'
  return levelLabels[value] ?? value
}

export function memberLevelColor(level: string | null | undefined): string {
  switch (level) {
    case 'platinum':
      return '#14b8a6'
    case 'gold':
      return '#f59e0b'
    case 'silver':
      return '#64748b'
    case 'bronze':
    default:
      return '#b45309'
  }
}

const statusLabels: Record<string, string> = {
  onsale: '在售',
  offsale: '下架',
  discontinued: '停产',
  active: '启用',
  inactive: '停用',
}

export function statusLabel(value: string | null | undefined): string {
  if (!value) return '-'
  return statusLabels[value] ?? value
}
