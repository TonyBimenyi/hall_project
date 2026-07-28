<template>
  <ion-page class="home-page">
    <HeaderBar
      eyebrow="Tableau de bord"
      title="Accueil"
      :show-menu="false"
    >
      <template #actions>
        <div class="header-actions-shell">
          <ion-button
            fill="clear"
            class="header-cta-btn bell-btn"
            @click="toggleNotifications"
            :disabled="notificationsLoading"
          >
            <Icon icon="solar:bell-linear" class="header-cta-icon" />
            <span v-if="unreadCount > 0" class="bell-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
          </ion-button>
        </div>
      </template>
    </HeaderBar>

    <ion-content class="home-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement du tableau de bord"
      />
      <div class="content-shell">

        <section class="hero-card">
          <div class="hero-copy">
            <small class="hero-eyebrow">{{ todayLabel }}</small>
            <h1 class="hero-title">Bonjour, <span class="hero-accent">{{ displayUserFull }}</span></h1>
            <div class="hero-role-row">
              <span class="hero-role-chip">
                <Icon icon="solar:shield-user-linear" class="hero-role-ic" />
                <span class="hero-role-text">{{ displayRole }}</span>
              </span>
              <span class="hero-user-initials">{{ userInitials }}</span>
            </div>
            <p class="hero-sub">Un aperçu clair des arrivées, des revenus et des salles disponibles.</p>
          </div>
          <div class="hero-mark" aria-hidden="true">
            <div class="hero-mark-inner">
              <Icon icon="solar:stars-linear" />
            </div>
          </div>
        </section>

        <section class="stats-grid">
          <StatCard
            label="Réservations du jour"
            :value="stats.todayBookings"
            caption="Séjours / événements"
            delta="+12%"
            delta-tone="positive"
            icon="solar:calendar-linear"
            variant="primary"
          />
          <StatCard
            label="Revenus (mois)"
            :value="stats.monthRevenue"
            caption="Paiements encaissés"
            delta="+4.3%"
            delta-tone="positive"
            icon="solar:wallet-money-linear"
            variant="gold"
          />
          <StatCard
            label="Chambres occupées"
            :value="stats.occupiedRooms"
            :caption="occupancyCaption"
            delta="Taux élevé"
            delta-tone="neutral"
            icon="solar:bed-linear"
            variant="default"
          />
          <StatCard
            label="Clients à l'arrivée"
            :value="stats.arrivalsToday"
            caption="Check-in aujourd'hui"
            delta="À accueillir"
            delta-tone="neutral"
            icon="solar:users-group-rounded-linear"
            variant="teal"
          />
        </section>

        <section class="section-block">
          <div class="section-head">
            <div>
              <div class="section-kicker">À venir</div>
              <h2 class="section-title">Réservations récentes</h2>
            </div>
            <ion-button router-link="/bookings" fill="clear" class="section-link">
              Voir tout
              <Icon icon="solar:arrow-right-linear" class="section-link-icon" />
            </ion-button>
          </div>

          <div class="section-divider" aria-hidden="true"></div>

          <div class="bookings-stack">
            <BookingCard
              v-for="booking in recentBookings"
              :key="booking.id"
              :booking="booking"
              @click="openBooking(booking)"
              @view="openBooking"
              @edit="toastEdit"
              @delete="handleDeleteBooking"
            />
            <div v-if="!recentBookings.length" class="empty-block">
              <Icon icon="solar:documents-linear" class="empty-icon" />
              <p>Aucune réservation récente.</p>
            </div>
          </div>
        </section>

        <section class="section-block">
          <div class="section-head">
            <div>
              <div class="section-kicker">Chambres &amp; Salles</div>
              <h2 class="section-title">Chambres à la une</h2>
            </div>
            <ion-button router-link="/rooms" fill="clear" class="section-link">
              Toutes
              <Icon icon="solar:arrow-right-linear" class="section-link-icon" />
            </ion-button>
          </div>

          <div class="section-divider" aria-hidden="true"></div>

          <div class="rooms-stack">
            <RoomCard
              v-for="room in featuredRooms"
              :key="room.id"
              :room="room"
              @view="toastRoomView"
              @edit="toastRoomEdit"
              @delete="handleDeleteRoom"
            />
          </div>
        </section>

        <div class="page-bottom-spacer" />
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end" class="fab-shell">
        <ion-fab-button class="fab-main" @click="toastNewBooking">
          <Icon icon="solar:add-linear" width="30" height="30" style="width:30px;height:30px;display:block" />
        </ion-fab-button>
      </ion-fab>
    </ion-content>

    <div
      v-if="notificationsOpen"
      class="notif-backdrop"
      @click="closeNotifications"
    />
    <div
      v-if="notificationsOpen"
      class="notif-panel"
      role="dialog"
      aria-label="Notifications"
      @click.stop
    >
      <div class="notif-panel-head">
        <div>
          <div class="notif-panel-kicker">Centre</div>
          <h3 class="notif-panel-title">Notifications <span v-if="unreadCount" class="notif-unread-chip">{{ unreadCount }} nouvelle{{ unreadCount > 1 ? 's' : '' }}</span></h3>
        </div>
        <button
          v-if="unreadCount > 0"
          class="notif-mark-all"
          type="button"
          @click="markAllRead"
        >
          Tout marquer lu
        </button>
      </div>
      <div class="notif-panel-hairline" aria-hidden="true"></div>
      <div class="notif-list">
        <div v-if="notificationsLoading" class="notif-empty loading">
          <Icon icon="solar:loader-linear" class="spin" />
          <span>Chargement…</span>
        </div>
        <template v-else-if="notifications.length">
          <button
            v-for="item in notifications"
            :key="item.id"
            type="button"
            class="notif-item"
            :class="{ unread: !item.read }"
            @click="openNotification(item)"
          >
            <span class="notif-icon" :style="{ background: iconBgFor(item.type), color: iconColorFor(item.type) }">
              <Icon :icon="iconFor(item.type)" />
            </span>
            <span class="notif-copy">
              <span class="notif-title">{{ item.title }}</span>
              <span class="notif-body">{{ item.message }}</span>
              <span class="notif-meta">{{ formatRelative(item.created_at) }}</span>
            </span>
            <span v-if="!item.read" class="notif-dot" aria-hidden="true"></span>
          </button>
        </template>
        <div v-else class="notif-empty">
          <Icon icon="solar:documents-linear" class="notif-empty-icon" />
          <span>Aucune notification pour le moment.</span>
        </div>
      </div>
    </div>
  </ion-page>
</template>

<script>
import {
  IonButton,
  IonContent,
  IonFab,
  IonFabButton,
  IonPage
} from '@ionic/vue'
import { endpoints, getStoredUser, saveAuthSession } from '@/lib/api.js'
import HeaderBar from '@/components/HeaderBar.vue'
import StatCard from '@/components/StatCard.vue'
import BookingCard from '@/components/BookingCard.vue'
import RoomCard from '@/components/RoomCard.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const MOCK_STATS = {
  todayBookings: '—',
  monthRevenue: '— Fbu',
  occupiedRooms: '— / —',
  arrivalsToday: '—'
}

const MOCK_NOTIFICATIONS = [
  {
    id: 'n1',
    type: 'booking',
    title: 'Nouvelle réservation',
    message: 'Jeanine Ndayikengurukiye a réservé la Salle Royale pour le 28 juin.',
    read: false,
    created_at: new Date(Date.now() - 18 * 60 * 1000).toISOString()
  },
  {
    id: 'n2',
    type: 'payment',
    title: 'Paiement reçu',
    message: 'Paiement de 1 840 000 Fbu reçu pour RSV-0625-0041.',
    read: false,
    created_at: new Date(Date.now() - 120 * 60 * 1000).toISOString()
  },
  {
    id: 'n3',
    type: 'room',
    title: 'Chambre libérée',
    message: 'La chambre 202 — Chambre Simple Standard est prête pour le prochain client.',
    read: true,
    created_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString()
  },
  {
    id: 'n4',
    type: 'alert',
    title: 'Stock faible',
    message: 'Le stock de "Savon premium" est en dessous du seuil d\'alerte.',
    read: true,
    created_at: new Date(Date.now() - 24 * 3600 * 1000).toISOString()
  }
]

export default {
  name: 'HomeView',
  components: {
    IonButton,
    IonContent,
    IonFab,
    IonFabButton,
    IonPage,
    HeaderBar,
    StatCard,
    BookingCard,
    RoomCard,
    LoadingOverlay
  },
  data() {
    return {
      loadingSummary: false,
      loadingBookings: false,
      loadingRooms: false,
      stats: { ...MOCK_STATS },
      recentBookings: [],
      featuredRooms: [],
      notificationsOpen: false,
      notificationsLoading: false,
      notifications: [],
      storedUser: null
    }
  },
  computed: {
    todayLabel() {
      try {
        return new Date().toLocaleDateString('fr-FR', {
          weekday: 'long',
          day: 'numeric',
          month: 'long',
          year: 'numeric'
        })
      } catch (_) {
        return "Aujourd'hui"
      }
    },
    storedUserObj() {
      const a = this.storedUser || null
      const b = getStoredUser() || null
      const merged = {}
      if (b && typeof b === 'object') Object.assign(merged, b)
      if (a && typeof a === 'object') Object.assign(merged, a)
      return merged
    },
    displayUserFull() {
      const u = this.storedUserObj
      if (u?.full_name) {
        const v = String(u.full_name).trim()
        if (v && v !== 'Invité') return v
      }
      if (u?.first_name || u?.last_name) {
        const v = [u.first_name, u.last_name].filter(Boolean).join(' ').trim()
        if (v) return v
      }
      if (u?.name) {
        const v = String(u.name).trim()
        if (v) return v
      }
      if (u?.username) {
        const v = String(u.username).trim()
        if (v) return v
      }
      if (u?.email) {
        const v = String(u.email).trim().split('@')[0]
        if (v) return v.charAt(0).toUpperCase() + v.slice(1)
      }
      try {
        const stored = JSON.parse(localStorage.getItem('user') || 'null')
        if (stored && typeof stored === 'object') {
          const fallback = stored.full_name || stored.username || stored.name || (stored.email && stored.email.split('@')[0])
          if (fallback) return typeof fallback === 'string' && fallback.charAt ? fallback.charAt(0).toUpperCase() + fallback.slice(1) : fallback
        }
      } catch (_e) {}
      const rawLs = localStorage?.user_name
      if (rawLs) return String(rawLs)
      return 'Invité'
    },
    userInitials() {
      const name = String(this.displayUserFull || '').trim()
      if (!name || name === 'Invité') {
        const u = this.storedUserObj
        const fromU = [u?.username, u?.email].filter(Boolean)[0]
        if (fromU) return String(fromU).slice(0, 2).toUpperCase()
        return 'IN'
      }
      const parts = name.split(/\s+/).filter(Boolean)
      const first = parts[0]?.[0]?.toUpperCase() || ''
      const last = parts[1]?.[0]?.toUpperCase() || parts[0]?.[1]?.toUpperCase() || ''
      return (first + last) || name.slice(0, 2).toUpperCase()
    },
    displayRole() {
      const u = this.storedUserObj
      const r = u?.role || u?.user_type || u?.type || ''
      if (r) {
        const map = {
          admin: 'Administrateur',
          receptionist: 'Réceptionniste',
          manager: 'Directeur',
          accountant: 'Comptable',
          staff: 'Personnel',
          owner: 'Propriétaire'
        }
        const key = String(r).toLowerCase()
        return map[key] || r
      }
      return 'Administrateur'
    },
    occupancyCaption() {
      return 'Toutes les chambres de l\'établissement'
    },
    unreadCount() {
      return this.notifications.filter((n) => !n.read).length
    },
    showLoading() {
      return this.loadingSummary || this.loadingBookings || this.loadingRooms
    }
  },
  methods: {
    toggleNotifications(e) {
      if (e && typeof e.stopPropagation === 'function') e.stopPropagation()
      if (this.notificationsOpen) {
        this.closeNotifications()
      } else {
        this.openNotifications()
      }
    },
    openNotifications() {
      this.notificationsOpen = true
      this.loadNotifications()
    },
    closeNotifications() {
      this.notificationsOpen = false
    },
    async loadNotifications() {
      this.notificationsLoading = true
      try {
        const res = await endpoints.notifications({ ordering: '-created_at', page_size: 25 })
        const list = Array.isArray(res) ? res : (res?.results || [])
        if (list.length) {
          this.notifications = list.map((n) => this.mapNotification(n))
        } else {
          this.notifications = []
        }
      } catch (_err) {
        this.notifications = []
      } finally {
        this.notificationsLoading = false
      }
    },
    mapNotification(n) {
      if (!n) return null
      return {
        id: n.id,
        type: n.type || n.category || 'info',
        title: n.title || n.subject || 'Notification',
        message: n.message || n.body || n.text || '',
        read: Boolean(n.read || n.is_read || n.seen),
        created_at: n.created_at || n.timestamp || new Date().toISOString(),
        booking_id: n.booking_id,
        customer_id: n.customer_id
      }
    },
    iconFor(type) {
      switch (type) {
        case 'booking':
        case 'reservation':
          return 'solar:calendar-linear'
        case 'payment':
          return 'solar:wallet-money-linear'
        case 'room':
          return 'solar:bed-linear'
        case 'expense':
          return 'solar:bill-linear'
        case 'alert':
        case 'warning':
          return 'solar:bell-bing-linear'
        default:
          return 'solar:info-circle-linear'
      }
    },
    iconBgFor(type) {
      switch (type) {
        case 'booking':
        case 'reservation':
          return 'rgba(215, 111, 2, 0.10)'
        case 'payment':
          return 'rgba(22, 163, 74, 0.10)'
        case 'room':
          return 'rgba(26, 58, 122, 0.10)'
        case 'expense':
          return 'rgba(239, 68, 68, 0.10)'
        case 'alert':
        case 'warning':
          return 'rgba(212, 175, 55, 0.12)'
        default:
          return 'rgba(100, 116, 139, 0.10)'
      }
    },
    iconColorFor(type) {
      switch (type) {
        case 'booking':
        case 'reservation':
          return '#d76f02'
        case 'payment':
          return '#16a34a'
        case 'room':
          return '#1a3a7a'
        case 'expense':
          return '#ef4444'
        case 'alert':
        case 'warning':
          return '#d4af37'
        default:
          return '#475569'
      }
    },
    formatRelative(iso) {
      if (!iso) return ''
      const d = new Date(iso)
      if (Number.isNaN(d.getTime())) return ''
      const diffMs = Date.now() - d.getTime()
      const min = Math.round(diffMs / 60000)
      if (min < 1) return "À l'instant"
      if (min < 60) return `Il y a ${min} min`
      const hrs = Math.round(min / 60)
      if (hrs < 24) return `Il y a ${hrs} h`
      const days = Math.round(hrs / 24)
      if (days < 7) return `Il y a ${days} j`
      try {
        return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
      } catch (_) {
        return d.toLocaleDateString()
      }
    },
    markAllRead() {
      try {
        endpoints.notificationMarkAllRead().catch(() => null)
      } catch (_e) {}
      this.notifications.forEach((n) => { n.read = true })
    },
    openNotification(item) {
      if (!item) return
      if (!item.read) {
        if (item?.id != null) {
          try {
            endpoints.notificationMarkRead(item.id).catch(() => null)
          } catch (_e) {}
        }
        item.read = true
      }
      if (item?.booking_id) {
        this.$router.push(`/bookings/${item.booking_id}`)
      }
    },
    openBooking(booking) {
      if (!booking?.id) return
      this.$router.push(`/bookings/${booking.id}`)
    },
    toastEdit() {
      alert('Modification réservation (à venir)')
    },
    toastRoomView() {
      this.$router.push('/rooms')
    },
    toastRoomEdit() {
      alert('Modification chambre (à venir)')
    },
    handleDeleteBooking(b) {
      try {
        endpoints.deleteBooking && endpoints.deleteBooking(b?.id).catch(() => null)
      } catch (_) {}
      this.recentBookings = this.recentBookings.filter((x) => x.id !== b?.id)
    },
    handleDeleteRoom(r) {
      try {
        endpoints.deleteRoom && endpoints.deleteRoom(r?.id).catch(() => null)
      } catch (_) {}
      this.featuredRooms = this.featuredRooms.filter((x) => x.id !== r?.id)
    },
    toastNewBooking() {
      alert('Nouvelle réservation (à venir)')
    },
    formatRevenue(value) {
      const n = Number(value || 0)
      try {
        return n.toLocaleString('fr-FR') + ' Fbu'
      } catch (_) {
        return `${n.toFixed(0)} Fbu`
      }
    },
    buildRoomDisplay(booking) {
      if (booking?.room_display) return booking.room_display
      const items = booking?.items
      if (Array.isArray(items) && items.length) {
        const first = items[0]
        const num = first?.room_number || first?.room?.room_number || ''
        const name = first?.room_name || first?.room?.name || ''
        if (num && name) return `${num} — ${name}`
        if (name) return name
        if (num) return num
      }
      return '-'
    },
    mapBooking(booking) {
      if (!booking) return null
      return {
        id: booking.id,
        code: booking.display_id || booking.code || `#${booking.id || ''}`,
        customer_name: booking.customer_name || booking.customer?.full_name || 'Client inconnu',
        booking_type: booking.booking_type,
        hall_name: booking.hall?.name || booking.hall_name,
        room_display: this.buildRoomDisplay(booking),
        status: booking.status,
        total_price: booking.total_price,
        start_date: booking.start_date,
        end_date: booking.end_date
      }
    },
    mapRoom(room) {
      if (!room) return null
      return {
        id: room.id,
        room_number: room.room_number,
        name: room.name || room.room_name || room.type_name || '',
        room_type: room.room_type || room.type || '',
        status: room.status || room.state || 'available',
        capacity: room.capacity,
        price_per_night: room.price_per_night || room.price || 0,
        additional_services: Array.isArray(room.additional_services)
          ? room.additional_services
          : []
      }
    },
    applySummary(summary, rawBookings, rawRooms) {
      const s = { ...this.stats }
      const bookings = Array.isArray(rawBookings) ? rawBookings : []
      const rooms = Array.isArray(rawRooms) ? rawRooms : []
      const todayIso = new Date().toISOString().slice(0, 10)
      const now = new Date()
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10)
      const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().slice(0, 10)
      if (summary && typeof summary === 'object') {
        const todayBookingsVal = [
          summary.bookings_today,
          summary.bookingsToday,
          summary.today_bookings,
          summary.total_bookings_today,
          summary.todayBookingsCount,
          summary.count_bookings_today
        ].find((v) => v != null && v !== '')
        if (todayBookingsVal != null) s.todayBookings = todayBookingsVal
        const revenueVal = [
          summary.revenue_month,
          summary.month_revenue,
          summary.monthly_revenue,
          summary.revenueMonth,
          summary.revenu_mois,
          summary.total_revenue_month
        ].find((v) => v != null && v !== '')
        if (revenueVal != null) s.monthRevenue = this.formatRevenue(revenueVal)
        const occupiedVal = [
          summary.rooms_occupied,
          summary.occupied_rooms,
          summary.roomsOccupied,
          summary.occupied_count,
          summary.chambres_occupees
        ].find((v) => v != null && v !== '')
        const totalVal = [
          summary.rooms_total,
          summary.total_rooms,
          summary.roomsTotal,
          summary.total_count,
          summary.chambres_total
        ].find((v) => v != null && v !== '')
        if (occupiedVal != null && totalVal != null) {
          s.occupiedRooms = `${occupiedVal}/${totalVal}`
        } else if (occupiedVal != null && rooms.length) {
          s.occupiedRooms = `${occupiedVal}/${rooms.length}`
        }
        const arrivalsVal = [
          summary.arrivals_today,
          summary.arrivalsToday,
          summary.today_arrivals,
          summary.todayArrivals,
          summary.arrivees_aujourdhui
        ].find((v) => v != null && v !== '')
        if (arrivalsVal != null) s.arrivalsToday = arrivalsVal
      }
      if (s.todayBookings === MOCK_STATS.todayBookings && bookings.length) {
        const count = bookings.filter((b) => {
          const d = (b.start_date || b.check_in || b.date_arrivee || '').toString().slice(0, 10)
          return d === todayIso
        }).length
        if (count) s.todayBookings = count
      }
      if (s.monthRevenue === MOCK_STATS.monthRevenue && bookings.length) {
        const monthBookings = bookings.filter((b) => {
          const d = (b.start_date || b.created_at || b.date_reservation || '').toString().slice(0, 10)
          return d && d >= monthStart && d <= monthEnd
        })
        const total = monthBookings.reduce((acc, b) => {
          const amt = Number(b.amount_paid || b.total_paid || b.montant_paye || b.total_price || b.prix_total || 0)
          return acc + amt
        }, 0)
        if (total > 0) s.monthRevenue = this.formatRevenue(total)
      }
      if (s.occupiedRooms === MOCK_STATS.occupiedRooms && rooms.length) {
        const busy = ['occupied', 'reserved', 'occupee', 'reservee', 'en_cours', 'maintenance', 'cleaning']
        const occupiedCount = rooms.filter((r) => {
          const st = String(r.status || r.state || r.etat || 'available').toLowerCase()
          return busy.indexOf(st) !== -1
        }).length
        s.occupiedRooms = `${occupiedCount}/${rooms.length}`
      }
      if (s.arrivalsToday === MOCK_STATS.arrivalsToday && bookings.length) {
        const count = bookings.filter((b) => {
          const st = String(b.status || b.statut || '').toLowerCase()
          const isArrival = st === 'confirmed' || st === 'confirmee' || st === 'checkin' || st === 'arrival' || st === 'en_attente'
          const d = (b.start_date || b.check_in || b.date_arrivee || '').toString().slice(0, 10)
          return d === todayIso && isArrival
        }).length
        if (count) s.arrivalsToday = count
      }
      this.stats = s
    },
    applyBookings(result) {
      let list = []
      if (Array.isArray(result)) {
        list = result
      } else if (result && Array.isArray(result.results)) {
        list = result.results
      }
      const mapped = list
        .map((b) => this.mapBooking(b))
        .filter(Boolean)
        .slice(0, 3)
      this.recentBookings = mapped
    },
    applyRooms(result) {
      let list = []
      if (Array.isArray(result)) {
        list = result
      } else if (result && Array.isArray(result.results)) {
        list = result.results
      }
      const priority = ['occupied', 'reserved', 'cleaning', 'available']
      const sortKey = (r) => {
        const s = String(r.status || '').toLowerCase()
        const p = priority.indexOf(s)
        return p === -1 ? 99 : p
      }
      const mapped = [...list]
        .sort((a, b) => sortKey(a) - sortKey(b))
        .map((r) => this.mapRoom(r))
        .filter(Boolean)
        .slice(0, 3)
      this.featuredRooms = mapped
    },
    async refreshUser() {
      try {
        const user = await endpoints.me()
        if (user && typeof user === 'object') {
          this.storedUser = user
          const access = localStorage.getItem('access_token')
          const refresh = localStorage.getItem('refresh_token')
          saveAuthSession({ access, refresh, user })
        }
      } catch (_e) {}
    },
    async loadData() {
      this.loadingSummary = true
      this.loadingBookings = true
      this.loadingRooms = true
      try {
        const promises = [
          endpoints.summary().catch(() => null),
          endpoints.bookings({ ordering: '-created_at', page_size: 100 }).catch(() => null),
          endpoints.rooms({ page_size: 200 }).catch(() => null),
          this.refreshUser()
        ]
        const [summary, bookingsResult, roomsResult] = await Promise.all(promises)
        const rawBookings = Array.isArray(bookingsResult)
          ? bookingsResult
          : (bookingsResult && Array.isArray(bookingsResult.results) ? bookingsResult.results : [])
        const rawRooms = Array.isArray(roomsResult)
          ? roomsResult
          : (roomsResult && Array.isArray(roomsResult.results) ? roomsResult.results : [])
        this.applySummary(summary || null, rawBookings, rawRooms)
        if (bookingsResult) {
          this.applyBookings(bookingsResult)
        }
        if (roomsResult) {
          this.applyRooms(roomsResult)
        }
      } catch (_) {
      } finally {
        this.loadingSummary = false
        this.loadingBookings = false
        this.loadingRooms = false
      }
    }
  },
  mounted() {
    this.storedUser = getStoredUser()
    this.loadData()
    this.notifications = []
  }
}
</script>

<style scoped>
.home-page {
  background: #fbf7f2;
}

.home-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
  position: relative;
  z-index: 1;
}

.hero-card {
  margin-top: 18px;
  margin-bottom: 20px;
  padding: 22px 20px 20px;
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.18), transparent 44%),
    linear-gradient(135deg, #1a3a7a 0%, #17336b 55%, #1a3a7a 100%);
  color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 22px 42px rgba(26, 58, 122, 0.24);
}

.hero-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hero-eyebrow {
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d4af37;
  font-weight: 700;
}

.hero-title {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: 0.005em;
  font-family: 'Playfair Display', Georgia, serif;
}

.hero-accent {
  color: #ffffff;
  font-weight: 800;
}

.hero-role-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-role-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 11px;
  border-radius: 999px;
  background: rgba(212, 175, 55, 0.18);
  border: 1px solid rgba(212, 175, 55, 0.32);
  color: #f5e5a5;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.hero-role-ic {
  font-size: 0.9rem;
  color: #d4af37;
}

.hero-user-initials {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: linear-gradient(135deg, #d76f02, #e68a33);
  color: #ffffff;
  font-weight: 800;
  letter-spacing: 0.02em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(215, 111, 2, 0.32);
  font-size: 0.9rem;
  border: 2px solid rgba(255, 255, 255, 0.18);
}

.hero-sub {
  margin: 0;
  color: rgba(248, 250, 252, 0.82);
  font-size: 0.88rem;
  line-height: 1.45;
  max-width: 36ch;
}

.hero-mark {
  flex: 0 0 auto;
  width: 58px;
  height: 58px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(6px);
}

.hero-mark-inner {
  width: 38px;
  height: 38px;
  border-radius: 14px;
  background: rgba(212, 175, 55, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4af37;
  font-size: 1.3rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 8px;
}

.section-block {
  margin-top: 22px;
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 0 2px;
}

.section-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.section-title {
  margin: 6px 0 0;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.005em;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
}

.section-divider {
  margin: 12px 2px 14px;
  height: 1px;
  background: rgba(23, 11, 2, 0.08);
}

.section-link {
  --color: #d76f02;
  --background-hover: rgba(215, 111, 2, 0.05);
  font-weight: 700;
  font-size: 0.86rem;
  letter-spacing: 0.01em;
  padding: 6px 8px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.section-link-icon {
  font-size: 0.95rem;
}

.bookings-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rooms-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-block {
  padding: 28px 18px;
  border-radius: 20px;
  border: 1px dashed rgba(23, 11, 2, 0.08);
  background: rgba(251, 247, 242, 0.8);
  text-align: center;
  color: #64748b;
  font-size: 0.9rem;
}

.empty-icon {
  font-size: 1.6rem;
  color: #94a3b8;
  margin-bottom: 6px;
  display: inline-block;
}

.header-actions-shell {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.header-cta-btn {
  --background-hover: rgba(23, 11, 2, 0.06);
  --color: #170b02;
  width: 40px;
  height: 40px;
  border-radius: 14px;
  position: relative;
}

.header-cta-icon {
  font-size: 1.25rem;
}

.bell-btn {
  overflow: visible;
}

.bell-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: #ef4444;
  color: #ffffff;
  font-size: 0.6rem;
  font-weight: 800;
  letter-spacing: 0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid #ffffff;
  pointer-events: none;
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.4);
}

.notif-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.38);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  z-index: 50;
}

.notif-panel {
  position: fixed;
  z-index: 51;
  top: calc(70px + env(safe-area-inset-top));
  right: 12px;
  left: 12px;
  max-width: calc(min(420px, 100vw - 24px));
  max-height: calc(min(72vh, 620px));
  margin-left: auto;
  margin-right: auto;
  background: #ffffff;
  border-radius: 22px;
  border: 1px solid rgba(23, 11, 2, 0.08);
  box-shadow:
    0 30px 80px rgba(15, 23, 42, 0.28),
    0 8px 24px rgba(15, 23, 42, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transform-origin: top right;
  animation: notifIn 180ms cubic-bezier(0.22, 1, 0.36, 1);
}

@keyframes notifIn {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.notif-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 18px 14px;
}

.notif-panel-kicker {
  font-size: 0.65rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.notif-panel-title {
  margin: 4px 0 0;
  font-size: 1.02rem;
  font-weight: 800;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
  display: flex;
  align-items: center;
  gap: 8px;
}

.notif-unread-chip {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(215, 111, 2, 0.10);
  color: #d76f02;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  font-family: 'Inter', sans-serif;
}

.notif-mark-all {
  border: none;
  background: rgba(215, 111, 2, 0.08);
  color: #d76f02;
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.18s ease;
}
.notif-mark-all:active { background: rgba(215, 111, 2, 0.16); }

.notif-panel-hairline {
  height: 1px;
  margin: 0 18px;
  background: rgba(23, 11, 2, 0.08);
}

.notif-list {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  padding: 8px 0 10px;
  flex: 1 1 auto;
}

.notif-item {
  width: 100%;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 18px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(23, 11, 2, 0.05);
  text-align: left;
  cursor: pointer;
  transition: background 0.16s ease;
  position: relative;
}
.notif-item:last-child { border-bottom: none; }
.notif-item:active { background: rgba(23, 11, 2, 0.04); }
.notif-item.unread { background: rgba(215, 111, 2, 0.035); }

.notif-icon {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  font-size: 1.05rem;
}

.notif-copy {
  min-width: 0;
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-right: 10px;
}

.notif-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #170b02;
  line-height: 1.3;
}
.notif-item.unread .notif-title { color: #170b02; font-weight: 800; }

.notif-body {
  font-size: 0.82rem;
  color: #475569;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notif-meta {
  margin-top: 4px;
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.notif-dot {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #d76f02;
  box-shadow: 0 0 0 3px rgba(215, 111, 2, 0.12);
}

.notif-empty {
  padding: 30px 22px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.88rem;
  text-align: center;
}
.notif-empty.loading { flex-direction: row; gap: 10px; }
.notif-empty-icon { font-size: 1.6rem; color: #94a3b8; }

.spin {
  animation: spin 900ms linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}

.page-bottom-spacer {
  height: 110px;
}

.fab-shell {
  --ion-fab-margin-bottom: calc(84px + env(safe-area-inset-bottom));
  --ion-fab-margin-end: 16px;
}

:deep(.fab-shell .fab-main) {
  --background: linear-gradient(135deg, #d76f02, #e68a33);
  --background-activated: #c36202;
  --background-hover: #e68a33;
  --color: #ffffff;
  --border-radius: 22px;
  width: 58px;
  height: 58px;
  box-shadow: 0 16px 40px rgba(215,111,2,0.42);
}

:deep(.fab-shell ion-fab-button .iconify,
       .fab-shell ion-fab-button svg,
       .fab-shell ion-fab-button [data-icon]) {
  width: 26px !important;
  height: 26px !important;
  max-width: 26px !important;
  max-height: 26px !important;
  display: inline-block !important;
  opacity: 1 !important;
  visibility: visible !important;
}

:deep(.fab-shell .fab-main .iconify,
       .fab-shell .fab-main svg) {
  width: 30px !important;
  height: 30px !important;
  max-width: 30px !important;
  max-height: 30px !important;
}

@media (min-width: 768px) {
  .content-shell {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
  }

  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .notif-panel {
    right: max(24px, calc((100vw - 900px) / 2 + 24px));
    left: auto;
    width: 380px;
    margin: 0;
  }
}

@media print {
  ion-header,
  ion-tab-bar,
  .fab-shell,
  .bell-btn,
  .notif-panel,
  .notif-backdrop {
    display: none !important;
  }
  .home-content { --background: #ffffff; }
  .home-page { background: #ffffff; }
}
</style>
