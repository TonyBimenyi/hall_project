const normalizeText = (value) => String(value || '')
  .trim()
  .toLowerCase()
  .normalize('NFKD')
  .replace(/[\u0300-\u036f]/g, '')

const toAdminPath = (path) => {
  const cleaned = String(path || '').trim()
  if (!cleaned) return '/'
  if (cleaned === '/admin/') return '/admin'
  return cleaned.endsWith('/') ? cleaned.slice(0, -1) : cleaned
}

export const normalizeRoleLabel = (value) => {
  const role = normalizeText(value)
  if (!role) return ''
  if (['admin', 'proprietaire'].includes(role)) return 'proprietaire'
  if (['manager', 'gestionnaire'].includes(role)) return 'gestionnaire'
  if (['gerant', 'gerante'].includes(role)) return 'gerant'
  if (['receptionniste', 'receptionist', 'reception'].includes(role)) return 'receptionniste'
  return role
}

export const getRoleKey = (user) => {
  if (user?.is_superuser) return 'super_admin'

  const normalizedRole = normalizeRoleLabel(user?.personnel_role || user?.role)
  if (normalizedRole) return normalizedRole

  if (user?.is_staff) return 'proprietaire'
  return 'user'
}

export const getRoleLabel = (user) => {
  const role = getRoleKey(user)
  if (role === 'super_admin') return 'Super Admin'
  if (role === 'proprietaire') return 'Proprietaire'
  if (role === 'gestionnaire') return 'Gestionnaire'
  if (role === 'gerant') return 'Gerant'
  if (role === 'receptionniste') return 'Receptionniste'
  if (user?.personnel_role) return String(user.personnel_role)
  return 'Utilisateur'
}

export const canAccessAdmin = (user) => ['super_admin', 'proprietaire', 'gestionnaire', 'gerant', 'receptionniste'].includes(getRoleKey(user))

export const canManageStaffAccounts = (user) => ['super_admin', 'proprietaire', 'gestionnaire'].includes(getRoleKey(user))

export const canDeleteBookings = (user) => ['super_admin', 'proprietaire', 'gestionnaire', 'receptionniste'].includes(getRoleKey(user))

export const canSeeSyntheticRevenue = (user) => ['super_admin', 'proprietaire', 'gestionnaire'].includes(getRoleKey(user))

export const canAccessAdminRoute = (user, path) => {
  if (!canAccessAdmin(user)) return false

  const role = getRoleKey(user)
  const adminPath = toAdminPath(path)

  if (!adminPath.startsWith('/admin')) return false
  if (role === 'super_admin' || role === 'proprietaire' || role === 'gestionnaire') return true
  if (role === 'gerant') return adminPath !== '/admin/reports' && !adminPath.startsWith('/admin/reports/')
  if (role === 'receptionniste') {
    return (
      adminPath === '/admin/bookings' ||
      adminPath.startsWith('/admin/bookings/') ||
      adminPath === '/admin/calendar' ||
      adminPath.startsWith('/admin/calendar/') ||
      adminPath === '/admin/profile'
    )
  }

  return false
}

export const getDefaultAdminRoute = (user) => {
  if (!canAccessAdmin(user)) return '/dashboard'
  return getRoleKey(user) === 'receptionniste' ? '/admin/bookings' : '/admin'
}

export const filterNavigationByRole = (items, user) => {
  const list = Array.isArray(items) ? items : []
  return list.filter(item => canAccessAdminRoute(user, item?.url))
}

export const getStoredUser = () => {
  if (!process.client) return {}
  try {
    return JSON.parse(localStorage.getItem('user') || '{}') || {}
  } catch {
    return {}
  }
}
