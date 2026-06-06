// composables/useApi.js
import axios from 'axios'
import { computed } from 'vue'

const normalizeApiBase = (value) => {
  const v = String(value || '').trim()
  if (!v) return ''
  return v.endsWith('/') ? v : `${v}/`
}

export const getApiBaseUrl = () => {
  const envBase =
    import.meta.env?.NUXT_PUBLIC_API_BASE ||
    import.meta.env?.NUXT_PUBLIC_API_BASE_URL ||
    import.meta.env?.NUXT_PUBLIC_API_BASEURL

  if (envBase) return normalizeApiBase(envBase)

  try {
    const config = useRuntimeConfig()
    if (config?.public?.apiBase) return normalizeApiBase(config.public.apiBase)
  } catch {
  }

  // return 'https://api.labertha-villa.com/api/'
  return 'http://localhost:3000/api/'
}

export const getApiOrigin = () => {
  const apiBase = getApiBaseUrl()
  return apiBase.replace(/\/api\/?$/, '')
}

export const useAuth = () => {
  const user = computed(() => {
    try {
      return JSON.parse(localStorage.getItem('user') || '{}')
    } catch {
      return {}
    }
  })

  const token = computed(() => localStorage.getItem('access_token'))

  return { user, token }
}

// Axios instance
export const api = axios.create({
  baseURL: '',
})

// Request interceptor to add the auth token
api.interceptors.request.use(
  (config) => {
    config.baseURL = getApiBaseUrl()
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${getApiOrigin()}/api/token/refresh/`, {
            refresh: refreshToken,
          })
          localStorage.setItem('access_token', response.data.access)
          api.defaults.headers.common.Authorization = `Bearer ${response.data.access}`
          return api(originalRequest)
        } catch (refreshError) {
          // If refresh fails, log out user
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
