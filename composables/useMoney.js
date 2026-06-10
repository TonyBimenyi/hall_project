import { computed } from 'vue'

const normalizeInput = (value) => String(value ?? '')
  .replace(/\s+/g, '')
  .replace(/,/g, '.')
  .replace(/[^\d.-]/g, '')

const groupThousands = (value) => value.replace(/\B(?=(\d{3})+(?!\d))/g, ' ')

export const useMoney = () => {
  const parseMoney = (value) => {
    if (typeof value === 'number') return Number.isFinite(value) ? value : 0
    const cleaned = normalizeInput(value)
    if (!cleaned || cleaned === '-' || cleaned === '.' || cleaned === '-.') return 0
    const parsed = Number(cleaned)
    return Number.isFinite(parsed) ? parsed : 0
  }

  const formatNumberSpaces = (value, options = {}) => {
    const {
      minimumFractionDigits = 0,
      maximumFractionDigits = 0,
    } = options

    const num = parseMoney(value)
    const negative = num < 0 ? '-' : ''
    const abs = Math.abs(num)
    const hasFractionConfig = maximumFractionDigits > 0 || minimumFractionDigits > 0
    const raw = hasFractionConfig
      ? abs.toFixed(maximumFractionDigits)
      : String(Math.round(abs))

    let [intPart, decimalPart = ''] = raw.split('.')

    if (hasFractionConfig && maximumFractionDigits > minimumFractionDigits) {
      decimalPart = decimalPart.replace(/0+$/, '')
      if (decimalPart.length < minimumFractionDigits) {
        decimalPart = decimalPart.padEnd(minimumFractionDigits, '0')
      }
    }

    const grouped = groupThousands(intPart)
    return decimalPart ? `${negative}${grouped}.${decimalPart}` : `${negative}${grouped}`
  }

  const formatMoney = (value, currency = 'Fbu') => `${formatNumberSpaces(value)} ${currency}`

  const formatMoneyInput = (value) => {
    const normalized = normalizeInput(value)
    if (!normalized) return ''
    return formatNumberSpaces(normalized)
  }

  const moneyInputModel = (source, key) => computed({
    get() {
      const current = source.value?.[key]
      if (current === '' || current === null || current === undefined) return ''
      return formatMoneyInput(current)
    },
    set(nextValue) {
      if (source.value) {
        source.value[key] = parseMoney(nextValue)
      }
    }
  })

  return {
    parseMoney,
    formatMoney,
    formatMoneyInput,
    formatNumberSpaces,
    moneyInputModel,
  }
}
