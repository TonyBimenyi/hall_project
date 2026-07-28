<template>
  <ion-page class="bookings-page">
    <HeaderBar title="Réservations" eyebrow="Planning" :show-menu="false">
      <template #actions>
        <ion-button class="header-print-btn" @click="handlePrint">
          <Icon icon="solar:printer-linear" class="header-cta-icon" />
        </ion-button>
        <ion-button :class="['filter-btn', filtersOpen ? 'filter-active' : 'filter-collapsed']" @click="toggleFilters">
          <Icon :icon="filtersOpen ? 'solar:settings-3-linear' : 'solar:filter-linear'" class="filter-icon" />
        </ion-button>
      </template>
    </HeaderBar>

    <ion-content class="bookings-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement des réservations"
      />
      <div class="content-shell">

        <section v-if="filtersOpen" class="filters-card">
          <div class="filters-head">
            <div class="filters-kicker">Filtres rapides</div>
            <h2 class="filters-title">Affiner la liste</h2>
          </div>
          <div class="filters-row">
            <ion-segment v-model="statusFilter" class="status-segment" :scrollable="true">
              <ion-segment-button value="all">
                <ion-label>Tout</ion-label>
              </ion-segment-button>
              <ion-segment-button value="pending">
                <ion-label>En attente</ion-label>
              </ion-segment-button>
              <ion-segment-button value="confirmed">
                <ion-label>Confirmée</ion-label>
              </ion-segment-button>
              <ion-segment-button value="paid">
                <ion-label>Payée</ion-label>
              </ion-segment-button>
              <ion-segment-button value="cancelled">
                <ion-label>Annulée</ion-label>
              </ion-segment-button>
            </ion-segment>
          </div>
          <div class="filters-row row-inline">
            <div class="filters-search-shell">
              <Icon icon="solar:magnifer-linear" class="filters-search-icon" />
              <ion-input
                v-model="searchQuery"
                :placeholder="'Rechercher client, code, salle…'"
                class="filters-search-input"
                inputmode="search"
                fill="none"
                lines="none"
              />
            </div>
          </div>
        </section>

        <section class="summary-strip">
          <div class="summary-item total">
            <span>{{ filteredBookings.length }}</span>
            <small>{{ filteredBookings.length === 1 ? 'réservation' : 'réservations' }}</small>
          </div>
          <div class="summary-item pending">
            <span>{{ pendingCount }}</span>
            <small>En attente</small>
          </div>
          <div class="summary-item paid">
            <span>{{ paidCount }}</span>
            <small>Payée</small>
          </div>
        </section>

        <section class="bookings-list-shell">
          <div class="list-head">
            <div>
              <div class="list-kicker">Catalogue</div>
              <h2 class="list-title">Résultats</h2>
            </div>
          </div>
          <div class="list-divider" aria-hidden="true"></div>

          <div class="bookings-stack">
            <BookingCard
              v-for="booking in filteredBookings"
              :key="booking.id"
              :booking="booking"
              @click="openBooking(booking)"
              @view="openBooking"
              @edit="toastEdit"
              @delete="handleDeleteBooking"
            />

            <div v-if="!filteredBookings.length" class="empty-block">
              <Icon icon="solar:calendar-linear" class="empty-icon" />
              <p>Aucune réservation ne correspond.</p>
            </div>
          </div>
        </section>

        <div class="page-bottom-spacer" />
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end" class="fab-shell">
        <ion-fab-button class="fab-main">
          <Icon icon="solar:add-linear" width="30" height="30" style="width:30px;height:30px;display:block" />
        </ion-fab-button>
        <ion-fab-list side="top">
          <ion-fab-button class="fab-sub booking-sub" @click="toastNewBooking">
            <Icon icon="solar:calendar-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button class="fab-sub payment-sub" @click="toastNewPayment">
            <Icon icon="solar:wallet-money-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
        </ion-fab-list>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script>
import {
  IonButton,
  IonContent,
  IonFab,
  IonFabButton,
  IonFabList,
  IonInput,
  IonLabel,
  IonPage,
  IonSegment,
  IonSegmentButton
} from '@ionic/vue'
import { endpoints } from '@/lib/api.js'
import HeaderBar from '@/components/HeaderBar.vue'
import BookingCard from '@/components/BookingCard.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const MOCK_BOOKINGS = [
  { id: 1, code: 'RSV-0625-0042', customer_name: 'Jeanine Ndayikengurukiye', booking_type: 'hall', hall_name: 'Salle Royale', start_date: '2026-06-28', end_date: '2026-06-28', status: 'confirmed', total_price: 2850000 },
  { id: 2, code: 'RSV-0625-0041', customer_name: 'Hôtel Savane Co.', booking_type: 'room', room_display: '101 — Chambre Double Deluxe', start_date: '2026-06-25', end_date: '2026-06-30', status: 'paid', total_price: 1840000 },
  { id: 3, code: 'RSV-0625-0039', customer_name: 'Didier Ndayizeye', booking_type: 'room', room_display: '203 — Suite Présidentielle', start_date: '2026-06-27', end_date: '2026-07-01', status: 'pending', total_price: 3920000 },
  { id: 4, code: 'RSV-0625-0036', customer_name: 'Annonciate Nshimirimana', booking_type: 'room', room_display: '104 — Chambre Twin', start_date: '2026-06-26', end_date: '2026-06-29', status: 'pending', total_price: 1240000 },
  { id: 5, code: 'RSV-0625-0033', customer_name: 'Union des Commerçants', booking_type: 'hall', hall_name: 'Salle Séminaire', start_date: '2026-07-05', end_date: '2026-07-05', status: 'cancelled', total_price: 950000 }
]

export default {
  name: 'BookingsView',
  components: {
    IonButton,
    IonContent,
    IonFab,
    IonFabButton,
    IonFabList,
    IonInput,
    IonLabel,
    IonPage,
    IonSegment,
    IonSegmentButton,
    HeaderBar,
    BookingCard,
    LoadingOverlay
  },
  data() {
    return {
      loading: true,
      filtersOpen: true,
      statusFilter: 'all',
      searchQuery: '',
      bookings: []
    }
  },
  computed: {
    filteredBookings() {
      const query = String(this.searchQuery || '').trim().toLowerCase()
      const status = this.statusFilter
      return this.bookings.filter((b) => {
        const byStatus = status === 'all' ? true : String(b.status || '') === status
        if (!byStatus) return false
        if (!query) return true
        const hay = [
          b.customer_name,
          b.code,
          b.hall_name,
          b.room_display
        ].join(' | ').toLowerCase()
        return hay.includes(query)
      })
    },
    pendingCount() {
      return this.filteredBookings.filter((b) => b.status === 'pending').length
    },
    paidCount() {
      return this.filteredBookings.filter((b) => b.status === 'paid').length
    },
    showLoading() {
      return this.loading
    }
  },
  methods: {
    toggleFilters() {
      this.filtersOpen = !this.filtersOpen
    },
    openBooking(booking) {
      if (!booking?.id) return
      this.$router.push(`/bookings/${booking.id}`)
    },
    toastEdit() {
      try {
        const t = document.querySelector('ion-toast')
        if (t) return
      } catch (_) {}
      alert('Modification (à venir)')
    },
    handleDeleteBooking(b) {
      const code = b?.code || b?.display_id || `#${b?.id || ''}`
      try {
        endpoints.deleteBooking && endpoints.deleteBooking(b?.id).catch(() => null)
      } catch (_) {}
      this.bookings = this.bookings.filter((x) => x.id !== b?.id)
      this.fetchBookings().catch(() => null)
    },
    toastNewBooking() {
      alert('Nouvelle réservation (à venir)')
    },
    toastNewPayment() {
      alert('Nouveau paiement (à venir)')
    },
    handlePrint() {
      window.print()
    },
    async fetchBookings() {
      this.loading = true
      try {
        const result = await endpoints.bookings({ ordering: '-created_at' })
        if (Array.isArray(result)) {
          this.bookings = result
        } else if (result && typeof result === 'object' && Array.isArray(result.results)) {
          this.bookings = result.results
        } else {
          this.bookings = []
        }
      } catch (err) {
        this.bookings = MOCK_BOOKINGS
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.fetchBookings()
  }
}
</script>

<style scoped>
.bookings-page {
  background: #fbf7f2;
}

.bookings-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
  position: relative;
  z-index: 1;
}

.filters-card {
  margin-top: 18px;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 24px;
  padding: 18px 18px 16px;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
}

.filters-head {
  margin-bottom: 12px;
}

.filters-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.filters-title {
  margin: 6px 0 0;
  font-size: 1.02rem;
  font-weight: 800;
  color: #170b02;
  letter-spacing: 0.005em;
  font-family: 'Playfair Display', Georgia, serif;
}

.filters-row {
  margin-bottom: 10px;
}

.filters-row.row-inline {
  margin-bottom: 0;
}

.status-segment {
  --background: #fbf7f2;
  --border-radius: 14px;
  padding: 4px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding-inline: 0;
}

:deep(.status-segment .ion-segment-button) {
  --color-checked: #ffffff;
  --indicator-color: transparent;
  --background-checked: linear-gradient(135deg, #d76f02, #e68a33);
  --border-radius: 12px;
  --color: #475569;
  --padding-start: 12px;
  --padding-end: 12px;
  font-weight: 700;
  letter-spacing: 0.01em;
  min-width: 0;
  flex: 0 0 auto;
}

:deep(.status-segment .ion-segment-button.segment-button-checked) {
  color: #fff;
  box-shadow: 0 8px 18px rgba(215,111,2,0.26);
}

.filters-search-shell {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px;
  background: #fbf7f2;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 16px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.filters-search-shell:focus-within {
  border-color: #d76f02;
  box-shadow: 0 0 0 3px rgba(215, 111, 2, 0.10);
}

.filters-search-icon {
  color: #64748b;
  font-size: 1rem;
  flex: 0 0 auto;
}

.filters-search-input {
  flex: 1 1 auto;
  min-width: 0;
}

.summary-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin: 18px 0 4px;
}

.summary-item {
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 18px;
  padding: 14px 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.summary-item span {
  font-size: 1.3rem;
  font-weight: 800;
  color: #170b02;
  letter-spacing: -0.01em;
}

.summary-item small {
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.summary-item.total span {
  color: #170b02;
}

.summary-item.pending span {
  color: #f59e0b;
}

.summary-item.paid span {
  color: #10b981;
}

.bookings-list-shell {
  margin-top: 22px;
}

.list-head {
  padding: 0 2px;
}

.list-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.list-title {
  margin: 6px 0 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
}

.list-divider {
  margin: 12px 2px 14px;
  height: 1px;
  background: rgba(23, 11, 2, 0.08);
}

.bookings-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.header-print-btn {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  --background: transparent;
  --background-hover: rgba(26, 58, 122, 0.06);
  --background-activated: rgba(26, 58, 122, 0.12);
  --color: #1a3a7a;
  --box-shadow: none;
  margin-right: 4px;
}

.header-cta-icon {
  font-size: 1.2rem;
}

.filter-btn {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  --background-hover: rgba(215, 111, 2, 0.08);
  --background-activated: rgba(215, 111, 2, 0.16);
  --box-shadow: none;
  --border-radius: 14px;
}

.filter-btn.filter-active {
  --background: #d76f02;
  --background-hover: #c36202;
  --background-activated: #b05902;
  --color: #ffffff;
  --border-color: #d76f02;
  border: 1px solid #d76f02;
}

.filter-btn.filter-collapsed {
  --background: transparent;
  --background-hover: rgba(215, 111, 2, 0.06);
  --background-activated: rgba(215, 111, 2, 0.12);
  --color: #d76f02;
  --border-color: rgba(23, 11, 2, 0.12);
  border: 1px solid rgba(23, 11, 2, 0.12);
}

.filter-icon {
  font-size: 1.2rem;
  color: #d76f02;
}

.filter-btn.filter-active .filter-icon {
  color: #ffffff;
}

.empty-block {
  padding: 28px 18px;
  border-radius: 20px;
  border: 1px dashed rgba(215, 111, 2, 0.25);
  background: #fbf7f2;
  text-align: center;
  color: #d76f02;
  font-size: 0.9rem;
}

.empty-icon {
  font-size: 1.6rem;
  color: #d76f02;
  margin-bottom: 6px;
  display: inline-block;
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

:deep(.fab-shell .fab-sub) {
  width: 46px;
  height: 46px;
  --border-radius: 16px;
}
:deep(.fab-shell .booking-sub) {
  --background: linear-gradient(135deg, #1a3a7a, #1e4489);
  --color: #fff;
}
:deep(.fab-shell .payment-sub) {
  --background: linear-gradient(135deg, #10b981, #12c490);
  --color: #fff;
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

@media print {
  ion-header,
  ion-tab-bar,
  .fab-shell,
  .filter-btn,
  .header-print-btn {
    display: none !important;
  }
  .bookings-content {
    --background: #ffffff;
  }
  .bookings-page {
    background: #ffffff;
  }
  .content-shell {
    padding: 0;
    max-width: 100%;
  }
}

@media (min-width: 768px) {
  .content-shell {
    max-width: 860px;
    margin: 0 auto;
    padding: 0 24px;
  }
}
</style>
