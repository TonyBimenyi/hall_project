import { computed, ref, unref, watch } from 'vue'

export const usePagination = (itemsRef, pageSize = 50) => {
  const currentPage = ref(1)

  const totalItems = computed(() => {
    const items = unref(itemsRef)
    return Array.isArray(items) ? items.length : 0
  })

  const totalPages = computed(() => {
    const pages = Math.ceil(totalItems.value / pageSize)
    return Math.max(1, pages)
  })

  const startIndex = computed(() => {
    if (totalItems.value === 0) return 0
    return ((currentPage.value - 1) * pageSize) + 1
  })

  const endIndex = computed(() => {
    if (totalItems.value === 0) return 0
    return Math.min(currentPage.value * pageSize, totalItems.value)
  })

  const paginatedItems = computed(() => {
    const items = unref(itemsRef)
    if (!Array.isArray(items) || items.length === 0) return []
    const start = (currentPage.value - 1) * pageSize
    return items.slice(start, start + pageSize)
  })

  const canPrev = computed(() => currentPage.value > 1)
  const canNext = computed(() => currentPage.value < totalPages.value)

  const prevPage = () => {
    if (canPrev.value) currentPage.value -= 1
  }

  const nextPage = () => {
    if (canNext.value) currentPage.value += 1
  }

  const resetPage = () => {
    currentPage.value = 1
  }

  watch(() => unref(itemsRef), () => {
    currentPage.value = 1
  }, { deep: true })

  watch(totalPages, (pages) => {
    if (currentPage.value > pages) currentPage.value = pages
  }, { immediate: true })

  return {
    currentPage,
    totalItems,
    totalPages,
    startIndex,
    endIndex,
    paginatedItems,
    canPrev,
    canNext,
    prevPage,
    nextPage,
    resetPage,
    pageSize,
  }
}
