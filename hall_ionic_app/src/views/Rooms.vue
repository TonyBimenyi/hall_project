<template>
  <ion-page class="rooms-page">
    <HeaderBar title="Chambres &amp; Salles" eyebrow="Inventaire" :show-menu="false">
      <template #actions>
        <ion-button class="header-print-btn" @click="handlePrint">
          <Icon icon="solar:printer-linear" class="header-cta-icon" />
        </ion-button>
      </template>
    </HeaderBar>

    <ion-content class="rooms-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement de l'inventaire"
      />
      <div class="content-shell">

        <section class="category-shell">
          <ion-segment v-model="activeCategory" class="category-segment" :scrollable="false">
            <ion-segment-button value="rooms">
              <ion-label class="seg-label">
                <Icon icon="solar:bed-linear" class="seg-ic" />
                Chambres <span class="pill-count">({{ roomCounts.rooms }})</span>
              </ion-label>
            </ion-segment-button>
            <ion-segment-button value="halls">
              <ion-label class="seg-label">
                <Icon icon="solar:buildings-2-linear" class="seg-ic" />
                Salles <span class="pill-count">({{ roomCounts.halls }})</span>
              </ion-label>
            </ion-segment-button>
          </ion-segment>
        </section>

        <section class="status-strip">
          <button
            v-for="chip in statusChips"
            :key="chip.value"
            :class="['status-chip', { active: activeStatus === chip.value }]"
            @click="activeStatus = chip.value"
          >
            <span :class="['status-chip-dot', `dot-${chip.value}`]" />
            <span class="status-chip-label">{{ chip.label }}</span>
            <span class="status-chip-count">{{ categoryStatusCounts[chip.value] || 0 }}</span>
          </button>
        </section>

        <section class="rooms-hero">
          <div class="rooms-hero-copy">
            <div class="rooms-hero-kicker">État en temps réel</div>
            <h1 class="rooms-hero-title">{{ filteredRooms.length }} {{ activeCategory === 'halls' ? 'salle' : 'chambre' }}{{ filteredRooms.length > 1 ? 's' : '' }}</h1>
            <p class="rooms-hero-sub">{{ activeCategory === 'halls' ? 'Salles de réception et conférence' : 'Chambres nuitée' }}, disponible{{ filteredRooms.length > 1 ? 's' : '' }} immédiatement.</p>
          </div>
          <div class="rooms-hero-chart">
            <div class="hero-arc">
              <div class="hero-arc-fill" :style="{ '--pct': occupancyPct + '%' }"></div>
              <div class="hero-arc-value">{{ occupancyPct }}%</div>
              <div class="hero-arc-label">Occupation</div>
            </div>
          </div>
        </section>

        <section class="rooms-list-shell">
          <div class="list-head">
            <div>
              <div class="list-kicker">Liste</div>
              <h2 class="list-title">{{ activeCategory === 'halls' ? 'Salles' : 'Chambres' }}</h2>
            </div>
          </div>
          <div class="list-divider" aria-hidden="true"></div>

          <div class="rooms-stack">
            <RoomCard
              v-for="room in filteredRooms"
              :key="room.id"
              :room="room"
              @view="toastRoomView"
              @edit="toastRoomEdit"
              @delete="handleDeleteRoom"
            />
            <div v-if="!filteredRooms.length" class="empty-block">
              <Icon :icon="activeCategory === 'halls' ? 'solar:buildings-2-linear' : 'solar:bed-linear'" class="empty-icon" />
              <p>Aucune {{ activeCategory === 'halls' ? 'salle' : 'chambre' }} dans ce statut.</p>
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
          <ion-fab-button v-if="activeCategory !== 'halls'" class="fab-sub room-sub" @click="toastNewRoom">
            <Icon icon="solar:bed-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button v-if="activeCategory !== 'rooms'" class="fab-sub hall-sub" @click="toastNewHall">
            <Icon icon="solar:buildings-2-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
        </ion-fab-list>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonContent, IonFab, IonFabButton, IonFabList, IonLabel, IonPage, IonSegment, IonSegmentButton } from '@ionic/vue'
import { endpoints } from '@/lib/api.js'
import HeaderBar from '@/components/HeaderBar.vue'
import RoomCard from '@/components/RoomCard.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'

const MOCK_ROOMS = [
  { id: 101, room_number: '101', name: 'Chambre Double Deluxe', room_type: 'double', status: 'occupied', capacity: 2, price_per_night: 185000, additional_services: [{ name: 'Petit-déjeuner' }, { name: 'Wi-Fi premium' }] },
  { id: 102, room_number: '102', name: 'Chambre Double Standard', room_type: 'double', status: 'available', capacity: 2, price_per_night: 120000, additional_services: [{ name: 'Petit-déjeuner' }] },
  { id: 103, room_number: '103', name: 'Chambre Simple Standard', room_type: 'single', status: 'reserved', capacity: 1, price_per_night: 95000, additional_services: [{ name: 'Wi-Fi' }] },
  { id: 104, room_number: '104', name: 'Chambre Twin', room_type: 'twin', status: 'available', capacity: 2, price_per_night: 130000, additional_services: [{ name: 'Petit-déjeuner' }, { name: 'Wi-Fi' }] },
  { id: 201, room_number: '201', name: 'Chambre Familiale', room_type: 'family', status: 'cleaning', capacity: 5, price_per_night: 285000, additional_services: [{ name: 'Petit-déjeuner' }, { name: 'Minibar' }, { name: 'Wi-Fi premium' }] },
  { id: 202, room_number: '202', name: 'Chambre Simple Standard', room_type: 'single', status: 'available', capacity: 1, price_per_night: 95000, additional_services: [{ name: 'Petit-déjeuner' }] },
  { id: 303, room_number: '303', name: 'Suite Présidentielle', room_type: 'suite', status: 'maintenance', capacity: 4, price_per_night: 420000, additional_services: [{ name: 'Petit-déjeuner' }, { name: 'Accès spa' }, { name: 'Wi-Fi premium' }, { name: 'Bar gratuit' }] }
]

const MOCK_HALLS = [
  { id: 'h1', is_hall: true, code: 'SR', name: 'Salle Royale', room_type: 'hall', status: 'available', capacity: 250, price: 2850000, additional_services: [{ name: 'Éclairage scène' }, { name: 'Sonorisation' }, { name: 'Tables & chaises' }] },
  { id: 'h2', is_hall: true, code: 'SS', name: 'Salle Séminaire', room_type: 'conference', status: 'reserved', capacity: 80, price: 950000, additional_services: [{ name: 'Vidéo projecteur' }, { name: 'Wi-Fi premium' }] },
  { id: 'h3', is_hall: true, code: 'SJ', name: 'Salle des Fêtes', room_type: 'event', status: 'occupied', capacity: 150, price: 1850000, additional_services: [{ name: 'Piste de danse' }, { name: 'Bar' }] }
]

export default {
  name: 'RoomsView',
  components: {
    IonContent,
    IonFab,
    IonFabButton,
    IonFabList,
    IonLabel,
    IonPage,
    IonSegment,
    IonSegmentButton,
    HeaderBar,
    RoomCard,
    LoadingOverlay
  },
  data() {
    return {
      activeCategory: 'rooms',
      activeStatus: 'all',
      statusChips: [
        { value: 'all', label: 'Tout' },
        { value: 'available', label: 'Disponible' },
        { value: 'reserved', label: 'Réservée' },
        { value: 'occupied', label: 'Occupée' },
        { value: 'cleaning', label: 'Nettoyage' },
        { value: 'maintenance', label: 'Maintenance' }
      ],
      loading: true,
      rooms: [],
      halls: []
    }
  },
  computed: {
    roomCounts() {
      return {
        rooms: Array.isArray(this.rooms) ? this.rooms.length : 0,
        halls: Array.isArray(this.halls) ? this.halls.length : 0
      }
    },
    activeList() {
      return this.activeCategory === 'halls' ? (this.halls || []) : (this.rooms || [])
    },
    categoryStatusCounts() {
      const counts = { all: this.activeList.length }
      for (const r of this.activeList) {
        counts[r.status] = (counts[r.status] || 0) + 1
      }
      return counts
    },
    filteredRooms() {
      if (this.activeStatus === 'all') return this.activeList
      return this.activeList.filter((r) => String(r.status || '') === this.activeStatus)
    },
    occupancyPct() {
      const total = this.activeList.length || 1
      const occupied = this.activeList.filter((r) => ['occupied', 'reserved'].includes(r.status)).length
      return Math.round((occupied / total) * 100)
    },
    showLoading() {
      return this.loading
    }
  },
  watch: {},
  methods: {
    toastRoomView() {
      alert('Voir détails (à venir)')
    },
    toastRoomEdit() {
      alert('Modifier (à venir)')
    },
    handleDeleteRoom(r) {
      const name = r?.name || (this.activeCategory === 'halls' ? 'cette salle' : 'cette chambre')
      const ok = window.confirm(`Supprimer ${name} ?`)
      if (!ok) return
      try {
        if (this.activeCategory === 'halls') {
          endpoints.deleteHall && endpoints.deleteHall(r?.id).catch(() => null)
          this.halls = this.halls.filter((x) => x.id !== r?.id)
        } else {
          endpoints.deleteRoom && endpoints.deleteRoom(r?.id).catch(() => null)
          this.rooms = this.rooms.filter((x) => x.id !== r?.id)
        }
      } catch (_) {
        if (this.activeCategory === 'halls') {
          this.halls = this.halls.filter((x) => x.id !== r?.id)
        } else {
          this.rooms = this.rooms.filter((x) => x.id !== r?.id)
        }
      }
    },
    toastNewRoom() {
      alert('Nouvelle chambre (à venir)')
    },
    toastNewHall() {
      alert('Nouvelle salle (à venir)')
    },
    handlePrint() {
      window.print()
    },
    async loadInventory() {
      this.loading = true
      try {
        const [roomsData, hallsData] = await Promise.all([
          endpoints.rooms(),
          endpoints.halls()
        ])

        const roomsList = Array.isArray(roomsData) ? roomsData : (roomsData?.results || roomsData?.data || [])
        const hallsList = Array.isArray(hallsData) ? hallsData : (hallsData?.results || hallsData?.data || [])

        this.rooms = roomsList.length ? roomsList : MOCK_ROOMS
        this.halls = hallsList.length ? hallsList.map((h, idx) => ({
          id: h.id != null ? h.id : `hall-idx-${idx}`,
          is_hall: true,
          room_number: h.code || h.hall_code || `S${h.id ?? idx + 1}`,
          name: h.name || 'Salle',
          room_type: h.room_type || h.type || 'hall',
          status: h.status || 'available',
          capacity: h.capacity || 0,
          price_per_night: h.price_per_night || h.price || 0,
          additional_services: Array.isArray(h.additional_services) ? h.additional_services : (h.amenities || [])
        })) : MOCK_HALLS
      } catch (_err) {
        this.rooms = MOCK_ROOMS
        this.halls = MOCK_HALLS
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.loadInventory()
  }
}
</script>

<style scoped>
.rooms-page {
  background: #fbf7f2;
}

.rooms-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
  position: relative;
  z-index: 1;
}

.category-shell {
  margin-top: 16px;
  padding: 4px;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 18px;
  box-shadow: 0 8px 22px rgba(23, 11, 2, 0.04);
}

.category-segment {
  --background: #ffffff;
  --border-radius: 14px;
  padding: 2px;
}

:deep(.category-segment .ion-segment-button) {
  --indicator-color: transparent;
  --background-checked: transparent;
  --color-checked: #ffffff;
  --color: #475569;
  --border-radius: 14px;
  --padding-start: 10px;
  --padding-end: 10px;
  --padding-top: 8px;
  --padding-bottom: 8px;
  min-height: 44px;
  font-weight: 700;
  letter-spacing: 0.01em;
}

:deep(.category-segment .ion-segment-button.segment-button-checked) {
  background: linear-gradient(135deg, #d76f02, #e68a33);
  color: #ffffff;
  box-shadow: 0 8px 20px rgba(215,111,2,0.26);
}

.seg-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.86rem;
  white-space: nowrap;
}

.seg-ic {
  font-size: 1rem;
}

.pill-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1px 7px;
  border-radius: 999px;
  background: rgba(23, 11, 2, 0.08);
  font-size: 0.72rem;
  font-weight: 800;
  color: inherit;
  opacity: 0.9;
}

:deep(.category-segment .ion-segment-button.segment-button-checked .pill-count) {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}

.status-strip {
  margin-top: 14px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  padding: 4px 2px 6px;
}

.status-strip::-webkit-scrollbar { display: none; }

.status-chip {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #fff8f0;
  border: 1px solid rgba(23, 11, 2, 0.08);
  color: #64748b;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  transition: all 0.2s ease;
  cursor: pointer;
}

.status-chip.active {
  background: #d76f02;
  color: #ffffff;
  border-color: #d76f02;
  box-shadow: 0 10px 20px rgba(215, 111, 2, 0.18);
}

.status-chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-chip-dot.dot-all { background: #94a3b8; }
.status-chip-dot.dot-available { background: #16a34a; }
.status-chip-dot.dot-reserved { background: #2563eb; }
.status-chip-dot.dot-occupied { background: #061b49; }
.status-chip-dot.dot-cleaning { background: #d4a017; }
.status-chip-dot.dot-maintenance { background: #dc2626; }

.status-chip-count {
  font-weight: 800;
  font-size: 0.78rem;
  padding: 1px 7px;
  border-radius: 999px;
  background: rgba(23, 11, 2, 0.06);
}

.status-chip.active .status-chip-count {
  background: rgba(255, 255, 255, 0.18);
}

.rooms-hero {
  margin-top: 12px;
  padding: 22px 20px 20px;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.18), transparent 44%),
    linear-gradient(135deg, #1a3a7a 0%, #17336b 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 22px 42px rgba(26, 58, 122, 0.22);
}

.rooms-hero-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rooms-hero-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d4af37;
  font-weight: 700;
}

.rooms-hero-title {
  margin: 4px 0 0;
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: #ffffff;
  font-family: 'Playfair Display', Georgia, serif;
}

.rooms-hero-sub {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.86rem;
  line-height: 1.45;
  max-width: 30ch;
}

.rooms-hero-chart {
  flex: 0 0 auto;
}

.hero-arc {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: conic-gradient(#d4af37 var(--pct, 60%), rgba(255, 255, 255, 0.12) var(--pct, 60%));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  position: relative;
  box-shadow: inset 0 0 0 3px #d76f02;
}

.hero-arc::before {
  content: "";
  position: absolute;
  inset: 10px;
  border-radius: 50%;
  background: rgba(23, 51, 107, 0.96);
}

.hero-arc-fill {
  display: none;
}

.hero-arc-value,
.hero-arc-label {
  position: relative;
  z-index: 1;
}

.hero-arc-value {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: #ffffff;
}

.hero-arc-label {
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 700;
  margin-top: 1px;
}

.rooms-list-shell {
  margin-top: 22px;
}

.list-head {
  padding: 0 2px;
}

.list-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 700;
}

.list-title {
  margin: 6px 0 0;
  font-size: 1.05rem;
  font-weight: 800;
  font-family: 'Playfair Display', Georgia, serif;
  color: #170b02;
}

.list-divider {
  margin: 12px 2px 14px;
  height: 1px;
  background: rgba(23, 11, 2, 0.08);
}

.rooms-stack {
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

.empty-block {
  padding: 28px 18px;
  border-radius: 20px;
  border: 1px dashed rgba(215, 111, 2, 0.3);
  background: #fff8f0;
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
:deep(.fab-shell .room-sub) {
  --background: linear-gradient(135deg, #1a3a7a, #1e4489);
  --color: #fff;
}
:deep(.fab-shell .hall-sub) {
  --background: linear-gradient(135deg, #d4af37, #e0bf5a);
  --color: #170b02;
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
  .header-print-btn,
  .category-shell {
    display: none !important;
  }
  .rooms-content { --background: #ffffff; }
  .rooms-page { background: #ffffff; }
}

@media (min-width: 768px) {
  .content-shell {
    max-width: 860px;
    margin: 0 auto;
    padding: 0 24px;
  }
}
</style>
