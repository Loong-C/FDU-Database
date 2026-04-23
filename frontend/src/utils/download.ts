// 简易 CSV 导出：用于分析/列表页的结果下载。

function escapeCell(value: unknown): string {
  if (value === null || value === undefined) return ''
  const str = typeof value === 'string' ? value : String(value)
  if (/[",\n]/.test(str)) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

export function downloadCsv(
  rows: Array<Record<string, unknown>>,
  columns: Array<{ key: string; label: string }>,
  filename: string,
) {
  const header = columns.map((c) => escapeCell(c.label)).join(',')
  const body = rows
    .map((row) => columns.map((c) => escapeCell(row[c.key])).join(','))
    .join('\n')
  const csv = `${header}\n${body}`
  // BOM 避免 Excel 打开乱码
  const blob = new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename.endsWith('.csv') ? filename : `${filename}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
