<!-- pages/admin/bookings.vue -->
<template>
  <div class="bookings-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Réservations</h1>
        <p>Gérer toutes les réservations de salle et chambre</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i>
          <span class="btn-label">Export PDF</span>
        </button>
        <button v-if="canExportExcel" class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
          <i class="fas fa-file-excel"></i>
          <span class="btn-label">Export XLS</span>
        </button>
        <NuxtLink to="/admin/calendar" class="btn btn-secondary btn-sm admin-head-btn">
          <i class="fas fa-calendar-alt"></i>
          <span class="btn-label">Calendrier global</span>
        </NuxtLink>
        <button class="btn btn-primary btn-sm admin-head-btn" @click="openAddModal">
          <i class="fas fa-plus"></i>
          <span class="btn-label">Nouvelle réservation</span>
        </button>
      </div>
    </div>

    <!-- Controls -->
    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            type="text"
            v-model="search"
            placeholder="Rechercher par client, salle ou chambre..."
            class="search-input-clean"
          />
        </div>
        <button class="btn btn-sm" @click="resetFilters" style="margin-right: 8px;">
          <i class="fas fa-redo"></i> Réinitialiser
        </button>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>
      <div v-show="!isMobile || filtersOpen" class="filters-panel">
        <div class="filter-wrapper">
          <select v-model="statusFilter" class="filter-select-clean">
            <option value="">Tous les statuts</option>
            <option value="pending">En attente</option>
            <option value="confirmed">Confirmé</option>
            <option value="paid">Payé</option>
            <option value="cancelled">Annulé</option>
          </select>
        </div>
        <div class="filter-wrapper">
          <select v-model="hallFilter" class="filter-select-clean">
            <option value="">Tous les types</option>
            <option value="hall">Salles</option>
            <option value="room">Chambres</option>
          </select>
        </div>
        <div class="filter-wrapper">
          <select v-model="eventTypeFilter" class="filter-select-clean">
            <option value="">Tous les événements</option>
            <option value="Mariage">Mariage</option>
            <option value="Séminaire">Séminaire</option>
            <option value="Gala">Gala</option>
            <option value="Anniversaire">Anniversaire</option>
            <option value="Réunion">Réunion</option>
            <option value="Autres">Autres</option>
          </select>
        </div>
        <div class="filter-wrapper">
          <select v-model="preset" class="filter-select-clean">
            <option value="all">Toutes les dates</option>
            <option value="7d">7 derniers jours</option>
            <option value="28d">28 derniers jours</option>
            <option value="90d">90 derniers jours</option>
            <option value="this_month">Ce mois</option>
            <option value="last_month">Mois dernier</option>
            <option value="year">Cette année</option>
            <option value="custom">Personnalisé</option>
          </select>
        </div>
        <div v-if="preset === 'custom'" class="filter-wrapper">
          <input v-model="customStart" type="date" class="filter-input-clean" />
        </div>
        <div v-if="preset === 'custom'" class="filter-wrapper">
          <input v-model="customEnd" type="date" class="filter-input-clean" />
        </div>
        <div class="filter-wrapper">
          <input v-model="minAmountInput" inputmode="numeric" type="text" class="filter-input-clean" placeholder="Min (Fbu)" />
        </div>
        <div class="filter-wrapper">
          <input v-model="maxAmountInput" inputmode="numeric" type="text" class="filter-input-clean" placeholder="Max (Fbu)" />
        </div>
      </div>
      <div class="filter-range-note">{{ activeRangeNotice }}</div>
    </div>

    <!-- Table -->
    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <h2 class="table-title" style="margin-bottom:0;">
          Toutes les réservations ({{ loadingBookings ? '...' : filteredBookings.length }})
        </h2>
        <AdminAppTablePagination
          :start="bookingsStartIndex"
          :end="bookingsEndIndex"
          :total="bookingsTotalItems"
          :can-prev="bookingsCanPrev"
          :can-next="bookingsCanNext"
          :disabled="loadingBookings"
          @prev="bookingsPrevPage"
          @next="bookingsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingBookings">
          <div v-for="n in 6" :key="`sk-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-70"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-50"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-60"></div>
              <div class="skeleton-line skeleton-w-50"></div>
              <div class="skeleton-line skeleton-w-40"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="booking in paginatedBookings" :key="booking.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ booking.customer_name }}</div>
                <div class="admin-card-subtitle">{{ getBookingDisplayId(booking) }} • {{ booking.booking_type === 'hall' ? booking.hall_name : booking.room_display }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              </div>

              <div class="admin-card-actions">
                <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(booking.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === booking.id" class="actions-menu" @click.stop>
                  <NuxtLink v-if="booking.status !== 'paid'" class="actions-item" :to="`/admin/payments?booking=${booking.id}`" @click="closeActions">
                    <i class="fas fa-coins"></i> Payer
                  </NuxtLink>
                  <button
                    v-if="booking.status === 'pending'"
                    class="actions-item"
                    @click="printBookingJeton(booking)"
                  >
                    <i class="fas fa-file-arrow-down"></i> Télécharger le jeton
                  </button>
                  <button
                    v-if="booking.status === 'pending'"
                    class="actions-item"
                    :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'approve' }"
                    :disabled="actionBookingId === booking.id"
                    @click="approve(booking)"
                  >
                    <i class="fas fa-check-circle"></i> Approuver
                  </button>
                  <button
                    v-if="booking.status === 'pending'"
                    class="actions-item"
                    :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'reject' }"
                    :disabled="actionBookingId === booking.id"
                    @click="reject(booking)"
                  >
                    <i class="fas fa-times-circle"></i> Rejeter
                  </button>
                  <button class="actions-item" @click="viewBooking(booking)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editBooking(booking)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button v-if="canDeleteBookings" class="actions-item danger" @click="confirmDelete(booking)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Code</span>
                <span class="v">{{ getBookingDisplayId(booking) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Événement</span>
                <span class="v">{{ booking.event_type }}</span>
              </div>
              <div v-if="booking.booking_type === 'room'" class="admin-kv">
                <span class="k">Client hébergé</span>
                <span class="v">{{ booking.guest_full_name || booking.customer_name }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Montant</span>
                <span class="v">{{ formatMoney(booking.total_price) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v">
                  <span :class="['badge', getBadgeClass(booking.status)]">{{ getStatusTranslation(booking.status) }}</span>
                </span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingBookings && filteredBookings.length === 0" class="empty-cell">Aucune réservation</div>
      </div>

      <div v-else class="table-wrapper">
        <table ref="tableRef" class="bookings-table admin-table">
          <thead>
            <tr>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('code') }" @click="toggleBookingSort('code')">Code <i :class="bookingSortIconClass('code')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('customer_name') }" @click="toggleBookingSort('customer_name')">Client <i :class="bookingSortIconClass('customer_name')"></i></button></th>
              <th>Type</th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('hall_name') }" @click="toggleBookingSort('hall_name')">Salle/Chambre <i :class="bookingSortIconClass('hall_name')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('event_type') }" @click="toggleBookingSort('event_type')">Événement <i :class="bookingSortIconClass('event_type')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('start_date') }" @click="toggleBookingSort('start_date')">Dates <i :class="bookingSortIconClass('start_date')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('total_price') }" @click="toggleBookingSort('total_price')">Montant <i :class="bookingSortIconClass('total_price')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('status') }" @click="toggleBookingSort('status')">Statut <i :class="bookingSortIconClass('status')"></i></button></th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loadingBookings">
              <tr v-for="n in 6" :key="`sk-${n}`">
                <td><div class="skeleton-line skeleton-w-50"></div></td>
                <td class="customer-cell">
                  <div class="skeleton-lines">
                    <div class="skeleton-line skeleton-w-70"></div>
                    <div class="skeleton-line skeleton-w-50"></div>
                  </div>
                </td>
                <td><div class="skeleton-line skeleton-w-40"></div></td>
                <td><div class="skeleton-line skeleton-w-60"></div></td>
                <td><div class="skeleton-line skeleton-w-50"></div></td>
                <td class="date-cell">
                  <div class="skeleton-lines">
                    <div class="skeleton-line skeleton-w-60"></div>
                    <div class="skeleton-line skeleton-w-40"></div>
                  </div>
                </td>
                <td class="amount-cell"><div class="skeleton-line skeleton-w-50"></div></td>
                <td><div class="skeleton-line skeleton-w-40"></div></td>
                <td class="actions-cell"><div class="skeleton-line skeleton-w-60"></div></td>
              </tr>
            </template>
            <tr v-else v-for="booking in paginatedBookings" :key="booking.id">
              <td><code>{{ getBookingDisplayId(booking) }}</code></td>
              <td class="customer-cell">
                <div class="customer-name">{{ booking.customer_name }}</div>
                <div class="customer-email">{{ booking.customer_email }}</div>
                <div v-if="booking.booking_type === 'room'" class="customer-meta">{{ guestIdSummary(booking) }}</div>
              </td>
              <td>
                <span class="badge" :style="{ background: booking.booking_type === 'hall' ? '#eff6ff' : '#f0fdf4', color: booking.booking_type === 'hall' ? '#1e40af' : '#166534' }">
                  {{ booking.booking_type === 'hall' ? 'Salle' : 'Chambre' }}
                </span>
              </td>
              <td>{{ booking.booking_type === 'hall' ? booking.hall_name : booking.room_display }}</td>
              <td>{{ booking.event_type }}</td>
              <td class="date-cell">{{ formatDateRange(booking.start_date, booking.end_date) }}</td>
              <td class="amount-cell">{{ formatMoney(booking.total_price) }}</td>
              <td>
                <span :class="['badge', getBadgeClass(booking.status)]">
                  {{ getStatusTranslation(booking.status) }}
                </span>
              </td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(booking.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === booking.id" class="actions-menu" @click.stop>
                    <NuxtLink v-if="booking.status !== 'paid'" class="actions-item" :to="`/admin/payments?booking=${booking.id}`" @click="closeActions">
                      <i class="fas fa-coins"></i> Payer
                    </NuxtLink>
                    <button v-if="booking.status === 'pending'" class="actions-item" @click="printBookingJeton(booking)">
                      <i class="fas fa-file-arrow-down"></i> Télécharger le jeton
                    </button>
                    <button v-if="booking.status === 'pending'" class="actions-item" :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'approve' }" :disabled="actionBookingId === booking.id" @click="approve(booking)">
                      <i class="fas fa-check-circle"></i> Approuver
                    </button>
                    <button v-if="booking.status === 'pending'" class="actions-item" :class="{ 'is-loading': actionBookingId === booking.id && actionType === 'reject' }" :disabled="actionBookingId === booking.id" @click="reject(booking)">
                      <i class="fas fa-times-circle"></i> Rejeter
                    </button>
                    <button class="actions-item" @click="viewBooking(booking)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="actions-item" @click="editBooking(booking)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button v-if="canDeleteBookings" class="actions-item danger" @click="confirmDelete(booking)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la réservation' : 'Nouvelle réservation'" width="760px">
      <form @submit.prevent="saveBooking" class="admin-form booking-form-shell">
        <div class="booking-form-hero">
          <div class="booking-form-hero-copy">
            <span class="booking-form-eyebrow">Réservation</span>
            <h3>{{ isEditing ? 'Mettre à jour la réservation' : 'Créer une nouvelle réservation' }}</h3>
            <p>Un parcours plus clair pour gérer le client, la chambre ou la salle, la période et le total en un seul endroit.</p>
          </div>
          <div class="booking-form-hero-meta">
            <span class="booking-form-chip">{{ form.customer_kind === 'organization' ? 'Organisation' : 'Particulier' }}</span>
            <span class="booking-form-chip accent">{{ form.booking_type === 'room' ? 'Réservation chambre' : 'Réservation salle' }}</span>
          </div>
        </div>

        <section class="booking-form-section">
          <div class="booking-form-section-head">
            <div>
              <span class="booking-form-section-kicker">Étape 1</span>
              <h4>Client et contact</h4>
            </div>
            <p>Définissez le type de réservation puis complétez les informations du client ou de l’organisation.</p>
          </div>

          <div class="form-grid booking-form-grid">
            <div class="form-group">
              <label class="form-label">Réservation pour</label>
              <select v-model="form.customer_kind" class="form-select" @change="onCustomerKindChange">
                <option value="individual">Particulier</option>
                <option value="organization">Organisation</option>
              </select>
            </div>

            <div v-if="form.customer_kind === 'organization'" class="form-group full organization-booking-note">
              <strong>Réservation organisation</strong>
              <small>Une organisation peut réserver plusieurs chambres et la pièce d'identité n'est pas obligatoire.</small>
            </div>

            <div v-if="form.customer_kind === 'individual'" class="form-group full customer-lookup-card">
              <div class="customer-lookup-head">
                <div>
                  <label class="form-label">Client</label>
                  <small>Rechercher par nom ou téléphone, puis sélectionner ou créer rapidement.</small>
                </div>
                <button type="button" class="btn btn-outline btn-sm" @click="toggleQuickCustomerForm">
                  <i class="fas fa-user-plus"></i>
                  {{ showQuickCustomerForm ? 'Fermer' : 'Nouveau client' }}
                </button>
              </div>
              <div class="customer-search-shell">
                <i class="fas fa-search customer-search-icon"></i>
                <input
                  v-model="customerSearch"
                  type="text"
                  class="form-input customer-search-input"
                  placeholder="Rechercher par nom ou téléphone"
                  @focus="openCustomerResults"
                />
              </div>
              <div v-if="customerResultsOpen" class="customer-results-list">
                <button
                  v-for="customer in customerSearchResults"
                  :key="customer.id"
                  type="button"
                  class="customer-result-item"
                  @click="selectCustomer(customer)"
                >
                  <strong>{{ customer.full_name || `${customer.first_name || ''} ${customer.last_name || ''}`.trim() }}</strong>
                  <span>{{ customer.phone || '-' }}<template v-if="customer.email"> • {{ customer.email }}</template></span>
                </button>
                <div v-if="loadingCustomers" class="customer-results-empty">Recherche des clients...</div>
                <div v-else-if="!customerSearchResults.length" class="customer-results-empty">
                  Aucun client trouvé. Utilisez <strong>Nouveau client</strong>.
                </div>
              </div>
              <div v-if="selectedCustomer" class="selected-customer-card">
                <div class="selected-customer-main">
                  <strong>{{ selectedCustomer.full_name || `${selectedCustomer.first_name || ''} ${selectedCustomer.last_name || ''}`.trim() }}</strong>
                  <span>{{ selectedCustomer.phone || '-' }}<template v-if="selectedCustomer.email"> • {{ selectedCustomer.email }}</template></span>
                  <span v-if="selectedCustomer.identity_number">{{ customerIdentitySummary(selectedCustomer) }}</span>
                </div>
                <button type="button" class="btn btn-outline btn-sm" @click="clearSelectedCustomer">Changer</button>
              </div>
            </div>

            <div v-if="form.customer_kind === 'individual' && showQuickCustomerForm" class="form-group full quick-customer-card">
              <div class="quick-customer-head">
                <strong>Nouveau client</strong>
                <span>Création rapide en moins de 30 secondes</span>
              </div>
              <div class="form-grid quick-customer-grid">
                <div class="form-group">
                  <label class="form-label">Nom</label>
                  <input v-model="quickCustomerForm.last_name" type="text" class="form-input" placeholder="Nom" />
                </div>
                <div class="form-group">
                  <label class="form-label">Prénom</label>
                  <input v-model="quickCustomerForm.first_name" type="text" class="form-input" placeholder="Prénom" />
                </div>
                <div class="form-group">
                  <label class="form-label">Téléphone</label>
                  <input v-model="quickCustomerForm.phone" type="text" class="form-input" placeholder="Ex: 79 00 00 00" />
                </div>
                <div class="form-group">
                  <label class="form-label">Email</label>
                  <input v-model="quickCustomerForm.email" type="email" class="form-input" placeholder="email@exemple.com" />
                </div>
                <div class="form-group">
                  <label class="form-label">Type de pièce</label>
                  <select v-model="quickCustomerForm.identity_type" class="form-select">
                    <option value="">Sélectionner</option>
                    <option v-for="option in guestIdTypeOptions" :key="`quick-${option.value}`" :value="option.value">{{ option.label }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">ID / Passeport</label>
                  <input v-model="quickCustomerForm.identity_number" type="text" class="form-input" placeholder="Numéro de pièce" />
                </div>
                <div class="form-group full">
                  <label class="form-label">Adresse</label>
                  <input v-model="quickCustomerForm.address" type="text" class="form-input" placeholder="Adresse (optionnel)" />
                </div>
                <div class="form-group full">
                  <label class="form-label">Notes</label>
                  <textarea v-model="quickCustomerForm.notes" class="form-textarea" rows="2" placeholder="Notes utiles (optionnel)"></textarea>
                </div>
              </div>
              <div class="quick-customer-actions">
                <small v-if="form.booking_type === 'room'">Pour une réservation de chambre, la pièce d'identité est obligatoire.</small>
                <button type="button" class="btn btn-primary btn-sm" :class="{ 'is-loading': savingCustomer }" :disabled="savingCustomer" @click="createQuickCustomer">
                  Enregistrer et sélectionner
                </button>
              </div>
            </div>

            <template v-if="form.customer_kind === 'individual'">
              <div class="form-group">
                <label class="form-label">Nom</label>
                <input v-model="form.customer_last_name" type="text" class="form-input" placeholder="Nom" required />
              </div>
              <div class="form-group">
                <label class="form-label">Prénom</label>
                <input v-model="form.customer_first_name" type="text" class="form-input" placeholder="Prénom" required />
              </div>
            </template>
            <template v-else>
              <div class="form-group full">
                <label class="form-label">Nom de l'organisation</label>
                <input v-model="form.organization_name" type="text" class="form-input" placeholder="Nom de l'organisation" required />
              </div>
              <div class="form-group full">
                <label class="form-label">Nom du contact</label>
                <input v-model="form.organization_contact_name" type="text" class="form-input" placeholder="Nom du contact" required />
              </div>
            </template>

            <div class="form-group">
              <label class="form-label">Email</label>
              <input v-model="form.customer_email" type="email" class="form-input" placeholder="email@exemple.com" />
            </div>
            <div class="form-group">
              <label class="form-label">Téléphone</label>
              <input v-model="form.customer_phone" type="text" class="form-input" placeholder="Ex: 79 00 00 00" />
            </div>
          </div>
        </section>

        <section class="booking-form-section">
          <div class="booking-form-section-head">
            <div>
              <span class="booking-form-section-kicker">Étape 2</span>
              <h4>Détails de la réservation</h4>
            </div>
            <p>Choisissez le type de réservation, l’espace concerné et les informations spécifiques au séjour.</p>
          </div>

          <div class="form-grid booking-form-grid">
            <div class="form-group">
              <label class="form-label">Type de réservation</label>
              <select v-model="form.booking_type" class="form-select" @change="onBookingTypeChange">
                <option value="hall">Salle</option>
                <option value="room">Chambre</option>
              </select>
            </div>
            <div v-if="form.booking_type === 'hall'" class="form-group">
              <label class="form-label">Salle</label>
              <select v-model="form.hall" class="form-select" required @change="onItemChange">
                <option v-for="h in halls" :key="h.id" :value="h.id">{{ h.name }}</option>
              </select>
            </div>
            <div v-if="form.booking_type === 'room'" class="form-group full">
              <div class="room-selection-head">
                <label class="form-label">Chambres</label>
                <small>Sélectionnez une ou plusieurs chambres disponibles pour cette même réservation.</small>
              </div>
              <div class="room-selection-grid">
                <label
                  v-for="r in rooms"
                  :key="`room-option-${r.id}`"
                  :class="['room-option-card', { selected: isRoomSelected(r.id), unavailable: isRoomUnavailable(r.id), maintenance: String(r.status || '') === 'maintenance' }]"
                >
                  <input
                    type="checkbox"
                    class="room-option-input"
                    :checked="isRoomSelected(r.id)"
                    :disabled="isRoomUnavailable(r.id)"
                    @change="toggleRoomSelection(r.id)"
                  />
                  <div class="room-option-check" aria-hidden="true">
                    <i class="fas" :class="isRoomSelected(r.id) ? 'fa-check' : 'fa-plus'"></i>
                  </div>
                  <div class="room-option-main">
                    <div class="room-option-top">
                      <strong>{{ r.room_number }} - {{ r.name }}</strong>
                      <span class="room-option-price">{{ formatMoney(r.price_per_night) }}/nuit</span>
                    </div>
                    <div class="room-option-meta">
                      <span class="room-option-type">{{ roomTypeLabel(r.room_type) }}</span>
                      <span :class="['room-option-status', `status-${String(r.status || 'available')}`]">
                        {{ isRoomUnavailable(r.id) ? 'Indisponible' : roomStatusLabel(r.status) }}
                      </span>
                    </div>
                    <small v-if="roomBookedDatesSummary(r.id)" class="room-option-booked-dates">
                      {{ roomBookedDatesSummary(r.id) }}
                    </small>
                    <small>{{ isRoomSelected(r.id) ? 'Chambre sélectionnée pour cette réservation.' : 'Cliquez pour sélectionner cette chambre.' }}</small>
                  </div>
                </label>
              </div>
              <small class="form-hint" v-if="!selectedRoomIds.length">Choisissez au moins une chambre.</small>
              <small class="form-hint" v-else-if="selectedRoomIds.length > 1">Toutes les chambres sélectionnées resteront dans une seule réservation, avec un seul jeton et une seule facture.</small>
            </div>
            <div v-if="form.booking_type === 'room' && selectedRooms.length" class="form-group full room-booking-note">
              <div class="room-booking-note-head">
                <strong>{{ selectedRoomsSummary }}</strong>
                <span class="status-pill">{{ selectedRooms.length }} chambre{{ selectedRooms.length > 1 ? 's' : '' }}</span>
              </div>
              <small v-if="form.customer_kind === 'organization'">Réservation au nom d'une organisation: les personnes hébergées seront enregistrées au check-in pour chaque chambre.</small>
              <small v-else>Pour une chambre, sélectionnez ou créez d'abord le client. Les pièces d'identité seront demandées au check-in, pas pendant la réservation.</small>
            </div>
            <div v-if="form.booking_type === 'hall'" class="form-group">
              <label class="form-label">Type d'événement</label>
              <select v-model="form.event_type" class="form-select" required>
                <option v-for="eventOption in eventTypeOptions" :key="eventOption" :value="eventOption">{{ eventOption }}</option>
              </select>
            </div>
            <div v-if="form.booking_type === 'hall' && isOtherEventType" class="form-group full">
              <label class="form-label">Détails de l'événement</label>
              <textarea
                v-model="form.event_type_other"
                class="form-textarea"
                rows="3"
                required
                placeholder="Précisez le type d'événement"
              ></textarea>
            </div>
            <template v-if="form.booking_type === 'room'">
              <div class="form-group full organization-room-note">
                <strong>Informations voyageurs au check-in</strong>
                <small>Les noms des personnes hébergées ainsi que leurs pièces d'identité seront saisis à l'arrivée, chambre par chambre.</small>
              </div>
              <div v-if="formStayHistory.length" class="form-group full stay-history-card">
                <div class="stay-history-head">
                  <strong>Historique de séjour</strong>
                  <span>{{ formStayHistory.length }} séjour(s)</span>
                </div>
                <div class="stay-history-list compact">
                  <div v-for="stay in formStayHistory" :key="`form-stay-${stay.id}`" class="stay-history-item">
                    <strong>{{ stay.room_display || '-' }}</strong>
                    <span>{{ stay.start_date }} → {{ stay.end_date }}</span>
                    <span>{{ getStatusTranslation(stay.status) }}</span>
                    <span>Check-in: {{ stay.checked_in_at ? formatDateTime(stay.checked_in_at) : 'Non effectué' }}</span>
                    <span>Check-out: {{ stay.checked_out_at ? formatDateTime(stay.checked_out_at) : 'Non effectué' }}</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </section>

        <section class="booking-form-section">
          <div class="booking-form-section-head">
            <div>
              <span class="booking-form-section-kicker">Étape 3</span>
              <h4>Période et montant</h4>
            </div>
            <p>Choisissez les dates, ajoutez les services utiles et validez le total calculé automatiquement.</p>
          </div>

          <div class="form-grid booking-form-grid">
            <div class="form-group full">
              <div class="calendar-top">
                <strong>{{ calendarMonthLabel }}</strong>
                <div class="calendar-nav">
                  <button class="icon-btn" type="button" @click="prevCalendarMonth">
                    <i class="fas fa-chevron-left"></i>
                  </button>
                  <button class="icon-btn" type="button" @click="nextCalendarMonth">
                    <i class="fas fa-chevron-right"></i>
                  </button>
                  <button class="btn btn-outline btn-sm" type="button" @click="clearCalendarDates">
                    Effacer
                  </button>
                </div>
              </div>
              <div class="weekday-row">
                <span v-for="d in calendarWeekdays" :key="d">{{ d }}</span>
              </div>
              <div class="calendar-grid-admin">
                <button
                  v-for="cell in adminCalendarCells"
                  :key="cell.key"
                  class="day-cell"
                  :class="{
                    muted: !cell.currentMonth,
                    disabled: cell.isPast || (!isEditing && cell.isBooked),
                    start: isSameCalendarDate(cell.date, calendarRangeStart),
                    end: isSameCalendarDate(cell.date, calendarRangeEnd),
                    inrange: isCalendarInRange(cell.date, calendarRangeStart, calendarRangeEnd),
                    booked: cell.isBooked
                  }"
                  :disabled="cell.isPast || (!isEditing && cell.isBooked)"
                  type="button"
                  @click="onAdminCalendarDayClick(cell.date)"
                >
                  {{ cell.date.getDate() }}
                </button>
              </div>
              <div class="calendar-legend">
                <span><i class="dot booked"></i> Réservé</span>
                <span><i class="dot selected"></i> Début/Fin</span>
                <span><i class="dot range"></i> Période</span>
              </div>
              <div class="selected-period-card">
                <div class="selected-period-label">Période sélectionnée</div>
                <div class="selected-period-value">{{ selectedPeriodLabel }}</div>
                <div class="selected-period-hint">{{ selectedPeriodHint }}</div>
              </div>
            </div>

            <div v-if="itemAdditionalServices.length" class="form-group full addons-section">
              <div class="addons-head">
                <strong>Services additionnels</strong>
                <span v-if="addonsTotal > 0" class="addons-total">+ {{ formatMoney(addonsTotal) }}</span>
              </div>
              <div class="addons-list">
                <div v-for="service in itemAdditionalServices" :key="service.name" class="addon-item">
                  <div v-if="!service.has_subservices" class="addon-line">
                    <label :class="['addon-toggle', { 'is-active': isServiceSelected(service.name) }]">
                      <input
                        type="checkbox"
                        :checked="isServiceSelected(service.name)"
                        @change="toggleSimpleService(service)"
                      />
                      <span class="toggle-switch" aria-hidden="true">
                        <span class="toggle-knob"></span>
                      </span>
                      <span class="addon-toggle-copy">
                        <strong>{{ service.name }}</strong>
                        <small>{{ isServiceSelected(service.name) ? 'Service ajoute a la reservation.' : 'Activer pour ajouter ce service.' }}</small>
                      </span>
                    </label>
                    <div class="addon-side">
                      <div class="addon-side-top">
                        <strong class="addon-price">{{ formatMoney(service.price) }}</strong>
                        <span class="addon-unit">Par unité</span>
                      </div>
                      <div class="addon-qty-control" :class="{ 'is-disabled': !isServiceSelected(service.name) }" @click.stop>
                        <span class="addon-qty-label">Qté</span>
                        <div class="addon-stepper">
                          <button
                            type="button"
                            class="addon-step-btn"
                            :disabled="!isServiceSelected(service.name) || getServiceQuantity(service.name) <= 1"
                            @click.stop="changeSimpleServiceQuantity(service.name, -1)"
                          >
                            <i class="fas fa-minus"></i>
                          </button>
                          <input
                            :value="getServiceQuantity(service.name)"
                            type="number"
                            min="1"
                            step="1"
                            class="addon-qty-input"
                            :disabled="!isServiceSelected(service.name)"
                            @click.stop
                            @input="updateSimpleServiceQuantity(service.name, $event.target.value)"
                          />
                          <button
                            type="button"
                            class="addon-step-btn"
                            :disabled="!isServiceSelected(service.name)"
                            @click.stop="changeSimpleServiceQuantity(service.name, 1)"
                          >
                            <i class="fas fa-plus"></i>
                          </button>
                        </div>
                      </div>
                      <strong v-if="isServiceSelected(service.name)" class="addon-line-total">Sous-total {{ formatMoney(getServiceLineTotal(service)) }}</strong>
                    </div>
                  </div>
                  <div v-else class="addon-sub-block">
                    <div class="addon-sub-head">
                      <strong>{{ service.name }}</strong>
                      <span class="muted-line">Choisissez les sous-services</span>
                    </div>
                    <div class="addon-subs">
                      <div
                        v-for="sub in (service.subservices || [])"
                        :key="`${service.name}-${sub.name}`"
                        class="addon-sub-row"
                      >
                        <label
                          :class="['addon-toggle', 'addon-sub-line', { 'is-active': isSubserviceSelected(service.name, sub.name) }]"
                        >
                          <input
                            type="checkbox"
                            :checked="isSubserviceSelected(service.name, sub.name)"
                            @change="toggleSubservice(service.name, sub.name)"
                          />
                          <span class="toggle-switch" aria-hidden="true">
                            <span class="toggle-knob"></span>
                          </span>
                          <span class="addon-toggle-copy">
                            <strong>{{ sub.name }}</strong>
                            <small>{{ isSubserviceSelected(service.name, sub.name) ? 'Sous-service selectionne.' : 'Activer pour ajouter ce sous-service.' }}</small>
                          </span>
                        </label>
                        <div class="addon-side">
                          <div class="addon-side-top">
                            <strong class="addon-price">{{ formatMoney(sub.price) }}</strong>
                            <span class="addon-unit">Par unité</span>
                          </div>
                          <div class="addon-qty-control" :class="{ 'is-disabled': !isSubserviceSelected(service.name, sub.name) }" @click.stop>
                            <span class="addon-qty-label">Qté</span>
                            <div class="addon-stepper">
                              <button
                                type="button"
                                class="addon-step-btn"
                                :disabled="!isSubserviceSelected(service.name, sub.name) || getSubserviceQuantity(service.name, sub.name) <= 1"
                                @click.stop="changeSubserviceQuantity(service.name, sub.name, -1)"
                              >
                                <i class="fas fa-minus"></i>
                              </button>
                              <input
                                :value="getSubserviceQuantity(service.name, sub.name)"
                                type="number"
                                min="1"
                                step="1"
                                class="addon-qty-input"
                                :disabled="!isSubserviceSelected(service.name, sub.name)"
                                @click.stop
                                @input="updateSubserviceQuantity(service.name, sub.name, $event.target.value)"
                              />
                              <button
                                type="button"
                                class="addon-step-btn"
                                :disabled="!isSubserviceSelected(service.name, sub.name)"
                                @click.stop="changeSubserviceQuantity(service.name, sub.name, 1)"
                              >
                                <i class="fas fa-plus"></i>
                              </button>
                            </div>
                          </div>
                          <strong v-if="isSubserviceSelected(service.name, sub.name)" class="addon-line-total">Sous-total {{ formatMoney(getSubserviceLineTotal(service.name, sub)) }}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Montant (Fbu)</label>
              <input
                v-model="totalPriceInput"
                inputmode="numeric"
                type="text"
                class="form-input"
                :disabled="!isEditing"
                :readonly="!isEditing"
                required
              />
              <small class="form-hint" v-if="daysCount > 0">{{ daysCount }} {{ form.booking_type === 'hall' ? 'jour(s)' : 'nuit(s)' }} à {{ formatMoney(pricePerUnit) }}/{{ form.booking_type === 'hall' ? 'jour' : 'nuit' }}</small>
              <small class="form-hint" v-if="!isEditing">Montant calcule automatiquement selon la salle et la periode.</small>
            </div>
          </div>
        </section>

        <div class="booking-total-banner booking-total-banner-bottom">
          <div class="booking-total-main">
            <span class="booking-total-label">Résumé du montant</span>
            <strong class="booking-total-value">{{ formatMoney(form.total_price || 0) }}</strong>
            <small class="booking-total-hint">
              Le total se met à jour automatiquement selon la salle, la période et les services ajoutés.
            </small>
          </div>
          <div class="booking-total-meta">
            <div class="booking-total-chip">
              <span class="chip-label">Base</span>
              <strong>{{ formatMoney(baseBookingAmount) }}</strong>
            </div>
            <div class="booking-total-chip">
              <span class="chip-label">Quantité services</span>
              <strong>{{ selectedAddonsCount }} unité{{ selectedAddonsCount > 1 ? 's' : '' }}</strong>
            </div>
            <div class="booking-total-chip">
              <span class="chip-label">Supplément</span>
              <strong>{{ formatMoney(addonsTotal) }}</strong>
            </div>
            <div class="booking-total-chip">
              <span class="chip-label">Durée</span>
              <strong>{{ daysCount > 0 ? `${daysCount} ${form.booking_type === 'room' ? 'nuit(s)' : 'jour(s)'}` : 'Non definie' }}</strong>
            </div>
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingBooking }" :disabled="savingBooking" @click="saveBooking">{{ isEditing ? 'Mettre à jour' : 'Créer' }}</button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de la réservation" width="640px">
      <div v-if="selectedBooking" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ String(selectedBooking.customer_name || 'RE').trim().slice(0, 2).toUpperCase() }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ getBookingDisplayId(selectedBooking) }}</div>
            <h3>{{ selectedBooking.customer_name }}</h3>
            <p>{{ selectedBooking.booking_type === 'hall' ? selectedBooking.hall_name : selectedBooking.room_display }} • {{ selectedBooking.event_type }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', getBadgeClass(selectedBooking.status)]">{{ getStatusTranslation(selectedBooking.status) }}</span>
            <span class="badge badge-info">{{ formatMoney(selectedBooking.total_price) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Réservation</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Email</span><span class="entity-view-value">{{ selectedBooking.customer_email || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Téléphone</span><span class="entity-view-value">{{ selectedBooking.customer_phone || '-' }}</span></div>
              <div v-if="selectedBooking.customer_kind === 'organization'" class="entity-view-item"><span class="entity-view-label">Organisation</span><span class="entity-view-value">{{ selectedBooking.organization_name || selectedBooking.customer_name || '-' }}</span></div>
              <div v-if="selectedBooking.customer_kind === 'organization'" class="entity-view-item"><span class="entity-view-label">Contact</span><span class="entity-view-value">{{ selectedBooking.organization_contact_name || selectedBooking.guest_full_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">{{ selectedBooking.booking_type === 'hall' ? 'Salle' : 'Chambre' }}</span><span class="entity-view-value">{{ selectedBooking.booking_type === 'hall' ? selectedBooking.hall_name : selectedBooking.room_display || 'N/A' }}</span></div>
              <div v-if="selectedBooking.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Statut chambre</span><span class="entity-view-value">{{ roomStatusLabel(selectedBooking.room_status) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Événement</span><span class="entity-view-value">{{ selectedBooking.event_type }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Période</span><span class="entity-view-value">{{ formatDateRange(selectedBooking.start_date, selectedBooking.end_date) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Montant total</span><span class="entity-view-value">{{ formatMoney(selectedBooking.total_price) }}</span></div>
              <div v-if="Number(selectedBooking.addons_total || 0) > 0" class="entity-view-item"><span class="entity-view-label">Services additionnels</span><span class="entity-view-value">{{ formatMoney(selectedBooking.addons_total) }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Suivi administratif</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ getStatusTranslation(selectedBooking.status) }}</span></div>
              <div v-if="selectedBooking.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Client hébergé</span><span class="entity-view-value">{{ selectedBooking.guest_full_name || selectedBooking.customer_name }}</span></div>
              <div v-if="selectedBooking.booking_type === 'room' && selectedBooking.customer_kind !== 'organization'" class="entity-view-item"><span class="entity-view-label">Pièce</span><span class="entity-view-value">{{ guestIdSummary(selectedBooking) }}</span></div>
              <div v-if="selectedBooking.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Check-in</span><span class="entity-view-value">{{ selectedBooking.checked_in_at ? formatDateTime(selectedBooking.checked_in_at) : 'Non effectué' }}</span></div>
              <div v-if="selectedBooking.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Check-out</span><span class="entity-view-value">{{ selectedBooking.checked_out_at ? formatDateTime(selectedBooking.checked_out_at) : 'Non effectué' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé le</span><span class="entity-view-value">{{ formatDisplayDate(selectedBooking.created_at) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedBooking.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedBooking.updated_by_name || selectedBooking.created_by_name || '-' }}</span></div>
            </div>
          </section>

          <section v-if="selectedBooking.booking_type === 'room'" class="entity-view-card entity-view-card-full">
            <div class="entity-view-card-title">Historique de séjour</div>
            <div v-if="!selectedBooking.stay_history?.length" class="entity-view-empty">Aucun séjour précédent trouvé</div>
            <div v-else class="stay-history-list">
              <div v-for="stay in selectedBooking.stay_history" :key="`stay-${stay.id}`" class="stay-history-item">
                <strong>{{ stay.room_display || '-' }}</strong>
                <span>{{ stay.start_date }} → {{ stay.end_date }}</span>
                <span>{{ getStatusTranslation(stay.status) }}</span>
                <span>Check-in: {{ stay.checked_in_at ? formatDateTime(stay.checked_in_at) : 'Non effectué' }}</span>
                <span>Check-out: {{ stay.checked_out_at ? formatDateTime(stay.checked_out_at) : 'Non effectué' }}</span>
              </div>
            </div>
          </section>

          <section v-if="selectedBooking.additional_services_selected?.length" class="entity-view-card entity-view-card-full">
            <div class="entity-view-card-title">Détails services</div>
            <div class="services-preview">
              <div
                v-for="(svc, idx) in selectedBooking.additional_services_selected"
                :key="`${svc.name}-${idx}`"
                class="service-preview-item"
              >
                <div class="service-preview-title">
                  <strong>{{ svc.name }}</strong>
                  <span v-if="!svc.subservices?.length">x{{ addonQuantityValue(svc?.quantity) }}</span>
                </div>
                <div v-if="svc.subservices?.length" class="service-preview-subs">
                  <div v-for="(sub, sidx) in svc.subservices" :key="`${svc.name}-${sidx}`" class="service-preview-sub">
                    <span>{{ sub.name }}</span>
                    <span>x{{ addonQuantityValue(sub?.quantity) }}</span>
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

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer la réservation de <strong>{{ selectedBooking?.customer_name }}</strong> ? Cette action est irréversible.</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingBooking }" :disabled="deletingBooking" @click="deleteBooking">Supprimer</button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useDateFormat } from '~/composables/useDateFormat'
import { useTableSort } from '~/composables/useTableSort'
import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { canDeleteBookings as canDeleteBookingsByRole, canExportAdminExcel, getStoredUser } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const { formatMoney, formatNumberSpaces, moneyInputModel, parseMoney } = useMoney()
const { formatDateRange, formatDisplayDate, formatDateTime } = useDateFormat()
const { escapeHtml } = useDocumentBranding()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName, openPrintPreviewHtml } = useAdminExportDocuments()
const eventTypeOptions = ['Mariage', 'Séminaire', 'Gala', 'Anniversaire', 'Réunion', 'Autres']
const guestIdTypeOptions = [
  { value: 'passport', label: 'Passeport' },
  { value: 'id_card', label: 'Carte d’identité' },
  { value: 'driving_license', label: 'Permis de conduire' },
]

const search = ref('')
const statusFilter = ref('')
const hallFilter = ref('')
const eventTypeFilter = ref('')
const preset = ref('28d')
const customStart = ref('')
const customEnd = ref('')
const minAmount = ref(null)
const maxAmount = ref(null)
const currentUser = ref({})
const canDeleteBookings = computed(() => canDeleteBookingsByRole(currentUser.value))
const canExportExcel = computed(() => canExportAdminExcel(currentUser.value))

const toYmd = (date) => {
  const d = (date instanceof Date) ? date : new Date(date)
  if (Number.isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const addDays = (ymd, days) => {
  const base = new Date(`${ymd}T00:00:00`)
  base.setDate(base.getDate() + days)
  return toYmd(base)
}

const resolvePreset = (value) => {
  const todayYmd = toYmd(new Date())
  if (value === 'all') return { start: '', end: '' }
  if (value === '7d') return { start: addDays(todayYmd, -6), end: todayYmd }
  if (value === '28d') return { start: addDays(todayYmd, -27), end: todayYmd }
  if (value === '90d') return { start: addDays(todayYmd, -89), end: todayYmd }
  if (value === 'year') {
    const now = new Date()
    const start = `${now.getFullYear()}-01-01`
    return { start, end: todayYmd }
  }
  if (value === 'this_month') {
    const now = new Date()
    const start = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
    return { start, end: todayYmd }
  }
  if (value === 'last_month') {
    const now = new Date()
    const firstThisMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const lastPrevMonth = new Date(firstThisMonth)
    lastPrevMonth.setDate(0)
    const startPrevMonth = new Date(lastPrevMonth.getFullYear(), lastPrevMonth.getMonth(), 1)
    return { start: toYmd(startPrevMonth), end: toYmd(lastPrevMonth) }
  }
  if (value === 'custom') {
    const start = String(customStart.value || '').slice(0, 10)
    const end = String(customEnd.value || '').slice(0, 10)
    if (start && end && end >= start) return { start, end }
    return resolvePreset('28d')
  }
  return resolvePreset('28d')
}

const activeRange = computed(() => resolvePreset(preset.value))
const rangeStartYmd = computed(() => activeRange.value.start)
const rangeEndYmd = computed(() => activeRange.value.end)
const activeRangeNotice = computed(() => {
  if (!rangeStartYmd.value || !rangeEndYmd.value) return 'Aucune limite de période sur la date de création.'
  if (preset.value === 'custom') return `Date de création personnalisée: du ${rangeStartYmd.value} au ${rangeEndYmd.value}.`
  return `Date de création calculée jusqu'à aujourd'hui: du ${rangeStartYmd.value} au ${rangeEndYmd.value}.`
})
const inRangeYmd = (ymd, rangeStart, rangeEnd) => {
  const v = String(ymd || '').slice(0, 10)
  if (!rangeStart || !rangeEnd) return true
  if (!v) return false
  return v >= rangeStart && v <= rangeEnd
}
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedBooking = ref(null)
const tableRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const savingBooking = ref(false)
const deletingBooking = ref(false)
const actionBookingId = ref(null)
const actionType = ref('')
const loadingBookings = ref(false)
const loadingHalls = ref(false)
const rooms = ref([])
const loadingRooms = ref(false)
const customers = ref([])
const loadingCustomers = ref(false)
const savingCustomer = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)
const customerSearch = ref('')
const customerResultsOpen = ref(false)
const selectedCustomer = ref(null)
const showQuickCustomerForm = ref(false)
let customerSearchTimer = null

const calendarRanges = ref([])
const calendarViewMonth = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const calendarRangeStart = ref(null)
const calendarRangeEnd = ref(null)
const calendarWeekdays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

const formatCalendarYMD = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
const isSameCalendarDate = (a, b) => !!(a && b && formatCalendarYMD(a) === formatCalendarYMD(b))
const isCalendarInRange = (d, s, e) => !!(s && e && d > s && d < e)

const calendarMonthLabel = computed(() => calendarViewMonth.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }))
const bookedSet = computed(() => {
  const set = new Set()
  for (const r of calendarRanges.value) {
    const start = new Date(r.start_date)
    const end = new Date(r.end_date)
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      set.add(formatCalendarYMD(new Date(d)))
    }
  }
  return set
})

const adminCalendarCells = computed(() => {
  const first = new Date(calendarViewMonth.value.getFullYear(), calendarViewMonth.value.getMonth(), 1)
  const firstWeekday = (first.getDay() + 6) % 7
  const start = new Date(first)
  start.setDate(first.getDate() - firstWeekday)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const ymd = formatCalendarYMD(d)
    return {
      key: `${ymd}-${i}`,
      date: d,
      currentMonth: d.getMonth() === calendarViewMonth.value.getMonth(),
      isPast: d < today,
      isBooked: bookedSet.value.has(ymd),
    }
  })
})

const prevCalendarMonth = () => {
  calendarViewMonth.value = new Date(calendarViewMonth.value.getFullYear(), calendarViewMonth.value.getMonth() - 1, 1)
}

const nextCalendarMonth = () => {
  calendarViewMonth.value = new Date(calendarViewMonth.value.getFullYear(), calendarViewMonth.value.getMonth() + 1, 1)
}

const clearCalendarDates = () => {
  calendarRangeStart.value = null
  calendarRangeEnd.value = null
  form.value.start_date = ''
  form.value.end_date = ''
  daysCount.value = 0
  calculatePrice()
}

const hasCalendarConflict = (start, end) => {
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    if (bookedSet.value.has(formatCalendarYMD(new Date(d)))) return true
  }
  return false
}

const syncFormDatesFromCalendarRange = () => {
  if (!calendarRangeStart.value) return
  const end = calendarRangeEnd.value || calendarRangeStart.value
  form.value.start_date = formatCalendarYMD(calendarRangeStart.value)
  form.value.end_date = formatCalendarYMD(end)
  calculatePrice()
}

const onAdminCalendarDayClick = (date) => {
  if (!calendarRangeStart.value || calendarRangeEnd.value) {
    calendarRangeStart.value = date
    calendarRangeEnd.value = null
    syncFormDatesFromCalendarRange()
    return
  }

  if (date < calendarRangeStart.value) {
    calendarRangeStart.value = date
    calendarRangeEnd.value = null
    syncFormDatesFromCalendarRange()
    return
  }

  if (!isEditing.value && hasCalendarConflict(calendarRangeStart.value, date)) {
    notify('Certaines dates sont déjà réservées pour cette salle.', 'warning')
    return
  }

  calendarRangeEnd.value = date
  syncFormDatesFromCalendarRange()
}

const fetchCalendarRanges = async () => {
  if ((form.value.booking_type === 'hall' && !form.value.hall) || (form.value.booking_type === 'room' && !selectedRoomIds.value.length)) {
    calendarRanges.value = []
    return
  }
  try {
    if (form.value.booking_type === 'hall') {
      const res = await api.get('bookings/calendar/', { params: { hall: form.value.hall } })
      calendarRanges.value = Array.isArray(res.data) ? res.data : []
      return
    }
    const ranges = []
    for (const roomId of selectedRoomIds.value) {
      const res = await api.get('bookings/calendar/', { params: { room: roomId } })
      const items = Array.isArray(res.data) ? res.data : []
      ranges.push(...items)
    }
    calendarRanges.value = ranges
  } catch {
    calendarRanges.value = []
  }
}

const exportXls = async () => {
  if (!canExportExcel.value) {
    notify("L'export Excel n'est pas autorisé pour ce rôle", 'warning')
    return
  }
  if (!tableRef.value) return
  exportingXls.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(tableRef.value, { htmlMode: 'outer', removeActionsColumn: true })
  downloadHtmlAsXls({ type: 'bookings', contentHtml })
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  if (!tableRef.value) return
  exportingPdf.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(tableRef.value, { htmlMode: 'outer', removeActionsColumn: true })
  const html = buildPdfDocumentHtml({
    title: 'Réservations',
    documentTitle: buildExportFileName('bookings', 'pdf').replace(/\.pdf$/, ''),
    subtitle: 'Liste des réservations filtrées exportée depuis l’administration.',
    typeLabel: 'Réservations PDF',
    tableTitle: 'Liste des réservations',
    periodLabel: rangeStartYmd.value && rangeEndYmd.value ? `${rangeStartYmd.value} -> ${rangeEndYmd.value}` : 'Toutes les dates',
    contentHtml,
  })
  const ok = await downloadPdfHtml({ html, fileName: buildExportFileName('bookings', 'pdf') })
  if (!ok) {
    exportingPdf.value = false
    return
  }
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

const createEmptyBookingForm = () => ({
  id: null,
  customer: null,
  customer_kind: 'individual',
  customer_first_name: '',
  customer_last_name: '',
  organization_name: '',
  organization_contact_name: '',
  customer_email: '',
  customer_phone: '',
  booking_type: 'hall',
  hall: '',
  room: '',
  rooms_selected: [],
  guest_full_name: '',
  guest_id_type: 'passport',
  guest_id_number: '',
  event_type: 'Mariage',
  event_type_other: '',
  start_date: '',
  end_date: '',
  additional_services_selected: [],
  total_price: 0,
  status: 'pending'
})
const createEmptyQuickCustomerForm = () => ({
  first_name: '',
  last_name: '',
  phone: '',
  email: '',
  identity_type: '',
  identity_number: '',
  address: '',
  notes: '',
})

const form = ref(createEmptyBookingForm())
const quickCustomerForm = ref(createEmptyQuickCustomerForm())
const isOtherEventType = computed(() => form.value.event_type === 'Autres')
const totalPriceInput = moneyInputModel(form, 'total_price')
const minAmountInput = computed({
  get: () => (minAmount.value === null || minAmount.value === '' ? '' : formatNumberSpaces(minAmount.value)),
  set: (value) => {
    minAmount.value = value === '' ? null : parseMoney(value)
  }
})
const maxAmountInput = computed({
  get: () => (maxAmount.value === null || maxAmount.value === '' ? '' : formatNumberSpaces(maxAmount.value)),
  set: (value) => {
    maxAmount.value = value === '' ? null : parseMoney(value)
  }
})

const bookings = ref([])
const halls = ref([])

const customerSearchResults = computed(() => {
  const selectedId = Number(selectedCustomer.value?.id || 0)
  return (customers.value || []).filter((customer) => Number(customer?.id || 0) !== selectedId)
})

const fetchBookings = async () => {
  loadingBookings.value = true
  try {
    const response = await api.get('bookings/')
    bookings.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement des réservations', 'danger')
  } finally {
    loadingBookings.value = false
  }
}

const fetchHalls = async () => {
  loadingHalls.value = true
  try {
    const response = await api.get('halls/')
    halls.value = response.data
    if (halls.value.length > 0 && !form.value.hall) {
      form.value.hall = halls.value[0].id
    }
  } catch (error) {
    notify('Erreur lors du chargement des salles', 'danger')
  } finally {
    loadingHalls.value = false
  }
}

const fetchRooms = async () => {
  loadingRooms.value = true
  try {
    const response = await api.get('rooms/')
    rooms.value = response.data
    if (rooms.value.length > 0 && !form.value.room && form.value.booking_type === 'room') {
      form.value.room = rooms.value[0].id
      form.value.rooms_selected = [rooms.value[0].id]
    }
  } catch (error) {
    notify('Erreur lors du chargement des chambres', 'danger')
  } finally {
    loadingRooms.value = false
  }
}

const fetchCustomers = async (searchTerm = '') => {
  loadingCustomers.value = true
  try {
    const params = { limit: searchTerm ? 8 : 6 }
    if (searchTerm) params.search = searchTerm
    const response = await api.get('customers/', { params })
    customers.value = Array.isArray(response.data) ? response.data : []
  } catch {
    customers.value = []
  } finally {
    loadingCustomers.value = false
  }
}

const updateResponsiveState = () => {
  if (!process.client) return
  const nextIsMobile = window.innerWidth <= 992
  if (nextIsMobile !== isMobile.value) {
    isMobile.value = nextIsMobile
    filtersOpen.value = !nextIsMobile
  } else {
    isMobile.value = nextIsMobile
  }
}

const closeActionsOnDocumentClick = () => {
  openActionsId.value = null
  customerResultsOpen.value = false
}

const openBookingFromQuery = () => {
  const viewId = Number(route.query.view)
  if (!viewId) return
  const booking = bookings.value.find(item => Number(item?.id) === viewId)
  if (!booking) return
  selectedBooking.value = booking
  showViewModal.value = true
}

watch(() => `${route.query.view || ''}:${route.query.focus || ''}:${bookings.value.length}`, () => {
  openBookingFromQuery()
})

watch(customerSearch, (value) => {
  if (!showFormModal.value) return
  customerResultsOpen.value = true
  if (customerSearchTimer) {
    clearTimeout(customerSearchTimer)
  }
  customerSearchTimer = setTimeout(() => {
    fetchCustomers(String(value || '').trim())
  }, 180)
})

onMounted(async () => {
  currentUser.value = getStoredUser()
  await Promise.all([fetchBookings(), fetchHalls(), fetchRooms(), fetchCustomers()])
  openBookingFromQuery()
  if (process.client) {
    updateResponsiveState()
    window.addEventListener('resize', updateResponsiveState)
    document.addEventListener('click', closeActionsOnDocumentClick)
  }
})

onBeforeUnmount(() => {
  if (!process.client) return
  window.removeEventListener('resize', updateResponsiveState)
  document.removeEventListener('click', closeActionsOnDocumentClick)
  if (customerSearchTimer) {
    window.clearTimeout(customerSearchTimer)
    customerSearchTimer = null
  }
})

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const resetFilters = () => {
  search.value = ''
  statusFilter.value = ''
  hallFilter.value = ''
  eventTypeFilter.value = ''
  preset.value = '28d'
  customStart.value = ''
  customEnd.value = ''
  minAmount.value = null
  maxAmount.value = null
}

const pricePerUnit = ref(0)
const daysCount = ref(0)

const selectedHall = computed(() => halls.value.find(h => String(h.id) === String(form.value.hall)) || null)
const selectedRoomIds = computed(() => {
  const ids = Array.isArray(form.value.rooms_selected) ? form.value.rooms_selected : []
  const normalized = ids
    .map(id => String(id || '').trim())
    .filter(Boolean)
  return Array.from(new Set(normalized))
})
const selectedRooms = computed(() => rooms.value.filter(r => selectedRoomIds.value.includes(String(r.id))))
const selectedRoom = computed(() => rooms.value.find(r => String(r.id) === String(form.value.room)) || null)
const selectedItem = computed(() => form.value.booking_type === 'hall' ? selectedHall.value : selectedRoom.value)
const normalizeAddonQuantity = (value) => {
  const quantity = Number.parseInt(String(value ?? '').trim(), 10)
  return Number.isFinite(quantity) && quantity > 0 ? quantity : 1
}
const addonQuantityValue = (value) => normalizeAddonQuantity(value)
const normalizeAdditionalServicesSelection = (value) => {
  if (!Array.isArray(value)) return []
  return value
    .filter(item => item && typeof item === 'object')
    .map((item) => {
      const normalized = {
        name: String(item?.name || '').trim(),
        quantity: normalizeAddonQuantity(item?.quantity),
      }
      const subs = Array.isArray(item?.subservices)
        ? item.subservices
          .filter(sub => sub && typeof sub === 'object')
          .map(sub => ({
            name: String(sub?.name || '').trim(),
            quantity: normalizeAddonQuantity(sub?.quantity),
          }))
          .filter(sub => sub.name)
        : []
      if (subs.length) normalized.subservices = subs
      return normalized
    })
    .filter(item => item.name)
}
const itemAdditionalServices = computed(() => {
  if (form.value.booking_type === 'room' && selectedRooms.value.length !== 1) return []
  return Array.isArray(selectedItem.value?.additional_services) ? selectedItem.value.additional_services : []
})
const customerFullName = computed(() => `${String(form.value.customer_first_name || '').trim()} ${String(form.value.customer_last_name || '').trim()}`.trim())
const organizationContactName = computed(() => String(form.value.organization_contact_name || '').trim())
const activeGuestName = computed(() => (
  form.value.booking_type === 'room'
    ? (form.value.customer_kind === 'organization' ? organizationContactName.value : customerFullName.value)
    : ''
))
const selectedRoomsSummary = computed(() => (
  selectedRooms.value
    .map(room => `${room.room_number} - ${room.name}`)
    .join(', ')
))
const selectedPeriodLabel = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 'Aucune période sélectionnée'
  return formatDateRange(form.value.start_date, form.value.end_date)
})
const selectedPeriodHint = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 'Choisissez la période directement dans le calendrier.'
  const durationLabel = `${daysCount.value || 0} ${form.value.booking_type === 'room' ? 'nuit(s)' : 'jour(s)'} sélectionné(s)`
  if (form.value.booking_type === 'room' && selectedRoomIds.value.length > 1) {
    return `${durationLabel} pour ${selectedRoomIds.value.length} chambres`
  }
  return durationLabel
})
const roomTypeLabel = (roomType) => ({
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
}[String(roomType || '')] || String(roomType || ''))
const roomStatusLabel = (status) => ({
  available: 'Disponible',
  reserved: 'Réservée',
  occupied: 'Occupée',
  cleaning: 'Nettoyage',
  maintenance: 'Maintenance',
}[String(status || 'available')] || String(status || 'available'))
const customerIdentitySummary = (customer) => {
  const type = String(customer?.identity_type || '').trim()
  const number = String(customer?.identity_number || '').trim()
  if (!type && !number) return '-'
  const label = guestIdTypeOptions.find(option => option.value === type)?.label || type || 'Pièce'
  return [label, number].filter(Boolean).join(' • ')
}
const roomAvailabilityMap = computed(() => {
  const map = new Map()
  const start = String(form.value.start_date || '').slice(0, 10)
  const end = String(form.value.end_date || '').slice(0, 10)
  for (const room of rooms.value) {
    const roomId = String(room?.id || '')
    const unavailable = String(room?.status || '') === 'maintenance' || bookings.value.some((booking) => {
      if (booking.booking_type !== 'room' || String(booking.status || '') === 'cancelled') return false
      if (Number(booking.id) === Number(form.value.id || 0)) return false
      const bookingRoomIds = Array.isArray(booking.room_ids)
        ? booking.room_ids.map(id => String(id || '').trim()).filter(Boolean)
        : (booking.room ? [String(booking.room)] : [])
      if (!bookingRoomIds.includes(roomId)) return false
      if (!start || !end) return false
      const bookingStart = String(booking.start_date || '').slice(0, 10)
      const bookingEnd = String(booking.end_date || '').slice(0, 10)
      return Boolean(bookingStart && bookingEnd && bookingStart <= end && bookingEnd >= start)
    })
    map.set(roomId, unavailable)
  }
  return map
})
const roomBookingConflictsMap = computed(() => {
  const map = new Map()
  const start = String(form.value.start_date || '').slice(0, 10)
  const end = String(form.value.end_date || '').slice(0, 10)
  for (const room of rooms.value) {
    const roomId = String(room?.id || '')
    const conflicts = bookings.value.filter((booking) => {
      if (booking.booking_type !== 'room' || String(booking.status || '') === 'cancelled') return false
      if (Number(booking.id) === Number(form.value.id || 0)) return false
      const bookingRoomIds = Array.isArray(booking.room_ids)
        ? booking.room_ids.map(id => String(id || '').trim()).filter(Boolean)
        : (booking.room ? [String(booking.room)] : [])
      if (!bookingRoomIds.includes(roomId)) return false
      const bookingStart = String(booking.start_date || '').slice(0, 10)
      const bookingEnd = String(booking.end_date || '').slice(0, 10)
      if (!bookingStart || !bookingEnd) return false
      if (start && end) return bookingStart <= end && bookingEnd >= start
      return true
    }).map((booking) => ({
      id: booking.id,
      start_date: String(booking.start_date || '').slice(0, 10),
      end_date: String(booking.end_date || '').slice(0, 10),
      status: String(booking.status || ''),
      code: booking.code || '',
    }))
    map.set(roomId, conflicts)
  }
  return map
})
const isRoomUnavailable = (roomId) => Boolean(roomAvailabilityMap.value.get(String(roomId || '')))
const isRoomSelected = (roomId) => selectedRoomIds.value.includes(String(roomId || ''))
const roomBookingConflicts = (roomId) => roomBookingConflictsMap.value.get(String(roomId || '')) || []
const roomBookedDatesSummary = (roomId) => {
  const conflicts = roomBookingConflicts(roomId)
  if (!conflicts.length) return ''
  const [firstConflict] = conflicts
  const hasSelectedPeriod = Boolean(String(form.value.start_date || '').slice(0, 10) && String(form.value.end_date || '').slice(0, 10))
  const firstLabel = `${hasSelectedPeriod ? 'Déjà réservée' : 'Réservée'} du ${firstConflict.start_date} au ${firstConflict.end_date}`
  if (conflicts.length === 1) return firstLabel
  return `${firstLabel} • +${conflicts.length - 1} autre(s) période(s)`
}
const pruneUnavailableSelectedRooms = () => {
  if (form.value.booking_type !== 'room') return
  const next = selectedRoomIds.value.filter(roomId => !isRoomUnavailable(roomId))
  if (next.length === selectedRoomIds.value.length) return
  form.value.rooms_selected = next
  syncPrimaryRoomSelection()
  if (selectedRoomIds.value.length !== 1) {
    form.value.additional_services_selected = []
  }
}
const baseBookingAmount = computed(() => Number(daysCount.value || 0) * Number(pricePerUnit.value || 0))
const selectedAddonsCount = computed(() => {
  const selected = normalizeAdditionalServicesSelection(form.value.additional_services_selected)
  let count = 0
  for (const item of selected) {
    const subs = Array.isArray(item?.subservices) ? item.subservices : []
    count += subs.length > 0
      ? subs.reduce((sum, sub) => sum + addonQuantityValue(sub?.quantity), 0)
      : addonQuantityValue(item?.quantity)
  }
  return count
})

const addonsTotal = computed(() => {
  const services = itemAdditionalServices.value
  const selected = normalizeAdditionalServicesSelection(form.value.additional_services_selected)
  if (!services.length || !selected.length) return 0

  const serviceIndex = new Map(services.map(s => [String(s?.name || ''), s]))
  let total = 0
  for (const item of selected) {
    const name = String(item?.name || '')
    const cfg = serviceIndex.get(name)
    if (!cfg) continue
    if (cfg.has_subservices) {
      const subs = Array.isArray(item?.subservices) ? item.subservices : []
      const subIndex = new Map((cfg.subservices || []).map(sub => [String(sub?.name || ''), Number(sub?.price || 0)]))
      for (const sub of subs) {
        total += (subIndex.get(String(sub?.name || '')) || 0) * addonQuantityValue(sub?.quantity)
      }
      continue
    }
    total += Number(cfg.price || 0) * addonQuantityValue(item?.quantity)
  }
  return total
})

const syncPrimaryRoomSelection = () => {
  if (form.value.booking_type !== 'room') {
    form.value.room = ''
    form.value.rooms_selected = []
    return
  }
  const normalized = selectedRoomIds.value
  form.value.rooms_selected = normalized
  form.value.room = normalized[0] || ''
}

const toggleRoomSelection = (roomId) => {
  const roomKey = String(roomId || '')
  if (!roomKey || isRoomUnavailable(roomKey)) return
  const next = [...selectedRoomIds.value]
  const index = next.indexOf(roomKey)
  if (index >= 0) {
    next.splice(index, 1)
  } else {
    next.push(roomKey)
  }
  form.value.rooms_selected = next
  syncPrimaryRoomSelection()
  if (selectedRoomIds.value.length !== 1) {
    form.value.additional_services_selected = []
  }
  fetchCalendarRanges()
  calculatePrice()
}

const onCustomerKindChange = () => {
  if (form.value.customer_kind === 'organization') {
    resetQuickCustomerState()
    form.value.customer = null
    form.value.customer_first_name = ''
    form.value.customer_last_name = ''
  } else {
    form.value.organization_name = ''
    form.value.organization_contact_name = ''
  }
  calculatePrice()
}

const onBookingTypeChange = () => {
  clearCalendarDates()
  form.value.hall = null
  form.value.room = null
  form.value.rooms_selected = []
  form.value.additional_services_selected = []
  form.value.event_type_other = ''
  form.value.event_type = form.value.booking_type === 'room' ? 'Séjour' : 'Mariage'
  if (form.value.booking_type === 'hall' && halls.value.length > 0) {
    form.value.hall = halls.value[0].id
  } else if (form.value.booking_type === 'room' && rooms.value.length > 0) {
    form.value.room = rooms.value[0].id
    form.value.rooms_selected = [String(rooms.value[0].id)]
  }
  if (form.value.booking_type === 'hall') {
    form.value.guest_id_type = ''
    form.value.guest_id_number = ''
  }
  fetchCalendarRanges()
  calculatePrice()
}

const onItemChange = () => {
  form.value.additional_services_selected = []
  clearCalendarDates()
  fetchCalendarRanges()
  calculatePrice()
}

const calculatePrice = () => {
  if (!form.value.start_date || !form.value.end_date) {
    daysCount.value = 0
    pricePerUnit.value = 0
    form.value.total_price = Number(addonsTotal.value || 0)
    return
  }

  const start = new Date(form.value.start_date)
  const end = new Date(form.value.end_date)
  const diffTime = Math.abs(end - start)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
  daysCount.value = diffDays

  if (form.value.booking_type === 'hall') {
    const hallPrice = Number(selectedHall.value?.price_per_day || 0)
    pricePerUnit.value = hallPrice
    form.value.total_price = (diffDays * hallPrice) + Number(addonsTotal.value || 0)
    return
  }

  const totalRoomRate = selectedRooms.value.reduce((sum, room) => sum + Number(room?.price_per_night || 0), 0)
  const singleRoomRate = Number(selectedRoom.value?.price_per_night || 0)
  pricePerUnit.value = selectedRooms.value.length > 1 ? totalRoomRate : singleRoomRate
  const baseTotal = diffDays * totalRoomRate
  const addons = selectedRooms.value.length === 1 ? Number(addonsTotal.value || 0) : 0
  form.value.total_price = baseTotal + addons
}

watch(
  () => form.value.additional_services_selected,
  () => calculatePrice(),
  { deep: true }
)

watch(
  () => form.value.hall,
  async (nextHall, prevHall) => {
    if (!showFormModal.value) return
    await fetchCalendarRanges()
    if (!isEditing.value && String(nextHall || '') !== String(prevHall || '')) {
      clearCalendarDates()
    }
    if (String(nextHall || '') !== String(prevHall || '')) {
      form.value.additional_services_selected = []
    }
    calculatePrice()
  }
)

watch(
  () => form.value.rooms_selected,
  () => {
    if (!showFormModal.value || form.value.booking_type !== 'room') return
    syncPrimaryRoomSelection()
    if (selectedRoomIds.value.length !== 1) {
      form.value.additional_services_selected = []
    }
    fetchCalendarRanges()
    calculatePrice()
  },
  { deep: true }
)

watch(
  () => `${form.value.booking_type}:${String(form.value.start_date || '')}:${String(form.value.end_date || '')}:${bookings.value.length}`,
  () => {
    if (!showFormModal.value || form.value.booking_type !== 'room') return
    pruneUnavailableSelectedRooms()
    calculatePrice()
  }
)

const isServiceSelected = (serviceName) => {
  return (form.value.additional_services_selected || []).some(s => String(s?.name || '') === String(serviceName || ''))
}

const toggleSimpleService = (service) => {
  const name = String(service?.name || '').trim()
  if (!name) return
  const selected = Array.isArray(form.value.additional_services_selected) ? [...form.value.additional_services_selected] : []
  const idx = selected.findIndex(s => String(s?.name || '') === name)
  if (idx >= 0) {
    selected.splice(idx, 1)
  } else {
    selected.push({ name, quantity: 1 })
  }
  form.value.additional_services_selected = selected
}

const getServiceQuantity = (serviceName) => {
  const item = (form.value.additional_services_selected || []).find(s => String(s?.name || '') === String(serviceName || ''))
  return addonQuantityValue(item?.quantity)
}

const updateSimpleServiceQuantity = (serviceName, value) => {
  const name = String(serviceName || '').trim()
  if (!name) return
  const selected = Array.isArray(form.value.additional_services_selected) ? [...form.value.additional_services_selected] : []
  const item = selected.find(s => String(s?.name || '') === name)
  if (!item) return
  item.quantity = normalizeAddonQuantity(value)
  form.value.additional_services_selected = selected
}

const changeSimpleServiceQuantity = (serviceName, delta) => {
  const next = getServiceQuantity(serviceName) + Number(delta || 0)
  updateSimpleServiceQuantity(serviceName, Math.max(1, next))
}

const isSubserviceSelected = (serviceName, subName) => {
  const item = (form.value.additional_services_selected || []).find(s => String(s?.name || '') === String(serviceName || ''))
  const subs = Array.isArray(item?.subservices) ? item.subservices : []
  return subs.some(sub => String(sub?.name || '') === String(subName || ''))
}

const toggleSubservice = (serviceName, subName) => {
  const name = String(serviceName || '').trim()
  const sub = String(subName || '').trim()
  if (!name || !sub) return
  const selected = Array.isArray(form.value.additional_services_selected) ? [...form.value.additional_services_selected] : []
  let item = selected.find(s => String(s?.name || '') === name)
  if (!item) {
    item = { name, quantity: 1, subservices: [{ name: sub, quantity: 1 }] }
    selected.push(item)
    form.value.additional_services_selected = selected
    return
  }
  const subs = Array.isArray(item.subservices) ? [...item.subservices] : []
  const idx = subs.findIndex(s => String(s?.name || '') === sub)
  if (idx >= 0) {
    subs.splice(idx, 1)
  } else {
    subs.push({ name: sub, quantity: 1 })
  }
  if (subs.length === 0) {
    form.value.additional_services_selected = selected.filter(s => String(s?.name || '') !== name)
  } else {
    item.subservices = subs
    form.value.additional_services_selected = selected
  }
}

const getSubserviceQuantity = (serviceName, subName) => {
  const item = (form.value.additional_services_selected || []).find(s => String(s?.name || '') === String(serviceName || ''))
  const sub = (Array.isArray(item?.subservices) ? item.subservices : []).find(s => String(s?.name || '') === String(subName || ''))
  return addonQuantityValue(sub?.quantity)
}

const updateSubserviceQuantity = (serviceName, subName, value) => {
  const name = String(serviceName || '').trim()
  const sub = String(subName || '').trim()
  if (!name || !sub) return
  const selected = Array.isArray(form.value.additional_services_selected) ? [...form.value.additional_services_selected] : []
  const item = selected.find(s => String(s?.name || '') === name)
  if (!item) return
  const subs = Array.isArray(item.subservices) ? [...item.subservices] : []
  const target = subs.find(s => String(s?.name || '') === sub)
  if (!target) return
  target.quantity = normalizeAddonQuantity(value)
  item.subservices = subs
  form.value.additional_services_selected = selected
}

const changeSubserviceQuantity = (serviceName, subName, delta) => {
  const next = getSubserviceQuantity(serviceName, subName) + Number(delta || 0)
  updateSubserviceQuantity(serviceName, subName, Math.max(1, next))
}

const getServiceLineTotal = (service) => Number(service?.price || 0) * getServiceQuantity(service?.name)
const getSubserviceLineTotal = (serviceName, sub) => Number(sub?.price || 0) * getSubserviceQuantity(serviceName, sub?.name)

const resetQuickCustomerState = () => {
  customerSearch.value = ''
  customerResultsOpen.value = false
  selectedCustomer.value = null
  showQuickCustomerForm.value = false
  quickCustomerForm.value = createEmptyQuickCustomerForm()
}

const syncQuickCustomerFormFromBooking = () => {
  quickCustomerForm.value = {
    ...createEmptyQuickCustomerForm(),
    first_name: String(form.value.customer_first_name || '').trim(),
    last_name: String(form.value.customer_last_name || '').trim(),
    phone: String(form.value.customer_phone || '').trim(),
    email: String(form.value.customer_email || '').trim(),
    identity_type: String(form.value.guest_id_type || '').trim(),
    identity_number: String(form.value.guest_id_number || '').trim(),
  }
}

const openCustomerResults = async () => {
  customerResultsOpen.value = true
  await fetchCustomers(String(customerSearch.value || '').trim())
}

const selectCustomer = (customer) => {
  if (!customer) return
  selectedCustomer.value = customer
  form.value.customer_kind = 'individual'
  form.value.customer = customer.id
  form.value.customer_first_name = String(customer.first_name || '').trim()
  form.value.customer_last_name = String(customer.last_name || '').trim()
  form.value.customer_phone = String(customer.phone || '').trim()
  form.value.customer_email = String(customer.email || '').trim()
  if (form.value.booking_type === 'room') {
    form.value.guest_id_type = String(customer.identity_type || form.value.guest_id_type || 'passport').trim()
    form.value.guest_id_number = String(customer.identity_number || '').trim()
  }
  customerSearch.value = customer.full_name || `${customer.first_name || ''} ${customer.last_name || ''}`.trim() || customer.phone || ''
  customerResultsOpen.value = false
  showQuickCustomerForm.value = false
}

const clearSelectedCustomer = () => {
  selectedCustomer.value = null
  form.value.customer = null
  customerSearch.value = ''
  customerResultsOpen.value = true
}

const toggleQuickCustomerForm = () => {
  showQuickCustomerForm.value = !showQuickCustomerForm.value
  if (showQuickCustomerForm.value) {
    syncQuickCustomerFormFromBooking()
  }
}

const createQuickCustomer = async () => {
  if (savingCustomer.value) return
  if (!String(quickCustomerForm.value.first_name || '').trim() && !String(quickCustomerForm.value.last_name || '').trim()) {
    notify('Le nom du client est requis', 'warning')
    return
  }
  if (!String(quickCustomerForm.value.phone || '').trim()) {
    notify('Le téléphone du client est requis', 'warning')
    return
  }
  if (form.value.booking_type === 'room' && (!String(quickCustomerForm.value.identity_type || '').trim() || !String(quickCustomerForm.value.identity_number || '').trim())) {
    notify('Pour une chambre, la pièce d’identité du client est obligatoire', 'warning')
    return
  }

  savingCustomer.value = true
  try {
    const payload = {
      first_name: String(quickCustomerForm.value.first_name || '').trim(),
      last_name: String(quickCustomerForm.value.last_name || '').trim(),
      phone: String(quickCustomerForm.value.phone || '').trim(),
      email: String(quickCustomerForm.value.email || '').trim(),
      identity_type: String(quickCustomerForm.value.identity_type || '').trim(),
      identity_number: String(quickCustomerForm.value.identity_number || '').trim(),
      address: String(quickCustomerForm.value.address || '').trim(),
      notes: String(quickCustomerForm.value.notes || '').trim(),
    }
    const response = await api.post('customers/', payload)
    const createdCustomer = response?.data || null
    if (createdCustomer) {
      customers.value = [createdCustomer, ...customers.value.filter(item => Number(item?.id) !== Number(createdCustomer.id))]
      selectCustomer(createdCustomer)
      notify('Client créé et sélectionné', 'success')
    }
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.phone || data.first_name || data.detail || 'Impossible de créer le client', 'danger')
  } finally {
    savingCustomer.value = false
  }
}

const filteredBookings = computed(() => {
  return bookings.value.filter(b => {
    const q = search.value.toLowerCase().trim()
    const matchesSearch = q === '' ||
      String(b.customer_name || '').toLowerCase().includes(q) ||
      String(b.customer_email || '').toLowerCase().includes(q) ||
      String(b.hall_name || '').toLowerCase().includes(q) ||
      String(b.room_display || '').toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || b.status === statusFilter.value
    const matchesType = hallFilter.value === '' || (
      (hallFilter.value === 'hall' && b.booking_type === 'hall') || (hallFilter.value === 'room' && b.booking_type === 'room')
    )
    const matchesEventType = eventTypeFilter.value === '' || (eventTypeFilter.value === 'Autres'
      ? String(b.event_type || '').startsWith('Autres: ')
      : b.event_type === eventTypeFilter.value)

    const matchesDate = inRangeYmd(b.created_at, rangeStartYmd.value, rangeEndYmd.value)

    const amount = Number(b.total_price || 0)
    const minOk = minAmount.value == null || minAmount.value === '' || amount >= Number(minAmount.value)
    const maxOk = maxAmount.value == null || maxAmount.value === '' || amount <= Number(maxAmount.value)

    return matchesSearch && matchesStatus && matchesType && matchesEventType && matchesDate && minOk && maxOk
  })
})
const formStayHistory = computed(() => {
  if (form.value.booking_type !== 'room') return []
  const guestName = activeGuestName.value.toLowerCase()
  const guestIdNumber = String(form.value.guest_id_number || '').trim().toLowerCase()
  const customerEmail = String(form.value.customer_email || '').trim().toLowerCase()
  return bookings.value
    .filter((booking) => {
      if (booking.booking_type !== 'room') return false
      if (Number(booking.id) === Number(form.value.id || 0)) return false
      const sameId = guestIdNumber && String(booking.guest_id_number || '').trim().toLowerCase() === guestIdNumber
      const sameGuest = guestName && String(booking.guest_full_name || '').trim().toLowerCase() === guestName
      const sameEmail = customerEmail && String(booking.customer_email || '').trim().toLowerCase() === customerEmail
      return sameId || sameGuest || sameEmail
    })
    .slice()
    .sort((a, b) => new Date(b.start_date || 0) - new Date(a.start_date || 0))
    .slice(0, 5)
    .map(booking => ({
      id: booking.id,
      room_display: booking.room_display,
      start_date: booking.start_date,
      end_date: booking.end_date,
      status: booking.status,
      checked_in_at: booking.checked_in_at,
      checked_out_at: booking.checked_out_at,
    }))
})

const {
  sortedItems: sortedBookings,
  toggleSort: toggleBookingSort,
  isSortActive: isBookingSortActive,
  sortIconClass: bookingSortIconClass,
} = useTableSort(filteredBookings, {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    total_price: booking => Number(booking?.total_price || 0),
  },
})

const getBookingDisplayId = (booking) => booking?.code || 'LBR00000001'
const guestIdSummary = (booking) => {
  const type = String(booking?.guest_id_type || '').trim()
  const number = String(booking?.guest_id_number || '').trim()
  if (!type && !number) return '-'
  const label = guestIdTypeOptions.find(option => option.value === type)?.label || type || 'Pièce'
  return [label, number].filter(Boolean).join(' • ')
}
const extractApiErrorMessage = (payload) => {
  if (!payload) return ''
  if (typeof payload === 'string') return payload
  if (Array.isArray(payload)) {
    for (const item of payload) {
      const message = extractApiErrorMessage(item)
      if (message) return message
    }
    return ''
  }
  if (typeof payload === 'object') {
    for (const value of Object.values(payload)) {
      const message = extractApiErrorMessage(value)
      if (message) return message
    }
  }
  return ''
}

const {
  paginatedItems: paginatedBookings,
  totalItems: bookingsTotalItems,
  startIndex: bookingsStartIndex,
  endIndex: bookingsEndIndex,
  canPrev: bookingsCanPrev,
  canNext: bookingsCanNext,
  prevPage: bookingsPrevPage,
  nextPage: bookingsNextPage,
} = usePagination(sortedBookings, 50)

const saveBooking = async () => {
  savingBooking.value = true
  const previewWindow = !isEditing.value && process.client
    ? window.open('', '_blank', 'width=1180,height=920')
    : null
  if (previewWindow && !previewWindow.closed) {
    try {
      previewWindow.document.open('text/html', 'replace')
      previewWindow.document.write(`<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Préparation du jeton</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      font-family: Arial, sans-serif;
      background: #f8fafc;
      color: #0f172a;
    }
    .preview-loading {
      width: min(520px, 100%);
      padding: 28px;
      border-radius: 24px;
      border: 1px solid #dbe3ee;
      background: #ffffff;
      box-shadow: 0 24px 50px rgba(15, 23, 42, 0.1);
      text-align: center;
    }
    .preview-loading strong {
      display: block;
      font-size: 1.15rem;
      margin-bottom: 10px;
    }
    .preview-loading span {
      color: #64748b;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="preview-loading">
    <strong>Préparation du jeton...</strong>
    <span>La fenêtre d’aperçu reste ouverte pendant l’enregistrement de la réservation.</span>
  </div>
</body>
</html>`)
      previewWindow.document.close()
    } catch {}
  }
  try {
    const payload = buildBookingPayload()
    if (form.value.booking_type === 'room' && !selectedRoomIds.value.length) {
      if (previewWindow && !previewWindow.closed) previewWindow.close()
      notify('Complétez les informations de réservation avant de continuer', 'warning')
      return
    }
    if (isEditing.value) {
      await api.put(`bookings/${form.value.id}/`, payload)
      notify('Réservation mise à jour avec succès', 'success')
    } else {
      if (form.value.booking_type === 'room') {
        const unavailable = selectedRooms.value.filter(room => isRoomUnavailable(room.id))
        if (unavailable.length) {
          if (previewWindow && !previewWindow.closed) previewWindow.close()
          notify(`Ces chambres ne sont plus disponibles: ${unavailable.map(room => room.room_number).join(', ')}`, 'warning')
          return
        }
      }
      const response = await api.post('bookings/', payload)
      await fetchBookings()
      const createdBooking = bookings.value.find(booking => booking.id === response.data?.id) || response.data
      if (form.value.booking_type === 'room' && selectedRoomIds.value.length > 1) {
        notify(`Réservation multi-chambres créée avec succès (${selectedRoomIds.value.length} chambres)`, 'success')
      } else if (payload.customer_email) {
        notify(response.data?.email_sent ? 'Nouvelle réservation créée et email envoyé' : 'Nouvelle réservation créée, mais email non envoyé', response.data?.email_sent ? 'success' : 'warning')
      } else {
        notify('Nouvelle réservation créée', 'success')
      }
      if (createdBooking) {
        openReservationJetonPrintPreview(createdBooking, Boolean(response.data?.email_sent), previewWindow)
      } else if (previewWindow && !previewWindow.closed) {
        previewWindow.close()
      }
    }
    showFormModal.value = false
    if (isEditing.value) {
      fetchBookings()
    }
  } catch (error) {
    if (previewWindow && !previewWindow.closed) previewWindow.close()
    const data = error?.response?.data || {}
    notify(extractApiErrorMessage(data) || 'Erreur lors de l\'enregistrement', 'danger')
  } finally {
    savingBooking.value = false
  }
}

const deleteBooking = async () => {
  if (!selectedBooking.value?.id) return
  if (!canDeleteBookings.value) {
    notify('Ce role ne peut pas supprimer une reservation', 'warning')
    showDeleteModal.value = false
    return
  }
  deletingBooking.value = true
  try {
    await api.delete(`bookings/${selectedBooking.value.id}/`)
    notify('Réservation supprimée', 'danger')
    showDeleteModal.value = false
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingBooking.value = false
  }
}

const approve = async (booking) => {
  if (!booking?.id) return
  closeActions()
  actionBookingId.value = booking.id
  actionType.value = 'approve'
  try {
    await api.patch(`bookings/${booking.id}/`, { status: 'confirmed' })
    notify(`Réservation de ${booking.customer_name} approuvée`, 'success')
    fetchBookings()
  } catch (error) {
    notify('Erreur lors de l\'approbation', 'danger')
  } finally {
    actionBookingId.value = null
    actionType.value = ''
  }
}

const reject = async (booking) => {
  if (!booking?.id) return
  closeActions()
  actionBookingId.value = booking.id
  actionType.value = 'reject'
  try {
    await api.patch(`bookings/${booking.id}/`, { status: 'cancelled' })
    notify(`Réservation de ${booking.customer_name} rejetée`, 'warning')
    fetchBookings()
  } catch (error) {
    notify('Erreur lors du rejet', 'danger')
  } finally {
    actionBookingId.value = null
    actionType.value = ''
  }
}

const getStatusTranslation = (status) => {
  const map = {
    pending: 'En attente',
    confirmed: 'Confirmé',
    paid: 'Payé',
    cancelled: 'Annulé'
  }
  return map[status] || status
}

const getBadgeClass = (status) => {
  const map = {
    pending: 'badge-warning',
    confirmed: 'badge-info',
    paid: 'badge-success',
    cancelled: 'badge-danger'
  }
  return map[status] || ''
}

const openAddModal = () => {
  isEditing.value = false
  form.value = {
    ...createEmptyBookingForm(),
    hall: halls.value[0]?.id || null,
    room: rooms.value[0]?.id || '',
    rooms_selected: rooms.value[0]?.id ? [String(rooms.value[0].id)] : [],
  }
  resetQuickCustomerState()
  daysCount.value = 0
  calendarViewMonth.value = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
  calendarRangeStart.value = null
  calendarRangeEnd.value = null
  fetchCustomers()
  fetchCalendarRanges()
  showFormModal.value = true
}

const editBooking = (booking) => {
  closeActions()
  isEditing.value = true
  form.value = mapBookingToForm(booking)
  selectedCustomer.value = booking?.customer && form.value.customer_kind !== 'organization'
    ? {
      id: booking.customer,
      first_name: form.value.customer_first_name,
      last_name: form.value.customer_last_name,
      full_name: booking.customer_full_name || `${form.value.customer_first_name} ${form.value.customer_last_name}`.trim(),
      phone: booking.customer_profile_phone || booking.customer_phone || '',
      email: booking.customer_profile_email || booking.customer_email || '',
      identity_type: booking.customer_profile_identity_type || booking.guest_id_type || '',
      identity_number: booking.customer_profile_identity_number || booking.guest_id_number || '',
    }
    : null
  customerSearch.value = selectedCustomer.value?.full_name || ''
  customerResultsOpen.value = false
  showQuickCustomerForm.value = false
  if (form.value.start_date) {
    const d = new Date(form.value.start_date)
    if (!Number.isNaN(d.getTime())) {
      d.setHours(0, 0, 0, 0)
      calendarViewMonth.value = new Date(d.getFullYear(), d.getMonth(), 1)
      calendarRangeStart.value = d
    }
  } else {
    calendarRangeStart.value = null
  }
  if (form.value.end_date) {
    const d2 = new Date(form.value.end_date)
    if (!Number.isNaN(d2.getTime())) {
      d2.setHours(0, 0, 0, 0)
      calendarRangeEnd.value = d2
    } else {
      calendarRangeEnd.value = null
    }
  } else {
    calendarRangeEnd.value = null
  }
  fetchCalendarRanges()
  calculatePrice()
  showFormModal.value = true
}

const viewBooking = (booking) => {
  closeActions()
  selectedBooking.value = booking
  showViewModal.value = true
}

const confirmDelete = (booking) => {
  closeActions()
  if (!canDeleteBookings.value) {
    notify('Ce role ne peut pas supprimer une reservation', 'warning')
    return
  }
  selectedBooking.value = booking
  showDeleteModal.value = true
}

const printBookingJeton = async (booking) => {
  closeActions()
  await printReservationJeton(booking)
}

const normalizeEventType = (eventType, eventTypeOther = '') => {
  if (eventType !== 'Autres') return eventType
  const details = String(eventTypeOther || '').trim()
  return details ? `Autres: ${details}` : 'Autres'
}

const mapBookingToForm = (booking) => {
  const rawEventType = String(booking?.event_type || '')
  const isKnown = eventTypeOptions.includes(rawEventType)
  const rawFull = String(booking?.customer_name || '').trim()
  const nameParts = rawFull.split(' ').filter(Boolean)
  const customer_first_name = nameParts[0] || ''
  const customer_last_name = nameParts.length > 1 ? nameParts.slice(1).join(' ') : ''

  if (booking?.booking_type === 'room') {
    return {
      ...booking,
      customer: booking?.customer || null,
      customer_kind: booking?.customer_kind || 'individual',
      customer_first_name,
      customer_last_name,
      organization_name: booking?.organization_name || '',
      organization_contact_name: booking?.organization_contact_name || '',
      rooms_selected: Array.isArray(booking?.room_ids) && booking.room_ids.length
        ? booking.room_ids.map(id => String(id))
        : (booking?.room ? [String(booking.room)] : []),
      additional_services_selected: normalizeAdditionalServicesSelection(booking?.additional_services_selected),
      event_type: 'Séjour',
      event_type_other: '',
    }
  }

  if (isKnown) {
    return {
      ...booking,
      customer: booking?.customer || null,
      customer_kind: booking?.customer_kind || 'individual',
      customer_first_name,
      customer_last_name,
      organization_name: booking?.organization_name || '',
      organization_contact_name: booking?.organization_contact_name || '',
      rooms_selected: [],
      additional_services_selected: normalizeAdditionalServicesSelection(booking?.additional_services_selected),
      event_type_other: '',
    }
  }

  const otherPrefix = 'Autres: '
  return {
    ...booking,
    customer: booking?.customer || null,
    customer_kind: booking?.customer_kind || 'individual',
    customer_first_name,
    customer_last_name,
    organization_name: booking?.organization_name || '',
    organization_contact_name: booking?.organization_contact_name || '',
    rooms_selected: [],
    additional_services_selected: normalizeAdditionalServicesSelection(booking?.additional_services_selected),
    event_type: 'Autres',
    event_type_other: rawEventType.startsWith(otherPrefix) ? rawEventType.slice(otherPrefix.length) : rawEventType,
  }
}

const buildBookingPayload = () => {
  const { event_type_other, customer_first_name, customer_last_name, rooms_selected, ...payload } = form.value
  const fullName = `${String(customer_first_name || '').trim()} ${String(customer_last_name || '').trim()}`.trim()
  const customerName = form.value.customer_kind === 'organization'
    ? String(form.value.organization_name || '').trim()
    : fullName
  const guestName = payload.booking_type === 'room'
    ? (form.value.customer_kind === 'organization'
      ? String(form.value.organization_contact_name || '').trim()
      : fullName)
    : ''
  return {
    ...payload,
    additional_services_selected: normalizeAdditionalServicesSelection(payload.additional_services_selected),
    customer: form.value.customer_kind === 'organization' ? null : (payload.customer || null),
    room: payload.booking_type === 'room' ? (payload.room || selectedRoomIds.value[0] || '') : '',
    room_ids: payload.booking_type === 'room' ? selectedRoomIds.value.map(id => Number(id)) : [],
    customer_name: customerName,
    customer_email: String(payload.customer_email || '').trim(),
    customer_phone: String(payload.customer_phone || '').trim(),
    guest_full_name: guestName,
    guest_id_type: '',
    guest_id_number: '',
    event_type: payload.booking_type === 'room' ? 'Séjour' : normalizeEventType(form.value.event_type, event_type_other),
  }
}

const buildPdfFileName = (prefix, identifier) => {
  const normalizedIdentifier = String(identifier || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')

  return normalizedIdentifier
    ? `${prefix}-${normalizedIdentifier}.pdf`
    : buildExportFileName(prefix, 'pdf')
}

const buildReservationJetonPdfHtml = (booking, emailSent = null) => {
  const displayId = getBookingDisplayId(booking)
  const reservationNumber = booking?.id || '-'
  const bookedItemLabel = booking?.booking_type === 'room'
    ? ((Number(booking?.room_count || 0) > 1) ? 'Chambres' : 'Chambre')
    : 'Salle'
  const bookedItemName = booking?.booking_type === 'room' ? (booking?.room_display || '') : (booking?.hall_name || '')
  const emailValue = booking?.customer_email || 'Non renseigné'
  const emailSentLabel = typeof emailSent === 'boolean' ? (emailSent ? 'Oui' : 'Non') : '-'
  const periodLabel = formatDateRange(booking?.start_date, booking?.end_date)
  const clientRows = [
    ['Client', booking?.customer_name || '-'],
    ...(booking?.customer_kind === 'organization'
      ? [
        ['Organisation', booking?.organization_name || booking?.customer_name || '-'],
        ['Contact', booking?.organization_contact_name || booking?.guest_full_name || '-'],
      ]
      : []),
    ['Email client', emailValue],
  ]
  const reservationRows = [
    [bookedItemLabel, bookedItemName || '-'],
    ['Evénement', booking?.event_type || '-'],
    ['Période', periodLabel || '-'],
    ['Montant', formatMoney(booking?.total_price)],
    ['Statut', getStatusTranslation(booking?.status)],
  ]
  const followUpRows = [
    ['Code de réservation', displayId],
    ['Numéro', reservationNumber],
  ]

  if (typeof emailSent === 'boolean') {
    followUpRows.push(['Email envoyé', emailSentLabel])
  }

  if (booking?.booking_type === 'room') {
    followUpRows.push(['Client hébergé', booking?.guest_full_name || booking?.customer_name || '-'])
    if (booking?.customer_kind !== 'organization') {
      followUpRows.push(['Pièce', guestIdSummary(booking)])
    }
  }

  return buildPdfDocumentHtml({
    title: 'Jeton de réservation',
    documentTitle: `Jeton ${displayId}`,
    subtitle: 'Jeton officiel de reservation a presenter pour le suivi de votre dossier ou a l accueil.',
    typeLabel: 'Jeton PDF',
    headerVariant: 'ticket',
    headerEyebrow: 'Document de suivi',
    headerReference: displayId,
    tableTitle: 'Détails du jeton',
    tableTitles: ['Résumé du jeton', 'Client et contact', 'Réservation', 'Suivi du dossier'],
    periodLabel,
    contentHtml: `
      <div class="section-card">
        <div class="section-header"><h2>Résumé du jeton</h2></div>
        <table>
          <thead>
            <tr>
              <th>Information</th>
              <th>Valeur</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Code de réservation</td>
              <td>${escapeHtml(displayId)}</td>
            </tr>
            <tr>
              <td>Numéro</td>
              <td>${escapeHtml(reservationNumber)}</td>
            </tr>
            <tr>
              <td>Client</td>
              <td>${escapeHtml(booking?.customer_name || '-')}</td>
            </tr>
            <tr>
              <td>${escapeHtml(bookedItemLabel)}</td>
              <td>${escapeHtml(bookedItemName || '-')}</td>
            </tr>
            <tr>
              <td>Période</td>
              <td>${escapeHtml(periodLabel || '-')}</td>
            </tr>
            <tr>
              <td>Montant</td>
              <td>${escapeHtml(formatMoney(booking?.total_price))}</td>
            </tr>
            <tr>
              <td>Statut</td>
              <td>${escapeHtml(getStatusTranslation(booking?.status))}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="section-card">
        <div class="section-header"><h2>Client et contact</h2></div>
        <table>
          <thead>
            <tr>
              <th>Information</th>
              <th>Valeur</th>
            </tr>
          </thead>
          <tbody>
            ${clientRows.map(([label, value]) => `
              <tr>
                <td>${escapeHtml(label)}</td>
                <td>${escapeHtml(value)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      <div class="section-card">
        <div class="section-header"><h2>Réservation</h2></div>
        <table>
          <thead>
            <tr>
              <th>Information</th>
              <th>Valeur</th>
            </tr>
          </thead>
          <tbody>
            ${reservationRows.map(([label, value]) => `
              <tr>
                <td>${escapeHtml(label)}</td>
                <td>${escapeHtml(value)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      <div class="section-card">
        <div class="section-header"><h2>Suivi du dossier</h2></div>
        <table>
          <thead>
            <tr>
              <th>Information</th>
              <th>Valeur</th>
            </tr>
          </thead>
          <tbody>
            ${followUpRows.map(([label, value]) => `
              <tr>
                <td>${escapeHtml(label)}</td>
                <td>${escapeHtml(value)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
      <div class="section-card">
        <div class="section-header"><h2>Note</h2></div>
        <p>Merci de conserver ce jeton. Il peut vous etre demande lors du suivi de votre dossier ou a l arrivee.</p>
      </div>
    `,
  })
}

const openReservationJetonPrintPreview = (booking, emailSent = null, previewWindow = null) => {
  if (!process.client || !booking) return
  const html = buildReservationJetonPdfHtml(booking, emailSent)
  const ok = openPrintPreviewHtml({
    html,
    title: `Jeton ${getBookingDisplayId(booking)}`,
    autoPrint: false,
    printWindow: previewWindow,
  })
  if (!ok) {
    notify('Impossible d’ouvrir l’aperçu d’impression du jeton', 'warning')
  }
}

const printReservationJeton = async (booking) => {
  if (!process.client || !booking) return
  const html = buildReservationJetonPdfHtml(booking)
  const ok = await downloadPdfHtml({
    html,
    fileName: buildPdfFileName('jeton-reservation', getBookingDisplayId(booking)),
  })
  if (!ok) {
    notify('Impossible de télécharger le jeton PDF', 'warning')
  }
}
</script>

<style scoped>
.bookings-page {
  padding: 0;
}

.admin-cards {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-10);
  gap: var(--space-4);
  flex-wrap: wrap;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
}

.page-header p {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.header-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: .5rem;
}

.controls-top {
  width: 100%;
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.filters-panel {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-top: var(--space-4);
}

.filter-range-note {
  margin-top: 0.75rem;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 700;
}

.filters-toggle {
  display: none;
  width: 42px;
  height: 42px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #475569;
}

.filters-toggle.active {
  background: rgba(212, 175, 55, .18);
  border-color: rgba(212, 175, 55, .35);
  color: #0f172a;
}

.actions-dropdown {
  position: relative;
  display: inline-flex;
}

.actions-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
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

.actions-item:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
  color: #b91c1c;
}

@media (max-width: 992px) {
  .filters-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .filters-panel {
    gap: var(--space-3);
  }
}

.header-actions {
  display: flex;
  gap: var(--space-3);
}

.controls {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
  padding: var(--space-4) var(--space-6);
  align-items: center;
  height: auto;
  flex-wrap: wrap;
}

.search-wrapper {
  flex-grow: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
}

.search-input-clean {
  width: 100%;
  padding: 0.625rem 1rem 0.625rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.9rem;
  background: #f8fafc;
  transition: var(--transition-fast);
}

.search-input-clean:focus {
  background: white;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}

.filter-select-clean {
  padding: 0.625rem 2rem 0.625rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.9rem;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  cursor: pointer;
}

.filter-input-clean {
  padding: 0.625rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.9rem;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  transition: var(--transition-fast);
}

.filter-input-clean:focus {
  background: white;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1);
}

.table-title {
  font-size: 1rem;
  font-weight: 800;
  margin-bottom: var(--space-6);
  color: #1e293b;
  padding: 0 var(--space-2);
}

.bookings-table {
  width: 100%;
}

.customer-name {
  font-weight: 700;
  color: var(--gray-900);
  font-size: 0.95rem;
}

.customer-email {
  font-size: 0.8rem;
  color: var(--gray-500);
  font-weight: 500;
}

.customer-meta {
  margin-top: 0.3rem;
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 600;
}

.amount-cell {
  font-weight: 800;
  color: #0f172a;
  font-size: 0.9rem;
}

.btn-icon {
  width: 34px;
  height: 34px;
  font-size: 1.1rem;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.approve:hover { color: var(--success); }
.btn-icon.reject:hover { color: var(--warning); }
.btn-icon.view:hover { color: var(--info); }
.btn-icon.edit:hover { color: var(--primary); }
.btn-icon.delete:hover { color: var(--danger); }
.btn-icon.pay:hover { color: #b45309; }

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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.booking-form-shell {
  display: grid;
  gap: 1rem;
}

.booking-form-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.2rem;
  border: 1px solid rgba(191, 219, 254, 0.9);
  border-radius: 24px;
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.14), transparent 34%),
    linear-gradient(135deg, #ffffff 0%, #f8fbff 52%, #eef6ff 100%);
  box-shadow: 0 16px 32px rgba(15, 23, 42, 0.08);
}

.booking-form-hero-copy {
  display: grid;
  gap: 0.35rem;
}

.booking-form-eyebrow {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.booking-form-hero-copy h3 {
  margin: 0;
  color: #0f172a;
  font-size: 1.2rem;
  font-weight: 800;
}

.booking-form-hero-copy p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
  max-width: 44rem;
}

.booking-form-hero-meta {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.55rem;
}

.booking-form-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 0.85rem;
  border-radius: 999px;
  border: 1px solid #dbeafe;
  background: rgba(255, 255, 255, 0.85);
  color: #334155;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.booking-form-chip.accent {
  border-color: rgba(212, 175, 55, 0.3);
  background: rgba(212, 175, 55, 0.12);
  color: #8a6a12;
}

.booking-form-section {
  display: grid;
  gap: 1rem;
  padding: 1.05rem 1.1rem 1.15rem;
  border: 1px solid var(--gray-200);
  border-radius: 22px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
}

.booking-form-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.booking-form-section-kicker {
  display: inline-flex;
  align-items: center;
  margin-bottom: 0.25rem;
  color: #2563eb;
  font-size: 0.73rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.booking-form-section-head h4 {
  margin: 0;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 800;
}

.booking-form-section-head p {
  margin: 0;
  max-width: 28rem;
  color: #64748b;
  line-height: 1.55;
  font-size: 0.9rem;
}

.booking-form-grid {
  gap: 1rem;
}

.customer-lookup-card,
.quick-customer-card {
  padding: 1rem;
  border: 1px solid #dbeafe;
  border-radius: 18px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
}

.organization-booking-note,
.organization-room-note {
  padding: 0.95rem 1rem;
  border-radius: 16px;
  border: 1px solid #c7d2fe;
  background: linear-gradient(180deg, #ffffff 0%, #f8faff 100%);
  display: grid;
  gap: 0.25rem;
}

.organization-booking-note strong,
.organization-room-note strong {
  color: #1e293b;
}

.organization-booking-note small,
.organization-room-note small {
  color: #64748b;
  line-height: 1.5;
}

.customer-lookup-head,
.quick-customer-head,
.quick-customer-actions,
.selected-customer-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.customer-lookup-head small,
.quick-customer-head span,
.quick-customer-actions small {
  color: #64748b;
  line-height: 1.45;
}

.customer-search-shell {
  position: relative;
  margin-top: 0.8rem;
}

.customer-search-icon {
  position: absolute;
  top: 50%;
  left: 14px;
  transform: translateY(-50%);
  color: #64748b;
}

.customer-search-input {
  padding-left: 40px;
}

.customer-results-list {
  display: grid;
  gap: 0.55rem;
  margin-top: 0.8rem;
}

.customer-result-item,
.customer-results-empty,
.selected-customer-card {
  padding: 0.85rem 1rem;
  border-radius: 14px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
}

.customer-result-item {
  display: grid;
  gap: 0.2rem;
  text-align: left;
  transition: all 0.18s ease;
}

.customer-result-item strong,
.selected-customer-main strong {
  color: #0f172a;
}

.customer-result-item span,
.selected-customer-main span {
  color: #64748b;
  font-size: 0.85rem;
}

.customer-result-item:hover {
  border-color: #bfdbfe;
  background: #eff6ff;
}

.selected-customer-main {
  display: grid;
  gap: 0.18rem;
}

.quick-customer-grid {
  margin-top: 0.85rem;
}

.quick-customer-actions {
  margin-top: 0.85rem;
}

.room-selection-head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
}

.room-selection-head small {
  color: #64748b;
  line-height: 1.45;
}

.room-selection-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.room-option-card {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.9rem;
  align-items: flex-start;
  min-height: 138px;
  padding: 1rem;
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  cursor: pointer;
}

.room-option-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.room-option-check {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  border: 1px solid #cbd5e1;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  color: #64748b;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.room-option-card:hover {
  transform: translateY(-1px);
  border-color: rgba(59, 130, 246, 0.36);
  box-shadow: 0 18px 30px rgba(59, 130, 246, 0.12);
}

.room-option-card.selected {
  border-color: rgba(59, 130, 246, 0.68);
  background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%);
  box-shadow: 0 20px 36px rgba(59, 130, 246, 0.16);
}

.room-option-card.selected .room-option-check {
  border-color: rgba(59, 130, 246, 0.35);
  background: linear-gradient(180deg, #93c5fd 0%, #60a5fa 100%);
  color: #ffffff;
}

.room-option-card.unavailable {
  opacity: 0.7;
  cursor: not-allowed;
  border-color: rgba(148, 163, 184, 0.2);
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  box-shadow: none;
}

.room-option-card.maintenance {
  border-color: #fecaca;
}

.room-option-main {
  display: grid;
  gap: 0.45rem;
  min-width: 0;
}

.room-option-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.room-option-price {
  color: #0f172a;
  font-size: 0.82rem;
  font-weight: 800;
  white-space: nowrap;
}

.room-option-meta {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.room-option-type,
.room-option-status {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.02em;
}

.room-option-type {
  background: rgba(148, 163, 184, 0.12);
  color: #475569;
}

.room-option-main strong {
  color: #0f172a;
  font-size: 1rem;
  line-height: 1.45;
}

.room-option-main span,
.room-option-main small {
  color: #64748b;
  font-size: 0.85rem;
}

.room-option-main small {
  line-height: 1.5;
}

.room-option-booked-dates {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.7rem;
  border-radius: 12px;
  background: rgba(254, 242, 242, 0.95);
  border: 1px solid rgba(252, 165, 165, 0.55);
  color: #b91c1c;
  font-weight: 700;
}

.room-option-booked-dates::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.8;
}

.booking-total-banner {
  display: grid;
  gap: 14px;
  padding: 18px;
  border: 1px solid rgba(212, 175, 55, 0.28);
  border-radius: 22px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.78) 0%, rgba(30, 41, 59, 0.72) 58%, rgba(139, 107, 18, 0.68) 100%);
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.14);
  overflow: hidden;
  isolation: isolate;
  -webkit-backdrop-filter: blur(18px) saturate(135%);
  backdrop-filter: blur(18px) saturate(135%);
}

.booking-total-banner-bottom {
  margin-top: 18px;
}

.room-booking-note {
  padding: 0.95rem 1rem;
  border: 1px solid #dbeafe;
  border-radius: 16px;
  background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
  box-shadow: 0 10px 24px rgba(148, 163, 184, 0.12);
}

.room-booking-note strong {
  color: #0f172a;
}

.room-booking-note small {
  display: block;
  color: #475569;
  line-height: 1.5;
}

.room-booking-note-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
  flex-wrap: wrap;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.7rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 800;
  border: 1px solid transparent;
}

.status-available {
  background: #ecfdf3;
  color: #15803d;
  border-color: #bbf7d0;
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

.stay-history-card {
  border: 1px solid var(--gray-200);
  border-radius: 18px;
  background: var(--gray-50);
  padding: 1rem;
}

.stay-history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  color: var(--gray-900);
}

.stay-history-list {
  display: grid;
  gap: 0.75rem;
}

.stay-history-list.compact {
  gap: 0.55rem;
}

.stay-history-item {
  display: grid;
  gap: 0.15rem;
  padding: 0.85rem 1rem;
  border: 1px solid var(--gray-200);
  border-radius: 14px;
  background: #ffffff;
  color: var(--gray-700);
  font-size: 0.88rem;
}

.stay-history-item strong {
  color: var(--gray-900);
}

.booking-total-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.booking-total-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.booking-total-value {
  color: #ffffff;
  font-size: 1.8rem;
  line-height: 1.1;
  font-weight: 900;
}

.booking-total-hint {
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.82rem;
  line-height: 1.45;
}

.booking-total-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.booking-total-chip {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.booking-total-chip .chip-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.booking-total-chip strong {
  color: #ffffff;
  font-size: 0.92rem;
  font-weight: 800;
  word-break: break-word;
}

.form-group.full {
  grid-column: span 2;
}

.calendar-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 6px;
  margin-bottom: 10px;
}

.calendar-nav {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  color: #334155;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
  margin-bottom: 8px;
  color: #64748b;
  font-weight: 800;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.weekday-row span {
  text-align: center;
}

.calendar-grid-admin {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.day-cell {
  height: 38px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  font-weight: 800;
  color: #0f172a;
}

.day-cell.muted {
  opacity: 0.55;
}

.day-cell.booked {
  background: rgba(220, 38, 38, 0.08);
  border-color: rgba(220, 38, 38, 0.18);
  color: #991b1b;
}

.day-cell.disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.day-cell.start,
.day-cell.end {
  background: rgba(212, 175, 55, 0.18);
  border-color: rgba(212, 175, 55, 0.35);
  color: #0f172a;
}

.day-cell.inrange {
  background: rgba(212, 175, 55, 0.12);
  border-color: rgba(212, 175, 55, 0.22);
}

.calendar-legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 12px;
  color: #64748b;
  font-weight: 700;
  font-size: 0.85rem;
}

.calendar-legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 6px;
  vertical-align: middle;
}

.calendar-legend .dot.booked {
  background: #dc2626;
}

.calendar-legend .dot.selected {
  background: #d4af37;
}

.calendar-legend .dot.range {
  background: rgba(212, 175, 55, 0.45);
}

.selected-period-card {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.selected-period-label {
  color: #64748b;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.selected-period-value {
  margin-top: 0.35rem;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 800;
}

.selected-period-hint {
  margin-top: 0.35rem;
  color: #64748b;
  font-size: 0.85rem;
  line-height: 1.45;
}

.addons-section {
  border-top: 1px solid var(--gray-200);
  padding-top: 14px;
}

.addons-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}

.addons-total {
  color: var(--gray-900);
  font-weight: 900;
}

.addons-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.addon-item {
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 22px;
  padding: 16px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
}

.addon-line {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(250px, 290px);
  gap: 14px;
  align-items: stretch;
}

.addon-side {
  display: grid;
  gap: 12px;
  align-content: start;
  padding: 16px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
}

.addon-side-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.addon-toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-height: 96px;
  padding: 16px 18px;
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 20px;
  background: var(--white);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.addon-toggle:hover {
  border-color: rgba(59, 130, 246, 0.22);
  background: #f8fbff;
  transform: translateY(-1px);
}

.addon-toggle input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.addon-toggle.is-active {
  border-color: rgba(34, 197, 94, 0.38);
  background: linear-gradient(180deg, rgba(34, 197, 94, 0.1) 0%, rgba(255, 255, 255, 0.98) 100%);
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.1);
}

.toggle-switch {
  position: relative;
  width: 50px;
  height: 30px;
  border-radius: 999px;
  background: var(--gray-300);
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
  background: var(--white);
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.18);
  transition: transform 0.2s ease;
}

.addon-toggle.is-active .toggle-switch {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
}

.addon-toggle.is-active .toggle-knob {
  transform: translateX(20px);
}

.addon-toggle-copy {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}

.addon-toggle-copy strong {
  color: var(--gray-900);
  font-size: 1rem;
  font-weight: 800;
}

.addon-toggle-copy small {
  color: var(--gray-500);
  font-size: 0.82rem;
  line-height: 1.35;
}

.addon-price {
  color: var(--gray-900);
  font-weight: 800;
  white-space: nowrap;
  font-size: 1.05rem;
}

.addon-unit {
  color: var(--gray-500);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.addon-qty-control {
  display: grid;
  gap: 8px;
}

.addon-qty-control.is-disabled {
  opacity: 0.72;
}

.addon-qty-label {
  color: var(--gray-500);
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.addon-stepper {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) 42px;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--gray-200);
  border-radius: 16px;
  background: #f8fafc;
}

.addon-step-btn {
  width: 42px;
  height: 42px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  background: var(--white);
  color: var(--gray-700);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

.addon-step-btn:hover:not(:disabled) {
  border-color: rgba(37, 99, 235, 0.28);
  color: #2563eb;
  background: #eff6ff;
  transform: translateY(-1px);
}

.addon-step-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.addon-qty-input {
  width: 100%;
  min-width: 0;
  height: 44px;
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  background: var(--white);
  color: var(--gray-900);
  font-size: 1rem;
  font-weight: 800;
  text-align: center;
}

.addon-line-total {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-weight: 900;
  white-space: nowrap;
}

.addon-sub-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 10px;
}

.addon-subs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.addon-sub-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(250px, 290px);
  gap: 14px;
  align-items: stretch;
}

.addon-sub-line {
  display: flex;
  gap: 12px;
  align-items: center;
}

.services-preview {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.service-preview-item {
  border: 1px solid var(--gray-200);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  background: var(--gray-50);
}

.service-preview-title,
.service-preview-sub {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.service-preview-subs {
  margin-top: 0.55rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: var(--gray-600);
}

html[data-admin-theme="dark"] .addons-section {
  border-top-color: rgba(51, 65, 85, 0.9);
}

html[data-admin-theme="dark"] .addon-item {
  border-color: rgba(51, 65, 85, 0.95);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.86) 0%, rgba(15, 23, 42, 0.76) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

html[data-admin-theme="dark"] .addon-toggle {
  border-color: rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.88);
}

html[data-admin-theme="dark"] .addon-toggle:hover {
  border-color: rgba(71, 85, 105, 0.95);
  background: rgba(15, 23, 42, 0.96);
}

html[data-admin-theme="dark"] .addon-toggle.is-active {
  border-color: rgba(34, 197, 94, 0.55);
  background: linear-gradient(180deg, rgba(20, 83, 45, 0.4) 0%, rgba(15, 23, 42, 0.92) 100%);
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.16);
}

html[data-admin-theme="dark"] .toggle-switch {
  background: rgba(71, 85, 105, 0.9);
}

html[data-admin-theme="dark"] .toggle-knob {
  background: #f8fafc;
  box-shadow: 0 6px 14px rgba(2, 6, 23, 0.45);
}

html[data-admin-theme="dark"] .addon-price {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .addon-unit,
html[data-admin-theme="dark"] .addon-qty-label {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .addon-side,
html[data-admin-theme="dark"] .addon-stepper,
html[data-admin-theme="dark"] .addon-qty-control,
html[data-admin-theme="dark"] .addon-qty-input {
  background: rgba(15, 23, 42, 0.88);
  border-color: rgba(51, 65, 85, 0.95);
  color: #f8fafc;
}

html[data-admin-theme="dark"] .addon-step-btn {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(51, 65, 85, 0.95);
  color: #e2e8f0;
}

html[data-admin-theme="dark"] .addon-step-btn:hover:not(:disabled) {
  background: rgba(30, 64, 175, 0.18);
  border-color: rgba(96, 165, 250, 0.35);
  color: #bfdbfe;
}

html[data-admin-theme="dark"] .addon-line-total {
  background: rgba(30, 64, 175, 0.16);
  color: #93c5fd;
}

html[data-admin-theme="dark"] .addon-sub-head .muted-line,
html[data-admin-theme="dark"] .addon-toggle-copy small {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .service-preview-item {
  border-color: rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.7);
}

html[data-admin-theme="dark"] .room-booking-note {
  border-color: rgba(59, 130, 246, 0.28);
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.92) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02), 0 14px 28px rgba(2, 6, 23, 0.28);
}

html[data-admin-theme="dark"] .booking-form-hero {
  border-color: rgba(51, 65, 85, 0.95);
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.92) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 16px 30px rgba(2, 6, 23, 0.28);
}

html[data-admin-theme="dark"] .booking-form-eyebrow {
  background: rgba(59, 130, 246, 0.18);
  color: #bfdbfe;
}

html[data-admin-theme="dark"] .booking-form-hero-copy h3,
html[data-admin-theme="dark"] .booking-form-section-head h4 {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .booking-form-hero-copy p,
html[data-admin-theme="dark"] .booking-form-section-head p,
html[data-admin-theme="dark"] .booking-form-section-kicker {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .booking-form-chip {
  border-color: rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.72);
  color: #e2e8f0;
}

html[data-admin-theme="dark"] .booking-form-chip.accent {
  border-color: rgba(212, 175, 55, 0.28);
  background: rgba(161, 98, 7, 0.16);
  color: #fde68a;
}

html[data-admin-theme="dark"] .booking-form-section {
  border-color: rgba(51, 65, 85, 0.95);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(15, 23, 42, 0.82) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

html[data-admin-theme="dark"] .organization-booking-note,
html[data-admin-theme="dark"] .organization-room-note,
html[data-admin-theme="dark"] .room-option-card {
  border-color: rgba(51, 65, 85, 0.95);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.78) 100%);
}

html[data-admin-theme="dark"] .organization-booking-note strong,
html[data-admin-theme="dark"] .organization-room-note strong,
html[data-admin-theme="dark"] .room-option-main strong {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .organization-booking-note small,
html[data-admin-theme="dark"] .organization-room-note small,
html[data-admin-theme="dark"] .room-option-main span,
html[data-admin-theme="dark"] .room-option-main small,
html[data-admin-theme="dark"] .room-selection-head small {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .room-option-check {
  border-color: rgba(71, 85, 105, 0.95);
  background: rgba(30, 41, 59, 0.96);
  color: #cbd5e1;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

html[data-admin-theme="dark"] .room-option-card.selected {
  border-color: rgba(96, 165, 250, 0.68);
  background: linear-gradient(180deg, rgba(30, 41, 59, 0.98) 0%, rgba(15, 23, 42, 0.92) 100%);
}

html[data-admin-theme="dark"] .room-option-card.selected .room-option-check {
  border-color: rgba(96, 165, 250, 0.52);
  background: linear-gradient(180deg, rgba(96, 165, 250, 0.9) 0%, rgba(59, 130, 246, 0.96) 100%);
  color: #ffffff;
}

html[data-admin-theme="dark"] .room-option-card.unavailable {
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.72) 0%, rgba(15, 23, 42, 0.58) 100%);
}

html[data-admin-theme="dark"] .room-option-price {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .room-option-type {
  background: rgba(148, 163, 184, 0.16);
  color: #e2e8f0;
}

html[data-admin-theme="dark"] .room-option-booked-dates {
  background: rgba(127, 29, 29, 0.18);
  border-color: rgba(248, 113, 113, 0.32);
  color: #fecaca;
}

html[data-admin-theme="dark"] .room-booking-note strong {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .room-booking-note small {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .customer-lookup-card,
html[data-admin-theme="dark"] .quick-customer-card,
html[data-admin-theme="dark"] .customer-result-item,
html[data-admin-theme="dark"] .customer-results-empty,
html[data-admin-theme="dark"] .selected-customer-card {
  border-color: rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.82);
}

html[data-admin-theme="dark"] .customer-result-item strong,
html[data-admin-theme="dark"] .selected-customer-main strong {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .customer-result-item span,
html[data-admin-theme="dark"] .selected-customer-main span,
html[data-admin-theme="dark"] .customer-lookup-head small,
html[data-admin-theme="dark"] .quick-customer-head span,
html[data-admin-theme="dark"] .quick-customer-actions small,
html[data-admin-theme="dark"] .customer-search-icon {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .customer-result-item:hover {
  border-color: rgba(59, 130, 246, 0.38);
  background: rgba(30, 41, 59, 0.95);
}

html[data-admin-theme="dark"] .stay-history-card {
  border-color: rgba(51, 65, 85, 0.95);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.86) 0%, rgba(15, 23, 42, 0.74) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

html[data-admin-theme="dark"] .stay-history-head {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .stay-history-item {
  border-color: rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.94);
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .stay-history-item strong {
  color: #f8fafc;
}

html[data-admin-theme="dark"] .selected-period-card {
  border-color: rgba(51, 65, 85, 0.95);
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.82) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

html[data-admin-theme="dark"] .selected-period-label,
html[data-admin-theme="dark"] .selected-period-hint {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .selected-period-value {
  color: #f8fafc;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-group.full {
    grid-column: auto;
  }
  .booking-form-hero {
    padding: 1rem;
  }
  .booking-form-hero,
  .booking-form-section-head {
    flex-direction: column;
  }
  .booking-form-hero-meta {
    justify-content: flex-start;
  }
  .booking-form-section {
    padding: 0.95rem;
  }
  .entity-view-hero { flex-direction: column; align-items: flex-start; }
  .entity-view-badges { align-items: flex-start; flex-direction: row; flex-wrap: wrap; }
  .entity-view-grid { grid-template-columns: 1fr; }
  .entity-view-item { flex-direction: column; }
  .entity-view-value { text-align: left; }
  .booking-total-banner {
    padding: 16px;
  }
  .booking-total-meta {
    grid-template-columns: 1fr 1fr;
  }
  .addon-line {
    flex-direction: column;
    align-items: stretch;
  }
  .addon-side,
  .addon-sub-row {
    grid-template-columns: 1fr;
  }
  .addon-line {
    grid-template-columns: 1fr;
  }
  .addon-sub-line {
    align-items: flex-start;
  }
  .addon-price {
    padding-left: 0;
  }
  .addon-side-top {
    flex-direction: column;
    align-items: flex-start;
  }
  .room-selection-grid {
    grid-template-columns: 1fr;
  }
  .room-option-card {
    grid-template-columns: 1fr;
    min-height: unset;
  }
  .room-option-check {
    width: 40px;
    height: 40px;
  }
  .room-option-top {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .booking-total-meta {
    grid-template-columns: 1fr;
  }
  .booking-total-value {
    font-size: 1.5rem;
  }
}
</style>
