import { ref, computed } from 'vue'

// Notification type definitions
const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  WARNING: 'warning',
  DANGER: 'danger',
  INFO: 'info'
}

// Role definitions
const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  RECEPTIONIST: 'receptionist',
  INVENTORY_MANAGER: 'inventory_manager',
  STOREKEEPER: 'storekeeper'
}

// Global notifications state
const notifications = ref([
  {
    id: 1,
    title: 'Payment Received',
    message: 'Payment received for reservation LBR26060025.',
    type: NOTIFICATION_TYPES.SUCCESS,
    timestamp: Date.now() - 5 * 60 * 1000, // 5 minutes ago
    read: false,
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.RECEPTIONIST]
  },
  {
    id: 2,
    title: 'Payment Overdue',
    message: 'Payment overdue for reservation LBR26060020.',
    type: NOTIFICATION_TYPES.DANGER,
    timestamp: Date.now() - 60 * 60 * 1000, // 1 hour ago
    read: false,
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.RECEPTIONIST]
  },
  {
    id: 3,
    title: 'Low Stock Warning',
    message: 'Low stock warning: Towels remaining: 5.',
    type: NOTIFICATION_TYPES.WARNING,
    timestamp: Date.now() - 2 * 60 * 60 * 1000, // 2 hours ago
    read: true,
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.INVENTORY_MANAGER, ROLES.STOREKEEPER]
  },
  {
    id: 4,
    title: 'Out of Stock',
    message: 'Out of stock: Bath Towels.',
    type: NOTIFICATION_TYPES.DANGER,
    timestamp: Date.now() - 24 * 60 * 60 * 1000, // 1 day ago
    read: true,
    roles: [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.INVENTORY_MANAGER, ROLES.STOREKEEPER]
  }
])

const showNotificationsDropdown = ref(false)

// Current user role (from local storage or useUser composable)
const currentUserRole = ref(() => {
  if (process.client) {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (user?.is_superuser) return ROLES.SUPER_ADMIN
      if (user?.personnel_role?.toLowerCase() === 'receptionist') return ROLES.RECEPTIONIST
      if (user?.personnel_role?.toLowerCase() === 'inventory manager' || user?.personnel_role?.toLowerCase() === 'storekeeper') return ROLES.INVENTORY_MANAGER
      if (user?.is_staff) return ROLES.ADMIN
    } catch {
      return ROLES.ADMIN
    }
  }
  return ROLES.ADMIN
})

// Computed properties
const filteredNotifications = computed(() => {
  const role = currentUserRole.value()
  return notifications.value.filter(n => n.roles.includes(role))
})

const unreadNotifications = computed(() => {
  return filteredNotifications.value.filter(n => !n.read)
})

const unreadCount = computed(() => unreadNotifications.value.length)

const recentNotifications = computed(() => {
  return filteredNotifications.value.slice(0, 5)
})

// Helper function to format time ago
const formatTimeAgo = (timestamp) => {
  const now = Date.now()
  const diff = now - timestamp
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`
  if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  return 'Just now'
}

// Functions
const markAsRead = (notificationId) => {
  const notification = notifications.value.find(n => n.id === notificationId)
  if (notification) {
    notification.read = true
  }
}

const markAllAsRead = () => {
  notifications.value.forEach(n => {
    if (n.roles.includes(currentUserRole.value())) {
      n.read = true
    }
  })
}

const addNotification = (notification) => {
  notifications.value.unshift({
    id: Date.now(),
    read: false,
    timestamp: Date.now(),
    ...notification
  })
}

// Exports
export {
  notifications,
  showNotificationsDropdown,
  filteredNotifications,
  unreadNotifications,
  unreadCount,
  recentNotifications,
  NOTIFICATION_TYPES,
  ROLES,
  formatTimeAgo,
  markAsRead,
  markAllAsRead,
  addNotification
}
