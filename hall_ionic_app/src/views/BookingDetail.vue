<template>
  <ion-page class="booking-detail-page">
    <HeaderBar
      title="Réservation"
      eyebrow="Détails"
      :show-menu="false"
      :show-back="true"
      back-href="/bookings"
    />

    <ion-content class="detail-content">
      <div class="content-shell">

        <section class="hero-ribbon">
          <div class="hero-code">{{ booking.code || `#${booking.id || ''}` }}</div>
          <div class="hero-customer">{{ booking.customer_name || '—' }}</div>
          <div class="hero-subtitle">{{ bookingItemLabel || periodLabel }}</div>
          <div :class="['hero-status', `status-${booking.status || 'pending'}`]">
            {{ statusLabel }}
          </div>
        </section>

        <section class="entity-card">
          <div class="entity-head">
            <div class="entity-kicker">Réservation</div>
            <h2 class="entity-title">Informations principales</h2>
          </div>
          <div class="entity-hairline" aria-hidden="true"></div>
          <div class="entity-list">
            <div class="entity-row">
              <span class="entity-label">Type</span>
              <span class="entity-value">{{ bookingTypeLabel }}</span>
            </div>
            <div class="entity-row">
              <span class="entity-label">Espace</span>
              <span class="entity-value">{{ bookingItemLabel }}</span>
            </div>
            <div class="entity-row">
              <span class="entity-label">Période</span>
              <span class="entity-value">{{ periodLabel }}</span>
            </div>
            <div class="entity-row">
              <span class="entity-label">Nombre de nuits</span>
              <span class="entity-value">{{ nightsCount }} nuit{{ nightsCount > 1 ? 's' : '' }}</span>
            </div>
          </div>
        </section>

        <section class="entity-card">
          <div class="entity-head">
            <div class="entity-kicker">Client</div>
            <h2 class="entity-title">Coordonnées</h2>
          </div>
          <div class="entity-hairline" aria-hidden="true"></div>
          <div class="entity-list">
            <div class="entity-row">
              <span class="entity-label">Téléphone</span>
              <a class="entity-value link" :href="`tel:${booking.customer_phone}`">{{ booking.customer_phone || '—' }}</a>
            </div>
            <div class="entity-row">
              <span class="entity-label">Email</span>
              <a class="entity-value link" :href="`mailto:${booking.customer_email}`">{{ booking.customer_email || '—' }}</a>
            </div>
          </div>
        </section>

        <section class="entity-card totals-card">
          <div class="entity-head">
            <div class="entity-kicker">TOTAUX</div>
            <h2 class="entity-title">Montants &amp; statut</h2>
          </div>
          <div class="entity-hairline" aria-hidden="true"></div>
          <div class="entity-list">
            <div class="entity-row">
              <span class="entity-label">Sous-total</span>
              <span class="entity-value">{{ formatMoney(booking.total_price) }}</span>
            </div>
            <div class="entity-row">
              <span class="entity-label">Déjà payé</span>
              <span class="entity-value">{{ formatMoney(booking.paid_amount || 0) }}</span>
            </div>
            <div :class="['entity-row', 'accent', remainingAmount > 0 ? 'unpaid' : 'paid']">
              <span class="entity-label">Reste à payer</span>
              <span class="entity-value">{{ formatMoney(remainingAmount) }}</span>
            </div>
          </div>
        </section>

        <section class="actions-block">
          <ion-button expand="block" fill="outline" class="action-btn outline-primary" @click="handlePrint">
            <template v-slot:start>
              <Icon icon="solar:printer-linear" />
            </template>
            Imprimer le reçu
          </ion-button>
          <ion-button expand="block" fill="outline" class="action-btn outline-primary" @click="toastContact">
            <template v-slot:start>
              <Icon icon="solar:phone-linear" />
            </template>
            Contacter le client
          </ion-button>
        </section>

        <div class="page-bottom-spacer" />
      </div>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonButton, IonContent, IonPage } from '@ionic/vue'
import HeaderBar from '@/components/HeaderBar.vue'
import { endpoints } from '@/lib/api.js'

export default {
  name: 'BookingDetailView',
  components: {
    IonButton,
    IonContent,
    IonPage,
    HeaderBar
  },
  data() {
    return {
      booking: {
        id: 0,
        code: '',
        customer_name: '',
        customer_phone: '',
        customer_email: '',
        booking_type: '',
        hall_name: '',
        room_display: '',
        start_date: '',
        end_date: '',
        total_price: 0,
        paid_amount: 0,
        status: 'pending'
      },
      statusMap: {
        pending: 'En attente',
        confirmed: 'Confirmée',
        paid: 'Payée',
        cancelled: 'Annulée'
      }
    }
  },
  computed: {
    statusLabel() {
      return this.statusMap[this.booking.status] || 'Inconnu'
    },
    bookingTypeLabel() {
      return String(this.booking.booking_type || '') === 'room' ? 'Chambre' : 'Salle'
    },
    bookingItemLabel() {
      if (this.booking.booking_type === 'room') return this.booking.room_display || '-'
      return this.booking.hall_name || '-'
    },
    periodLabel() {
      const start = String(this.booking.start_date || '').slice(0, 10)
      const end = String(this.booking.end_date || '').slice(0, 10)
      if (!start && !end) return '—'
      if (start === end) return start
      return `${start}   →   ${end}`
    },
    nightsCount() {
      const start = new Date(String(this.booking.start_date || ''))
      const end = new Date(String(this.booking.end_date || ''))
      if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 1
      const diff = Math.max(0, Math.round((end - start) / 86400000))
      return diff + 1
    },
    remainingAmount() {
      return Math.max(0, Number(this.booking.total_price || 0) - Number(this.booking.paid_amount || 0))
    }
  },
  methods: {
    formatMoney(raw) {
      const n = Number(raw || 0)
      try {
        return n.toLocaleString('fr-FR') + ' Fbu'
      } catch (_) {
        return `${n.toFixed(0)} Fbu`
      }
    },
    handlePrint() {
      if (typeof window !== 'undefined' && typeof window.print === 'function') {
        window.print()
      }
    },
    toastContact() {
      const phone = this.booking.customer_phone
      const msg = phone ? `Contacter : ${phone}` : 'Contacter le client'
      this.$ionicToast?.show?.({ message: msg, duration: 2000, color: 'primary' })
    },
    getMockBooking(id) {
      const list = [
        {
          id: 1, code: 'RSV-0625-0042', customer_name: 'Jeanine Ndayikengurukiye',
          booking_type: 'hall', hall_name: 'Salle Royale',
          start_date: '2026-06-28', end_date: '2026-06-28', status: 'confirmed',
          total_price: 2850000, paid_amount: 1425000,
          customer_phone: '+257 79 12 34 56', customer_email: 'jeanine@example.bi',
          room_display: ''
        },
        {
          id: 2, code: 'RSV-0625-0041', customer_name: 'Hôtel Savane Co.',
          booking_type: 'room', room_display: '101 — Chambre Double Deluxe',
          start_date: '2026-06-25', end_date: '2026-06-30', status: 'paid',
          total_price: 1840000, paid_amount: 1840000,
          customer_phone: '+257 22 00 00 00', customer_email: 'contact@savane.bi',
          hall_name: ''
        },
        {
          id: 3, code: 'RSV-0625-0039', customer_name: 'Didier Ndayizeye',
          booking_type: 'room', room_display: '203 — Suite Présidentielle',
          start_date: '2026-06-27', end_date: '2026-07-01', status: 'pending',
          total_price: 3920000, paid_amount: 0,
          customer_phone: '+257 76 11 22 33', customer_email: 'didier@example.bi',
          hall_name: ''
        }
      ]
      return list.find((b) => Number(b.id) === Number(id)) || list[0] || { id: 0 }
    },
    applyBookingData(data) {
      if (!data) return
      this.booking = {
        id: data.id || 0,
        code: data.display_id || data.code || '',
        customer_name: (data.customer?.full_name) || data.customer_name || '',
        customer_phone: data.customer_phone || (data.customer?.phone) || '',
        customer_email: data.customer_email || (data.customer?.email) || '',
        booking_type: data.booking_type || '',
        hall_name: (data.hall?.name) || data.hall_name || '',
        room_display: data.room_display || this.buildRoomDisplay(data),
        start_date: data.start_date || data.check_in || '',
        end_date: data.end_date || data.check_out || '',
        total_price: Number(data.total_price || data.amount || 0),
        paid_amount: Number(data.paid_amount || 0),
        status: data.status || 'pending'
      }
    },
    buildRoomDisplay(data) {
      if (data.room_display) return data.room_display
      const room = data.room || {}
      const parts = []
      if (room.number) parts.push(room.number)
      if (room.name || room.type) parts.push(room.name || room.type)
      return parts.join(' — ')
    }
  },
  mounted() {
    const id = this.$route?.params?.id
    if (!id) {
      this.applyBookingData(this.getMockBooking(1))
      return
    }
    endpoints.booking(id)
      .then((data) => {
        this.applyBookingData(data)
      })
      .catch((err) => {
        const status = err?.response?.status
        if (status === 404 || !status) {
          this.applyBookingData(this.getMockBooking(id))
        } else {
          this.applyBookingData(this.getMockBooking(id))
        }
      })
  }
}
</script>

<style scoped>
.booking-detail-page {
  background: #fbf7f2;
}

.detail-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
}

.hero-ribbon {
  margin-top: 18px;
  padding: 20px 20px 18px;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.16), transparent 46%),
    linear-gradient(135deg, #1a3a7a 0%, #17336b 100%);
  color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
  box-shadow: 0 22px 42px rgba(26, 58, 122, 0.22);
}

.hero-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  color: #d4af37;
  font-weight: 700;
}

.hero-customer {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: 0.005em;
  color: #ffffff;
  font-family: 'Playfair Display', Georgia, serif;
}

.hero-subtitle {
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.hero-status {
  margin-top: 6px;
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: #d76f02;
  color: #ffffff;
}

.entity-card {
  margin-top: 18px;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 24px;
  padding: 18px 18px 16px;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
}

.entity-head {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.entity-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d76f02;
  font-weight: 700;
}

.entity-title {
  margin: 4px 0 0;
  font-size: 1.02rem;
  font-weight: 800;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
}

.entity-hairline {
  margin: 14px 0 12px;
  height: 1px;
  background: rgba(23, 11, 2, 0.08);
}

.entity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.entity-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
}

.entity-label {
  font-size: 0.8rem;
  color: #64748b;
  font-weight: 500;
  flex: 0 0 auto;
}

.entity-value {
  color: #170b02;
  font-weight: 700;
  font-size: 0.95rem;
  text-align: right;
}

.entity-value.link {
  text-decoration: none;
  color: #1a3a7a;
}

.entity-row.accent.unpaid .entity-label {
  color: #64748b;
}

.entity-row.accent.unpaid .entity-value {
  color: #ef4444;
  font-weight: 800;
  font-size: 1rem;
}

.entity-row.accent.paid .entity-label {
  color: #64748b;
}

.entity-row.accent.paid .entity-value {
  color: #10b981;
  font-weight: 800;
  font-size: 1rem;
}

.totals-card .entity-row:last-child {
  padding-top: 8px;
  margin-top: 2px;
  border-top: 1px dashed rgba(23, 11, 2, 0.08);
}

.actions-block {
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.action-btn {
  --border-radius: 18px;
  --padding-top: 14px;
  --padding-bottom: 14px;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.action-btn.outline-primary {
  --color: #d76f02;
  --border-color: #d76f02;
  --background-hover: rgba(215, 111, 2, 0.06);
  --background-activated: rgba(215, 111, 2, 0.12);
}

.page-bottom-spacer {
  height: 40px;
}

@media (min-width: 768px) {
  .content-shell {
    max-width: 720px;
    margin: 0 auto;
    padding: 0 24px;
  }
}

@media print {
  ion-header,
  ion-tab-bar,
  .actions-block {
    display: none !important;
  }
  .booking-detail-page,
  .detail-content,
  .content-shell {
    --background: #ffffff !important;
    background: #ffffff !important;
  }
  .hero-ribbon,
  .entity-card {
    box-shadow: none !important;
    break-inside: avoid;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>
