<template>
  <div class="notifications-page">
    <div class="page-header-wrapper">
      <div>
        <h1 class="page-title">Notifications</h1>
        <p class="page-subtitle">Manage all your notifications in one place</p>
      </div>
      <button v-if="unreadCount > 0" class="btn btn-primary" @click="handleMarkAllAsRead">
        <i class="fas fa-check-double"></i>
        Mark all as read
      </button>
    </div>

    <div class="notifications-container">
      <template v-if="filteredNotifications.length === 0">
        <div class="empty-state">
          <i class="fas fa-inbox"></i>
          <h2>No notifications</h2>
          <p>You're all caught up!</p>
        </div>
      </template>
      <template v-else>
        <div
          v-for="notification in filteredNotifications"
          :key="notification.id"
          class="notification-card"
          :class="{ unread: !notification.read }"
          @click="handleMarkAsRead(notification.id)"
        >
          <div class="card-icon" :class="notification.type">
            <i :class="getIconForType(notification.type)"></i>
          </div>
          <div class="card-content">
            <div class="card-header">
              <h3 class="card-title">{{ notification.title }}</h3>
              <span class="card-time">{{ formatTimeAgo(notification.timestamp) }}</span>
            </div>
            <p class="card-message">{{ notification.message }}</p>
          </div>
          <div v-if="!notification.read" class="card-badge"></div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import {
  filteredNotifications,
  unreadCount,
  formatTimeAgo,
  markAsRead,
  markAllAsRead,
  NOTIFICATION_TYPES
} from '~/composables/useNotifications'

const handleMarkAsRead = (id) => {
  markAsRead(id)
}

const handleMarkAllAsRead = () => {
  markAllAsRead()
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
</script>

<style scoped>
.notifications-page {
  max-width: 900px;
  margin: 0 auto;
}

.page-header-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  gap: 16px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #1e293b;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 0.95rem;
  color: #64748b;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 10px;
  background: #d4af37;
  color: white;
  border: none;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
}

.btn-primary:hover {
  background: #b8941f;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(212, 175, 55, 0.4);
}

.notifications-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  display: flex;
  gap: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.notification-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: rgba(212, 175, 55, 0.3);
}

.notification-card.unread {
  background: rgba(212, 175, 55, 0.05);
  border-color: rgba(212, 175, 55, 0.4);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
}

.card-icon.success {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.card-icon.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.card-icon.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.card-icon.info {
  background: rgba(14, 165, 233, 0.15);
  color: #0ea5e9;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.card-title {
  font-weight: 700;
  font-size: 1.05rem;
  color: #1e293b;
}

.card-time {
  font-size: 0.8rem;
  color: #94a3b8;
  flex-shrink: 0;
}

.card-message {
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.5;
}

.card-badge {
  width: 10px;
  height: 10px;
  background: #d4af37;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 8px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state i {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 16px;
}

.empty-state h2 {
  font-size: 1.5rem;
  color: #475569;
  margin-bottom: 8px;
  font-weight: 700;
}

.empty-state p {
  color: #94a3b8;
  font-size: 0.95rem;
}

@media (max-width: 768px) {
  .page-header-wrapper {
    flex-direction: column;
    align-items: flex-start;
  }

  .notification-card {
    padding: 16px;
  }

  .card-icon {
    width: 42px;
    height: 42px;
    font-size: 1.1rem;
  }

  .card-title {
    font-size: 0.95rem;
  }
}
</style>
