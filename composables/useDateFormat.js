const pad = (value) => String(value).padStart(2, '0')

export const useDateFormat = () => {
  const formatDisplayDate = (value) => {
    if (!value) return ''
    const raw = String(value).slice(0, 10)
    const parts = raw.split('-')
    if (parts.length === 3) {
      const [year, month, day] = parts
      if (year && month && day) return `${day}-${month}-${year}`
    }

    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return `${pad(date.getDate())}-${pad(date.getMonth() + 1)}-${date.getFullYear()}`
  }

  const formatDateTime = (value) => {
    if (!value) return ''
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return `${pad(date.getDate())}-${pad(date.getMonth() + 1)}-${date.getFullYear()} ${pad(date.getHours())}:${pad(date.getMinutes())}`
  }

  const formatDateRange = (start, end, separator = ' au ') => {
    const startText = formatDisplayDate(start)
    const endText = formatDisplayDate(end)
    if (!startText && !endText) return ''
    if (!endText || startText === endText) return startText
    if (!startText) return endText
    return `${startText}${separator}${endText}`
  }

  return {
    formatDisplayDate,
    formatDateTime,
    formatDateRange,
  }
}
