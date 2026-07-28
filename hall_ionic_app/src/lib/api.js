import axios from 'axios'

const normalizeApiBase = (value) => {
  const v = String(value || '').trim()
  if (!v) return ''
  return v.endsWith('/') ? v : `${v}/`
}

const IS_BROWSER = typeof window !== 'undefined'

let _authRouter = null
export const setAuthRouter = (router) => {
  _authRouter = router
}

const redirectToLogin = () => {
  if (!IS_BROWSER) return
  if (_authRouter && typeof _authRouter.replace === 'function') {
    _authRouter.replace('/login').catch(() => {})
  } else {
    const base = window.location.pathname.split('/#/')[0] || '/'
    window.location.href = `${base}#/login`
  }
}

export const getApiBaseUrl = () => {
  const envBase =
    (IS_BROWSER ? window.__API_BASE__ : null) ||
    import.meta.env?.VITE_API_BASE ||
    import.meta.env?.NUXT_PUBLIC_API_BASE ||
    import.meta.env?.NUXT_PUBLIC_API_BASE_URL

  if (envBase) return normalizeApiBase(envBase)

  return 'https://api.labertha-villa.com/api/'
}

export const getApiOrigin = () => {
  const apiBase = getApiBaseUrl()
  return apiBase.replace(/\/api\/?$/, '')
}

export const isAuthenticated = () => {
  if (!IS_BROWSER) return false
  return Boolean(localStorage.getItem('access_token'))
}

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000
})

api.interceptors.request.use((config) => {
  config.baseURL = getApiBaseUrl()
  const token = IS_BROWSER ? localStorage.getItem('access_token') : null
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => Promise.reject(error))

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const responseStatus = error?.response?.status
    const responseDetail = String(error?.response?.data?.detail || '')
    const isAuth403 =
      responseDetail.includes('Authentication credentials were not provided') ||
      responseDetail.includes('Given token not valid') ||
      responseDetail.includes('Token is invalid') ||
      responseDetail.includes('Token is expired') ||
      responseDetail.includes('User inactive or deleted')

    if (responseStatus === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = IS_BROWSER ? localStorage.getItem('refresh_token') : null
      if (refreshToken) {
        try {
          const response = await endpoints.tokenRefresh({ refresh: refreshToken })
          localStorage.setItem('access_token', response.access)
          api.defaults.headers.common.Authorization = `Bearer ${response.access}`
          return api(originalRequest)
        } catch (_refreshError) {
          if (IS_BROWSER) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user')
            redirectToLogin()
          }
        }
      } else if (IS_BROWSER) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        redirectToLogin()
      }
    }

    if (IS_BROWSER && responseStatus === 403 && isAuth403) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      redirectToLogin()
    }

    return Promise.reject(error)
  }
)

export const endpoints = {
  summary: () => api.get('summary/').then((r) => r.data),
  bookings: (params) => api.get('bookings/', { params }).then((r) => r.data),
  booking: (id) => api.get(`bookings/${id}/`).then((r) => r.data),
  rooms: (params) => api.get('rooms/', { params }).then((r) => r.data),
  halls: (params) => api.get('halls/', { params }).then((r) => r.data),
  customers: (params) => api.get('customers/', { params }).then((r) => r.data),
  payments: (params) => api.get('payments/', { params }).then((r) => r.data),
  personnel: (params) => api.get('personnel/', { params }).then((r) => r.data),
  expenses: (params) => api.get('expenses/', { params }).then((r) => r.data),
  materials: (params) => api.get('materials/', { params }).then((r) => r.data),
  notifications: (params) => api.get('notifications/', { params }).then((r) => r.data),
  notificationMarkRead: (id) => api.patch(`notifications/${id}/read/`).then((r) => r.data),
  notificationMarkAllRead: () => api.post('notifications/mark-all-read/').then((r) => r.data),
  me: () => api.get('me/').then((r) => r.data),
  updateMe: (payload) => api.patch('me/', payload).then((r) => r.data),
  tokenObtain: (payload) => api.post('token/', payload).then((r) => r.data),
  tokenRefresh: (payload) => api.post('token/refresh/', payload).then((r) => r.data),
  magicLinkRequest: (payload) => api.post('auth/magic-link/request/', payload).then((r) => r.data),
  magicLinkVerify: (payload) => api.post('auth/magic-link/verify/', payload).then((r) => r.data)
}

export const normalizeLoginUsername = (raw) => {
  if (!raw && raw !== 0) return ''
  const value = String(raw).trim()
  const compact = value.replace(/\s+/g, '')
  const isPhoneLike = /^\+?\d+$/.test(compact)
  return isPhoneLike ? compact.replace(/\D/g, '') : value
}

export const loginWithPassword = async ({ username, password }) => {
  const loginUsername = normalizeLoginUsername(username)
  const tokenResponse = await endpoints.tokenObtain({ username: loginUsername, password })

  const access = tokenResponse?.access
  const refresh = tokenResponse?.refresh

  if (access) {
    saveAuthSession({ access, refresh, user: null })
    api.defaults.headers.common.Authorization = `Bearer ${access}`
  }

  let user = getStoredUser()
  if (!user && access) {
    try {
      user = await endpoints.me()
      saveAuthSession({ access, refresh, user })
    } catch (_e) {
      // if me call fails, we still keep the tokens
    }
  }

  return { tokens: tokenResponse, user }
}

export const getStoredUser = () => {
  if (!IS_BROWSER) return null
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch (_) {
    return null
  }
}

export const saveAuthSession = ({ access, refresh, user }) => {
  if (!IS_BROWSER) return
  if (access) localStorage.setItem('access_token', access)
  if (refresh) localStorage.setItem('refresh_token', refresh)
  if (user) localStorage.setItem('user', JSON.stringify(user))
}

export const clearAuthSession = () => {
  if (!IS_BROWSER) return
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
}
