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
          <div class="stat-icon primary"><i class="fas fa-receipt"></i></div>
          <div class="stat-info">
            <span class="label">Pieces</span>
            <span class="value info">{{ filteredEntries.length }}</span>
          </div>
        </div>
      </div>

      <div class="accounting-summary card">
        <div class="accounting-summary-main">
          <span class="summary-eyebrow">Journal</span>
          <h2>Suivi comptable par piece justificative</h2>
          <p>Chaque ecriture est ordonnee chronologiquement. Le numero de piece justificative suit l'ordre  des operations comptables valides.</p>
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

      <div class="table-container card">
        <div class="ledger-head">
          <div>
            <h2 class="table-title">Grand livre comptable</h2>
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
                <td class="amount-cell text-success">{{ entry.recette > 0 ? formatMoney(entry.recette) : '-' }}</td>
                <td class="amount-cell text-danger">{{ entry.depense > 0 ? formatMoney(entry.depense) : '-' }}</td>
                <td class="amount-cell" :class="entry.balance >= 0 ? 'text-success' : 'text-danger'">{{ formatMoney(entry.balance) }}</td>
              </tr>
              <tr v-if="filteredEntries.length === 0">
                <td colspan="8" class="empty-cell">Aucune ecriture comptable sur cette periode.</td>
              </tr>
            </template>
          </tbody>
          <tfoot v-if="!isLoading && filteredEntries.length">
            <tr class="table-total-row">
              <td colspan="5">Totaux de la periode</td>
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
        recette: toNumber(payment?.amount),
        depense: 0,
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
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
:global(html[data-admin-theme="dark"]) .summary-chip,
:global(html[data-admin-theme="dark"]) .ledger-card,
:global(html[data-admin-theme="dark"]) .table-total-row td {
  background: rgba(15, 23, 42, 0.82);
  border-color: rgba(51, 65, 85, 0.95);
}

:global(html[data-admin-theme="dark"]) .page-header p,
:global(html[data-admin-theme="dark"]) .filter-range-note,
:global(html[data-admin-theme="dark"]) .ledger-subtitle,
:global(html[data-admin-theme="dark"]) .accounting-summary-main p,
:global(html[data-admin-theme="dark"]) .current-balance-chip span,
:global(html[data-admin-theme="dark"]) .summary-chip-label,
:global(html[data-admin-theme="dark"]) .accounting-table .cell-sub,
:global(html[data-admin-theme="dark"]) .actor-hint,
:global(html[data-admin-theme="dark"]) .stat-info .label {
  color: #cbd5e1;
}

:global(html[data-admin-theme="dark"]) .page-header h1,
:global(html[data-admin-theme="dark"]) .accounting-summary-main h2,
:global(html[data-admin-theme="dark"]) .current-balance-chip strong,
:global(html[data-admin-theme="dark"]) .stat-info .value,
:global(html[data-admin-theme="dark"]) .summary-chip strong,
:global(html[data-admin-theme="dark"]) .accounting-table .cell-main,
:global(html[data-admin-theme="dark"]) .actor-name {
  color: #f8fafc;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .accounting-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 992px) {
  .filters-panel {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .stats-grid,
  .filters-panel {
    grid-template-columns: 1fr;
  }
}
</style>
