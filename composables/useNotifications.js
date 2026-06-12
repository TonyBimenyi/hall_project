import { ref, computed } from 'vue'
import { api } from '~/composables/useApi'

const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  WARNING: 'warning',
  DANGER: 'danger',
  INFO: 'info',
}

const notifications = ref([])
const loadingNotifications = ref(false)
const notificationsLoaded = ref(false)
const showNotificationsDropdown = ref(false)

const normalizeNotification = (item) => ({
  ...item,
  read: !!item?.is_read,
  timestamp: item?.created_at || null,
})

const filteredNotifications = computed(() => notifications.value)
const unreadNotifications = computed(() => filteredNotifications.value.filter((item) => !item.read))
const unreadCount = computed(() => unreadNotifications.value.length)
const recentNotifications = computed(() => filteredNotifications.value.slice(0, 5))

const fetchNotifications = async ({ force = false } = {}) => {
  if (loadingNotifications.value) return notifications.value
  if (notificationsLoaded.value && !force) return notifications.value

  loadingNotifications.value = true
  try {
    const response = await api.get('notifications/')
    const items = Array.isArray(response?.data) ? response.data : []
    notifications.value = items.map(normalizeNotification)
    notificationsLoaded.value = true
  } catch (error) {
    if (force) {
      notifications.value = []
    }
    throw error
  } finally {
    loadingNotifications.value = false
  }

  return notifications.value
}

const refreshNotifications = async () => fetchNotifications({ force: true })

const markAsRead = async (notificationId) => {
  const notification = notifications.value.find((item) => item.id === notificationId)
  if (!notification || notification.read) return notification

  notification.read = true
  notification.is_read = true
  try {
    const response = await api.post(`notifications/${notificationId}/mark-read/`)
    const updated = normalizeNotification(response?.data || notification)
    const index = notifications.value.findIndex((item) => item.id === notificationId)
    if (index >= 0) notifications.value[index] = updated
    return updated
  } catch (error) {
    notification.read = false
    notification.is_read = false
    throw error
  }
}

const markAllAsRead = async () => {
  const previous = notifications.value.map((item) => ({ id: item.id, read: item.read, is_read: item.is_read }))
  notifications.value = notifications.value.map((item) => ({
    ...item,
    read: true,
    is_read: true,
  }))

  try {
    await api.post('notifications/mark-all-read/')
  } catch (error) {
    notifications.value = notifications.value.map((item) => {
      const old = previous.find((entry) => entry.id === item.id)
      return old ? { ...item, read: old.read, is_read: old.is_read } : item
    })
    throw error
  }
}

const formatTimeAgo = (timestamp) => {
  const value = timestamp ? new Date(timestamp) : null
  if (!value || Number.isNaN(value.getTime())) return ''

  const seconds = Math.max(0, Math.floor((Date.now() - value.getTime()) / 1000))
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 0) return `il y a ${days} jour${days > 1 ? 's' : ''}`
  if (hours > 0) return `il y a ${hours} heure${hours > 1 ? 's' : ''}`
  if (minutes > 0) return `il y a ${minutes} minute${minutes > 1 ? 's' : ''}`
  return "A l'instant"
}

export {
  notifications,
  loadingNotifications,
  showNotificationsDropdown,
  filteredNotifications,
  unreadNotifications,
  unreadCount,
  recentNotifications,
  NOTIFICATION_TYPES,
  fetchNotifications,
  refreshNotifications,
  formatTimeAgo,
  markAsRead,
  markAllAsRead,
}
