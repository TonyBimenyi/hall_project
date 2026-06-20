<template>
  <div class="payments-page">
    <div class="page-header">
      <div>
        <h1>Paiements</h1>
        <p>Choisir une réservation non soldée, payer en avance ou en totalité</p>
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
        <button class="btn btn-primary btn-sm admin-head-btn" @click="openAddModal()">
          <i class="fas fa-plus"></i>
          <span class="btn-label">Nouveau paiement</span>
        </button>
      </div>
    </div>

    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            type="text"
            v-model="search"
            placeholder="Rechercher (client, email, référence)..."
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
        <select v-model="statusFilter" class="filter-select-clean">
          <option value="">Tous les statuts</option>
          <option value="paid">Payé</option>
          <option value="pending">En attente</option>
          <option value="failed">Échoué</option>
        </select>
        <select v-model="methodFilter" class="filter-select-clean">
          <option value="">Toutes les méthodes</option>
          <option v-for="m in methods" :key="m" :value="m">{{ m }}</option>
        </select>
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
        <input v-if="preset === 'custom'" v-model="customStart" type="date" class="filter-input-clean" />
        <input v-if="preset === 'custom'" v-model="customEnd" type="date" class="filter-input-clean" />
      </div>
      <div class="filter-range-note">{{ activeRangeNotice }}</div>
    </div>

    <div ref="exportRef" class="export-scope">
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-hand-holding-usd"></i></div>
        <div class="stat-info">
          <span class="label">Revenu encaissé</span>
          <span class="value success">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>{{ formatMoney(displayTotalRevenue) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div class="stat-info">
          <span class="label">Reste à encaisser</span>
          <span class="value warning">
            <span v-if="isLoading" class="skeleton-line skeleton-w-70"></span>
            <template v-else>{{ formatMoney(displayTotalRemaining) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-list-check"></i></div>
        <div class="stat-info">
          <span class="label">Réservations non soldées</span>
          <span class="value info">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayUnpaidBookings }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-exchange-alt"></i></div>
        <div class="stat-info">
          <span class="label">Transactions</span>
          <span class="value">
            <span v-if="isLoading" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayPaymentsCount }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="card section-card">
      <div class="section-header" style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <h2>Réservations à payer / séjour</h2>
        <AdminAppTablePagination
          :start="unpaidStartIndex"
          :end="unpaidEndIndex"
          :total="unpaidTotalItems"
          :can-prev="unpaidCanPrev"
          :can-next="unpaidCanNext"
          :disabled="isLoading"
          @prev="unpaidPrevPage"
          @next="unpaidNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="isLoading">
          <div v-for="n in 5" :key="`sk-unpaid-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-60"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-40"></div>
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
          <div v-for="booking in paginatedUnpaidBookings" :key="booking.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ booking.customer_name }}</div>
                <div class="admin-card-subtitle">{{ getBookingDisplayId(booking) }} • {{ bookingItemLabel(booking) }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              </div>
              <div class="admin-card-actions">
                <button v-if="toNumber(booking.remaining_amount) > 0" class="btn btn-primary btn-sm" title="Payer" @click="openAddModal(booking)">
                  <i class="fas fa-coins"></i>
                </button>
                <button
                  v-if="booking.booking_type === 'room' && !booking.checked_in_at"
                  class="btn btn-outline btn-sm"
                  :class="{ 'is-loading': stayActionLoadingId === booking.id && stayActionType === 'check_in' }"
                  :disabled="stayActionLoadingId === booking.id"
                  @click="manageStay(booking, 'check_in')"
                >
                  <i class="fas fa-right-to-bracket"></i>
                </button>
                <button
                  v-if="booking.booking_type === 'room' && booking.checked_in_at && !booking.checked_out_at"
                  class="btn btn-outline btn-sm"
                  :class="{ 'is-loading': stayActionLoadingId === booking.id && stayActionType === 'check_out' }"
                  :disabled="stayActionLoadingId === booking.id"
                  @click="manageStay(booking, 'check_out')"
                >
                  <i class="fas fa-right-from-bracket"></i>
                </button>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Code</span>
                <span class="v">{{ getBookingDisplayId(booking) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Type</span>
                <span class="v">{{ booking.booking_type === 'room' ? 'Chambre' : 'Salle' }}</span>
              </div>
              <div v-if="booking.booking_type === 'room'" class="admin-kv">
                <span class="k">Client hébergé</span>
                <span class="v">{{ booking.guest_full_name || booking.customer_name }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Total</span>
                <span class="v">{{ formatMoney(booking.total_price) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Déjà payé</span>
                <span :class="['v', { 'text-red': toNumber(booking.paid_amount) === 0, 'text-yellow': toNumber(booking.paid_amount) > 0 && toNumber(booking.paid_amount) < toNumber(booking.total_price) }]">{{ formatMoney(booking.paid_amount) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Reste</span>
                <span class="v">{{ formatMoney(booking.remaining_amount) }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!isLoading && filteredUnpaidBookings.length === 0" class="empty-cell">Aucune réservation à gérer</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('code') }" @click="toggleUnpaidSort('code')">Code <i :class="unpaidSortIconClass('code')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('customer_name') }" @click="toggleUnpaidSort('customer_name')">Client <i :class="unpaidSortIconClass('customer_name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('hall_name') }" @click="toggleUnpaidSort('hall_name')">Salle / Chambre <i :class="unpaidSortIconClass('hall_name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('start_date') }" @click="toggleUnpaidSort('start_date')">Période <i :class="unpaidSortIconClass('start_date')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('total_price') }" @click="toggleUnpaidSort('total_price')">Total <i :class="unpaidSortIconClass('total_price')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('paid_amount') }" @click="toggleUnpaidSort('paid_amount')">Déjà payé <i :class="unpaidSortIconClass('paid_amount')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('remaining_amount') }" @click="toggleUnpaidSort('remaining_amount')">Reste <i :class="unpaidSortIconClass('remaining_amount')"></i></button></th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="isLoading">
            <tr v-for="n in 5" :key="`sk-unpaid-${n}`">
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td>
                <div class="skeleton-lines">
                  <div class="skeleton-line skeleton-w-60"></div>
                  <div class="skeleton-line skeleton-w-40"></div>
                </div>
              </td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="booking in paginatedUnpaidBookings" :key="booking.id">
              <td><code>{{ getBookingDisplayId(booking) }}</code></td>
              <td>
                <div class="customer-name">{{ booking.customer_name }}</div>
                <div class="customer-email">{{ booking.customer_email }}</div>
                <div v-if="booking.booking_type === 'room'" class="customer-email">{{ booking.guest_full_name || booking.customer_name }} • {{ guestIdSummary(booking) }}</div>
              </td>
              <td>{{ bookingItemLabel(booking) }}</td>
              <td>{{ formatDateRange(booking.start_date, booking.end_date) }}</td>
              <td>{{ formatMoney(booking.total_price) }}</td>
              <td :class="{ 'text-red': toNumber(booking.paid_amount) === 0, 'text-yellow': toNumber(booking.paid_amount) > 0 && toNumber(booking.paid_amount) < toNumber(booking.total_price) }">{{ formatMoney(booking.paid_amount) }}</td>
              <td><span class="remain">{{ formatMoney(booking.remaining_amount) }}</span></td>
              <td>
                <div class="table-inline-actions">
                  <button v-if="toNumber(booking.remaining_amount) > 0" class="btn btn-primary btn-sm" @click="openAddModal(booking)">
                    <i class="fas fa-coins"></i> Payer
                  </button>
                  <button
                    v-if="booking.booking_type === 'room' && !booking.checked_in_at"
                    class="btn btn-outline btn-sm"
                    :class="{ 'is-loading': stayActionLoadingId === booking.id && stayActionType === 'check_in' }"
                    :disabled="stayActionLoadingId === booking.id"
                    @click="manageStay(booking, 'check_in')"
                  >
                    <i class="fas fa-right-to-bracket"></i> Check-in
                  </button>
                  <button
                    v-if="booking.booking_type === 'room' && booking.checked_in_at && !booking.checked_out_at"
                    class="btn btn-outline btn-sm"
                    :class="{ 'is-loading': stayActionLoadingId === booking.id && stayActionType === 'check_out' }"
                    :disabled="stayActionLoadingId === booking.id"
                    @click="manageStay(booking, 'check_out')"
                  >
                    <i class="fas fa-right-from-bracket"></i> Check-out
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredUnpaidBookings.length === 0">
              <td colspan="8" class="empty-cell">Aucune réservation à gérer</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div class="card section-card">
      <div class="section-header" style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <h2>Historique des paiements</h2>
        <AdminAppTablePagination
          :start="paymentsStartIndex"
          :end="paymentsEndIndex"
          :total="paymentsTotalItems"
          :can-prev="paymentsCanPrev"
          :can-next="paymentsCanNext"
          :disabled="isLoading"
          @prev="paymentsPrevPage"
          @next="paymentsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="isLoading">
          <div v-for="n in 6" :key="`sk-pay-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-60"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-40"></div>
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
          <div v-for="payment in paginatedPayments" :key="payment.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ payment.booking_customer_name }}</div>
                <div class="admin-card-subtitle">{{ getPaymentDisplayId(payment) }} • {{ formatDisplayDate(payment.date) }} • {{ formatMoney(payment.amount) }}</div>
              </div>
              <div class="admin-card-actions">
                <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(payment.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === payment.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewPayment(payment)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="printPaymentInvoice(payment)">
                    <i class="fas fa-file-arrow-down"></i> Télécharger la facture
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(payment)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Code</span>
                <span class="v">{{ getPaymentDisplayId(payment) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Référence</span>
                <span class="v">{{ payment.reference }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Type</span>
                <span class="v">{{ payment.kind === 'full' ? 'Total' : 'Avance' }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Méthode</span>
                <span class="v">{{ payment.method }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v"><span :class="['badge', getBadgeClass(payment.status)]">{{ translateStatus(payment.status) }}</span></span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!isLoading && filteredPayments.length === 0" class="empty-cell">Aucun paiement enregistré</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('code') }" @click="togglePaymentSort('code')">Code <i :class="paymentSortIconClass('code')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('date') }" @click="togglePaymentSort('date')">Date <i :class="paymentSortIconClass('date')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('booking_customer_name') }" @click="togglePaymentSort('booking_customer_name')">Client <i :class="paymentSortIconClass('booking_customer_name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('reference') }" @click="togglePaymentSort('reference')">Référence <i :class="paymentSortIconClass('reference')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('kind') }" @click="togglePaymentSort('kind')">Type <i :class="paymentSortIconClass('kind')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('amount') }" @click="togglePaymentSort('amount')">Montant <i :class="paymentSortIconClass('amount')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('method') }" @click="togglePaymentSort('method')">Méthode <i :class="paymentSortIconClass('method')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isPaymentSortActive('status') }" @click="togglePaymentSort('status')">Statut <i :class="paymentSortIconClass('status')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="isLoading">
            <tr v-for="n in 6" :key="`sk-payments-${n}`">
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-60"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="payment in paginatedPayments" :key="payment.id">
              <td><code>{{ getPaymentDisplayId(payment) }}</code></td>
              <td>{{ formatDisplayDate(payment.date) }}</td>
              <td>{{ payment.booking_customer_name }}</td>
              <td><code>{{ payment.reference }}</code></td>
              <td>{{ payment.kind === 'full' ? 'Total' : 'Avance' }}</td>
              <td>{{ formatMoney(payment.amount) }}</td>
              <td>{{ payment.method }}</td>
              <td><span :class="['badge', getBadgeClass(payment.status)]">{{ translateStatus(payment.status) }}</span></td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(payment.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === payment.id" class="actions-menu" @click.stop>
                    <button class="actions-item" @click="viewPayment(payment)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="actions-item" @click="printPaymentInvoice(payment)">
                      <i class="fas fa-file-arrow-down"></i> Télécharger la facture
                    </button>
                    <button class="actions-item danger" @click="confirmDelete(payment)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="filteredPayments.length === 0">
              <td colspan="9" class="empty-cell">Aucun paiement enregistré</td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    </div>

    <AdminAppModal v-model="showFormModal" title="Enregistrer un paiement" width="560px">
      <form class="admin-form" @submit.prevent="savePayment">
        <div class="form-group">
          <label class="form-label">Réservation</label>
          <select v-model="form.booking" class="form-select" required @change="onBookingChange">
            <option v-for="b in actionableBookings" :key="b.id" :value="b.id">
              {{ b.customer_name }} - {{ bookingItemLabel(b) }} (reste: {{ formatMoney(b.remaining_amount) }})
            </option>
          </select>
        </div>

        <div v-if="selectedBookingForForm" class="booking-summary">
          <div><strong>Type:</strong> {{ selectedBookingForForm.booking_type === 'room' ? 'Chambre' : 'Salle' }}</div>
          <div><strong>Unité:</strong> {{ bookingItemLabel(selectedBookingForForm) }}</div>
          <div><strong>Total:</strong> {{ formatMoney(selectedBookingForForm.total_price) }}</div>
          <div><strong>Déjà payé:</strong> {{ formatMoney(selectedBookingForForm.paid_amount) }}</div>
          <div><strong>Reste:</strong> {{ formatMoney(selectedBookingForForm.remaining_amount) }}</div>
          <div v-if="selectedBookingForForm.booking_type === 'room'"><strong>Client hébergé:</strong> {{ selectedBookingForForm.guest_full_name || selectedBookingForForm.customer_name }}</div>
          <div v-if="selectedBookingForForm.booking_type === 'room'"><strong>Pièce:</strong> {{ guestIdSummary(selectedBookingForForm) }}</div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Type de paiement</label>
            <select v-model="form.kind" class="form-select" @change="onKindChange">
              <option value="advance">Avance</option>
              <option value="full">Paiement total</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Montant (Fbu)</label>
            <input v-model="amountInput" inputmode="numeric" type="text" class="form-input" placeholder="0" required />
          </div>
        </div>

        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Date</label>
            <input v-model="form.date" type="date" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Méthode</label>
            <select v-model="form.method" class="form-select" required>
              <option value="Virement">Virement</option>
              <option value="Espèces">Espèces</option>
              <option value="Carte">Carte</option>
              <option value="Mobile Money">Mobile Money</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Référence</label>
          <input v-model="form.reference" type="text" class="form-input" required />
        </div>

        <div v-if="selectedBookingForForm?.booking_type === 'room'" class="form-group">
          <label class="form-label">Gestion du séjour</label>
          <select v-model="form.room_action" class="form-select">
            <option value="none">Aucune action</option>
            <option v-if="!selectedBookingForForm.checked_in_at" value="check_in">Valider le check-in</option>
            <option v-if="selectedBookingForForm.checked_in_at && !selectedBookingForForm.checked_out_at" value="check_out">Valider le check-out</option>
          </select>
          <small class="form-hint">Le check-in exige un paiement marqué comme payé et une pièce d'identité déjà renseignée.</small>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingPayment }" :disabled="savingPayment" @click="savePayment">
          Enregistrer
        </button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showViewModal" title="Détails du paiement" width="580px">
      <div v-if="selectedPayment" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ String(getPaymentDisplayId(selectedPayment) || 'PA').slice(0, 2).toUpperCase() }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ getPaymentDisplayId(selectedPayment) }}</div>
            <h3>{{ selectedPayment.booking_customer_name || 'Client' }}</h3>
            <p>{{ paymentBookingItemLabel(selectedPayment) || '-' }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', getBadgeClass(selectedPayment.status)]">{{ translateStatus(selectedPayment.status) }}</span>
            <span class="badge badge-info">{{ formatMoney(selectedPayment.amount) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Paiement</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Réservation</span><span class="entity-view-value">{{ selectedPayment.booking_code || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Type</span><span class="entity-view-value">{{ selectedPayment.booking_type === 'room' ? 'Chambre' : 'Salle' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Salle / Chambre</span><span class="entity-view-value">{{ paymentBookingItemLabel(selectedPayment) || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Période</span><span class="entity-view-value">{{ formatDateRange(selectedPayment.booking_start_date, selectedPayment.booking_end_date) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Paiement</span><span class="entity-view-value">{{ selectedPayment.kind === 'full' ? 'Paiement total' : 'Avance' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Référence</span><span class="entity-view-value">{{ selectedPayment.reference || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Méthode</span><span class="entity-view-value">{{ selectedPayment.method || '-' }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Suivi</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Montant</span><span class="entity-view-value">{{ formatMoney(selectedPayment.amount) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Reste après paiement</span><span class="entity-view-value">{{ formatMoney(selectedPayment.booking_remaining_amount) }}</span></div>
              <div v-if="selectedPayment.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Client hébergé</span><span class="entity-view-value">{{ selectedPayment.booking_guest_full_name || selectedPayment.booking_customer_name }}</span></div>
              <div v-if="selectedPayment.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Pièce</span><span class="entity-view-value">{{ guestIdSummary({ guest_id_type: selectedPayment.booking_guest_id_type, guest_id_number: selectedPayment.booking_guest_id_number }) }}</span></div>
              <div v-if="selectedPayment.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Statut chambre</span><span class="entity-view-value">{{ roomStatusLabel(selectedPayment.booking_room_status) }}</span></div>
              <div v-if="selectedPayment.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Check-in</span><span class="entity-view-value">{{ selectedPayment.booking_checked_in_at ? formatDateTime(selectedPayment.booking_checked_in_at) : 'Non effectué' }}</span></div>
              <div v-if="selectedPayment.booking_type === 'room'" class="entity-view-item"><span class="entity-view-label">Check-out</span><span class="entity-view-value">{{ selectedPayment.booking_checked_out_at ? formatDateTime(selectedPayment.booking_checked_out_at) : 'Non effectué' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé le</span><span class="entity-view-value">{{ formatDisplayDate(selectedPayment.created_at) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedPayment.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedPayment.updated_by_name || selectedPayment.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ translateStatus(selectedPayment.status) }}</span></div>
            </div>
          </section>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-outline" @click="printPaymentInvoice(selectedPayment)">Télécharger la facture</button>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Supprimer le paiement <strong>{{ selectedPayment?.reference }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingPayment }" :disabled="deletingPayment" @click="deletePayment">
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
import { useDateFormat } from '~/composables/useDateFormat'
import { useTableSort } from '~/composables/useTableSort'
import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const { escapeHtml } = useDocumentBranding()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName, openPrintPreviewHtml } = useAdminExportDocuments()
const { formatMoney, moneyInputModel } = useMoney()
const { formatDateRange, formatDisplayDate, formatDateTime } = useDateFormat()

const payments = ref([])
const bookings = ref([])
const exportRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const search = ref('')
const statusFilter = ref('')
const methodFilter = ref('')
const preset = ref('28d')
const customStart = ref('')
const customEnd = ref('')
const loadingPayments = ref(false)
const loadingBookingsData = ref(false)
const isMobile = ref(false)
const filtersOpen = ref(false)
const openActionsId = ref(null)
const savingPayment = ref(false)
const deletingPayment = ref(false)
const stayActionLoadingId = ref(null)
const stayActionType = ref('')

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const resetFilters = () => {
  search.value = ''
  statusFilter.value = ''
  methodFilter.value = ''
  preset.value = '28d'
  customStart.value = ''
  customEnd.value = ''
}

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

const isLoading = computed(() => loadingPayments.value || loadingBookingsData.value)

const exportXls = async () => {
  if (!exportRef.value) return
  exportingXls.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(exportRef.value, { htmlMode: 'inner', removeActionsColumn: true })
  downloadHtmlAsXls({ type: 'payments', contentHtml })
  setTimeout(() => {
    exportingXls.value = false
  }, 350)
}

const exportPdf = async () => {
  if (!exportRef.value) return
  exportingPdf.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(exportRef.value, { htmlMode: 'inner', removeActionsColumn: true })
  const html = buildPdfDocumentHtml({
    title: 'Paiements',
    documentTitle: buildExportFileName('payments', 'pdf').replace(/\.pdf$/, ''),
    subtitle: 'Etat des paiements et des réservations à solder exporté depuis l’administration.',
    typeLabel: 'Paiements PDF',
    tableTitles: ['Liste des paiements', 'Réservations à solder'],
    periodLabel: rangeStartYmd.value && rangeEndYmd.value ? `${rangeStartYmd.value} -> ${rangeEndYmd.value}` : 'Toutes les dates',
    contentHtml,
  })
  const ok = await downloadPdfHtml({ html, fileName: buildExportFileName('payments', 'pdf') })
  if (!ok) {
    exportingPdf.value = false
    return
  }
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

const buildPaymentPdfFileName = (prefix, identifier) => {
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

const buildInvoicePdfHtml = (payment) => {
  const paymentCode = getPaymentDisplayId(payment)
  const reservationCode = String(payment?.booking_code || '').trim() || `Reservation #${payment?.booking || '-'}`
  const paymentTypeLabel = payment?.kind === 'full' ? 'Paiement total' : 'Avance'
  const reservationTypeLabel = payment?.booking_type === 'room' ? 'Chambre' : 'Salle'
  const periodLabel = formatDateRange(payment?.booking_start_date, payment?.booking_end_date)
  const detailRows = [
    ['Paiement', paymentCode],
    ['Réservation', reservationCode],
    ['Date', formatDisplayDate(payment?.date)],
    ['Client', payment?.booking_customer_name || 'Client'],
    ['Email client', payment?.booking_customer_email || '-'],
    ['Référence', payment?.reference || '-'],
    ['Méthode', payment?.method || '-'],
    ['Type', paymentTypeLabel],
    ['Type de réservation', reservationTypeLabel],
    [reservationTypeLabel, paymentBookingItemLabel(payment) || '-'],
    ['Période', periodLabel || '-'],
    ['Statut', translateStatus(payment?.status)],
    ['Montant payé', formatMoney(payment?.amount)],
    ['Total réservation', formatMoney(payment?.booking_total_price)],
    ['Reste à payer', formatMoney(payment?.booking_remaining_amount)],
  ]

  return buildPdfDocumentHtml({
    title: 'Facture de paiement',
    documentTitle: `Facture ${paymentCode}`,
    subtitle: 'Facture generee automatiquement apres enregistrement du paiement.',
    typeLabel: 'Facture PDF',
    tableTitle: 'Détails du paiement',
    tableTitles: ['Détails du paiement'],
    periodLabel,
    showMeta: false,
    contentHtml: `
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

const openPaymentInvoicePrintPreview = (payment) => {
  if (!payment || !process.client) return
  closeActions()
  const html = buildInvoicePdfHtml(payment)
  const ok = openPrintPreviewHtml({
    html,
    title: `Facture ${getPaymentDisplayId(payment)}`,
  })
  if (!ok) {
    notify('Impossible d’ouvrir l’aperçu d’impression de la facture', 'warning')
  }
}

const printPaymentInvoice = async (payment) => {
  if (!payment || !process.client) return
  closeActions()
  const html = buildInvoicePdfHtml(payment)
  const ok = await downloadPdfHtml({
    html,
    fileName: buildPaymentPdfFileName('facture-paiement', getPaymentDisplayId(payment)),
  })
  if (!ok) {
    notify('Impossible de télécharger la facture PDF', 'warning')
  }
}

const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const selectedPayment = ref(null)

// #region debug-point A:payment-debug-reporter
const reportPaymentDebug = (hypothesisId, msg, data = {}) => {
  try {
    fetch('http://127.0.0.1:7777/event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: 'post-broken-pipe',
        runId: 'pre-fix',
        hypothesisId,
        location: 'pages/admin/payments.vue',
        msg: `[DEBUG] ${msg}`,
        data,
        ts: Date.now(),
      }),
    }).catch(() => {})
  } catch {
  }
}
// #endregion

const form = ref({
  booking: null,
  date: new Date().toISOString().split('T')[0],
  reference: '',
  amount: 0,
  method: 'Virement',
  kind: 'advance',
  status: 'paid',
  room_action: 'none',
})
const amountInput = moneyInputModel(form, 'amount')

const toNumber = (v) => Number(v || 0)
const unpaidOnlyBookings = computed(() => bookings.value.filter(b => toNumber(b.remaining_amount) > 0 && b.status !== 'cancelled'))
const actionableBookings = computed(() => bookings.value.filter((booking) => {
  if (booking.status === 'cancelled') return false
  if (toNumber(booking.remaining_amount) > 0) return true
  return booking.booking_type === 'room' && !booking.checked_out_at
}))
const roomStatusLabel = (status) => ({
  available: 'Disponible',
  reserved: 'Réservée',
  occupied: 'Occupée',
  cleaning: 'Nettoyage',
  maintenance: 'Maintenance',
}[String(status || 'available')] || String(status || 'available'))
const guestIdSummary = (booking) => {
  const type = String(booking?.guest_id_type || '').trim()
  const number = String(booking?.guest_id_number || '').trim()
  if (!type && !number) return '-'
  const labelMap = {
    passport: 'Passeport',
    id_card: 'Carte d’identité',
    driving_license: 'Permis de conduire',
  }
  return [labelMap[type] || type || 'Pièce', number].filter(Boolean).join(' • ')
}
const bookingItemLabel = (booking) => booking?.booking_type === 'room' ? (booking?.room_display || '-') : (booking?.hall_name || '-')
const paymentBookingItemLabel = (payment) => payment?.booking_type === 'room' ? (payment?.booking_room_display || '-') : (payment?.booking_hall_name || '-')
const filteredUnpaidBookings = computed(() => {
  const q = search.value.toLowerCase().trim()
  return actionableBookings.value.filter((b) => {
    const matchesSearch = q === '' ||
      String(b.customer_name || '').toLowerCase().includes(q) ||
      String(b.customer_email || '').toLowerCase().includes(q) ||
      String(b.hall_name || '').toLowerCase().includes(q) ||
      String(b.room_display || '').toLowerCase().includes(q) ||
      String(b.guest_full_name || '').toLowerCase().includes(q) ||
      String(b.guest_id_number || '').toLowerCase().includes(q)
    const matchesDate = inRangeYmd(b.created_at, rangeStartYmd.value, rangeEndYmd.value)
    return matchesSearch && matchesDate
  })
})

const {
  sortedItems: sortedUnpaidBookings,
  toggleSort: toggleUnpaidSort,
  isSortActive: isUnpaidSortActive,
  sortIconClass: unpaidSortIconClass,
} = useTableSort(filteredUnpaidBookings, {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    hall_name: booking => booking?.booking_type === 'room' ? (booking?.room_display || '') : (booking?.hall_name || ''),
    total_price: booking => toNumber(booking?.total_price),
    paid_amount: booking => toNumber(booking?.paid_amount),
    remaining_amount: booking => toNumber(booking?.remaining_amount),
  },
})

const getBookingDisplayId = (booking) => booking?.code || 'LBR00000001'

const filteredPayments = computed(() => {
  const q = search.value.toLowerCase().trim()
  return (payments.value || []).filter((p) => {
    const matchesSearch = q === '' ||
      String(p.booking_customer_name || '').toLowerCase().includes(q) ||
      String(p.reference || '').toLowerCase().includes(q) ||
      String(p.booking_hall_name || '').toLowerCase().includes(q) ||
      String(p.booking_room_display || '').toLowerCase().includes(q) ||
      String(p.booking_guest_full_name || '').toLowerCase().includes(q) ||
      String(p.booking_guest_id_number || '').toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || p.status === statusFilter.value
    const matchesMethod = methodFilter.value === '' || p.method === methodFilter.value
    const matchesDate = inRangeYmd(p.created_at || p.date, rangeStartYmd.value, rangeEndYmd.value)
    return matchesSearch && matchesStatus && matchesMethod && matchesDate
  })
})

const {
  sortedItems: sortedPayments,
  toggleSort: togglePaymentSort,
  isSortActive: isPaymentSortActive,
  sortIconClass: paymentSortIconClass,
} = useTableSort(filteredPayments, {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    amount: payment => toNumber(payment?.amount),
  },
})

const getPaymentDisplayId = (payment) => payment?.code || 'LBP00000001'

const {
  paginatedItems: paginatedPayments,
  totalItems: paymentsTotalItems,
  startIndex: paymentsStartIndex,
  endIndex: paymentsEndIndex,
  canPrev: paymentsCanPrev,
  canNext: paymentsCanNext,
  prevPage: paymentsPrevPage,
  nextPage: paymentsNextPage,
} = usePagination(sortedPayments, 5)

const {
  paginatedItems: paginatedUnpaidBookings,
  totalItems: unpaidTotalItems,
  startIndex: unpaidStartIndex,
  endIndex: unpaidEndIndex,
  canPrev: unpaidCanPrev,
  canNext: unpaidCanNext,
  prevPage: unpaidPrevPage,
  nextPage: unpaidNextPage,
} = usePagination(sortedUnpaidBookings, 5)

const selectedBookingForForm = computed(() => actionableBookings.value.find(b => b.id === form.value.booking) || null)
const totalRevenue = computed(() => filteredPayments.value.filter(p => p.status === 'paid').reduce((a, p) => a + toNumber(p.amount), 0))
const totalRemaining = computed(() => filteredUnpaidBookings.value.reduce((a, b) => a + toNumber(b.remaining_amount), 0))
const methods = computed(() => Array.from(new Set((filteredPayments.value || []).map(p => p.method).filter(Boolean))).sort())

const displayTotalRevenue = ref(0)
const displayTotalRemaining = ref(0)
const displayUnpaidBookings = ref(0)
const displayPaymentsCount = ref(0)

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

watch(totalRevenue, (v) => animateCounter(displayTotalRevenue, v), { immediate: true })
watch(totalRemaining, (v) => animateCounter(displayTotalRemaining, v), { immediate: true })
watch(() => unpaidOnlyBookings.value.length, (v) => animateCounter(displayUnpaidBookings, v), { immediate: true })
watch(() => filteredPayments.value.length, (v) => animateCounter(displayPaymentsCount, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const fetchPayments = async () => {
  loadingPayments.value = true
  try {
    const { data } = await api.get('payments/')
    payments.value = Array.isArray(data) ? data : []
  } catch {
    notify('Erreur lors du chargement des paiements', 'danger')
  } finally {
    loadingPayments.value = false
  }
}

const fetchBookings = async () => {
  loadingBookingsData.value = true
  try {
    const { data } = await api.get('bookings/')
    bookings.value = Array.isArray(data) ? data : []
  } catch {
    notify('Erreur lors du chargement des réservations', 'danger')
  } finally {
    loadingBookingsData.value = false
  }
}

const resetForm = () => {
  form.value = {
    booking: actionableBookings.value[0]?.id || null,
    date: new Date().toISOString().split('T')[0],
    reference: 'PAY-' + Math.floor(1000 + Math.random() * 9000),
    amount: 0,
    method: 'Virement',
    kind: 'advance',
    status: 'paid',
    room_action: 'none',
  }
}

const syncPaymentKindWithAmount = () => {
  const booking = selectedBookingForForm.value
  if (!booking) return

  const remaining = toNumber(booking.remaining_amount)
  const amount = toNumber(form.value.amount)

  if (remaining <= 0) {
    form.value.kind = 'full'
    return
  }

  form.value.kind = amount === remaining ? 'full' : 'advance'
}

const onKindChange = () => {
  if (!selectedBookingForForm.value) return
  if (form.value.kind === 'full') {
    form.value.amount = toNumber(selectedBookingForForm.value.remaining_amount)
  }
  syncPaymentKindWithAmount()
}

const onBookingChange = () => {
  if (!selectedBookingForForm.value) return
  form.value.room_action = 'none'
  if (form.value.kind === 'full') {
    form.value.amount = toNumber(selectedBookingForForm.value.remaining_amount)
  } else if (form.value.amount <= 0) {
    form.value.amount = Math.min(100000, toNumber(selectedBookingForForm.value.remaining_amount))
  }
  syncPaymentKindWithAmount()
}

watch(() => form.value.amount, () => {
  syncPaymentKindWithAmount()
})

watch(selectedBookingForForm, () => {
  syncPaymentKindWithAmount()
})

const manageStay = async (booking, action) => {
  if (!booking?.id || stayActionLoadingId.value) return
  stayActionLoadingId.value = booking.id
  stayActionType.value = action
  try {
    await api.post(`bookings/${booking.id}/${action === 'check_in' ? 'check-in' : 'check-out'}/`)
    notify(action === 'check_in' ? 'Check-in enregistré' : 'Check-out enregistré', 'success')
    await Promise.all([fetchBookings(), fetchPayments()])
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.detail || 'Impossible de mettre à jour le séjour', 'danger')
  } finally {
    stayActionLoadingId.value = null
    stayActionType.value = ''
  }
}

const openAddModal = (booking = null) => {
  resetForm()
  if (booking?.id) {
    form.value.booking = booking.id
  } else if (route.query.booking) {
    form.value.booking = Number(route.query.booking)
  }
  onBookingChange()
  showFormModal.value = true
}

const savePayment = async () => {
  if (savingPayment.value) return
  if (!selectedBookingForForm.value) {
    notify('Sélectionnez une réservation', 'warning')
    return
  }
  const remaining = toNumber(selectedBookingForForm.value.remaining_amount)
  if (form.value.amount <= 0) {
    notify('Montant invalide', 'warning')
    return
  }
  if (form.value.amount > remaining) {
    notify('Le montant dépasse le reste à payer', 'warning')
    return
  }
  savingPayment.value = true
  try {
    // #region debug-point A:payment-submit
    reportPaymentDebug('A', 'savePayment submit', {
      booking: form.value.booking,
      amount: form.value.amount,
      kind: form.value.kind,
      status: form.value.status,
      roomAction: form.value.room_action,
      selectedBookingId: selectedBookingForForm.value?.id ?? null,
      remaining,
    })
    // #endregion
    const { data } = await api.post('payments/', form.value)
    // #region debug-point B:payment-post-success
    reportPaymentDebug('B', 'payment post success before refresh', {
      responseId: data?.id ?? null,
      responseKeys: Object.keys(data || {}),
      invoiceEmailSent: data?.invoice_email_sent ?? null,
    })
    // #endregion
    notify('Paiement enregistré avec succès', 'success')
    showFormModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
    const createdPayment = payments.value.find(item => item.id === data?.id) || data
    // #region debug-point D:payment-after-refresh
    reportPaymentDebug('D', 'payment refresh completed', {
      paymentsCount: payments.value.length,
      bookingsCount: bookings.value.length,
      createdPaymentFound: Boolean(createdPayment),
      createdPaymentId: createdPayment?.id ?? null,
    })
    // #endregion
    await nextTick()
    // #region debug-point E:payment-before-print
    reportPaymentDebug('E', 'payment about to print invoice', {
      createdPaymentId: createdPayment?.id ?? null,
      responseId: data?.id ?? null,
    })
    // #endregion
    openPaymentInvoicePrintPreview(createdPayment)
  } catch (error) {
    const data = error?.response?.data || {}
    // #region debug-point C:payment-submit-error
    reportPaymentDebug('C', 'savePayment catch', {
      message: error?.message || null,
      status: error?.response?.status ?? null,
      data,
    })
    // #endregion
    notify(data.room_action || data.amount || data.booking || data.detail || 'Erreur lors de l\'enregistrement du paiement', 'danger')
  } finally {
    savingPayment.value = false
  }
}

const viewPayment = (payment) => {
  closeActions()
  selectedPayment.value = payment
  showViewModal.value = true
}

const confirmDelete = (payment) => {
  closeActions()
  selectedPayment.value = payment
  showDeleteModal.value = true
}

const deletePayment = async () => {
  if (deletingPayment.value || !selectedPayment.value?.id) return
  deletingPayment.value = true
  try {
    await api.delete(`payments/${selectedPayment.value.id}/`)
    notify('Paiement supprimé', 'danger')
    showDeleteModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
  } catch {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingPayment.value = false
  }
}

const translateStatus = (status) => ({ paid: 'Complété', pending: 'En attente', failed: 'Échoué' }[status] || status)
const getBadgeClass = (status) => ({ paid: 'badge-success', pending: 'badge-warning', failed: 'badge-danger' }[status] || '')

const openPaymentFromQuery = () => {
  const viewId = Number(route.query.view)
  if (!viewId) return
  const payment = payments.value.find(item => Number(item?.id) === viewId)
  if (!payment) return
  selectedPayment.value = payment
  showViewModal.value = true
}

watch(() => `${route.query.view || ''}:${route.query.focus || ''}:${payments.value.length}`, () => {
  openPaymentFromQuery()
})

onMounted(async () => {
  await Promise.all([fetchPayments(), fetchBookings()])
  if (route.query.booking) openAddModal()
  openPaymentFromQuery()
  if (process.client) {
    const update = () => {
      const nextIsMobile = window.innerWidth <= 992
      if (nextIsMobile !== isMobile.value) {
        isMobile.value = nextIsMobile
        filtersOpen.value = !nextIsMobile
      } else {
        isMobile.value = nextIsMobile
      }
    }
    update()
    window.addEventListener('resize', update)
    onBeforeUnmount(() => window.removeEventListener('resize', update))

    const onDocClick = () => { openActionsId.value = null }
    document.addEventListener('click', onDocClick)
    onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
  }
})
</script>

<style scoped>
.payments-page { padding: 0; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-8); gap: var(--space-4); flex-wrap: wrap; }
.page-header h1 { font-size: 1.75rem; font-weight: 800; margin: 0; color: #0f172a; }
.page-header p { color: #64748b; margin-top: .35rem; }
.header-actions { display: inline-flex; gap: .5rem; flex-wrap: wrap; align-items: center; justify-content: flex-end; }

.controls { display: flex; gap: var(--space-4); margin-bottom: var(--space-8); padding: var(--space-4) var(--space-6); align-items: center; flex-wrap: wrap; }
.controls-top { width: 100%; display: flex; gap: var(--space-3); align-items: center; }
.filters-panel { width: 100%; display: flex; gap: var(--space-4); flex-wrap: wrap; align-items: center; }
.filter-range-note {
  margin-top: 0.75rem;
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 700;
}
.filters-toggle { display: none; width: 42px; height: 42px; border: 1px solid #e2e8f0; background: #f8fafc; color: #475569; }
.filters-toggle.active { background: rgba(212, 175, 55, .18); border-color: rgba(212, 175, 55, .35); color: #0f172a; }
.filters-panel .filter-select-clean, .filters-panel .filter-input-clean { flex: 1 1 190px; }
.search-wrapper { flex: 1 1 320px; position: relative; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: #94a3b8; font-size: 0.9rem; }
.search-input-clean { width: 100%; padding: 0.625rem 1rem 0.625rem 2.5rem; border: 1px solid #e2e8f0; border-radius: var(--rounded-md); font-size: 0.9rem; background: #f8fafc; transition: var(--transition-fast); }
.search-input-clean:focus { background: white; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); }
.filter-select-clean { padding: 0.625rem 2rem 0.625rem 1rem; border: 1px solid #e2e8f0; border-radius: var(--rounded-md); font-size: 0.9rem; background: #f8fafc; color: #475569; font-weight: 600; cursor: pointer; }
.filter-input-clean { padding: 0.625rem 1rem; border: 1px solid #e2e8f0; border-radius: var(--rounded-md); font-size: 0.9rem; background: #f8fafc; color: #475569; font-weight: 600; transition: var(--transition-fast); }
.filter-input-clean:focus { background: white; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-5); margin-bottom: var(--space-8); }
.stat-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); }
.stat-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.stat-icon.success { background: #ecfdf3; color: #16a34a; }
.stat-icon.warning { background: #fffbeb; color: #d97706; }
.stat-icon.info { background: #eff6ff; color: #2563eb; }
.stat-icon.primary { background: #eef2ff; color: #4338ca; }
.label { display: block; color: #94a3b8; font-size: .72rem; text-transform: uppercase; font-weight: 700; letter-spacing: .05em; }
.value { font-size: 1.2rem; font-weight: 800; color: #0f172a; }
.value.success { color: #16a34a; }
.value.warning { color: #d97706; }
.value.info { color: #2563eb; }
.section-card { margin-bottom: var(--space-8); }
.section-header { margin-bottom: var(--space-4); }
.section-header h2 { font-size: 1rem; font-weight: 800; color: #1e293b; }
.customer-name { font-weight: 700; color: var(--gray-900); }
.customer-email { font-size: .8rem; color: var(--gray-500); }
.remain { color: #b45309; font-weight: 800; }
.text-red { color: #dc2626; font-weight: 800; }
.text-yellow { color: #d97706; font-weight: 800; }
.empty-cell { text-align: center; color: #94a3b8; font-weight: 600; padding: 1rem; }
.table-inline-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.booking-summary {
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 14px;
  padding: 0.95rem 1rem;
  display: grid;
  gap: 0.45rem;
  margin-bottom: 0.25rem;
  color: var(--gray-700);
}

.booking-summary strong {
  color: var(--gray-900);
}

html[data-admin-theme="dark"] .booking-summary {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(51, 65, 85, 0.95);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}
.btn-sm { padding: .45rem .75rem; font-size: .78rem; }
.btn-icon { width: 32px; height: 32px; background: #f8fafc; color: #64748b; }
.entity-view-modal { display: grid; gap: 18px; }
.entity-view-hero { display: flex; align-items: center; gap: 16px; padding: 18px; border-radius: 20px; background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%); color: #ffffff; }
.entity-view-avatar { width: 64px; height: 64px; border-radius: 18px; background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.18); display: flex; align-items: center; justify-content: center; font-size: 1rem; font-weight: 800; letter-spacing: .08em; flex-shrink: 0; }
.entity-view-main { min-width: 0; flex: 1; }
.entity-view-code { display: inline-flex; align-items: center; padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,0.14); font-size: .72rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }
.entity-view-main h3 { margin: 6px 0 4px; font-size: 1.15rem; font-weight: 800; color: #ffffff; }
.entity-view-main p { margin: 0; color: rgba(255,255,255,.78); font-size: .92rem; }
.entity-view-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }
.entity-view-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.entity-view-card { border: 1px solid #e2e8f0; border-radius: 18px; background: #ffffff; padding: 16px; }
.entity-view-card-title { margin-bottom: 14px; font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #64748b; }
.entity-view-list { display: grid; gap: 10px; }
.entity-view-item { display: flex; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 14px; background: #f8fafc; border: 1px solid #e2e8f0; }
.entity-view-label { color: #64748b; font-size: .82rem; font-weight: 700; }
.entity-view-value { color: #0f172a; font-size: .9rem; font-weight: 700; text-align: right; word-break: break-word; }

.actions-cell { width: 1%; white-space: nowrap; }
.actions-dropdown { position: relative; display: inline-flex; }
.actions-menu { position: absolute; top: calc(100% + 8px); right: 0; min-width: 180px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12); padding: 6px; z-index: 30; }
.actions-item { width: 100%; display: flex; align-items: center; gap: 10px; padding: 10px 12px; border-radius: 10px; color: #334155; font-weight: 700; font-size: 0.9rem; text-align: left; }
.actions-item:hover { background: #f8fafc; color: #0f172a; }
.actions-item.danger { color: #dc2626; }
.actions-item.danger:hover { background: #fef2f2; color: #b91c1c; }

@media (max-width: 992px) {
  .filters-toggle { display: inline-flex; align-items: center; justify-content: center; }
  .filters-panel { gap: var(--space-3); }
}

@media (max-width: 640px) {
  .entity-view-hero { flex-direction: column; align-items: flex-start; }
  .entity-view-badges { align-items: flex-start; flex-direction: row; flex-wrap: wrap; }
  .entity-view-grid { grid-template-columns: 1fr; }
  .entity-view-item { flex-direction: column; }
  .entity-view-value { text-align: left; }
}
</style>
