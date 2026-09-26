<template>
  <div class="treasury-page">
    <div class="page-header">
      <div>
        <h1>Tresorerie Banque et Caisse</h1>
        <p>Cash provisioning, Bank vers Caisse, depot Caisse vers Bank, suivi des soldes.</p>
      </div>
      <div class="header-actions">
        <div class="actions-dropdown" :ref="el => setHeaderMenuRef(el)">
          <button class="btn btn-primary btn-sm admin-head-btn header-new-btn" @click.stop="toggleHeaderMenu">
            <i class="fas fa-plus"></i><span class="btn-label">Nouvelle opération</span><i class="fas fa-chevron-down header-caret" :class="{ open: openHeaderMenu }"></i>
          </button>
          <div v-if="openHeaderMenu" class="actions-menu header-menu" @click.stop>
            <button class="actions-item" @click="openOperationModal('funding')"><span class="action-ico ico-green"><i class="fas fa-plus"></i></span><span class="action-txt">Approvisionner<small>Cash externe vers un compte</small></span></button>
            <button class="actions-item" @click="openTransferModal('bank_to_caisse')"><span class="action-ico ico-blue"><i class="fas fa-building-columns"></i></span><span class="action-txt">Bank vers Caisse<small>Approvisonner la caisse</small></span></button>
            <button class="actions-item" @click="openTransferModal('caisse_to_bank')"><span class="action-ico ico-amber"><i class="fas fa-cash-register"></i></span><span class="action-txt">Caisse vers Bank<small>Déposer le cash en banque</small></span></button>
            <div class="actions-divider"></div>
            <button class="actions-item" @click="openAccountModal()"><span class="action-ico ico-dark"><i class="fas fa-university"></i></span><span class="action-txt">Gérer les comptes<small>Caisse / Banque, solde initial</small></span></button>
          </div>
        </div>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-wallet"></i></div>
        <div class="stat-info"><span class="stat-label">Tresorerie totale</span><span class="stat-value">{{ formatMoney(totalBalance) }}</span></div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-cash-register"></i></div>
        <div class="stat-info"><span class="stat-label">Total Caisses</span><span class="stat-value">{{ formatMoney(caisseBalance) }}</span></div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-building-columns"></i></div>
        <div class="stat-info"><span class="stat-label">Total Banques</span><span class="stat-value">{{ formatMoney(banqueBalance) }}</span></div>
      </div>
    </div>

    <div class="card section-card">
      <div class="section-header"><h2>Comptes</h2><span class="muted">{{ accounts.length }} compte(s)</span></div>
      <div class="accounts-grid">
        <div v-for="account in accounts" :key="account.id" class="account-card" :class="account.kind">
          <div class="account-top">
            <div>
              <div class="account-name">{{ account.name }} ({{ account.kind }})</div>
              <div v-if="account.bank_name" class="account-sub">{{ account.bank_name }} {{ account.account_number }}</div>
            </div>
            <div class="actions-dropdown" :ref="el => setAccountMenuRef(el, account.id)">
              <button class="btn-icon account-menu-btn" :class="{ active: openAccountMenuId === account.id }" title="Actions" aria-label="Actions du compte" @click.stop="toggleAccountMenu(account.id)">
                <i class="fas fa-ellipsis-v"></i>
              </button>
              <div v-if="openAccountMenuId === account.id" class="actions-menu account-menu" @click.stop>
                <div class="actions-menu-head">{{ account.name }}<span>{{ account.kind === 'banque' ? formatBankIdentity(account) || 'Compte banque' : 'Caisse' }}</span></div>
                <button class="actions-item" @click="openOperationModal('funding', account)"><span class="action-ico ico-green"><i class="fas fa-plus"></i></span><span class="action-txt">Approvisionner<small>Cash externe vers ce compte</small></span></button>
                <button class="actions-item" @click="openTransferModal('bank_to_caisse', account)"><span class="action-ico ico-blue"><i class="fas fa-building-columns"></i></span><span class="action-txt">Bank vers Caisse<small>Depuis une banque vers ici</small></span></button>
                <button class="actions-item" @click="openTransferModal('caisse_to_bank', account)"><span class="action-ico ico-amber"><i class="fas fa-cash-register"></i></span><span class="action-txt">Caisse vers Bank<small>Déposer vers une banque</small></span></button>
                <div class="actions-divider"></div>
                <button class="actions-item" @click="openAccountModal(account)"><span class="action-ico ico-dark"><i class="fas fa-pen"></i></span><span class="action-txt">Modifier<small>Nom, banque, solde initial</small></span></button>
              </div>
            </div>
          </div>
          <div class="account-balance">{{ formatMoney(account.current_balance) }}</div>
        </div>
        <div v-if="!loading && accounts.length === 0" class="empty-cell">Aucun compte. Creez une Caisse et une Banque.</div>
      </div>
    </div>
    <div class="controls card">
      <div class="controls-top">
        <div class="search-wrapper">
          <i class="fas fa-search search-icon"></i>
          <input v-model="search" type="text" class="search-input-clean" placeholder="Rechercher code, intitule, reference..." />
        </div>
        <button class="btn btn-sm" @click="resetFilters"><i class="fas fa-redo"></i> Reinitialiser</button>
      </div>
      <div class="filters-panel">
        <select v-model="typeFilter" class="filter-select-clean">
          <option value="">Tous les types</option>
          <option value="funding">Approvisionnements</option>
          <option value="transfer">Transferts internes</option>
          <option value="withdrawal">Retraits</option>
        </select>
        <select v-model="accountFilter" class="filter-select-clean">
          <option value="">Tous les comptes</option>
          <option v-for="a in accounts" :key="a.id" :value="String(a.id)">{{ a.name }}</option>
        </select>
        <select v-model="statusFilter" class="filter-select-clean">
          <option value="">Tous les statuts</option>
          <option value="paid">Valide</option>
          <option value="pending">En attente</option>
        </select>
      </div>
    </div>

    <div class="card table-card">
      <div class="section-header">
        <h2>Journal des mouvements</h2>
        <AdminAppTablePagination :start="opsStartIndex" :end="opsEndIndex" :total="opsTotalItems" :can-prev="canOpsPrev" :can-next="canOpsNext" :disabled="loading" @prev="opsPrevPage" @next="opsNextPage" />
      </div>
      <div class="table-container">
        <table class="admin-table">
          <thead><tr><th>Code</th><th>Date</th><th>Type</th><th>Intitule</th><th>Mouvement</th><th>Banque / Compte</th><th>Montant</th><th>Statut</th><th>Actions</th></tr></thead>
          <tbody>
            <template v-if="loading"><tr v-for="n in 5" :key="n"><td v-for="c in 9" :key="c"><div class="skeleton-line skeleton-w-60"></div></td></tr></template>
            <template v-else>
              <tr v-for="op in paginatedOps" :key="op.id">
                <td><code>{{ op.code || '-' }}</code></td>
                <td>{{ formatDisplayDate(op.date) }}</td>
                <td><span class="badge" :class="typeBadge(op.operation_type)">{{ directionLabel(op) }}</span></td>
                <td><div class="cell-main">{{ op.label }}</div><div v-if="op.reference" class="cell-sub">Ref: {{ op.reference }}</div></td>
                <td><div class="cell-main">{{ movementLabel(op) }}</div><div class="cell-sub">{{ op.created_by_name || '-' }}</div></td>
                <td><div class="cell-main">{{ op.bank_display || bankLabelForOp(op) || '-' }}</div><div v-if="op.bank_display || bankLabelForOp(op)" class="cell-sub">Banque / N° compte</div></td>
                <td class="amount-cell text-success">{{ formatMoney(op.amount) }}</td>
                <td><span class="badge" :class="op.status === 'paid' ? 'badge-success' : 'badge-warning'">{{ op.status === 'paid' ? 'Valide' : 'En attente' }}</span></td>
                <td class="actions-cell">
                  <div class="actions-dropdown" :ref="el => setOpMenuRef(el, op.id)">
                    <button class="btn btn-sm btn-outline" title="Actions" aria-label="Actions de l'opération" @click.stop="toggleOpMenu(op.id)"><i class="fas fa-ellipsis-v"></i></button>
                    <div v-if="openOpMenuId === op.id" class="actions-menu" @click.stop>
                      <button class="actions-item" @click="openOperationModal(op.operation_type, null, op)"><i class="fas fa-pen"></i> Modifier</button>
                      <button class="actions-item danger" @click="askDelete(op)"><i class="fas fa-trash"></i> Supprimer</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredOps.length === 0"><td colspan="9" class="empty-cell">Aucune operation.</td></tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
    <AdminAppModal v-model="showAccountModal" title="Compte Banque / Caisse" width="560px">
      <form class="admin-form" @submit.prevent="saveAccount">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Nom du compte *</label><input v-model="accountForm.name" class="form-input" required /></div>
          <div class="form-group"><label class="form-label">Type *</label><select v-model="accountForm.kind" class="form-select"><option value="caisse">Caisse</option><option value="banque">Banque</option></select></div>
        </div>
        <div v-if="accountForm.kind === 'banque'" class="form-grid">
          <div class="form-group"><label class="form-label">Banque *</label><input v-model="accountForm.bank_name" class="form-input" /></div>
          <div class="form-group"><label class="form-label">N° compte</label><input v-model="accountForm.account_number" class="form-input" /></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Solde initial (Fbu)</label><input v-model="accountInitialInput" class="form-input" /></div>
          <div class="form-group"><label class="form-label">Statut</label><select v-model="accountForm.is_active" class="form-select"><option :value="true">Actif</option><option :value="false">Inactif</option></select></div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showAccountModal = false">Annuler</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveAccount">Enregistrer</button>
      </template>
    </AdminAppModal>


    <AdminAppModal v-model="showOperationModal" :title="operationModalTitle" width="640px">
      <form class="admin-form" @submit.prevent="saveOperation">
        <div v-if="transferDirection" class="booking-summary">{{ transferHint }}</div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Type *</label><select v-model="opForm.operation_type" class="form-select" @change="onOpTypeChange"><option value="funding">Approvisionnement (Cash provisioning)</option><option value="transfer">Transfert Bank / Caisse</option><option value="withdrawal">Retrait</option></select></div>
          <div class="form-group"><label class="form-label">Date *</label><input v-model="opForm.date" type="date" class="form-input" required /></div>
        </div>
        <div v-if="opForm.operation_type === 'transfer'" class="form-grid">
          <div class="form-group"><label class="form-label">Sens du transfert *</label><select v-model="transferDirection" class="form-select" @change="onTransferDirectionChange"><option value="bank_to_caisse">Bank vers Caisse (approvisionner la caisse)</option><option value="caisse_to_bank">Caisse vers Bank (depot en banque)</option></select></div>
          <div class="form-group"><label class="form-label">Source Bank</label><input :value="bankOptionLabel(findAccount(opForm.from_account)) || '—'" class="form-input" readonly /></div>
        </div>
        <div class="form-grid">
          <div v-if="opForm.operation_type !== 'funding'" class="form-group"><label class="form-label">{{ sourceLabel }} *</label><select v-model="opForm.from_account" class="form-select" @change="onSourceAccountChange"><option :value="null">Choisir</option><option v-for="a in sourceAccountOptions" :key="a.id" :value="a.id">{{ accountOptionLabel(a) }}</option></select></div>
          <div v-if="opForm.operation_type !== 'withdrawal'" class="form-group"><label class="form-label">{{ destinationLabel }} *</label><select v-model="opForm.to_account" class="form-select" @change="onDestinationAccountChange"><option :value="null">Choisir</option><option v-for="a in destinationAccountOptions" :key="a.id" :value="a.id">{{ accountOptionLabel(a) }}</option></select></div>
        </div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Nom de la banque</label><input v-model="opForm.bank_name" class="form-input" placeholder="Ex: BCB, KCB, Equity..." /></div>
          <div class="form-group"><label class="form-label">Numero de compte</label><input v-model="opForm.account_number" class="form-input" placeholder="Ex: 001234567890" /></div>
        </div>
        <div class="form-group"><label class="form-label">Montant (Fbu) *</label><input v-model="opAmountInput" class="form-input" required /></div>
        <div class="form-group"><label class="form-label">Intitule *</label><input v-model="opForm.label" class="form-input" required /></div>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Reference</label><input v-model="opForm.reference" class="form-input" /></div>
          <div class="form-group"><label class="form-label">Statut</label><select v-model="opForm.status" class="form-select"><option value="paid">Valide</option><option value="pending">En attente</option></select></div>
        </div>
        <div v-if="operationImpact" class="booking-summary">{{ operationImpact }}</div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showOperationModal = false">Annuler</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveOperation">Enregistrer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="420px">
      <p>Supprimer l'operation ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" :disabled="saving" @click="deleteOperation">Supprimer</button>
      </template>
    </AdminAppModal>
  </div>
</template>
<script setup>
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useDateFormat } from '~/composables/useDateFormat'
import { notify } from '~/composables/useNotification'
definePageMeta({ layout: 'admin' })
const { formatMoney, parseMoney, moneyInputModel } = useMoney()
const { formatDisplayDate } = useDateFormat()
const accounts = ref([])
const operations = ref([])
const loading = ref(false)
const saving = ref(false)
const search = ref('')
const typeFilter = ref('')
const accountFilter = ref('')
const statusFilter = ref('')
const showAccountModal = ref(false)
const showOperationModal = ref(false)
const showDeleteModal = ref(false)
const editingAccountId = ref(null)
const editingOpId = ref(null)
const selectedOp = ref(null)
const openAccountMenuId = ref(null)
const openOpMenuId = ref(null)
const openHeaderMenu = ref(false)
const accountMenuRefs = new Map()
const opMenuRefs = new Map()
let headerMenuRef = null
const toggleAccountMenu = (id) => { openAccountMenuId.value = openAccountMenuId.value === id ? null : id; if (openAccountMenuId.value) { openOpMenuId.value = null; openHeaderMenu.value = false } }
const toggleOpMenu = (id) => { openOpMenuId.value = openOpMenuId.value === id ? null : id; if (openOpMenuId.value) { openAccountMenuId.value = null; openHeaderMenu.value = false } }
const toggleHeaderMenu = () => { openHeaderMenu.value = !openHeaderMenu.value; if (openHeaderMenu.value) { openAccountMenuId.value = null; openOpMenuId.value = null } }
const closeAllMenus = () => { openAccountMenuId.value = null; openOpMenuId.value = null; openHeaderMenu.value = false }
const setAccountMenuRef = (el, id) => { if (el) accountMenuRefs.set(Number(id), el); else accountMenuRefs.delete(Number(id)) }
const setOpMenuRef = (el, id) => { if (el) opMenuRefs.set(Number(id), el); else opMenuRefs.delete(Number(id)) }
const setHeaderMenuRef = (el) => { headerMenuRef = el || null }
const handleDocumentClick = (event) => {
  const target = event?.target
  if (!(target instanceof Element)) { closeAllMenus(); return }
  if (headerMenuRef && headerMenuRef.contains(target)) return
  for (const el of [...accountMenuRefs.values(), ...opMenuRefs.values()]) {
    if (el && el.contains(target)) return
  }
  closeAllMenus()
}
const accountForm = ref({ name: '', kind: 'caisse', bank_name: '', account_number: '', initial_balance: 0, is_active: true })
const accountInitialInput = moneyInputModel(accountForm, 'initial_balance')
const opForm = ref({ operation_type: 'funding', date: new Date().toISOString().slice(0, 10), from_account: null, to_account: null, amount: 0, reference: '', label: '', bank_name: '', account_number: '', notes: '', status: 'paid' })
const opAmountInput = moneyInputModel(opForm, 'amount')
const activeAccounts = computed(() => accounts.value.filter(a => a.is_active))
const bankAccounts = computed(() => activeAccounts.value.filter(a => a.kind === 'banque'))
const caisseAccounts = computed(() => activeAccounts.value.filter(a => a.kind === 'caisse'))
const transferDirection = ref('')
const toNumber = (v) => Number(v || 0)
const totalBalance = computed(() => accounts.value.reduce((s, a) => s + toNumber(a.current_balance), 0))
const caisseBalance = computed(() => accounts.value.filter(a => a.kind === 'caisse').reduce((s, a) => s + toNumber(a.current_balance), 0))
const banqueBalance = computed(() => accounts.value.filter(a => a.kind === 'banque').reduce((s, a) => s + toNumber(a.current_balance), 0))
const typeLabel = (t) => t === 'funding' ? 'Approvisionnement' : t === 'transfer' ? 'Transfert' : 'Retrait'
const typeBadge = (t) => t === 'funding' ? 'badge-success' : t === 'transfer' ? 'badge-info' : 'badge-warning'
const accountName = (id) => accounts.value.find(a => Number(a.id) === Number(id))?.name || '-'
const findAccount = (id) => accounts.value.find(a => Number(a.id) === Number(id)) || null
const formatBankIdentity = (account) => {
  const bank = String(account?.bank_name || '').trim()
  const number = String(account?.account_number || '').trim()
  if (bank && number) return `${bank} — ${number}`
  return bank || number || ''
}
const accountOptionLabel = (account) => {
  if (!account) return '— Choisir —'
  const identity = formatBankIdentity(account)
  const kindTag = account.kind === 'banque' ? 'Banque' : 'Caisse'
  const base = String(account.name || '').trim() || kindTag
  if (account.kind === 'banque') {
    const bankId = identity || base
    return `${bankId} (${formatMoney(account.current_balance)})`
  }
  return identity ? `${base} — ${identity} (${formatMoney(account.current_balance)})` : `${base} (${formatMoney(account.current_balance)})`
}
const bankOptionLabel = (account) => {
  if (!account) return '—'
  const identity = formatBankIdentity(account)
  if (identity) return identity
  const fallback = String(account.name || '').trim()
  return fallback || 'Banque'
}
const bankLabelForOp = (op) => {
  if (op?.bank_display) return String(op.bank_display)
  if (String(op?.to_account_kind || '') === 'banque') {
    const label = formatBankIdentity(findAccount(op.to_account))
    if (label) return label
  }
  if (String(op?.from_account_kind || '') === 'banque') {
    const label = formatBankIdentity(findAccount(op.from_account))
    if (label) return label
  }
  const toLabel = formatBankIdentity(findAccount(op?.to_account))
  const fromLabel = formatBankIdentity(findAccount(op?.from_account))
  if (op?.operation_type === 'funding') return toLabel || fromLabel
  if (op?.operation_type === 'transfer') return toLabel && fromLabel ? `${fromLabel} → ${toLabel}` : (toLabel || fromLabel)
  return fromLabel || toLabel
}
const sourceLabel = computed(() => {
  if (opForm.value.operation_type === 'transfer') return transferDirection.value === 'caisse_to_bank' ? 'Caisse source' : 'Source Bank'
  return 'Compte source'
})
const destinationLabel = computed(() => {
  if (opForm.value.operation_type === 'transfer') return transferDirection.value === 'caisse_to_bank' ? 'Bank destinataire' : 'Caisse destinataire'
  return 'Compte destinataire'
})
const sourceAccountOptions = computed(() => {
  if (opForm.value.operation_type !== 'transfer' || !transferDirection.value) return activeAccounts.value
  return transferDirection.value === 'caisse_to_bank' ? caisseAccounts.value : bankAccounts.value
})
const destinationAccountOptions = computed(() => {
  if (opForm.value.operation_type !== 'transfer' || !transferDirection.value) return activeAccounts.value
  return transferDirection.value === 'caisse_to_bank' ? bankAccounts.value : caisseAccounts.value
})
const transferHint = computed(() => {
  if (opForm.value.operation_type !== 'transfer' || !transferDirection.value) return ''
  return transferDirection.value === 'bank_to_caisse'
    ? 'Cash provisioning / Bank vers Caisse : sortir de la banque pour alimenter la caisse.'
    : 'Bank deposit / Caisse vers Bank : deposer le cash de la caisse vers la banque.'
})
const directionLabel = (op) => {
  if (op?.operation_type !== 'transfer') return typeLabel(op?.operation_type)
  const fromKind = String(op?.from_account_kind || findAccount(op?.from_account)?.kind || '')
  const toKind = String(op?.to_account_kind || findAccount(op?.to_account)?.kind || '')
  if (fromKind === 'banque' && toKind === 'caisse') return 'Bank → Caisse'
  if (fromKind === 'caisse' && toKind === 'banque') return 'Caisse → Bank'
  return 'Transfert'
}
const movementLabel = (op) => {
  if (op.operation_type === 'funding') return `Externe vers ${op.to_account_name || accountName(op.to_account)}`
  if (op.operation_type === 'transfer') return `${op.from_account_name || accountName(op.from_account)} vers ${op.to_account_name || accountName(op.to_account)}`
  return `${op.from_account_name || accountName(op.from_account)} vers sortie`
}
const operationModalTitle = computed(() => {
  if (editingOpId.value) return "Modifier l'operation"
  if (opForm.value.operation_type === 'transfer') return transferDirection.value === 'caisse_to_bank' ? 'Depot Caisse vers Bank' : 'Cash provisioning Bank vers Caisse'
  return 'Approvisionner Banque / Caisse'
})
const operationImpact = computed(() => {
  const amount = toNumber(opForm.value.amount)
  if (!amount) return ''
  if (opForm.value.operation_type === 'funding' && opForm.value.to_account) return `+ ${formatMoney(amount)} sur ${accountName(opForm.value.to_account)}`
  if (opForm.value.operation_type === 'transfer' && opForm.value.from_account && opForm.value.to_account) return `${formatMoney(amount)} : ${accountName(opForm.value.from_account)} vers ${accountName(opForm.value.to_account)}`
  if (opForm.value.operation_type === 'withdrawal' && opForm.value.from_account) return `- ${formatMoney(amount)} sur ${accountName(opForm.value.from_account)}`
  return ''
})
const filteredOps = computed(() => {
  const q = search.value.trim().toLowerCase()
  return operations.value.filter((op) => {
    if (typeFilter.value && op.operation_type !== typeFilter.value) return false
    if (statusFilter.value && op.status !== statusFilter.value) return false
    if (accountFilter.value && String(op.from_account) !== String(accountFilter.value) && String(op.to_account) !== String(accountFilter.value)) return false
    if (!q) return true
    return [op.code, op.label, op.reference].some(v => String(v || '').toLowerCase().includes(q))
  }).sort((a, b) => String(b.date || '').localeCompare(String(a.date || '')) || Number(b.id || 0) - Number(a.id || 0))
})
const { currentPage: opsPage, totalPages: opsTotalPages, paginatedItems: paginatedOps, startIndex: opsStartIndex, endIndex: opsEndIndex, totalItems: opsTotalItems, canPrev: canOpsPrev, canNext: canOpsNext, prevPage: opsPrevPage, nextPage: opsNextPage } = usePagination(filteredOps, 10)
const resetFilters = () => { search.value = ''; typeFilter.value = ''; accountFilter.value = ''; statusFilter.value = '' }
const fetchAll = async () => {
  loading.value = true
  try {
    const [accRes, opRes] = await Promise.all([api.get('treasury-accounts/'), api.get('treasury-operations/')])
    accounts.value = Array.isArray(accRes.data) ? accRes.data : []
    operations.value = Array.isArray(opRes.data) ? opRes.data : []
  } catch { notify('Erreur chargement tresorerie', 'danger') }
  finally { loading.value = false }
}
const openAccountModal = (account = null) => {
  closeAllMenus()
  editingAccountId.value = account?.id || null
  accountForm.value = account ? { name: account.name, kind: account.kind, bank_name: account.bank_name || '', account_number: account.account_number || '', initial_balance: toNumber(account.initial_balance), is_active: account.is_active !== false } : { name: '', kind: 'caisse', bank_name: '', account_number: '', initial_balance: 0, is_active: true }
  showAccountModal.value = true
}
const saveAccount = async () => {
  if (!String(accountForm.value.name || '').trim()) { notify('Nom requis', 'danger'); return }
  saving.value = true
  try {
    const payload = { ...accountForm.value, name: String(accountForm.value.name).trim(), initial_balance: parseMoney(accountForm.value.initial_balance) }
    if (editingAccountId.value) await api.patch(`treasury-accounts/${editingAccountId.value}/`, payload)
    else await api.post('treasury-accounts/', payload)
    showAccountModal.value = false
    notify('Compte enregistre', 'success')
    await fetchAll()
  } catch { notify('Erreur enregistrement', 'danger') }
  finally { saving.value = false }
}
const openOperationModal = (type = 'funding', presetAccount = null, existing = null) => {
  closeAllMenus()
  editingOpId.value = existing?.id || null
  transferDirection.value = ''
  if (existing) {
    opForm.value = { operation_type: existing.operation_type, date: String(existing.date || '').slice(0, 10), from_account: existing.from_account || null, to_account: existing.to_account || null, amount: toNumber(existing.amount), reference: existing.reference || '', label: existing.label || '', bank_name: existing.bank_name || '', account_number: existing.account_number || '', notes: existing.notes || '', status: existing.status || 'paid' }
    if (existing.operation_type === 'transfer') {
      const fromKind = String(existing.from_account_kind || findAccount(existing.from_account)?.kind || '')
      const toKind = String(existing.to_account_kind || findAccount(existing.to_account)?.kind || '')
      transferDirection.value = (fromKind === 'caisse' && toKind === 'banque') ? 'caisse_to_bank' : 'bank_to_caisse'
    }
  } else {
    opForm.value = { operation_type: type, date: new Date().toISOString().slice(0, 10), from_account: null, to_account: presetAccount?.id || null, amount: 0, reference: '', label: '', bank_name: '', account_number: '', notes: '', status: 'paid' }
    if (type === 'transfer') {
      transferDirection.value = 'bank_to_caisse'
      applyTransferDirection(presetAccount)
    }
  }
  showOperationModal.value = true
}
const applyTransferDirection = (presetAccount = null) => {
  const preset = presetAccount || null
  const presetKind = String(preset?.kind || '')
  if (transferDirection.value === 'bank_to_caisse') {
    opForm.value.from_account = presetKind === 'banque' ? (preset?.id || null) : (bankAccounts.value[0]?.id || opForm.value.from_account || null)
    opForm.value.to_account = presetKind === 'caisse' ? (preset?.id || null) : (caisseAccounts.value[0]?.id || opForm.value.to_account || null)
    const source = findAccount(opForm.value.from_account)
    if (source) {
      if (!String(opForm.value.bank_name || '').trim()) opForm.value.bank_name = source.bank_name || ''
      if (!String(opForm.value.account_number || '').trim()) opForm.value.account_number = source.account_number || ''
    }
    if (!String(opForm.value.label || '').trim()) opForm.value.label = 'Cash provisioning Bank vers Caisse'
  } else if (transferDirection.value === 'caisse_to_bank') {
    opForm.value.from_account = presetKind === 'caisse' ? (preset?.id || null) : (caisseAccounts.value[0]?.id || opForm.value.from_account || null)
    opForm.value.to_account = presetKind === 'banque' ? (preset?.id || null) : (bankAccounts.value[0]?.id || opForm.value.to_account || null)
    const destination = findAccount(opForm.value.to_account)
    if (destination) {
      if (!String(opForm.value.bank_name || '').trim()) opForm.value.bank_name = destination.bank_name || ''
      if (!String(opForm.value.account_number || '').trim()) opForm.value.account_number = destination.account_number || ''
    }
    if (!String(opForm.value.label || '').trim()) opForm.value.label = 'Depot Caisse vers Bank'
  }
}
const openTransferModal = (direction = 'bank_to_caisse', presetAccount = null) => {
  closeAllMenus()
  transferDirection.value = direction
  editingOpId.value = null
  opForm.value = { operation_type: 'transfer', date: new Date().toISOString().slice(0, 10), from_account: null, to_account: null, amount: 0, reference: '', label: '', bank_name: '', account_number: '', notes: '', status: 'paid' }
  applyTransferDirection(presetAccount)
  showOperationModal.value = true
}
const onOpTypeChange = () => {
  if (opForm.value.operation_type === 'transfer' && !transferDirection.value) {
    transferDirection.value = 'bank_to_caisse'
    applyTransferDirection()
  }
  if (opForm.value.operation_type !== 'transfer') transferDirection.value = ''
}
const onTransferDirectionChange = () => { applyTransferDirection() }
const onSourceAccountChange = () => {
  if (opForm.value.operation_type !== 'transfer') return
  const source = findAccount(opForm.value.from_account)
  if (!source) return
  if (transferDirection.value === 'bank_to_caisse' && String(source.kind) === 'banque') {
    opForm.value.bank_name = source.bank_name || opForm.value.bank_name
    opForm.value.account_number = source.account_number || opForm.value.account_number
  }
  if (transferDirection.value === 'caisse_to_bank' && String(source.kind) === 'caisse' && !String(opForm.value.label || '').trim()) {
    opForm.value.label = 'Depot Caisse vers Bank'
  }
}
const onDestinationAccountChange = () => {
  if (opForm.value.operation_type !== 'transfer') return
  const destination = findAccount(opForm.value.to_account)
  if (!destination) return
  if (transferDirection.value === 'caisse_to_bank' && String(destination.kind) === 'banque') {
    opForm.value.bank_name = destination.bank_name || opForm.value.bank_name
    opForm.value.account_number = destination.account_number || opForm.value.account_number
  }
  if (transferDirection.value === 'bank_to_caisse' && String(destination.kind) === 'caisse' && !String(opForm.value.label || '').trim()) {
    opForm.value.label = 'Cash provisioning Bank vers Caisse'
  }
}
const saveOperation = async () => {
  const amount = parseMoney(opForm.value.amount)
  if (!amount || amount <= 0) { notify('Montant invalide', 'danger'); return }
  if (opForm.value.operation_type === 'funding' && !opForm.value.to_account) { notify('Choisissez le compte', 'danger'); return }
  if (opForm.value.operation_type === 'transfer') {
    if (!transferDirection.value) { notify('Choisissez le sens du transfert', 'danger'); return }
    if (!opForm.value.from_account || !opForm.value.to_account) { notify('Choisissez la Bank source et la Caisse / Bank destinataire', 'danger'); return }
    if (Number(opForm.value.from_account) === Number(opForm.value.to_account)) { notify('Comptes differents requis', 'danger'); return }
    const srcKind = String(findAccount(opForm.value.from_account)?.kind || '')
    const dstKind = String(findAccount(opForm.value.to_account)?.kind || '')
    if (!((srcKind === 'banque' && dstKind === 'caisse') || (srcKind === 'caisse' && dstKind === 'banque'))) { notify('Transfert autorise uniquement Bank vers Caisse ou Caisse vers Bank', 'danger'); return }
  }
  saving.value = true
  try {
    const payload = { ...opForm.value, amount, from_account: opForm.value.from_account || null, to_account: opForm.value.to_account || null, bank_name: String(opForm.value.bank_name || '').trim(), account_number: String(opForm.value.account_number || '').trim() }
    if (editingOpId.value) await api.patch(`treasury-operations/${editingOpId.value}/`, payload)
    else await api.post('treasury-operations/', payload)
    showOperationModal.value = false
    notify('Operation enregistree', 'success')
    await fetchAll()
  } catch { notify('Erreur operation', 'danger') }
  finally { saving.value = false }
}
const askDelete = (op) => { closeAllMenus(); selectedOp.value = op; showDeleteModal.value = true }
const deleteOperation = async () => {
  if (!selectedOp.value) return
  saving.value = true
  try {
    await api.delete(`treasury-operations/${selectedOp.value.id}/`)
    showDeleteModal.value = false
    notify('Operation supprimee', 'success')
    await fetchAll()
  } catch { notify('Suppression impossible', 'danger') }
  finally { saving.value = false }
}
onMounted(fetchAll)
onMounted(() => {
  if (process.client) document.addEventListener('click', handleDocumentClick)
})
onBeforeUnmount(() => {
  if (process.client) document.removeEventListener('click', handleDocumentClick)
})
</script>
<style scoped>
.treasury-page { padding: 0; }
.page-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.page-header h1 { font-size: 1.75rem; margin: 0 0 6px; }
.page-header p { margin: 0; color: var(--gray-500); }
.header-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 20px; }
.stat-card { display: flex; align-items: center; gap: 14px; padding: 18px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.warning { background: #fffbeb; color: #d97706; }
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-label { display: block; font-size: 0.7rem; color: #94a3b8; font-weight: 700; text-transform: uppercase; }
.stat-value { display: block; font-size: 1.25rem; font-weight: 800; }
.section-card { margin-bottom: 20px; }
.section-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 14px; }
.section-header h2 { margin: 0; font-size: 1.1rem; }
.muted { color: var(--gray-500); font-size: 0.85rem; }
.accounts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 14px; }
.account-card { border: 1px solid var(--gray-200); border-radius: 16px; padding: 16px; background: var(--gray-50); display: grid; gap: 8px; }
.account-card.banque { border-left: 5px solid #0ea5e9; }
.account-card.caisse { border-left: 5px solid #d97706; }
.account-name { font-weight: 800; }
.account-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.account-menu-btn { width: 34px; height: 34px; border: 1px solid var(--gray-200); border-radius: 10px; background: var(--white); color: var(--gray-500); display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.account-menu-btn:hover, .account-menu-btn.active { color: var(--gray-900); border-color: var(--gray-300); background: var(--gray-50); }
.actions-dropdown { position: relative; display: inline-flex; }
.actions-menu { position: absolute; top: calc(100% + 8px); right: 0; min-width: 250px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16); padding: 6px; z-index: 30; overflow: hidden; animation: menu-pop 0.16s ease-out; }
.header-menu { min-width: 300px; }
.account-menu { min-width: 280px; }
.actions-item { width: 100%; display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 10px; color: #0f172a; font-weight: 700; font-size: 0.9rem; text-align: left; background: transparent; border: 0; cursor: pointer; transition: background 0.15s ease, transform 0.15s ease; }
.actions-item:hover { background: #f1f5f9; transform: translateX(2px); }
.actions-item i { width: 16px; text-align: center; color: #64748b; }
.actions-item.danger { color: #dc2626; }
.actions-item.danger i { color: #dc2626; }
.actions-item.danger:hover { background: #fef2f2; }
.action-ico { width: 38px; height: 38px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.95rem; flex-shrink: 0; }
.action-ico i { width: auto; color: inherit; }
.ico-green { color: #16a34a; border: 1px solid #bbf7d0; }
.ico-blue { color: #2563eb; border: 1px solid #bfdbfe; }
.ico-amber { color: #d97706; border: 1px solid #fde68a; }
.ico-dark { background: #0f172a; color: #fbbf24; border: 1px solid #1e293b; }
.action-txt { display: flex; flex-direction: column; line-height: 1.25; }
.action-txt small { font-weight: 600; font-size: 0.75rem; color: #64748b; }
.actions-divider { height: 1px; background: #e2e8f0; margin: 6px 4px; }
.actions-menu-head { padding: 10px 12px 8px; font-weight: 800; font-size: 0.85rem; color: #0f172a; display: flex; flex-direction: column; gap: 2px; border-bottom: 1px solid #f1f5f9; margin-bottom: 4px; }
.actions-menu-head span { font-weight: 600; font-size: 0.75rem; color: #64748b; }
.header-new-btn { gap: 8px; box-shadow: 0 10px 25px rgba(212, 175, 55, 0.35); }
.header-caret { font-size: 0.7rem; margin-left: 2px; transition: transform 0.18s ease; }
.header-caret.open { transform: rotate(180deg); }
@keyframes menu-pop { from { opacity: 0; transform: translateY(-6px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
.actions-cell { width: 1%; white-space: nowrap; }
.account-sub { color: var(--gray-500); font-size: 0.85rem; }
.account-balance { font-size: 1.3rem; font-weight: 900; }
.controls { margin-bottom: 20px; }
.controls-top { display: flex; gap: 12px; flex-wrap: wrap; }
.search-wrapper { position: relative; flex: 1; min-width: 260px; }
.search-icon { position: absolute; top: 50%; left: 14px; transform: translateY(-50%); color: var(--gray-400); }
.search-input-clean, .filter-select-clean, .form-input, .form-select { width: 100%; min-height: 46px; border-radius: 14px; border: 1px solid var(--gray-200); background: #fff; }
.search-input-clean { padding: 0 14px 0 42px; }
.filter-select-clean, .form-input, .form-select { padding: 0 14px; }
.filters-panel { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }
.cell-main { font-weight: 700; }
.cell-sub { color: var(--gray-500); font-size: 0.82rem; }
.amount-cell { font-weight: 800; }
.text-success { color: var(--success); }
.admin-form { display: grid; gap: 14px; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.form-label { display: block; font-weight: 700; font-size: 0.85rem; margin-bottom: 6px; }
.booking-summary { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 12px; font-weight: 700; color: #166534; }
@media (max-width: 640px) { .form-grid, .filters-panel { grid-template-columns: 1fr; } }
</style>