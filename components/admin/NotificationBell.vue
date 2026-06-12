<template>
  <div class="notification-bell">
    <button class="bell-btn" @click="toggleDropdown" :class="{ active: showDropdown }">
      <i class="fas fa-bell"></i>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>

    <Transition name="dropdown">
      <div v-if="showDropdown" class="notification-dropdown">
        <div class="dropdown-header">
          <span class="header-title">Notifications</span>
          <button v-if="unreadCount > 0" class="mark-all-btn" @click="handleMarkAllAsRead">
            Tout marquer comme lu
          </button>
        </div>

        <div class="notifications-list">
          <template v-if="loadingNotifications">
            <div class="empty-state">
              <i class="fas fa-spinner fa-spin"></i>
              <span>Chargement des notifications...</span>
            </div>
          </template>
          <template v-else-if="recentNotifications.length === 0">
            <div class="empty-state">
              <i class="fas fa-inbox"></i>
              <span>Aucune notification</span>
            </div>
          </template>
          <template v-else>
            <div
              v-for="notification in recentNotifications"
              :key="notification.id"
              class="notification-item"
              :class="{ unread: !notification.read }"
              @click="openNotificationDetails(notification)"
            >
              <div class="notification-icon" :class="notification.type">
                <i :class="getIconForType(notification.type)"></i>
              </div>
              <div class="notification-content">
                <div class="notification-title">{{ notification.title }}</div>
                <div class="notification-message">{{ notification.message }}</div>
                <div class="notification-time">{{ formatTimeAgo(notification.timestamp) }}</div>
              </div>
              <div v-if="!notification.read" class="unread-dot"></div>
            </div>
          </template>
        </div>

        <div class="dropdown-footer">
          <NuxtLink to="/admin/notifications" class="view-all-btn">
            Voir toutes les notifications
          </NuxtLink>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import {
  showNotificationsDropdown,
  unreadCount,
  recentNotifications,
  loadingNotifications,
  fetchNotifications,
  formatTimeAgo,
  markAsRead,
  markAllAsRead,
  NOTIFICATION_TYPES
} from '~/composables/useNotifications'

const showDropdown = ref(false)

const toggleDropdown = async () => {
  showDropdown.value = !showDropdown.value
  showNotificationsDropdown.value = showDropdown.value
  if (showDropdown.value) {
    await fetchNotifications({ force: true }).catch(() => {})
  }
}

const handleMarkAsRead = async (id) => {
  await markAsRead(id).catch(() => {})
}

const handleMarkAllAsRead = async () => {
  await markAllAsRead().catch(() => {})
}

const getNotificationTarget = (notification) => {
  const focus = String(Date.now())
  if (notification?.payment) {
    return { path: '/admin/payments', query: { view: String(notification.payment), focus } }
  }
  if (notification?.booking) {
    return { path: '/admin/bookings', query: { view: String(notification.booking), focus } }
  }
  if (notification?.material) {
    return { path: '/admin/materials', query: { view: String(notification.material), focus } }
  }
  return null
}

const openNotificationDetails = async (notification) => {
  if (!notification) return
  if (!notification.read) {
    await markAsRead(notification.id).catch(() => {})
  }
  showDropdown.value = false
  showNotificationsDropdown.value = false
  const target = getNotificationTarget(notification)
  if (!target) return
  await navigateTo(target)
}

const getIconForType = (type) => {
  switch (type) {
    case NOTIFICATION_TYPES.SUCCESS:
      return 'fas fa-check-circle'
    case NOTIFICATION_TYPES.WARNING:
      return 'fas fa-exclamation-triangle'
    case NOTIFICATION_TYPES.DANGER:
      return 'fas fa-times-circle'
    case NOTIFICATION_TYPES.INFO:
      return 'fas fa-info-circle'
    default:
      return 'fas fa-bell'
  }
}

const handleOutsideClick = (e) => {
  const bellEl = document.querySelector('.notification-bell')
  if (bellEl && !bellEl.contains(e.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  fetchNotifications().catch(() => {})
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
.notification-bell {
  position: relative;
  margin-right: var(--space-4);
}

.bell-btn {
  position: relative;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bell-btn:hover {
  background: rgba(212, 175, 55, 0.15);
  border-color: rgba(212, 175, 55, 0.35);
  color: #d4af37;
}

.bell-btn.active {
  background: rgba(212, 175, 55, 0.2);
  border-color: rgba(212, 175, 55, 0.45);
  color: #d4af37;
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 18px;
  height: 18px;
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 800;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}

/* Dropdown */
.notification-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 360px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.15);
  border: 1px solid #e2e8f0;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.25s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
}

.header-title {
  font-weight: 800;
  font-size: 1rem;
  color: #1e293b;
}

.mark-all-btn {
  font-size: 0.8rem;
  color: #d4af37;
  font-weight: 600;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mark-all-btn:hover {
  color: #b8941f;
}

.notifications-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 16px 20px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid #f8fafc;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: rgba(212, 175, 55, 0.08);
}

.notification-item.unread:hover {
  background: rgba(212, 175, 55, 0.12);
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1rem;
}

.notification-icon.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.notification-icon.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.notification-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.notification-icon.info {
  background: rgba(14, 165, 233, 0.15);
  color: #0ea5e9;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: #1e293b;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 0.85rem;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 4px;
}

.notification-time {
  font-size: 0.75rem;
  color: #94a3b8;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #d4af37;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 6px;
}

.dropdown-footer {
  padding: 12px 20px;
  border-top: 1px solid #f1f5f9;
  text-align: center;
}

.view-all-btn {
  display: inline-block;
  font-size: 0.85rem;
  font-weight: 700;
  color: #d4af37;
  text-decoration: none;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  color: #b8941f;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
}

.empty-state i {
  font-size: 2.5rem;
  margin-bottom: 12px;
  display: block;
}

/* Mobile styles */
@media (max-width: 992px) {
  .notification-dropdown {
    width: calc(100vw - 32px);
    right: 0;
  }
}
</style>
