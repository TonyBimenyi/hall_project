<template>
  <div class="accounting-page">
    <div class="page-header">
      <div>
        <h1>Comptabilite</h1>
        <p>Journal comptable des recettes et depenses validees avec suivi  des pieces justificatives.</p>
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
            placeholder="Rechercher par piece, reference, intitule ou auteur..."
          />
        </div>
        <button class="btn btn-sm" @click="resetFilters">
          <i class="fas fa-redo"></i> Reinitialiser
        </button>
        <button class="btn-icon filters-toggle" :class="{ active: filtersOpen }" title="Filtres" @click="filtersOpen = !filtersOpen">
          <i class="fas fa-filter"></i>
        </button>
      </div>

      <div v-show="!isMobile || filtersOpen" class="filters-panel">
        <select v-model="entryTypeFilter" class="filter-select-clean">
          <option value="">Toutes les ecritures</option>
          <option value="recette">Recettes</option>
          <option value="depense">Depenses</option>
        </select>
        <select v-model="preset" class="filter-select-clean">
          <option value="7d">7 derniers jours</option>
          <option value="28d">28 derniers jours</option>
          <option value="90d">90 derniers jours</option>
          <option value="this_month">Ce mois</option>
          <option value="last_month">Mois dernier</option>
          <option value="year">Cette annee</option>
          <option value="all">Toutes les dates</option>
          <option value="custom">Personnalise</option>
        </select>
        <input v-if="preset === 'custom'" v-model="customStart" type="date" class="filter-input-clean" />
        <input v-if="preset === 'custom'" v-model="customEnd" type="date" class="filter-input-clean" />
        <div class="current-balance-chip">
          <span>Solde actuelle</span>
          <strong :class="currentBalance >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(currentBalance) }}</strong>
        </div>
      </div>

      <div class="filter-range-note">
        {{ activeRangeNotice }}
      </div>
    </div>

    <div ref="exportRef" class="export-scope">
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-icon success"><i class="fas fa-arrow-trend-up"></i></div>
          <div class="stat-info">
            <span class="label">Recettes</span>
            <span class="value success">{{ formatMoney(totalRecettes) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon info"><i class="fas fa-money-check-dollar"></i></div>
          <div class="stat-info">
            <span class="label">Entrees manuelles</span>
            <span class="value info">{{ formatMoney(totalManualEntrees) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon danger"><i class="fas fa-arrow-trend-down"></i></div>
          <div class="stat-info">
            <span class="label">Depenses</span>
            <span class="value danger">{{ formatMoney(totalDepenses) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon" style="background:#fef3c7;color:#92400e;"><i class="fas fa-file-invoice-dollar"></i></div>
          <div class="stat-info">
            <span class="label">TCSTH collectée</span>
            <span class="value" style="color:#92400e;">{{ formatMoney(totalTVACollectee) }}</span>
          </div>
        </div>
        <div class="stat-card card">
          <div class="stat-icon primary"><i class="fas fa-receipt"></i></div>
          <div class="stat-info">
            <span class="label">Pieces</span>
            <span class="value info">{{ filteredEntries.length }}</span>
          </div>
        </div>
      </div>

      <div class="cashflow-overview card">
        <div class="cashflow-overview-head">
          <div>
            <span class="summary-eyebrow">Flux</span>
            <h2>Vue d'ensemble des entrees et sorties</h2>
            <p>Choisissez une lecture journalière regroupée par date ou une lecture détaillée pièce par pièce.</p>
          </div>
          <div class="cashflow-mode-switch">
            <button
              type="button"
              class="cashflow-mode-btn"
              :class="{ active: cashflowOverviewMode === 'daily' }"
              @click="cashflowOverviewMode = 'daily'"
            >
              Vue journaliere
            </button>
            <button
              type="button"
              class="cashflow-mode-btn"
              :class="{ active: cashflowOverviewMode === 'detailed' }"
              @click="cashflowOverviewMode = 'detailed'"
            >
              Vue detaillee
            </button>
          </div>
        </div>

        <div class="cashflow-overview-meta">
          <span>{{ cashflowOverviewNotice }}</span>
          <strong>{{ cashflowOverviewRangeLabel }}</strong>
        </div>

        <div class="cashflow-period-grid">
          <div class="cashflow-summary-card success-tone">
            <span class="cashflow-summary-label">Entrees de la periode</span>
            <strong class="text-success">{{ formatMoney(periodOverview.recettes) }}</strong>
            <small>{{ periodOverview.recetteCount }} mouvement(s)</small>
          </div>
          <div class="cashflow-summary-card danger-tone">
            <span class="cashflow-summary-label">Sorties de la periode</span>
            <strong class="text-danger">{{ formatMoney(periodOverview.depenses) }}</strong>
            <small>{{ periodOverview.depenseCount }} mouvement(s)</small>
          </div>
          <div class="cashflow-summary-card info-tone">
            <span class="cashflow-summary-label">Net de la periode</span>
            <strong :class="periodOverview.net >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(periodOverview.net) }}</strong>
            <small>{{ periodOverview.totalCount }} operation(s)</small>
          </div>
        </div>

        <div v-if="cashflowOverviewMode === 'daily'" class="cashflow-daily-list">
          <div class="ledger-head cashflow-table-head">
            <div>
              <h2 class="table-title">Flux journaliers regroupes</h2>
              <p class="ledger-subtitle">Toutes les entrees et sorties sont fusionnées sur une seule ligne par jour.</p>
            </div>
          </div>

          <div v-if="isMobile" class="admin-cards">
            <div v-if="cashflowDailyRows.length === 0" class="empty-cell">Aucun mouvement pour cette plage de dates.</div>
            <div v-else v-for="row in cashflowDailyRows" :key="row.date" class="admin-card ledger-card cashflow-daily-card">
              <div class="admin-card-head">
                <div>
                  <div class="admin-card-title">{{ formatDisplayDate(row.date) }}</div>
                  <div class="admin-card-subtitle">{{ row.totalCount }} mouvement(s)</div>
                </div>
                <span :class="['cashflow-net-pill', row.net >= 0 ? 'positive' : 'negative']">
                  {{ row.net >= 0 ? '+' : '' }}{{ formatMoney(row.net) }}
                </span>
              </div>

              <div class="admin-card-body">
                <div class="admin-kv">
                  <span class="k">Nombre d'entrees</span>
                  <span class="v">{{ row.recetteCount }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Montant des entrees</span>
                  <span class="v text-success">{{ formatMoney(row.recettes) }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Nombre de sorties</span>
                  <span class="v">{{ row.depenseCount }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Montant des sorties</span>
                  <span class="v text-danger">{{ formatMoney(row.depenses) }}</span>
                </div>
              </div>
            </div>
          </div>

          <table v-else class="admin-table accounting-table cashflow-daily-table">
            <colgroup>
              <col class="cashflow-col-date" />
              <col class="cashflow-col-count" />
              <col class="cashflow-col-amount" />
              <col class="cashflow-col-count" />
              <col class="cashflow-col-amount" />
              <col class="cashflow-col-net" />
            </colgroup>
            <thead>
              <tr>
                <th>Date</th>
                <th>Nb entrees</th>
                <th>Montant entrees</th>
                <th>Nb sorties</th>
                <th>Montant sorties</th>
                <th>Net journalier</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="cashflowDailyRows.length === 0">
                <td colspan="6" class="empty-cell">Aucun mouvement pour cette plage de dates.</td>
              </tr>
              <tr v-for="row in cashflowDailyRows" :key="row.date">
                <td>
                  <div class="cell-main">{{ formatDisplayDate(row.date) }}</div>
                  <div class="cell-sub">{{ row.totalCount }} mouvement(s)</div>
                </td>
                <td>{{ row.recetteCount }}</td>
                <td class="amount-cell text-success">{{ formatMoney(row.recettes) }}</td>
                <td>{{ row.depenseCount }}</td>
                <td class="amount-cell text-danger">{{ formatMoney(row.depenses) }}</td>
                <td class="amount-cell" :class="row.net >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(row.net) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="cashflowOverviewMode === 'detailed'" class="accounting-summary card">
        <div class="accounting-summary-main">
          <span class="summary-eyebrow">Journal</span>
          <h2>Vue detaillee par piece justificative</h2>
          <p>Chaque ecriture est ordonnee chronologiquement. Le numero de piece justificative suit l'ordre des operations comptables valides.</p>
        </div>
        <div class="accounting-summary-chips">
          <div class="summary-chip">
            <span class="summary-chip-label">Premiere piece</span>
            <strong>{{ firstVoucherLabel }}</strong>
          </div>
          <div class="summary-chip">
            <span class="summary-chip-label">Derniere piece</span>
            <strong>{{ lastVoucherLabel }}</strong>
          </div>
          <div class="summary-chip">
            <span class="summary-chip-label">Solde periode</span>
            <strong :class="netBalance >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(netBalance) }}</strong>
          </div>
        </div>
      </div>

      <div v-if="cashflowOverviewMode === 'detailed'" class="table-container card">
        <div class="ledger-head">
          <div>
            <h2 class="table-title">Vue detaillee des pieces</h2>
            <p class="ledger-subtitle">Recettes issues des paiements encaisses, des entrees manuelles et des depenses validees.</p>
          </div>
          <AdminAppTablePagination
            :start="entriesStartIndex"
            :end="entriesEndIndex"
            :total="entriesTotalItems"
            :can-prev="entriesCanPrev"
            :can-next="entriesCanNext"
            :disabled="isLoading"
            @prev="entriesPrevPage"
            @next="entriesNextPage"
          />
        </div>

        <div v-if="isMobile" class="admin-cards">
          <template v-if="isLoading">
            <div v-for="n in 5" :key="`ledger-skeleton-${n}`" class="admin-card">
              <div class="admin-card-head">
                <div style="width: 100%;">
                  <div class="skeleton-line skeleton-w-60"></div>
                  <div style="margin-top: 8px;" class="skeleton-line skeleton-w-45"></div>
                </div>
              </div>
              <div class="admin-card-body">
                <div class="skeleton-line skeleton-w-70"></div>
                <div class="skeleton-line skeleton-w-40"></div>
                <div class="skeleton-line skeleton-w-50"></div>
              </div>
            </div>
          </template>

          <template v-else>
            <div v-for="entry in paginatedEntries" :key="entry.entryKey" class="admin-card ledger-card">
              <div class="admin-card-head">
                <div>
                  <div class="admin-card-title">{{ entry.voucherNumber }}</div>
                  <div class="admin-card-subtitle">{{ formatDisplayDate(entry.date) }} • {{ entry.typeLabel }}</div>
                </div>
                <span :class="['badge', entry.movementType === 'recette' ? 'badge-success' : 'badge-danger']">{{ entry.typeLabel }}</span>
              </div>

              <div class="admin-card-body">
                <div class="admin-kv">
                  <span class="k">Reference</span>
                  <span class="v">{{ entry.reference }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Intitule</span>
                  <span class="v">{{ entry.title }}</span>
                </div>
                <div class="admin-kv" v-if="entry.subtitle">
                  <span class="k">Detail</span>
                  <span class="v">{{ entry.subtitle }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Auteur</span>
                  <span class="v">{{ entry.actor }}</span>
                </div>
                <div class="admin-kv" v-if="entry.subtotal_ht > 0">
                  <span class="k">Sous-total HT</span>
                  <span class="v">{{ formatMoney(entry.subtotal_ht) }}</span>
                </div>
                <div class="admin-kv" v-if="entry.tva_amount > 0">
                  <span class="k">TCSTH {{ entryTVARate(entry) }}% (hébergement)</span>
                  <span class="v" style="color:#92400e;">{{ formatMoney(entry.tva_amount) }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Recette</span>
                  <span class="v text-success">{{ entry.recette > 0 ? formatMoney(entry.recette) : '-' }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Depense</span>
                  <span class="v text-danger">{{ entry.depense > 0 ? formatMoney(entry.depense) : '-' }}</span>
                </div>
                <div class="admin-kv">
                  <span class="k">Solde</span>
                  <span class="v" :class="entry.balance >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(entry.balance) }}</span>
                </div>
              </div>
            </div>
          </template>

          <div v-if="!isLoading && filteredEntries.length === 0" class="empty-cell">Aucune ecriture comptable sur cette periode.</div>
        </div>

        <table v-else class="admin-table accounting-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>No. piece justificatif</th>
              <th>Reference</th>
              <th>Intitule</th>
              <th>Auteur</th>
              <th>HT</th>
              <th>TCSTH</th>
              <th>Recettes</th>
              <th>Depenses</th>
              <th>Solde</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="isLoading">
              <tr v-for="n in 6" :key="`acct-sk-${n}`">
                <td><div class="skeleton-line skeleton-w-40"></div></td>
                <td><div class="skeleton-line skeleton-w-40"></div></td>
                <td><div class="skeleton-line skeleton-w-50"></div></td>
                <td><div class="skeleton-line skeleton-w-80"></div></td>
                <td><div class="skeleton-line skeleton-w-50"></div></td>
                <td><div class="skeleton-line skeleton-w-35"></div></td>
                <td><div class="skeleton-line skeleton-w-35"></div></td>
                <td><div class="skeleton-line skeleton-w-35"></div></td>
                <td><div class="skeleton-line skeleton-w-35"></div></td>
                <td><div class="skeleton-line skeleton-w-40"></div></td>
              </tr>
            </template>

            <template v-else>
              <tr v-for="entry in paginatedEntries" :key="entry.entryKey">
                <td>{{ formatDisplayDate(entry.date) }}</td>
                <td><code>{{ entry.voucherNumber }}</code></td>
                <td>
                  <div class="cell-main">{{ entry.reference }}</div>
                  <div v-if="entry.referenceHint" class="cell-sub">{{ entry.referenceHint }}</div>
                </td>
                <td>
                  <div class="cell-main">{{ entry.title }}</div>
                  <div v-if="entry.subtitle" class="cell-sub">{{ entry.subtitle }}</div>
                </td>
                <td>
                  <div class="actor-cell">
                    <span class="actor-name">{{ entry.actor }}</span>
                    <span v-if="entry.actorHint" class="actor-hint">{{ entry.actorHint }}</span>
                  </div>
                </td>
                <td class="amount-cell">{{ entry.subtotal_ht > 0 ? formatMoney(entry.subtotal_ht) : '-' }}</td>
                <td class="amount-cell" style="color:#92400e;">{{ entry.tva_amount > 0 ? formatMoney(entry.tva_amount) : '-' }}</td>
                <td class="amount-cell text-success">{{ entry.recette > 0 ? formatMoney(entry.recette) : '-' }}</td>
                <td class="amount-cell text-danger">{{ entry.depense > 0 ? formatMoney(entry.depense) : '-' }}</td>
                <td class="amount-cell" :class="entry.balance >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(entry.balance) }}</td>
              </tr>
              <tr v-if="filteredEntries.length === 0">
                <td colspan="10" class="empty-cell">Aucune ecriture comptable sur cette periode.</td>
              </tr>
            </template>
          </tbody>
          <tfoot v-if="!isLoading && filteredEntries.length">
            <tr class="table-total-row">
              <td colspan="5">Totaux de la periode</td>
              <td class="amount-cell">{{ formatMoney(totalHT) }}</td>
              <td class="amount-cell" style="color:#92400e;">{{ formatMoney(totalTVACollectee) }}</td>
              <td class="amount-cell text-success">{{ formatMoney(totalRecettes) }}</td>
              <td class="amount-cell text-danger">{{ formatMoney(totalDepenses) }}</td>
              <td class="amount-cell" :class="netBalance >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(netBalance) }}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useDateFormat } from '~/composables/useDateFormat'
import { useAdminExportDocuments } from '~/composables/useAdminExportDocuments'
import { useDisplayIds } from '~/composables/useDisplayIds'
import { canExportAdminExcel, getStoredUser } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })

const { formatMoney } = useMoney()
const { formatDisplayDate } = useDateFormat()
const { getSanitizedExportHtml, buildPdfDocumentHtml, downloadHtmlAsXls, downloadPdfHtml, buildExportFileName } = useAdminExportDocuments()
const { buildHashSequenceMap } = useDisplayIds()

const COMPTA_TVA_PCT = 5
const COMPTA_TVA_DIV = 1 + (COMPTA_TVA_PCT / 100)
const _comptaRound = (n) => Math.round((Number(n || 0) + Number.EPSILON) * 100) / 100
const _tvaAppliesForEntry = (objOrType) => {
  if (typeof objOrType === 'string') {
    return String(objOrType || '').toLowerCase() === 'room'
  }
  const o = objOrType || {}
  // Si booking_type explicit → le prendre
  const bt = String(o.booking_type || '').toLowerCase()
  if (bt === 'room' || bt === 'hall') return bt === 'room'
  // Si sourceType autre que payment -> pas TVA (dépenses/entrées manuelles)
  if (o.sourceType && o.sourceType !== 'payment') return false
  // Si subtitle/itemLabel contient "Salle" ou event_type → hall
  const sub = String(o.subtitle || '')
  const title = String(o.title || '').toLowerCase()
  if (sub.includes('Salle') || title.includes('salle')) return false
  // Sinon défaut pour les paiements/booking: on applique (room)
  return o.sourceType === 'payment'
}
const comptaExtractHT = (ttc, ctx = null) => {
  const value = Number(ttc || 0)
  const applies = ctx ? _tvaAppliesForEntry(ctx) : true
  if (!applies || value <= 0) return value
  return _comptaRound(value / COMPTA_TVA_DIV)
}
const comptaExtractTVA = (ttc, ctx = null) => {
  const value = Number(ttc || 0)
  const applies = ctx ? _tvaAppliesForEntry(ctx) : true
  if (!applies || value <= 0) return 0
  return _comptaRound(value - comptaExtractHT(value, ctx))
}
const entryTVARate = (entry) => {
  if (!entry) return 0
  const explicit = Number(entry?.tva_rate ?? NaN)
  if (!isNaN(explicit) && explicit !== 0 && entry?.tva_amount > 0) return explicit
  return _tvaAppliesForEntry(entry) ? COMPTA_TVA_PCT : 0
}

const payments = ref([])
const expenses = ref([])
const entrees = ref([])
const currentUser = ref({})
const exportRef = ref(null)
const exportingPdf = ref(false)
const exportingXls = ref(false)
const loadingPayments = ref(false)
const loadingExpenses = ref(false)
const loadingEntrees = ref(false)
const search = ref('')
const entryTypeFilter = ref('')
const preset = ref('28d')
const customStart = ref('')
const customEnd = ref('')
const isMobile = ref(false)
const filtersOpen = ref(false)
const cashflowOverviewMode = ref('daily')

const canExportExcel = computed(() => canExportAdminExcel(currentUser.value))
const isLoading = computed(() => loadingPayments.value || loadingExpenses.value || loadingEntrees.value)

const toNumber = (value) => Number(value || 0)
const pad = (value, size = 4) => String(value || 0).padStart(size, '0')

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
    return { start: `${now.getFullYear()}-01-01`, end: todayYmd }
  }
  if (value === 'this_month') {
    const now = new Date()
    return { start: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`, end: todayYmd }
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
  if (!rangeStartYmd.value || !rangeEndYmd.value) return 'Toutes les ecritures valides sont affichees sans limite de date.'
  if (preset.value === 'custom') return `Periode personnalisee: du ${rangeStartYmd.value} au ${rangeEndYmd.value}.`
  return `Periode comptable affichee: du ${rangeStartYmd.value} au ${rangeEndYmd.value}.`
})

const inRangeYmd = (ymd, start, end) => {
  const value = String(ymd || '').slice(0, 10)
  if (!start || !end) return true
  if (!value) return false
  return value >= start && value <= end
}

const paymentDisplayId = (payment) => payment?.code || (payment?.id ? `LBP${pad(payment.id, 8)}` : 'LBP00000001')
const expenseDisplayIds = computed(() => buildHashSequenceMap(expenses.value))
const expenseDisplayId = (expense) => expenseDisplayIds.value.get(expense?.id) || '#0001'

const paymentItemLabel = (payment) => {
  if (payment?.booking_type === 'room') return payment?.booking_room_display || '-'
  return payment?.booking_hall_name || '-'
}

const paymentEntries = computed(() => {
  return (payments.value || [])
    .filter(payment => String(payment?.status || '') === 'paid')
    .map((payment) => {
      const bookingCode = String(payment?.booking_code || '').trim()
      const clientName = String(payment?.booking_customer_name || '').trim() || 'Client'
      const itemLabel = paymentItemLabel(payment)
      const title = bookingCode
        ? `Recette reservation ${bookingCode} - ${clientName}`
        : `Recette reservation - ${clientName}`
      const subtitle = [payment?.booking_event_type || '', itemLabel].filter(Boolean).join(' • ')
      const amount = toNumber(payment?.amount)
      const booking_type = String(payment?.booking_type || payment?.booking?.booking_type || '').toLowerCase() || ((itemLabel || '').includes('Salle') || (payment?.booking_event_type || '').trim() ? 'hall' : 'room')
      const appliesTVA = booking_type === 'room'
      const hasExplicitTVA = payment?.booking_tva_amount !== undefined && payment?.booking_tva_amount !== null && payment?.booking_tva_amount !== ''
      const tva_amount = hasExplicitTVA ? toNumber(payment.booking_tva_amount) : (appliesTVA ? comptaExtractTVA(payment?.booking_total_price, { booking_type }) : 0)
      const subtotal_ht = hasExplicitTVA ? toNumber(payment?.booking_subtotal_ht) : (appliesTVA ? comptaExtractHT(payment?.booking_total_price, { booking_type }) : toNumber(payment?.booking_total_price))
      const tva_rate = hasExplicitTVA ? toNumber(payment?.booking_tva_rate) : (appliesTVA ? COMPTA_TVA_PCT : 0)
      return {
        entryKey: `payment-${payment.id}`,
        sourceType: 'payment',
        movementType: 'recette',
        typeLabel: 'Recette',
        id: Number(payment?.id || 0),
        date: String(payment?.date || payment?.created_at || '').slice(0, 10),
        createdAt: String(payment?.created_at || payment?.date || ''),
        reference: String(payment?.reference || '').trim() || paymentDisplayId(payment),
        referenceHint: bookingCode ? `Code reservation: ${bookingCode}` : '',
        title,
        subtitle,
        actor: String(payment?.created_by_name || payment?.updated_by_name || 'Systeme').trim() || 'Systeme',
        actorHint: String(payment?.method || '').trim() || '',
        recette: amount,
        depense: 0,
        subtotal_ht,
        tva_amount,
        tva_rate,
        booking_type,
      }
    })
})

const expenseEntries = computed(() => {
  return (expenses.value || [])
    .filter(expense => String(expense?.status || '') === 'paid')
    .map((expense) => {
      const displayId = expenseDisplayId(expense)
      const description = String(expense?.description || '').trim() || 'Depense interne'
      const paidTo = String(expense?.paid_to || '').trim()
      return {
        entryKey: `expense-${expense.id}`,
        sourceType: 'expense',
        movementType: 'depense',
        typeLabel: 'Depense',
        id: Number(expense?.id || 0),
        date: String(expense?.date || '').slice(0, 10),
        createdAt: String(expense?.created_at || expense?.date || ''),
        reference: displayId,
        referenceHint: paidTo ? `Beneficiaire: ${paidTo}` : '',
        title: description,
        subtitle: [expense?.category || '', paidTo].filter(Boolean).join(' • '),
        actor: String(expense?.created_by_name || expense?.paid_by || 'Systeme').trim() || 'Systeme',
        actorHint: String(expense?.paid_by || '').trim() || '',
        recette: 0,
        depense: toNumber(expense?.amount),
        subtotal_ht: 0,
        tva_amount: 0,
        tva_rate: 0,
      }
    })
})

const entreeEntries = computed(() => {
  return (entrees.value || [])
    .filter(entree => String(entree?.status || '') === 'paid')
    .map((entree) => {
      const title = String(entree?.title || '').trim() || 'Entree manuelle'
      const receivedFrom = String(entree?.received_from || '').trim()
      return {
        entryKey: `entree-${entree.id}`,
        sourceType: 'entree',
        movementType: 'recette',
        typeLabel: 'Recette',
        id: Number(entree?.id || 0),
        date: String(entree?.date || entree?.created_at || '').slice(0, 10),
        createdAt: String(entree?.created_at || entree?.date || ''),
        reference: String(entree?.reference || entree?.code || '').trim() || 'Entree',
        referenceHint: entree?.code ? `Code entree: ${entree.code}` : '',
        title,
        subtitle: [entree?.category || '', receivedFrom].filter(Boolean).join(' • '),
        actor: String(entree?.created_by_name || entree?.received_by || 'Systeme').trim() || 'Systeme',
        actorHint: String(entree?.received_by || '').trim() || '',
        recette: toNumber(entree?.amount),
        depense: 0,
        subtotal_ht: 0,
        tva_amount: 0,
        tva_rate: 0,
      }
    })
})

const ledgerEntriesAsc = computed(() => {
  return [...paymentEntries.value, ...entreeEntries.value, ...expenseEntries.value]
    .filter(entry => entry.date)
    .sort((a, b) => {
      if (a.date !== b.date) return a.date.localeCompare(b.date)
      const createdCompare = String(a.createdAt || '').localeCompare(String(b.createdAt || ''))
      if (createdCompare !== 0) return createdCompare
      return Number(a.id || 0) - Number(b.id || 0)
    })
})

const voucherMap = computed(() => {
  const output = new Map()
  ledgerEntriesAsc.value.forEach((entry, index) => {
    output.set(entry.entryKey, `PJ-${pad(index + 1)}`)
  })
  return output
})

const filteredEntries = computed(() => {
  const query = search.value.toLowerCase().trim()
  return ledgerEntriesAsc.value
    .filter((entry) => {
      const matchesType = entryTypeFilter.value === '' || entry.movementType === entryTypeFilter.value
      const matchesDate = inRangeYmd(entry.date, rangeStartYmd.value, rangeEndYmd.value)
      const voucherNumber = voucherMap.value.get(entry.entryKey) || ''
      const haystack = [
        entry.reference,
        entry.referenceHint,
        entry.title,
        entry.subtitle,
        entry.actor,
        entry.actorHint,
        voucherNumber,
      ].join(' ').toLowerCase()
      const matchesSearch = query === '' || haystack.includes(query)
      return matchesType && matchesDate && matchesSearch
    })
    .map(entry => ({
      ...entry,
      voucherNumber: voucherMap.value.get(entry.entryKey) || 'PJ-0000',
    }))
})

const entriesInActiveRange = computed(() => {
  return ledgerEntriesAsc.value.filter(entry => inRangeYmd(entry.date, rangeStartYmd.value, rangeEndYmd.value))
})

const periodOverview = computed(() => {
  return entriesInActiveRange.value.reduce((summary, entry) => {
    const recette = Number(entry.recette || 0)
    const depense = Number(entry.depense || 0)
    summary.recettes += recette
    summary.depenses += depense
    summary.net += recette - depense
    if (recette > 0) summary.recetteCount += 1
    if (depense > 0) summary.depenseCount += 1
    summary.totalCount += 1
    return summary
  }, {
    recettes: 0,
    depenses: 0,
    net: 0,
    recetteCount: 0,
    depenseCount: 0,
    totalCount: 0,
  })
})

const cashflowDailyRows = computed(() => {
  const grouped = new Map()
  for (const entry of entriesInActiveRange.value) {
    const date = String(entry.date || '').slice(0, 10)
    if (!date) continue
    if (!grouped.has(date)) {
      grouped.set(date, {
        date,
        recettes: 0,
        depenses: 0,
        net: 0,
        recetteCount: 0,
        depenseCount: 0,
        totalCount: 0,
      })
    }
    const row = grouped.get(date)
    const recette = Number(entry.recette || 0)
    const depense = Number(entry.depense || 0)
    row.recettes += recette
    row.depenses += depense
    row.net += recette - depense
    if (recette > 0) row.recetteCount += 1
    if (depense > 0) row.depenseCount += 1
    row.totalCount += 1
  }
  return Array.from(grouped.values()).sort((a, b) => b.date.localeCompare(a.date))
})

const cashflowOverviewRangeLabel = computed(() => {
  if (!rangeStartYmd.value || !rangeEndYmd.value) return 'Toutes les dates'
  if (rangeStartYmd.value === rangeEndYmd.value) return `Le ${rangeStartYmd.value}`
  return `Du ${rangeStartYmd.value} au ${rangeEndYmd.value}`
})

const cashflowOverviewNotice = computed(() => {
  if (cashflowOverviewMode.value === 'detailed') {
    return 'Lecture détaillée de chaque pièce comptable validée dans la plage active.'
  }
  return 'Lecture jour par jour avec toutes les entrées et sorties regroupées sur une seule ligne.'
})

const balanceMap = computed(() => {
  const output = new Map()
  let balance = 0
  for (const entry of filteredEntries.value) {
    balance += Number(entry.recette || 0) - Number(entry.depense || 0)
    output.set(entry.entryKey, balance)
  }
  return output
})

const decoratedEntries = computed(() => {
  return filteredEntries.value.map(entry => ({
    ...entry,
    balance: balanceMap.value.get(entry.entryKey) || 0,
  }))
})

const totalRecettes = computed(() => decoratedEntries.value.reduce((sum, entry) => sum + Number(entry.recette || 0), 0))
const totalDepenses = computed(() => decoratedEntries.value.reduce((sum, entry) => sum + Number(entry.depense || 0), 0))
const netBalance = computed(() => totalRecettes.value - totalDepenses.value)
const totalHT = computed(() => decoratedEntries.value.reduce((sum, entry) => sum + Number(entry.subtotal_ht || 0), 0))
const totalTVACollectee = computed(() => decoratedEntries.value.reduce((sum, entry) => sum + Number(entry.tva_amount || 0), 0))
const totalManualEntrees = computed(() => entreeEntries.value.reduce((sum, entry) => sum + Number(entry.recette || 0), 0))
const currentBalance = computed(() => {
  const recettes = [...paymentEntries.value, ...entreeEntries.value].reduce((sum, entry) => sum + Number(entry.recette || 0), 0)
  const depenses = expenseEntries.value.reduce((sum, entry) => sum + Number(entry.depense || 0), 0)
  return recettes - depenses
})
const firstVoucherLabel = computed(() => decoratedEntries.value[0]?.voucherNumber || 'Aucune')
const lastVoucherLabel = computed(() => decoratedEntries.value[decoratedEntries.value.length - 1]?.voucherNumber || 'Aucune')

const {
  paginatedItems: paginatedEntries,
  totalItems: entriesTotalItems,
  startIndex: entriesStartIndex,
  endIndex: entriesEndIndex,
  canPrev: entriesCanPrev,
  canNext: entriesCanNext,
  prevPage: entriesPrevPage,
  nextPage: entriesNextPage,
} = usePagination(decoratedEntries, 25)

const resetFilters = () => {
  search.value = ''
  entryTypeFilter.value = ''
  preset.value = '28d'
  customStart.value = ''
  customEnd.value = ''
}

const fetchPayments = async () => {
  loadingPayments.value = true
  try {
    const { data } = await api.get('payments/')
    payments.value = Array.isArray(data) ? data : []
  } catch {
    notify('Erreur lors du chargement des recettes comptables', 'danger')
  } finally {
    loadingPayments.value = false
  }
}

const fetchExpenses = async () => {
  loadingExpenses.value = true
  try {
    const { data } = await api.get('expenses/')
    expenses.value = Array.isArray(data) ? data : []
  } catch {
    notify('Erreur lors du chargement des depenses comptables', 'danger')
  } finally {
    loadingExpenses.value = false
  }
}

const fetchEntrees = async () => {
  loadingEntrees.value = true
  try {
    const { data } = await api.get('entrees/')
    entrees.value = Array.isArray(data) ? data : []
  } catch {
    notify('Erreur lors du chargement des entrees comptables', 'danger')
  } finally {
    loadingEntrees.value = false
  }
}

const exportXls = async () => {
  if (!canExportExcel.value || !exportRef.value) return
  exportingXls.value = true
  await nextTick()
  const contentHtml = getSanitizedExportHtml(exportRef.value, { htmlMode: 'inner', removeActionsColumn: true })
  downloadHtmlAsXls({ type: 'comptabilite', contentHtml })
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
    title: 'Comptabilite',
    documentTitle: buildExportFileName('comptabilite', 'pdf').replace(/\.pdf$/, ''),
    subtitle: 'Journal comptable des recettes, entrees manuelles et depenses exporte depuis l’administration.',
    typeLabel: 'Comptabilite PDF',
    tableTitles: ['Grand livre comptable'],
    periodLabel: rangeStartYmd.value && rangeEndYmd.value ? `${rangeStartYmd.value} -> ${rangeEndYmd.value}` : 'Toutes les dates',
    contentHtml,
  })
  const ok = await downloadPdfHtml({ html, fileName: buildExportFileName('comptabilite', 'pdf') })
  if (!ok) {
    exportingPdf.value = false
    return
  }
  setTimeout(() => {
    exportingPdf.value = false
  }, 350)
}

onMounted(async () => {
  currentUser.value = getStoredUser()
  await Promise.all([fetchPayments(), fetchExpenses(), fetchEntrees()])
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
  }
})
</script>

<style scoped>
.accounting-page {
  padding: 0;
}


.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-8);
}

.page-header h1 {
  font-size: 1.75rem;
  margin: 0 0 0.35rem;
}

.page-header p {
  margin: 0;
  color: var(--gray-500);
  max-width: 720px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.controls {
  margin-bottom: var(--space-6);
}

.controls-top {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-icon {
  position: absolute;
  top: 50%;
  left: 14px;
  transform: translateY(-50%);
  color: var(--gray-400);
}
.ledger-head h2{
  font-size: 1.75rem;
}

.search-input-clean,
.filter-select-clean,
.filter-input-clean {
  width: 100%;
  min-height: 46px;
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  color: var(--gray-900);
}

.search-input-clean {
  padding: 0 14px 0 42px;
}

.filter-select-clean,
.filter-input-clean {
  padding: 0 14px;
}

.filters-toggle {
  width: 42px;
  height: 42px;
  border: 1px solid var(--gray-200);
  border-radius: 12px;
  background: var(--white);
}

.filters-toggle.active {
  color: #2563eb;
  border-color: rgba(37, 99, 235, 0.25);
  background: rgba(37, 99, 235, 0.06);
}

.filters-panel {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.current-balance-chip {
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 46px;
  padding: 0 16px;
  border: 1px solid var(--gray-200);
  border-radius: 14px;
  background: var(--white);
  white-space: nowrap;
}

.current-balance-chip span {
  color: var(--gray-500);
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.current-balance-chip strong {
  color: var(--gray-900);
  font-size: 1rem;
}

.filter-range-note {
  margin-top: 12px;
  color: var(--gray-500);
  font-size: 0.86rem;
}

.export-scope {
  display: grid;
  gap: 18px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  flex-shrink: 0;
}

.stat-icon.success { background: var(--success-bg); color: var(--success); }
.stat-icon.danger { background: var(--danger-bg); color: var(--danger); }
.stat-icon.primary { background: rgba(37, 99, 235, 0.12); color: #2563eb; }
.stat-icon.info { background: var(--info-bg); color: var(--info); }

.stat-info {
  display: grid;
  gap: 4px;
}

.stat-info .label {
  color: var(--gray-500);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-info .value {
  color: var(--gray-900);
  font-size: 1.35rem;
  font-weight: 900;
}

.accounting-summary {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.95fr);
  gap: 16px;
  align-items: stretch;
}

.cashflow-overview {
  display: grid;
  gap: 16px;
}

.cashflow-overview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.cashflow-overview-head h2 {
  margin: 0.85rem 0 0.35rem;
  font-size: 1.3rem;
}

.cashflow-overview-head p {
  margin: 0;
  color: var(--gray-500);
  line-height: 1.6;
}

.cashflow-mode-switch {
  display: inline-flex;
  gap: 8px;
  padding: 6px;
  border: 1px solid var(--gray-200);
  border-radius: 16px;
  background: var(--gray-50);
}

.cashflow-mode-btn {
  min-height: 40px;
  padding: 0 16px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--gray-600);
  font-weight: 700;
}

.cashflow-mode-btn.active {
  background: var(--white);
  color: #2563eb;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
}

.cashflow-overview-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--gray-500);
  font-size: 0.9rem;
}

.cashflow-overview-meta strong {
  color: var(--gray-900);
}

.cashflow-period-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.cashflow-summary-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  border: 1px solid var(--gray-200);
  border-radius: 18px;
  background: var(--white);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.cashflow-summary-card small {
  color: var(--gray-500);
}

.cashflow-summary-label {
  color: gray;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.success-tone {
  background: var(--white);
  /* border-color: rgba(0, 138, 92, 0.22); */
  border: 2px solid rgba(0, 138, 92, 0.22);
}

.danger-tone {
  background: var(--white);
  border-color: rgba(239, 68, 68, 0.18);
  border: 2px solid rgba(239, 68, 68, 0.18);
}

.info-tone {
 background: var(--white);
  border-color: rgba(37, 99, 235, 0.18);
  border: 2px solid rgba(37, 99, 235, 0.18);
}

.cashflow-daily-list {
  display: grid;
  gap: 14px;
}

.cashflow-table-head {
  margin-bottom: 0;
}

.cashflow-daily-card {
  border: 1px solid var(--gray-200);
}

.cashflow-daily-table th,
.cashflow-daily-table td {
  vertical-align: middle;
}

.cashflow-daily-table {
  table-layout: fixed;
}

.cashflow-col-date {
  width: 22%;
}

.cashflow-col-count {
  width: 10%;
}

.cashflow-col-amount,
.cashflow-col-net {
  width: 19%;
}

.cashflow-daily-table thead th {
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.cashflow-daily-table td {
  padding-top: 20px;
  padding-bottom: 20px;
  text-align: left;
}

.cashflow-daily-table th:nth-child(2),
.cashflow-daily-table th:nth-child(4),
.cashflow-daily-table td:nth-child(2),
.cashflow-daily-table td:nth-child(4) {
  text-align: center;
  font-weight: 700;
}

.cashflow-daily-table th:nth-child(3),
.cashflow-daily-table th:nth-child(5),
.cashflow-daily-table th:nth-child(6),
.cashflow-daily-table td:nth-child(3),
.cashflow-daily-table td:nth-child(5),
.cashflow-daily-table td:nth-child(6) {
  text-align: right;
}

.cashflow-day-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.cashflow-day-head strong {
  display: block;
  color: var(--gray-900);
}

.cashflow-day-head small {
  color: var(--gray-500);
}

.cashflow-net-pill {
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 800;
  white-space: nowrap;
}

.cashflow-net-pill.positive {
  background: var(--success-bg);
  color: var(--success);
}

.cashflow-net-pill.negative {
  background: var(--danger-bg);
  color: var(--danger);
}

.cashflow-day-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.cashflow-day-stat {
  display: grid;
  gap: 6px;
  padding: 18px;
  border: 1px solid var(--gray-200);
  border-radius: 14px;
  background: rgba(248, 250, 252, 0.88);
}

.cashflow-day-stat span {
  color: var(--gray-500);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.accounting-summary-main {
  padding: 4px 2px;
}

.summary-eyebrow {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #2563eb;
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.accounting-summary-main h2 {
  margin: 0.85rem 0 0.4rem;
  font-size: 1.3rem;
}

.accounting-summary-main p {
  margin: 0;
  color: var(--gray-500);
  line-height: 1.6;
}

.accounting-summary-chips {
  display: grid;
  gap: 12px;
}

.summary-chip {
  border: 1px solid var(--gray-200);
  border-radius: 18px;
  padding: 16px 18px;
  background: var(--white);
}

.summary-chip-label {
  display: block;
  color: var(--gray-500);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.summary-chip strong {
  font-size: 1.08rem;
  color: var(--gray-900);
}

.ledger-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: var(--space-4);
}

.ledger-head .table-title {
  margin: 0 0 0.35rem;
}

.table-title{
  font-size: 1.75 rem;
}



.ledger-subtitle {
  margin: 0;
  color: var(--gray-500);
}

.accounting-table .cell-main {
  color: var(--gray-900);
  font-weight: 700;
}

.accounting-table .cell-sub {
  margin-top: 4px;
  color: var(--gray-500);
  font-size: 0.82rem;
}

.actor-cell {
  display: grid;
  gap: 4px;
}

.actor-name {
  color: var(--gray-900);
  font-weight: 700;
}

.actor-hint {
  color: var(--gray-500);
  font-size: 0.82rem;
}

.amount-cell {
  font-weight: 800;
  text-align: right;
  white-space: nowrap;
}

.text-success {
  color: var(--success) !important;
}

.text-danger {
  color: var(--danger) !important;
}

.ledger-card {
  border: 1px solid var(--gray-200);
}

.table-total-row td {
  font-weight: 900;
  background: var(--gray-50);
}

:global(html[data-admin-theme="dark"]) .search-input-clean,
:global(html[data-admin-theme="dark"]) .filter-select-clean,
:global(html[data-admin-theme="dark"]) .filter-input-clean,
:global(html[data-admin-theme="dark"]) .filters-toggle,
:global(html[data-admin-theme="dark"]) .current-balance-chip,
:global(html[data-admin-theme="dark"]) .cashflow-mode-switch,
:global(html[data-admin-theme="dark"]) .cashflow-daily-card,
:global(html[data-admin-theme="dark"]) .cashflow-summary-card,
:global(html[data-admin-theme="dark"]) .cashflow-day-stat,
:global(html[data-admin-theme="dark"]) .summary-chip,
:global(html[data-admin-theme="dark"]) .ledger-card,
:global(html[data-admin-theme="dark"]) .table-total-row td {
  background: rgba(15, 23, 42, 0.82);
  border-color: rgba(51, 65, 85, 0.95);
}

:global(html[data-admin-theme="dark"]) .page-header p,
:global(html[data-admin-theme="dark"]) .filter-range-note,
:global(html[data-admin-theme="dark"]) .ledger-subtitle,
:global(html[data-admin-theme="dark"]) .cashflow-overview-head p,
:global(html[data-admin-theme="dark"]) .cashflow-overview-meta,
:global(html[data-admin-theme="dark"]) .cashflow-summary-card small,
:global(html[data-admin-theme="dark"]) .cashflow-summary-label,
:global(html[data-admin-theme="dark"]) .cashflow-day-head small,
:global(html[data-admin-theme="dark"]) .cashflow-day-stat span,
:global(html[data-admin-theme="dark"]) .accounting-summary-main p,
:global(html[data-admin-theme="dark"]) .current-balance-chip span,
:global(html[data-admin-theme="dark"]) .summary-chip-label,
:global(html[data-admin-theme="dark"]) .accounting-table .cell-sub,
:global(html[data-admin-theme="dark"]) .actor-hint,
:global(html[data-admin-theme="dark"]) .stat-info .label {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .page-header h1,
:global(html[data-admin-theme="dark"]) .cashflow-overview-head h2,
:global(html[data-admin-theme="dark"]) .cashflow-overview-meta strong,
:global(html[data-admin-theme="dark"]) .cashflow-day-head strong,
:global(html[data-admin-theme="dark"]) .accounting-summary-main h2,
:global(html[data-admin-theme="dark"]) .current-balance-chip strong,
:global(html[data-admin-theme="dark"]) .stat-info .value,
:global(html[data-admin-theme="dark"]) .summary-chip strong,
:global(html[data-admin-theme="dark"]) .accounting-table .cell-main,
:global(html[data-admin-theme="dark"]) .actor-name {
  color: #f8fafc;
}

:global(html[data-admin-theme="dark"]) .cashflow-mode-btn {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .cashflow-mode-btn.active {
  background: rgba(30, 41, 59, 0.95);
  color: #93c5fd;
  box-shadow: none;
}

:global(html[data-admin-theme="dark"]) .cashflow-summary-card.success-tone,
:global(html[data-admin-theme="dark"]) .cashflow-summary-card.danger-tone,
:global(html[data-admin-theme="dark"]) .cashflow-summary-card.info-tone {
  background: rgba(15, 23, 42, 0.92) !important;
  box-shadow: none;
}

:global(html[data-admin-theme="dark"]) .cashflow-summary-card.success-tone {
  border-color: rgba(16, 185, 129, 0.28) !important;
}

:global(html[data-admin-theme="dark"]) .cashflow-summary-card.danger-tone {
  border-color: rgba(239, 68, 68, 0.24) !important;
}

:global(html[data-admin-theme="dark"]) .cashflow-summary-card.info-tone {
  border-color: rgba(59, 130, 246, 0.24) !important;
}

:global(html[data-admin-theme="dark"]) .cashflow-summary-card .cashflow-summary-label,
:global(html[data-admin-theme="dark"]) .cashflow-summary-card small {
  color: #cbd5e1 !important;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .cashflow-period-grid {
    grid-template-columns: 1fr;
  }

  .accounting-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .filters-panel {
    grid-template-columns: 1fr 1fr;
  }

  .cashflow-day-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid,
  .filters-panel {
    grid-template-columns: 1fr;
  }

  .cashflow-mode-switch {
    width: 100%;
  }

  .cashflow-mode-btn {
    flex: 1 1 0;
  }

}
</style>
