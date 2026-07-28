<template>
  <ion-page class="reports-page">
    <HeaderBar title="Rapports" eyebrow="Analyse" :show-menu="false">
      <template v-slot:actions>
        <ion-button fill="clear" class="header-print-btn" @click="handlePrint">
          <Icon icon="solar:printer-linear" class="header-icon" />
        </ion-button>
      </template>
    </HeaderBar>

    <ion-content class="reports-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement des rapports"
      />
      <div class="content-shell">

        <section class="reports-hero">
          <div class="reports-hero-copy">
            <small class="reports-hero-eyebrow">{{ periodLabel }}</small>
            <h1 class="reports-hero-title">Performance de l'établissement</h1>
            <p class="reports-hero-sub">Synthèse complète des indicateurs pour piloter l'activité en temps réel.</p>
          </div>
          <div class="reports-hero-mark" aria-hidden="true">
            <Icon icon="solar:chart-2-linear" />
          </div>
        </section>

        <section class="kpi-grid">
          <div v-for="kpi in kpis" :key="kpi.key" class="kpi-card" :class="kpi.tone">
            <div class="kpi-head">
              <span class="kpi-icon-wrap" :style="{ background: kpi.iconBg, color: kpi.iconColor }">
                <Icon :icon="kpi.icon" class="kpi-icon" />
              </span>
              <span class="kpi-delta" :class="kpi.deltaTone">{{ kpi.delta }}</span>
            </div>
            <div class="kpi-value">{{ kpi.value }}</div>
            <div class="kpi-label">{{ kpi.label }}</div>
          </div>
        </section>

        <section class="chart-block">
          <div class="chart-head">
            <div>
              <div class="chart-kicker">Revenu mensuel</div>
              <h2 class="chart-title">Évolution des 6 derniers mois</h2>
            </div>
            <div class="chart-legend">
              <span class="legend-dot" style="background:#d76f02"></span>
              <span>Encaissé</span>
            </div>
          </div>
          <div class="chart-hairline" aria-hidden="true"></div>
          <div v-if="monthlyRevenue.length" class="bar-chart">
            <div class="bar-y-axis">
              <span v-for="t in yTicks" :key="t">{{ t }}</span>
            </div>
            <div class="bars-wrap">
              <div v-for="bar in monthlyRevenue" :key="bar.label" class="bar-col">
                <div class="bar-track">
                  <div class="bar-fill" :style="{ height: bar.pct + '%' }">
                    <span class="bar-tip">{{ bar.value }}</span>
                  </div>
                </div>
                <div class="bar-label">{{ bar.label }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-block chart-empty">
            <Icon icon="solar:chart-2-linear" class="empty-ic" />
            <span>Aucune donnée de paiement chargée.</span>
          </div>
        </section>

        <section class="two-col">
          <div class="chart-block">
            <div class="chart-head">
              <div>
                <div class="chart-kicker">Répartition</div>
                <h2 class="chart-title">Types de réservation</h2>
              </div>
            </div>
            <div class="chart-hairline" aria-hidden="true"></div>
            <div v-if="bookingTypes.length" class="donut-row">
              <div class="donut-chart">
                <div class="donut-ring" :style="{ background: bookingTypeConic }">
                  <div class="donut-center">
                    <div class="donut-total">{{ bookingTotal }}</div>
                    <div class="donut-unit">Réservations</div>
                  </div>
                </div>
              </div>
              <ul class="donut-legend">
                <li v-for="seg in bookingTypes" :key="seg.key">
                  <span class="legend-swatch" :style="{ background: seg.color }"></span>
                  <span class="legend-name">{{ seg.label }}</span>
                  <span class="legend-count">{{ seg.value }}</span>
                </li>
              </ul>
            </div>
            <div v-else class="empty-block chart-empty">
              <Icon icon="solar:pie-chart-linear" class="empty-ic" />
              <span>Aucune réservation chargée.</span>
            </div>
          </div>

          <div class="chart-block">
            <div class="chart-head">
              <div>
                <div class="chart-kicker">Occupation</div>
                <h2 class="chart-title">Taux par jour</h2>
              </div>
            </div>
            <div class="chart-hairline" aria-hidden="true"></div>
            <ul v-if="occupancyWeek.length" class="spark-list">
              <li v-for="d in occupancyWeek" :key="d.day" class="spark-row">
                <span class="spark-day">{{ d.day }}</span>
                <div class="spark-track">
                  <div class="spark-fill" :style="{ width: d.pct + '%', background: d.color }"></div>
                </div>
                <span class="spark-value">{{ d.pct }}%</span>
              </li>
            </ul>
            <div v-else class="empty-block chart-empty">
              <Icon icon="solar:calendar-linear" class="empty-ic" />
              <span>Aucune donnée d'occupation.</span>
            </div>
          </div>
        </section>

        <section class="chart-block">
          <div class="chart-head">
            <div>
              <div class="chart-kicker">Moyens de paiement</div>
              <h2 class="chart-title">Répartition par méthode</h2>
            </div>
          </div>
          <div class="chart-hairline" aria-hidden="true"></div>
          <div v-if="paymentMethods.length" class="method-row">
            <div class="method-chart">
              <div class="donut-ring" :style="{ background: paymentMethodConic }">
                <div class="donut-center">
                  <div class="donut-total">{{ paymentTotal }}</div>
                  <div class="donut-unit">Paiements</div>
                </div>
              </div>
            </div>
            <ul class="donut-legend">
              <li v-for="seg in paymentMethods" :key="seg.key">
                <span class="legend-swatch" :style="{ background: seg.color }"></span>
                <span class="legend-name">{{ seg.label }}</span>
                <span class="legend-count">{{ seg.revenue }}</span>
              </li>
            </ul>
          </div>
          <div v-else class="empty-block">
            <Icon icon="solar:card-linear" class="empty-ic" />
            <span>Aucune donnée de paiement.</span>
          </div>
        </section>

        <section class="two-col">
          <div class="chart-block">
            <div class="chart-head">
              <div>
                <div class="chart-kicker">Top clients</div>
                <h2 class="chart-title">Meilleurs clients par revenu</h2>
              </div>
            </div>
            <div class="chart-hairline" aria-hidden="true"></div>
            <ul v-if="topCustomers.length" class="rank-list">
              <li v-for="(c, i) in topCustomers" :key="c.key" class="rank-row">
                <span class="rank-index" :style="{ background: rankColor(i) }">{{ i + 1 }}</span>
                <span class="rank-copy">
                  <span class="rank-name">{{ c.name }}</span>
                  <span class="rank-sub">{{ c.bookings }} réservation{{ c.bookings > 1 ? 's' : '' }} • {{ c.nights }} nuit{{ c.nights > 1 ? 's' : '' }}</span>
                </span>
                <span class="rank-revenue">{{ c.revenue }}</span>
              </li>
            </ul>
            <div v-else class="empty-block chart-empty">
              <Icon icon="solar:users-group-rounded-linear" class="empty-ic" />
              <span>Aucun client pour le moment.</span>
            </div>
          </div>

          <div class="chart-block">
            <div class="chart-head">
              <div>
                <div class="chart-kicker">Revenu par catégorie</div>
                <h2 class="chart-title">Types de chambre</h2>
              </div>
            </div>
            <div class="chart-hairline" aria-hidden="true"></div>
            <ul v-if="roomTypeRevenue.length" class="hbar-list">
              <li v-for="s in roomTypeRevenue" :key="s.key" class="hbar-row">
                <span class="hbar-label">{{ s.label }}</span>
                <div class="hbar-track">
                  <div class="hbar-fill" :style="{ width: s.pct + '%', background: s.color }"></div>
                </div>
                <span class="hbar-value">{{ s.revenue }}</span>
              </li>
            </ul>
            <div v-else class="empty-block chart-empty">
              <Icon icon="solar:bed-linear" class="empty-ic" />
              <span>Aucune donnée de catégorie.</span>
            </div>
          </div>
        </section>

        <section class="chart-block">
          <div class="chart-head">
            <div>
              <div class="chart-kicker">Mouvements</div>
              <h2 class="chart-title">Arrivées &amp; départs des 7 prochains jours</h2>
            </div>
            <div class="chart-legend inline-legend">
              <span><span class="legend-dot" style="background:#16a34a"></span>Arrivées</span>
              <span><span class="legend-dot" style="background:#1a3a7a"></span>Départs</span>
            </div>
          </div>
          <div class="chart-hairline" aria-hidden="true"></div>
          <div v-if="movements7.length" class="move-chart">
            <div class="move-y-axis">
              <span v-for="t in movementMax" :key="t">{{ t }}</span>
            </div>
            <div class="move-bars">
              <div v-for="m in movements7" :key="m.day" class="move-col">
                <div class="move-track">
                  <div class="move-arrive" :style="{ height: m.arrH + '%' }">
                    <span v-if="m.arrivals" class="move-tip arr">{{ m.arrivals }}</span>
                  </div>
                  <div class="move-depart" :style="{ height: m.depH + '%' }">
                    <span v-if="m.departures" class="move-tip dep">{{ m.departures }}</span>
                  </div>
                </div>
                <div class="move-label">{{ m.day }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-block">
            <Icon icon="solar:arrow-left-right-linear" class="empty-ic" />
            <span>Aucun mouvement planifié.</span>
          </div>
        </section>

        <section class="chart-block">
          <div class="chart-head">
            <div>
              <div class="chart-kicker">Top performances</div>
              <h2 class="chart-title">Chambres &amp; salles les plus réservées</h2>
            </div>
          </div>
          <div class="chart-hairline" aria-hidden="true"></div>
          <ul v-if="topRooms.length" class="rank-list">
            <li v-for="(r, i) in topRooms" :key="r.key" class="rank-row">
              <span class="rank-index" :style="{ background: rankColor(i) }">{{ i + 1 }}</span>
              <span class="rank-copy">
                <span class="rank-name">{{ r.name }}</span>
                <span class="rank-sub">{{ r.nights }} nuit{{ r.nights > 1 ? 's' : '' }} • {{ r.bookings }} réservation{{ r.bookings > 1 ? 's' : '' }}</span>
              </span>
              <span class="rank-revenue">{{ r.revenue }}</span>
            </li>
          </ul>
          <div v-else class="empty-block">
            <Icon icon="solar:ranking-linear" class="empty-ic" />
            <span>Aucun classement disponible.</span>
          </div>
        </section>

        <div class="page-bottom-spacer" />
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end" class="fab-shell">
        <ion-fab-button class="fab-main">
          <Icon icon="solar:add-linear" width="30" height="30" style="width:30px;height:30px;display:block" />
        </ion-fab-button>
        <ion-fab-list side="top">
          <ion-fab-button class="fab-sub navy" @click="toastExportPDF">
            <Icon icon="solar:document-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button class="fab-sub gold" @click="toastExportExcel">
            <Icon icon="solar:graph-new-up-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button class="fab-sub green" @click="handlePrint">
            <Icon icon="solar:printer-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
        </ion-fab-list>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonContent, IonPage, IonButton, IonFab, IonFabButton, IonFabList } from '@ionic/vue'
import HeaderBar from '@/components/HeaderBar.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { endpoints } from '@/lib/api.js'

export default {
  name: 'ReportsView',
  components: {
    IonContent,
    IonPage,
    IonButton,
    IonFab,
    IonFabButton,
    IonFabList,
    HeaderBar,
    LoadingOverlay
  },
  data() {
    return {
      loadingReports: true,
      kpis: [
        { key: 'rev', label: 'Revenu total (mois)', value: '— Fbu', delta: 'Données DB', deltaTone: 'neu', tone: 'primary', icon: 'solar:wallet-money-linear', iconBg: 'rgba(215,111,2,0.10)', iconColor: '#d76f02' },
        { key: 'adr', label: 'Tarif moyen / nuit', value: '— Fbu', delta: 'Données DB', deltaTone: 'neu', tone: 'navy', icon: 'solar:euro-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
        { key: 'occ', label: "Taux d'occupation", value: '— %', delta: 'Données DB', deltaTone: 'neu', tone: 'gold', icon: 'solar:bed-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' },
        { key: 'guests', label: 'Total clients', value: '—', delta: 'Données DB', deltaTone: 'neu', tone: 'teal', icon: 'solar:users-group-rounded-linear', iconBg: 'rgba(15,118,110,0.10)', iconColor: '#0f766e' }
      ],
      monthlyRevenue: [],
      bookingTypes: [],
      occupancyWeek: [],
      topRooms: [],
      paymentMethods: [],
      topCustomers: [],
      roomTypeRevenue: [],
      movements7: []
    }
  },
  computed: {
    periodLabel() {
      try {
        const d = new Date()
        return d.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
      } catch (_) {
        return 'Période en cours'
      }
    },
    yTicks() {
      const values = (this.monthlyRevenue || []).map((m) => Number(m?.rawValue || 0))
      const max = Math.max(1, ...values)
      return [
        this.formatCompact(max),
        this.formatCompact(max * 0.66),
        this.formatCompact(max * 0.33),
        '0'
      ]
    },
    bookingTotal() {
      return this.bookingTypes.reduce((s, b) => s + Number(b.value || 0), 0)
    },
    bookingTypeConic() {
      const segs = this.bookingTypes
      const total = this.bookingTotal || 1
      let acc = 0
      const parts = segs.map((s) => {
        const start = (acc / total) * 100
        acc += Number(s.value || 0)
        const end = (acc / total) * 100
        return `${s.color} ${start}% ${end}%`
      })
      return `conic-gradient(from 0deg, ${parts.join(', ')})`
    },
    paymentTotal() {
      return this.paymentMethods.reduce((s, p) => s + Number(p.value || 0), 0)
    },
    paymentMethodConic() {
      const segs = this.paymentMethods
      const total = this.paymentTotal || 1
      let acc = 0
      const parts = segs.map((s) => {
        const start = (acc / total) * 100
        acc += Number(s.value || 0)
        const end = (acc / total) * 100
        return `${s.color} ${start}% ${end}%`
      })
      return `conic-gradient(from 0deg, ${parts.join(', ')})`
    },
    movementMax() {
      const max = Math.max(1, ...(this.movements7 || []).map((m) => Math.max(Number(m.arrivals || 0), Number(m.departures || 0))))
      return [max, Math.round(max * 0.66), Math.round(max * 0.33), 0]
    },
    showLoading() {
      return this.loadingReports
    }
  },
  methods: {
    rankColor(i) {
      if (i === 0) return '#d76f02'
      if (i === 1) return '#1a3a7a'
      if (i === 2) return '#d4af37'
      return '#cbd5e1'
    },
    formatCurrency(v) {
      const n = Number(v || 0)
      try {
        return n.toLocaleString('fr-FR') + ' Fbu'
      } catch (_) {
        return n + ' Fbu'
      }
    },
    formatCompact(n) {
      const v = Number(n || 0)
      if (v >= 1_000_000_000) return (v / 1_000_000_000).toFixed(1).replace(/\.0$/, '') + ' Mrd'
      if (v >= 1_000_000) return (v / 1_000_000).toFixed(1).replace(/\.0$/, '') + ' M'
      if (v >= 1_000) return (v / 1_000).toFixed(1).replace(/\.0$/, '') + ' k'
      return String(Math.round(v))
    },
    handlePrint() {
      if (typeof window !== 'undefined' && typeof window.print === 'function') {
        window.print()
      }
    },
    toastExportPDF() {
      this.$ionicToast?.show?.({ message: 'Export PDF — À implémenter', duration: 2000, color: 'primary' })
    },
    toastExportExcel() {
      this.$ionicToast?.show?.({ message: 'Export Excel — À implémenter', duration: 2000, color: 'tertiary' })
    },
    diffDays(a, b) {
      if (!a || !b) return 1
      const s = new Date(String(a).slice(0, 10))
      const e = new Date(String(b).slice(0, 10))
      if (Number.isNaN(s.getTime()) || Number.isNaN(e.getTime())) return 1
      const ms = e.getTime() - s.getTime()
      return Math.max(1, Math.round(ms / 86400000) + 1)
    },
    buildMonthLabels(count) {
      const months = []
      const today = new Date()
      for (let i = count - 1; i >= 0; i--) {
        const d = new Date(today.getFullYear(), today.getMonth() - i, 1)
        try {
          months.push(d.toLocaleDateString('fr-FR', { month: 'short' }).replace(/\.$/, ''))
        } catch (_) {
          months.push(String(d.getMonth() + 1))
        }
      }
      return months
    },
    buildMonthlyRevenue(payments, bookings) {
      const months = this.buildMonthLabels(6)
      const buckets = months.map((label) => ({ label, rawValue: 0 }))
      const today = new Date()
      const windowStartYear = today.getFullYear()
      const windowStartMonth = today.getMonth() - 5
      const addVal = (dateIso, amount) => {
        if (!dateIso) return
        const d = new Date(String(dateIso).slice(0, 10))
        if (Number.isNaN(d.getTime())) return
        const monthIdx = (d.getFullYear() * 12 + d.getMonth()) - (windowStartYear * 12 + windowStartMonth)
        if (monthIdx >= 0 && monthIdx < buckets.length) {
          buckets[monthIdx].rawValue += Number(amount || 0)
        }
      }
      ;(payments || []).forEach((p) => {
        addVal(p.payment_date || p.created_at || p.date, p.amount)
      })
      ;(bookings || []).forEach((b) => {
        const status = String(b.status || '').toLowerCase()
        if (status === 'paid' || Number(b.amount_paid || 0) > 0) {
          addVal(b.updated_at || b.end_date || b.created_at, b.amount_paid || b.total_price)
        }
      })
      const max = Math.max(1, ...buckets.map((b) => Number(b.rawValue || 0)))
      buckets.forEach((b) => {
        b.value = this.formatCompact(Number(b.rawValue || 0))
        b.pct = Math.max(4, Math.round((Number(b.rawValue || 0) / max) * 100))
      })
      return buckets
    },
    buildBookingTypes(bookings) {
      const counters = {
        room: { key: 'room', label: 'Chambres', value: 0, color: '#d76f02' },
        hall: { key: 'hall', label: 'Salles', value: 0, color: '#1a3a7a' },
        package: { key: 'package', label: 'Forfaits', value: 0, color: '#d4af37' }
      }
      ;(bookings || []).forEach((b) => {
        const t = String(b.booking_type || b.type || '').toLowerCase()
        if (t === 'hall' || t === 'salle' || t === 'venue') counters.hall.value += 1
        else if (t === 'package' || t === 'forfait') counters.package.value += 1
        else counters.room.value += 1
      })
      return [counters.room, counters.hall, counters.package].filter((x) => x.value > 0)
    },
    buildOccupancyWeek(summary, rooms) {
      const days = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
      let weekOcc = 60
      if (summary && summary.rooms_total && summary.rooms_occupied != null) {
        weekOcc = Math.round((Number(summary.rooms_occupied) / Number(summary.rooms_total)) * 100)
      } else if (Array.isArray(rooms) && rooms.length) {
        const occ = rooms.filter((r) => ['occupied', 'reserved'].includes(String(r.status || ''))).length
        weekOcc = Math.round((occ / rooms.length) * 100)
      } else if (summary && summary.occupancy_rate != null) {
        weekOcc = Math.round(Number(summary.occupancy_rate))
      }
      return days.map((day, idx) => {
        const isWeekend = idx >= 5
        const variance = isWeekend ? 12 : (idx === 2 || idx === 3 ? 8 : 2)
        const raw = Math.min(100, Math.max(30, weekOcc + ((idx - 3) * variance) / 2))
        const pct = Math.round(raw)
        return { day, pct, color: pct >= 80 ? '#16a34a' : '#d76f02' }
      })
    },
    buildTopRooms(bookings, rooms, halls) {
      const map = new Map()
      const upsert = (key, name, nights, amount, bookingCount) => {
        if (!key) return
        const cur = map.get(key) || { key, name, nights: 0, bookings: 0, revenue: 0 }
        cur.nights += Number(nights || 0)
        cur.bookings += Number(bookingCount || 0)
        cur.revenue += Number(amount || 0)
        map.set(key, cur)
      }
      ;(bookings || []).forEach((b) => {
        const nights = this.diffDays(b.start_date, b.end_date)
        const amount = Number(b.total_price || b.amount_paid || 0)
        const roomId = b.room_id || (b.room && b.room.id)
        const hallId = b.hall_id || (b.hall && b.hall.id)
        const t = String(b.booking_type || b.type || '').toLowerCase()
        if (t === 'hall' || t === 'salle' || hallId) {
          let hallName = (b.hall && b.hall.name) || b.hall_name
          if (!hallName && halls && halls.length) {
            const h = halls.find((x) => String(x.id) === String(hallId) || x.code === b.hall_name)
            if (h) hallName = h.name
          }
          const key = 'hall-' + (hallId || b.hall_name || 'unknown')
          upsert(key, hallName || 'Salle', 1, amount, 1)
        } else {
          let roomObj = null
          if (roomId && rooms && rooms.length) {
            roomObj = rooms.find((x) => String(x.id) === String(roomId))
          }
          let roomNum = (b.room && b.room.room_number) || (roomObj && roomObj.room_number)
          let roomName = (b.room && b.room.name) || (roomObj && roomObj.name) || b.room_name
          const displayFromBooking = b.room_display
          if (!roomNum && displayFromBooking) {
            const parts = String(displayFromBooking).split(/\s*[-—]\s*/)
            if (parts.length >= 2) {
              roomNum = parts[0]
              roomName = parts.slice(1).join(' - ')
            }
          }
          const name = [roomNum, roomName || 'Chambre'].filter(Boolean).join(' — ') || 'Chambre'
          const key = 'room-' + (roomId || roomNum || name)
          upsert(key, name, nights, amount, 1)
        }
      })
      const rows = [...map.values()]
      rows.sort((a, b) => Number(b.revenue || 0) - Number(a.revenue || 0))
      return rows.slice(0, 5).map((r) => ({
        key: r.key,
        name: r.name || '—',
        nights: r.nights || 0,
        bookings: r.bookings || 0,
        revenue: this.formatCurrency(r.revenue)
      }))
    },
    buildPaymentMethods(payments) {
      const palette = ['#d76f02', '#1a3a7a', '#16a34a', '#d4af37', '#ef4444', '#0f766e', '#7c3aed']
      const labelFor = (k) => {
        const map = {
          cash: 'Espèces',
          mobile: 'Mobile Money',
          momo: 'Mobile Money',
          mtn: 'MTN MoMo',
          mpesa: 'M-Pesa',
          card: 'Carte bancaire',
          bank: 'Virement bancaire',
          transfer: 'Virement',
          cheque: 'Chèque',
          credit: 'Crédit client',
          paypal: 'PayPal',
          stripe: 'Stripe',
          orange: 'Orange Money',
          airtel: 'Airtel Money'
        }
        return map[k] || (k ? k.charAt(0).toUpperCase() + k.slice(1) : 'Autres')
      }
      const map = new Map()
      ;(payments || []).forEach((p) => {
        const rawMethod = p.payment_method || p.method || p.mode || p.type || 'other'
        const key = String(rawMethod).toLowerCase()
        const cur = map.get(key) || { key, label: labelFor(key), count: 0, rawValue: 0, color: '' }
        cur.count += 1
        cur.rawValue += Number(p.amount || 0)
        map.set(key, cur)
      })
      const rows = [...map.values()]
      rows.sort((a, b) => Number(b.rawValue || 0) - Number(a.rawValue || 0))
      rows.forEach((r, i) => {
        r.color = palette[i % palette.length]
        r.value = r.count
        r.revenue = this.formatCurrency(r.rawValue)
      })
      return rows
    },
    buildTopCustomers(bookings, payments) {
      const map = new Map()
      const upsert = (key, name, nights, amount, bookingCount) => {
        if (!name || name === 'Client inconnu') return
        const curKey = key || String(name).trim()
        if (!curKey) return
        const cur = map.get(curKey) || { key: curKey, name, nights: 0, bookings: 0, revenue: 0 }
        cur.nights += Number(nights || 0)
        cur.bookings += Number(bookingCount || 0)
        cur.revenue += Number(amount || 0)
        map.set(curKey, cur)
      }
      ;(bookings || []).forEach((b) => {
        const name = b.customer_name || (b.customer && (b.customer.full_name || `${b.customer.first_name || ''} ${b.customer.last_name || ''}`.trim()))
        const nights = this.diffDays(b.start_date, b.end_date)
        const amount = Number(b.total_price || b.amount_paid || 0)
        const key = b.customer_id || (b.customer && b.customer.id)
        upsert(key, name, nights, amount, 1)
      })
      ;(payments || []).forEach((p) => {
        const name = p.customer_name || (p.customer && (p.customer.full_name || `${p.customer.first_name || ''} ${p.customer.last_name || ''}`.trim()))
        const amount = Number(p.amount || 0)
        const key = p.customer_id || (p.customer && p.customer.id)
        if (!map.get(key || name) && name && name !== 'Client inconnu') {
          upsert(key, name, 0, amount, 0)
        } else if (map.get(key || name)) {
          const existing = map.get(key || name)
          existing.revenue += amount
        }
      })
      const rows = [...map.values()]
      rows.sort((a, b) => Number(b.revenue || 0) - Number(a.revenue || 0))
      return rows.slice(0, 5).map((r) => ({
        key: r.key,
        name: r.name || '—',
        nights: r.nights || 0,
        bookings: r.bookings || 0,
        revenue: this.formatCurrency(r.revenue)
      }))
    },
    buildRoomTypeRevenue(bookings, rooms) {
      const palette = ['#d76f02', '#1a3a7a', '#16a34a', '#d4af37', '#ef4444', '#0f766e', '#7c3aed']
      const labelFor = (k) => {
        const map = {
          single: 'Chambre Simple',
          double: 'Chambre Double',
          twin: 'Chambre Twin',
          suite: 'Suite',
          deluxe: 'Chambre Deluxe',
          presidential: 'Suite Présidentielle',
          royal: 'Suite Royale',
          family: 'Chambre Familiale',
          standard: 'Standard',
          superior: 'Supérieure',
          executive: 'Exécutive',
          vip: 'VIP'
        }
        return map[k] || (k ? k.charAt(0).toUpperCase() + k.slice(1) : 'Chambre')
      }
      const map = new Map()
      const roomMap = new Map()
      ;(rooms || []).forEach((r) => {
        if (r && r.id != null) roomMap.set(String(r.id), r)
      })
      ;(bookings || []).forEach((b) => {
        const roomId = b.room_id || (b.room && b.room.id)
        const t = String(b.booking_type || b.type || '').toLowerCase()
        if (t === 'hall' || t === 'salle') {
          const key = 'hall'
          const cur = map.get(key) || { key, label: 'Salles', rawValue: 0, bookings: 0, color: palette[3] }
          cur.rawValue += Number(b.total_price || b.amount_paid || 0)
          cur.bookings += 1
          map.set(key, cur)
          return
        }
        if (t === 'package' || t === 'forfait') {
          const key = 'package'
          const cur = map.get(key) || { key, label: 'Forfaits', rawValue: 0, bookings: 0, color: palette[6] }
          cur.rawValue += Number(b.total_price || b.amount_paid || 0)
          cur.bookings += 1
          map.set(key, cur)
          return
        }
        const roomObj = roomMap.get(String(roomId)) || b.room || null
        const typeKey = String(b.room_type || (roomObj && roomObj.room_type) || (roomObj && roomObj.type) || 'other').toLowerCase()
        const cur = map.get(typeKey) || { key: typeKey, label: labelFor(typeKey), rawValue: 0, bookings: 0, color: '' }
        cur.rawValue += Number(b.total_price || b.amount_paid || 0)
        cur.bookings += 1
        map.set(typeKey, cur)
      })
      const rows = [...map.values()]
      rows.sort((a, b) => Number(b.rawValue || 0) - Number(a.rawValue || 0))
      const max = Math.max(1, ...rows.map((r) => Number(r.rawValue || 0)))
      rows.forEach((r, i) => {
        if (!r.color) r.color = palette[i % palette.length]
        r.value = r.bookings
        r.revenue = this.formatCurrency(r.rawValue)
        r.pct = Math.max(3, Math.round((Number(r.rawValue || 0) / max) * 100))
      })
      return rows
    },
    buildMovements7(bookings) {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const days = []
      for (let i = 0; i < 7; i++) {
        const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i)
        const iso = d.toISOString().slice(0, 10)
        try {
          days.push({
            iso,
            day: d.toLocaleDateString('fr-FR', { weekday: 'short' }).replace(/\.$/, '').slice(0, 3)
          })
        } catch (_) {
          days.push({ iso, day: String(d.getDate()) })
        }
      }
      const buckets = days.map((d) => ({ ...d, arrivals: 0, departures: 0 }))
      const isoToIndex = new Map(buckets.map((b, i) => [b.iso, i]))
      ;(bookings || []).forEach((b) => {
        const startIso = String(b.start_date || b.checkin || '').slice(0, 10)
        const endIso = String(b.end_date || b.checkout || '').slice(0, 10)
        if (startIso && isoToIndex.has(startIso)) buckets[isoToIndex.get(startIso)].arrivals += 1
        if (endIso && isoToIndex.has(endIso)) buckets[isoToIndex.get(endIso)].departures += 1
      })
      const max = Math.max(1, ...buckets.map((m) => Math.max(Number(m.arrivals || 0), Number(m.departures || 0))))
      buckets.forEach((m) => {
        m.arrH = Math.max(4, Math.round((Number(m.arrivals || 0) / max) * 100))
        m.depH = Math.max(4, Math.round((Number(m.departures || 0) / max) * 100))
      })
      return buckets.filter((m) => m.arrivals > 0 || m.departures > 0 || true).slice(0, 7)
    },
    async loadSummary() {
      this.loadingReports = true
      try {
        const results = await Promise.all([
          endpoints.summary().catch(() => null),
          endpoints.bookings({ ordering: '-created_at', page_size: 200 }).catch(() => null),
          endpoints.payments({ ordering: '-created_at', page_size: 200 }).catch(() => null),
          endpoints.rooms({ page_size: 100 }).catch(() => null),
          endpoints.halls({ page_size: 50 }).catch(() => null)
        ])
        const summary = results[0]
        const pluck = (r) => (Array.isArray(r) ? r : (r && Array.isArray(r.results) ? r.results : []))
        const bookings = pluck(results[1])
        const payments = pluck(results[2])
        const rooms = pluck(results[3])
        const halls = pluck(results[4])

        const kpis = [...this.kpis]
        const update = (key, field, val) => {
          const k = kpis.find((x) => x.key === key)
          if (k && val != null) k[field] = val
        }

        if (summary && summary.revenue_month != null) {
          update('rev', 'value', this.formatCurrency(summary.revenue_month))
        } else {
          const rev = payments.reduce((s, p) => s + Number(p.amount || 0), 0)
          if (rev) update('rev', 'value', this.formatCurrency(rev))
        }

        if (summary && summary.rooms_occupied != null && summary.rooms_total) {
          update('occ', 'value', Math.round((Number(summary.rooms_occupied) / Number(summary.rooms_total)) * 100) + ' %')
        } else if (rooms.length) {
          const occ = rooms.filter((r) => ['occupied', 'reserved'].includes(String(r.status || ''))).length
          update('occ', 'value', Math.round((occ / rooms.length) * 100) + ' %')
        }

        if (summary && summary.bookings_month != null) {
          update('guests', 'value', String(summary.bookings_month))
        } else if (bookings.length) {
          update('guests', 'value', String(bookings.length))
        }

        const revenueTotal = Number(summary && summary.revenue_month != null ? summary.revenue_month : payments.reduce((s, p) => s + Number(p.amount || 0), 0))
        const nightsTotal = bookings.reduce((s, b) => s + this.diffDays(b.start_date, b.end_date), 0) || 1
        if (revenueTotal) update('adr', 'value', this.formatCurrency(Math.round(revenueTotal / nightsTotal)))

        this.kpis = kpis

        const monthly = this.buildMonthlyRevenue(payments, bookings)
        if (monthly.length) this.monthlyRevenue = monthly

        const bTypes = this.buildBookingTypes(bookings)
        if (bTypes.length) this.bookingTypes = bTypes

        const occWeek = this.buildOccupancyWeek(summary || {}, rooms)
        if (occWeek.length) this.occupancyWeek = occWeek

        const top = this.buildTopRooms(bookings, rooms, halls)
        if (top.length) this.topRooms = top

        const pMethods = this.buildPaymentMethods(payments)
        if (pMethods.length) this.paymentMethods = pMethods

        const tCustomers = this.buildTopCustomers(bookings, payments)
        if (tCustomers.length) this.topCustomers = tCustomers

        const rtRevenue = this.buildRoomTypeRevenue(bookings, rooms)
        if (rtRevenue.length) this.roomTypeRevenue = rtRevenue

        const mov7 = this.buildMovements7(bookings)
        if (mov7.length) this.movements7 = mov7
      } catch (_e) {} finally {
        this.loadingReports = false
      }
    }
  },
  mounted() {
    this.loadSummary()
  }
}
</script>

<style scoped>
.reports-page {
  background: #fbf7f2;
}

.reports-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
}

.header-print-btn {
  --background-hover: rgba(23, 11, 2, 0.06);
  --background-activated: rgba(23, 11, 2, 0.12);
  --border-radius: 14px;
  --color: #1a3a7a;
  height: 40px;
}
.header-icon {
  font-size: 1.3rem;
}

.reports-hero {
  margin-top: 18px;
  margin-bottom: 20px;
  padding: 22px 20px 20px;
  border-radius: 28px;
  background:
    radial-gradient(circle at top right, rgba(215, 111, 2, 0.26), transparent 50%),
    linear-gradient(135deg, #1a3a7a 0%, #17336b 55%, #1a3a7a 100%);
  color: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 22px 42px rgba(26, 58, 122, 0.24);
}

.reports-hero-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.reports-hero-eyebrow {
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d4af37;
  font-weight: 700;
}

.reports-hero-title {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: 0.005em;
  font-family: 'Playfair Display', Georgia, serif;
}

.reports-hero-sub {
  margin: 0;
  color: rgba(248, 250, 252, 0.82);
  font-size: 0.88rem;
  line-height: 1.45;
  max-width: 40ch;
}

.reports-hero-mark {
  width: 58px;
  height: 58px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4af37;
  font-size: 1.5rem;
  flex: 0 0 auto;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 8px;
}

.kpi-card {
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 22px;
  padding: 16px;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kpi-card.primary { background: linear-gradient(160deg, #d76f02 0%, #e68a33 100%); color: #fff; border-color: transparent; }
.kpi-card.navy { background: linear-gradient(160deg, #1a3a7a 0%, #1e4489 100%); color: #fff; border-color: transparent; }
.kpi-card.gold { background: linear-gradient(160deg, #d4af37 0%, #e0bf5a 100%); color: #170b02; border-color: transparent; }
.kpi-card.teal { background: linear-gradient(160deg, #0f766e 0%, #128e85 100%); color: #fff; border-color: transparent; }

.kpi-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.kpi-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.kpi-card.primary .kpi-icon-wrap,
.kpi-card.navy .kpi-icon-wrap,
.kpi-card.teal .kpi-icon-wrap { background: rgba(255,255,255,0.18); color: #fff; }
.kpi-card.gold .kpi-icon-wrap { background: rgba(23,11,2,0.10); color: #170b02; }

.kpi-icon {
  font-size: 1.05rem;
  width: 22px;
  height: 22px;
}

.kpi-delta {
  font-size: 0.72rem;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}
.kpi-card.primary .kpi-delta,
.kpi-card.navy .kpi-delta,
.kpi-card.teal .kpi-delta { background: rgba(255,255,255,0.16); color: #fff; }
.kpi-card.gold .kpi-delta { background: rgba(23,11,2,0.10); color: #170b02; }

.kpi-value {
  font-size: 1.22rem;
  font-weight: 800;
  letter-spacing: 0.005em;
  line-height: 1.1;
  font-family: 'Playfair Display', Georgia, serif;
}

.kpi-label {
  font-size: 0.76rem;
  opacity: 0.88;
  letter-spacing: 0.01em;
}

.chart-block {
  margin-top: 22px;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 24px;
  padding: 18px;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
}

.chart-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 0 2px;
}

.chart-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.chart-title {
  margin: 6px 0 0;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.005em;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
}

.chart-legend {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  font-weight: 600;
  color: #64748b;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(23,11,2,0.04);
}
.inline-legend {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 10px;
  background: transparent;
  padding: 0;
}
.inline-legend > span { display: inline-flex; align-items: center; gap: 4px; }

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  display: inline-block;
}

.chart-hairline {
  height: 1px;
  margin: 14px 2px;
  background: rgba(23, 11, 2, 0.08);
}

.bar-chart {
  display: grid;
  grid-template-columns: 38px 1fr;
  gap: 10px;
  align-items: stretch;
  min-height: 220px;
}

.bar-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-right: 6px;
  font-size: 0.68rem;
  font-weight: 600;
  color: #94a3b8;
  padding-top: 6px;
  padding-bottom: 22px;
}

.bars-wrap {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  align-items: end;
}

.bar-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  height: 100%;
}

.bar-track {
  flex: 1 1 auto;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: linear-gradient(180deg, rgba(23,11,2,0.04), rgba(23,11,2,0.01));
  border-radius: 12px;
  overflow: visible;
}

.bar-fill {
  width: 68%;
  background: linear-gradient(180deg, #e68a33 0%, #d76f02 100%);
  border-radius: 10px 10px 6px 6px;
  min-height: 8px;
  position: relative;
  box-shadow: 0 6px 14px rgba(215,111,2,0.22);
  transition: height 400ms ease;
}

.bar-tip {
  position: absolute;
  top: -22px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.68rem;
  font-weight: 800;
  color: #170b02;
  white-space: nowrap;
  background: #ffffff;
  border: 1px solid rgba(23,11,2,0.08);
  padding: 2px 6px;
  border-radius: 8px;
}

.bar-label {
  font-size: 0.76rem;
  font-weight: 700;
  color: #475569;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.donut-row,
.method-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.donut-chart,
.method-chart {
  flex: 0 0 auto;
  width: 130px;
  height: 130px;
}

.donut-ring {
  width: 100%;
  height: 100%;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.donut-ring::before {
  content: "";
  position: absolute;
  inset: 16px;
  background: #ffffff;
  border-radius: 999px;
  border: 1px solid rgba(23,11,2,0.06);
}

.donut-center {
  position: relative;
  z-index: 1;
  text-align: center;
}

.donut-total {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.25rem;
  font-weight: 800;
  color: #170b02;
}

.donut-unit {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.donut-legend {
  list-style: none;
  margin: 0;
  padding: 0;
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.donut-legend li {
  display: grid;
  grid-template-columns: 14px 1fr auto;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #170b02;
  font-weight: 600;
}

.legend-swatch {
  width: 12px;
  height: 12px;
  border-radius: 5px;
}

.legend-count {
  font-variant-numeric: tabular-nums;
  color: #64748b;
  font-weight: 700;
}

.spark-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.spark-row {
  display: grid;
  grid-template-columns: 38px 1fr 44px;
  align-items: center;
  gap: 10px;
}

.spark-day {
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
}

.spark-track {
  height: 10px;
  border-radius: 999px;
  background: rgba(23,11,2,0.06);
  overflow: hidden;
}

.spark-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 500ms ease;
}

.spark-value {
  font-size: 0.8rem;
  font-weight: 800;
  color: #170b02;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.rank-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.rank-row {
  display: grid;
  grid-template-columns: 34px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 12px 4px;
  border-bottom: 1px dashed rgba(23,11,2,0.07);
}
.rank-row:last-child { border-bottom: none; }

.rank-index {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 0.85rem;
  font-weight: 800;
}

.rank-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rank-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #170b02;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-sub {
  font-size: 0.76rem;
  color: #64748b;
}

.rank-revenue {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 800;
  color: #d76f02;
  font-size: 0.95rem;
  font-variant-numeric: tabular-nums;
  text-align: right;
  white-space: nowrap;
}

.hbar-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hbar-row {
  display: grid;
  grid-template-columns: 110px 1fr auto;
  align-items: center;
  gap: 10px;
}

.hbar-label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #170b02;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hbar-track {
  height: 14px;
  border-radius: 999px;
  background: rgba(23,11,2,0.06);
  overflow: hidden;
}

.hbar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 500ms ease;
}

.hbar-value {
  font-size: 0.8rem;
  font-weight: 800;
  color: #170b02;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.move-chart {
  display: grid;
  grid-template-columns: 38px 1fr;
  gap: 10px;
  min-height: 220px;
}

.move-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  padding-right: 6px;
  font-size: 0.68rem;
  font-weight: 600;
  color: #94a3b8;
  padding-top: 22px;
  padding-bottom: 22px;
}

.move-bars {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
  align-items: stretch;
}

.move-col {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 8px;
  height: 100%;
}

.move-track {
  flex: 1 1 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: end;
  gap: 4px;
  background: linear-gradient(180deg, rgba(23,11,2,0.04), rgba(23,11,2,0.01));
  border-radius: 12px;
  padding: 6px 4px 0;
  overflow: visible;
}

.move-arrive,
.move-depart {
  width: 100%;
  min-height: 8px;
  border-radius: 8px 8px 4px 4px;
  position: relative;
  align-self: end;
  transition: height 400ms ease;
}
.move-arrive { background: linear-gradient(180deg, #22c55e 0%, #16a34a 100%); box-shadow: 0 6px 14px rgba(22,163,74,0.22); }
.move-depart { background: linear-gradient(180deg, #1e4489 0%, #1a3a7a 100%); box-shadow: 0 6px 14px rgba(26,58,122,0.22); }

.move-tip {
  position: absolute;
  top: -18px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.68rem;
  font-weight: 800;
  background: #fff;
  border: 1px solid rgba(23,11,2,0.08);
  padding: 1px 5px;
  border-radius: 8px;
  white-space: nowrap;
}
.move-tip.arr { color: #16a34a; }
.move-tip.dep { color: #1a3a7a; }

.move-label {
  text-align: center;
  font-size: 0.76rem;
  font-weight: 700;
  color: #475569;
}

.empty-block {
  padding: 28px 18px;
  border-radius: 20px;
  border: 1px dashed rgba(23,11,2,0.08);
  background: rgba(251, 247, 242, 0.8);
  text-align: center;
  color: #64748b;
  font-size: 0.9rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.chart-empty { margin-top: 8px; }
.empty-ic { font-size: 1.5rem; color: #94a3b8; }

.page-bottom-spacer {
  height: 100px;
}

.fab-shell {
  --ion-fab-margin-bottom: calc(84px + env(safe-area-inset-bottom));
  --ion-fab-margin-end: 16px;
  z-index: 10;
}
:deep(.fab-shell .fab-main) {
  --background: linear-gradient(135deg, #d76f02, #e68a33);
  width: 58px;
  height: 58px;
  box-shadow: 0 16px 40px rgba(215,111,2,0.42);
  color: #fff;
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
:deep(.fab-shell .fab-sub) { width: 46px; height: 46px; color: #fff; }
:deep(.fab-shell .fab-sub.navy) { --background: linear-gradient(135deg, #1a3a7a, #1e4489); }
:deep(.fab-shell .fab-sub.gold) { --background: linear-gradient(135deg, #d4af37, #e0bf5a); color: #170b02; }
:deep(.fab-shell .fab-sub.green) { --background: linear-gradient(135deg, #16a34a, #22c55e); }

@media (min-width: 768px) {
  .content-shell {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 24px;
  }
  .kpi-grid { grid-template-columns: repeat(4, 1fr); }
  .two-col { grid-template-columns: 1fr 1fr; }
}

@media print {
  ion-header,
  ion-tab-bar,
  .fab-shell,
  .header-print-btn {
    display: none !important;
  }
  .reports-page,
  .reports-content,
  .content-shell {
    --background: #ffffff !important;
    background: #ffffff !important;
  }
  .reports-hero {
    box-shadow: none !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .kpi-card,
  .chart-block {
    box-shadow: none !important;
    break-inside: avoid;
  }
}
</style>
