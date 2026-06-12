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
          <option value="7d">7 jours</option>
          <option value="28d">28 jours</option>
          <option value="90d">90 jours</option>
          <option value="this_month">Ce mois</option>
          <option value="last_month">Mois dernier</option>
          <option value="year">Cette année</option>
          <option value="custom">Personnalisé</option>
        </select>
        <input v-if="preset === 'custom'" v-model="customStart" type="date" class="filter-input-clean" />
        <input v-if="preset === 'custom'" v-model="customEnd" type="date" class="filter-input-clean" />
      </div>
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
        <h2>Réservations à payer</h2>
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
                <div class="admin-card-subtitle">{{ getBookingDisplayId(booking) }} • {{ booking.hall_name }} • {{ formatDateRange(booking.start_date, booking.end_date) }}</div>
              </div>
              <div class="admin-card-actions">
                <button class="btn btn-primary btn-sm" title="Payer" @click="openAddModal(booking)">
                  <i class="fas fa-coins"></i>
                </button>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Code</span>
                <span class="v">{{ getBookingDisplayId(booking) }}</span>
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
        <div v-if="!isLoading && filteredUnpaidBookings.length === 0" class="empty-cell">Toutes les réservations sont soldées</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('code') }" @click="toggleUnpaidSort('code')">Code <i :class="unpaidSortIconClass('code')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('customer_name') }" @click="toggleUnpaidSort('customer_name')">Client <i :class="unpaidSortIconClass('customer_name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isUnpaidSortActive('hall_name') }" @click="toggleUnpaidSort('hall_name')">Salle <i :class="unpaidSortIconClass('hall_name')"></i></button></th>
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
              </td>
              <td>{{ booking.hall_name }}</td>
              <td>{{ formatDateRange(booking.start_date, booking.end_date) }}</td>
              <td>{{ formatMoney(booking.total_price) }}</td>
              <td :class="{ 'text-red': toNumber(booking.paid_amount) === 0, 'text-yellow': toNumber(booking.paid_amount) > 0 && toNumber(booking.paid_amount) < toNumber(booking.total_price) }">{{ formatMoney(booking.paid_amount) }}</td>
              <td><span class="remain">{{ formatMoney(booking.remaining_amount) }}</span></td>
              <td>
                <button class="btn btn-primary btn-sm" @click="openAddModal(booking)">
                  <i class="fas fa-coins"></i> Payer
                </button>
              </td>
            </tr>
            <tr v-if="filteredUnpaidBookings.length === 0">
              <td colspan="8" class="empty-cell">Toutes les réservations sont soldées</td>
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
                    <i class="fas fa-print"></i> Imprimer la facture
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
                      <i class="fas fa-print"></i> Imprimer la facture
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
            <option v-for="b in unpaidBookings" :key="b.id" :value="b.id">
              {{ b.customer_name }} - {{ b.hall_name }} (reste: {{ formatMoney(b.remaining_amount) }})
            </option>
          </select>
        </div>

        <div v-if="selectedBookingForForm" class="booking-summary">
          <div><strong>Total:</strong> {{ formatMoney(selectedBookingForForm.total_price) }}</div>
          <div><strong>Déjà payé:</strong> {{ formatMoney(selectedBookingForForm.paid_amount) }}</div>
          <div><strong>Reste:</strong> {{ formatMoney(selectedBookingForForm.remaining_amount) }}</div>
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
            <p>{{ selectedPayment.booking_hall_name || '-' }}</p>
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
              <div class="entity-view-item"><span class="entity-view-label">Période</span><span class="entity-view-value">{{ formatDateRange(selectedPayment.booking_start_date, selectedPayment.booking_end_date) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Type</span><span class="entity-view-value">{{ selectedPayment.kind === 'full' ? 'Paiement total' : 'Avance' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Référence</span><span class="entity-view-value">{{ selectedPayment.reference || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Méthode</span><span class="entity-view-value">{{ selectedPayment.method || '-' }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Suivi</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Montant</span><span class="entity-view-value">{{ formatMoney(selectedPayment.amount) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Reste après paiement</span><span class="entity-view-value">{{ formatMoney(selectedPayment.booking_remaining_amount) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Créé par</span><span class="entity-view-value">{{ selectedPayment.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Dernière action</span><span class="entity-view-value">{{ selectedPayment.updated_by_name || selectedPayment.created_by_name || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Statut</span><span class="entity-view-value">{{ translateStatus(selectedPayment.status) }}</span></div>
            </div>
          </section>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-outline" @click="printPaymentInvoice(selectedPayment)">Imprimer la facture</button>
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
import { useDisplayIds } from '~/composables/useDisplayIds'
import { useTableSort } from '~/composables/useTableSort'
import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'

definePageMeta({ layout: 'admin' })
const route = useRoute()
const { documentBranding, documentLogoUrl, escapeHtml } = useDocumentBranding()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName } = useAdminExportDocuments()
const { formatMoney, moneyInputModel } = useMoney()
const { formatDateRange, formatDisplayDate } = useDateFormat()
const { buildMonthlySequenceMap } = useDisplayIds()

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

const inRangeYmd = (ymd, rangeStart, rangeEnd) => {
  const v = String(ymd || '').slice(0, 10)
  if (!rangeStart || !rangeEnd) return true
  if (!v) return false
  return v >= rangeStart && v <= rangeEnd
}

const dateOverlapsRange = (start, end, rangeStart, rangeEnd) => {
  const s = String(start || '').slice(0, 10)
  const e = String(end || '').slice(0, 10)
  if (!rangeStart || !rangeEnd) return true
  if (!s || !e) return false
  return s <= rangeEnd && e >= rangeStart
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

const buildInvoiceHtml = (payment) => {
  const typeLabel = payment?.kind === 'full' ? 'Paiement total' : 'Avance'
  const reservationCode = String(payment?.booking_code || '').trim() || `Reservation #${payment?.booking || '-'}`
  const paymentCode = getPaymentDisplayId(payment)

  return `<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Facture ${escapeHtml(paymentCode)}</title>
  <style>
    :root {
      color-scheme: light;
      --paper-width: 80mm;
      --text: #111827;
      --muted: #6b7280;
      --line: #d1d5db;
      --soft: #f9fafb;
      --brand: #111827;
    }
    @page {
      size: 80mm auto;
      margin: 4mm;
    }
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      padding: 12px;
      font-family: Inter, Arial, sans-serif;
      font-size: 12px;
      line-height: 1.45;
      color: var(--text);
      background: #eef2f7;
    }
    .receipt {
      width: 100%;
      max-width: var(--paper-width);
      margin: 0 auto;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 14px 12px 16px;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    .center {
      text-align: center;
    }
    .brand-logo {
      width: 52px;
      height: 52px;
      object-fit: contain;
      display: block;
      margin: 0 auto 8px;
    }
    .brand-name {
      font-size: 15px;
      font-weight: 800;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .brand-title {
      margin: 6px 0 0;
      font-size: 16px;
      font-weight: 700;
    }
    .brand-subtitle {
      margin: 2px 0 0;
      color: var(--muted);
      font-size: 11px;
    }
    .divider {
      margin: 12px 0;
      border-top: 1px dashed var(--line);
    }
    .meta {
      display: grid;
      gap: 6px;
    }
    .meta-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-start;
    }
    .meta-row strong:last-child,
    .meta-row span:last-child {
      text-align: right;
      word-break: break-word;
    }
    .section-label {
      display: block;
      margin-bottom: 8px;
      color: var(--brand);
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .block {
      margin-bottom: 12px;
    }
    .soft {
      padding: 10px;
      border-radius: 10px;
      background: var(--soft);
      border: 1px solid #e5e7eb;
    }
    .muted {
      color: var(--muted);
    }
    .totals {
      display: block;
    }
    .total-row {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 4px 0;
    }
    .total-row.grand-total {
      margin-top: 6px;
      padding-top: 8px;
      border-top: 1px dashed var(--line);
      font-size: 14px;
      font-weight: 800;
    }
    .footer-note {
      margin-top: 10px;
      text-align: center;
      color: var(--muted);
      font-size: 11px;
    }
    .footer-contact {
      margin-top: 10px;
      text-align: center;
      font-size: 11px;
      line-height: 1.55;
    }
    .footer-contact strong {
      display: block;
      margin-bottom: 4px;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    @media print {
      body {
        padding: 0;
        background: #ffffff;
      }
      .receipt {
        width: 72mm;
        max-width: 72mm;
        border: none;
        border-radius: 0;
        box-shadow: none;
        padding: 0;
      }
    }
  </style>
</head>
<body>
  <main class="receipt">
    <section class="center">
      <img src="${escapeHtml(documentLogoUrl)}" alt="${escapeHtml(documentBranding.name)}" class="brand-logo" />
      <div class="brand-name">${escapeHtml(documentBranding.name)}</div>
      <div class="brand-title">${escapeHtml(documentBranding.tagline)}</div>
      <div class="brand-subtitle">${escapeHtml(documentBranding.documents?.invoiceTitle || 'Recu de paiement')}</div>
    </section>

    <div class="divider"></div>

    <section class="block meta">
      <div class="meta-row">
        <span class="muted">Paiement</span>
        <strong>${escapeHtml(paymentCode)}</strong>
      </div>
      <div class="meta-row">
        <span class="muted">Reservation</span>
        <strong>${escapeHtml(reservationCode)}</strong>
      </div>
      <div class="meta-row">
        <span class="muted">Date</span>
        <strong>${escapeHtml(formatDisplayDate(payment?.date))}</strong>
      </div>
      <div class="meta-row">
        <span class="muted">Edition</span>
        <strong>${escapeHtml(formatDisplayDate(new Date().toISOString()))}</strong>
      </div>
    </section>

    <div class="divider"></div>

    <section class="block soft">
      <span class="section-label">Client</span>
      <div><strong>${escapeHtml(payment?.booking_customer_name || 'Client')}</strong></div>
      <div class="muted">${escapeHtml(payment?.booking_customer_email || '-')}</div>
      <div>${escapeHtml(payment?.booking_hall_name || '-')}</div>
      <div class="muted">Periode: ${escapeHtml(formatDateRange(payment?.booking_start_date, payment?.booking_end_date))}</div>
    </section>

    <section class="block">
      <span class="section-label">Details</span>
      <div class="meta">
        <div class="meta-row">
          <span class="muted">Reference</span>
          <strong>${escapeHtml(payment?.reference || '-')}</strong>
        </div>
        <div class="meta-row">
          <span class="muted">Methode</span>
          <strong>${escapeHtml(payment?.method || '-')}</strong>
        </div>
        <div class="meta-row">
          <span class="muted">Type</span>
          <strong>${escapeHtml(typeLabel)}</strong>
        </div>
        <div class="meta-row">
          <span class="muted">Salle</span>
          <strong>${escapeHtml(payment?.booking_hall_name || '-')}</strong>
        </div>
      </div>
    </section>

    <div class="divider"></div>

    <section class="block totals">
      <div class="total-row">
        <span class="muted">Montant paye</span>
        <strong>${escapeHtml(formatMoney(payment?.amount))}</strong>
      </div>
      <div class="total-row">
        <span class="muted">Total reservation</span>
        <strong>${escapeHtml(formatMoney(payment?.booking_total_price))}</strong>
      </div>
      <div class="total-row grand-total">
        <span>Reste a payer</span>
        <span>${escapeHtml(formatMoney(payment?.booking_remaining_amount))}</span>
      </div>
    </section>

    <div class="divider"></div>

    <section class="footer-contact">
      <strong>Adresse et contact</strong>
      <div>${escapeHtml(documentBranding.address)}</div>
      <div>${escapeHtml(documentBranding.contacts.join(' • '))}</div>
    </section>

    <div class="footer-note">
      Merci pour votre confiance.
    </div>
  </main>
</body>
</html>`
}

const printPaymentInvoice = async (payment) => {
  if (!payment || !process.client) return
  closeActions()
  const html = buildInvoiceHtml(payment)
  const win = window.open('', '_blank')
  if (!win) {
    notify('Impossible d\'ouvrir la fenetre d\'impression', 'warning')
    return
  }
  win.document.write(html)
  win.document.close()
  win.focus()
  setTimeout(() => {
    win.print()
  }, 250)
}

const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const selectedPayment = ref(null)

const form = ref({
  booking: null,
  date: new Date().toISOString().split('T')[0],
  reference: '',
  amount: 0,
  method: 'Virement',
  kind: 'advance',
  status: 'paid'
})
const amountInput = moneyInputModel(form, 'amount')

const toNumber = (v) => Number(v || 0)
const unpaidBookings = computed(() => bookings.value.filter(b => toNumber(b.remaining_amount) > 0 && b.status !== 'cancelled'))
const filteredUnpaidBookings = computed(() => {
  const q = search.value.toLowerCase().trim()
  return unpaidBookings.value.filter((b) => {
    const matchesSearch = q === '' ||
      String(b.customer_name || '').toLowerCase().includes(q) ||
      String(b.customer_email || '').toLowerCase().includes(q) ||
      String(b.hall_name || '').toLowerCase().includes(q)
    const matchesDate = dateOverlapsRange(b.start_date, b.end_date, rangeStartYmd.value, rangeEndYmd.value)
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
      String(p.reference || '').toLowerCase().includes(q)
    const matchesStatus = statusFilter.value === '' || p.status === statusFilter.value
    const matchesMethod = methodFilter.value === '' || p.method === methodFilter.value
    const matchesDate = inRangeYmd(p.date, rangeStartYmd.value, rangeEndYmd.value)
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

const selectedBookingForForm = computed(() => filteredUnpaidBookings.value.find(b => b.id === form.value.booking) || null)
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
watch(() => filteredUnpaidBookings.value.length, (v) => animateCounter(displayUnpaidBookings, v), { immediate: true })
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
    booking: unpaidBookings.value[0]?.id || null,
    date: new Date().toISOString().split('T')[0],
    reference: 'PAY-' + Math.floor(1000 + Math.random() * 9000),
    amount: 0,
    method: 'Virement',
    kind: 'advance',
    status: 'paid'
  }
}

const onKindChange = () => {
  if (!selectedBookingForForm.value) return
  if (form.value.kind === 'full') {
    form.value.amount = toNumber(selectedBookingForForm.value.remaining_amount)
  }
}

const onBookingChange = () => {
  if (!selectedBookingForForm.value) return
  if (form.value.kind === 'full') {
    form.value.amount = toNumber(selectedBookingForForm.value.remaining_amount)
  } else if (form.value.amount <= 0) {
    form.value.amount = Math.min(100000, toNumber(selectedBookingForForm.value.remaining_amount))
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
    const { data } = await api.post('payments/', form.value)
    notify('Paiement enregistré avec succès', 'success')
    showFormModal.value = false
    await Promise.all([fetchPayments(), fetchBookings()])
    const createdPayment = payments.value.find(item => item.id === data?.id) || data
    await nextTick()
    printPaymentInvoice(createdPayment)
  } catch {
    notify('Erreur lors de l\'enregistrement du paiement', 'danger')
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
