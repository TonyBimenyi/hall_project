<!-- pages/admin/proformas.vue -->
<template>
  <div class="proformas-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>Factures Proforma</h1>
        <p>Préparer, enregistrer, modifier et convertir les devis et proformas en réservations</p>
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
        <NuxtLink to="/admin/bookings" class="btn btn-secondary btn-sm admin-head-btn">
          <i class="fas fa-calendar-days"></i>
          <span class="btn-label">Toutes les réservations</span>
        </NuxtLink>
        <button class="btn btn-primary btn-sm admin-head-btn" @click="openAddModal">
          <i class="fas fa-plus"></i>
          <span class="btn-label">Nouvelle proforma</span>
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
            placeholder="Rechercher par client, code, salle ou chambre..."
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
            <option value="pending">En attente (Non converti)</option>
            <option value="converted">Converti en réservation</option>
            <option value="cancelled">Annulé</option>
          </select>
        </div>
        <div class="filter-wrapper">
          <select v-model="typeFilter" class="filter-select-clean">
            <option value="">Tous les types</option>
            <option value="hall">Salles</option>
            <option value="room">Chambres</option>
          </select>
        </div>
        <div class="filter-wrapper">
          <select v-model="preset" class="filter-select-clean">
            <option value="all">Toutes les dates</option>
            <option value="7d">7 derniers jours</option>
            <option value="28d">28 derniers jours</option>
            <option value="this_month">Ce mois</option>
            <option value="last_month">Mois dernier</option>
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
      <div class="filter-range-note">
        <span class="filter-range-status"><i class="fas fa-chart-simple"></i> {{ filteredProformas.length }} proforma{{ filteredProformas.length > 1 ? 's' : '' }}</span>
        <!-- <span>{{ activeRangeNotice }}</span> -->
      </div>
    </div>

    <!-- Table -->
    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <h2 class="table-title" style="margin-bottom:0; font-size: 20px;">
          Toutes les proformas ({{ loadingProformas ? '...' : filteredProformas.length }})
        </h2>
        <AdminAppTablePagination
          :start="proformasStartIndex"
          :end="proformasEndIndex"
          :total="proformasTotalItems"
          :can-prev="proformasCanPrev"
          :can-next="proformasCanNext"
          :disabled="loadingProformas"
          @prev="proformasPrevPage"
          @next="proformasNextPage"
        />
      </div>

      <!-- Mobile cards -->
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingProformas">
          <div v-for="n in 4" :key="`sk-pcard-${n}`" class="admin-card">
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
          <div v-for="proforma in paginatedProformas" :key="proforma.id" class="admin-card has-actions">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ proforma.customer_name }}</div>
                <div class="admin-card-subtitle">{{ getProformaDisplayId(proforma) }} • {{ getProformaItemSummary(proforma) }} • {{ formatDateRange(proforma.start_date, proforma.end_date) }}</div>
              </div>

              <div class="admin-card-actions">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(proforma.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === proforma.id" class="actions-menu" @click.stop>
                    <button
                      v-if="proforma.status !== 'converted'"
                      class="actions-item highlight-action"
                      :class="{ 'is-loading': convertingId === proforma.id }"
                      :disabled="convertingId === proforma.id"
                      @click="handleConvertClick(proforma)"
                    >
                      <i class="fas fa-check-circle"></i> Convertir en réservation
                    </button>
                    <NuxtLink
                      v-else-if="proforma.converted_booking"
                      class="actions-item"
                      :to="`/admin/bookings`"
                      @click="closeActions"
                    >
                      <i class="fas fa-calendar-check"></i> Voir la réservation
                    </NuxtLink>
                    <button class="actions-item" :disabled="downloadingProformaId === proforma.id" @click="printProformaPdf(proforma)">
                      <i class="fas fa-file-invoice"></i> {{ downloadingProformaId === proforma.id ? 'Génération...' : 'Télécharger la proforma' }}
                    </button>
                    <button class="actions-item" @click="viewProforma(proforma)">
                      <i class="fas fa-eye"></i> Voir détails
                    </button>
                    <button v-if="proforma.status !== 'converted'" class="actions-item" @click="editProforma(proforma)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button v-if="canDeleteProformas" class="actions-item danger" @click="confirmDelete(proforma)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Code</span>
                <span class="v">{{ getProformaDisplayId(proforma) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Événement</span>
                <span class="v">{{ proforma.event_type }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Montant TTC</span>
                <span class="v">{{ formatMoney(proforma.total_price) }}</span>
              </div>
              <div class="admin-kv">
                <span class="k">Statut</span>
                <span class="v">
                  <span :class="['badge', getBadgeClass(proforma.status)]">{{ getStatusTranslation(proforma.status) }}</span>
                </span>
              </div>
              <div v-if="proforma.converted_booking_code" class="admin-kv">
                <span class="k">Réservation liée</span>
                <span class="v"><code>{{ proforma.converted_booking_code }}</code></span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingProformas && filteredProformas.length === 0" class="empty-cell">Aucune proforma enregistrée</div>
      </div>

      <!-- Desktop table -->
      <div v-else class="table-wrapper">
        <table ref="tableRef" class="proformas-table admin-table">
          <thead>
            <tr>
              <th><button class="table-sort-btn" :class="{ active: isSortActive('code') }" @click="toggleSort('code')">Code <i :class="sortIconClass('code')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isSortActive('customer_name') }" @click="toggleSort('customer_name')">Client <i :class="sortIconClass('customer_name')"></i></button></th>
              <th>Type</th>
              <th>Salle / Chambre</th>
              <th>Événement</th>
              <th><button class="table-sort-btn" :class="{ active: isSortActive('start_date') }" @click="toggleSort('start_date')">Dates <i :class="sortIconClass('start_date')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isSortActive('total_price') }" @click="toggleSort('total_price')">Montant <i :class="sortIconClass('total_price')"></i></button></th>
              <th><button class="table-sort-btn" :class="{ active: isSortActive('status') }" @click="toggleSort('status')">Statut <i :class="sortIconClass('status')"></i></button></th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="loadingProformas">
              <tr v-for="n in 5" :key="`sk-ptr-${n}`">
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
                <td class="date-cell"><div class="skeleton-line skeleton-w-60"></div></td>
                <td class="amount-cell"><div class="skeleton-line skeleton-w-50"></div></td>
                <td><div class="skeleton-line skeleton-w-40"></div></td>
                <td class="actions-cell"><div class="skeleton-line skeleton-w-60"></div></td>
              </tr>
            </template>
            <tr v-else v-for="proforma in paginatedProformas" :key="proforma.id">
              <td><code>{{ getProformaDisplayId(proforma) }}</code></td>
              <td class="customer-cell">
                <div class="customer-name">{{ proforma.customer_name }}</div>
                <div class="customer-email">{{ proforma.customer_email || proforma.customer_phone || '-' }}</div>
              </td>
              <td>
                <span class="badge" :style="{ background: proforma.booking_type === 'hall' ? '#eff6ff' : '#f0fdf4', color: proforma.booking_type === 'hall' ? '#1e40af' : '#166534' }">
                  {{ proforma.booking_type === 'hall' ? 'Salle' : 'Chambre' }}
                </span>
              </td>
              <td>{{ getProformaItemSummary(proforma) }}</td>
              <td>{{ proforma.event_type }}</td>
              <td class="date-cell">{{ formatDateRange(proforma.start_date, proforma.end_date) }}</td>
              <td class="amount-cell">
                <div class="booking-amount-box">
                  <span class="booking-amount-val">{{ formatMoney(proforma.total_price) }}</span>
                  <span v-if="Number(proforma.discount_amount || 0) > 0" class="discount-table-badge" :title="`Remise: -${formatMoney(proforma.discount_amount)}`">
                    <i class="fas fa-tag"></i> -{{ formatMoney(proforma.discount_amount) }}
                  </span>
                </div>
              </td>
              <td>
                <span :class="['badge', getBadgeClass(proforma.status)]">
                  {{ getStatusTranslation(proforma.status) }}
                </span>
                <div v-if="proforma.converted_booking_code" style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">
                  Res: <code>{{ proforma.converted_booking_code }}</code>
                </div>
              </td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(proforma.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === proforma.id" class="actions-menu" @click.stop>
                    <button
                      v-if="proforma.status !== 'converted'"
                      class="actions-item highlight-action"
                      :class="{ 'is-loading': convertingId === proforma.id }"
                      :disabled="convertingId === proforma.id"
                      @click="handleConvertClick(proforma)"
                    >
                      <i class="fas fa-check-circle"></i> Convertir en réservation
                    </button>
                    <NuxtLink
                      v-else-if="proforma.converted_booking"
                      class="actions-item"
                      :to="`/admin/bookings`"
                      @click="closeActions"
                    >
                      <i class="fas fa-calendar-check"></i> Voir la réservation
                    </NuxtLink>
                    <button class="actions-item" :disabled="downloadingProformaId === proforma.id" @click="printProformaPdf(proforma)">
                      <i class="fas fa-file-invoice"></i> {{ downloadingProformaId === proforma.id ? 'Génération...' : 'Télécharger la proforma' }}
                    </button>
                    <button class="actions-item" @click="viewProforma(proforma)">
                      <i class="fas fa-eye"></i> Voir détails
                    </button>
                    <button v-if="proforma.status !== 'converted'" class="actions-item" @click="editProforma(proforma)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button v-if="canDeleteProformas" class="actions-item danger" @click="confirmDelete(proforma)">
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

    <!-- Modal Form (Nouvelle / Modifier Proforma) -->
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la facture proforma' : 'Nouvelle facture proforma'" width="780px">
      <form @submit.prevent="saveProforma" class="admin-form proforma-form-shell">
        <div class="booking-form-hero">
          <div class="booking-form-hero-copy">
            <span class="booking-form-eyebrow">Facture Proforma / Devis</span>
            <h3>{{ isEditing ? 'Mettre à jour la facture proforma' : 'Établir une facture proforma' }}</h3>
            <p>Préparez une estimation détaillée pour votre client. Vous pourrez l'enregistrer, l'imprimer et la convertir en réservation à tout moment.</p>
          </div>
          <div class="booking-form-hero-meta">
            <span class="booking-form-chip">{{ form.customer_kind === 'organization' ? 'Organisation' : 'Particulier' }}</span>
            <span class="booking-form-chip accent">{{ form.booking_type === 'room' ? 'Proforma Chambres' : 'Proforma Salle' }}</span>
          </div>
        </div>

        <!-- Section 1: Client & Contact -->
        <section class="booking-form-section">
          <div class="booking-form-section-head">
            <div>
              <span class="booking-form-section-kicker">Étape 1</span>
              <h4>Client et contact</h4>
            </div>
            <p>Indiquez le client ou l'organisation destinataire du devis.</p>
          </div>

          <div class="form-grid booking-form-grid">
            <div class="form-group">
              <label class="form-label">Devis pour</label>
              <select v-model="form.customer_kind" class="form-select" @change="onCustomerKindChange">
                <option value="individual">Particulier</option>
                <option value="organization">Organisation</option>
              </select>
            </div>

            <div v-if="form.customer_kind === 'organization'" class="form-group full organization-booking-note">
              <strong>Devis organisation</strong>
              <small>Précisez la raison sociale de l'organisation et la personne de contact.</small>
            </div>

            <div v-if="form.customer_kind === 'individual'" class="form-group full customer-lookup-card">
              <div class="customer-lookup-head">
                <div>
                  <label class="form-label">Client</label>
                  <small>Rechercher un client existant ou en créer un nouveau.</small>
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
                  placeholder="Rechercher par nom ou téléphone..."
                  @focus="openCustomerResults"
                  @click.stop
                />
              </div>

              <div v-if="customerResultsOpen" class="customer-results-list" @click.stop>
                <button
                  v-for="c in customerSearchResults"
                  :key="c.id"
                  type="button"
                  class="customer-result-item"
                  @click="selectCustomer(c)"
                >
                  <strong>{{ c.full_name || `${c.first_name || ''} ${c.last_name || ''}`.trim() }}</strong>
                  <span>{{ c.phone || '-' }}<template v-if="c.email"> • {{ c.email }}</template></span>
                </button>
                <div v-if="loadingCustomers" class="customer-results-empty">
                  Recherche des clients...
                </div>
                <div v-if="!loadingCustomers && !customerSearchResults.length" class="customer-results-empty">
                  Aucun client trouvé. Utilisez <strong>Nouveau client</strong> ci-dessus.
                </div>
              </div>

              <div v-if="selectedCustomerBadge" class="selected-customer-pill">
                <i class="fas fa-check-circle"></i>
                <span>
                  Client sélectionné: <strong>{{ selectedCustomerBadge }}</strong>
                  <small v-if="form.customer_phone || form.customer_email">
                    {{ form.customer_phone || '-' }}<template v-if="form.customer_email"> • {{ form.customer_email }}</template>
                  </small>
                </span>
                <button type="button" class="btn-link" @click="clearSelectedCustomer">Changer</button>
              </div>
            </div>

            <!-- Quick customer form -->
            <div v-if="showQuickCustomerForm && form.customer_kind === 'individual'" class="form-group full quick-customer-shell">
              <h5>Création rapide d'un client</h5>
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Prénom *</label>
                  <input v-model="quickCustomer.first_name" type="text" class="form-input" placeholder="Prénom" />
                </div>
                <div class="form-group">
                  <label class="form-label">Nom</label>
                  <input v-model="quickCustomer.last_name" type="text" class="form-input" placeholder="Nom" />
                </div>
                <div class="form-group">
                  <label class="form-label">Téléphone *</label>
                  <input v-model="quickCustomer.phone" type="text" class="form-input" placeholder="+257..." />
                </div>
                <div class="form-group">
                  <label class="form-label">Email</label>
                  <input v-model="quickCustomer.email" type="email" class="form-input" placeholder="client@email.com" />
                </div>
              </div>
              <button type="button" class="btn btn-primary btn-sm" :disabled="savingQuickCustomer" @click="saveQuickCustomer">
                <i class="fas fa-check"></i> Enregistrer et lier
              </button>
            </div>

            <!-- Organization details -->
            <template v-if="form.customer_kind === 'organization'">
              <div class="form-group">
                <label class="form-label">Nom de l'organisation *</label>
                <input v-model="form.organization_name" type="text" class="form-input" placeholder="Ex: Société ABC" required />
              </div>
              <div class="form-group">
                <label class="form-label">Contact référent *</label>
                <input v-model="form.organization_contact_name" type="text" class="form-input" placeholder="Nom du responsable" required />
              </div>
              <div class="form-group">
                <label class="form-label">Téléphone *</label>
                <input v-model="form.customer_phone" type="text" class="form-input" placeholder="Téléphone contact" required />
              </div>
              <div class="form-group">
                <label class="form-label">Email organisation</label>
                <input v-model="form.customer_email" type="email" class="form-input" placeholder="contact@organisation.com" />
              </div>
            </template>

            <!-- Individual client information -->
            <template v-else>
              <div class="form-group full client-info-heading">
                <div>
                  <strong>Informations du client</strong>
                  <small>Les champs sont remplis automatiquement et restent modifiables.</small>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Prénom client *</label>
                <input v-model="form.customer_first_name" type="text" class="form-input" placeholder="Prénom" required />
              </div>
              <div class="form-group">
                <label class="form-label">Nom client</label>
                <input v-model="form.customer_last_name" type="text" class="form-input" placeholder="Nom" />
              </div>
              <div class="form-group">
                <label class="form-label">Téléphone client *</label>
                <input v-model="form.customer_phone" type="text" class="form-input" placeholder="+257 ..." required />
              </div>
              <div class="form-group">
                <label class="form-label">Email client</label>
                <input v-model="form.customer_email" type="email" class="form-input" placeholder="email@domaine.com" />
              </div>
            </template>
          </div>
        </section>

        <!-- Section 2: Type, Période & Emplacement -->
        <section class="booking-form-section">
          <div class="booking-form-section-head">
            <div>
              <span class="booking-form-section-kicker">Étape 2</span>
              <h4>Prestation et dates</h4>
            </div>
            <p>Choisissez si ce devis concerne une salle ou une / plusieurs chambres.</p>
          </div>

          <div class="form-grid booking-form-grid">
            <div class="form-group">
              <label class="form-label">Type de réservation</label>
              <select v-model="form.booking_type" class="form-select" @change="onBookingTypeChange">
                <option value="hall">Salles</option>
                <option value="room">Chambres</option>
              </select>
            </div>

            <!-- Hall selection -->
            <div v-if="form.booking_type === 'hall'" class="form-group">
              <label class="form-label">Salle *</label>
              <select v-model="form.hall" class="form-select" required>
                <option value="">Sélectionner une salle</option>
                <option v-for="h in halls" :key="h.id" :value="h.id">
                  {{ h.name }} (Capacité: {{ h.capacity }} pers, {{ formatMoney(h.price_per_day) }}/jour)
                </option>
              </select>
            </div>

            <!-- Rooms selection -->
            <div v-if="form.booking_type === 'room'" class="form-group full">
              <div class="room-selection-head">
                <label class="form-label">Chambres concernées *</label>
                <small>Sélectionnez une ou plusieurs chambres disponibles pour cette même proforma.</small>
              </div>
              <div class="room-selection-grid">
                <label
                  v-for="r in rooms"
                  :key="`proforma-room-option-${r.id}`"
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
                      <span :class="['room-option-status', `status-${String(r.status || 'available')}`]">{{ isRoomUnavailable(r.id) ? 'Indisponible' : roomStatusLabel(r.status) }}</span>
                    </div>
                    <small v-if="roomAvailabilityMessage(r)" class="room-option-booked-dates">{{ roomAvailabilityMessage(r) }}</small>
                    <small>{{ isRoomSelected(r.id) ? 'Chambre sélectionnée pour cette proforma.' : 'Cliquez pour sélectionner cette chambre.' }}</small>
                  </div>
                </label>
              </div>
              <small class="form-hint" v-if="!form.rooms_selected.length">Sélectionnez au moins une chambre pour le devis.</small>
            </div>

            <div class="form-group">
              <label class="form-label">Type d'événement / Motif</label>
              <select v-if="form.booking_type === 'hall'" v-model="form.event_type" class="form-select" required>
                <option value="Mariage">Mariage</option>
                <option value="Séminaire">Séminaire</option>
                <option value="Gala">Gala</option>
                <option value="Anniversaire">Anniversaire</option>
                <option value="Réunion">Réunion</option>
                <option value="Autres">Autres</option>
              </select>
              <input v-else v-model="form.event_type" type="text" class="form-input" placeholder="Séjour, vacances, mission..." required />
            </div>

            <div class="form-group full">
              <label class="form-label">Période du devis *</label>
              <AdminDateRangeSelector
                v-model:startDate="form.start_date"
                v-model:endDate="form.end_date"
                :booked-dates="calendarRanges"
                :booking-type="form.booking_type"
                :is-editing="false"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Validité du devis</label>
              <input v-model="form.valid_until" type="date" class="form-input" />
              <small class="form-hint">Date limite d'acceptation du devis proforma.</small>
            </div>
          </div>
        </section>

        <!-- Section 3: Services Additionnels & Remises -->
        <section class="booking-form-section">
          <div class="booking-form-section-head">
            <div>
              <span class="booking-form-section-kicker">Étape 3</span>
              <h4>Services & Remises</h4>
            </div>
            <p>Ajoutez des options ou services complémentaires et appliquez une éventuelle remise.</p>
          </div>

          <div v-if="availableAdditionalServices.length" class="additional-services-shell">
            <div class="room-service-group proforma-service-group">
              <div class="room-service-group-head">
                <div><strong>Services additionnels</strong><small>Choisissez les options à ajouter à cette proforma.</small></div>
                <span class="room-service-group-count">{{ availableAdditionalServices.length }} service{{ availableAdditionalServices.length > 1 ? 's' : '' }}</span>
              </div>
              <div class="room-service-flex">
                <template v-for="srv in availableAdditionalServices" :key="srv.name">
                  <article v-if="!srv.has_subservices" class="room-service-card" :class="{ 'is-active': isServiceSelected(srv.name) }">
                  <div class="room-service-card-top"><strong>{{ srv.name }}</strong><span>{{ formatMoney(srv.price) }}</span></div>
                  <div class="room-service-card-bottom"><small>Quantité</small><div class="room-service-stepper"><button type="button" class="room-service-step-btn" :disabled="getServiceQty(srv.name) <= 0" @click="changeProformaServiceQuantity(srv, -1)"><i class="fas fa-minus"></i></button><span class="room-service-qty">{{ getServiceQty(srv.name) }}</span><button type="button" class="room-service-step-btn" @click="changeProformaServiceQuantity(srv, 1)"><i class="fas fa-plus"></i></button></div></div>
                  </article>
                  <article v-else class="room-service-card room-service-card-stack">
                  <div class="room-service-card-top"><strong>{{ srv.name }}</strong><span>Sous-services</span></div>
                  <div class="room-subservice-flex">
                    <div v-for="sub in (srv.subservices || [])" :key="`${srv.name}-${sub.name}`" class="room-subservice-card" :class="{ 'is-active': isSubserviceSelected(srv.name, sub.name) }">
                      <div class="room-subservice-top"><strong>{{ sub.name }}</strong><span>{{ formatMoney(sub.price) }}</span></div>
                      <div class="room-service-card-bottom"><small>Quantité</small><div class="room-service-stepper"><button type="button" class="room-service-step-btn" :disabled="getSubserviceQty(srv.name, sub.name) <= 0" @click="changeProformaSubserviceQuantity(srv, sub, -1)"><i class="fas fa-minus"></i></button><span class="room-service-qty">{{ getSubserviceQty(srv.name, sub.name) }}</span><button type="button" class="room-service-step-btn" @click="changeProformaSubserviceQuantity(srv, sub, 1)"><i class="fas fa-plus"></i></button></div></div>
                    </div>
                  </div>
                  </article>
                </template>
              </div>
            </div>
          </div>

          <div class="pricing-discount-panel form-group full">
            <div class="pdp-header"><div class="pdp-header-left"><div class="pdp-icon-box"><i class="fas fa-percent"></i></div><div><h5 class="pdp-title">Remise & Tarification Finale</h5><p class="pdp-subtitle">Appliquez une réduction et vérifiez le montant total net calculé.</p></div></div><label v-if="canManageProformaDiscount" class="pdp-discount-toggle" :class="{ 'is-active': discountEnabled }"><input type="checkbox" :checked="discountEnabled" @change="setDiscountEnabled($event.target.checked)" /><span class="pdp-discount-toggle-track" aria-hidden="true"><span class="pdp-discount-toggle-knob"></span></span><span class="pdp-discount-toggle-copy"><strong>{{ discountEnabled ? 'Remise activée' : 'Tarif standard' }}</strong><small>{{ discountEnabled ? 'Afficher les champs de remise' : 'Aucune remise appliquée' }}</small></span></label></div>
            <div v-if="discountEnabled" class="pdp-body-grid"><div class="pdp-control-card"><div class="pdp-field-header"><label class="pdp-label"><i class="fas fa-tag" style="color: #10b981;"></i><span>Remise accordée</span></label><button v-if="Number(form.discount_amount || 0) > 0" type="button" class="pdp-clear-btn" @click="clearDiscount"><i class="fas fa-times-circle"></i> Réinitialiser</button></div><div class="pdp-input-wrapper"><span class="pdp-input-icon"><i class="fas fa-minus" style="color: #10b981;"></i></span><input v-model.number="form.discount_amount" inputmode="numeric" type="number" min="0" class="pdp-input pdp-input-amount" placeholder="0" /><span class="pdp-input-suffix">FBU</span></div><div class="pdp-presets"><span class="pdp-presets-label">Raccourcis:</span><div class="pdp-presets-list"><button v-for="pct in [5, 10, 15, 20, 25]" :key="pct" type="button" class="pdp-preset-btn" :class="{ 'is-active': Math.round(grossProformaAmount * pct / 100) === Number(form.discount_amount || 0) }" @click="applyQuickDiscountPercent(pct)">{{ pct }}%</button></div></div><label class="pdp-label"><i class="fas fa-comment-dots" style="color: #94a3b8;"></i><span>Motif de la remise (optionnel)</span></label><input v-model="form.discount_reason" type="text" class="pdp-input pdp-input-reason" placeholder="Ex: Client fidèle, Accord commercial, Promotion..." /></div><div class="pdp-hero-card"><span class="pdp-hero-label"><i class="fas fa-receipt"></i> Montant Net Final</span><span class="pdp-hero-val">{{ formatMoney(calculatedTotalPrice) }}</span><div class="pdp-mini-summary"><div class="pdp-summary-row"><span class="pdp-summary-k">Montant brut</span><span class="pdp-summary-v">{{ formatMoney(grossProformaAmount) }}</span></div><div v-if="Number(form.discount_amount || 0) > 0" class="pdp-summary-row pdp-summary-discount"><span class="pdp-summary-k">Déduction remise</span><span class="pdp-summary-v">-{{ formatMoney(form.discount_amount) }}</span></div></div></div></div>
          </div>

          <div class="form-grid booking-form-grid" style="margin-top: 16px;">
            <div class="form-group full">
              <label class="form-label">Notes & Conditions particulières</label>
              <textarea v-model="form.notes" class="form-textarea" rows="2" placeholder="Précisions pour le devis..."></textarea>
            </div>
          </div>
        </section>

        <!-- Section 4: Live Breakdown Summary -->
        <section class="booking-form-section summary-preview-section">
          <h4>Récapitulatif financier du devis</h4>
          <div class="summary-breakdown-card">
            <div class="breakdown-row">
              <span>Hébergement / Salle de base ({{ calculatedDuration }} jour{{ calculatedDuration > 1 ? 's' : '' }})</span>
              <span>{{ formatMoney(calculatedBaseAccomodation) }}</span>
            </div>
            <div v-if="calculatedServicesTotal > 0" class="breakdown-row">
              <span>Services additionnels</span>
              <span>{{ formatMoney(calculatedServicesTotal) }}</span>
            </div>
            <div class="breakdown-row">
              <span>Sous-total HT</span>
              <span>{{ formatMoney(calculatedSubtotalHt) }}</span>
            </div>
            <div v-if="form.booking_type === 'room'" class="breakdown-row">
              <span>TCSTH (10%)</span>
              <span>{{ formatMoney(calculatedTvaAmount) }}</span>
            </div>
            <div v-if="Number(form.discount_amount || 0) > 0" class="breakdown-row discount">
              <span>Remise accordée</span>
              <span>-{{ formatMoney(form.discount_amount) }}</span>
            </div>
            <div class="breakdown-row total">
              <strong>Total Net à payer (TTC)</strong>
              <strong>{{ formatMoney(calculatedTotalPrice) }}</strong>
            </div>
          </div>
        </section>

        <div class="modal-actions-footer">
          <button type="button" class="btn btn-outline" @click="showFormModal = false">Annuler</button>
          <button type="submit" class="btn btn-primary" :class="{ 'is-loading': savingProforma }" :disabled="savingProforma">
            <i class="fas fa-save"></i>
            <span>{{ isEditing ? 'Mettre à jour la proforma' : 'Enregistrer la proforma' }}</span>
          </button>
        </div>
      </form>
    </AdminAppModal>

    <!-- Modal View Details -->
    <AdminAppModal v-model="showViewModal" title="Détails de la facture proforma" width="680px">
      <div v-if="selectedProforma" class="entity-view-modal">
        <div class="entity-view-hero">
          <div class="entity-view-avatar">{{ nameInitials(selectedProforma.customer_name) || 'PF' }}</div>
          <div class="entity-view-main">
            <div class="entity-view-code">{{ getProformaDisplayId(selectedProforma) }}</div>
            <h3>{{ selectedProforma.customer_name }}</h3>
            <p>{{ getProformaItemSummary(selectedProforma) }} • {{ selectedProforma.event_type }}</p>
          </div>
          <div class="entity-view-badges">
            <span :class="['badge', getBadgeClass(selectedProforma.status)]">{{ getStatusTranslation(selectedProforma.status) }}</span>
            <span class="badge badge-info">{{ formatMoney(selectedProforma.total_price) }}</span>
          </div>
        </div>

        <div class="entity-view-grid">
          <section class="entity-view-card">
            <div class="entity-view-card-title">Client & Contact</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Client</span><span class="entity-view-value">{{ selectedProforma.customer_name }}</span></div>
              <div v-if="selectedProforma.organization_name" class="entity-view-item"><span class="entity-view-label">Organisation</span><span class="entity-view-value">{{ selectedProforma.organization_name }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Téléphone</span><span class="entity-view-value">{{ selectedProforma.customer_phone || '-' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Email</span><span class="entity-view-value">{{ selectedProforma.customer_email || '-' }}</span></div>
            </div>
          </section>

          <section class="entity-view-card">
            <div class="entity-view-card-title">Prestation & Période</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Type</span><span class="entity-view-value">{{ selectedProforma.booking_type === 'hall' ? 'Salle' : 'Chambre' }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Emplacement</span><span class="entity-view-value">{{ getProformaItemSummary(selectedProforma) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Période</span><span class="entity-view-value">{{ formatDateRange(selectedProforma.start_date, selectedProforma.end_date) }}</span></div>
              <div class="entity-view-item"><span class="entity-view-label">Validité</span><span class="entity-view-value">{{ selectedProforma.valid_until ? formatDisplayDate(selectedProforma.valid_until) : 'Non définie' }}</span></div>
            </div>
          </section>

          <section class="entity-view-card entity-view-card-full">
            <div class="entity-view-card-title">Montants</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Sous-total HT</span><span class="entity-view-value">{{ formatMoney(selectedProforma.subtotal_ht) }}</span></div>
              <div v-if="Number(selectedProforma.tva_amount || 0) > 0" class="entity-view-item"><span class="entity-view-label">TCSTH (10%)</span><span class="entity-view-value">{{ formatMoney(selectedProforma.tva_amount) }}</span></div>
              <div v-if="Number(selectedProforma.discount_amount || 0) > 0" class="entity-view-item"><span class="entity-view-label">Remise</span><span class="entity-view-value" style="color: #059669; font-weight: 700;">-{{ formatMoney(selectedProforma.discount_amount) }} ({{ selectedProforma.discount_reason || 'Remise' }})</span></div>
              <div class="entity-view-item highlight"><span class="entity-view-label">Total Net TTC</span><span class="entity-view-value" style="color: #0f172a; font-weight: 800;">{{ formatMoney(selectedProforma.total_price) }}</span></div>
            </div>
          </section>

          <section v-if="selectedProforma.converted_booking_code" class="entity-view-card entity-view-card-full">
            <div class="entity-view-card-title">Conversion</div>
            <div class="entity-view-list">
              <div class="entity-view-item"><span class="entity-view-label">Code réservation créée</span><span class="entity-view-value"><code>{{ selectedProforma.converted_booking_code }}</code></span></div>
            </div>
          </section>
        </div>
      </div>
      <template #footer>
        <button v-if="selectedProforma && selectedProforma.status !== 'converted'" class="btn btn-primary" :class="{ 'is-loading': convertingId === selectedProforma.id }" @click="handleConvertClick(selectedProforma)">
          <i class="fas fa-check-circle"></i> Convertir en réservation
        </button>
        <button class="btn btn-outline" :disabled="downloadingProformaId === selectedProforma?.id" @click="printProformaPdf(selectedProforma)">
          <i class="fas fa-file-invoice"></i> {{ downloadingProformaId === selectedProforma?.id ? 'Génération...' : 'Télécharger la proforma' }}
        </button>
        <button class="btn btn-secondary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Modal Delete Confirmation -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="420px">
      <p>Êtes-vous sûr de vouloir supprimer la proforma <strong>{{ getProformaDisplayId(selectedProforma) }}</strong> de <strong>{{ selectedProforma?.customer_name }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :class="{ 'is-loading': deletingProforma }" :disabled="deletingProforma" @click="deleteProforma">
          Supprimer
        </button>
      </template>
    </AdminAppModal>

    <!-- Modal Convert Confirmation -->
    <AdminAppModal v-model="showConvertModal" title="Convertir en réservation" width="480px">
      <div v-if="selectedProforma" class="convert-modal-body">
        <p>Voulez-vous transformer la facture proforma <strong>{{ getProformaDisplayId(selectedProforma) }}</strong> en une véritable réservation active pour <strong>{{ selectedProforma.customer_name }}</strong> ?</p>
        <div class="convert-summary-pill">
          <div><strong>Emplacement:</strong> {{ getProformaItemSummary(selectedProforma) }}</div>
          <div><strong>Dates:</strong> {{ formatDateRange(selectedProforma.start_date, selectedProforma.end_date) }}</div>
          <div><strong>Total:</strong> {{ formatMoney(selectedProforma.total_price) }}</div>
        </div>
        <small style="color: #64748b;">La disponibilité sera vérifiée et une facture officielle de réservation sera générée.</small>
      </div>
      <template #footer>
        <button class="btn btn-outline" @click="showConvertModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': convertingId === selectedProforma?.id }" :disabled="convertingId === selectedProforma?.id" @click="executeConvert">
          <i class="fas fa-check-circle"></i> Confirmer la réservation
        </button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { canDeleteBookings, canExportAdminExcel, getRoleKey, getStoredUser } from '~/composables/useRoleAccess'
import AdminAppModal from '~/components/admin/app/modal.vue'
import AdminAppTablePagination from '~/components/admin/app/TablePagination.vue'
import AdminDateRangeSelector from '~/components/admin/AdminDateRangeSelector.vue'

definePageMeta({
  layout: 'admin',
})
const {
  buildExportFileName,
  buildPdfDocumentHtml,
  downloadPdfHtml,
  openPrintPreviewHtml,
  downloadExcelTable,
  escapeHtml,
} = useAdminExportDocuments()

const proformas = ref([])
const bookings = ref([])
const halls = ref([])
const rooms = ref([])
const customers = ref([])
const loadingCustomers = ref(false)
const loadingProformas = ref(false)
const savingProforma = ref(false)
const deletingProforma = ref(false)
const convertingId = ref(null)
const downloadingProformaId = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const openActionsId = ref(null)

const isMobile = ref(false)
const filtersOpen = ref(false)
const search = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const preset = ref('all')
const customStart = ref('')
const customEnd = ref('')
const minAmountInput = ref('')
const maxAmountInput = ref('')

const sortKey = ref('id')
const sortDirection = ref('desc')

const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const showConvertModal = ref(false)
const isEditing = ref(false)
const selectedProforma = ref(null)
const discountEnabled = ref(false)

const form = ref({
  id: null,
  customer_kind: 'individual',
  customer: null,
  customer_first_name: '',
  customer_last_name: '',
  organization_name: '',
  organization_contact_name: '',
  customer_phone: '',
  customer_email: '',
  booking_type: 'hall',
  hall: '',
  room: '',
  rooms_selected: [],
  event_type: 'Mariage',
  start_date: '',
  end_date: '',
  valid_until: '',
  discount_amount: 0,
  discount_reason: '',
  additional_services_selected: [],
  notes: '',
})

const calendarRanges = ref([])

const fetchCalendarRanges = async () => {
  if (form.value.booking_type === 'room') {
    calendarRanges.value = selectedRooms.value.flatMap(room => roomBookingsIndex.value.get(String(room.id)) || [])
    return
  }
  if (!form.value.hall) {
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

watch(() => [form.value.booking_type, form.value.hall, form.value.rooms_selected], () => {
  if (showFormModal.value) {
    fetchCalendarRanges()
  }
}, { deep: true })

const page = ref(1)
const pageSize = ref(15)

const customerSearch = ref('')
const customerResultsOpen = ref(false)
const showQuickCustomerForm = ref(false)
let customerSearchTimer = null
let customerRequestId = 0
const savingQuickCustomer = ref(false)
const quickCustomer = ref({
  first_name: '',
  last_name: '',
  phone: '',
  email: '',
})

const canDeleteProformas = computed(() => canDeleteBookings(getStoredUser()))
const canExportExcel = computed(() => canExportAdminExcel(getStoredUser()))
const canManageProformaDiscount = computed(() => ['super_admin', 'proprietaire', 'gestionnaire', 'gerant'].includes(getRoleKey(getStoredUser())))

const updateIsMobile = () => {
  if (process.client) {
    isMobile.value = window.innerWidth <= 768
  }
}

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const closeActions = () => {
  openActionsId.value = null
}

const formatMoney = (val) => {
  const n = Number(val || 0)
  return new Intl.NumberFormat('fr-FR').format(n) + ' Fbu'
}

const formatDisplayDate = (d) => {
  if (!d) return '-'
  try {
    const dt = new Date(d)
    return dt.toLocaleDateString('fr-FR')
  } catch {
    return String(d)
  }
}

const formatDateRange = (s, e) => {
  if (!s || !e) return '-'
  if (s === e) return formatDisplayDate(s)
  return `${formatDisplayDate(s)} - ${formatDisplayDate(e)}`
}

const nameInitials = (name) => {
  const value = String(name || '').trim()
  if (!value) return ''
  const words = value.split(/\s+/).filter(Boolean)
  const pick = []
  if (words.length >= 2) {
    pick.push(words[0][0])
    pick.push(words[words.length - 1][0])
  } else {
    const w = words[0] || ''
    pick.push(w[0])
    if (w[1]) pick.push(w[1])
  }
  return pick.filter(Boolean).map(c => String(c).toUpperCase()).join('.')
}

const getProformaDisplayId = (p) => {
  return p?.code || `#PRF-${p?.id}`
}

const getBadgeClass = (status) => {
  switch (status) {
    case 'converted':
      return 'badge-success'
    case 'cancelled':
      return 'badge-danger'
    default:
      return 'badge-warning'
  }
}

const getStatusTranslation = (status) => {
  switch (status) {
    case 'converted':
      return 'Converti'
    case 'cancelled':
      return 'Annulé'
    case 'pending':
    default:
      return 'En attente'
  }
}

const getProformaItemSummary = (p) => {
  if (!p) return '-'
  if (p.booking_type === 'hall') {
    return p.hall_name || (halls.value.find(h => h.id === p.hall)?.name || 'Salle')
  }
  return p.room_display || 'Chambre'
}

// Calculations for form
const selectedRooms = computed(() => {
  const ids = form.value.rooms_selected.map(id => Number(id))
  return rooms.value.filter(r => ids.includes(r.id))
})

const activeRoomBookings = computed(() => {
  return bookings.value
    .filter(booking => booking.booking_type === 'room' && String(booking.status || '') !== 'cancelled')
    .map(booking => {
      const roomIds = Array.isArray(booking.room_ids)
        ? booking.room_ids.map(id => String(id || '')).filter(Boolean)
        : (booking.room ? [String(booking.room)] : [])
      return {
        id: booking.id,
        start_date: String(booking.start_date || '').slice(0, 10),
        end_date: String(booking.end_date || '').slice(0, 10),
        roomIds,
      }
    })
    .filter(booking => booking.roomIds.length && booking.start_date && booking.end_date)
})

const roomBookingsIndex = computed(() => {
  const index = new Map()
  activeRoomBookings.value.forEach(booking => {
    booking.roomIds.forEach(roomId => {
      if (!index.has(roomId)) index.set(roomId, [])
      index.get(roomId).push(booking)
    })
  })
  return index
})

const selectedRoomBookingConflicts = (roomId) => {
  const start = String(form.value.start_date || '').slice(0, 10)
  const end = String(form.value.end_date || '').slice(0, 10)
  return (roomBookingsIndex.value.get(String(roomId)) || []).filter(booking => {
    if (!start || !end) return false
    return booking.start_date <= end && booking.end_date >= start
  })
}

const selectedHall = computed(() => {
  return halls.value.find(h => String(h.id) === String(form.value.hall))
})

const availableAdditionalServices = computed(() => {
  if (form.value.booking_type === 'hall') {
    return selectedHall.value?.additional_services || []
  }
  if (!selectedRooms.value.length) return []
  const list = []
  selectedRooms.value.forEach(room => {
    (room.additional_services || []).forEach(srv => {
      if (!list.some(item => item.name === srv.name)) {
        list.push(srv)
      }
    })
  })
  return list
})

const calculatedDuration = computed(() => {
  if (!form.value.start_date || !form.value.end_date) return 0
  try {
    const s = new Date(form.value.start_date)
    const e = new Date(form.value.end_date)
    const diff = Math.ceil((e - s) / (1000 * 60 * 60 * 24))
    const res = form.value.booking_type === 'hall' ? diff + 1 : diff
    return res > 0 ? res : 0
  } catch {
    return 0
  }
})

const calculatedBaseAccomodation = computed(() => {
  const days = calculatedDuration.value
  if (form.value.booking_type === 'hall') {
    const price = Number(selectedHall.value?.price_per_day || 0)
    return days * price
  }
  const totalPerNight = selectedRooms.value.reduce((acc, r) => acc + Number(r.price_per_night || 0), 0)
  return days * totalPerNight
})

const calculatedServicesTotal = computed(() => {
  let total = 0
  const selected = form.value.additional_services_selected || []
  const available = availableAdditionalServices.value
  selected.forEach(item => {
    const match = available.find(s => s.name === item.name)
    if (!match) return
    if (match.has_subservices) {
      (item.subservices || []).forEach(sub => {
        const subMatch = (match.subservices || []).find(s => s.name === sub.name)
        if (subMatch) {
          total += Number(subMatch.price || 0) * Number(sub.quantity || 1)
        }
      })
    } else {
      total += Number(match.price || 0) * Number(item.quantity || 1)
    }
  })
  return total
})

const calculatedSubtotalHt = computed(() => {
  return calculatedBaseAccomodation.value + calculatedServicesTotal.value
})

const calculatedTvaAmount = computed(() => {
  if (form.value.booking_type !== 'room') return 0
  return Math.round(calculatedBaseAccomodation.value * 0.1)
})

const calculatedTotalPrice = computed(() => {
  const gross = calculatedSubtotalHt.value + calculatedTvaAmount.value
  const discount = Math.max(0, Number(form.value.discount_amount || 0))
  return Math.max(0, gross - discount)
})

const grossProformaAmount = computed(() => calculatedSubtotalHt.value + calculatedTvaAmount.value)

const applyQuickDiscountPercent = (pct) => {
  if (!canManageProformaDiscount.value || grossProformaAmount.value <= 0) return
  discountEnabled.value = true
  form.value.discount_amount = Math.round(grossProformaAmount.value * (pct / 100))
  if (!form.value.discount_reason || form.value.discount_reason.startsWith('Remise ')) {
    form.value.discount_reason = `Remise ${pct}%`
  }
}

const clearDiscount = () => {
  form.value.discount_amount = 0
  form.value.discount_reason = ''
}

const setDiscountEnabled = (value) => {
  if (!canManageProformaDiscount.value) return
  discountEnabled.value = Boolean(value)
  if (!discountEnabled.value) clearDiscount()
}

// Customer Search & Quick Add
const customerSearchResults = computed(() => {
  const q = String(customerSearch.value || '').toLowerCase().trim()
  if (!q) return customers.value.slice(0, 8)
  return customers.value.filter(c => {
    const name = `${c.full_name || ''} ${c.first_name || ''} ${c.last_name || ''}`.toLowerCase()
    const phone = String(c.phone || '').toLowerCase()
    const email = String(c.email || '').toLowerCase()
    return name.includes(q) || phone.includes(q) || email.includes(q)
  }).slice(0, 8)
})

const selectedCustomerBadge = computed(() => {
  if (form.value.customer) {
    const c = customers.value.find(item => String(item.id) === String(form.value.customer))
    if (c) return `${c.first_name || ''} ${c.last_name || ''}`.trim() || c.phone
  }
  if (form.value.customer_first_name) {
    return `${form.value.customer_first_name} ${form.value.customer_last_name}`.trim()
  }
  return null
})

const selectCustomer = (c) => {
  if (!c) return
  form.value.customer = c.id
  form.value.customer_first_name = c.first_name || ''
  form.value.customer_last_name = c.last_name || ''
  form.value.customer_phone = c.phone || ''
  form.value.customer_email = c.email || ''
  customerResultsOpen.value = false
  customerSearch.value = c.full_name || `${c.first_name || ''} ${c.last_name || ''}`.trim()
}

const clearSelectedCustomer = () => {
  form.value.customer = null
  form.value.customer_first_name = ''
  form.value.customer_last_name = ''
  form.value.customer_phone = ''
  form.value.customer_email = ''
  customerSearch.value = ''
  customerResultsOpen.value = true
}

const fetchCustomersForSearch = async (searchTerm = '') => {
  const requestId = ++customerRequestId
  loadingCustomers.value = true
  try {
    const response = await api.get('customers/', {
      params: { limit: searchTerm ? 12 : 8, ...(searchTerm ? { search: searchTerm } : {}) },
    })
    if (requestId !== customerRequestId) return
    customers.value = Array.isArray(response.data) ? response.data : (response.data?.results || [])
  } catch {
    if (requestId === customerRequestId) customers.value = []
  } finally {
    if (requestId === customerRequestId) loadingCustomers.value = false
  }
}

const openCustomerResults = () => {
  customerResultsOpen.value = true
  fetchCustomersForSearch(String(customerSearch.value || '').trim())
}

watch(customerSearch, (value) => {
  if (!showFormModal.value || !customerResultsOpen.value) return
  if (customerSearchTimer) clearTimeout(customerSearchTimer)
  customerSearchTimer = setTimeout(() => {
    fetchCustomersForSearch(String(value || '').trim())
  }, 180)
})

const toggleQuickCustomerForm = () => {
  showQuickCustomerForm.value = !showQuickCustomerForm.value
}

const saveQuickCustomer = async () => {
  if (!quickCustomer.value.first_name.trim() || !quickCustomer.value.phone.trim()) {
    notify('Le prénom et le téléphone sont obligatoires', 'warning')
    return
  }
  savingQuickCustomer.value = true
  try {
    const res = await api.post('customers/', quickCustomer.value)
    customers.value.unshift(res.data)
    selectCustomer(res.data)
    showQuickCustomerForm.value = false
    quickCustomer.value = { first_name: '', last_name: '', phone: '', email: '' }
    notify('Client créé et lié au devis', 'success')
  } catch (err) {
    notify('Erreur lors de la création du client', 'danger')
  } finally {
    savingQuickCustomer.value = false
  }
}

// Services management
const isServiceSelected = (name) => {
  return (form.value.additional_services_selected || []).some(s => s.name === name)
}

const toggleServiceSelection = (srv) => {
  const list = form.value.additional_services_selected || []
  const idx = list.findIndex(s => s.name === srv.name)
  if (idx >= 0) {
    list.splice(idx, 1)
  } else {
    list.push({
      name: srv.name,
      quantity: 1,
      subservices: srv.has_subservices ? [] : undefined,
    })
  }
  form.value.additional_services_selected = [...list]
}

const isSubserviceSelected = (srvName, subName) => {
  const srv = (form.value.additional_services_selected || []).find(s => s.name === srvName)
  if (!srv || !Array.isArray(srv.subservices)) return false
  return srv.subservices.some(sub => sub.name === subName)
}

const toggleSubserviceSelection = (srvName, sub) => {
  const srv = (form.value.additional_services_selected || []).find(s => s.name === srvName)
  if (!srv) return
  if (!Array.isArray(srv.subservices)) srv.subservices = []
  const idx = srv.subservices.findIndex(item => item.name === sub.name)
  if (idx >= 0) {
    srv.subservices.splice(idx, 1)
  } else {
    srv.subservices.push({ name: sub.name, quantity: 1 })
  }
  form.value.additional_services_selected = [...form.value.additional_services_selected]
}

const getServiceQty = (name) => {
  const item = (form.value.additional_services_selected || []).find(s => s.name === name)
  return item?.quantity || 0
}

const setServiceQty = (name, val) => {
  const item = (form.value.additional_services_selected || []).find(s => s.name === name)
  if (item) {
    item.quantity = Math.max(1, parseInt(val) || 1)
  }
}

const changeProformaServiceQuantity = (service, delta) => {
  const current = getServiceQty(service.name)
  const next = current + Number(delta || 0)
  if (next <= 0) {
    form.value.additional_services_selected = (form.value.additional_services_selected || []).filter(item => item.name !== service.name)
    return
  }
  if (!isServiceSelected(service.name)) {
    toggleServiceSelection(service)
    return
  }
  setServiceQty(service.name, next)
}

const getSubserviceQty = (srvName, subName) => {
  const srv = (form.value.additional_services_selected || []).find(s => s.name === srvName)
  const sub = (srv?.subservices || []).find(item => item.name === subName)
  return sub?.quantity || 0
}

const setSubserviceQty = (srvName, subName, val) => {
  const srv = (form.value.additional_services_selected || []).find(s => s.name === srvName)
  const sub = (srv?.subservices || []).find(item => item.name === subName)
  if (sub) {
    sub.quantity = Math.max(1, parseInt(val) || 1)
  }
}

const changeProformaSubserviceQuantity = (service, subservice, delta) => {
  const current = getSubserviceQty(service.name, subservice.name)
  const next = current + Number(delta || 0)
  if (next <= 0) {
    const parent = (form.value.additional_services_selected || []).find(item => item.name === service.name)
    if (!parent) return
    parent.subservices = (parent.subservices || []).filter(item => item.name !== subservice.name)
    form.value.additional_services_selected = [...form.value.additional_services_selected]
    return
  }
  if (!isServiceSelected(service.name)) toggleServiceSelection(service)
  if (!isSubserviceSelected(service.name, subservice.name)) toggleSubserviceSelection(service.name, subservice)
  setSubserviceQty(service.name, subservice.name, next)
}

const roomTypeLabel = (roomType) => ({
  single: 'Simple',
  double: 'Double',
  suite: 'Suite',
  family: 'Familiale',
}[String(roomType || '').toLowerCase()] || roomType || 'Standard')

const roomStatusLabel = (status) => ({
  available: 'Disponible',
  reserved: 'Réservée',
  occupied: 'Occupée',
  maintenance: 'Maintenance',
}[String(status || '').toLowerCase()] || 'Disponible')

const isRoomUnavailable = (roomId) => {
  const room = rooms.value.find(item => Number(item.id) === Number(roomId))
  return ['occupied', 'maintenance'].includes(String(room?.status || '').toLowerCase()) || selectedRoomBookingConflicts(roomId).length > 0
}

const roomAvailabilityMessage = (room) => {
  const conflicts = selectedRoomBookingConflicts(room?.id)
  const periods = roomBookingsIndex.value.get(String(room?.id)) || []
  const [firstPeriod, ...otherPeriods] = conflicts.length ? conflicts : periods
  if (firstPeriod) {
    const suffix = otherPeriods.length ? ` • +${otherPeriods.length} autre(s) période(s)` : ''
    return `Réservée du ${firstPeriod.start_date} au ${firstPeriod.end_date}${suffix}`
  }
  const status = String(room?.status || '').toLowerCase()
  if (status === 'reserved') return 'Chambre actuellement réservée'
  if (status === 'occupied') return 'Chambre actuellement occupée'
  if (status === 'maintenance') return 'Chambre indisponible pour maintenance'
  return ''
}

const toggleRoomSelection = (id) => {
  if (isRoomUnavailable(id)) return
  const roomId = String(id)
  const selected = form.value.rooms_selected.map(String)
  const next = selected.includes(roomId)
    ? selected.filter(item => item !== roomId)
    : [...selected, roomId]
  form.value.rooms_selected = next
  onRoomsSelectionChange()
}

const isRoomSelected = (id) => {
  return form.value.rooms_selected.includes(String(id))
}

const onRoomsSelectionChange = () => {
  if (form.value.rooms_selected.length > 0) {
    form.value.room = form.value.rooms_selected[0]
  } else {
    form.value.room = ''
  }
}

const onBookingTypeChange = () => {
  if (form.value.booking_type === 'hall') {
    form.value.event_type = 'Mariage'
    form.value.rooms_selected = []
    form.value.room = ''
  } else {
    form.value.event_type = 'Séjour'
    form.value.hall = ''
  }
}

const onCustomerKindChange = () => {
  if (form.value.customer_kind === 'organization') {
    form.value.customer = null
  }
}

// Fetching & Filtering
const fetchProformas = async () => {
  loadingProformas.value = true
  try {
    const res = await api.get('proformas/')
    proformas.value = Array.isArray(res.data) ? res.data : (res.data?.results || [])
  } catch (err) {
    notify('Impossible de charger les factures proforma', 'danger')
  } finally {
    loadingProformas.value = false
  }
}

const fetchFacilitiesAndCustomers = async () => {
  const responses = await Promise.allSettled([
    api.get('halls/'),
    api.get('rooms/'),
    api.get('customers/', { params: { limit: 12 } }),
    api.get('bookings/'),
  ])
  const [hRes, rRes, cRes, bRes] = responses
  if (hRes.status === 'fulfilled') {
    halls.value = Array.isArray(hRes.value.data) ? hRes.value.data : (hRes.value.data?.results || [])
  }
  if (rRes.status === 'fulfilled') {
    rooms.value = Array.isArray(rRes.value.data) ? rRes.value.data : (rRes.value.data?.results || [])
  }
  if (cRes.status === 'fulfilled') {
    customers.value = Array.isArray(cRes.value.data) ? cRes.value.data : (cRes.value.data?.results || [])
  }
  if (bRes.status === 'fulfilled') {
    bookings.value = Array.isArray(bRes.value.data) ? bRes.value.data : (bRes.value.data?.results || [])
  }
}

const filteredProformas = computed(() => {
  let list = [...proformas.value]

  const q = search.value.toLowerCase().trim()
  if (q) {
    list = list.filter(p => {
      const code = String(p.code || '').toLowerCase()
      const cName = String(p.customer_name || '').toLowerCase()
      const org = String(p.organization_name || '').toLowerCase()
      const hall = String(p.hall_name || '').toLowerCase()
      const room = String(p.room_display || '').toLowerCase()
      return code.includes(q) || cName.includes(q) || org.includes(q) || hall.includes(q) || room.includes(q)
    })
  }

  if (statusFilter.value) {
    list = list.filter(p => p.status === statusFilter.value)
  }

  if (typeFilter.value) {
    list = list.filter(p => p.booking_type === typeFilter.value)
  }

  const minAmt = parseFloat(minAmountInput.value)
  if (!isNaN(minAmt)) {
    list = list.filter(p => Number(p.total_price || 0) >= minAmt)
  }

  const maxAmt = parseFloat(maxAmountInput.value)
  if (!isNaN(maxAmt)) {
    list = list.filter(p => Number(p.total_price || 0) <= maxAmt)
  }

  // Sorting
  list.sort((a, b) => {
    let aVal = a[sortKey.value]
    let bVal = b[sortKey.value]
    if (sortKey.value === 'total_price') {
      aVal = Number(aVal || 0)
      bVal = Number(bVal || 0)
    }
    if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1
    return 0
  })

  return list
})

const proformasTotalItems = computed(() => filteredProformas.value.length)
const proformasStartIndex = computed(() => (page.value - 1) * pageSize.value + 1)
const proformasEndIndex = computed(() => Math.min(page.value * pageSize.value, proformasTotalItems.value))
const proformasCanPrev = computed(() => page.value > 1)
const proformasCanNext = computed(() => proformasEndIndex.value < proformasTotalItems.value)

const paginatedProformas = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredProformas.value.slice(start, start + pageSize.value)
})

const proformasPrevPage = () => { if (proformasCanPrev.value) page.value-- }
const proformasNextPage = () => { if (proformasCanNext.value) page.value++ }

const toggleSort = (key) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDirection.value = 'asc'
  }
}
const isSortActive = (key) => sortKey.value === key
const sortIconClass = (key) => {
  if (sortKey.value !== key) return 'fas fa-sort'
  return sortDirection.value === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down'
}

const resetFilters = () => {
  search.value = ''
  statusFilter.value = ''
  typeFilter.value = ''
  preset.value = 'all'
  customStart.value = ''
  customEnd.value = ''
  minAmountInput.value = ''
  maxAmountInput.value = ''
  page.value = 1
}

const activeRangeNotice = computed(() => {
  if (preset.value === 'all') return 'Affichage de toutes les proformas.'
  return `Filtre actif: ${preset.value}`
})

// Modal actions
const openAddModal = () => {
  isEditing.value = false
  const today = new Date().toISOString().split('T')[0]
  const in7days = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  form.value = {
    id: null,
    customer_kind: 'individual',
    customer: null,
    customer_first_name: '',
    customer_last_name: '',
    organization_name: '',
    organization_contact_name: '',
    customer_phone: '',
    customer_email: '',
    booking_type: 'hall',
    hall: halls.value[0]?.id || '',
    room: '',
    rooms_selected: [],
    event_type: 'Mariage',
    start_date: today,
    end_date: today,
    valid_until: in7days,
    discount_amount: 0,
    discount_reason: '',
    additional_services_selected: [],
    notes: '',
  }
  discountEnabled.value = false
  fetchCalendarRanges()
  showFormModal.value = true
}

const editProforma = (p) => {
  closeActions()
  isEditing.value = true
  const rawRooms = Array.isArray(p.room_ids) && p.room_ids.length
    ? p.room_ids.map(id => String(id))
    : (p.room ? [String(p.room)] : [])
  form.value = {
    id: p.id,
    customer_kind: p.customer_kind || 'individual',
    customer: p.customer || null,
    customer_first_name: p.customer_name?.split(' ')[0] || '',
    customer_last_name: p.customer_name?.split(' ').slice(1).join(' ') || '',
    organization_name: p.organization_name || '',
    organization_contact_name: p.organization_contact_name || '',
    customer_phone: p.customer_phone || '',
    customer_email: p.customer_email || '',
    booking_type: p.booking_type || 'hall',
    hall: p.hall || '',
    room: p.room || '',
    rooms_selected: rawRooms,
    event_type: p.event_type || 'Mariage',
    start_date: p.start_date || '',
    end_date: p.end_date || '',
    valid_until: p.valid_until || '',
    discount_amount: Number(p.discount_amount || 0),
    discount_reason: p.discount_reason || '',
    additional_services_selected: p.additional_services_selected || [],
    notes: p.notes || '',
  }
  discountEnabled.value = canManageProformaDiscount.value && (Number(form.value.discount_amount || 0) > 0 || Boolean(String(form.value.discount_reason || '').trim()))
  fetchCalendarRanges()
  showFormModal.value = true
}

const saveProforma = async () => {
  const isOrg = form.value.customer_kind === 'organization'
  const fullName = isOrg
    ? form.value.organization_name
    : `${form.value.customer_first_name} ${form.value.customer_last_name}`.trim()

  if (!fullName) {
    notify('Le nom du client ou de l’organisation est obligatoire', 'warning')
    return
  }

  if (form.value.booking_type === 'hall' && !form.value.hall) {
    notify('Veuillez sélectionner une salle', 'warning')
    return
  }
  if (form.value.booking_type === 'room' && !form.value.rooms_selected.length) {
    notify('Veuillez sélectionner au moins une chambre', 'warning')
    return
  }

  savingProforma.value = true
  try {
    const { rooms_selected, ...rest } = form.value
    const payload = {
      ...rest,
      customer_name: fullName,
      room_ids: form.value.booking_type === 'room' ? form.value.rooms_selected.map(id => Number(id)) : [],
      room: form.value.booking_type === 'room' ? (form.value.rooms_selected[0] || null) : null,
      hall: form.value.booking_type === 'hall' ? form.value.hall : null,
      total_price: Math.max(0, Number(calculatedTotalPrice.value || 0)),
      discount_amount: Math.max(0, Number(form.value.discount_amount || 0)),
    }

    if (isEditing.value) {
      await api.put(`proformas/${form.value.id}/`, payload)
      notify('Facture proforma mise à jour avec succès', 'success')
    } else {
      await api.post('proformas/', payload)
      notify('Facture proforma enregistrée avec succès', 'success')
    }
    showFormModal.value = false
    await fetchProformas()
  } catch (err) {
    const data = err?.response?.data || {}
    notify(data.detail || Object.values(data)[0] || 'Erreur lors de l’enregistrement', 'danger')
  } finally {
    savingProforma.value = false
  }
}

const viewProforma = (p) => {
  closeActions()
  selectedProforma.value = p
  showViewModal.value = true
}

const confirmDelete = (p) => {
  closeActions()
  selectedProforma.value = p
  showDeleteModal.value = true
}

const deleteProforma = async () => {
  if (!selectedProforma.value) return
  deletingProforma.value = true
  try {
    await api.delete(`proformas/${selectedProforma.value.id}/`)
    notify('Facture proforma supprimée', 'success')
    showDeleteModal.value = false
    await fetchProformas()
  } catch (err) {
    notify('Erreur lors de la suppression de la proforma', 'danger')
  } finally {
    deletingProforma.value = false
  }
}

// Convert to Booking
const handleConvertClick = (p) => {
  closeActions()
  selectedProforma.value = p
  showConvertModal.value = true
}

const executeConvert = async () => {
  if (!selectedProforma.value) return
  convertingId.value = selectedProforma.value.id
  try {
    await api.post(`proformas/${selectedProforma.value.id}/convert/`)
    notify('Devis proforma converti avec succès en réservation !', 'success')
    showConvertModal.value = false
    showViewModal.value = false
    await fetchProformas()
  } catch (err) {
    const data = err?.response?.data || {}
    notify(data.detail || 'Impossible de convertir cette proforma en réservation', 'danger')
  } finally {
    convertingId.value = null
  }
}

// PDF Generation
const buildProformaPdfHtml = (p) => {
  const displayId = getProformaDisplayId(p)
  const periodLabel = formatDateRange(p.start_date, p.end_date)
  const itemSummary = getProformaItemSummary(p)
  const duration = calculatedDurationFromDates(p.start_date, p.end_date, p.booking_type)

  const clientRows = [
    ['Client / Destinataire', p.customer_name || '-'],
    ...(p.organization_name ? [['Organisation', p.organization_name]] : []),
    ['Téléphone', p.customer_phone || '-'],
    ['Email', p.customer_email || '-'],
  ]

  const discountVal = Number(p.discount_amount || 0)
  const addonsTotal = Number(p.addons_total || 0)
  const baseAmount = Math.max(0, Number(p.subtotal_ht || 0) + discountVal - addonsTotal)
  const durationLabel = `${duration} ${p.booking_type === 'room' ? 'nuit(s)' : 'jour(s)'}`
  const itemsRows = [
    [
      p.booking_type === 'hall' ? 'Location Salle Événementielle' : 'Hébergement en Chambre(s)',
      itemSummary,
      durationLabel,
      formatMoney(baseAmount),
    ]
  ]

  const catalogServices = p.booking_type === 'hall'
    ? (halls.value.find(hall => String(hall.id) === String(p.hall))?.additional_services || [])
    : rooms.value
      .filter(room => (Array.isArray(p.room_ids) ? p.room_ids : [p.room]).map(String).includes(String(room.id)))
      .flatMap(room => room.additional_services || [])
  const selectedServices = Array.isArray(p.additional_services_selected) ? p.additional_services_selected : []
  selectedServices.forEach(selected => {
    const catalog = catalogServices.find(service => service.name === selected.name)
    if (!catalog) return
    if (catalog.has_subservices) {
      ;(selected.subservices || []).forEach(selectedSub => {
        const sub = (catalog.subservices || []).find(item => item.name === selectedSub.name)
        if (!sub) return
        const quantity = Number(selectedSub.quantity || 1)
        itemsRows.push([`Service - ${catalog.name}`, `${sub.name} x ${quantity}`, 'Option', formatMoney(Number(sub.price || 0) * quantity)])
      })
    } else {
      const quantity = Number(selected.quantity || 1)
      itemsRows.push(['Service additionnel', `${catalog.name} x ${quantity}`, 'Option', formatMoney(Number(catalog.price || 0) * quantity)])
    }
  })

  const tvaVal = Number(p.tva_amount || 0)
  const totalVal = Number(p.total_price || 0)

  return buildPdfDocumentHtml({
    title: 'Facture Proforma',
    documentTitle: `Proforma ${displayId}`,
    subtitle: 'Ce document est une facture proforma / devis estimatif valable sous réserve de disponibilité au moment de la confirmation.',
    typeLabel: 'Facture Proforma',
    headerVariant: 'ticket',
    headerEyebrow: 'DEVIS & FACTURE PROFORMA',
    headerReference: displayId,
    tableTitle: 'Détail de la proposition',
    tableTitles: ['Client et contact', 'Prestations prévues', 'Récapitulatif financier'],
    periodLabel,
    contentHtml: `
      <div class="section-card">
        <div class="section-header"><h2>Client & Contact</h2></div>
        <table>
          <thead>
            <tr><th>Information</th><th>Détails</th></tr>
          </thead>
          <tbody>
            ${clientRows.map(([label, val]) => `<tr><td>${escapeHtml(label)}</td><td>${escapeHtml(val)}</td></tr>`).join('')}
            <tr><td>Validité du devis</td><td><strong>${escapeHtml(p.valid_until ? formatDisplayDate(p.valid_until) : '7 jours à compter de l’émission')}</strong></td></tr>
          </tbody>
        </table>
      </div>

      <div class="section-card">
        <div class="section-header"><h2>Prestations & Période</h2></div>
        <table>
          <thead>
            <tr>
              <th>Désignation</th>
              <th>Emplacement / Détail</th>
              <th>Durée</th>
              <th>Montant HT</th>
            </tr>
          </thead>
          <tbody>
            ${itemsRows.map(([desig, det, dur, mt]) => `
              <tr>
                <td>${escapeHtml(desig)}</td>
                <td>${escapeHtml(det)}</td>
                <td>${escapeHtml(dur)}</td>
                <td>${escapeHtml(mt)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <div class="section-card">
        <div class="section-header"><h2>Total & Règlement</h2></div>
        <table>
          <tbody>
            <tr><td>Sous-total HT</td><td style="text-align:right;">${escapeHtml(formatMoney(p.subtotal_ht))}</td></tr>
            ${tvaVal > 0 ? `<tr><td>TCSTH (10%)</td><td style="text-align:right;">${escapeHtml(formatMoney(tvaVal))}</td></tr>` : ''}
            ${discountVal > 0 ? `<tr><td>Remise commerciale</td><td style="text-align:right; color:#b91c1c;">-${escapeHtml(formatMoney(discountVal))}</td></tr>` : ''}
            <tr style="font-size:1.1rem; font-weight:800; background:#f8fafc;">
              <td>Total Net TTC</td>
              <td style="text-align:right;">${escapeHtml(formatMoney(totalVal))}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section-card">
        <div class="section-header"><h2>Conditions d'acceptation</h2></div>
        <p>Pour confirmer cette réservation, veuillez valider cette facture proforma auprès de notre service d'accueil ou effectuer un acompte convenu. Une facture officielle et un reçu de paiement vous seront alors délivrés.</p>
        ${p.notes ? `<p><strong>Notes :</strong> ${escapeHtml(p.notes)}</p>` : ''}
      </div>
    `,
  })
}

const calculatedDurationFromDates = (s, e, bookingType = 'hall') => {
  if (!s || !e) return 1
  try {
    const start = new Date(s)
    const end = new Date(e)
    const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24))
    const d = bookingType === 'room' ? diff : diff + 1
    return d > 0 ? d : 1
  } catch {
    return 1
  }
}

const printProformaPdf = async (p) => {
  if (!p || !process.client || downloadingProformaId.value) return
  closeActions()
  downloadingProformaId.value = p.id
  try {
    const html = buildProformaPdfHtml(p)
    const ok = await downloadPdfHtml({
      html,
      fileName: buildExportFileName(`proforma-${p.code || p.id}`, 'pdf'),
    })
    if (!ok) notify('Impossible de télécharger la proforma PDF', 'warning')
  } catch (error) {
    console.error('Proforma PDF download failed', error)
    notify('Erreur lors de la génération de la proforma PDF', 'danger')
  } finally {
    downloadingProformaId.value = null
  }
}

const exportPdf = async () => {
  exportingPdf.value = true
  try {
    const tableEl = document.querySelector('.proformas-table')
    if (!tableEl) return
    const html = buildPdfDocumentHtml({
      title: 'Liste des factures proforma',
      documentTitle: 'Liste des Proformas',
      tableTitle: 'Proformas',
      periodLabel: activeRangeNotice.value,
      contentHtml: tableEl.outerHTML,
    })
    await downloadPdfHtml({
      html,
      fileName: buildExportFileName('liste-proformas', 'pdf'),
    })
  } finally {
    exportingPdf.value = false
  }
}

const exportXls = async () => {
  exportingXls.value = true
  try {
    const tableEl = document.querySelector('.proformas-table')
    if (!tableEl) return
    downloadExcelTable(tableEl, buildExportFileName('liste-proformas', 'xls'))
  } finally {
    exportingXls.value = false
  }
}

onMounted(() => {
  updateIsMobile()
  window.addEventListener('resize', updateIsMobile)
  document.addEventListener('click', closeActions)
  fetchProformas()
  fetchFacilitiesAndCustomers()
})

onBeforeUnmount(() => {
  if (process.client) {
    window.removeEventListener('resize', updateIsMobile)
    document.removeEventListener('click', closeActions)
  }
  if (customerSearchTimer) clearTimeout(customerSearchTimer)
})
</script>

<style scoped>
.proformas-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-8);
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
  gap: 0.5rem;
}

.controls-top {
  width: 100%;
  display: flex;
  gap: var(--space-3);
  align-items: center;
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
  flex: 1 1 320px;
  min-width: 220px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.9rem;
  pointer-events: none;
}

.search-input-clean,
.filter-select-clean,
.filter-input-clean {
  min-height: 42px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9rem;
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
}

.search-input-clean {
  width: 100%;
  padding: 0.625rem 1rem 0.625rem 2.5rem;
}

.filter-select-clean {
  width: 100%;
  padding: 0.625rem 2rem 0.625rem 1rem;
  cursor: pointer;
}

.filter-input-clean {
  width: 100%;
  padding: 0.625rem 1rem;
}

.search-input-clean:focus,
.filter-select-clean:focus,
.filter-input-clean:focus {
  outline: none;
  background: #ffffff;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.12);
}

.filters-panel {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: var(--space-4);
}

.filter-wrapper {
  flex: 1 1 160px;
  min-width: 145px;
}

.filter-range-note {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.9rem;
  padding-top: 0.75rem;
  /* border-top: 1px solid #e2e8f0; */
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 700;
}

.filter-range-status {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: var(--gray-200);
  color: #1d4ed8;
  font-size: 0.75rem;
  font-weight: 800;
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

:global(html[data-admin-theme="dark"]) .controls {
  background: linear-gradient(145deg, #0f172a 0%, #111c34 100%);
  border-color: #263752;
}

:global(html[data-admin-theme="dark"]) .search-input-clean,
:global(html[data-admin-theme="dark"]) .filter-select-clean,
:global(html[data-admin-theme="dark"]) .filter-input-clean,
:global(html[data-admin-theme="dark"]) .filters-toggle {
  background: #0b1528;
  border-color: #3b4d6b;
  color: #e2e8f0;
}

:global(html[data-admin-theme="dark"]) .search-input-clean::placeholder,
:global(html[data-admin-theme="dark"]) .filter-input-clean::placeholder {
  color: #94a3b8;
}

:global(html[data-admin-theme="dark"]) .search-input-clean:focus,
:global(html[data-admin-theme="dark"]) .filter-select-clean:focus,
:global(html[data-admin-theme="dark"]) .filter-input-clean:focus {
  background: #111c34;
  border-color: #d4af37;
}

:global(html[data-admin-theme="dark"]) .filter-range-note {
  border-top-color: #263752;
  color: #94a3b8;
}

:global(html[data-admin-theme="dark"]) .filter-range-status {
  background: rgba(59, 130, 246, .18);
  color: #93c5fd;
}

@media (max-width: 992px) {
  .filters-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .filters-panel {
    gap: 0.65rem;
  }
}

@media (max-width: 640px) {
  .controls {
    padding: 1rem;
  }

  .controls-top {
    gap: 0.55rem;
  }

  .controls-top > .btn {
    padding-inline: 0.7rem;
  }

  .filter-wrapper {
    flex-basis: 100%;
  }
}

.actions-dropdown {
  position: relative;
  display: inline-flex;
}

.actions-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  background: var(--gray-600);
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
  font-size: 0.88rem;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
}

.actions-item:hover {
  background: var(--gray-600);
  color: #0f172a;
}

.actions-item.highlight-action {
  color: #15803d;
  /* background: var(--gray-200); */
}

.actions-item.highlight-action:hover {
  background: #dcfce7;
}

.actions-item.danger {
  color: #b91c1c;
}

.actions-item.danger:hover {
  background: #fef2f2;
}

/* Form layout */
.proforma-form-shell {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-x: hidden;
}

.proforma-form-shell,
.proforma-form-shell * {
  min-width: 0;
  max-width: 100%;
}

.proforma-form-shell .form-grid,
.proforma-form-shell .pdp-body-grid,
.proforma-form-shell .room-service-flex,
.proforma-form-shell .room-subservice-flex {
  width: 100%;
  min-width: 0;
}

.proforma-form-shell .form-input,
.proforma-form-shell .form-select,
.proforma-form-shell .form-textarea,
.proforma-form-shell .pdp-input {
  max-width: 100%;
}

.booking-form-hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.15rem 1.2rem;
  border: 1px solid rgba(191, 219, 254, 0.9);
  border-radius: 24px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7), 0 16px 32px rgba(15, 23, 42, 0.06);
  flex-wrap: wrap;
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
  color: var(--gray-600);
  line-height: 1.6;
  max-width: 44rem;
  font-size: 0.88rem;
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
  border: 1px solid #e2e8f0;
  border-radius: 22px;
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
  text-transform: uppercase;
  font-size: 0.73rem;
  font-weight: 800;
  color: #2563eb;
  letter-spacing: 0.08em;
}

.booking-form-section-head h4 {
  margin: 0;
  font-size: 1rem;
  color: #0f172a;
  font-weight: 800;
}

.booking-form-section-head p {
  color: var(--gray-600);
  font-size: 0.9rem;
  margin: 0;
  max-width: 28rem;
  line-height: 1.55;
}

.booking-form-grid {
  gap: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.form-group.full {
  grid-column: 1 / -1;
}

.room-selection-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
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
  margin-top: 0.75rem;
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

.room-option-input { position: absolute; opacity: 0; pointer-events: none; }
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

.room-option-card:hover { transform: translateY(-1px); border-color: rgba(59, 130, 246, 0.36); box-shadow: 0 18px 30px rgba(59, 130, 246, 0.12); }
.room-option-card.selected { border-color: rgba(59, 130, 246, 0.68); background: linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%); box-shadow: 0 20px 36px rgba(59, 130, 246, 0.16); }
.room-option-card.selected .room-option-check { border-color: rgba(59, 130, 246, 0.35); background: linear-gradient(180deg, #93c5fd 0%, #60a5fa 100%); color: #ffffff; }
.room-option-card.unavailable { opacity: 0.7; cursor: not-allowed; border-color: rgba(148, 163, 184, 0.2); background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); box-shadow: none; }
.room-option-card.maintenance { border-color: #fecaca; }
.room-option-main { display: grid; gap: 0.45rem; min-width: 0; }
.room-option-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; }
.room-option-main strong { color: #0f172a; font-size: 1rem; line-height: 1.45; }
.room-option-price { color: #0f172a; font-size: 0.82rem; font-weight: 800; white-space: nowrap; }
.room-option-meta { display: flex; align-items: center; gap: 0.55rem; flex-wrap: wrap; }
.room-option-type, .room-option-status { display: inline-flex; align-items: center; padding: 0.35rem 0.7rem; border-radius: 999px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.02em; }
.room-option-type { background: rgba(148, 163, 184, 0.12); color: #475569; }
.room-option-main span, .room-option-main small { color: #64748b; font-size: 0.85rem; }
.room-option-main small { line-height: 1.5; }
.room-option-booked-dates { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.45rem 0.7rem; border-radius: 12px; background: rgba(254, 242, 242, 0.95); border: 1px solid rgba(252, 165, 165, 0.55); color: #b91c1c !important; font-weight: 700; }
.room-option-booked-dates::before { content: ''; width: 7px; height: 7px; border-radius: 999px; background: currentColor; opacity: 0.8; }
.room-option-status.status-available { background: #dcfce7; color: #166534; }
.room-option-status.status-reserved { background: #e2e8f0; color: #475569; }
.room-option-status.status-occupied, .room-option-status.status-maintenance { background: #fee2e2; color: #991b1b; }
.room-option-status.status-cleaning { background: #fef3c7; color: #92400e; }
.room-option-status.status-unknown { background: #e2e8f0; color: #475569; }

.room-option-card .form-hint {
  font-size: 0.85rem;
}

.customer-lookup-card {
  border: 1px dashed #cbd5e1;
  padding: 14px;
  border-radius: 12px;
  /* background: #f8fafc; */
}

.customer-lookup-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.customer-search-shell {
  position: relative;
}

.customer-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.customer-search-input {
  padding-left: 36px;
}

.customer-results-list {
  margin-top: 8px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  max-height: 180px;
  overflow-y: auto;
}

.customer-result-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  border: none;
  background: none;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  text-align: left;
}

.customer-result-item:hover {
  background: #f8fafc;
}

.selected-customer-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #ecfdf5;
  color: #065f46;
  padding: 6px 12px;
  border-radius: 20px;
  margin-top: 10px;
  font-size: 0.88rem;
}

.quick-customer-shell {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  padding: 16px;
  border-radius: 12px;
  margin-top: 10px;
}

/* Services */
.proforma-service-group { margin-top: 0.75rem; }
.room-service-groups { display: flex; flex-direction: column; gap: 12px; }
.room-service-group { border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 18px; padding: 12px; background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); }
.room-service-group-head { display: flex; justify-content: space-between; gap: 8px; align-items: center; margin-bottom: 10px; }
.room-service-group-head div { display: grid; gap: 3px; }
.room-service-group-head strong { color: #0f172a; font-size: 0.93rem; font-weight: 800; }
.room-service-group-head small { color: #64748b; font-size: 0.78rem; font-weight: 700; }
.room-service-group-count { color: #64748b; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; }
.room-service-flex { display: flex; flex-wrap: wrap; gap: 8px; }
.room-service-card { border: 1px solid rgba(203, 213, 225, 0.9); border-radius: 14px; background: #fff; min-width: 190px; max-width: 203px; flex: 1 1 210px; padding: 10px 11px; display: flex; flex-direction: column; gap: 8px; }
.room-service-card.is-active { border-color: rgba(34, 197, 94, 0.55); box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.1); }
.room-service-card-top, .room-service-card-bottom, .room-subservice-top { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.room-service-card-top strong, .room-subservice-top strong { color: #0f172a; font-size: 0.84rem; font-weight: 800; }
.room-service-card-top span, .room-subservice-top span { color: #475569; font-size: 0.78rem; font-weight: 800; white-space: nowrap; }
.room-service-card-bottom small { color: #64748b; font-size: 0.7rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.04em; }
.room-service-stepper { display: inline-flex; align-items: center; gap: 6px; }
.room-service-step-btn { width: 26px; height: 26px; border: 1px solid #cbd5e1; border-radius: 8px; background: #f8fafc; color: #475569; display: inline-flex; align-items: center; justify-content: center; font-size: 0.7rem; cursor: pointer; }
.room-service-step-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.room-service-qty { min-width: 24px; text-align: center; color: #0f172a; font-size: 0.82rem; font-weight: 900; }
.room-service-card-stack { max-width: none; flex: 1 1 100%; }
.room-subservice-flex { display: flex; flex-wrap: wrap; gap: 8px; }
.room-subservice-card { border: 1px solid rgba(203, 213, 225, 0.9); border-radius: 12px; padding: 9px 10px; min-width: 170px; max-width: 220px; flex: 1 1 180px; background: #fff; display: flex; flex-direction: column; gap: 6px; }
.room-subservice-card.is-active { border-color: rgba(59, 130, 246, 0.45); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

.addons-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 10px; }
.addons-total { color: #047857; font-size: .85rem; font-weight: 800; }
.addons-list { display: grid; gap: 10px; }
.addon-item { border: 1px solid #e2e8f0; border-radius: 14px; background: #f8fafc; overflow: hidden; }
.addon-line, .addon-sub-row { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 14px; }
.addon-toggle { display: inline-flex; align-items: center; gap: 10px; min-width: 0; cursor: pointer; }
.addon-toggle input { position: absolute; opacity: 0; pointer-events: none; }
.toggle-switch { position: relative; width: 38px; height: 22px; border-radius: 999px; background: #cbd5e1; flex: 0 0 auto; transition: .18s ease; }
.toggle-knob { position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; box-shadow: 0 2px 5px rgba(15, 23, 42, .18); transition: .18s ease; }
.addon-toggle.is-active .toggle-switch { background: #10b981; }
.addon-toggle.is-active .toggle-knob { transform: translateX(16px); }
.addon-toggle-copy { display: grid; gap: 3px; min-width: 0; }
.addon-toggle-copy strong { color: #0f172a; font-size: .86rem; }
.addon-toggle-copy small, .addon-unit, .muted-line { color: #64748b; font-size: .72rem; }
.addon-side { display: grid; justify-items: end; gap: 7px; flex: 0 0 auto; }
.addon-side-top { display: flex; align-items: baseline; gap: 8px; }
.addon-price { color: #0f172a; font-size: .84rem; }
.addon-qty-control { display: flex; align-items: center; gap: 8px; }
.addon-qty-control.is-disabled { opacity: .45; }
.addon-qty-label { color: #64748b; font-size: .72rem; font-weight: 700; }
.addon-stepper { display: inline-flex; align-items: center; border: 1px solid #cbd5e1; border-radius: 8px; overflow: hidden; background: #fff; }
.addon-step-btn { width: 27px; height: 27px; border: 0; background: #f1f5f9; color: #334155; cursor: pointer; }
.addon-step-btn:disabled { cursor: not-allowed; opacity: .45; }
.addon-qty-input { width: 40px; height: 27px; border: 0; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; text-align: center; font-weight: 700; }
.addon-line-total { color: #047857; font-size: .75rem; }
.addon-sub-block { padding: 12px 14px; }
.addon-sub-head { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 8px; }
.addon-subs { display: grid; gap: 6px; padding-left: 12px; border-left: 2px solid #dbeafe; }
.addon-sub-row { padding: 8px 0; }

.pricing-discount-panel { display: flex; flex-direction: column; gap: 16px; padding: 18px; border: 1px solid #dbeafe; border-radius: 18px; background: #fff; box-shadow: 0 8px 24px rgba(15, 23, 42, .05); }
.pdp-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding-bottom: 14px; border-bottom: 1px solid #e2e8f0; }
.pdp-header-left { display: flex; align-items: center; gap: 12px; }
.pdp-icon-box { display: grid; place-items: center; width: 38px; height: 38px; border-radius: 10px; color: #059669; background: #ecfdf5; }
.pdp-title { margin: 0; color: #0f172a; font-size: .95rem; font-weight: 800; }
.pdp-subtitle { margin: 3px 0 0; color: #64748b; font-size: .78rem; }
.pdp-discount-toggle { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; }
.pdp-discount-toggle input { position: absolute; opacity: 0; pointer-events: none; }
.pdp-discount-toggle-track { position: relative; width: 46px; height: 28px; border-radius: 999px; background: #cbd5e1; flex: 0 0 auto; }
.pdp-discount-toggle-knob { position: absolute; top: 3px; left: 3px; width: 20px; height: 20px; border-radius: 50%; background: #fff; box-shadow: 0 3px 8px rgba(15, 23, 42, .2); transition: .18s ease; }
.pdp-discount-toggle.is-active .pdp-discount-toggle-track { background: #10b981; }
.pdp-discount-toggle.is-active .pdp-discount-toggle-knob { transform: translateX(18px); }
.pdp-discount-toggle-copy { display: grid; gap: 2px; }
.pdp-discount-toggle-copy strong { color: #0f172a; font-size: .8rem; }
.pdp-discount-toggle-copy small { color: #64748b; font-size: .72rem; }
.pdp-body-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(280px, .9fr); gap: 16px; }
.pdp-control-card { display: grid; gap: 12px; padding: 16px; border: 1px solid #e2e8f0; border-radius: 14px; }
.pdp-field-header { display: flex; justify-content: space-between; align-items: center; }
.pdp-label { display: inline-flex; align-items: center; gap: 6px; color: #334155; font-size: .82rem; font-weight: 700; }
.pdp-clear-btn { border: 0; background: transparent; color: #ef4444; font-size: .73rem; font-weight: 700; cursor: pointer; }
.pdp-input-wrapper { position: relative; display: flex; align-items: center; }
.pdp-input { width: 100%; height: 42px; border: 1.5px solid #cbd5e1; border-radius: 10px; background: #f8fafc; color: #0f172a; font-weight: 700; padding: 0 3.2rem 0 2.2rem; }
.pdp-input-reason { padding: 0 12px; font-weight: 500; }
.pdp-input-icon { position: absolute; left: 10px; }
.pdp-input-suffix { position: absolute; right: 8px; padding: 3px 6px; border-radius: 6px; background: #e2e8f0; color: #475569; font-size: .68rem; font-weight: 800; }
.pdp-presets { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.pdp-presets-label { color: #64748b; font-size: .72rem; font-weight: 700; }
.pdp-presets-list { display: flex; gap: 5px; }
.pdp-preset-btn { padding: 3px 8px; border: 1px solid #cbd5e1; border-radius: 6px; background: #f1f5f9; color: #334155; font-size: .72rem; font-weight: 700; cursor: pointer; }
.pdp-preset-btn.is-active { border-color: #059669; background: #059669; color: #fff; }
.pdp-hero-card { display: grid; align-content: start; gap: 16px; padding: 18px; border-radius: 14px; background: linear-gradient(145deg, #0f172a, #1e293b); color: #fff; }
.pdp-hero-label { color: #94a3b8; font-size: .8rem; font-weight: 800; text-transform: uppercase; }
.pdp-hero-val { color: #fff; font-size: 1.75rem; font-weight: 900; }
.pdp-mini-summary { display: grid; gap: 6px; padding: 8px 10px; border: 1px solid rgba(255,255,255,.08); border-radius: 8px; background: rgba(0,0,0,.25); }
.pdp-summary-row { display: flex; justify-content: space-between; gap: 10px; font-size: .73rem; }
.pdp-summary-k { color: #94a3b8; }
.pdp-summary-v { color: #e2e8f0; font-weight: 700; }
.pdp-summary-discount .pdp-summary-k, .pdp-summary-discount .pdp-summary-v { color: #34d399; }

.services-list-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.service-item-card {
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.service-item-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.service-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.subservices-wrapper {
  margin-top: 8px;
  padding-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.subservice-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.qty-input {
  width: 70px;
  padding: 4px 8px;
  height: 32px;
}

/* Summary Card */
.summary-breakdown-card {
  /* background: #f8fafc; */
  border: 1px solid var(--gray-300);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.92rem;
  color: var(--gray-600);
}

.breakdown-row.discount {
  color: #b91c1c;
}

.breakdown-row.total {
  border-top: 2px solid #e2e8f0;
  padding-top: 8px;
  margin-top: 4px;
  font-size: 1.1rem;
  color: var(--gray-600);
}

.modal-actions-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.convert-summary-pill {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  margin: 12px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Entity View Modal (Details View) */
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
.entity-view-item.highlight { background: #eff6ff; border-color: rgba(59, 130, 246, 0.22); }
.entity-view-label { color: #64748b; font-size: .82rem; font-weight: 700; }
.entity-view-value { color: #0f172a; font-size: .9rem; font-weight: 700; text-align: right; word-break: break-word; }

/* Dark mode overrides */
:global(html[data-admin-theme="dark"]) .booking-form-hero {
  border-color: rgba(51, 65, 85, 0.95);
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 34%),
    linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(30, 41, 59, 0.92) 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 16px 30px rgba(2, 6, 23, 0.28);
}

:global(html[data-admin-theme="dark"]) .booking-form-eyebrow {
  background: rgba(59, 130, 246, 0.18);
  color: #bfdbfe;
}

:global(html[data-admin-theme="dark"]) .booking-form-hero-copy h3,
:global(html[data-admin-theme="dark"]) .booking-form-section-head h4,
:global(html[data-admin-theme="dark"]) .booking-form-section {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .booking-form-hero-copy p,
:global(html[data-admin-theme="dark"]) .booking-form-section-head p,
:global(html[data-admin-theme="dark"]) .booking-form-section {
  color: rgba(226, 232, 240, 0.72);
}

:global(html[data-admin-theme="dark"]) .booking-form-chip {
  background: rgba(15, 23, 42, 0.62);
  border-color: rgba(51, 65, 85, 0.95);
  color: rgba(226, 232, 240, 0.88);
}

:global(html[data-admin-theme="dark"]) .booking-form-chip.accent {
  background: rgba(212, 175, 55, 0.16);
  border-color: rgba(212, 175, 55, 0.28);
  color: #fde68a;
}

:global(html[data-admin-theme="dark"]) .booking-form-section {
  background:
    linear-gradient(180deg, rgba(15, 23, 42, 0.78) 0%, rgba(15, 23, 42, 0.62) 100%);
  border-color: rgba(30, 41, 59, 0.95);
  box-shadow: 0 8px 24px rgba(2, 6, 23, 0.18);
}

:global(html[data-admin-theme="dark"]) .booking-form-section-kicker {
  color: #93c5fd;
}

:global(html[data-admin-theme="dark"]) .entity-view-card {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .entity-view-item {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .entity-view-item.highlight {
  background: rgba(59, 130, 246, 0.14);
  border-color: rgba(59, 130, 246, 0.32);
}

:global(html[data-admin-theme="dark"]) .entity-view-card-title,
:global(html[data-admin-theme="dark"]) .entity-view-label {
  color: rgba(226, 232, 240, 0.72);
}

:global(html[data-admin-theme="dark"]) .entity-view-value {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .booking-form-section-kicker {
  color: #93c5fd;
}

:global(html[data-admin-theme="dark"]) .booking-form-section-head p {
  color: rgba(226, 232, 240, 0.72);
}

:global(html[data-admin-theme="dark"]) .addon-item,
:global(html[data-admin-theme="dark"]) .pricing-discount-panel,
:global(html[data-admin-theme="dark"]) .pdp-control-card {
  background: #111c34;
  border-color: #334155;
}
:global(html[data-admin-theme="dark"]) .room-service-group {
  background: linear-gradient(180deg, #111c34 0%, #0f172a 100%);
  border-color: #334155;
}
:global(html[data-admin-theme="dark"]) .room-service-group-head strong,
:global(html[data-admin-theme="dark"]) .room-service-card-top strong,
:global(html[data-admin-theme="dark"]) .room-subservice-top strong,
:global(html[data-admin-theme="dark"]) .room-service-qty {
  color: #f8fafc;
}
:global(html[data-admin-theme="dark"]) .room-service-group-head small,
:global(html[data-admin-theme="dark"]) .room-service-group-count,
:global(html[data-admin-theme="dark"]) .room-service-card-bottom small {
  color: #cbd5e1;
}
:global(html[data-admin-theme="dark"]) .room-service-card,
:global(html[data-admin-theme="dark"]) .room-subservice-card {
  background: #0f172a;
  border-color: #334155;
}
:global(html[data-admin-theme="dark"]) .room-service-card-top span,
:global(html[data-admin-theme="dark"]) .room-subservice-top span {
  color: #cbd5e1;
}
:global(html[data-admin-theme="dark"]) .room-service-step-btn {
  background: #1e293b;
  border-color: #475569;
  color: #cbd5e1;
}
:global(html[data-admin-theme="dark"]) .addon-toggle-copy strong,
:global(html[data-admin-theme="dark"]) .addon-price,
:global(html[data-admin-theme="dark"]) .pdp-title,
:global(html[data-admin-theme="dark"]) .pdp-label {
  color: #f8fafc;
}
:global(html[data-admin-theme="dark"]) .addon-stepper,
:global(html[data-admin-theme="dark"]) .addon-step-btn,
:global(html[data-admin-theme="dark"]) .pdp-input {
  background: #0f172a;
  border-color: #475569;
  color: #f8fafc;
}
:global(html[data-admin-theme="dark"]) .pdp-header { border-bottom-color: #334155; }
:global(html[data-admin-theme="dark"]) .room-selection-head small,
:global(html[data-admin-theme="dark"]) .room-option-main span,
:global(html[data-admin-theme="dark"]) .room-option-main small {
  color: #cbd5e1;
}
:global(html[data-admin-theme="dark"]) .room-option-card {
  border-color: #334155;
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  box-shadow: none;
}
:global(html[data-admin-theme="dark"]) .room-option-card.selected {
  border-color: rgba(96, 165, 250, 0.68);
  background: linear-gradient(180deg, #1e3a5f 0%, #172554 100%);
}
:global(html[data-admin-theme="dark"]) .room-option-card.unavailable {
  background: linear-gradient(180deg, #172033 0%, #0f172a 100%);
}
:global(html[data-admin-theme="dark"]) .room-option-check {
  border-color: #475569;
  background: #1e293b;
  color: #cbd5e1;
}
:global(html[data-admin-theme="dark"]) .room-option-main strong,
:global(html[data-admin-theme="dark"]) .room-option-price {
  color: #f8fafc;
}
:global(html[data-admin-theme="dark"]) .room-option-type {
  background: rgba(148, 163, 184, 0.16);
  color: #e2e8f0;
}
:global(html[data-admin-theme="dark"]) .room-option-status.status-available { background: rgba(34, 197, 94, 0.18); color: #86efac; }
:global(html[data-admin-theme="dark"]) .room-option-status.status-reserved { background: rgba(148, 163, 184, 0.18); color: #cbd5e1; }
:global(html[data-admin-theme="dark"]) .room-option-status.status-occupied,
:global(html[data-admin-theme="dark"]) .room-option-status.status-maintenance { background: rgba(127, 29, 29, 0.3); color: #fecaca; }
:global(html[data-admin-theme="dark"]) .room-option-booked-dates { background: rgba(127, 29, 29, 0.22); border-color: rgba(248, 113, 113, 0.32); color: #fecaca !important; }

/* Responsive */
@media (max-width: 992px) {
  .entity-view-grid {
    grid-template-columns: 1fr;
  }
  .booking-form-section {
    padding: 1rem;
    border-radius: 18px;
  }
  .booking-form-hero {
    padding: 1rem;
    border-radius: 20px;
  }
}

@media (max-width: 640px) {
  .entity-view-hero { flex-direction: column; align-items: flex-start; }
  .entity-view-badges { align-items: flex-start; flex-direction: row; flex-wrap: wrap; }
  .entity-view-grid { grid-template-columns: 1fr; }
  .entity-view-item { flex-direction: column; }
  .entity-view-value { text-align: left; }
  .booking-form-hero-meta { justify-content: flex-start; }
  .booking-form-section-head {
    flex-direction: column;
  }
  .form-grid { grid-template-columns: 1fr; }
  .pdp-header,
  .addon-line,
  .addon-sub-row { align-items: flex-start; flex-direction: column; }
  .pdp-body-grid { grid-template-columns: 1fr; }
  .addon-side { width: 100%; justify-items: start; }
  .addon-sub-block { padding: 10px; }
  .room-option-card { grid-template-columns: auto minmax(0, 1fr); min-height: unset; }
  .room-option-top { flex-direction: column; }
}
</style>
