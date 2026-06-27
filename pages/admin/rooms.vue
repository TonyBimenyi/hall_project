<template>
  <div class="admin-rooms">
    <div class="header-actions">
      <div class="page-title">
        <h1>Gestion des Chambres</h1>
        <p>Créer, modifier et suivre les capacités et tarifs des chambres</p>
      </div>
      <button v-if="canManageFacilitiesCatalog" class="btn btn-primary btn-sm admin-head-btn" @click="openAddModal">
        <i class="fas fa-plus"></i>
        <span class="btn-label">Ajouter une chambre</span>
      </button>
    </div>

    <div v-if="showRoomStats" class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-door-closed"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total Chambres</span>
          <span class="stat-value">
            <span v-if="loadingRooms" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayTotalRooms }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <span class="stat-label">Capacité Totale</span>
          <span class="stat-value info">
            <span v-if="loadingRooms" class="skeleton-line skeleton-w-40"></span>
            <template v-else>{{ displayTotalCapacity }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-coins"></i></div>
        <div class="stat-info">
          <span class="stat-label">Prix Moyen / Nuit</span>
          <span class="stat-value success">
            <span v-if="loadingRooms" class="skeleton-line skeleton-w-60"></span>
            <template v-else>{{ formatMoney(displayAverageNightlyPrice) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-crown"></i></div>
        <div class="stat-info">
          <span class="stat-label">Plus Haute Tarification</span>
          <span class="stat-value warning">
            <span v-if="loadingRooms" class="skeleton-line skeleton-w-60"></span>
            <template v-else>{{ formatMoney(displayHighestNightlyPrice) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-circle-check"></i></div>
        <div class="stat-info">
          <span class="stat-label">Disponibles</span>
          <span class="stat-value success">{{ roomStatusCounts.available }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-bed"></i></div>
        <div class="stat-info">
          <span class="stat-label">Occupées</span>
          <span class="stat-value">{{ roomStatusCounts.occupied }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-soap"></i></div>
        <div class="stat-info">
          <span class="stat-label">Nettoyage</span>
          <span class="stat-value info">{{ roomStatusCounts.cleaning }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-bookmark"></i></div>
        <div class="stat-info">
          <span class="stat-label">Réservées</span>
          <span class="stat-value info">{{ roomStatusCounts.reserved }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-screwdriver-wrench"></i></div>
        <div class="stat-info">
          <span class="stat-label">Maintenance</span>
          <span class="stat-value warning">{{ roomStatusCounts.maintenance }}</span>
        </div>
      </div>
    </div>

    <div class="desk-tabs card">
      <button :class="['desk-tab-btn', { active: activeDeskTab === 'checkin' }]" @click="activeDeskTab = 'checkin'">
        <i class="fas fa-right-to-bracket"></i>
        <span>Check-in</span>
      </button>
      <button :class="['desk-tab-btn', { active: activeDeskTab === 'checkout' }]" @click="activeDeskTab = 'checkout'">
        <i class="fas fa-right-from-bracket"></i>
        <span>Check-out</span>
      </button>
      <button :class="['desk-tab-btn', { active: activeDeskTab === 'rooms' }]" @click="activeDeskTab = 'rooms'">
        <i class="fas fa-bed"></i>
        <span>Chambres</span>
      </button>
    </div>

    <div v-if="activeDeskTab !== 'rooms'" class="frontdesk-controls card">
      <div class="frontdesk-controls-top">
        <div class="frontdesk-search-shell">
          <i class="fas fa-search frontdesk-search-icon"></i>
          <input
            v-model="frontdeskSearch"
            type="text"
            class="frontdesk-search-input"
            placeholder="Rechercher par client, chambre ou code"
          />
        </div>
        <button class="btn btn-outline btn-sm frontdesk-reset-btn" @click="resetFrontdeskFilters">Réinitialiser</button>
      </div>
      <div class="frontdesk-filters-row">
        <select v-model="frontdeskPaymentFilter" class="frontdesk-select">
          <option value="all">Tous les paiements</option>
          <option value="settled">Séjours soldés</option>
          <option value="balance_due">Avec reste à payer</option>
        </select>
        <select v-model="frontdeskActivityWindow" class="frontdesk-select">
          <option value="24h">Activité 24h</option>
          <option value="72h">Activité 72h</option>
          <option value="7d">Activité 7 jours</option>
          <option value="all">Toute l’activité</option>
        </select>
      </div>
    </div>

    <div v-if="activeDeskTab !== 'rooms'" :class="['frontdesk-grid', `frontdesk-grid-${activeDeskTab}`]">
      <section v-if="activeDeskTab === 'checkin'" class="desk-panel card">
        <div class="desk-panel-head">
          <div>
            <h2>Arrivées / Check-in</h2>
            <p>Clients attendus ou réservations prêtes à accueillir.</p>
          </div>
          <div class="desk-panel-tools">
            <span class="desk-count">{{ pendingArrivalTotalItems }}</span>
            <AdminAppTablePagination
              :start="pendingArrivalStartIndex"
              :end="pendingArrivalEndIndex"
              :total="pendingArrivalTotalItems"
              :can-prev="pendingArrivalCanPrev"
              :can-next="pendingArrivalCanNext"
              :disabled="deskLoading"
              @prev="pendingArrivalPrevPage"
              @next="pendingArrivalNextPage"
            />
          </div>
        </div>
        <div v-if="deskLoading" class="desk-empty">Chargement des séjours...</div>
        <div v-else-if="filteredPendingArrivalBookings.length === 0" class="desk-empty">Aucune arrivée en attente</div>
          <div v-else class="desk-list desk-list-checkin">
          <div v-for="booking in paginatedPendingArrivalBookings" :key="`arrival-${booking.id}`" class="desk-item">
            <div class="desk-item-main">
              <div class="desk-item-title">{{ roomStayGuestLabel(booking) }}</div>
              <div class="desk-item-sub">{{ booking.room_display || '-' }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              <div class="desk-item-meta">
                <span :class="['status-pill', `status-${booking.room_status || 'reserved'}`]">{{ roomStatusLabel(booking.room_status || 'reserved') }}</span>
                <span class="desk-mini">{{ booking.code || '-' }}</span>
                <span class="desk-mini">{{ booking.guest_count || 0 }} pers.</span>
              </div>
            </div>
            <div class="desk-item-actions">
              <button v-if="Number(booking.remaining_amount || 0) > 0" class="btn btn-outline btn-sm" @click="openPaymentForBooking(booking)">Paiement</button>
              <button class="btn btn-primary btn-sm" :class="{ 'is-loading': isStayActionLoading(booking, 'check_in') }" :disabled="stayActionLoadingId || !booking.can_check_in" @click="openStayModal(booking, 'check_in')">Check-in</button>
              <button class="btn btn-outline btn-sm" @click="openBookingDetails(booking)">Détails</button>
            </div>
          </div>
        </div>
      </section>

      <section v-if="activeDeskTab === 'checkout'" class="desk-panel card">
        <div class="desk-panel-head">
          <div>
            <h2>Séjours en cours</h2>
            <p>Clients présents dans l'hôtel et prêts au départ.</p>
          </div>
          <div class="desk-panel-tools">
            <span class="desk-count">{{ inHouseTotalItems }}</span>
            <AdminAppTablePagination
              :start="inHouseStartIndex"
              :end="inHouseEndIndex"
              :total="inHouseTotalItems"
              :can-prev="inHouseCanPrev"
              :can-next="inHouseCanNext"
              :disabled="deskLoading"
              @prev="inHousePrevPage"
              @next="inHouseNextPage"
            />
          </div>
        </div>
        <div v-if="deskLoading" class="desk-empty">Chargement des séjours...</div>
        <div v-else-if="filteredInHouseBookings.length === 0" class="desk-empty">Aucun client en chambre</div>
          <div v-else class="desk-list">
          <div v-for="booking in paginatedInHouseBookings" :key="`stay-${booking.id}`" class="desk-item">
            <div class="desk-item-main">
              <div class="desk-item-title">{{ roomStayGuestLabel(booking) }}</div>
              <div class="desk-item-sub">{{ booking.room_display || '-' }} • Check-in {{ formatDeskDateTime(booking.checked_in_at) }}</div>
              <div class="desk-item-meta">
                <span :class="['status-pill', 'status-occupied']">Occupée</span>
                <span class="desk-mini">{{ booking.code || '-' }}</span>
                <span class="desk-mini">{{ booking.guest_count || 0 }} pers.</span>
              </div>
            </div>
            <div class="desk-item-actions">
              <button v-if="Number(booking.remaining_amount || 0) > 0" class="btn btn-outline btn-sm" @click="openPaymentForBooking(booking)">Solder</button>
              <button class="btn btn-primary btn-sm" :class="{ 'is-loading': isStayActionLoading(booking, 'check_out') }" :disabled="stayActionLoadingId || Number(booking.remaining_amount || 0) > 0 || !booking.can_check_out" @click="manageStay(booking, 'check_out')">Check-out</button>
              <button class="btn btn-outline btn-sm" @click="openBookingDetails(booking)">Détails</button>
            </div>
          </div>
        </div>
      </section>

      <section v-if="activeDeskTab === 'checkout'" class="desk-panel card">
        <div class="desk-panel-head">
          <div>
            <h2>Nettoyage / remise en service</h2>
            <p>Chambres libérées qui doivent être préparées avant la prochaine arrivée.</p>
          </div>
          <div class="desk-panel-tools">
            <span class="desk-count">{{ cleaningTotalItems }}</span>
            <AdminAppTablePagination
              :start="cleaningStartIndex"
              :end="cleaningEndIndex"
              :total="cleaningTotalItems"
              :can-prev="cleaningCanPrev"
              :can-next="cleaningCanNext"
              :disabled="deskLoading"
              @prev="cleaningPrevPage"
              @next="cleaningNextPage"
            />
          </div>
        </div>
        <div v-if="deskLoading" class="desk-empty">Chargement des chambres...</div>
        <div v-else-if="filteredCleaningRoomsList.length === 0" class="desk-empty">Aucune chambre en nettoyage</div>
        <div v-else class="desk-list">
          <div v-for="room in paginatedCleaningRooms" :key="`clean-${room.id}`" class="desk-item">
            <div class="desk-item-main">
              <div class="desk-item-title">{{ room.room_number }} - {{ room.name }}</div>
              <div class="desk-item-sub">{{ roomTypeLabel(room.room_type) }} • {{ formatMoney(room.price_per_night) }}/nuit</div>
              <div class="desk-item-meta">
                <span :class="['status-pill', 'status-cleaning']">Nettoyage</span>
                <span class="desk-mini" v-if="lastCompletedStayForRoom(room.id)?.checked_out_at">Sortie: {{ formatDeskDateTime(lastCompletedStayForRoom(room.id).checked_out_at) }}</span>
                <span class="desk-mini" v-if="nextReservationForRoom(room.id)">Prochaine arrivée: {{ roomStayGuestLabel(nextReservationForRoom(room.id)) }}</span>
              </div>
            </div>
            <div class="desk-item-actions">
              <button v-if="canManageFacilitiesCatalog" class="btn btn-primary btn-sm" @click="setRoomStatus(room, 'available')">Marquer prête</button>
              <button v-if="nextReservationForRoom(room.id)" class="btn btn-outline btn-sm" @click="openBookingDetails(nextReservationForRoom(room.id))">Voir réservation</button>
            </div>
          </div>
        </div>
      </section>

      <section class="desk-activity card">
        <div class="desk-panel-head desk-activity-head">
          <div>
            <h2>Activité récente</h2>
            <p>Suivi rapide des dernières arrivées et sorties enregistrées.</p>
          </div>
          <div class="desk-activity-badges">
            <span class="desk-mini">Entrées: {{ filteredRecentCheckIns.length }}</span>
            <span class="desk-mini">Sorties: {{ filteredRecentCheckOuts.length }}</span>
          </div>
        </div>

        <div class="desk-activity-grid">
          <div class="activity-column">
            <div class="activity-column-head">
              <div>
                <strong>Check-ins récents</strong>
                <small>Derniers clients arrivés</small>
              </div>
              <div class="activity-column-tools">
                <span class="status-pill status-occupied">Arrivées</span>
                <AdminAppTablePagination
                  :start="recentCheckInsStartIndex"
                  :end="recentCheckInsEndIndex"
                  :total="recentCheckInsTotalItems"
                  :can-prev="recentCheckInsCanPrev"
                  :can-next="recentCheckInsCanNext"
                  :disabled="deskLoading"
                  @prev="recentCheckInsPrevPage"
                  @next="recentCheckInsNextPage"
                />
              </div>
            </div>
            <div v-if="deskLoading" class="desk-empty">Chargement des arrivées...</div>
            <div v-else-if="filteredRecentCheckIns.length === 0" class="desk-empty">Aucun check-in récent</div>
            <div v-else class="activity-list">
              <div v-for="booking in paginatedRecentCheckIns" :key="`recent-checkin-${booking.id}`" class="activity-item">
                <div class="activity-item-main">
                  <div class="activity-title">{{ roomStayGuestLabel(booking) }}</div>
                  <div class="activity-sub">{{ booking.room_display || '-' }} • {{ booking.code || '-' }}</div>
                  <div class="activity-time">Entrée le {{ formatDeskDateTime(booking.checked_in_at) }}</div>
                </div>
                <button class="btn btn-outline btn-sm" @click="openBookingDetails(booking)">Détails</button>
              </div>
            </div>
          </div>

          <div class="activity-column">
            <div class="activity-column-head">
              <div>
                <strong>Check-outs récents</strong>
                <small>Derniers clients partis</small>
              </div>
              <div class="activity-column-tools">
                <span class="status-pill status-cleaning">Départs</span>
                <AdminAppTablePagination
                  :start="recentCheckOutsStartIndex"
                  :end="recentCheckOutsEndIndex"
                  :total="recentCheckOutsTotalItems"
                  :can-prev="recentCheckOutsCanPrev"
                  :can-next="recentCheckOutsCanNext"
                  :disabled="deskLoading"
                  @prev="recentCheckOutsPrevPage"
                  @next="recentCheckOutsNextPage"
                />
              </div>
            </div>
            <div v-if="deskLoading" class="desk-empty">Chargement des sorties...</div>
            <div v-else-if="filteredRecentCheckOuts.length === 0" class="desk-empty">Aucun check-out récent</div>
            <div v-else class="activity-list">
              <div v-for="booking in paginatedRecentCheckOuts" :key="`recent-checkout-${booking.id}`" class="activity-item">
                <div class="activity-item-main">
                  <div class="activity-title">{{ roomStayGuestLabel(booking) }}</div>
                  <div class="activity-sub">{{ booking.room_display || '-' }} • {{ booking.code || '-' }}</div>
                  <div class="activity-time">Sortie le {{ formatDeskDateTime(booking.checked_out_at) }}</div>
                </div>
                <button class="btn btn-outline btn-sm" @click="openBookingDetails(booking)">Détails</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="desk-guide card">
        <div class="desk-guide-head">
          <h2>Processus normal</h2>
          <p>Gestion claire du séjour, de la réservation à la remise en service.</p>
        </div>
        <div class="desk-guide-grid">
          <div class="guide-step">
            <strong>1. Réservation</strong>
            <span>Disponible → Réservée</span>
            <small>Une réservation existe, le client n'est pas encore arrivé.</small>
          </div>
          <div class="guide-step">
            <strong>2. Check-in</strong>
            <span>Réservée → Occupée</span>
            <small>Le client est enregistré et la chambre est attribuée.</small>
          </div>
          <div class="guide-step">
            <strong>3. Check-out</strong>
            <span>Occupée → Nettoyage</span>
            <small>Facture soldée, départ validé, séjour clôturé.</small>
          </div>
          <div class="guide-step">
            <strong>4. Chambre prête</strong>
            <span>Nettoyage → Disponible</span>
            <small>Le ménage confirme que la chambre peut repartir en vente.</small>
          </div>
        </div>
      </section>
    </div>

    <div v-if="activeDeskTab === 'rooms'" class="table-container card">
      <div class="rooms-table-toolbar" style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <h2 class="table-title" style="margin-bottom:0;">Toutes les chambres ({{ loadingRooms ? '...' : rooms.length }})</h2>
        <AdminAppTablePagination
          :start="roomsStartIndex"
          :end="roomsEndIndex"
          :total="roomsTotalItems"
          :can-prev="roomsCanPrev"
          :can-next="roomsCanNext"
          :disabled="loadingRooms"
          @prev="roomsPrevPage"
          @next="roomsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingRooms">
          <div v-for="n in 6" :key="`sk-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-70"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-50"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-60"></div>
              <div class="skeleton-line skeleton-w-40"></div>
              <div class="skeleton-line skeleton-w-50"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="room in paginatedRooms" :key="room.id" class="admin-card">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ room.name }} ({{ room.room_number }})</div>
                <div class="admin-card-subtitle">{{ room.capacity }} pers. • {{ roomTypeLabel(room.room_type) }} • {{ formatMoney(room.price_per_night) }}/nuit • {{ roomStatusLabel(room.status) }}</div>
              </div>

              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(room.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === room.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewRoom(room)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button v-if="canManageFacilitiesCatalog && room.status === 'cleaning'" class="actions-item" @click="setRoomStatus(room, 'available')">
                    <i class="fas fa-broom"></i> Marquer prête
                  </button>
                  <button v-if="canManageFacilitiesCatalog && room.status !== 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'maintenance')">
                    <i class="fas fa-screwdriver-wrench"></i> Mettre en maintenance
                  </button>
                  <button v-if="canManageFacilitiesCatalog && room.status === 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'available')">
                    <i class="fas fa-circle-check"></i> Rendre disponible
                  </button>
                  <button v-if="canManageFacilitiesCatalog" class="actions-item" @click="editRoom(room)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button v-if="canManageFacilitiesCatalog" class="actions-item danger" @click="confirmDelete(room)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">N° Chambre</span>
                <span class="v">{{ room.room_number }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Type</span>
                <span class="v">{{ roomTypeLabel(room.room_type) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Capacité</span>
                <span class="v">{{ room.capacity }} pers.</span>
              </div>
              <div class="admin-kv">
                <span class="k">Prix / Nuit</span>
                <span class="v">{{ formatMoney(room.price_per_night) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v"><span :class="['status-pill', `status-${room.status || 'available'}`]">{{ roomStatusLabel(room.status) }}</span></span>
              </div>
              <div class="admin-kv">
                <span class="k">Services additionnels</span>
                <span class="v">
                  <span :class="['service-state-pill', roomHasAdditionalServices(room) ? 'is-yes' : 'is-no']">
                    <i :class="roomHasAdditionalServices(room) ? 'fas fa-circle-check' : 'fas fa-ban'"></i>
                    {{ roomHasAdditionalServices(room) ? 'Oui' : 'Non' }}
                  </span>
                </span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingRooms && rooms.length === 0" class="empty-cell">Aucune chambre disponible</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('name') }" @click="toggleRoomSort('name')">Nom <i :class="roomSortIconClass('name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('room_number') }" @click="toggleRoomSort('room_number')">N° <i :class="roomSortIconClass('room_number')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('room_type') }" @click="toggleRoomSort('room_type')">Type <i :class="roomSortIconClass('room_type')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('capacity') }" @click="toggleRoomSort('capacity')">Capacité <i :class="roomSortIconClass('capacity')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('price_per_night') }" @click="toggleRoomSort('price_per_night')">Prix / Nuit <i :class="roomSortIconClass('price_per_night')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('status') }" @click="toggleRoomSort('status')">Statut <i :class="roomSortIconClass('status')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isRoomSortActive('services') }" @click="toggleRoomSort('services')">Services <i :class="roomSortIconClass('services')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingRooms">
            <tr v-for="n in 6" :key="`sk-${n}`">
              <td><div class="skeleton-line skeleton-w-60"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="room in paginatedRooms" :key="room.id">
              <td><strong>{{ room.name }}</strong></td>
              <td>{{ room.room_number }}</td>
              <td>{{ roomTypeLabel(room.room_type) }}</td>
              <td>{{ room.capacity }} pers.</td>
              <td>{{ formatMoney(room.price_per_night) }}</td>
              <td><span :class="['status-pill', `status-${room.status || 'available'}`]">{{ roomStatusLabel(room.status) }}</span></td>
              <td>
                <span :class="['service-state-pill', roomHasAdditionalServices(room) ? 'is-yes' : 'is-no']">
                  <i :class="roomHasAdditionalServices(room) ? 'fas fa-circle-check' : 'fas fa-ban'"></i>
                  {{ roomHasAdditionalServices(room) ? 'Oui' : 'Non' }}
                </span>
              </td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(room.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === room.id" class="actions-menu" @click.stop>
                    <button class="actions-item" @click="viewRoom(room)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button v-if="canManageFacilitiesCatalog && room.status === 'cleaning'" class="actions-item" @click="setRoomStatus(room, 'available')">
                      <i class="fas fa-broom"></i> Marquer prête
                    </button>
                    <button v-if="canManageFacilitiesCatalog && room.status !== 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'maintenance')">
                      <i class="fas fa-screwdriver-wrench"></i> Mettre en maintenance
                    </button>
                    <button v-if="canManageFacilitiesCatalog && room.status === 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'available')">
                      <i class="fas fa-circle-check"></i> Rendre disponible
                    </button>
                    <button v-if="canManageFacilitiesCatalog" class="actions-item" @click="editRoom(room)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button v-if="canManageFacilitiesCatalog" class="actions-item danger" @click="confirmDelete(room)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          <tr v-if="rooms.length === 0">
            <td colspan="8" class="empty-cell">Aucune chambre disponible</td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la chambre' : 'Ajouter une chambre'" width="500px">
      <form @submit.prevent="saveRoom" class="admin-form">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Nom de la chambre</label>
            <input v-model="form.name" type="text" class="form-input" required placeholder="Ex: Chambre Double Standard" />
          </div>
          <div class="form-group">
            <label class="form-label">Numéro de chambre</label>
            <input v-model="form.room_number" type="text" class="form-input" required placeholder="Ex: 101" />
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Type de chambre</label>
            <select v-model="form.room_type" class="form-select" required>
              <option v-for="type in roomTypeOptions" :key="type.value" :value="type.value">{{ type.label }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Statut</label>
            <select v-model="form.status" class="form-select" required>
              <option v-for="status in roomStatusOptions" :key="status.value" :value="status.value">{{ status.label }}</option>
            </select>
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Capacité</label>
            <input v-model.number="form.capacity" type="number" class="form-input" min="1" required />
          </div>
          <div class="form-group">
            <label class="form-label">Prix / Nuit (Fbu)</label>
            <input v-model="pricePerNightInput" inputmode="numeric" type="text" class="form-input" placeholder="0" required />
          </div>
        </div>
        <div class="services-section">
          <div class="services-head">
            <div>
              <h3>Services additionnels</h3>
              <p>Ajoutez les options payantes de cette chambre avec ou sans sous-services.</p>
            </div>
            <button type="button" class="btn btn-outline btn-sm" @click="addService">
              <i class="fas fa-plus"></i> Ajouter un service
            </button>
          </div>

          <div v-if="form.additional_services.length === 0" class="services-empty">
            Aucun service additionnel pour cette chambre.
          </div>

          <div v-for="(service, serviceIndex) in form.additional_services" :key="service.id" class="service-card">
            <div class="service-card-head">
              <strong>Service {{ serviceIndex + 1 }}</strong>
              <button type="button" class="btn-icon delete" title="Supprimer" @click="removeService(serviceIndex)">
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Nom du service</label>
                <input v-model="service.name" list="default-room-service-options" type="text" class="form-input" placeholder="Ex: Petit-déjeuner" />
              </div>
              <div class="form-group">
                <label :class="['toggle-field', 'service-toggle', { 'is-active': service.has_subservices }]">
                  <input v-model="service.has_subservices" type="checkbox" @change="onServiceHasSubservicesChange(service)" />
                  <span class="toggle-switch" aria-hidden="true">
                    <span class="toggle-knob"></span>
                  </span>
                  <span class="toggle-copy">
                    <strong>Ce service a des sous-services</strong>
                    <small>{{ service.has_subservices ? 'Les prix seront definis par sous-service.' : 'Un seul prix sera applique a ce service.' }}</small>
                  </span>
                </label>
              </div>
            </div>

            <div v-if="!service.has_subservices" class="form-group">
              <label class="form-label">Prix du service (Fbu)</label>
              <input v-model="buildServicePriceModel(service).value" inputmode="numeric" type="text" class="form-input" placeholder="0" />
            </div>

            <div v-else class="subservices-section">
              <div class="subservices-head">
                <strong>Sous-services</strong>
                <button type="button" class="btn btn-outline btn-sm" @click="addSubservice(service)">
                  <i class="fas fa-plus"></i> Ajouter un sous-service
                </button>
              </div>

              <div
                v-for="(subservice, subIndex) in service.subservices"
                :key="subservice.id"
                class="subservice-row"
              >
                <input v-model="subservice.name" type="text" class="form-input" :placeholder="`Sous-service ${subIndex + 1}`" />
                <input v-model="buildSubservicePriceModel(subservice).value" inputmode="numeric" type="text" class="form-input" placeholder="Prix (Fbu)" />
                <button type="button" class="btn-icon delete" title="Supprimer" @click="removeSubservice(service, subIndex)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </div>
          </div>
          <datalist id="default-room-service-options">
            <option v-for="serviceName in defaultRoomServiceOptions" :key="serviceName" :value="serviceName"></option>
          </datalist>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingRoom }" :disabled="savingRoom" @click="saveRoom">
          {{ isEditing ? 'Mettre à jour' : 'Ajouter' }}
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeskBookingModal" title="Détails de la réservation" width="700px">
      <div v-if="selectedDeskBooking" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ String(selectedDeskBooking.customer_name || 'RE').trim().slice(0, 2).toUpperCase() }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ getBookingDisplayId(selectedDeskBooking) }}</div>
            <h3>{{ selectedDeskBooking.customer_name }}</h3>
            <p>{{ selectedDeskBooking.room_display || '-' }} • {{ selectedDeskBooking.event_type || 'Séjour' }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', 'badge-info']">{{ getStatusTranslation(selectedDeskBooking.status) }}</span>
            <span class="badge badge-success">{{ formatMoney(selectedDeskBooking.total_price) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Réservation</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Client</span><span class="entity-view-value">{{ selectedDeskBooking.customer_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Téléphone</span><span class="entity-view-value">{{ selectedDeskBooking.customer_phone || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Email</span><span class="entity-view-value">{{ selectedDeskBooking.customer_email || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Chambre</span><span class="entity-view-value">{{ selectedDeskBooking.room_display || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Période</span><span class="entity-view-value">{{ formatDateRange(selectedDeskBooking.start_date, selectedDeskBooking.end_date) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Montant total</span><span class="entity-view-value">{{ formatMoney(selectedDeskBooking.total_price) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Déjà paye</span><span class="entity-view-value">{{ formatMoney(selectedDeskBooking.paid_amount) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Reste</span><span class="entity-view-value">{{ formatMoney(selectedDeskBooking.remaining_amount) }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Séjour</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Client hébergé</span><span class="entity-view-value">{{ selectedDeskBooking.guest_full_name || selectedDeskBooking.customer_name }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Pièce</span><span class="entity-view-value">{{ guestIdSummary(selectedDeskBooking) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut chambre</span><span class="entity-view-value">{{ roomStatusLabel(selectedDeskBooking.room_status || 'reserved') }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Check-in</span><span class="entity-view-value">{{ selectedDeskBooking.checked_in_at ? formatDeskDateTime(selectedDeskBooking.checked_in_at) : 'Non effectué' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Check-out</span><span class="entity-view-value">{{ selectedDeskBooking.checked_out_at ? formatDeskDateTime(selectedDeskBooking.checked_out_at) : 'Non effectué' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedDeskBooking.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedDeskBooking.updated_by_name || selectedDeskBooking.created_by_name || '-' }}</span></div>
            </div>
          </section>
        </div>
      </div>
      <template #footer>
        <button
          v-if="selectedDeskBooking && Number(selectedDeskBooking.remaining_amount || 0) > 0"
          class="btn btn-outline"
          @click="openPaymentForBooking(selectedDeskBooking)"
        >
          Enregistrer un paiement
        </button>
        <button class="btn btn-primary" @click="showDeskBookingModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeskPaymentModal" title="Enregistrer un paiement" width="560px">
      <form class="admin-form" @submit.prevent="saveDeskPayment">
        <div v-if="selectedDeskBooking" class="booking-summary">
          <div><strong>Réservation:</strong> {{ getBookingDisplayId(selectedDeskBooking) }}</div>
          <div><strong>Client:</strong> {{ selectedDeskBooking.customer_name }}</div>
          <div><strong>Chambre:</strong> {{ selectedDeskBooking.room_display || '-' }}</div>
          <div><strong>Total:</strong> {{ formatMoney(selectedDeskBooking.total_price) }}</div>
          <div><strong>Déjà paye:</strong> {{ formatMoney(selectedDeskBooking.paid_amount) }}</div>
          <div><strong>Reste:</strong> {{ formatMoney(selectedDeskBooking.remaining_amount) }}</div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Type de paiement</label>
            <select v-model="deskPaymentForm.kind" class="form-select" @change="onDeskPaymentKindChange">
              <option value="advance">Avance</option>
              <option value="full">Paiement total</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Montant (Fbu)</label>
            <input v-model="deskPaymentAmountInput" inputmode="numeric" type="text" class="form-input" placeholder="0" required />
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Date *</label>
            <input v-model="deskPaymentForm.date" type="date" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Méthode *</label>
            <select v-model="deskPaymentForm.method" class="form-select" required>
              <option value="Virement">Virement</option>
              <option value="Espèces">Espèces</option>
              <option value="Carte">Carte</option>
              <option value="Mobile Money">Mobile Money</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Référence *</label>
          <input v-model="deskPaymentForm.reference" type="text" class="form-input" required />
        </div>

      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showDeskPaymentModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingDeskPayment }" :disabled="savingDeskPayment" @click="saveDeskPayment">
          Enregistrer
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showStayModal" :title="selectedRoomStay?.action === 'check_out' ? 'Check-out chambre' : 'Check-in chambre'" width="680px">
      <div v-if="selectedRoomStay" class="stay-modal-shell">
        <div class="stay-modal-summary">
          <div><strong>Réservation:</strong> {{ selectedRoomStay.code || getBookingDisplayId(selectedRoomStay.booking) }}</div>
          <div><strong>Chambre:</strong> {{ selectedRoomStay.room_display }}</div>
          <div><strong>Client:</strong> {{ selectedRoomStay.customer_name }}</div>
          <div><strong>Période:</strong> {{ formatDateRange(selectedRoomStay.start_date, selectedRoomStay.end_date) }}</div>
        </div>

        <template v-if="selectedRoomStay.action === 'check_in'">
          <div class="stay-modal-head">
            <div>
              <h3>Personnes hébergées</h3>
              <p>Ajoutez les occupants de cette chambre. Le type et le numéro de pièce sont obligatoires pour chaque personne.</p>
            </div>
            <button type="button" class="btn btn-outline btn-sm" @click="addStayGuest">
              <i class="fas fa-plus"></i>
              Ajouter une personne
            </button>
          </div>

          <div class="stay-guests-list">
            <div v-for="(guest, index) in stayForm.guests" :key="`stay-guest-${index}`" class="stay-guest-card">
              <div class="stay-guest-card-head">
                <strong>Personne {{ index + 1 }}</strong>
                <button v-if="stayForm.guests.length > 1" type="button" class="btn-icon delete" @click="removeStayGuest(index)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Nom complet *</label>
                  <input v-model="guest.full_name" type="text" class="form-input" placeholder="Nom complet" />
                </div>
                <div class="form-group">
                  <label class="form-label">Type de pièce *</label>
                  <select v-model="guest.id_type" class="form-select">
                    <option v-for="option in guestIdTypeOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
                  </select>
                </div>
                <div class="form-group full">
                  <label class="form-label">Numéro de pièce *</label>
                  <input v-model="guest.id_number" type="text" class="form-input" placeholder="Numéro de pièce" />
                </div>
              </div>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="stay-modal-checkout">
            <h3>Confirmer le départ</h3>
            <p>Cette action clôture le séjour pour la chambre sélectionnée et la place en nettoyage.</p>
            <div class="stay-modal-guest-line">
              <strong>Occupants:</strong>
              <span>{{ roomStayGuestNames(selectedRoomStay) || 'Aucune personne enregistrée' }}</span>
            </div>
          </div>
        </template>
      </div>
      <template #footer>
        <button class="btn btn-outline" @click="closeStayModal">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingStayAction || isStayActionLoading(selectedRoomStay, selectedRoomStay?.action) }" :disabled="savingStayAction || stayActionLoadingId" @click="manageStay(selectedRoomStay, selectedRoomStay.action)">
          {{ selectedRoomStay?.action === 'check_out' ? 'Valider le check-out' : 'Valider le check-in' }}
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showViewModal" title="Détails de la chambre" width="620px">
      <div v-if="selectedRoom" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ String(selectedRoom.name || 'CH').trim().slice(0, 2).toUpperCase() }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">Chambre</div>
            <h3>{{ selectedRoom.name }}</h3>
            <p>{{ selectedRoom.room_number }} • {{ roomTypeLabel(selectedRoom.room_type) }} • Capacité {{ selectedRoom.capacity }} personnes</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', 'badge-info']">{{ roomStatusLabel(selectedRoom.status) }}</span>
            <span class="badge badge-info">{{ selectedRoom.capacity }} pers.</span>
            <span class="badge badge-success">{{ formatMoney(selectedRoom.price_per_night) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Chambre</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Nom</span><span class="entity-view-value">{{ selectedRoom.name }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Numéro</span><span class="entity-view-value">{{ selectedRoom.room_number }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Type</span><span class="entity-view-value">{{ roomTypeLabel(selectedRoom.room_type) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Capacité</span><span class="entity-view-value">{{ selectedRoom.capacity }} pers.</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ roomStatusLabel(selectedRoom.status) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Prix / nuit</span><span class="entity-view-value">{{ formatMoney(selectedRoom.price_per_night) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Services</span><span class="entity-view-value">{{ selectedRoom.additional_services?.length || 0 }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Suivi administratif</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedRoom.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedRoom.updated_by_name || selectedRoom.created_by_name || '-' }}</span></div>
            </div>
          </section>

          <section class="entity-view-card entity-view-card-full">
            <div class="entity-view-card-title">Services additionnels</div>
            <div v-if="!selectedRoom.additional_services?.length" class="entity-view-empty">Aucun service additionnel</div>
            <div v-else class="services-preview">
              <div v-for="(service, index) in selectedRoom.additional_services" :key="`${service.name}-${index}`" class="service-preview-item">
                <div class="service-preview-title">
                  <strong>{{ service.name }}</strong>
                  <span v-if="!service.has_subservices">{{ formatMoney(service.price) }}</span>
                </div>
                <div v-if="service.has_subservices" class="service-preview-subs">
                  <div v-for="(subservice, subIndex) in service.subservices || []" :key="`${service.name}-${subIndex}`" class="service-preview-sub">
                    <span>{{ subservice.name }}</span>
                    <strong>{{ formatMoney(subservice.price) }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer <strong>{{ selectedRoom?.name }} ({{ selectedRoom?.room_number }})</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button v-if="canManageFacilitiesCatalog" class="btn btn-danger" :class="{ 'is-loading': deletingRoom }" :disabled="deletingRoom" @click="deleteRoom">
          Supprimer
        </button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useTableSort } from '~/composables/useTableSort'
import { useDateFormat } from '~/composables/useDateFormat'
import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { canManageFacilities, getRoleKey, getStoredUser } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })
const { formatMoney, moneyInputModel, parseMoney, formatNumberSpaces } = useMoney()
const { formatDateRange, formatDateTime } = useDateFormat()
const { escapeHtml } = useDocumentBranding()
const { buildPdfDocumentHtml, openPrintPreviewHtml } = useAdminExportDocuments()

const rooms = ref([])
const bookings = ref([])
const loadingRooms = ref(false)
const loadingBookings = ref(false)
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const showDeskBookingModal = ref(false)
const showDeskPaymentModal = ref(false)
const showStayModal = ref(false)
const currentUser = ref({})
const isEditing = ref(false)
const selectedRoom = ref(null)
const selectedDeskBooking = ref(null)
const selectedRoomStay = ref(null)
const openActionsId = ref(null)
const isMobile = ref(false)
const frontdeskSearch = ref('')
const frontdeskPaymentFilter = ref('all')
const frontdeskActivityWindow = ref('24h')
const savingRoom = ref(false)
const deletingRoom = ref(false)
const savingDeskPayment = ref(false)
const stayActionLoadingId = ref(null)
const stayActionType = ref('')
const savingStayAction = ref(false)
const activeDeskTab = ref('checkin')
const canManageFacilitiesCatalog = computed(() => canManageFacilities(currentUser.value))
const showRoomStats = computed(() => getRoleKey(currentUser.value) !== 'receptionniste')

const roomTypeOptions = [
  { value: 'single', label: 'Simple' },
  { value: 'double', label: 'Double' },
  { value: 'twin', label: 'Twin' },
  { value: 'suite', label: 'Suite' },
  { value: 'family', label: 'Familiale' },
]
const roomStatusOptions = [
  { value: 'available', label: 'Disponible' },
  { value: 'reserved', label: 'Réservée' },
  { value: 'occupied', label: 'Occupée' },
  { value: 'cleaning', label: 'Nettoyage' },
  { value: 'maintenance', label: 'Maintenance' },
]
const guestIdTypeOptions = [
  { value: 'passport', label: 'Passeport' },
  { value: 'id_card', label: "Carte d'identité" },
  { value: 'driving_license', label: 'Permis de conduire' },
  { value: 'other', label: 'Autre pièce' },
]

const form = ref({
  id: null,
  name: '',
  room_number: '',
  room_type: 'double',
  status: 'available',
  capacity: 2,
  price_per_night: 0,
  additional_services: [],
})
const pricePerNightInput = moneyInputModel(form, 'price_per_night')
const deskPaymentForm = ref({
  booking: null,
  date: new Date().toISOString().split('T')[0],
  reference: '',
  amount: 0,
  method: 'Virement',
  kind: 'full',
  status: 'paid',
})
const stayForm = ref({
  guests: [
    { full_name: '', id_type: 'passport', id_number: '' },
  ],
})
const deskPaymentAmountInput = moneyInputModel(deskPaymentForm, 'amount')
const defaultRoomServiceOptions = ['Petit-déjeuner', 'Minibar', 'Service en chambre', 'Parking', 'WiFi premium', 'Autre']
const {
  sortedItems: sortedRooms,
  toggleSort: toggleRoomSort,
  isSortActive: isRoomSortActive,
  sortIconClass: roomSortIconClass,
} = useTableSort(computed(() => rooms.value), {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    capacity: room => Number(room?.capacity || 0),
    price_per_night: room => Number(room?.price_per_night || 0),
    room_number: room => room?.room_number || '',
    status: room => room?.status || '',
    services: room => (Array.isArray(room?.additional_services) && room.additional_services.length ? 1 : 0),
  },
})
const {
  paginatedItems: paginatedRooms,
  totalItems: roomsTotalItems,
  startIndex: roomsStartIndex,
  endIndex: roomsEndIndex,
  canPrev: roomsCanPrev,
  canNext: roomsCanNext,
  prevPage: roomsPrevPage,
  nextPage: roomsNextPage,
} = usePagination(sortedRooms, 50)

const totalCapacity = computed(() => rooms.value.reduce((sum, room) => sum + Number(room.capacity || 0), 0))
const averageNightlyPrice = computed(() => {
  if (!rooms.value.length) return 0
  const total = rooms.value.reduce((sum, room) => sum + Number(room.price_per_night || 0), 0)
  return Math.round(total / rooms.value.length)
})
const highestNightlyPrice = computed(() => {
  if (!rooms.value.length) return 0
  return Math.max(...rooms.value.map(room => Number(room.price_per_night || 0)))
})
const roomStatusCounts = computed(() => ({
  available: rooms.value.filter(room => (room?.status || 'available') === 'available').length,
  reserved: rooms.value.filter(room => room?.status === 'reserved').length,
  occupied: rooms.value.filter(room => room?.status === 'occupied').length,
  cleaning: rooms.value.filter(room => room?.status === 'cleaning').length,
  maintenance: rooms.value.filter(room => room?.status === 'maintenance').length,
}))
const roomBookings = computed(() => bookings.value.filter((booking) => booking?.booking_type === 'room' && booking?.status !== 'cancelled'))
const normalizedRoomStays = (booking) => Array.isArray(booking?.room_stays) ? booking.room_stays : []
const firstStayGuest = (roomStay) => Array.isArray(roomStay?.guests) && roomStay.guests.length ? roomStay.guests[0] : null
const roomStayGuestLabel = (roomStay) => {
  const firstGuest = firstStayGuest(roomStay)
  return firstGuest?.full_name || roomStay?.organization_contact_name || roomStay?.customer_name || '-'
}
const roomStayRepresentativeId = (roomStay) => {
  const firstGuest = firstStayGuest(roomStay)
  return {
    guest_id_type: firstGuest?.id_type || '',
    guest_id_number: firstGuest?.id_number || '',
  }
}
const roomStayEntries = computed(() => roomBookings.value.flatMap((booking) => {
  return normalizedRoomStays(booking).map((stay) => ({
    id: `${booking.id}-${stay.room_id}`,
    booking_id: booking.id,
    booking,
    code: booking.code,
    booking_status: booking.status,
    customer_name: booking.customer_name,
    customer_email: booking.customer_email,
    customer_phone: booking.customer_phone,
    customer_kind: booking.customer_kind,
    organization_name: booking.organization_name,
    organization_contact_name: booking.organization_contact_name,
    room_id: stay.room_id,
    room_display: stay.room_display || booking.room_display || '-',
    room_number: stay.room_number || '',
    room_name: stay.room_name || '',
    room_type: stay.room_type || '',
    room_capacity: Number(stay.room_capacity || 0),
    room_status: stay.room_status || booking.room_status || '',
    stay_status: stay.stay_status || '',
    start_date: booking.start_date,
    end_date: booking.end_date,
    total_price: booking.total_price,
    paid_amount: booking.paid_amount,
    remaining_amount: booking.remaining_amount,
    checked_in_at: stay.checked_in_at,
    checked_out_at: stay.checked_out_at,
    guests: Array.isArray(stay.guests) ? stay.guests : [],
    guest_count: Number(stay.guest_count || 0),
    can_check_in: Boolean(stay.can_check_in && booking.status === 'paid'),
    can_check_out: Boolean(stay.can_check_out),
  }))
}))
const pendingArrivalBookings = computed(() => roomStayEntries.value
  .filter((roomStay) => roomStay.booking_status === 'paid' && !roomStay.checked_in_at)
  .slice()
  .sort((a, b) => new Date(a?.start_date || 0) - new Date(b?.start_date || 0)))
const inHouseBookings = computed(() => roomStayEntries.value
  .filter((roomStay) => roomStay.checked_in_at && !roomStay.checked_out_at)
  .slice()
  .sort((a, b) => new Date(a?.checked_in_at || 0) - new Date(b?.checked_in_at || 0)))
const recentCheckIns = computed(() => roomStayEntries.value
  .filter((roomStay) => roomStay.checked_in_at)
  .slice()
  .sort((a, b) => new Date(b?.checked_in_at || 0) - new Date(a?.checked_in_at || 0)))
const recentCheckOuts = computed(() => roomStayEntries.value
  .filter((roomStay) => roomStay.checked_out_at)
  .slice()
  .sort((a, b) => new Date(b?.checked_out_at || 0) - new Date(a?.checked_out_at || 0)))
const cleaningRoomsList = computed(() => rooms.value.filter(room => room?.status === 'cleaning'))
const latestCompletedStayByRoomId = computed(() => {
  const map = new Map()
  for (const roomStay of roomStayEntries.value) {
    if (!roomStay?.checked_out_at) continue
    const roomId = Number(roomStay.room_id)
    if (!roomId) continue
    const existing = map.get(roomId)
    const currentTime = new Date(roomStay.checked_out_at).getTime()
      const existingTime = existing?.checked_out_at ? new Date(existing.checked_out_at).getTime() : 0
    if (!existing || currentTime > existingTime) {
      map.set(roomId, roomStay)
    }
  }
  return map
})
const deskLoading = computed(() => loadingRooms.value || loadingBookings.value)
const frontdeskSearchText = computed(() => String(frontdeskSearch.value || '').trim().toLowerCase())

const matchesFrontdeskPaymentFilter = (booking) => {
  const remaining = Number(booking?.remaining_amount || 0)
  if (frontdeskPaymentFilter.value === 'settled') return remaining <= 0
  if (frontdeskPaymentFilter.value === 'balance_due') return remaining > 0
  return true
}

const matchesFrontdeskBookingSearch = (booking) => {
  const q = frontdeskSearchText.value
  if (!q) return true
  return [
    roomStayGuestLabel(booking),
    booking?.customer_name,
    booking?.room_display,
    booking?.code,
    roomStayRepresentativeId(booking)?.guest_id_number,
    booking?.customer_phone,
  ].some(value => String(value || '').toLowerCase().includes(q))
}

const matchesFrontdeskRoomSearch = (room) => {
  const q = frontdeskSearchText.value
  if (!q) return true
  const nextBooking = nextReservationForRoom(room?.id)
  const lastBooking = lastCompletedStayForRoom(room?.id)
  return [
    room?.name,
    room?.room_number,
    roomTypeLabel(room?.room_type),
    roomStayGuestLabel(nextBooking),
    nextBooking?.customer_name,
    roomStayGuestLabel(lastBooking),
    lastBooking?.customer_name,
  ].some(value => String(value || '').toLowerCase().includes(q))
}

const matchesActivityWindow = (value) => {
  if (frontdeskActivityWindow.value === 'all') return true
  const timestamp = new Date(value || '').getTime()
  if (!timestamp) return false
  const now = Date.now()
  const hoursMap = {
    '24h': 24,
    '72h': 72,
    '7d': 24 * 7,
  }
  const limitHours = hoursMap[frontdeskActivityWindow.value] || 24
  return now - timestamp <= limitHours * 60 * 60 * 1000
}

const filteredPendingArrivalBookings = computed(() => pendingArrivalBookings.value.filter((booking) => {
  return matchesFrontdeskBookingSearch(booking) && matchesFrontdeskPaymentFilter(booking)
}))

const filteredInHouseBookings = computed(() => inHouseBookings.value.filter((booking) => {
  return matchesFrontdeskBookingSearch(booking) && matchesFrontdeskPaymentFilter(booking)
}))

const filteredCleaningRoomsList = computed(() => cleaningRoomsList.value.filter((room) => {
  return matchesFrontdeskRoomSearch(room)
}))

const filteredRecentCheckIns = computed(() => recentCheckIns.value.filter((booking) => {
  return matchesFrontdeskBookingSearch(booking) && matchesFrontdeskPaymentFilter(booking) && matchesActivityWindow(booking?.checked_in_at)
}))

const filteredRecentCheckOuts = computed(() => recentCheckOuts.value.filter((booking) => {
  return matchesFrontdeskBookingSearch(booking) && matchesFrontdeskPaymentFilter(booking) && matchesActivityWindow(booking?.checked_out_at)
}))

const {
  paginatedItems: paginatedPendingArrivalBookings,
  totalItems: pendingArrivalTotalItems,
  startIndex: pendingArrivalStartIndex,
  endIndex: pendingArrivalEndIndex,
  canPrev: pendingArrivalCanPrev,
  canNext: pendingArrivalCanNext,
  prevPage: pendingArrivalPrevPage,
  nextPage: pendingArrivalNextPage,
} = usePagination(filteredPendingArrivalBookings, 6)

const {
  paginatedItems: paginatedInHouseBookings,
  totalItems: inHouseTotalItems,
  startIndex: inHouseStartIndex,
  endIndex: inHouseEndIndex,
  canPrev: inHouseCanPrev,
  canNext: inHouseCanNext,
  prevPage: inHousePrevPage,
  nextPage: inHouseNextPage,
} = usePagination(filteredInHouseBookings, 6)

const {
  paginatedItems: paginatedCleaningRooms,
  totalItems: cleaningTotalItems,
  startIndex: cleaningStartIndex,
  endIndex: cleaningEndIndex,
  canPrev: cleaningCanPrev,
  canNext: cleaningCanNext,
  prevPage: cleaningPrevPage,
  nextPage: cleaningNextPage,
} = usePagination(filteredCleaningRoomsList, 6)

const {
  paginatedItems: paginatedRecentCheckIns,
  totalItems: recentCheckInsTotalItems,
  startIndex: recentCheckInsStartIndex,
  endIndex: recentCheckInsEndIndex,
  canPrev: recentCheckInsCanPrev,
  canNext: recentCheckInsCanNext,
  prevPage: recentCheckInsPrevPage,
  nextPage: recentCheckInsNextPage,
} = usePagination(filteredRecentCheckIns, 6)

const {
  paginatedItems: paginatedRecentCheckOuts,
  totalItems: recentCheckOutsTotalItems,
  startIndex: recentCheckOutsStartIndex,
  endIndex: recentCheckOutsEndIndex,
  canPrev: recentCheckOutsCanPrev,
  canNext: recentCheckOutsCanNext,
  prevPage: recentCheckOutsPrevPage,
  nextPage: recentCheckOutsNextPage,
} = usePagination(filteredRecentCheckOuts, 6)

const displayTotalRooms = ref(0)
const displayTotalCapacity = ref(0)
const displayAverageNightlyPrice = ref(0)
const displayHighestNightlyPrice = ref(0)

const rafMap = new Map()
const animateCounter = (outRef, toValue) => {
  if (typeof requestAnimationFrame === 'undefined' || typeof cancelAnimationFrame === 'undefined') {
    outRef.value = Math.round(Number(toValue || 0))
    return
  }

  const from = Number(outRef.value || 0)
  const to = Number(toValue || 0)
  const duration = 750
  const start = (typeof performance !== 'undefined' && typeof performance.now === 'function') ? performance.now() : Date.now()
  const existing = rafMap.get(outRef)
  if (existing) cancelAnimationFrame(existing)

  const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3)
  const step = (now) => {
    const p = Math.min(1, (now - start) / duration)
    const eased = easeOutCubic(p)
    const current = from + (to - from) * eased
    outRef.value = Math.round(current)
    if (p < 1) rafMap.set(outRef, requestAnimationFrame(step))
  }

  rafMap.set(outRef, requestAnimationFrame(step))
}

watch(() => rooms.value.length, (v) => animateCounter(displayTotalRooms, v), { immediate: true })
watch(totalCapacity, (v) => animateCounter(displayTotalCapacity, v), { immediate: true })
watch(averageNightlyPrice, (v) => animateCounter(displayAverageNightlyPrice, v), { immediate: true })
watch(highestNightlyPrice, (v) => animateCounter(displayHighestNightlyPrice, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const fetchRooms = async () => {
  loadingRooms.value = true
  try {
    const response = await api.get('rooms/')
    rooms.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    notify('Erreur lors du chargement des chambres', 'danger')
  } finally {
    loadingRooms.value = false
  }
}

const fetchBookings = async () => {
  loadingBookings.value = true
  try {
    const response = await api.get('bookings/')
    bookings.value = Array.isArray(response.data) ? response.data : []
  } catch {
    notify('Erreur lors du chargement des séjours', 'danger')
  } finally {
    loadingBookings.value = false
  }
}

onMounted(() => {
  currentUser.value = getStoredUser()
  fetchRooms()
  fetchBookings()
  if (process.client) {
    const update = () => { isMobile.value = window.innerWidth <= 992 }
    update()
    window.addEventListener('resize', update)
    onBeforeUnmount(() => window.removeEventListener('resize', update))

    const onDocClick = () => { openActionsId.value = null }
    document.addEventListener('click', onDocClick)
    onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
  }
})

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const roomHasAdditionalServices = (room) => Array.isArray(room?.additional_services) && room.additional_services.length > 0
const roomTypeLabel = (roomType) => {
  const value = String(roomType || '')
  const labels = {
    single: 'Simple',
    double: 'Double',
    twin: 'Twin',
    suite: 'Suite',
    family: 'Familiale',
    Single: 'Simple',
    Double: 'Double',
    Twin: 'Twin',
    Suite: 'Suite',
    Family: 'Familiale',
  }
  return labels[value] || value
}
const roomStatusLabel = (status) => {
  const value = String(status || 'available')
  return roomStatusOptions.find(item => item.value === value)?.label || value
}

const getBookingDisplayId = (booking) => booking?.code || `Reservation #${booking?.id || '-'}`

const getStatusTranslation = (status) => ({
  pending: 'En attente',
  confirmed: 'Confirmée',
  completed: 'Terminée',
  cancelled: 'Annulée',
  checked_in: 'Check-in effectué',
  checked_out: 'Check-out effectué',
}[status] || status || '-')

const guestIdSummary = (booking) => {
  const type = String(booking?.guest_id_type || booking?.booking_guest_id_type || '').trim()
  const number = String(booking?.guest_id_number || booking?.booking_guest_id_number || '').trim()
  const typeLabels = {
    passport: 'Passeport',
    id_card: "Carte d'identité",
    driving_license: 'Permis de conduire',
    other: 'Autre pièce',
  }
  if (!type && !number) return 'Non renseignée'
  return [typeLabels[type] || type || 'Pièce', number || '-'].join(' • ')
}
const createEmptyStayGuest = () => ({ full_name: '', id_type: 'passport', id_number: '' })
const resetStayForm = (roomStay = null) => {
  const existingGuests = Array.isArray(roomStay?.guests) ? roomStay.guests : []
  stayForm.value = {
    guests: existingGuests.length
      ? existingGuests.map(guest => ({
        full_name: String(guest?.full_name || '').trim(),
        id_type: String(guest?.id_type || 'passport').trim() || 'passport',
        id_number: String(guest?.id_number || '').trim(),
      }))
      : [createEmptyStayGuest()],
  }
}
const addStayGuest = () => {
  stayForm.value.guests.push(createEmptyStayGuest())
}
const removeStayGuest = (index) => {
  if (stayForm.value.guests.length === 1) return
  stayForm.value.guests.splice(index, 1)
}
const openStayModal = (roomStay, action = 'check_in') => {
  if (!roomStay?.booking_id || !roomStay?.room_id) return
  selectedRoomStay.value = {
    ...roomStay,
    action,
  }
  resetStayForm(roomStay)
  showStayModal.value = true
}
const closeStayModal = () => {
  showStayModal.value = false
  selectedRoomStay.value = null
  resetStayForm()
}
const roomStayLoadingKey = (roomStay, action) => `${roomStay?.booking_id || roomStay?.id}-${roomStay?.room_id || ''}-${action}`
const isStayActionLoading = (roomStay, action) => stayActionLoadingId.value === roomStayLoadingKey(roomStay, action)
const roomStayGuestNames = (roomStay) => {
  const guests = Array.isArray(roomStay?.guests) ? roomStay.guests : []
  return guests.map(guest => String(guest?.full_name || '').trim()).filter(Boolean).join(', ')
}

const resetFrontdeskFilters = () => {
  frontdeskSearch.value = ''
  frontdeskPaymentFilter.value = 'all'
  frontdeskActivityWindow.value = '24h'
}

const formatDeskDateTime = (value) => value ? formatDateTime(value) : '-'
const nextReservationForRoom = (roomId) => pendingArrivalBookings.value.find((booking) => Number(booking?.room_id) === Number(roomId))
const lastCompletedStayForRoom = (roomId) => latestCompletedStayByRoomId.value.get(Number(roomId)) || null

const syncSelectedDeskBooking = () => {
  if (!selectedDeskBooking.value?.id) return
  const fresh = bookings.value.find(item => Number(item?.id) === Number(selectedDeskBooking.value.id))
  if (fresh) selectedDeskBooking.value = fresh
}

watch(bookings, () => {
  syncSelectedDeskBooking()
}, { deep: true })

const resetDeskPaymentForm = (booking = null) => {
  const remaining = Number(booking?.remaining_amount || 0)
  deskPaymentForm.value = {
    booking: booking?.id || null,
    date: new Date().toISOString().split('T')[0],
    reference: '',
    amount: remaining > 0 ? remaining : 0,
    method: 'Virement',
    kind: 'full',
    status: 'paid',
  }
}

const syncDeskPaymentKindWithAmount = () => {
  const booking = selectedDeskBooking.value
  if (!booking) return
  const remaining = Number(booking?.remaining_amount || 0)
  const amount = Number(deskPaymentForm.value.amount || 0)
  if (remaining <= 0) {
    deskPaymentForm.value.kind = 'full'
    return
  }
  deskPaymentForm.value.kind = amount === remaining ? 'full' : 'advance'
}

const onDeskPaymentKindChange = () => {
  const booking = selectedDeskBooking.value
  if (!booking) return
  if (deskPaymentForm.value.kind === 'full') {
    deskPaymentForm.value.amount = Number(booking?.remaining_amount || 0)
  }
  syncDeskPaymentKindWithAmount()
}

watch(() => deskPaymentForm.value.amount, () => {
  syncDeskPaymentKindWithAmount()
})

const openPaymentForBooking = (booking) => {
  const bookingRef = booking?.booking || booking
  if (!bookingRef?.id) return
  selectedDeskBooking.value = bookingRef
  resetDeskPaymentForm(bookingRef)
  showDeskBookingModal.value = false
  showDeskPaymentModal.value = true
}

const openBookingDetails = (booking) => {
  const bookingRef = booking?.booking || booking
  if (!bookingRef?.id) return
  selectedDeskBooking.value = bookingRef
  showDeskBookingModal.value = true
}

const getDeskPaymentDisplayId = (payment) => payment?.code || (payment?.id ? `Paiement #${payment.id}` : 'Paiement')
const deskPaymentBookingItemLabel = (payment) => payment?.booking_type === 'room'
  ? (payment?.booking_room_display || '-')
  : (payment?.booking_hall_name || '-')

const buildDeskPaymentPrintHtml = (payment) => {
  const paymentCode = getDeskPaymentDisplayId(payment)
  const reservationCode = String(payment?.booking_code || '').trim() || getBookingDisplayId(selectedDeskBooking.value)
  const paymentTypeLabel = payment?.kind === 'full' ? 'Paiement total' : 'Avance'
  const reservationTypeLabel = payment?.booking_type === 'room' ? 'Chambre' : 'Salle'
  const periodLabel = formatDateRange(payment?.booking_start_date, payment?.booking_end_date)
  const detailRows = [
    ['Paiement', paymentCode],
    ['Réservation', reservationCode],
    ['Date', payment?.date || '-'],
    ['Client', payment?.booking_customer_name || '-'],
    ['Email client', payment?.booking_customer_email || '-'],
    ['Référence', payment?.reference || '-'],
    ['Méthode', payment?.method || '-'],
    ['Type', paymentTypeLabel],
    ['Type de réservation', reservationTypeLabel],
    [reservationTypeLabel, deskPaymentBookingItemLabel(payment) || '-'],
    ['Période', periodLabel || '-'],
    ['Montant payé', formatMoney(payment?.amount)],
    ['Total réservation', formatMoney(payment?.booking_total_price)],
    ['Reste à payer', formatMoney(payment?.booking_remaining_amount)],
  ]

  return buildPdfDocumentHtml({
    title: 'Facture de paiement',
    documentTitle: `Facture ${paymentCode}`,
    subtitle: 'Facture generee automatiquement apres enregistrement du paiement.',
    typeLabel: 'Facture à imprimer',
    tableTitle: 'Détails du paiement',
    tableTitles: ['Détails du paiement'],
    periodLabel,
    contentHtml: `
      <div class="summary-cards">
        <div class="summary-card">
          <div>
            <div class="label">Code paiement</div>
            <div class="value">${escapeHtml(paymentCode)}</div>
          </div>
        </div>
        <div class="summary-card">
          <div>
            <div class="label">Réservation</div>
            <div class="value">${escapeHtml(reservationCode)}</div>
          </div>
        </div>
        <div class="summary-card">
          <div>
            <div class="label">Montant payé</div>
            <div class="value">${escapeHtml(formatMoney(payment?.amount))}</div>
          </div>
        </div>
        <div class="summary-card">
          <div>
            <div class="label">Reste à payer</div>
            <div class="value">${escapeHtml(formatMoney(payment?.booking_remaining_amount))}</div>
          </div>
        </div>
      </div>
      <div class="section-card">
        <div class="section-header"><h2>Détails du paiement</h2></div>
        <table>
          <thead>
            <tr>
              <th>Information</th>
              <th>Valeur</th>
            </tr>
          </thead>
          <tbody>
            ${detailRows.map(([label, value]) => `
              <tr>
                <td>${escapeHtml(label)}</td>
                <td>${escapeHtml(value)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `,
  })
}

const printDeskPaymentInvoice = (payment) => {
  const html = buildDeskPaymentPrintHtml(payment)
  const ok = openPrintPreviewHtml({
    html,
    title: `Facture ${getDeskPaymentDisplayId(payment)}`,
  })
  if (!ok) {
    notify('Impossible d’ouvrir l’aperçu d’impression de la facture', 'warning')
  }
}

const setRoomStatus = async (room, status) => {
  if (!canManageFacilitiesCatalog.value) {
    notify("Vous n'avez pas l'autorisation de modifier le statut d'une chambre", 'warning')
    return
  }
  if (!room?.id || !status) return
  openActionsId.value = null
  try {
    await api.patch(`rooms/${room.id}/`, { status })
    notify('Statut de la chambre mis à jour', 'success')
    await Promise.all([fetchRooms(), fetchBookings()])
  } catch {
    notify('Impossible de mettre à jour le statut', 'danger')
  }
}

const manageStay = async (roomStay, action) => {
  if (!roomStay?.booking_id || !roomStay?.room_id || stayActionLoadingId.value) return
  savingStayAction.value = true
  stayActionLoadingId.value = roomStayLoadingKey(roomStay, action)
  stayActionType.value = action
  try {
    const payload = {
      room_id: roomStay.room_id,
    }
    if (action === 'check_in') {
      payload.guests = (stayForm.value.guests || []).map(guest => ({
        full_name: String(guest?.full_name || '').trim(),
        id_type: String(guest?.id_type || '').trim(),
        id_number: String(guest?.id_number || '').trim(),
      }))
    }
    await api.post(`bookings/${roomStay.booking_id}/${action === 'check_in' ? 'check-in-room' : 'check-out-room'}/`, payload)
    notify(action === 'check_in' ? 'Check-in enregistré' : 'Check-out enregistré', 'success')
    await Promise.all([fetchRooms(), fetchBookings()])
    closeStayModal()
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.room_id || data.detail || 'Impossible de mettre à jour le séjour', 'danger')
  } finally {
    savingStayAction.value = false
    stayActionLoadingId.value = null
    stayActionType.value = ''
  }
}

const saveDeskPayment = async () => {
  const booking = selectedDeskBooking.value
  if (!booking?.id || savingDeskPayment.value) return
  const remaining = Number(booking?.remaining_amount || 0)
  const amount = Number(deskPaymentForm.value.amount || 0)

  if (amount <= 0) {
    notify('Montant invalide', 'warning')
    return
  }
  if (amount > remaining) {
    notify('Le montant dépasse le reste à payer', 'warning')
    return
  }

  savingDeskPayment.value = true
  try {
    const payload = {
      booking: booking.id,
      date: deskPaymentForm.value.date,
      reference: String(deskPaymentForm.value.reference || '').trim(),
      amount,
      method: deskPaymentForm.value.method,
      kind: deskPaymentForm.value.kind,
      status: deskPaymentForm.value.status,
    }
    const { data } = await api.post('payments/', payload)
    notify('Paiement enregistré avec succès', 'success')
    showDeskPaymentModal.value = false
    await Promise.all([fetchRooms(), fetchBookings()])
    syncSelectedDeskBooking()
    await nextTick()
    const refreshedBooking = bookings.value.find(item => Number(item?.id) === Number(booking.id)) || booking
    printDeskPaymentInvoice({
      ...data,
      amount,
      date: payload.date,
      reference: payload.reference,
      method: payload.method,
      kind: payload.kind,
      status: payload.status,
      booking: booking.id,
      booking_code: booking.code || getBookingDisplayId(booking),
      booking_customer_name: booking.customer_name,
      booking_customer_email: booking.customer_email,
      booking_type: booking.booking_type,
      booking_room_display: booking.room_display,
      booking_room_count: booking.room_count,
      booking_hall_name: booking.hall_name,
      booking_start_date: booking.start_date,
      booking_end_date: booking.end_date,
      booking_total_price: booking.total_price,
      booking_remaining_amount: Number(refreshedBooking?.remaining_amount ?? Math.max(0, remaining - amount)),
      booking_guest_full_name: booking.guest_full_name,
      booking_guest_id_type: booking.guest_id_type,
      booking_guest_id_number: booking.guest_id_number,
      booking_room_status: refreshedBooking?.room_status || booking.room_status,
      booking_checked_in_at: refreshedBooking?.checked_in_at || booking.checked_in_at,
      booking_checked_out_at: refreshedBooking?.checked_out_at || booking.checked_out_at,
    })
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.room_action || data.amount || data.booking || data.detail || 'Erreur lors de l\'enregistrement du paiement', 'danger')
  } finally {
    savingDeskPayment.value = false
  }
}

const createSubservice = (values = {}) => ({
  id: `sub-${Math.random().toString(36).slice(2, 10)}`,
  name: values.name || '',
  price: Number(values.price || 0),
})

const createService = (values = {}) => ({
  id: `svc-${Math.random().toString(36).slice(2, 10)}`,
  name: values.name || defaultRoomServiceOptions[0],
  price: Number(values.price || 0),
  has_subservices: !!values.has_subservices,
  subservices: Array.isArray(values.subservices) ? values.subservices.map(createSubservice) : [],
})

const buildServicePriceModel = (service) => computed({
  get: () => (service.price ? formatNumberSpaces(service.price) : ''),
  set: (value) => {
    service.price = parseMoney(value)
  },
})

const buildSubservicePriceModel = (subservice) => computed({
  get: () => (subservice.price ? formatNumberSpaces(subservice.price) : ''),
  set: (value) => {
    subservice.price = parseMoney(value)
  },
})

const addService = () => {
  form.value.additional_services.push(createService())
}

const removeService = (index) => {
  form.value.additional_services.splice(index, 1)
}

const addSubservice = (service) => {
  service.subservices.push(createSubservice())
}

const removeSubservice = (service, index) => {
  service.subservices.splice(index, 1)
}

const onServiceHasSubservicesChange = (service) => {
  if (service.has_subservices) {
    service.price = 0
    if (!service.subservices.length) {
      service.subservices.push(createSubservice())
    }
    return
  }
  service.subservices = []
}

const normalizeAdditionalServices = (services) => {
  if (!Array.isArray(services)) return []
  return services
    .map((service) => {
      const name = String(service?.name || '').trim()
      if (!name) return null
      const hasSubservices = !!service?.has_subservices
      if (hasSubservices) {
        const subservices = Array.isArray(service?.subservices)
          ? service.subservices
            .map((subservice) => {
              const subName = String(subservice?.name || '').trim()
              if (!subName) return null
              return {
                name: subName,
                price: parseMoney(subservice?.price || 0),
              }
            })
            .filter(Boolean)
          : []
        return {
          name,
          price: 0,
          has_subservices: true,
          subservices,
        }
      }
      return {
        name,
        price: parseMoney(service?.price || 0),
        has_subservices: false,
        subservices: [],
      }
    })
    .filter(Boolean)
}

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    room_number: '',
    room_type: 'double',
    status: 'available',
    capacity: 2,
    price_per_night: 0,
    additional_services: [],
  }
}

const openAddModal = () => {
  if (!canManageFacilitiesCatalog.value) {
    notify("Vous n'avez pas l'autorisation d'ajouter une chambre", 'warning')
    return
  }
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewRoom = (room) => {
  openActionsId.value = null
  selectedRoom.value = room
  showViewModal.value = true
}

const editRoom = (room) => {
  if (!canManageFacilitiesCatalog.value) {
    notify("Vous n'avez pas l'autorisation de modifier une chambre", 'warning')
    return
  }
  openActionsId.value = null
  isEditing.value = true
  form.value = {
    ...room,
    capacity: Number(room.capacity),
    price_per_night: Number(room.price_per_night),
    additional_services: normalizeAdditionalServices(room.additional_services).map(createService),
  }
  showFormModal.value = true
}

const confirmDelete = (room) => {
  if (!canManageFacilitiesCatalog.value) {
    notify("Vous n'avez pas l'autorisation de supprimer une chambre", 'warning')
    return
  }
  openActionsId.value = null
  selectedRoom.value = room
  showDeleteModal.value = true
}

const saveRoom = async () => {
  if (!canManageFacilitiesCatalog.value) {
    notify("Vous n'avez pas l'autorisation d'enregistrer une chambre", 'warning')
    return
  }
  if (savingRoom.value) return
  savingRoom.value = true
  try {
    const payload = {
      name: String(form.value.name || '').trim(),
      room_number: String(form.value.room_number || '').trim(),
      room_type: form.value.room_type,
      status: form.value.status || 'available',
      capacity: Number(form.value.capacity || 0),
      price_per_night: Number(form.value.price_per_night || 0),
      additional_services: normalizeAdditionalServices(form.value.additional_services),
    }
    if (isEditing.value) {
      await api.put(`rooms/${form.value.id}/`, payload)
      notify('Chambre mise à jour avec succès', 'success')
    } else {
      await api.post('rooms/', payload)
      notify('Nouvelle chambre ajoutée avec succès', 'success')
    }
    showFormModal.value = false
    await Promise.all([fetchRooms(), fetchBookings()])
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.additional_services || data.detail || 'Erreur lors de l\'enregistrement', 'danger')
  } finally {
    savingRoom.value = false
  }
}

const deleteRoom = async () => {
  if (!canManageFacilitiesCatalog.value) {
    notify("Vous n'avez pas l'autorisation de supprimer une chambre", 'warning')
    return
  }
  if (deletingRoom.value || !selectedRoom.value?.id) return
  deletingRoom.value = true
  try {
    await api.delete(`rooms/${selectedRoom.value.id}/`)
    notify('Chambre supprimée', 'danger')
    showDeleteModal.value = false
    await Promise.all([fetchRooms(), fetchBookings()])
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingRoom.value = false
  }
}
</script>

<style scoped>
.admin-rooms {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-8);
  gap: var(--space-4);
  flex-wrap: wrap;
}

.page-title h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
}

.page-title p {
  margin-top: 0.35rem;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.desk-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0.85rem;
  margin-bottom: var(--space-6);
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.frontdesk-controls {
  display: grid;
  gap: 0.85rem;
  padding: 1rem 1.2rem;
  margin-bottom: var(--space-6);
  border: 1px solid #e2e8f0;
  box-shadow: none;
  background: var(--white);
}

.frontdesk-controls-top,
.frontdesk-filters-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.frontdesk-controls-top {
  justify-content: space-between;
}

.frontdesk-filters-row {
  padding-top: 0.15rem;
}

.frontdesk-search-shell {
  flex: 1 1 320px;
  position: relative;
}

.frontdesk-search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
}

.frontdesk-search-input,
.frontdesk-select {
  width: 100%;
  padding: 0.72rem 1rem;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.frontdesk-search-input {
  padding-left: 2.55rem;
}

.frontdesk-select {
  flex: 1 1 220px;
  cursor: pointer;
}

.frontdesk-reset-btn {
  min-height: 44px;
  padding-inline: 1rem;
  flex-shrink: 0;
}

.frontdesk-search-input:focus,
.frontdesk-select:focus {
  outline: none;
  border-color: var(--accent);
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.12);
}

.desk-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.8rem 1rem;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: var(--white);
  color: var(--gray-700);
  font-weight: 800;
  transition: all 0.2s ease;
}

.desk-tab-btn:hover {
  border-color: #cbd5e1;
  color: var(--gray-700);
  background: var(--gray-400);
}

.desk-tab-btn.active {
  border-color: #bfdbfe;
  color: var(--gray-700);
  background: var(--gray-400);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.frontdesk-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.frontdesk-grid-checkin {
  grid-template-columns: 1fr;
}

.frontdesk-grid-checkin .desk-panel {
  grid-column: 1 / -1;
}

.frontdesk-grid-checkout {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.desk-panel,
.desk-guide,
.desk-activity {
  padding: 1.2rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.desk-guide,
.desk-activity {
  grid-column: 1 / -1;
  background: var(--white)
}

.desk-panel-head,
.desk-guide-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.desk-panel-tools {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.desk-panel-head h2,
.desk-guide-head h2 {
  margin: 0;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 800;
}

.desk-panel-head p,
.desk-guide-head p {
  margin: 0.3rem 0 0;
  color: #64748b;
  font-size: 0.88rem;
  line-height: 1.45;
}

.desk-count {
  display: inline-flex;
  min-width: 34px;
  height: 34px;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.85rem;
  font-weight: 800;
}

.desk-list {
  display: grid;
  gap: 0.9rem;
}

.desk-list-checkin {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.desk-list-checkin .desk-item {
  flex-direction: column;
  align-items: stretch;
  height: 100%;
}

.desk-list-checkin .desk-item-main {
  min-width: 0;
}

.desk-list-checkin .desk-item-actions {
  justify-content: flex-start;
  margin-top: auto;
}

.desk-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  background: var(--white);
}

.desk-item-main {
  display: grid;
  gap: 0.28rem;
}

.desk-item-title {
  color: var(--gray-900);
  font-weight: 800;
}

.desk-item-sub {
  color: var(--gray-700);
  font-size: 0.88rem;
}

.desk-item-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-top: 0.2rem;
}

.desk-mini {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  background: var(--gray-200);
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 0.78rem;
  font-weight: 700;
}

.desk-item-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.desk-empty {
  padding: 1.1rem;
  border: 1px dashed #cbd5e1;
  border-radius: 18px;
  background: var(--gray-200);
  color: #64748b;
  text-align: center;
  font-weight: 700;
}

.desk-activity-head {
  margin-bottom: 1.2rem;
}

.desk-activity-badges {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.desk-activity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.activity-column {
  border: 2px solid var(--gray-300);
  border-radius: 20px;
  background: var(--white);
  padding: 1rem;
}

.activity-column-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.9rem;
}

.activity-column-tools {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.activity-column-head strong {
  display: block;
  color: #0f172a;
  font-size: 0.96rem;
  font-weight: 800;
}

.activity-column-head small {
  display: block;
  margin-top: 0.25rem;
  color: #64748b;
  line-height: 1.4;
}

.activity-list {
  display: grid;
  gap: 0.75rem;
}

.activity-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.9rem;
  padding: 0.9rem 1rem;
  border-radius: 16px;
  background: var(--white);
  border: 1px solid var(--gray-400);
}

.activity-item-main {
  display: grid;
  gap: 0.22rem;
  min-width: 0;
}

.activity-title {
  color: var(--gray-900);
  font-weight: 800;
}

.activity-sub {
  color: var(--gray-700);
  font-size: 0.84rem;
  font-weight: 700;
}

.activity-time {
  color: var(--gray-500);
  font-size: 0.82rem;
}

.desk-guide-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.guide-step {
  display: grid;
  gap: 0.35rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  /* background: #ffffff; */
  background: var(--white)
}

.guide-step strong {
  /* color: #0f172a; */
  color: var(--gray-700);
}

.guide-step span {
  color: #1d4ed8;
  font-weight: 800;
}

.guide-step small {
  color: #64748b;
  line-height: 1.45;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  border: 1px solid #eef2f7;
  box-shadow: none;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.primary { background: #eef2ff; color: #4338ca; }
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.warning { background: #fffbeb; color: #f59e0b; }

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  border: 1px solid transparent;
}

.status-available {
  background: #ecfdf3;
  color: #15803d;
  border-color: #bbf7d0;
}

.status-reserved {
  background: var(--white);
  color: var(--gray-700);
  border-color: #fde68a;
}

.status-occupied {
  background: var(--gray-300);
  color: #1d4ed8;
  border-color: #bfdbfe;
}

.status-cleaning {
  background: var(--gray-300);
  color: #0f766e;
  border-color: #a5f3fc;
}

.status-maintenance {
  background: #fef2f2;
  color: #b91c1c;
  border-color: #fecaca;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.actions-cell {
  width: 1%;
  white-space: nowrap;
}

.actions-dropdown {
  position: relative;
  display: inline-flex;
}

.actions-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 190px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12);
  padding: 6px;
  z-index: 30;
}

.actions-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #334155;
  font-weight: 700;
  font-size: 0.9rem;
  text-align: left;
}

.actions-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
  color: #b91c1c;
}

.stat-label {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
}

.stat-value.info { color: #0ea5e9; }
.stat-value.success { color: #22c55e; }
.stat-value.warning { color: #f59e0b; }

.table-title {
  font-size: 1rem;
  font-weight: 800;
  margin-bottom: var(--space-5);
  color: #1e293b;
}

.rooms-table-toolbar :deep(.table-pagination),
.desk-panel-tools :deep(.table-pagination),
.activity-column-tools :deep(.table-pagination) {
  margin-left: 0;
}

@media (max-width: 1200px) {
  .frontdesk-grid {
    grid-template-columns: 1fr;
  }

  .desk-list-checkin {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .frontdesk-grid-checkout {
    grid-template-columns: 1fr;
  }

  .desk-panel-tools {
    justify-content: flex-start;
  }

  .activity-column-tools {
    justify-content: flex-start;
  }

  .desk-activity-grid,
  .desk-guide-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .page-title h1 {
    font-size: 1.45rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--space-4);
  }

  .desk-tabs {
    gap: 0.6rem;
    padding: 0.75rem;
  }

  .desk-tab-btn {
    flex: 1 1 calc(50% - 0.3rem);
    justify-content: center;
  }

  .frontdesk-controls,
  .desk-panel,
  .desk-guide,
  .desk-activity {
    padding: 1rem;
  }

  .frontdesk-controls {
    gap: 0.75rem;
  }

  .frontdesk-controls-top,
  .frontdesk-filters-row,
  .desk-panel-head,
  .desk-guide-head,
  .desk-activity-head,
  .activity-column-head,
  .rooms-table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .frontdesk-search-shell,
  .frontdesk-select,
  .desk-panel-tools,
  .activity-column-tools {
    width: 100%;
  }

  .frontdesk-filters-row {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.65rem;
    padding-top: 0.8rem;
    border-top: 1px solid var(--gray-200);
  }

  .frontdesk-reset-btn {
    width: 100%;
    justify-content: center;
  }

  .desk-panel-tools,
  .activity-column-tools,
  .desk-activity-badges {
    justify-content: space-between;
  }

  .desk-item {
    align-items: stretch;
  }

  .desk-item-actions {
    width: 100%;
    justify-content: stretch;
  }

  .desk-item-actions .btn {
    flex: 1 1 calc(50% - 0.25rem);
    justify-content: center;
  }

  .activity-column {
    padding: 0.9rem;
  }

  .activity-item {
    align-items: flex-start;
  }

  .activity-item .btn {
    width: 100%;
    justify-content: center;
  }

  .actions-menu {
    min-width: min(220px, calc(100vw - 48px));
  }

  .entity-view-modal {
    gap: 14px;
  }

  .entity-view-hero {
    padding: 16px;
  }

  .entity-view-card,
  .booking-summary,
  .service-card {
    padding: 14px;
  }
}

@media (max-width: 640px) {
  .frontdesk-controls {
    padding: 0.85rem;
    gap: 0.65rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .desk-tabs {
    display: grid;
    grid-template-columns: 1fr;
  }

  .desk-tab-btn {
    width: 100%;
    flex: 1 1 100%;
  }

  .frontdesk-controls-top,
  .frontdesk-filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .frontdesk-search-shell {
    flex-basis: auto;
  }

  .frontdesk-search-input,
  .frontdesk-select,
  .frontdesk-reset-btn {
    min-height: 46px;
  }

  .frontdesk-filters-row {
    gap: 0.55rem;
    padding-top: 0.7rem;
  }

  .desk-item {
    flex-direction: column;
  }

  .desk-list-checkin {
    grid-template-columns: 1fr;
  }

  .activity-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .desk-item-actions {
    justify-content: flex-start;
  }

  .desk-item-actions .btn {
    width: 100%;
    flex: 1 1 100%;
  }

  .desk-panel-tools {
    width: 100%;
  }

  .activity-column-tools {
    width: 100%;
  }

  .rooms-table-toolbar {
    align-items: stretch;
  }

  .rooms-table-toolbar :deep(.table-pagination),
  .desk-panel-tools :deep(.table-pagination),
  .activity-column-tools :deep(.table-pagination) {
    width: 100%;
  }

  .desk-panel,
  .desk-guide,
  .desk-activity,
  .frontdesk-controls,
  .activity-column {
    padding: 0.85rem;
  }

  .desk-panel-head h2,
  .desk-guide-head h2,
  .activity-column-head strong {
    font-size: 0.95rem;
  }

  .desk-item,
  .activity-item {
    padding: 0.85rem;
  }

  .desk-activity-grid,
  .desk-guide-grid {
    grid-template-columns: 1fr;
  }

  .desk-activity-badges {
    flex-direction: column;
    align-items: stretch;
  }

  .activity-column-tools,
  .desk-panel-tools {
    flex-direction: column;
    align-items: stretch;
  }

  .desk-count {
    align-self: flex-start;
  }

  .entity-view-hero {
    padding: 14px;
  }

  .entity-view-avatar {
    width: 56px;
    height: 56px;
  }

  .entity-view-main h3 {
    font-size: 1rem;
  }
}

:global(html[data-admin-theme="dark"]) .desk-tabs,
:global(html[data-admin-theme="dark"]) .frontdesk-controls,
:global(html[data-admin-theme="dark"]) .desk-panel,
:global(html[data-admin-theme="dark"]) .desk-guide,
:global(html[data-admin-theme="dark"]) .desk-activity,
:global(html[data-admin-theme="dark"]) .stat-card,
:global(html[data-admin-theme="dark"]) .actions-menu {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .desk-tab-btn,
:global(html[data-admin-theme="dark"]) .frontdesk-search-input,
:global(html[data-admin-theme="dark"]) .frontdesk-select,
:global(html[data-admin-theme="dark"]) .desk-item,
:global(html[data-admin-theme="dark"]) .activity-column,
:global(html[data-admin-theme="dark"]) .activity-item,
:global(html[data-admin-theme="dark"]) .guide-step,
:global(html[data-admin-theme="dark"]) .booking-summary,
:global(html[data-admin-theme="dark"]) .stay-modal-summary,
:global(html[data-admin-theme="dark"]) .stay-guest-card,
:global(html[data-admin-theme="dark"]) .stay-modal-checkout,
:global(html[data-admin-theme="dark"]) .entity-view-card,
:global(html[data-admin-theme="dark"]) .entity-view-item,
:global(html[data-admin-theme="dark"]) .entity-view-empty {
  background: rgba(15, 23, 42, 0.88);
  border-color: rgba(51, 65, 85, 0.9);
}

:global(html[data-admin-theme="dark"]) .frontdesk-search-input,
:global(html[data-admin-theme="dark"]) .frontdesk-select,
:global(html[data-admin-theme="dark"]) .desk-item-sub,
:global(html[data-admin-theme="dark"]) .activity-sub,
:global(html[data-admin-theme="dark"]) .activity-time,
:global(html[data-admin-theme="dark"]) .desk-panel-head p,
:global(html[data-admin-theme="dark"]) .desk-guide-head p,
:global(html[data-admin-theme="dark"]) .page-title p {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .page-title h1,
:global(html[data-admin-theme="dark"]) .desk-panel-head h2,
:global(html[data-admin-theme="dark"]) .desk-guide-head h2,
:global(html[data-admin-theme="dark"]) .activity-column-head strong,
:global(html[data-admin-theme="dark"]) .activity-title,
:global(html[data-admin-theme="dark"]) .booking-summary strong,
:global(html[data-admin-theme="dark"]) .stay-modal-head h3,
:global(html[data-admin-theme="dark"]) .stay-modal-checkout h3,
:global(html[data-admin-theme="dark"]) .stay-guest-card-head strong,
:global(html[data-admin-theme="dark"]) .stay-modal-summary strong,
:global(html[data-admin-theme="dark"]) .stay-modal-guest-line strong,
:global(html[data-admin-theme="dark"]) .entity-view-value,
:global(html[data-admin-theme="dark"]) .table-title,
:global(html[data-admin-theme="dark"]) .stat-value {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .stay-modal-head p,
:global(html[data-admin-theme="dark"]) .stay-modal-checkout p,
:global(html[data-admin-theme="dark"]) .stay-modal-summary,
:global(html[data-admin-theme="dark"]) .stay-modal-guest-line {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .frontdesk-search-input:focus,
:global(html[data-admin-theme="dark"]) .frontdesk-select:focus {
  background: rgba(15, 23, 42, 0.98);
}

:global(html[data-admin-theme="dark"]) .frontdesk-search-icon,
:global(html[data-admin-theme="dark"]) .stat-label,
:global(html[data-admin-theme="dark"]) .activity-column-head small,
:global(html[data-admin-theme="dark"]) .entity-view-card-title,
:global(html[data-admin-theme="dark"]) .entity-view-label {
  color: #94a3b8;
}

:global(html[data-admin-theme="dark"]) .desk-mini,
:global(html[data-admin-theme="dark"]) .desk-empty,
:global(html[data-admin-theme="dark"]) .btn-icon {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(51, 65, 85, 0.9);
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .desk-count {
  background: rgba(37, 99, 235, 0.22);
  color: #bfdbfe;
}

:global(html[data-admin-theme="dark"]) .booking-summary,
:global(html[data-admin-theme="dark"]) .form-hint,
:global(html[data-admin-theme="dark"]) .entity-view-empty {
  color: #cbd5e1;
}

.btn-icon {
  width: 34px;
  height: 34px;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.view:hover { color: var(--info); }
.btn-icon.edit:hover { color: var(--primary); }
.btn-icon.delete:hover { color: var(--danger); }

.empty-cell {
  text-align: center;
  color: #94a3b8;
  font-weight: 600;
  padding: var(--space-4) 0;
}

.entity-view-modal { display: grid; gap: 18px; }
.entity-view-hero { display: flex; align-items: center; gap: 16px; padding: 18px; border-radius: 20px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #ffffff; }
.entity-view-avatar { width: 64px; height: 64px; border-radius: 18px; background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.18); display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 800; letter-spacing: .08em; flex-shrink: 0; }
.entity-view-main { min-width: 0; flex: 1; }
.entity-view-code { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.14); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.entity-view-main h3 { margin: 6px 0 4px; font-size: 1.15rem; font-weight: 800; color: #ffffff; }
.entity-view-main p { margin: 0; color: rgba(255,255,255,.78); font-size: .92rem; }
.entity-view-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.entity-view-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.entity-view-card { border: 1px solid #e2e8f0; border-radius: 18px; background: #ffffff; padding: 16px; }
.entity-view-card-full { grid-column: 1 / -1; }
.entity-view-card-title { margin-bottom: 14px; font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #64748b; }
.entity-view-list { display: grid; gap: 10px; }
.entity-view-item { display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 14px; background: #f8fafc; border: 1px solid #e2e8f0; }
.entity-view-label { color: #64748b; font-size: .82rem; font-weight: 700; }
.entity-view-value { color: #0f172a; font-size: .9rem; font-weight: 700; text-align: right; word-break: break-word; }
.entity-view-empty { padding: 1rem; border: 1px dashed #cbd5e1; border-radius: 14px; color: #64748b; font-weight: 600; background: #f8fafc; }

.booking-summary {
  display: grid;
  gap: 0.65rem;
  margin-bottom: 1rem;
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  color: #334155;
  font-size: 0.9rem;
}

.booking-summary strong {
  color: var(--gray-900);
}

.stay-modal-shell {
  display: grid;
  gap: 1rem;
}

.stay-modal-summary {
  display: grid;
  gap: 0.55rem;
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid #dbeafe;
  background: var(--white);
  color: var(--gray-700);
}

.stay-modal-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.stay-modal-head h3,
.stay-modal-checkout h3 {
  margin: 0;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 800;
}

.stay-modal-head p,
.stay-modal-checkout p {
  margin: 0.35rem 0 0;
  color: #64748b;
  line-height: 1.55;
}

.stay-guests-list {
  display: grid;
  gap: 0.85rem;
}

.stay-guest-card {
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid var(--gray-400);
  background: var(--white);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.04);
}

.stay-guest-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.stay-guest-card-head strong,
.stay-modal-summary strong,
.stay-modal-guest-line strong {
  color: var(--gray-900);
}

.stay-modal-checkout {
  padding: 1rem;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.stay-modal-guest-line {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.9rem;
  color: #475569;
  flex-wrap: wrap;
}

:global(html[data-admin-theme="dark"]) .stay-modal-summary,
:global(html[data-admin-theme="dark"]) .stay-guest-card,
:global(html[data-admin-theme="dark"]) .stay-modal-checkout {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.84) 100%);
  border-color: rgba(51, 65, 85, 0.95);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

:global(html[data-admin-theme="dark"]) .stay-modal-summary,
:global(html[data-admin-theme="dark"]) .stay-modal-head p,
:global(html[data-admin-theme="dark"]) .stay-modal-checkout p,
:global(html[data-admin-theme="dark"]) .stay-modal-guest-line {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .stay-modal-summary strong,
:global(html[data-admin-theme="dark"]) .stay-modal-head h3,
:global(html[data-admin-theme="dark"]) .stay-modal-checkout h3,
:global(html[data-admin-theme="dark"]) .stay-guest-card-head strong,
:global(html[data-admin-theme="dark"]) .stay-modal-guest-line strong {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .stay-guest-card .form-input,
:global(html[data-admin-theme="dark"]) .stay-guest-card .form-select,
:global(html[data-admin-theme="dark"]) .stay-guest-card .form-textarea {
  background: rgba(30, 41, 59, 0.95);
  border-color: rgba(71, 85, 105, 0.95);
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .stay-guest-card .form-input::placeholder,
:global(html[data-admin-theme="dark"]) .stay-guest-card .form-textarea::placeholder {
  color: #94a3b8;
}

:global(html[data-admin-theme="dark"]) .stay-guest-card .form-label {
  color: #cbd5e1;
}

.form-hint {
  display: block;
  margin-top: 0.5rem;
  color: #64748b;
  font-size: 0.82rem;
  line-height: 1.45;
}

.services-section {
  margin-top: 1rem;
  border-top: 1px solid #eef2f7;
  padding-top: 1rem;
}

.services-head,
.subservices-head,
.service-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.services-head h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
}

.services-head p {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 0.88rem;
}

@media (max-width: 640px) {
  .entity-view-hero { flex-direction: column; align-items: flex-start; }
  .entity-view-badges { align-items: flex-start; flex-direction: row; flex-wrap: wrap; }
  .entity-view-grid { grid-template-columns: 1fr; }
  .entity-view-item { flex-direction: column; }
  .entity-view-value { text-align: left; }
  .stay-modal-head { flex-direction: column; }
  .stay-modal-guest-line { flex-direction: column; }
}

.services-empty {
  margin-top: 0.75rem;
  padding: 1rem;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  color: #64748b;
  font-weight: 600;
  background: #f8fafc;
}

.service-card {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #fafcff;
}

.service-card-head {
  margin-bottom: 0.9rem;
}

.service-state-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 800;
  letter-spacing: 0.01em;
  border: 1px solid transparent;

}

.service-state-pill.is-yes {
  color: #166534;
  color: var(--gray-700);
  border-color: #bbf7d0;
}

.service-state-pill.is-no {
  color: #b91c1c;
  color: var(--gray-700);
  border-color: #fecaca;
}

.toggle-field {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 56px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #dbe3ee;
  border-radius: 16px;
  background: #f8fafc;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.toggle-field:hover {
  border-color: #cbd5e1;
  background: #f1f5f9;
}

.toggle-field input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.toggle-field.is-active {
  border-color: #86efac;
  background: #f0fdf4;
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.12);
}

.toggle-switch {
  position: relative;
  width: 50px;
  height: 30px;
  border-radius: 999px;
  background: #cbd5e1;
  flex-shrink: 0;
  transition: background 0.2s ease;
}

.toggle-knob {
  position: absolute;
  top: 4px;
  left: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.18);
  transition: transform 0.2s ease;
}

.toggle-field.is-active .toggle-switch {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.toggle-field.is-active .toggle-knob {
  transform: translateX(20px);
}

.toggle-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.toggle-copy strong {
  color: #0f172a;
  font-size: 0.92rem;
  font-weight: 800;
}

.toggle-copy small {
  color: #64748b;
  font-size: 0.78rem;
  line-height: 1.35;
}

.subservices-section {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px dashed #dbe3ee;
}

.subservice-row {
  display: grid;
  grid-template-columns: 1.3fr 1fr auto;
  gap: 10px;
  align-items: center;
  margin-top: 0.75rem;
}

.btn-icon.delete:hover {
  color: var(--danger);
}

.detail-block {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid #f1f5f9;
}

.muted-block {
  color: #64748b;
}

.services-preview {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.service-preview-item {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.85rem 1rem;
  background: #f8fafc;
}

.service-preview-title,
.service-preview-sub {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.service-preview-title {
  color: #0f172a;
}

.service-preview-subs {
  margin-top: 0.55rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: #475569;
}

@media (max-width: 900px) {
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .subservice-row {
    grid-template-columns: 1fr;
  }
}
</style>
