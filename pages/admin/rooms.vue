<template>
  <div class="admin-rooms">
    <div class="header-actions">
      <div class="page-title">
        <h1>Gestion des Chambres</h1>
        <p>Créer, modifier et suivre les capacités et tarifs des chambres</p>
      </div>
      <button class="btn btn-primary btn-sm admin-head-btn" @click="openAddModal">
        <i class="fas fa-plus"></i>
        <span class="btn-label">Ajouter une chambre</span>
      </button>
    </div>

    <div class="stats-grid mb-8">
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

    <div v-if="activeDeskTab !== 'rooms'" class="frontdesk-grid">
      <section v-if="activeDeskTab === 'checkin'" class="desk-panel card">
        <div class="desk-panel-head">
          <div>
            <h2>Arrivées / Check-in</h2>
            <p>Clients attendus ou réservations prêtes à accueillir.</p>
          </div>
          <span class="desk-count">{{ pendingArrivalBookings.length }}</span>
        </div>
        <div v-if="deskLoading" class="desk-empty">Chargement des séjours...</div>
        <div v-else-if="pendingArrivalBookings.length === 0" class="desk-empty">Aucune arrivée en attente</div>
        <div v-else class="desk-list">
          <div v-for="booking in pendingArrivalBookings.slice(0, 6)" :key="`arrival-${booking.id}`" class="desk-item">
            <div class="desk-item-main">
              <div class="desk-item-title">{{ booking.guest_full_name || booking.customer_name }}</div>
              <div class="desk-item-sub">{{ booking.room_display || '-' }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              <div class="desk-item-meta">
                <span :class="['status-pill', `status-${booking.room_status || 'reserved'}`]">{{ roomStatusLabel(booking.room_status || 'reserved') }}</span>
                <span class="desk-mini">{{ booking.code || '-' }}</span>
                <span class="desk-mini">{{ paymentStateLabel(booking) }}</span>
              </div>
            </div>
            <div class="desk-item-actions">
              <button v-if="Number(booking.remaining_amount || 0) > 0" class="btn btn-outline btn-sm" @click="openPaymentForBooking(booking)">Paiement</button>
              <button class="btn btn-primary btn-sm" :class="{ 'is-loading': stayActionLoadingId === booking.id && stayActionType === 'check_in' }" :disabled="stayActionLoadingId === booking.id || !booking.can_check_in" @click="manageStay(booking, 'check_in')">Check-in</button>
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
          <span class="desk-count">{{ inHouseBookings.length }}</span>
        </div>
        <div v-if="deskLoading" class="desk-empty">Chargement des séjours...</div>
        <div v-else-if="inHouseBookings.length === 0" class="desk-empty">Aucun client en chambre</div>
        <div v-else class="desk-list">
          <div v-for="booking in inHouseBookings.slice(0, 6)" :key="`stay-${booking.id}`" class="desk-item">
            <div class="desk-item-main">
              <div class="desk-item-title">{{ booking.guest_full_name || booking.customer_name }}</div>
              <div class="desk-item-sub">{{ booking.room_display || '-' }} • Check-in {{ formatDeskDate(booking.checked_in_at) }}</div>
              <div class="desk-item-meta">
                <span :class="['status-pill', 'status-occupied']">Occupée</span>
                <span class="desk-mini">{{ booking.code || '-' }}</span>
                <span class="desk-mini">{{ paymentStateLabel(booking) }}</span>
              </div>
            </div>
            <div class="desk-item-actions">
              <button v-if="Number(booking.remaining_amount || 0) > 0" class="btn btn-outline btn-sm" @click="openPaymentForBooking(booking)">Solder</button>
              <button class="btn btn-primary btn-sm" :class="{ 'is-loading': stayActionLoadingId === booking.id && stayActionType === 'check_out' }" :disabled="stayActionLoadingId === booking.id || Number(booking.remaining_amount || 0) > 0 || !booking.can_check_out" @click="manageStay(booking, 'check_out')">Check-out</button>
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
          <span class="desk-count">{{ cleaningRoomsList.length }}</span>
        </div>
        <div v-if="deskLoading" class="desk-empty">Chargement des chambres...</div>
        <div v-else-if="cleaningRoomsList.length === 0" class="desk-empty">Aucune chambre en nettoyage</div>
        <div v-else class="desk-list">
          <div v-for="room in cleaningRoomsList.slice(0, 6)" :key="`clean-${room.id}`" class="desk-item">
            <div class="desk-item-main">
              <div class="desk-item-title">{{ room.room_number }} - {{ room.name }}</div>
              <div class="desk-item-sub">{{ roomTypeLabel(room.room_type) }} • {{ formatMoney(room.price_per_night) }}/nuit</div>
              <div class="desk-item-meta">
                <span :class="['status-pill', 'status-cleaning']">Nettoyage</span>
                <span class="desk-mini" v-if="nextReservationForRoom(room.id)">Prochaine arrivée: {{ nextReservationForRoom(room.id).guest_full_name || nextReservationForRoom(room.id).customer_name }}</span>
              </div>
            </div>
            <div class="desk-item-actions">
              <button class="btn btn-primary btn-sm" @click="setRoomStatus(room, 'available')">Marquer prête</button>
              <button v-if="nextReservationForRoom(room.id)" class="btn btn-outline btn-sm" @click="openBookingDetails(nextReservationForRoom(room.id))">Voir réservation</button>
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
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
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
                  <button v-if="room.status === 'cleaning'" class="actions-item" @click="setRoomStatus(room, 'available')">
                    <i class="fas fa-broom"></i> Marquer prête
                  </button>
                  <button v-if="room.status !== 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'maintenance')">
                    <i class="fas fa-screwdriver-wrench"></i> Mettre en maintenance
                  </button>
                  <button v-if="room.status === 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'available')">
                    <i class="fas fa-circle-check"></i> Rendre disponible
                  </button>
                  <button class="actions-item" @click="editRoom(room)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(room)">
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
                    <button v-if="room.status === 'cleaning'" class="actions-item" @click="setRoomStatus(room, 'available')">
                      <i class="fas fa-broom"></i> Marquer prête
                    </button>
                    <button v-if="room.status !== 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'maintenance')">
                      <i class="fas fa-screwdriver-wrench"></i> Mettre en maintenance
                    </button>
                    <button v-if="room.status === 'maintenance'" class="actions-item" @click="setRoomStatus(room, 'available')">
                      <i class="fas fa-circle-check"></i> Rendre disponible
                    </button>
                    <button class="actions-item" @click="editRoom(room)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="actions-item danger" @click="confirmDelete(room)">
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
        <button class="btn btn-danger" :class="{ 'is-loading': deletingRoom }" :disabled="deletingRoom" @click="deleteRoom">
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

definePageMeta({ layout: 'admin' })
const { formatMoney, moneyInputModel, parseMoney, formatNumberSpaces } = useMoney()
const { formatDateRange, formatDisplayDate } = useDateFormat()

const rooms = ref([])
const bookings = ref([])
const loadingRooms = ref(false)
const loadingBookings = ref(false)
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedRoom = ref(null)
const openActionsId = ref(null)
const isMobile = ref(false)
const savingRoom = ref(false)
const deletingRoom = ref(false)
const stayActionLoadingId = ref(null)
const stayActionType = ref('')
const activeDeskTab = ref('checkin')

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
const pendingArrivalBookings = computed(() => roomBookings.value
  .filter((booking) => !booking?.checked_in_at && !booking?.checked_out_at)
  .slice()
  .sort((a, b) => new Date(a?.start_date || 0) - new Date(b?.start_date || 0)))
const inHouseBookings = computed(() => roomBookings.value
  .filter((booking) => booking?.checked_in_at && !booking?.checked_out_at)
  .slice()
  .sort((a, b) => new Date(a?.start_date || 0) - new Date(b?.start_date || 0)))
const cleaningRoomsList = computed(() => rooms.value.filter(room => room?.status === 'cleaning'))
const deskLoading = computed(() => loadingRooms.value || loadingBookings.value)

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

const formatDeskDate = (value) => value ? formatDisplayDate(value) : '-'
const paymentStateLabel = (booking) => Number(booking?.remaining_amount || 0) > 0
  ? `Reste: ${formatMoney(booking?.remaining_amount || 0)}`
  : 'Séjour soldé'
const nextReservationForRoom = (roomId) => pendingArrivalBookings.value.find((booking) => Number(booking?.room) === Number(roomId))

const openPaymentForBooking = (booking) => navigateTo(`/admin/payments?booking=${booking.id}`)
const openBookingDetails = (booking) => navigateTo(`/admin/bookings?view=${booking.id}`)

const setRoomStatus = async (room, status) => {
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

const manageStay = async (booking, action) => {
  if (!booking?.id || stayActionLoadingId.value) return
  stayActionLoadingId.value = booking.id
  stayActionType.value = action
  try {
    await api.post(`bookings/${booking.id}/${action === 'check_in' ? 'check-in' : 'check-out'}/`)
    notify(action === 'check_in' ? 'Check-in enregistré' : 'Check-out enregistré', 'success')
    await Promise.all([fetchRooms(), fetchBookings()])
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.detail || 'Impossible de mettre à jour le séjour', 'danger')
  } finally {
    stayActionLoadingId.value = null
    stayActionType.value = ''
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
  openActionsId.value = null
  selectedRoom.value = room
  showDeleteModal.value = true
}

const saveRoom = async () => {
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

.desk-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.8rem 1rem;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #475569;
  font-weight: 800;
  transition: all 0.2s ease;
}

.desk-tab-btn:hover {
  border-color: #cbd5e1;
  color: #0f172a;
  background: #f8fafc;
}

.desk-tab-btn.active {
  border-color: #bfdbfe;
  background: #eff6ff;
  color: #1d4ed8;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12);
}

.frontdesk-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.desk-panel,
.desk-guide {
  padding: 1.2rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.desk-guide {
  grid-column: 1 / -1;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}

.desk-panel-head,
.desk-guide-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
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

.desk-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  background: #f8fafc;
}

.desk-item-main {
  display: grid;
  gap: 0.28rem;
}

.desk-item-title {
  color: #0f172a;
  font-weight: 800;
}

.desk-item-sub {
  color: #475569;
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
  background: #ffffff;
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
  background: #f8fafc;
  color: #64748b;
  text-align: center;
  font-weight: 700;
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
  background: #ffffff;
}

.guide-step strong {
  color: #0f172a;
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
  background: #fffbeb;
  color: #b45309;
  border-color: #fde68a;
}

.status-occupied {
  background: #eff6ff;
  color: #1d4ed8;
  border-color: #bfdbfe;
}

.status-cleaning {
  background: #ecfeff;
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

@media (max-width: 1200px) {
  .frontdesk-grid {
    grid-template-columns: 1fr;
  }

  .desk-guide-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .desk-item {
    flex-direction: column;
  }

  .desk-item-actions {
    justify-content: flex-start;
  }

  .desk-guide-grid {
    grid-template-columns: 1fr;
  }
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
