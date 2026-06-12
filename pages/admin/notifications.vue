<template>
  <div class="notifications-page">
    <section class="hero-card card">
      <div class="hero-copy">
        <div class="hero-badge">
          <i class="fas fa-bell"></i>
          Centre de notifications
        </div>
        <h1 class="hero-title">Notifications Admin</h1>
        <p class="hero-subtitle">
          Suivez les paiements, les retards et les alertes de stock dans une interface moderne,
          claire et organisee.
        </p>
        <div class="hero-actions">
          <button v-if="unreadCount > 0" class="btn btn-primary hero-btn" @click="handleMarkAllAsRead">
            <i class="fas fa-check-double"></i>
            Tout marquer comme lu
          </button>
          <button class="btn btn-secondary hero-btn" @click="refreshPage">
            <i class="fas fa-rotate-right"></i>
            Actualiser
          </button>
        </div>
      </div>

      <div class="hero-visual">
        <div class="hero-ring">
          <div class="hero-ring-inner">
            <span class="hero-number">{{ unreadCount }}</span>
            <span class="hero-label">non lues</span>
          </div>
        </div>
      </div>
    </section>

    <section class="stats-grid">
      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-inbox"></i></div>
        <div class="stat-content">
          <span class="stat-label">Total</span>
          <strong class="stat-value">{{ filteredNotifications.length }}</strong>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon accent"><i class="fas fa-bell"></i></div>
        <div class="stat-content">
          <span class="stat-label">Non lues</span>
          <strong class="stat-value">{{ unreadCount }}</strong>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-calendar-day"></i></div>
        <div class="stat-content">
          <span class="stat-label">Aujourd'hui</span>
          <strong class="stat-value">{{ todayCount }}</strong>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-triangle-exclamation"></i></div>
        <div class="stat-content">
          <span class="stat-label">Importantes</span>
          <strong class="stat-value">{{ importantCount }}</strong>
        </div>
      </article>
    </section>

    <section class="toolbar card">
      <div class="toolbar-copy">
        <h2>Flux recent</h2>
        <p>Filtrez rapidement vos alertes et gardez en vue l'essentiel.</p>
      </div>

      <div class="toolbar-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          class="tab-btn"
          :class="{ active: activeTab === tab.value }"
          @click="activeTab = tab.value"
        >
          <span>{{ tab.label }}</span>
          <span class="tab-count">{{ tab.count }}</span>
        </button>
      </div>
    </section>

    <section class="list-card card">
      <template v-if="loadingNotifications">
        <div class="empty-state loading-state">
          <div class="empty-illustration"><i class="fas fa-spinner fa-spin"></i></div>
          <h2>Chargement des notifications</h2>
          <p>Veuillez patienter un instant.</p>
        </div>
      </template>

      <template v-else-if="visibleNotifications.length === 0">
        <div class="empty-state">
          <div class="empty-illustration"><i class="fas fa-inbox"></i></div>
          <h2>Aucune notification</h2>
          <p>Il n'y a aucune alerte pour le filtre selectionne.</p>
        </div>
      </template>

      <template v-else>
        <article
          v-for="notification in visibleNotifications"
          :key="notification.id"
          class="notification-item"
          :class="[`type-${notification.type}`, { unread: !notification.read }]"
          @click="handleMarkAsRead(notification.id)"
        >
          <div class="notification-side">
            <div class="notification-icon" :class="notification.type">
              <i :class="getIconForType(notification.type)"></i>
            </div>
            <div v-if="!notification.read" class="pulse-dot"></div>
          </div>

          <div class="notification-main">
            <div class="notification-top">
              <div class="notification-heading">
                <h3 class="notification-title">{{ notification.title }}</h3>
                <div class="notification-meta">
                  <span class="status-pill" :class="{ unread: !notification.read }">
                    {{ notification.read ? 'Lue' : 'Non lue' }}
                  </span>
                  <span class="type-pill" :class="notification.type">
                    {{ getTypeLabel(notification.type) }}
                  </span>
                </div>
              </div>

              <div class="notification-dates">
                <span class="relative-time">{{ formatTimeAgo(notification.timestamp) }}</span>
                <span class="absolute-time">{{ formatAbsoluteDate(notification.timestamp) }}</span>
              </div>
            </div>

            <p class="notification-message">{{ notification.message }}</p>

            <div v-if="buildDetailItems(notification).length" class="notification-details">
              <div
                v-for="detail in buildDetailItems(notification)"
                :key="`${notification.id}-${detail.label}`"
                class="detail-chip"
              >
                <span class="detail-label">{{ detail.label }}</span>
                <strong class="detail-value">{{ detail.value }}</strong>
              </div>
            </div>

            <div class="notification-actions">
              <button
                v-if="getNotificationTarget(notification)"
                class="inline-action primary"
                @click.stop="openNotificationDetails(notification)"
              >
                <i class="fas fa-arrow-up-right-from-square"></i>
                {{ getNotificationTargetLabel(notification) }}
              </button>
              <button
                v-if="!notification.read"
                class="inline-action"
                @click.stop="handleMarkAsRead(notification.id)"
              >
                <i class="fas fa-check"></i>
                Marquer comme lue
              </button>
              <span v-else class="inline-action muted">
                <i class="fas fa-check-circle"></i>
                Notification traitee
              </span>
            </div>
          </div>
        </article>
      </template>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  filteredNotifications,
  unreadCount,
  loadingNotifications,
  fetchNotifications,
  formatTimeAgo,
  markAsRead,
  markAllAsRead,
  NOTIFICATION_TYPES
} from '~/composables/useNotifications'

const activeTab = ref('all')

const isSameDay = (value) => {
  if (!value) return false
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return false
  const now = new Date()
  return date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
}

const todayCount = computed(() => filteredNotifications.value.filter(item => isSameDay(item.timestamp)).length)
const importantCount = computed(() => filteredNotifications.value.filter(item =>
  !item.read && (item.type === NOTIFICATION_TYPES.DANGER || item.type === NOTIFICATION_TYPES.WARNING)
).length)

const tabs = computed(() => [
  { value: 'all', label: 'Toutes', count: filteredNotifications.value.length },
  { value: 'unread', label: 'Non lues', count: unreadCount.value },
  { value: 'read', label: 'Lues', count: filteredNotifications.value.filter(item => item.read).length },
])

const visibleNotifications = computed(() => {
  if (activeTab.value === 'unread') return filteredNotifications.value.filter(item => !item.read)
  if (activeTab.value === 'read') return filteredNotifications.value.filter(item => item.read)
  return filteredNotifications.value
})

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

const getNotificationTargetLabel = (notification) => {
  if (notification?.payment) return 'Voir le paiement'
  if (notification?.booking) return 'Voir la reservation'
  if (notification?.material) return 'Voir le materiel'
  return 'Voir les details'
}

const openNotificationDetails = async (notification) => {
  if (!notification) return
  if (!notification.read) {
    await handleMarkAsRead(notification.id)
  }
  const target = getNotificationTarget(notification)
  if (!target) return
  await navigateTo(target)
}

const refreshPage = async () => {
  await fetchNotifications({ force: true }).catch(() => {})
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

const getTypeLabel = (type) => {
  switch (type) {
    case NOTIFICATION_TYPES.SUCCESS:
      return 'Succes'
    case NOTIFICATION_TYPES.WARNING:
      return 'Alerte'
    case NOTIFICATION_TYPES.DANGER:
      return 'Urgent'
    case NOTIFICATION_TYPES.INFO:
      return 'Info'
    default:
      return 'Notification'
  }
}

const getCategoryLabel = (category) => {
  switch (category) {
    case 'payment_received':
      return 'Paiement recu'
    case 'payment_overdue':
      return 'Paiement en retard'
    case 'low_inventory':
      return 'Stock faible'
    case 'out_of_stock':
      return 'Rupture de stock'
    default:
      return 'General'
  }
}

const buildDetailItems = (notification) => {
  const items = [
    { label: 'Categorie', value: getCategoryLabel(notification?.category) },
  ]

  if (notification?.booking_code) {
    items.push({ label: 'Reservation', value: notification.booking_code })
  }

  if (notification?.payment_code) {
    items.push({ label: 'Paiement', value: notification.payment_code })
  }

  if (notification?.material_name) {
    items.push({ label: 'Article', value: notification.material_name })
  }

  return items
}

const formatAbsoluteDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleString('fr-FR', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  fetchNotifications({ force: true }).catch(() => {})
})

definePageMeta({ layout: 'admin' })
</script>

<style scoped>
.notifications-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.hero-card {
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1.4fr 0.8fr;
  gap: var(--space-8);
  padding: var(--space-8);
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.22), transparent 30%),
    radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.10), transparent 35%),
    linear-gradient(135deg, #ffffff 0%, #f8fafc 55%, #f1f5f9 100%);
  border: 1px solid rgba(226, 232, 240, 0.95);
  box-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
}

.hero-copy {
  position: relative;
  z-index: 1;
}

.hero-badge {
  width: fit-content;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
  color: var(--gray-600);
  font-weight: 700;
  font-size: 0.82rem;
  margin-bottom: var(--space-5);
}

.hero-title {
  font-size: 2rem;
  line-height: 1.1;
  font-weight: 900;
  color: var(--gray-900);
  margin-bottom: var(--space-3);
}

.hero-subtitle {
  max-width: 620px;
  color: var(--gray-500);
  line-height: 1.7;
  font-size: 1rem;
}

.hero-actions {
  margin-top: var(--space-6);
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.hero-btn {
  min-height: 46px;
  padding-inline: 18px;
  border-radius: 14px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.btn-primary {
  border: none;
  color: #fff;
  background: linear-gradient(135deg, #d4af37, #c08f11);
  box-shadow: 0 10px 26px rgba(212, 175, 55, 0.28);
}

.btn-primary:hover {
  transform: translateY(-1px);
}

.btn-secondary {
  border: 1px solid var(--gray-200);
  color: var(--gray-600);
  background: rgba(255, 255, 255, 0.9);
}

.hero-visual {
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-ring {
  width: 220px;
  height: 220px;
  border-radius: 50%;
  padding: 16px;
  background:
    conic-gradient(from 180deg, rgba(212, 175, 55, 0.9), rgba(59, 130, 246, 0.2), rgba(212, 175, 55, 0.9));
  box-shadow: inset 0 0 30px rgba(255, 255, 255, 0.45), 0 18px 40px rgba(15, 23, 42, 0.10);
}

.hero-ring-inner {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.96);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 10px solid rgba(248, 250, 252, 0.95);
}

.hero-number {
  font-size: 3rem;
  font-weight: 900;
  line-height: 1;
  color: var(--gray-900);
}

.hero-label {
  margin-top: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--gray-500);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-5);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5);
  border-radius: 22px;
  border: 1px solid var(--gray-200);
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
}

.stat-icon {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
}

.stat-icon.primary {
  background: rgba(37, 99, 235, 0.12);
  color: #2563eb;
}

.stat-icon.accent {
  background: rgba(212, 175, 55, 0.16);
  color: #c08f11;
}

.stat-icon.info {
  background: rgba(14, 165, 233, 0.14);
  color: #0284c7;
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.14);
  color: #dc2626;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--gray-500);
  margin-bottom: 6px;
}

.stat-value {
  font-size: 1.7rem;
  line-height: 1;
  font-weight: 900;
  color: var(--gray-900);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-6);
  border-radius: 24px;
  border: 1px solid var(--gray-200);
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.toolbar-copy h2 {
  margin: 0 0 6px;
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--gray-900);
}

.toolbar-copy p {
  margin: 0;
  color: var(--gray-500);
}

.toolbar-tabs {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-radius: 18px;
  background: var(--gray-100);
  border: 1px solid var(--gray-200);
}

.tab-btn {
  border: none;
  background: transparent;
  color: var(--gray-600);
  font-weight: 800;
  padding: 12px 16px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
}

.tab-btn.active {
  background: var(--white);
  color: var(--gray-900);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.08);
}

.tab-count {
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 900;
  color: var(--gray-700);
}

.list-card {
  padding: var(--space-3);
  border-radius: 26px;
  border: 1px solid var(--gray-200);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.97), rgba(248, 250, 252, 0.97));
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.05);
}

.notification-item {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: var(--space-5);
  padding: var(--space-5);
  border-radius: 22px;
  border: 1px solid transparent;
  transition: all 0.25s ease;
  cursor: pointer;
}

.notification-item + .notification-item {
  margin-top: 10px;
}

.notification-item:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
}

.notification-item.unread {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(255, 255, 255, 0.95));
  border-color: rgba(212, 175, 55, 0.28);
}

.notification-item.type-danger.unread {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.06), rgba(255, 255, 255, 0.96));
  border-color: rgba(239, 68, 68, 0.20);
}

.notification-item.type-warning.unread {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.07), rgba(255, 255, 255, 0.96));
  border-color: rgba(245, 158, 11, 0.20);
}

.notification-side {
  position: relative;
}

.notification-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.35);
}

.notification-icon.success {
  background: rgba(34, 197, 94, 0.14);
  color: var(--success);
}

.notification-icon.warning {
  background: rgba(245, 158, 11, 0.14);
  color: var(--warning);
}

.notification-icon.danger {
  background: rgba(239, 68, 68, 0.14);
  color: var(--danger);
}

.notification-icon.info {
  background: rgba(59, 130, 246, 0.14);
  color: var(--info);
}

.pulse-dot {
  position: absolute;
  top: -4px;
  right: -2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--accent);
  border: 3px solid var(--white);
  box-shadow: 0 0 0 6px rgba(212, 175, 55, 0.12);
}

.notification-main {
  min-width: 0;
}

.notification-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
}

.notification-heading {
  min-width: 0;
}

.notification-title {
  margin: 0 0 10px;
  font-size: 1.08rem;
  font-weight: 900;
  color: var(--gray-900);
}

.notification-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.status-pill,
.type-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 12px;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 800;
}

.status-pill {
  background: var(--gray-200);
  color: var(--gray-600);
}

.status-pill.unread {
  background: rgba(212, 175, 55, 0.18);
  color: #9a6b00;
}

.type-pill.success {
  background: var(--success-bg);
  color: var(--success);
}

.type-pill.warning {
  background: var(--warning-bg);
  color: var(--warning);
}

.type-pill.danger {
  background: var(--danger-bg);
  color: var(--danger);
}

.type-pill.info {
  background: var(--info-bg);
  color: var(--info);
}

.notification-dates {
  text-align: right;
  flex-shrink: 0;
}

.relative-time {
  display: block;
  font-weight: 800;
  color: var(--gray-900);
  font-size: 0.88rem;
}

.absolute-time {
  display: block;
  margin-top: 6px;
  color: var(--gray-400);
  font-size: 0.8rem;
}

:global(html[data-admin-theme="dark"]) .hero-badge {
  background: rgba(255, 255, 255, 0.06);
}

:global(html[data-admin-theme="dark"]) .btn-secondary {
  background: rgba(255, 255, 255, 0.04);
}

:global(html[data-admin-theme="dark"]) .hero-ring {
  box-shadow: inset 0 0 30px rgba(255, 255, 255, 0.08), 0 18px 40px rgba(0, 0, 0, 0.35);
  background:
    conic-gradient(from 180deg, rgba(212, 175, 55, 0.75), rgba(59, 130, 246, 0.18), rgba(212, 175, 55, 0.75));
}

:global(html[data-admin-theme="dark"]) .hero-ring-inner {
  background: rgba(15, 23, 42, 0.88);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .stat-card {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(30, 41, 59, 0.95);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.22);
}

:global(html[data-admin-theme="dark"]) .toolbar {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.88) 0%, rgba(11, 18, 32, 0.92) 100%);
}

:global(html[data-admin-theme="dark"]) .toolbar-tabs {
  background: rgba(255, 255, 255, 0.06);
}

:global(html[data-admin-theme="dark"]) .tab-count {
  background: rgba(255, 255, 255, 0.10);
  color: var(--gray-900);
}

:global(html[data-admin-theme="dark"]) .tab-btn.active {
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.35);
}

:global(html[data-admin-theme="dark"]) .list-card {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(11, 18, 32, 0.92));
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22);
}

:global(html[data-admin-theme="dark"]) .notification-item:hover {
  background: rgba(255, 255, 255, 0.04);
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.28);
}

:global(html[data-admin-theme="dark"]) .notification-item {
  border-color: rgba(30, 41, 59, 0.95);
  background: rgba(255, 255, 255, 0.02);
}

:global(html[data-admin-theme="dark"]) .notification-title,
:global(html[data-admin-theme="dark"]) .relative-time,
:global(html[data-admin-theme="dark"]) .detail-value {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .absolute-time,
:global(html[data-admin-theme="dark"]) .detail-label {
  color: rgba(203, 213, 225, 0.78);
}

:global(html[data-admin-theme="dark"]) .notification-message {
  color: rgba(226, 232, 240, 0.9);
}

:global(html[data-admin-theme="dark"]) .status-pill {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(226, 232, 240, 0.85);
}

:global(html[data-admin-theme="dark"]) .status-pill.unread {
  color: #fde68a;
}

:global(html[data-admin-theme="dark"]) .notification-icon {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

:global(html[data-admin-theme="dark"]) .notification-item.unread {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.12), rgba(15, 23, 42, 0.86));
}

:global(html[data-admin-theme="dark"]) .notification-item.type-danger.unread {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.10), rgba(15, 23, 42, 0.88));
}

:global(html[data-admin-theme="dark"]) .notification-item.type-warning.unread {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(15, 23, 42, 0.88));
}

:global(html[data-admin-theme="dark"]) .pulse-dot {
  border-color: rgba(15, 23, 42, 0.92);
}

.notification-message {
  margin: 14px 0 0;
  color: var(--gray-600);
  line-height: 1.75;
  font-size: 0.96rem;
}

.notification-actions {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.notification-details {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 36px;
  padding: 0 12px;
  border-radius: 12px;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
}

.detail-label {
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--gray-500);
}

.detail-value {
  font-size: 0.85rem;
  font-weight: 800;
  color: var(--gray-900);
}

.inline-action.primary {
  color: var(--info);
  border-color: rgba(59, 130, 246, 0.2);
  background: rgba(59, 130, 246, 0.08);
}

.inline-action.primary:hover {
  color: #1e40af;
  border-color: rgba(59, 130, 246, 0.35);
  background: rgba(59, 130, 246, 0.14);
}

.inline-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: none;
  background: var(--gray-50);
  color: var(--gray-600);
  font-weight: 800;
  padding: 10px 14px;
  border-radius: 12px;
}

.inline-action.muted {
  background: transparent;
  color: var(--gray-400);
  padding-left: 0;
}

.empty-state {
  min-height: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-8);
}

.empty-illustration {
  width: 96px;
  height: 96px;
  border-radius: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.14), rgba(59, 130, 246, 0.12));
  color: var(--gray-500);
  font-size: 2rem;
  margin-bottom: var(--space-5);
}

.empty-state h2 {
  margin: 0 0 10px;
  color: var(--gray-900);
  font-size: 1.45rem;
  font-weight: 900;
}

.empty-state p {
  margin: 0;
  color: var(--gray-500);
  font-size: 0.98rem;
}

:global(html[data-admin-theme="dark"]) .hero-card {
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.14), transparent 30%),
    radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.10), transparent 35%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.92) 0%, rgba(11, 18, 32, 0.92) 100%);
  border-color: rgba(30, 41, 59, 0.95);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
}

:global(html[data-admin-theme="dark"]) .detail-chip {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .inline-action {
  background: rgba(255, 255, 255, 0.04);
}

:global(html[data-admin-theme="dark"] .notifications-page .hero-card) {
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.14), transparent 30%),
    radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.10), transparent 35%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.94) 0%, rgba(11, 18, 32, 0.94) 100%) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.32) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .stat-card) {
  background: rgba(15, 23, 42, 0.78) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.22) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .toolbar) {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.88) 0%, rgba(11, 18, 32, 0.92) 100%) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .list-card) {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.86), rgba(11, 18, 32, 0.92)) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.22) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .notification-item) {
  background: rgba(255, 255, 255, 0.02) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .notification-title),
:global(html[data-admin-theme="dark"] .notifications-page .relative-time),
:global(html[data-admin-theme="dark"] .notifications-page .detail-value) {
  color: #f8fafc !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .absolute-time),
:global(html[data-admin-theme="dark"] .notifications-page .detail-label) {
  color: rgba(203, 213, 225, 0.78) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .notification-item:hover) {
  background: rgba(255, 255, 255, 0.04) !important;
  box-shadow: 0 14px 32px rgba(0, 0, 0, 0.28) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .notification-item.unread) {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.12), rgba(15, 23, 42, 0.90)) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .notification-item.type-danger.unread) {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.10), rgba(15, 23, 42, 0.92)) !important;
}

:global(html[data-admin-theme="dark"] .notifications-page .notification-item.type-warning.unread) {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(15, 23, 42, 0.92)) !important;
}

@media (max-width: 1200px) {
  .hero-card {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    justify-content: flex-start;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .notifications-page {
    gap: var(--space-5);
  }

  .hero-card,
  .toolbar,
  .list-card {
    padding: var(--space-4);
  }

  .hero-title {
    font-size: 1.55rem;
  }

  .hero-ring {
    width: 170px;
    height: 170px;
  }

  .hero-number {
    font-size: 2.2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .toolbar-tabs {
    width: 100%;
    flex-wrap: wrap;
  }

  .notification-item {
    grid-template-columns: 1fr;
    gap: var(--space-4);
  }

  .notification-top {
    flex-direction: column;
  }

  .notification-dates {
    text-align: left;
  }

  .notification-side {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .pulse-dot {
    position: static;
  }
}
</style>
