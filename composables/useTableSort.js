import { computed, ref } from 'vue'

export const useTableSort = (items, options = {}) => {
  const {
    initialKey = 'id',
    initialDirection = 'desc',
    accessors = {},
  } = options

  const sortKey = ref(initialKey)
  const sortDirection = ref(initialDirection)

  const getValue = (item, key) => {
    const accessor = accessors[key]
    return typeof accessor === 'function' ? accessor(item) : item?.[key]
  }

  const normalizeValue = (value) => {
    if (value === null || value === undefined) return ''
    if (typeof value === 'number') return value
    if (typeof value === 'string') {
      const trimmed = value.trim()
      const asDate = Date.parse(trimmed)
      if (!Number.isNaN(asDate) && /^\d{4}-\d{2}-\d{2}/.test(trimmed)) return asDate
      const asNumber = Number(trimmed)
      if (!Number.isNaN(asNumber) && trimmed !== '') return asNumber
      return trimmed.toLowerCase()
    }
    return value
  }

  const compareValues = (a, b) => {
    const left = normalizeValue(a)
    const right = normalizeValue(b)
    if (left === right) return 0
    if (left === '') return 1
    if (right === '') return -1
    return left > right ? 1 : -1
  }

  const sortedItems = computed(() => {
    const list = Array.isArray(items.value) ? [...items.value] : []
    return list.sort((a, b) => {
      const result = compareValues(getValue(a, sortKey.value), getValue(b, sortKey.value))
      if (result !== 0) return sortDirection.value === 'asc' ? result : -result
      return Number(b?.id || 0) - Number(a?.id || 0)
    })
  })

  const toggleSort = (key) => {
    if (sortKey.value === key) {
      sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
      return
    }
    sortKey.value = key
    sortDirection.value = key === 'id' ? 'desc' : 'asc'
  }

  const isSortActive = (key) => sortKey.value === key
  const sortIconClass = (key) => {
    if (!isSortActive(key)) return 'fa-solid fa-sort'
    return sortDirection.value === 'asc' ? 'fa-solid fa-sort-up' : 'fa-solid fa-sort-down'
  }

  return {
    sortKey,
    sortDirection,
    sortedItems,
    toggleSort,
    isSortActive,
    sortIconClass,
  }
}
