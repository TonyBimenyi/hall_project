import { ref } from 'vue'

const STORAGE_KEY = 'admin_theme'

export const adminTheme = ref('light')

const normalizeTheme = (value) => {
  const v = String(value || '').toLowerCase()
  return v === 'dark' ? 'dark' : 'light'
}

export const getAdminTheme = () => {
  if (!process.client) return adminTheme.value
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored) return normalizeTheme(stored)
  const prefersDark = typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-color-scheme: dark)').matches
  return prefersDark ? 'dark' : 'light'
}

export const applyAdminTheme = (theme) => {
  if (!process.client) return
  const normalized = normalizeTheme(theme)
  adminTheme.value = normalized
  document.documentElement.setAttribute('data-admin-theme', normalized)
  try {
    localStorage.setItem(STORAGE_KEY, normalized)
  } catch {
    // ignore
  }
}

export const initAdminTheme = () => {
  const theme = getAdminTheme()
  applyAdminTheme(theme)
  return theme
}

export const toggleAdminTheme = () => {
  const next = (getAdminTheme() === 'dark') ? 'light' : 'dark'
  applyAdminTheme(next)
  return next
}

export const clearAdminTheme = () => {
  if (!process.client) return
  document.documentElement.removeAttribute('data-admin-theme')
}

