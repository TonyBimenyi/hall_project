<!-- pages/admin/bookings.vue -->
<template>
  <div class="bookings-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Réservations</h1>
        <p>Gérer toutes les réservations de salle</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': exportingPdf }" :disabled="exportingPdf || exportingXls" @click="exportPdf">
          <i class="fas fa-file-pdf"></i>
          <span class="btn-label">Export PDF</span>
        </button>
        <button class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': exportingXls }" :disabled="exportingPdf || exportingXls" @click="exportXls">
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
            placeholder="Rechercher par client ou salle..."
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
            <option value="">Toutes les salles</option>
            <option v-for="h in halls" :key="h.id" :value="h.id">{{ h.name }}</option>
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
            <option value="7d">7 jours</option>
            <option value="28d">28 jours</option>
            <option value="90d">90 jours</option>
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
                <div class="admin-card-subtitle">{{ getBookingDisplayId(booking) }} • {{ booking.hall_name }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
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
                    <i class="fas fa-print"></i> Imprimer le jeton
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
              <th><button class="table-sort-btn" :class="{ active: isBookingSortActive('hall_name') }" @click="toggleBookingSort('hall_name')">Salle <i :class="bookingSortIconClass('hall_name')"></i></button></th>
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
              </td>
              <td>{{ booking.hall_name }}</td>
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
                      <i class="fas fa-print"></i> Imprimer le jeton
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
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la réservation' : 'Nouvelle réservation'" width="600px">
      <form @submit.prevent="saveBooking" class="admin-form">
        <div class="booking-total-banner">
          <div class="booking-total-main">
            <span class="booking-total-label">Montant total en direct</span>
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
              <span class="chip-label">Services</span>
              <strong>{{ selectedAddonsCount }} selection{{ selectedAddonsCount > 1 ? 's' : '' }}</strong>
            </div>
            <div class="booking-total-chip">
              <span class="chip-label">Supplément</span>
              <strong>{{ formatMoney(addonsTotal) }}</strong>
            </div>
            <div class="booking-total-chip">
              <span class="chip-label">Durée</span>
              <strong>{{ daysCount > 0 ? `${daysCount} jour(s)` : 'Non definie' }}</strong>
            </div>
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Prénom</label>
            <input v-model="form.customer_first_name" type="text" class="form-input" placeholder="Prénom" required />
          </div>
          <div class="form-group">
            <label class="form-label">Nom</label>
            <input v-model="form.customer_last_name" type="text" class="form-input" placeholder="Nom" required />
          </div>
          <div class="form-group full">
            <label class="form-label">Email</label>
            <input v-model="form.customer_email" type="email" class="form-input" placeholder="email@exemple.com" />
          </div>
          <div class="form-group">
            <label class="form-label">Salle</label>
            <select v-model="form.hall" class="form-select" required @change="calculatePrice">
              <option v-for="h in halls" :key="h.id" :value="h.id">{{ h.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Type d'événement</label>
            <select v-model="form.event_type" class="form-select" required>
              <option v-for="eventOption in eventTypeOptions" :key="eventOption" :value="eventOption">{{ eventOption }}</option>
            </select>
          </div>
          <div v-if="isOtherEventType" class="form-group full">
            <label class="form-label">Détails de l'événement</label>
            <textarea
              v-model="form.event_type_other"
              class="form-textarea"
              rows="3"
              required
              placeholder="Précisez le type d'événement"
            ></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Date Début</label>
            <input :value="form.start_date" type="text" class="form-input" placeholder="YYYY-MM-DD" readonly required />
          </div>
          <div class="form-group">
            <label class="form-label">Date Fin</label>
            <input :value="form.end_date" type="text" class="form-input" placeholder="YYYY-MM-DD" readonly required />
          </div>
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
          </div>
          <div v-if="hallAdditionalServices.length" class="form-group full addons-section">
            <div class="addons-head">
              <strong>Services additionnels</strong>
              <span v-if="addonsTotal > 0" class="addons-total">+ {{ formatMoney(addonsTotal) }}</span>
            </div>
            <div class="addons-list">
              <div v-for="service in hallAdditionalServices" :key="service.name" class="addon-item">
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
                  <strong class="addon-price">{{ formatMoney(service.price) }}</strong>
                </div>
                <div v-else class="addon-sub-block">
                  <div class="addon-sub-head">
                    <strong>{{ service.name }}</strong>
                    <span class="muted-line">Choisissez les sous-services</span>
                  </div>
                  <div class="addon-subs">
                    <label
                      v-for="sub in (service.subservices || [])"
                      :key="`${service.name}-${sub.name}`"
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
                      <strong class="addon-price">{{ formatMoney(sub.price) }}</strong>
                    </label>
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
            <small class="form-hint" v-if="daysCount > 0">{{ daysCount }} jour(s) à {{ formatMoney(pricePerDay) }}/jour</small>
            <small class="form-hint" v-if="!isEditing">Montant calcule automatiquement selon la salle et la periode.</small>
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
            <p>{{ selectedBooking.hall_name }} • {{ selectedBooking.event_type }}</p>
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
              <div class="entity-view-item"><span class="entity-view-label">Salle</span><span class="entity-view-value">{{ selectedBooking.hall_name }}</span></div>
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
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedBooking.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedBooking.updated_by_name || selectedBooking.created_by_name || '-' }}</span></div>
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
                </div>
                <div v-if="svc.subservices?.length" class="service-preview-subs">
                  <div v-for="(sub, sidx) in svc.subservices" :key="`${svc.name}-${sidx}`" class="service-preview-sub">
                    <span>{{ sub.name }}</span>
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
import { useDisplayIds } from '~/composables/useDisplayIds'
import { useTableSort } from '~/composables/useTableSort'
import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { canDeleteBookings as canDeleteBookingsByRole, getStoredUser } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const { formatMoney, formatNumberSpaces, moneyInputModel, parseMoney } = useMoney()
const { formatDateRange, formatDisplayDate } = useDateFormat()
const { buildMonthlySequenceMap } = useDisplayIds()
const { documentBranding, documentLogoUrl, escapeHtml } = useDocumentBranding()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName } = useAdminExportDocuments()
const eventTypeOptions = ['Mariage', 'Séminaire', 'Gala', 'Anniversaire', 'Réunion', 'Autres']

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

const dateOverlapsRange = (start, end, rangeStart, rangeEnd) => {
  const s = String(start || '').slice(0, 10)
  const e = String(end || '').slice(0, 10)
  if (!rangeStart || !rangeEnd) return true
  if (!s || !e) return false
  return s <= rangeEnd && e >= rangeStart
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
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)

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
  if (!form.value?.hall) {
    calendarRanges.value = []
    return
  }
  try {
    const res = await api.get('bookings/calendar/', { params: { hall: form.value.hall } })
    calendarRanges.value = Array.isArray(res.data) ? res.data : []
  } catch {
    calendarRanges.value = []
  }
}

const exportXls = async () => {
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

const form = ref({
  id: null,
  customer_first_name: '',
  customer_last_name: '',
  customer_email: '',
  hall: '',
  event_type: 'Mariage',
  event_type_other: '',
  start_date: '',
  end_date: '',
  additional_services_selected: [],
  total_price: 0,
  status: 'pending'
})
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

onMounted(async () => {
  currentUser.value = getStoredUser()
  await Promise.all([fetchBookings(), fetchHalls()])
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

const pricePerDay = ref(0)
const daysCount = ref(0)

const selectedHall = computed(() => halls.value.find(h => String(h.id) === String(form.value.hall)) || null)
const hallAdditionalServices = computed(() => Array.isArray(selectedHall.value?.additional_services) ? selectedHall.value.additional_services : [])
const baseBookingAmount = computed(() => Number(daysCount.value || 0) * Number(pricePerDay.value || 0))
const selectedAddonsCount = computed(() => {
  const selected = Array.isArray(form.value.additional_services_selected) ? form.value.additional_services_selected : []
  let count = 0
  for (const item of selected) {
    const subs = Array.isArray(item?.subservices) ? item.subservices : []
    count += subs.length > 0 ? subs.length : 1
  }
  return count
})

const addonsTotal = computed(() => {
  const services = hallAdditionalServices.value
  const selected = Array.isArray(form.value.additional_services_selected) ? form.value.additional_services_selected : []
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
        total += subIndex.get(String(sub?.name || '')) || 0
      }
      continue
    }
    total += Number(cfg.price || 0)
  }
  return total
})

const calculatePrice = () => {
  if (form.value.start_date && form.value.end_date && form.value.hall) {
    const start = new Date(form.value.start_date)
    const end = new Date(form.value.end_date)
    const diffTime = Math.abs(end - start)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
    daysCount.value = diffDays
    
    const hall = halls.value.find(h => h.id === form.value.hall)
    if (hall) {
      pricePerDay.value = hall.price_per_day
      form.value.total_price = (diffDays * Number(hall.price_per_day || 0)) + Number(addonsTotal.value || 0)
    }
  }
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
    selected.push({ name })
  }
  form.value.additional_services_selected = selected
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
    item = { name, subservices: [{ name: sub }] }
    selected.push(item)
    form.value.additional_services_selected = selected
    return
  }
  const subs = Array.isArray(item.subservices) ? [...item.subservices] : []
  const idx = subs.findIndex(s => String(s?.name || '') === sub)
  if (idx >= 0) {
    subs.splice(idx, 1)
  } else {
    subs.push({ name: sub })
  }
  if (subs.length === 0) {
    form.value.additional_services_selected = selected.filter(s => String(s?.name || '') !== name)
  } else {
    item.subservices = subs
    form.value.additional_services_selected = selected
  }
}

const filteredBookings = computed(() => {
  return bookings.value.filter(b => {
    const q = search.value.toLowerCase().trim()
    const matchesSearch = q === '' ||
      String(b.customer_name || '').toLowerCase().includes(q) ||
      String(b.customer_email || '').toLowerCase().includes(q) ||
      String(b.hall_name || '').toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || b.status === statusFilter.value
    const matchesHall = hallFilter.value === '' || String(b.hall) === String(hallFilter.value) || String(b.hall_id) === String(hallFilter.value)
    const matchesEventType = eventTypeFilter.value === '' || (eventTypeFilter.value === 'Autres'
      ? String(b.event_type || '').startsWith('Autres: ')
      : b.event_type === eventTypeFilter.value)

    const matchesDate = dateOverlapsRange(b.start_date, b.end_date, rangeStartYmd.value, rangeEndYmd.value)

    const amount = Number(b.total_price || 0)
    const minOk = minAmount.value == null || minAmount.value === '' || amount >= Number(minAmount.value)
    const maxOk = maxAmount.value == null || maxAmount.value === '' || amount <= Number(maxAmount.value)

    return matchesSearch && matchesStatus && matchesHall && matchesEventType && matchesDate && minOk && maxOk
  })
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
  try {
    const payload = buildBookingPayload()
    if (isEditing.value) {
      await api.put(`bookings/${form.value.id}/`, payload)
      notify('Réservation mise à jour avec succès', 'success')
    } else {
      const response = await api.post('bookings/', payload)
      await fetchBookings()
      const createdBooking = bookings.value.find(booking => booking.id === response.data?.id) || response.data
      if (payload.customer_email) {
        notify(response.data?.email_sent ? 'Nouvelle réservation créée et email envoyé' : 'Nouvelle réservation créée, mais email non envoyé', response.data?.email_sent ? 'success' : 'warning')
      } else {
        notify('Nouvelle réservation créée', 'success')
      }
      if (createdBooking) {
        printReservationJeton(createdBooking, Boolean(response.data?.email_sent))
      }
    }
    showFormModal.value = false
    if (isEditing.value) {
      fetchBookings()
    }
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.additional_services_selected || data.dates || data.detail || 'Erreur lors de l\'enregistrement', 'danger')
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
    id: null,
    customer_first_name: '',
    customer_last_name: '',
    customer_email: '',
    hall: halls.value[0]?.id || '',
    event_type: 'Mariage',
    event_type_other: '',
    start_date: '',
    end_date: '',
    additional_services_selected: [],
    total_price: 0,
    status: 'pending',
  }
  daysCount.value = 0
  calendarViewMonth.value = new Date(new Date().getFullYear(), new Date().getMonth(), 1)
  calendarRangeStart.value = null
  calendarRangeEnd.value = null
  fetchCalendarRanges()
  showFormModal.value = true
}

const editBooking = (booking) => {
  closeActions()
  isEditing.value = true
  form.value = mapBookingToForm(booking)
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

const printBookingJeton = (booking) => {
  closeActions()
  printReservationJeton(booking)
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

  if (isKnown) {
    return { ...booking, customer_first_name, customer_last_name, additional_services_selected: booking?.additional_services_selected || [], event_type_other: '' }
  }

  const otherPrefix = 'Autres: '
  return {
    ...booking,
    customer_first_name,
    customer_last_name,
    additional_services_selected: booking?.additional_services_selected || [],
    event_type: 'Autres',
    event_type_other: rawEventType.startsWith(otherPrefix) ? rawEventType.slice(otherPrefix.length) : rawEventType,
  }
}

const buildBookingPayload = () => {
  const { event_type_other, customer_first_name, customer_last_name, ...payload } = form.value
  const fullName = `${String(customer_first_name || '').trim()} ${String(customer_last_name || '').trim()}`.trim()
  return {
    ...payload,
    customer_name: fullName,
    customer_email: String(payload.customer_email || '').trim(),
    event_type: normalizeEventType(form.value.event_type, event_type_other),
  }
}

const getCurrentPrintUserLabel = () => {
  if (!process.client) return 'Utilisateur'

  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    const first = String(user?.first_name || '').trim()
    const last = String(user?.last_name || '').trim()
    const full = `${first} ${last}`.trim()

    return full || user?.full_name || user?.email || user?.username || 'Utilisateur'
  } catch {
    return 'Utilisateur'
  }
}

const printReservationJeton = (booking, emailSent = null) => {
  if (!process.client) return
  const win = window.open('', '_blank', 'width=900,height=700')
  if (!win) return

  const displayId = getBookingDisplayId(booking)
  const printedBy = getCurrentPrintUserLabel()
  const reservationNumber = booking?.id || '-'
  let emailLine = `<div class="row"><span>Email client</span><strong>Non renseigne</strong></div>`
  if (booking.customer_email) {
    emailLine = `<div class="row"><span>Email client</span><strong>${escapeHtml(booking.customer_email)}</strong></div>`
    if (typeof emailSent === 'boolean') {
      emailLine += `<div class="row"><span>Email envoye</span><strong>${emailSent ? 'Oui' : 'Non'}</strong></div>`
    }
  }

  win.document.write(`<!doctype html>
  <html>
    <head>
      <meta charset="utf-8" />
      <title>${escapeHtml(documentBranding.documents?.bookingTitle || 'Jeton de reservation')}</title>
      <style>
        body { font-family: Arial, sans-serif; background: #eef2f7; padding: 24px; color: #0f172a; }
        .ticket { max-width: 820px; margin: 0 auto; background: #fff; border: 1px solid #dbe3ee; border-radius: 28px; overflow: hidden; box-shadow: 0 24px 50px rgba(15, 23, 42, 0.10); }
        .head { padding: 28px 30px 24px; background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #8b6b12 100%); color: #fff; }
        .brand { display: flex; justify-content: space-between; align-items: center; gap: 20px; }
        .brand-main { display: flex; align-items: center; gap: 16px; }
        .logo-wrap { width: 76px; height: 76px; border-radius: 22px; background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.24); display: flex; align-items: center; justify-content: center; overflow: hidden; backdrop-filter: blur(4px); }
        .logo-wrap img { width: 100%; height: 100%; object-fit: cover; }
        .brand-copy small { display: block; text-transform: uppercase; letter-spacing: 0.28em; font-size: 11px; color: rgba(255,255,255,.72); margin-bottom: 8px; }
        .brand-copy h1 { margin: 0; font-size: 30px; line-height: 1.05; }
        .brand-copy p { margin: 8px 0 0; color: rgba(255,255,255,.84); max-width: 420px; }
        .chip { display: inline-flex; align-items: center; justify-content: center; padding: 10px 14px; border-radius: 999px; background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.22); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; }
        .body { padding: 28px 30px 16px; }
        .top-meta { display: flex; justify-content: space-between; gap: 18px; flex-wrap: wrap; align-items: flex-start; margin-bottom: 20px; }
        .code-block { display: flex; flex-direction: column; gap: 8px; }
        .code-label { color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; font-size: 12px; }
        .code { display: inline-block; padding: 12px 16px; border-radius: 16px; background: linear-gradient(135deg, #eff6ff, #f8fafc); color: #1d4ed8; font-size: 24px; font-weight: 800; letter-spacing: 0.05em; border: 1px solid #bfdbfe; }
        .meta-panel { min-width: 260px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 18px; padding: 16px; }
        .meta-line { display: flex; justify-content: space-between; gap: 12px; font-size: 14px; padding: 6px 0; }
        .meta-line span { color: #64748b; font-weight: 700; }
        .meta-line strong { color: #0f172a; text-align: right; }
        .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }
        .row { display: flex; justify-content: space-between; gap: 12px; padding: 15px 16px; border: 1px solid #e2e8f0; border-radius: 16px; background: #fff; }
        .row span { color: #64748b; font-weight: 700; }
        .row strong { text-align: right; }
        .note { margin-top: 18px; padding: 16px 18px; border-radius: 16px; background: #fffaf0; border: 1px solid #fcd34d; color: #92400e; }
        .footer { margin-top: 22px; padding: 18px 30px 22px; border-top: 1px solid #e2e8f0; background: #f8fafc; }
        .footer-title { font-size: 13px; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; color: #475569; margin-bottom: 10px; }
        .footer-grid { display: grid; grid-template-columns: 1.3fr 1fr; gap: 18px; }
        .footer-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 14px 16px; }
        .footer-card p { margin: 0; color: #334155; line-height: 1.6; }
        .footer-card ul { list-style: none; padding: 0; margin: 0; }
        .footer-card li { padding: 3px 0; color: #334155; }
        @media (max-width: 720px) {
          .brand, .top-meta, .footer-grid, .grid { grid-template-columns: 1fr; display: grid; }
          .brand-main { align-items: flex-start; }
          .meta-panel { min-width: 0; }
          .row, .meta-line { flex-direction: column; }
          .row strong, .meta-line strong { text-align: left; }
        }
        @media print {
          body { background: #fff; padding: 0; }
          .ticket { border: none; box-shadow: none; }
        }
      </style>
    </head>
    <body>
      <div class="ticket">
        <div class="head">
          <div class="brand">
            <div class="brand-main">
              <div class="logo-wrap">
                <img src="${escapeHtml(documentLogoUrl)}" alt="Logo ${escapeHtml(documentBranding.name)}" />
              </div>
              <div class="brand-copy">
                <small>${escapeHtml(documentBranding.tagline)}</small>
                <h1>${escapeHtml(documentBranding.name)}</h1>
                <p>${escapeHtml(documentBranding.documents?.bookingTitle || 'Jeton officiel de reservation a presenter pour le suivi et l\'accueil.')}</p>
              </div>
            </div>
            <div class="chip">Reservation</div>
          </div>
        </div>
        <div class="body">
          <div class="top-meta">
            <div class="code-block">
              <span class="code-label">Code de reservation</span>
              <div class="code">${escapeHtml(displayId)}</div>
            </div>
            <div class="meta-panel">
              <div class="meta-line"><span>Numero</span><strong>${escapeHtml(reservationNumber)}</strong></div>
              <div class="meta-line"><span>Imprime par</span><strong>${escapeHtml(printedBy)}</strong></div>
              <div class="meta-line"><span>Date d'impression</span><strong>${escapeHtml(new Date().toLocaleString('fr-FR'))}</strong></div>
            </div>
          </div>
          <div class="grid">
            <div class="row"><span>Client</span><strong>${escapeHtml(booking.customer_name)}</strong></div>
            <div class="row"><span>Salle</span><strong>${escapeHtml(booking.hall_name || '')}</strong></div>
            <div class="row"><span>Evenement</span><strong>${escapeHtml(booking.event_type)}</strong></div>
            <div class="row"><span>Periode</span><strong>${escapeHtml(formatDateRange(booking.start_date, booking.end_date))}</strong></div>
            <div class="row"><span>Montant</span><strong>${escapeHtml(formatMoney(booking.total_price))}</strong></div>
            <div class="row"><span>Statut</span><strong>${escapeHtml(getStatusTranslation(booking.status))}</strong></div>
            ${emailLine}
          </div>
          <div class="note">
            Merci de conserver ce jeton. Il peut vous etre demande lors du suivi de votre dossier ou a l'arrivee.
          </div>
        </div>
        <div class="footer">
          <div class="footer-title">Informations de contact</div>
          <div class="footer-grid">
            <div class="footer-card">
              <p><strong>Adresse</strong><br />${escapeHtml(documentBranding.address)}</p>
            </div>
            <div class="footer-card">
              <ul>
                ${documentBranding.contacts.map(contact => `<li>${escapeHtml(contact)}</li>`).join('')}
              </ul>
            </div>
          </div>
        </div>
      </div>
      <script>
        window.onload = function () {
          window.print();
        };
      <\/script>
    </body>
  </html>`)
  win.document.close()
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

.booking-total-banner {
  position: sticky;
  top: 0;
  z-index: 5;
  display: grid;
  gap: 14px;
  margin-bottom: 18px;
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
  border: 1px solid var(--gray-200);
  border-radius: 14px;
  padding: 12px 14px;
  background: var(--gray-50);
}

.addon-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.addon-toggle {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-height: 56px;
  padding: 12px 14px;
  border: 1px solid var(--gray-200);
  border-radius: 16px;
  background: var(--white);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.addon-toggle:hover {
  border-color: var(--gray-300);
  background: var(--gray-50);
}

.addon-toggle input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.addon-toggle.is-active {
  border-color: #86efac;
  background: color-mix(in srgb, #22c55e 12%, var(--white));
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.12);
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
  font-size: 0.92rem;
  font-weight: 800;
}

.addon-toggle-copy small {
  color: var(--gray-500);
  font-size: 0.78rem;
  line-height: 1.35;
}

.addon-price {
  color: var(--gray-900);
  font-weight: 800;
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
  gap: 8px;
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
  background: rgba(15, 23, 42, 0.74);
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
  background: rgba(20, 83, 45, 0.34);
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

html[data-admin-theme="dark"] .addon-sub-head .muted-line,
html[data-admin-theme="dark"] .addon-toggle-copy small {
  color: #cbd5e1;
}

html[data-admin-theme="dark"] .service-preview-item {
  border-color: rgba(51, 65, 85, 0.95);
  background: rgba(15, 23, 42, 0.7);
}

@media (max-width: 640px) {
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
  .addon-sub-line {
    align-items: flex-start;
  }
  .addon-price {
    padding-left: 62px;
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
