<template>
  <div class="tva-page">
    <div class="page-header">
      <div>
        <h1>Déclaration TCSTH</h1>
        <p>Taxe de Consommation sur les Services et Tarifs d'Hébergement (5%) — s'applique UNIQUEMENT sur les nuitées (hébergement). Vue mensuelle et par période personnalisée.</p>
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
      </div>
    </div>

    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input
            v-model="search"
            type="text"
            class="search-input-clean"
            placeholder="Rechercher par réservation, client, chambre..."
          />
        </div>
        <button class="btn btn-sm" @click="resetFilters">
          <i class="fas fa-redo"></i> Réinitialiser
        </button>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>

      <div v-show="!isMobile || filtersOpen" class="filters-panel">
        <select v-model="viewMode" class="filter-select-clean">
          <option value="monthly">Vue mensuelle</option>
          <option value="bookings">Vue détaillée (réservations)</option>
        </select>
        <select v-model="preset" class="filter-select-clean">
          <option value="7d">7 derniers jours</option>
          <option value="28d">28 derniers jours</option>
          <option value="90d">90 derniers jours</option>
          <option value="this_month">Ce mois</option>
          <option value="last_month">Mois dernier</option>
          <option value="year">Cette année</option>
          <option value="all">Toutes les dates</option>
          <option value="custom">Personnalisé</option>
        </select>
        <input v-if="preset === 'custom'" v-model="customStart" type="date" class="filter-input-clean" />
        <input v-if="preset === 'custom'" v-model="customEnd" type="date" class="filter-input-clean" />
        <div class="current-balance-chip">
          <span>TCSTH à verser</span>
          <strong style="color:#92400e;">{{ formatMoney(periodTVADue) }}</strong>
        </div>
      </div>

      <div class="filter-range-note">
        {{ activeRangeNotice }}
      </div>
    </div>

    <div ref="exportRef" class="export-scope">
      <!-- Stats cards -->
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon tcsth"><i class="fas fa-file-invoice-dollar"></i></div>
          <div class="stat-info">
            <span class="label">TCSTH collectée (période)</span>
            <span class="value warning">{{ formatMoney(periodTVADue) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon success"><i class="fas fa-circle-check"></i></div>
          <div class="stat-info">
            <span class="label">TCSTH payée à l'OBR</span>
            <span class="value success">{{ formatMoney(periodTcsthPaid) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon warning"><i class="fas fa-clock"></i></div>
          <div class="stat-info">
            <span class="label">TCSTH en attente</span>
            <span class="value warning">{{ formatMoney(periodTcsthPending) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon primary"><i class="fas fa-door-closed"></i></div>
          <div class="stat-info">
            <span class="label">Chiffre HT (hôtel)</span>
            <span class="value primary">{{ formatMoney(periodHT) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon info"><i class="fas fa-money-bill-wave"></i></div>
          <div class="stat-info">
            <span class="label">Chiffre TTC (hôtel)</span>
            <span class="value info">{{ formatMoney(periodTTC) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon primary"><i class="fas fa-calendar-check"></i></div>
          <div class="stat-info">
            <span class="label">Réservations concernées</span>
            <span class="value primary">{{ periodBookingsCount }}</span>
          </div>
        </div>
      </div>

      <!-- Monthly view -->
      <section v-if="viewMode === 'monthly'" class="card">
        <div class="card-header">
          <div class="card-title">
            <i class="fas fa-calendar-alt"></i>
            <h2>TCSTH par mois</h2>
          </div>
          <div class="card-subtitle">Sur {{ monthlyData.length }} mois dans la période sélectionnée</div>
        </div>

        <div v-if="loading" class="table-skeleton ledger-skeleton">
          <div v-for="n in 6" :key="n" class="skeleton-row"><span /><span /><span /><span /><span /></div>
        </div>
        <div v-else-if="!monthlyData.length" class="empty-state">
          <i class="fas fa-file-invoice-dollar"></i>
          <p>Aucune réservation d'hôtel (TCSTH concernée) pour cette période.</p>
        </div>

        <div v-else class="table-wrap">
          <table class="admin-table ledger-table tcsth-monthly-table">
            <thead>
              <tr>
                <th>Période</th>
                <th style="text-align:right;">Réservations</th>
                <th style="text-align:right;">Chiffre HT</th>
                <th style="text-align:right;">Chiffre TTC</th>
                <th style="text-align:right;color:#92400e;">TCSTH collectée</th>
                <th style="text-align:center;">Statut</th>
                <th style="text-align:center;">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in monthlyData" :key="row.key" :class="{ 'row-paid': isMonthPaid(row.key) }">
                <td>
                  <div class="ledger-entry-ledger">
                    <i class="fas fa-calendar-month"></i>
                    <span>
                      <strong>{{ row.label }}</strong>
                      <small v-if="isMonthPaid(row.key)">Payé le {{ formatDate(getMonthPaidAt(row.key)) }}</small>
                    </span>
                  </div>
                </td>
                <td style="text-align:right;">{{ row.count }}</td>
                <td style="text-align:right;">{{ formatMoney(row.ht) }}</td>
                <td style="text-align:right;">{{ formatMoney(row.ttc) }}</td>
                <td style="text-align:right;color:#92400e;font-weight:700;">{{ formatMoney(row.tva) }}</td>
                <td style="text-align:center;">
                  <span v-if="isMonthPaid(row.key)" class="badge badge--success">
                    <i class="fas fa-circle-check"></i> Payé
                  </span>
                  <span v-else class="badge badge--warning">
                    <i class="fas fa-clock"></i> En attente
                  </span>
                </td>
                <td style="text-align:center;">
                  <div class="row-actions">
                    <button
                      v-if="!isMonthPaid(row.key)"
                      class="btn btn-sm btn-paid-month"
                      :disabled="markingMonth === row.key"
                      :class="{ 'is-loading': markingMonth === row.key }"
                      @click="markMonthPaid(row.key, row.tva)"
                      title="Marquer ce mois comme payé à l'OBR"
                    >
                      <i class="fas fa-check"></i>
                      <span class="btn-label">Marquer payé</span>
                    </button>
                    <button
                      v-else
                      class="btn btn-sm btn-unpay-month"
                      :disabled="markingMonth === row.key"
                      :class="{ 'is-loading': markingMonth === row.key }"
                      @click="unmarkMonthPaid(row.key)"
                      title="Annuler le paiement (si erreur)"
                    >
                      <i class="fas fa-rotate-left"></i>
                      <span class="btn-label">Rétablir</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <th><strong>TOTAL période</strong></th>
                <th style="text-align:right;"><strong>{{ periodBookingsCount }}</strong></th>
                <th style="text-align:right;"><strong>{{ formatMoney(periodHT) }}</strong></th>
                <th style="text-align:right;"><strong>{{ formatMoney(periodTTC) }}</strong></th>
                <th style="text-align:right;color:#92400e;"><strong>{{ formatMoney(periodTVADue) }}</strong></th>
                <th colspan="2">
                  <div class="footer-summary">
                    <span class="summary-chip chip-paid">
                      <i class="fas fa-circle-check"></i> Payé : {{ formatMoney(periodTcsthPaid) }}
                    </span>
                    <span class="summary-chip chip-warn">
                      <i class="fas fa-clock"></i> En attente : {{ formatMoney(periodTcsthPending) }}
                    </span>
                  </div>
                </th>
              </tr>
            </tfoot>
          </table>
        </div>
      </section>

      <!-- Detailed (bookings) view -->
      <section v-else class="card">
        <div class="card-header">
          <div class="card-title">
            <i class="fas fa-list"></i>
            <h2>Détail des réservations hôtel soumises à TCSTH</h2>
          </div>
          <div class="card-subtitle">{{ filteredBookings.length }} ligne(s) — période sélectionnée</div>
        </div>

        <div v-if="loading" class="table-skeleton ledger-skeleton">
          <div v-for="n in 8" :key="n" class="skeleton-row"><span /><span /><span /><span /><span /><span /></div>
        </div>
        <div v-else-if="!filteredBookings.length" class="empty-state">
          <i class="fas fa-calendar-days"></i>
          <p>Aucune réservation d'hôtel dans cette période.</p>
        </div>

        <div v-else class="table-wrap">
          <table class="admin-table ledger-table">
            <thead>
              <tr>
                <th>Date réservation</th>
                <th>Réservation</th>
                <th>Client</th>
                <th>Période séjour</th>
                <th style="text-align:right;">Chiffre HT</th>
                <th style="text-align:right;color:#92400e;">TCSTH (5% hébergement)</th>
                <th style="text-align:right;">Total TTC</th>
                <th>Statut</th>
                <th style="width:120px; text-align:center;">Facture</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in filteredBookings" :key="b.id">
                <td>{{ formatDate(b.created_at || b.start_date) }}</td>
                <td>
                  <div class="ledger-entry-ledger">
                    <i class="fas fa-door-closed"></i>
                    <span>
                      <strong>{{ b.code || ('#' + b.id) }}</strong>
                      <small v-if="b.room_display_summary">{{ b.room_display_summary }}</small>
                    </span>
                  </div>
                </td>
                <td>{{ b.customer_name || (b.customer ? (b.customer.full_name || b.customer.name) : '-') }}</td>
                <td>
                  <small>{{ formatDate(b.start_date) }} → {{ formatDate(b.end_date) }}</small>
                </td>
                <td style="text-align:right;">{{ formatMoney(bookingHT(b)) }}</td>
                <td style="text-align:right;color:#92400e;font-weight:600;">{{ formatMoney(bookingTVA(b)) }}</td>
                <td style="text-align:right;">{{ formatMoney(b.total_price) }}</td>
                <td>
                  <span class="badge" :class="badgeStatusClass(b.status)">
                    <i :class="badgeStatusIcon(b.status)"></i> {{ statusLabel(b.status) }}
                  </span>
                </td>
                <td style="text-align:center;">
                  <div class="facture-actions">
                    <button
                      class="btn btn-sm btn-export inv-btn inv-btn-download"
                      type="button"
                      :title="`Télécharger la facture ${b.code || '#' + b.id}`"
                      @click="downloadBookingInvoice(b)"
                    >
                      <i class="fas fa-file-arrow-down"></i>
                      <span class="btn-label">PDF</span>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <th colspan="4"><strong>TOTAL période</strong></th>
                <th style="text-align:right;"><strong>{{ formatMoney(periodHT) }}</strong></th>
                <th style="text-align:right;color:#92400e;"><strong>{{ formatMoney(periodTVADue) }}</strong></th>
                <th style="text-align:right;"><strong>{{ formatMoney(periodTTC) }}</strong></th>
                <th></th>
                <th></th>
              </tr>
            </tfoot>
          </table>
        </div>
      </section>

      <!-- Modal confirmation paiement mois -->
      <Teleport to="body">
        <div v-if="showPayConfirmModal" class="modal-overlay" @click.self="closePayModal">
          <div class="modal-card modal-card-sm">
            <div class="modal-header">
              <h3>Marquer TCSTH comme payé</h3>
              <button class="modal-close" @click="closePayModal"><i class="fas fa-xmark"></i></button>
            </div>
            <div class="modal-body">
              <p style="margin: 0 0 1rem; color: #475569;">
                Déclaration TCSTH pour le mois <strong>{{ payMonthLabel }}</strong>.
              </p>
              <div class="modal-total-box">
                <span class="mtl-label">Montant TCSTH à verser</span>
                <strong class="mtl-value">{{ formatMoney(payMonthAmount) }}</strong>
              </div>
              <div class="form-group">
                <label class="form-label">Date de paiement</label>
                <input v-model="payFormDate" type="date" class="filter-input-clean" style="width: 100%;" />
              </div>
              <div class="form-group">
                <label class="form-label">Référence OBR (numéro de quittance / bordereau — optionnel)</label>
                <input v-model="payFormRef" type="text" class="search-input-clean" placeholder="Ex: QUITT-2026-08-00123" />
              </div>
              <div class="form-group">
                <label class="form-label">Note (optionnel)</label>
                <textarea v-model="payFormNote" rows="2" class="search-input-clean" placeholder="Mode de paiement, observations..." style="resize: vertical; width:100%;"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button class="btn btn-grey" @click="closePayModal">Annuler</button>
              <button class="btn btn-primary" :disabled="!payFormDate" @click="confirmMarkPaid">
                <i class="fas fa-check"></i> Confirmer paiement
              </button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue'
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { useDateFormat } from '~/composables/useDateFormat'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { notify } from '~/composables/useNotification'

const { formatMoney } = useMoney()
const { formatDisplayDate: formatDate, formatDateRange } = useDateFormat()
const { escapeHtml, documentBranding } = useDocumentBranding()
const {
  exportPdf, exportXls, exportingPdf, exportingXls, canExportExcel, exportRef,
  downloadPdfHtml, buildPdfDocumentHtml, buildExportFileName,
} = useAdminExportDocuments({
  title: 'Déclaration TCSTH',
  scope: 'tcsth'
})

definePageMeta({ layout: 'admin' })

const TVA_RATE_PCT = 5
const TVA_DIVISOR = 1 + (TVA_RATE_PCT / 100)
const LS_KEY = 'hall_ui_tcsth_status_v1'
const _roundMoney = (n) => Math.round((Number(n || 0) + Number.EPSILON) * 100) / 100

// ========= TCSTH payment status helpers (localStorage) =========
const _tcsthRefreshTick = ref(0)
const _readAllStatus = () => {
  if (!process.client) return {}
  try {
    const raw = localStorage.getItem(LS_KEY) || '{}'
    return JSON.parse(raw) || {}
  } catch { return {} }
}
const _writeAllStatus = (obj) => {
  if (!process.client) return
  try { localStorage.setItem(LS_KEY, JSON.stringify(obj || {})) } catch {}
  _tcsthRefreshTick.value += 1
}
const isMonthPaid = (key) => {
  void _tcsthRefreshTick.value
  const all = _readAllStatus()
  return Boolean(all[key]?.paid)
}
const getMonthPaidAt = (key) => {
  void _tcsthRefreshTick.value
  const all = _readAllStatus()
  return all[key]?.paidAt || null
}
const getMonthPaidRef = (key) => {
  void _tcsthRefreshTick.value
  const all = _readAllStatus()
  return all[key]?.reference || ''
}

// ========= Invoice / Facture download helpers =========
const getBookingDisplayId = (b) => String(b?.code || '').trim() || `RES-${String(b?.id || '').padStart(6, '0')}`
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
const buildBookingInvoiceHtml = (b) => {
  const bookingCode = getBookingDisplayId(b)
  const periodLabel = formatDateRange(b?.start_date, b?.end_date)
  const bht = _roundMoney(bookingHT(b))
  const btva = _roundMoney(bookingTVA(b))
  const totalTTC = Number(b?.total_price || 0)
  const businessTaxId = String(documentBranding?.taxId || '').trim() || '4003469600'
  const businessRcNumber = String(documentBranding?.rcNumber || '').trim() || '0084351/26'
  const customerName = b?.customer_name || (b?.customer && (b.customer.full_name || b.customer.name)) || 'Client'
  const customerEmail = b?.customer_email || (b?.customer && (b.customer.email || b.customer.contact_email)) || '-'
  const guestName = b?.guest_full_name || customerName
  const roomsCount = Number(b?.room_count || 0)
  const roomsLabel = (b?.room_display || b?.room_display_summary ||
    (roomsCount > 1 ? `${roomsCount} chambres` : 'Chambre') || 'Chambre')
  const nightsCount = (() => {
    try {
      const s = new Date(b?.start_date); const e = new Date(b?.end_date)
      if (isNaN(s) || isNaN(e)) return '-'
      const ms = Math.max(0, e.getTime() - s.getTime())
      const n = Math.max(1, Math.round(ms / (24 * 3600 * 1000)))
      return `${n} nuit${n > 1 ? 's' : ''}`
    } catch { return '-' }
  })()
  const documentRef = bookingCode

  const etablissementRows = [
    ['Établissement', String(documentBranding?.name || 'La Bertha')],
    ['NIF', businessTaxId],
    ['RC N°', businessRcNumber],
    ['Adresse', String(documentBranding?.address || '-')],
  ]
  const clientRows = [
    ['Client', customerName],
    ['Hébergé', guestName],
    ['Email', customerEmail],
  ]
  const sejourRows = [
    ['Type', 'Hébergement'],
    ['Chambre(s)', String(roomsLabel)],
    ['Période', periodLabel || '-'],
    ['Durée', nightsCount],
    ['Nuit du', formatDate(b?.start_date)],
    ['Au', formatDate(b?.end_date)],
  ]
  const facturationRows = [
    ['N° Facture / Réservation', documentRef],
    ['Date document', formatDate(b?.created_at || b?.start_date || new Date())],
  ]

  const detailLines = [
    { label: 'Hébergement (Nuits)', qty: 1, unit: bht, total: bht },
  ]

  return buildPdfDocumentHtml({
    title: 'Facture d\'entrée',
    documentTitle: `Facture ${bookingCode}`,
    subtitle: 'Facture de sejour client en etablissement hotelier.',
    typeLabel: 'Facture',
    headerEyebrow: 'Facture de séjour',
    headerReference: documentRef,
    periodLabel,
    showMeta: false,
    contentHtml: `
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 10px;">
        <div class="section-card" style="margin:0;">
          <div class="section-header"><h2>Établissement</h2></div>
          <table>
            <tbody>
              ${etablissementRows.map(([k, v]) => `
                <tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        <div class="section-card" style="margin:0;">
          <div class="section-header"><h2>Client</h2></div>
          <table>
            <tbody>
              ${clientRows.map(([k, v]) => `
                <tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px;">
        <div class="section-card" style="margin:0;">
          <div class="section-header"><h2>Séjour</h2></div>
          <table>
            <tbody>
              ${sejourRows.map(([k, v]) => `
                <tr><td>${escapeHtml(k)}</td><td>${escapeHtml(String(v))}</td></tr>
              `).join('')}
            </tbody>
          </table>
        </div>
        <div class="section-card" style="margin:0;">
          <div class="section-header"><h2>Facturation</h2></div>
          <table>
            <tbody>
              ${facturationRows.map(([k, v]) => `
                <tr><td>${escapeHtml(k)}</td><td>${escapeHtml(String(v))}</td></tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <div class="section-card">
        <div class="section-header"><h2>Détail de la facture</h2></div>
        <table>
          <thead>
            <tr>
              <th style="text-align:left;">Désignation</th>
              <th style="text-align:right;">Qté</th>
              <th style="text-align:right;">Prix unit. HT</th>
              <th style="text-align:right;">Total HT</th>
            </tr>
          </thead>
          <tbody>
            ${detailLines.map(line => `
              <tr>
                <td style="text-align:left;">${escapeHtml(line.label)}</td>
                <td style="text-align:right;">${line.qty}</td>
                <td style="text-align:right;">${escapeHtml(formatMoney(line.unit))}</td>
                <td style="text-align:right;">${escapeHtml(formatMoney(line.total))}</td>
              </tr>
            `).join('')}
            <tr>
              <td colspan="3" style="text-align:right; font-weight:700;">Sous-total HT</td>
              <td style="text-align:right; font-weight:700;">${escapeHtml(formatMoney(bht))}</td>
            </tr>
            <tr>
              <td colspan="3" style="text-align:right;">TCSTH (${TVA_RATE_PCT}%)</td>
              <td style="text-align:right;">${escapeHtml(formatMoney(btva))}</td>
            </tr>
            <tr>
              <td colspan="3" style="text-align:right; font-weight:700; font-size:1.05em;">Total TTC</td>
              <td style="text-align:right; font-weight:700; font-size:1.05em;">${escapeHtml(formatMoney(totalTTC))}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section-card" style="margin-top: 12px;">
        <div class="section-header"><h2>Conditions</h2></div>
        <p style="margin: 6px 0; color:#334155; font-size: 0.92rem; line-height:1.5;">
          Merci d'avoir choisi notre établissement. Les prestations d'hébergement sont soumises au TCSTH au taux de ${TVA_RATE_PCT}% conformément à la législation en vigueur. Cette facture est générée automatiquement et reste valable sans signature manuscrite.
        </p>
      </div>
    `,
  })
}

const downloadBookingInvoice = async (b) => {
  if (!b || !process.client) return
  try {
    const html = buildBookingInvoiceHtml(b)
    const ok = await downloadPdfHtml({
      html,
      fileName: buildPdfFileName('facture-entree', getBookingDisplayId(b)),
    })
    if (!ok) {
      notify('Impossible de télécharger la facture PDF', 'warning')
    }
  } catch (e) {
    console.error(e)
    notify('Erreur génération facture', 'warning')
  }
}

const markingMonth = ref(null)
const showPayConfirmModal = ref(false)
const payMonthKey = ref(null)
const payMonthLabel = ref('')
const payMonthAmount = ref(0)
const payFormDate = ref('')
const payFormRef = ref('')
const payFormNote = ref('')

const markMonthPaid = (key, amount) => {
  const row = monthlyData.value.find(r => r.key === key)
  payMonthKey.value = key
  payMonthLabel.value = row ? row.label : key
  payMonthAmount.value = _roundMoney(amount || 0)
  payFormDate.value = new Date().toISOString().slice(0, 10)
  payFormRef.value = ''
  payFormNote.value = ''
  showPayConfirmModal.value = true
}
const closePayModal = () => {
  showPayConfirmModal.value = false
  payMonthKey.value = null
}
const confirmMarkPaid = () => {
  if (!payMonthKey.value || !payFormDate.value) return
  markingMonth.value = payMonthKey.value
  try {
    const all = _readAllStatus()
    all[payMonthKey.value] = {
      paid: true,
      paidAt: payFormDate.value,
      amount: Number(payMonthAmount.value || 0),
      reference: String(payFormRef.value || '').trim(),
      note: String(payFormNote.value || '').trim(),
      savedAt: new Date().toISOString()
    }
    _writeAllStatus(all)
  } finally {
    markingMonth.value = null
    closePayModal()
  }
}
const unmarkMonthPaid = (key) => {
  if (!key) return
  markingMonth.value = key
  try {
    const all = _readAllStatus()
    delete all[key]
    _writeAllStatus(all)
  } finally {
    markingMonth.value = null
  }
}
const extractHT = (ttc) => {
  const value = Number(ttc || 0)
  return value > 0 ? _roundMoney(value / TVA_DIVISOR) : 0
}
const extractTVA = (ttc) => {
  const value = Number(ttc || 0)
  return value > 0 ? _roundMoney(value - extractHT(value)) : 0
}
const bookingHT = (b) => Number(b?.subtotal_ht ?? extractHT(b?.total_price))
const bookingTVA = (b) => Number(b?.tva_amount ?? extractTVA(b?.total_price))

const search = ref('')
const viewMode = ref('monthly')
const preset = ref('this_month')
const customStart = ref('')
const customEnd = ref('')
const filtersOpen = ref(false)
const loading = ref(true)

const isMobile = ref(false)
const bookings = ref([])
const payments = ref([])
const fetchError = ref('')

const handleResize = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
  const today = new Date()
  customEnd.value = today.toISOString().slice(0, 10)
  const d = new Date(today.getFullYear(), today.getMonth(), 1)
  customStart.value = d.toISOString().slice(0, 10)
  loadAll()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

watch([preset, customStart, customEnd], () => { /* filtered via computed */ })

const startOf = (d) => {
  const x = new Date(d); x.setHours(0, 0, 0, 0); return x
}
const endOf = (d) => {
  const x = new Date(d); x.setHours(23, 59, 59, 999); return x
}

const dateBounds = computed(() => {
  const now = new Date()
  const todayISO = now.toISOString().slice(0, 10)
  const today = new Date(todayISO + 'T00:00:00')
  switch (preset.value) {
    case '7d': {
      const start = new Date(today); start.setDate(start.getDate() - 6)
      return [start, today]
    }
    case '28d': {
      const start = new Date(today); start.setDate(start.getDate() - 27)
      return [start, today]
    }
    case '90d': {
      const start = new Date(today); start.setDate(start.getDate() - 89)
      return [start, today]
    }
    case 'this_month': {
      const start = new Date(today.getFullYear(), today.getMonth(), 1)
      const end = new Date(today.getFullYear(), today.getMonth() + 1, 0)
      return [start, end]
    }
    case 'last_month': {
      const start = new Date(today.getFullYear(), today.getMonth() - 1, 1)
      const end = new Date(today.getFullYear(), today.getMonth(), 0)
      return [start, end]
    }
    case 'year': {
      const start = new Date(today.getFullYear(), 0, 1)
      return [start, today]
    }
    case 'all':
      return [null, null]
    case 'custom': {
      const s = customStart.value ? new Date(customStart.value + 'T00:00:00') : null
      const e = customEnd.value ? new Date(customEnd.value + 'T23:59:59') : null
      return [s, e]
    }
    default:
      return [null, null]
  }
})

const activeRangeNotice = computed(() => {
  const [s, e] = dateBounds.value
  if (!s && !e) return 'Toutes les dates sont incluses.'
  if (s && e) return `Période sélectionnée : du ${formatDate(s)} au ${formatDate(e)}.`
  return 'Période incomplète.'
})

const inPeriod = (d) => {
  const [s, e] = dateBounds.value
  const ts = new Date(d).getTime()
  if (isNaN(ts)) return false
  if (s && ts < startOf(s).getTime()) return false
  if (e && ts > endOf(e).getTime()) return false
  return true
}

// Filter to ROOM type bookings (hotel only)
const periodBookings = computed(() => {
  return bookings.value.filter(b => {
    const type = String(b?.booking_type || '').toLowerCase()
    if (type !== 'room') return false
    const refDate = b?.created_at || b?.start_date
    return inPeriod(refDate)
  })
})

const filteredBookings = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return periodBookings.value
  return periodBookings.value.filter(b => {
    const id = (b.code || '#' + (b.id || '')).toLowerCase()
    const client = ((b.customer_name || '') + ' ' + (b.customer && b.customer.full_name ? b.customer.full_name : '')).toLowerCase()
    const room = (b.room_display_summary || '').toLowerCase()
    return id.includes(q) || client.includes(q) || room.includes(q)
  })
})

const monthlyData = computed(() => {
  const map = {}
  const months = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
  for (const b of filteredBookings.value) {
    const ref = new Date(b.created_at || b.start_date)
    const Y = ref.getFullYear()
    const M = ref.getMonth()
    const key = `${Y}-${String(M+1).padStart(2,'0')}`
    if (!map[key]) map[key] = { key, label: `${months[M]} ${Y}`, year: Y, month: M, count: 0, ht: 0, ttc: 0, tva: 0 }
    map[key].count += 1
    map[key].ht += bookingHT(b)
    map[key].ttc += Number(b.total_price || 0)
    map[key].tva += bookingTVA(b)
  }
  return Object.values(map).map(r => ({
    ...r,
    ht: _roundMoney(r.ht),
    ttc: _roundMoney(r.ttc),
    tva: _roundMoney(r.tva)
  })).sort((a, b) => (a.year - b.year) || (a.month - b.month))
})

const periodHT = computed(() => _roundMoney(filteredBookings.value.reduce((s, b) => s + bookingHT(b), 0)))
const periodTTC = computed(() => _roundMoney(filteredBookings.value.reduce((s, b) => s + Number(b.total_price || 0), 0)))
const periodTVADue = computed(() => _roundMoney(filteredBookings.value.reduce((s, b) => s + bookingTVA(b), 0)))
const periodBookingsCount = computed(() => filteredBookings.value.length)

const periodTcsthPaid = computed(() => {
  void _tcsthRefreshTick.value
  const rows = monthlyData.value || []
  const all = _readAllStatus()
  return _roundMoney(
    rows
      .filter(r => Boolean(all[r.key]?.paid))
      .reduce((s, r) => s + Number(all[r.key]?.amount || r.tva || 0), 0)
  )
})
const periodTcsthPending = computed(() => {
  void _tcsthRefreshTick.value
  return _roundMoney(periodTVADue.value - periodTcsthPaid.value)
})

const badgeStatusClass = (status) => {
  switch (status) {
    case 'paid': return 'badge--success'
    case 'confirmed': return 'badge--primary'
    case 'pending': return 'badge--warning'
    case 'cancelled': return 'badge--danger'
    default: return 'badge--muted'
  }
}
const badgeStatusIcon = (status) => {
  switch (status) {
    case 'paid': return 'fas fa-check-circle'
    case 'confirmed': return 'fas fa-calendar-check'
    case 'pending': return 'fas fa-clock'
    case 'cancelled': return 'fas fa-xmark-circle'
    default: return 'fas fa-circle-question'
  }
}
const statusLabel = (status) => {
  switch (status) {
    case 'paid': return 'Payée'
    case 'confirmed': return 'Confirmée'
    case 'pending': return 'En attente'
    case 'cancelled': return 'Annulée'
    default: return status || '-'
  }
}

const resetFilters = () => {
  search.value = ''
  preset.value = 'this_month'
  const today = new Date()
  customEnd.value = today.toISOString().slice(0, 10)
  const d = new Date(today.getFullYear(), today.getMonth(), 1)
  customStart.value = d.toISOString().slice(0, 10)
}

const loadAll = async () => {
  loading.value = true
  fetchError.value = ''
  try {
    const [bRes, pRes] = await Promise.all([
      api.get('bookings/').catch(() => ({ data: [] })),
      api.get('payments/').catch(() => ({ data: [] }))
    ])
    bookings.value = Array.isArray(bRes?.data?.results ? bRes.data.results : (bRes?.data || [])) ? (bRes?.data?.results || bRes?.data || []) : []
    payments.value = Array.isArray(pRes?.data?.results ? pRes.data.results : (pRes?.data || [])) ? (pRes?.data?.results || pRes?.data || []) : []
  } catch (e) {
    fetchError.value = e.message || 'Erreur de chargement'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tva-page { padding: 0; display: flex; flex-direction: column; gap: 0; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-8); gap: var(--space-4); flex-wrap: wrap; }
.page-header h1 { font-size: 1.75rem; font-weight: 800; margin: 0; color: var(--gray-900); }
.page-header p { color: var(--gray-500); margin-top: .35rem; max-width: 720px; line-height: 1.45; }
.header-actions { display: inline-flex; gap: .5rem; flex-wrap: wrap; align-items: center; justify-content: flex-end; }

.controls { display: flex; gap: var(--space-4); margin-bottom: var(--space-8); padding: var(--space-4) var(--space-6); align-items: center; flex-wrap: wrap; background: var(--white); border: 1px solid var(--gray-200); border-radius: var(--rounded-lg); box-shadow: var(--shadow-sm); }
.controls-top { width: 100%; display: flex; gap: var(--space-3); align-items: center; }
.filters-panel { width: 100%; display: flex; gap: var(--space-4); flex-wrap: wrap; align-items: center; }
.filter-range-note { margin-top: 0.75rem; color: var(--gray-500); font-size: 0.85rem; font-weight: 700; }
.filters-toggle { display: none; width: 42px; height: 42px; border: 1px solid var(--gray-200); background: var(--gray-50); color: var(--gray-600); border-radius: var(--rounded-md); cursor: pointer; transition: var(--transition-fast); align-items: center; justify-content: center; }
.filters-toggle.active { background: var(--warning-bg); border-color: var(--warning); color: var(--gray-900); }
.filters-panel .filter-select-clean, .filters-panel .filter-input-clean { flex: 1 1 190px; }
.search-wrapper { flex: 1 1 320px; position: relative; }
.search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); color: var(--gray-400); font-size: 0.9rem; }
.search-input-clean { width: 100%; padding: 0.625rem 1rem 0.625rem 2.5rem; border: 1px solid var(--gray-200); border-radius: var(--rounded-md); font-size: 0.9rem; background: var(--gray-50); color: var(--gray-700); transition: var(--transition-fast); outline: none; }
.search-input-clean::placeholder { color: var(--gray-500); }
.search-input-clean:focus { background: var(--white); border-color: var(--accent); box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 10%, transparent); color: var(--gray-800); }
.filter-select-clean { padding: 0.625rem 2rem 0.625rem 1rem; border: 1px solid var(--gray-200); border-radius: var(--rounded-md); font-size: 0.9rem; background: var(--gray-50); color: var(--gray-600); font-weight: 600; cursor: pointer; outline: none; transition: var(--transition-fast); }
.filter-select-clean:focus { background: var(--white); border-color: var(--accent); box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 10%, transparent); color: var(--gray-800); }
.filter-input-clean { padding: 0.625rem 1rem; border: 1px solid var(--gray-200); border-radius: var(--rounded-md); font-size: 0.9rem; background: var(--gray-50); color: var(--gray-600); font-weight: 600; transition: var(--transition-fast); outline: none; }
.filter-input-clean:focus { background: var(--white); border-color: var(--accent); box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 10%, transparent); color: var(--gray-800); }
.current-balance-chip { margin-left: auto; display: inline-flex; align-items: center; gap: 10px; padding: .5rem .9rem; background: var(--warning-bg); border: 1px solid var(--warning); color: var(--warning); border-radius: 999px; font-size: .82rem; font-weight: 700; }

.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: var(--space-5); margin-bottom: var(--space-8); }
.stat-card { display: flex; align-items: center; gap: var(--space-4); padding: var(--space-5); background: var(--white); border: 1px solid var(--gray-200); border-radius: var(--rounded-lg); box-shadow: var(--shadow-sm); }
.stat-icon { width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.05rem; }
.stat-icon.success { background: var(--success-bg); color: var(--success); }
.stat-icon.warning { background: var(--warning-bg); color: var(--warning); }
.stat-icon.info { background: var(--info-bg); color: var(--info); }
.stat-icon.primary { background: var(--info-bg); color: var(--primary); }
.stat-icon.tcsth { background: var(--warning-bg); color: var(--warning); }
.label { display: block; color: var(--gray-400); font-size: .72rem; text-transform: uppercase; font-weight: 700; letter-spacing: .05em; }
.value { font-size: 1.2rem; font-weight: 800; color: var(--gray-900); }
.value.success { color: var(--success); }
.value.warning { color: var(--warning); }
.value.info { color: var(--info); }
.value.primary { color: var(--primary); }

.card { background: var(--white); border: 1px solid var(--gray-200); border-radius: var(--rounded-lg); box-shadow: var(--shadow-sm); margin-bottom: var(--space-8); }
.card:last-child { margin-bottom: 0; }
.card-header { padding: var(--space-5) var(--space-6); border-bottom: 1px solid var(--gray-100); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
.card-title { display: flex; align-items: center; gap: 10px; }
.card-title i { width: 36px; height: 36px; display: inline-flex; align-items: center; justify-content: center; background: var(--warning-bg); color: var(--warning); border-radius: 10px; font-size: 14px; }
.card-title h2 { margin: 0; font-size: 1.05rem; font-weight: 800; color: var(--gray-800); }
.card-subtitle { color: var(--gray-500); font-size: .85rem; }

.table-wrap { overflow-x: auto; }
.admin-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.admin-table thead th {
  text-align: left; padding: .9rem 1.25rem;
  background: var(--gray-50); border-bottom: 1px solid var(--gray-200);
  color: var(--gray-600); font-weight: 700; font-size: .72rem;
  text-transform: uppercase; letter-spacing: 0.05em;
  white-space: nowrap;
}
.admin-table tbody td { padding: .95rem 1.25rem; border-bottom: 1px solid var(--gray-100); color: var(--gray-900); vertical-align: middle; }
.admin-table tbody tr:hover { background: var(--gray-50); }
.admin-table tfoot th {
  padding: 1rem 1.25rem; background: var(--gray-50);
  border-top: 2px solid var(--gray-200); font-size: .9rem;
}

.ledger-entry-ledger { display: flex; align-items: center; gap: 10px; }
.ledger-entry-ledger i {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  background: var(--info-bg); color: var(--info); font-size: 13px; flex-shrink: 0;
}
.ledger-entry-ledger span { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ledger-entry-ledger small { color: var(--gray-500); font-size: .8rem; }

.badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: .35rem .75rem; border-radius: var(--rounded-full);
  font-size: .75rem; font-weight: 700;
  border: 1px solid transparent; white-space: nowrap;
}
.badge--success { background: var(--success-bg); color: var(--success); border-color: color-mix(in srgb, var(--success) 28%, transparent); }
.badge--warning { background: var(--warning-bg); color: var(--warning); border-color: color-mix(in srgb, var(--warning) 28%, transparent); }
.badge--primary { background: var(--info-bg); color: var(--info); border-color: color-mix(in srgb, var(--info) 28%, transparent); }
.badge--danger { background: var(--danger-bg); color: var(--danger); border-color: color-mix(in srgb, var(--danger) 28%, transparent); }
.badge--muted { background: var(--gray-50); color: var(--gray-600); border-color: var(--gray-200); }

.table-skeleton { display: flex; flex-direction: column; gap: 10px; padding: var(--space-6); }
.table-skeleton .skeleton-row {
  display: grid; grid-template-columns: 1.2fr 2fr 1.5fr 1.5fr 1.2fr 1.2fr;
  gap: 12px;
}
.table-skeleton.ledger-skeleton .skeleton-row { grid-template-columns: repeat(4, 1fr); }
.table-skeleton .skeleton-row span {
  height: 34px;
  background: linear-gradient(90deg, var(--gray-100) 25%, var(--gray-200) 50%, var(--gray-100) 75%);
  background-size: 200% 100%;
  border-radius: var(--rounded-md);
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

.empty-state { padding: 4rem 1rem; text-align: center; color: var(--gray-500); }
.empty-state i { font-size: 48px; color: var(--gray-300); margin-bottom: 1rem; display: block; }
.empty-state p { margin: 0; font-size: .9rem; font-weight: 600; }

.btn-sm { padding: .45rem .75rem; font-size: .78rem; }
.btn-icon { width: 32px; height: 32px; background: var(--gray-50); color: var(--gray-500); border-radius: var(--rounded-md); border: 1px solid var(--gray-200); cursor: pointer; }

/* ========== ROW PAID STATUS, ACTIONS, FOOTER SUMMARY ========== */
.tcsth-monthly-table tbody tr.row-paid {
  background: var(--success-bg);
}
.tcsth-monthly-table tbody tr.row-paid:hover {
  background: color-mix(in srgb, var(--success-bg) 85%, var(--success) 8%);
}
.tcsth-monthly-table .row-paid td:nth-child(5) { color: var(--success) !important; font-weight: 700; }

.row-actions { display: inline-flex; gap: .5rem; justify-content: center; }
.row-actions .btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .4rem;
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 700;
  border-radius: var(--rounded-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: var(--transition-all);
  line-height: 1.2;
  white-space: nowrap;
  letter-spacing: .01em;
  min-height: 38px;
}
.row-actions .btn.is-loading { opacity: .7; cursor: wait; }
.row-actions .btn:disabled { opacity: .55; cursor: not-allowed; }

.row-actions .btn-paid-month {
  background-color: var(--success);
  color: var(--white);
  box-shadow: 0 4px 14px 0 color-mix(in srgb, var(--success) 28%, transparent);
}
.row-actions .btn-paid-month:hover:not(:disabled) {
  filter: brightness(1.05);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 color-mix(in srgb, var(--success) 32%, transparent);
}

.row-actions .btn-unpay-month {
  background: var(--white);
  color: var(--warning);
  border: 1px solid var(--gray-200);
}
.row-actions .btn-unpay-month:hover:not(:disabled) {
  background: var(--warning-bg);
  border-color: var(--warning);
  transform: translateY(-1px);
  color: var(--warning);
}
@media (max-width: 768px) {
  .row-actions { gap: .35rem; }
  .row-actions .btn .btn-label { display: none; }
  .row-actions .btn {
    padding: 0;
    width: 38px;
    min-width: 38px;
    min-height: 38px;
    gap: 0;
  }
}

.facture-actions { display: inline-flex; justify-content: center; }
.facture-actions .inv-btn {
  min-height: 38px;
  padding: .5rem .75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .35rem;
}
.facture-actions .inv-btn i {
  color: var(--accent);
}
@media (max-width: 768px) {
  .facture-actions .btn .btn-label { display: none; }
  .facture-actions .inv-btn {
    padding: 0;
    width: 38px;
    min-width: 38px;
    min-height: 38px;
    gap: 0;
  }
}

.footer-summary {
  display: inline-flex;
  flex-wrap: wrap;
  gap: .6rem;
  justify-content: flex-end;
  width: 100%;
}
.summary-chip {
  display: inline-flex;
  align-items: center;
  gap: .5rem;
  padding: .45rem .85rem;
  border-radius: var(--rounded-full);
  font-size: .8rem;
  font-weight: 700;
  border: 1px solid;
  letter-spacing: .01em;
}
.summary-chip i { font-size: .75rem; opacity: .95; }
.chip-paid {
  background: var(--success-bg);
  color: var(--success);
  border-color: color-mix(in srgb, var(--success) 30%, transparent);
}
.chip-warn {
  background: var(--warning-bg);
  color: var(--warning);
  border-color: color-mix(in srgb, var(--warning) 30%, transparent);
}

.ledger-entry-ledger span {
  display: inline-flex;
  flex-direction: column;
}
.ledger-entry-ledger span small {
  font-weight: 500;
  color: var(--success);
  font-size: .7rem;
  margin-top: 2px;
}

/* ========== MODAL CONFIRMATION ========== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  animation: overlayFadeIn .18s ease-out;
}
@keyframes overlayFadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  background: var(--white);
  border-radius: 16px;
  width: 100%;
  max-width: 520px;
  box-shadow: var(--shadow-xl), 0 0 0 1px var(--gray-200);
  overflow: hidden;
  animation: modalRiseIn .22s cubic-bezier(.2,.9,.3,1.1);
}
.modal-card-sm { max-width: 460px; }
@keyframes modalRiseIn {
  from { opacity: 0; transform: translateY(18px) scale(.985); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header {
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--gray-200);
  background: linear-gradient(180deg, var(--white), var(--gray-50));
}
.modal-header h3 { margin: 0; font-size: 1.05rem; font-weight: 700; color: var(--gray-900); }
.modal-close {
  background: var(--gray-100);
  color: var(--gray-500);
  border: 1px solid var(--gray-200);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition-fast);
}
.modal-close:hover { background: var(--danger-bg); color: var(--danger); border-color: color-mix(in srgb, var(--danger) 30%, transparent); }

.modal-body { padding: 1.25rem; }
.form-group { margin-bottom: 1rem; }
.form-group:last-child { margin-bottom: 0; }
.form-label {
  display: block;
  font-size: .75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
  color: var(--gray-600);
  margin-bottom: .4rem;
}

.modal-total-box {
  background: var(--warning-bg);
  border: 1px solid var(--warning);
  padding: .85rem 1rem;
  border-radius: var(--rounded-md);
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}
.modal-total-box .mtl-label {
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--warning);
  opacity: .88;
}
.modal-total-box .mtl-value {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--warning);
}

.modal-footer {
  padding: 1rem 1.25rem;
  display: flex;
  justify-content: flex-end;
  gap: .6rem;
  border-top: 1px solid var(--gray-200);
  background: var(--gray-50);
}
.modal-footer .btn {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
  font-weight: 700;
  border-radius: var(--rounded-md);
  cursor: pointer;
  border: 1px solid transparent;
  transition: var(--transition-all);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .45rem;
  min-height: 40px;
}
.modal-footer .btn-grey {
  background: var(--white);
  color: var(--gray-600);
  border-color: var(--gray-300);
}
.modal-footer .btn-grey:hover {
  background: var(--gray-50);
  color: var(--gray-800);
  transform: translateY(-1px);
  border-color: var(--gray-400);
}
.modal-footer .btn-primary {
  background-color: var(--success);
  color: var(--white);
  box-shadow: 0 4px 14px 0 color-mix(in srgb, var(--success) 28%, transparent);
}
.modal-footer .btn-primary:hover:not(:disabled) {
  filter: brightness(1.05);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px 0 color-mix(in srgb, var(--success) 32%, transparent);
}
.modal-footer .btn:disabled { opacity: .55; cursor: not-allowed; }

@media (max-width: 768px) {
  .modal-overlay { padding: .5rem; }
  .modal-card { max-width: 100%; border-radius: 14px; }
  .modal-total-box { flex-direction: column; gap: .4rem; }
  .modal-total-box .mtl-value { font-size: 1.15rem; }
}

@media (max-width: 992px) {
  .filters-toggle { display: inline-flex; }
  .filters-panel { gap: var(--space-3); }
}
</style>
