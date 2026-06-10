const pad = (value, size = 4) => String(value).padStart(size, '0')

const normalizeDateKey = (value) => {
  if (!value) return '0000'
  const raw = String(value).slice(0, 10)
  const parts = raw.split('-')
  if (parts.length === 3) {
    const [year, month] = parts
    return `${String(month || '00').padStart(2, '0')}${String(year || '00').slice(-2)}`
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '0000'
  return `${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getFullYear()).slice(-2)}`
}

export const useDisplayIds = () => {
  const buildMonthlySequenceMap = (items, prefix, getDate) => {
    const sorted = [...(items || [])].sort((a, b) => {
      const da = String(getDate(a) || '')
      const db = String(getDate(b) || '')
      if (da !== db) return da.localeCompare(db)
      return Number(a?.id || 0) - Number(b?.id || 0)
    })

    const counts = new Map()
    const output = new Map()
    for (const item of sorted) {
      const key = normalizeDateKey(getDate(item))
      const next = (counts.get(key) || 0) + 1
      counts.set(key, next)
      output.set(item.id, `${prefix}${key}${pad(next)}`)
    }
    return output
  }

  const buildHashSequenceMap = (items) => {
    const sorted = [...(items || [])].sort((a, b) => Number(a?.id || 0) - Number(b?.id || 0))
    const output = new Map()
    sorted.forEach((item, index) => {
      output.set(item.id, `#${pad(index + 1)}`)
    })
    return output
  }

  const buildPersonnelSequenceMap = (items) => {
    const sorted = [...(items || [])].sort((a, b) => Number(a?.id || 0) - Number(b?.id || 0))
    const output = new Map()
    sorted.forEach((item, index) => {
      output.set(item.id, `EMP-${pad(index + 1)}`)
    })
    return output
  }

  return {
    buildMonthlySequenceMap,
    buildHashSequenceMap,
    buildPersonnelSequenceMap,
  }
}
