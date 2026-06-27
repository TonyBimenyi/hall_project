// composables/useApi.js
import axios from 'axios'
import { computed } from 'vue'

// #region debug-point A:post-debug-reporter
const reportPostDebug = (hypothesisId, msg, data = {}) => {
  try {
    fetch('http://127.0.0.1:7777/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'post-broken-pipe',
        runId: 'pre-fix',
        hypothesisId,
        location: 'composables/useApi.js',
        msg: `[DEBUG] ${msg}`,
        data,
        ts: Date.now(),
      }),
    }).catch(() => {})
  } catch {
  }
}
// #endregion

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
  return 'http://127.0.0.1:8000/api/'
}


export const getApiOrigin = () => {
  const apiBase = getApiBaseUrl()
  return apiBase.replace(/\/api\/?$/, '')
}

export const useAuth = () => {
  const user = computed(() => {
    if (!process.client) return {}
    try {
      return JSON.parse(localStorage.getItem('user') || '{}')
    } catch {
      return {}
    }
  })

  const token = computed(() => process.client ? localStorage.getItem('access_token') : null)

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
    const token = process.client ? localStorage.getItem('access_token') : null
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // #region debug-point A:request-start
    if (String(config.method || '').toLowerCase() === 'post' && /(bookings|payments)\/?$/.test(String(config.url || ''))) {
      reportPostDebug('A', 'axios request start', {
        method: config.method,
        url: config.url,
        hasAuth: Boolean(token),
        payloadKeys: Object.keys(config.data || {}),
      })
    }
    // #endregion
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => {
    // #region debug-point B:response-success
    if (String(response?.config?.method || '').toLowerCase() === 'post' && /(bookings|payments)\/?$/.test(String(response?.config?.url || ''))) {
      reportPostDebug('B', 'axios response success', {
        url: response?.config?.url,
        status: response?.status,
        responseKeys: Object.keys(response?.data || {}),
        responseId: response?.data?.id ?? null,
      })
    }
    // #endregion
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const responseStatus = error?.response?.status
    const responseDetail = String(error?.response?.data?.detail || '')
    // #region debug-point C:response-error
    if (String(originalRequest?.method || '').toLowerCase() === 'post' && /(bookings|payments)\/?$/.test(String(originalRequest?.url || ''))) {
      reportPostDebug('C', 'axios response error', {
        url: originalRequest?.url,
        status: responseStatus ?? null,
        message: error?.message || null,
        responseData: error?.response?.data || null,
      })
    }
    // #endregion
    if (responseStatus === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = process.client ? localStorage.getItem('refresh_token') : null
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
          if (process.client) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user')
            window.location.href = '/login'
          }
        }
      } else {
        if (process.client) window.location.href = '/login'
      }
    }

    // Some DRF auth failures come back as 403 instead of 401.
    if (
      process.client &&
      responseStatus === 403 &&
      (
        responseDetail.includes('Authentication credentials were not provided') ||
        responseDetail.includes('Given token not valid') ||
        responseDetail.includes('Token is invalid') ||
        responseDetail.includes('Token is expired') ||
        responseDetail.includes('User inactive or deleted')
      )
    ) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)
