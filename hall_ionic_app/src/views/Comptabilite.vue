<template>
  <ion-page class="compta-page">
    <HeaderBar title="Comptabilité" eyebrow="Finances" :show-menu="false">
      <template v-slot:actions>
        <ion-button fill="clear" class="header-print-btn" @click="handlePrint">
          <Icon icon="solar:printer-linear" class="header-icon" />
        </ion-button>
      </template>
    </HeaderBar>

    <ion-content class="compta-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement des finances"
      />
      <div class="content-shell">

        <section class="compta-hero">
          <div class="hero-col">
            <small class="hero-eyebrow">{{ periodLabel }}</small>
            <h1 class="hero-title">Solde net</h1>
            <div class="hero-balance" :class="balanceTone">{{ balanceLabel }}</div>
          </div>
          <div class="hero-marks" aria-hidden="true">
            <div class="mark-row pos"><span class="mark-swatch in"></span><span>Entrées</span><span class="mark-val">{{ totals.entries }}</span></div>
            <div class="mark-row neg"><span class="mark-swatch out"></span><span>Sorties</span><span class="mark-val">{{ totals.expenses }}</span></div>
          </div>
        </section>

        <section class="balance-cards">
          <div class="bcard in">
            <div class="bcard-head">
              <Icon icon="solar:wallet-money-linear" class="bcard-icon" />
              <span class="bcard-kicker">Entrées du mois</span>
            </div>
            <div class="bcard-value">{{ totals.entries }}</div>
            <div class="bcard-sub">{{ entryCount }} paiement{{ entryCount > 1 ? 's' : '' }} enregistré{{ entryCount > 1 ? 's' : '' }}</div>
          </div>
          <div class="bcard out">
            <div class="bcard-head">
              <Icon icon="solar:bill-list-linear" class="bcard-icon" />
              <span class="bcard-kicker">Dépenses du mois</span>
            </div>
            <div class="bcard-value">{{ totals.expenses }}</div>
            <div class="bcard-sub">{{ expenseCount }} ligne{{ expenseCount > 1 ? 's' : '' }} • Matériel &amp; personnel</div>
          </div>
        </section>

        <section class="segment-shell">
          <ion-segment v-model="activeTab" class="compta-segment" :scrollable="false">
            <ion-segment-button value="expenses">
              <ion-label>
                <span class="seg-ic"><Icon icon="solar:minus-circle-linear" /></span>
                Dépenses
              </ion-label>
            </ion-segment-button>
            <ion-segment-button value="entries">
              <ion-label>
                <span class="seg-ic"><Icon icon="solar:add-circle-linear" /></span>
                Entrées / Paiements
              </ion-label>
            </ion-segment-button>
          </ion-segment>
        </section>

        <section v-if="activeTab === 'expenses'" class="list-block">
          <div class="sub-tabs">
            <button
              v-for="t in expenseTabs"
              :key="t.key"
              type="button"
              class="sub-tab"
              :class="{ active: activeExpenseTab === t.key }"
              @click="activeExpenseTab = t.key"
            >
              <Icon :icon="t.icon" class="sub-tab-ic" />
              <span>{{ t.label }}</span>
              <span class="sub-tab-count">{{ t.count }}</span>
            </button>
          </div>

          <div class="list-head-row">
            <div>
              <div class="list-kicker">Total Dépenses</div>
              <h2 class="list-title">{{ currentExpenseTotal }}</h2>
            </div>
          </div>
          <div class="list-hairline" aria-hidden="true"></div>

          <ul class="tx-list">
            <li v-for="tx in currentExpenses" :key="tx.id" class="tx-row-shell">
              <div class="tx-row">
                <span class="tx-icon out" :style="{ background: tx.iconBg, color: tx.iconColor }">
                  <Icon :icon="tx.icon" />
                </span>
                <span class="tx-copy">
                  <span class="tx-title">{{ tx.title }}</span>
                  <span class="tx-sub">
                    <span v-if="tx.category" class="tx-cat">{{ tx.category }}</span>
                    <span v-if="tx.date">{{ formatDate(tx.date) }}</span>
                    <span v-if="tx.person" class="tx-person">• {{ tx.person }}</span>
                  </span>
                </span>
                <span class="tx-amount out">- {{ tx.amount }}</span>
              </div>
              <div class="tx-actions">
                <button type="button" class="tx-action-btn view" @click.stop="toastView(tx)">
                  <Icon icon="solar:eye-linear" />
                  <span>Voir</span>
                </button>
                <button type="button" class="tx-action-btn edit" @click.stop="toastEdit(tx)">
                  <Icon icon="solar:pen-2-linear" />
                  <span>Modifier</span>
                </button>
                <button type="button" class="tx-action-btn delete" @click.stop="handleDeleteExpense(tx)">
                  <Icon icon="solar:trash-bin-minimalistic-linear" />
                  <span>Supprimer</span>
                </button>
              </div>
            </li>
            <li v-if="!currentExpenses.length" class="empty-state">
              <Icon icon="solar:inbox-linear" class="empty-ic" />
              <span>Aucune dépense pour ce groupe.</span>
            </li>
          </ul>
        </section>

        <section v-if="activeTab === 'entries'" class="list-block">
          <div class="sub-tabs">
            <button
              v-for="t in entryTabs"
              :key="t.key"
              type="button"
              class="sub-tab"
              :class="{ active: activeEntryTab === t.key }"
              @click="activeEntryTab = t.key"
            >
              <Icon :icon="t.icon" class="sub-tab-ic" />
              <span>{{ t.label }}</span>
              <span class="sub-tab-count">{{ t.count }}</span>
            </button>
          </div>

          <div class="list-head-row">
            <div>
              <div class="list-kicker">Total Entrées</div>
              <h2 class="list-title">{{ currentEntryTotal }}</h2>
            </div>
          </div>
          <div class="list-hairline" aria-hidden="true"></div>

          <ul class="tx-list">
            <li v-for="tx in currentEntries" :key="tx.id" class="tx-row-shell">
              <div class="tx-row">
                <span class="tx-icon in" :style="{ background: tx.iconBg, color: tx.iconColor }">
                  <Icon :icon="tx.icon" />
                </span>
                <span class="tx-copy">
                  <span class="tx-title">{{ tx.title }}</span>
                  <span class="tx-sub">
                    <span v-if="tx.booking_code" class="tx-cat">{{ tx.booking_code }}</span>
                    <span v-if="tx.date">{{ formatDate(tx.date) }}</span>
                    <span v-if="tx.method" class="tx-person">• {{ tx.method }}</span>
                  </span>
                </span>
                <span class="tx-amount in">+ {{ tx.amount }}</span>
              </div>
              <div class="tx-actions">
                <button type="button" class="tx-action-btn view" @click.stop="toastView(tx)">
                  <Icon icon="solar:eye-linear" />
                  <span>Voir</span>
                </button>
                <button type="button" class="tx-action-btn edit" @click.stop="toastEdit(tx)">
                  <Icon icon="solar:pen-2-linear" />
                  <span>Modifier</span>
                </button>
                <button type="button" class="tx-action-btn delete" @click.stop="handleDeletePayment(tx)">
                  <Icon icon="solar:trash-bin-minimalistic-linear" />
                  <span>Supprimer</span>
                </button>
              </div>
            </li>
            <li v-if="!currentEntries.length" class="empty-state">
              <Icon icon="solar:inbox-linear" class="empty-ic" />
              <span>Aucun paiement pour cette catégorie.</span>
            </li>
          </ul>
        </section>

        <div class="page-bottom-spacer" />
      </div>

      <ion-fab slot="fixed" vertical="bottom" horizontal="end" class="fab-shell">
        <ion-fab-button class="fab-main">
          <Icon icon="solar:add-linear" width="30" height="30" style="width:30px;height:30px;display:block" />
        </ion-fab-button>
        <ion-fab-list side="top">
          <ion-fab-button class="fab-sub green" @click="toastNewPayment">
            <Icon icon="solar:wallet-money-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button class="fab-sub red" @click="toastNewExpense">
            <Icon icon="solar:bill-list-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button class="fab-sub navy" @click="handlePrint">
            <Icon icon="solar:printer-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
        </ion-fab-list>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonContent, IonPage, IonSegment, IonSegmentButton, IonLabel, IonButton, IonFab, IonFabButton, IonFabList } from '@ionic/vue'
import HeaderBar from '@/components/HeaderBar.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { endpoints } from '@/lib/api.js'

const MOCK_EXPENSES = [
  { id: 'e1', group: 'expense', title: "Achat produits d'entretien", category: 'Fournitures', amount: 285000, date: '2026-06-25', person: 'Ménage', icon: 'solar:spray-bottle-linear', iconBg: 'rgba(239,68,68,0.10)', iconColor: '#ef4444' },
  { id: 'e2', group: 'expense', title: 'Facture ENEO (électricité)', category: 'Utilités', amount: 412000, date: '2026-06-22', person: 'Admin', icon: 'solar:bolt-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' },
  { id: 'e3', group: 'expense', title: 'Loyer local annexe', category: 'Loyer', amount: 850000, date: '2026-06-20', person: 'Comptable', icon: 'solar:home-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
  { id: 'e4', group: 'expense', title: 'Commissions booking.com', category: 'Commission', amount: 318000, date: '2026-06-18', person: 'Admin', icon: 'solar:percent-circle-linear', iconBg: 'rgba(215,111,2,0.10)', iconColor: '#d76f02' }
]

const MOCK_PERSONNEL = [
  { id: 'p1', group: 'personnel', title: 'Salaire — Thérèse N.', category: 'Réception', amount: 380000, date: '2026-06-26', person: 'CDI · Plein', icon: 'solar:user-linear', iconBg: 'rgba(15,118,110,0.10)', iconColor: '#0f766e' },
  { id: 'p2', group: 'personnel', title: 'Salaire — Jean-Bosco C.', category: 'Maintenance', amount: 320000, date: '2026-06-26', person: 'CDI · Plein', icon: 'solar:user-linear', iconBg: 'rgba(15,118,110,0.10)', iconColor: '#0f766e' },
  { id: 'p3', group: 'personnel', title: 'Prime — Cuisine équipe', category: 'Restauration', amount: 120000, date: '2026-06-24', person: 'Prime exceptionnelle', icon: 'solar:medal-star-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' },
  { id: 'p4', group: 'personnel', title: 'Salaire — Chantal B.', category: 'Ménage', amount: 260000, date: '2026-06-22', person: 'CDD · Temps partiel', icon: 'solar:user-linear', iconBg: 'rgba(15,118,110,0.10)', iconColor: '#0f766e' }
]

const MOCK_MATERIALS = [
  { id: 'm1', group: 'material', title: 'Linge de lit (paquet x12)', category: 'Textile', amount: 165000, date: '2026-06-26', person: 'Stock · Qté 12', icon: 'solar:bedside-table-2-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
  { id: 'm2', group: 'material', title: 'Savon premium (caisse)', category: 'Hygiène', amount: 88000, date: '2026-06-24', person: 'Stock · Qté 40', icon: 'solar:heart-rate-linear', iconBg: 'rgba(15,118,110,0.10)', iconColor: '#0f766e' },
  { id: 'm3', group: 'material', title: 'Café &amp; accueil (lot)', category: 'Consommables', amount: 142000, date: '2026-06-20', person: 'Bar · Qté 10 kg', icon: 'solar:cup-tea-hot-linear', iconBg: 'rgba(215,111,2,0.10)', iconColor: '#d76f02' }
]

const MOCK_ENTRIES = [
  { id: 'i1', group: 'paid', title: 'Paiement — RSV-0625-0042', booking_code: 'RSV-0625-0042', amount: 2850000, date: '2026-06-26', method: 'Bank', icon: 'solar:card-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#16a34a' },
  { id: 'i2', group: 'paid', title: 'Paiement — RSV-0625-0041', booking_code: 'RSV-0625-0041', amount: 1840000, date: '2026-06-25', method: 'Mobile Money', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#16a34a' },
  { id: 'i3', group: 'paid', title: 'Paiement — RSV-0625-0040', booking_code: 'RSV-0625-0040', amount: 940000, date: '2026-06-23', method: 'Espèces', icon: 'solar:money-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#16a34a' }
]

const MOCK_PENDING = [
  { id: 'ip1', group: 'pending', title: 'Attente — RSV-0625-0039', booking_code: 'RSV-0625-0039', amount: 3920000, date: '2026-06-27', method: 'À encaisser', icon: 'solar:clock-circle-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' },
  { id: 'ip2', group: 'pending', title: 'Attente — RSV-0625-0038', booking_code: 'RSV-0625-0038', amount: 650000, date: '2026-06-29', method: 'Chèque', icon: 'solar:checklist-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' }
]

export default {
  name: 'ComptabiliteView',
  components: {
    IonContent,
    IonPage,
    IonSegment,
    IonSegmentButton,
    IonLabel,
    IonButton,
    IonFab,
    IonFabButton,
    IonFabList,
    HeaderBar,
    LoadingOverlay
  },
  data() {
    return {
      loadingCompta: true,
      activeTab: 'expenses',
      activeExpenseTab: 'all',
      activeEntryTab: 'paid',
      expenses: [...MOCK_EXPENSES],
      personnel: [...MOCK_PERSONNEL],
      materials: [...MOCK_MATERIALS],
      entries: [...MOCK_ENTRIES],
      pending: [...MOCK_PENDING]
    }
  },
  computed: {
    periodLabel() {
      try {
        const d = new Date()
        return d.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
      } catch (_) {
        return 'Période en cours'
      }
    },
    expenseTabs() {
      return [
        { key: 'all', label: 'Toutes', count: this.expenseCount, icon: 'solar:layers-linear' },
        { key: 'expense', label: 'Dépenses', count: this.expenses.length, icon: 'solar:bill-list-linear' },
        { key: 'personnel', label: 'Personnel', count: this.personnel.length, icon: 'solar:users-group-rounded-linear' },
        { key: 'material', label: 'Matériel', count: this.materials.length, icon: 'solar:box-linear' }
      ]
    },
    entryTabs() {
      return [
        { key: 'paid', label: 'Encaissés', count: this.entries.length, icon: 'solar:wallet-money-linear' },
        { key: 'pending', label: 'À encaisser', count: this.pending.length, icon: 'solar:clock-circle-linear' }
      ]
    },
    currentExpenses() {
      if (this.activeExpenseTab === 'all') {
        return [...this.expenses, ...this.personnel, ...this.materials].sort((a, b) => (b.date || '').localeCompare(a.date || ''))
      }
      if (this.activeExpenseTab === 'expense') return this.expenses
      if (this.activeExpenseTab === 'personnel') return this.personnel
      if (this.activeExpenseTab === 'material') return this.materials
      return []
    },
    currentEntries() {
      if (this.activeEntryTab === 'paid') return this.entries
      if (this.activeEntryTab === 'pending') return this.pending
      return []
    },
    expenseCount() {
      return this.expenses.length + this.personnel.length + this.materials.length
    },
    entryCount() {
      return this.entries.length
    },
    currentExpenseTotal() {
      const sum = this.currentExpenses.reduce((s, t) => s + Number(t.amount || 0), 0)
      return this.formatCurrency(sum)
    },
    currentEntryTotal() {
      const sum = this.currentEntries.reduce((s, t) => s + Number(t.amount || 0), 0)
      return this.formatCurrency(sum)
    },
    totals() {
      const exp = this.expenses.reduce((s, t) => s + Number(t.amount || 0), 0)
        + this.personnel.reduce((s, t) => s + Number(t.amount || 0), 0)
        + this.materials.reduce((s, t) => s + Number(t.amount || 0), 0)
      const ent = this.entries.reduce((s, t) => s + Number(t.amount || 0), 0)
      return {
        expenses: this.formatCurrency(exp),
        entries: this.formatCurrency(ent),
        net: ent - exp
      }
    },
    balanceTone() {
      return this.totals.net >= 0 ? 'pos' : 'neg'
    },
    balanceLabel() {
      const n = Math.abs(this.totals.net)
      const sign = this.totals.net >= 0 ? '' : '- '
      return sign + this.formatCurrency(n)
    },
    showLoading() {
      return this.loadingCompta
    }
  },
  methods: {
    formatCurrency(v) {
      const n = Number(v || 0)
      try {
        return n.toLocaleString('fr-FR') + ' Fbu'
      } catch (_) {
        return n + ' Fbu'
      }
    },
    formatDate(iso) {
      if (!iso) return ''
      const d = new Date(iso)
      if (Number.isNaN(d.getTime())) return iso
      try {
        return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
      } catch (_) {
        return iso
      }
    },
    handlePrint() {
      if (typeof window !== 'undefined' && typeof window.print === 'function') {
        window.print()
      }
    },
    toastView(tx) {
      const msg = tx?.title ? `Voir : ${tx.title}` : 'Voir détails'
      this.$ionicToast?.show?.({ message: msg, duration: 1800, color: 'tertiary' })
    },
    toastEdit(tx) {
      const msg = tx?.title ? `Modifier : ${tx.title}` : 'Modifier'
      this.$ionicToast?.show?.({ message: msg, duration: 1800, color: 'primary' })
    },
    toastNewPayment() {
      this.$ionicToast?.show?.({ message: 'Nouveau paiement — À implémenter', duration: 2000, color: 'success' })
    },
    toastNewExpense() {
      this.$ionicToast?.show?.({ message: 'Nouvelle dépense — À implémenter', duration: 2000, color: 'danger' })
    },
    handleDeleteExpense(tx) {
      if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
        const ok = window.confirm(`Supprimer cette ligne : "${tx?.title || 'élément'}" ?`)
        if (!ok) return
      }
      const id = tx?.id
      if (!id) return
      const filterFn = (arr) => arr.filter((x) => x.id !== id)
      this.expenses = filterFn(this.expenses)
      this.personnel = filterFn(this.personnel)
      this.materials = filterFn(this.materials)
    },
    handleDeletePayment(tx) {
      if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
        const ok = window.confirm(`Supprimer ce paiement : "${tx?.title || 'élément'}" ?`)
        if (!ok) return
      }
      const id = tx?.id
      if (!id) return
      this.entries = this.entries.filter((x) => x.id !== id)
      this.pending = this.pending.filter((x) => x.id !== id)
    },
    async loadData() {
      this.loadingCompta = true
      try {
        const [payRes, expRes, perRes, matRes] = await Promise.all([
          endpoints.payments({ ordering: '-created_at', page_size: 20 }).catch(() => null),
          endpoints.expenses({ ordering: '-created_at', page_size: 20 }).catch(() => null),
          endpoints.personnel({ page_size: 20 }).catch(() => null),
          endpoints.materials({ page_size: 20 }).catch(() => null)
        ])
        const pluck = (r) => Array.isArray(r) ? r : (r?.results || [])
        if (payRes && pluck(payRes).length) {
          this.entries = pluck(payRes).map((p) => ({
            id: p.id,
            group: 'paid',
            title: `Paiement — ${p.booking_display_id || p.booking?.display_id || (p.booking ? '#' + p.booking.id : '')}`,
            booking_code: p.booking_display_id || p.booking?.display_id || (p.booking ? '#' + p.booking.id : '-'),
            amount: Number(p.amount || 0),
            date: p.created_at || p.payment_date,
            method: p.method || p.payment_method || '-',
            icon: 'solar:wallet-money-linear',
            iconBg: 'rgba(22,163,74,0.10)',
            iconColor: '#16a34a'
          }))
        }
        if (expRes && pluck(expRes).length) {
          this.expenses = pluck(expRes).map((e) => ({
            id: e.id,
            group: 'expense',
            title: e.label || e.title || e.description || 'Dépense',
            category: e.category || e.type || 'Autre',
            amount: Number(e.amount || 0),
            date: e.created_at || e.date,
            person: e.author || e.recorded_by || '-',
            icon: 'solar:bill-linear',
            iconBg: 'rgba(239,68,68,0.10)',
            iconColor: '#ef4444'
          }))
        }
        if (perRes && pluck(perRes).length) {
          this.personnel = pluck(perRes).slice(0, 10).map((pr) => ({
            id: pr.id,
            group: 'personnel',
            title: `${pr.full_name || pr.name || 'Employé'} — Salaire`,
            category: pr.role || pr.position || 'Personnel',
            amount: Number(pr.salary || 0) || 250000,
            date: pr.created_at || pr.hire_date || new Date().toISOString(),
            person: pr.contract_type || pr.status || 'Actif',
            icon: 'solar:user-linear',
            iconBg: 'rgba(15,118,110,0.10)',
            iconColor: '#0f766e'
          }))
        }
        if (matRes && pluck(matRes).length) {
          this.materials = pluck(matRes).slice(0, 10).map((m) => ({
            id: m.id,
            group: 'material',
            title: m.name || m.label || 'Article',
            category: m.category || 'Stock',
            amount: (Number(m.unit_price || 0) * Number(m.quantity || 1)) || Number(m.cost || 0) || 0,
            date: m.created_at || m.purchase_date || new Date().toISOString(),
            person: m.quantity ? `Qté ${m.quantity}` : '-',
            icon: 'solar:box-linear',
            iconBg: 'rgba(26,58,122,0.10)',
            iconColor: '#1a3a7a'
          }))
        }
      } catch (_e) {} finally {
        this.loadingCompta = false
      }
    }
  },
  mounted() {
    this.loadData()
  }
}
</script>

<style scoped>
.compta-page {
  background: #fbf7f2;
}

.compta-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
}

.header-print-btn {
  --background-hover: rgba(23, 11, 2, 0.06);
  --background-activated: rgba(23, 11, 2, 0.12);
  --border-radius: 14px;
  --color: #1a3a7a;
  height: 40px;
}
.header-icon {
  font-size: 1.3rem;
}

.compta-hero {
  margin-top: 18px;
  margin-bottom: 14px;
  padding: 22px 20px;
  border-radius: 28px;
  background:
    radial-gradient(circle at 92% 10%, rgba(22,163,74,0.20), transparent 44%),
    radial-gradient(circle at 8% 92%, rgba(239,68,68,0.18), transparent 44%),
    linear-gradient(135deg, #1a3a7a 0%, #17336b 55%, #1a3a7a 100%);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 22px 42px rgba(26, 58, 122, 0.24);
}

.hero-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.hero-eyebrow {
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d4af37;
  font-weight: 700;
}

.hero-title {
  margin: 0;
  font-size: 0.9rem;
  letter-spacing: 0.01em;
  font-weight: 600;
  color: rgba(248, 250, 252, 0.82);
}

.hero-balance {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: 0.005em;
  line-height: 1.05;
}
.hero-balance.pos { color: #86efac; text-shadow: 0 2px 12px rgba(22,163,74,0.28); }
.hero-balance.neg { color: #fecaca; }

.hero-marks {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 0 0 auto;
  min-width: 160px;
}

.mark-row {
  display: grid;
  grid-template-columns: 12px 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 14px;
  font-size: 0.8rem;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
}
.mark-row.pos { color: #bbf7d0; }
.mark-row.neg { color: #fecaca; }

.mark-swatch {
  width: 12px;
  height: 12px;
  border-radius: 5px;
}
.mark-swatch.in { background: #16a34a; box-shadow: 0 0 0 3px rgba(22,163,74,0.15); }
.mark-swatch.out { background: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.15); }

.mark-val {
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.balance-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 6px;
}

.bcard {
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 22px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
}

.bcard-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bcard-icon {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  padding: 7px;
  box-sizing: border-box;
}
.bcard.in .bcard-icon { background: rgba(22,163,74,0.10); color: #16a34a; }
.bcard.out .bcard-icon { background: rgba(239,68,68,0.10); color: #ef4444; }

.bcard-kicker {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #64748b;
}

.bcard-value {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.2rem;
  font-weight: 800;
  color: #170b02;
  font-variant-numeric: tabular-nums;
}

.bcard-sub {
  font-size: 0.78rem;
  color: #64748b;
  line-height: 1.35;
}

.segment-shell {
  padding: 18px 0 4px;
}

.compta-segment {
  --background: #ffffff;
  --border-radius: 16px;
  padding: 4px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid rgba(23,11,2,0.08);
  box-shadow: 0 8px 22px rgba(23,11,2,0.04);
}

:deep(.compta-segment .ion-segment-button) {
  --indicator-color: transparent;
  --background-checked: transparent;
  --color-checked: #ffffff;
  --color: #475569;
  --border-radius: 14px;
  --padding-start: 6px;
  --padding-end: 6px;
  --padding-top: 8px;
  --padding-bottom: 8px;
  min-height: 42px;
}
:deep(.compta-segment .ion-segment-button.segment-button-checked) {
  background: linear-gradient(135deg, #d76f02, #e68a33);
  color: #ffffff;
  box-shadow: 0 8px 20px rgba(215,111,2,0.28);
}

.seg-ic {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 6px;
  font-size: 1rem;
  vertical-align: -2px;
}

.sub-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 6px 0 16px;
}

.sub-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #ffffff;
  border: 1px solid rgba(23,11,2,0.08);
  color: #475569;
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.18s ease;
}
.sub-tab.active {
  background: rgba(215,111,2,0.10);
  color: #d76f02;
  border-color: rgba(215,111,2,0.30);
}

.sub-tab-ic { font-size: 0.95rem; }

.sub-tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1px 7px;
  background: rgba(23,11,2,0.06);
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  color: #475569;
}
.sub-tab.active .sub-tab-count {
  background: #d76f02;
  color: #ffffff;
}

.list-block {
  margin-top: 10px;
  background: #ffffff;
  border: 1px solid rgba(23,11,2,0.08);
  border-radius: 24px;
  padding: 18px;
  box-shadow: 0 12px 30px rgba(23,11,2,0.04);
}

.list-head-row {
  padding: 0 2px 4px;
}

.list-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.list-title {
  margin: 6px 0 0;
  font-size: 1.2rem;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 800;
  color: #170b02;
  font-variant-numeric: tabular-nums;
}

.list-hairline {
  height: 1px;
  margin: 12px 2px 14px;
  background: rgba(23, 11, 2, 0.08);
}

.tx-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.tx-row-shell {
  display: flex;
  flex-direction: column;
  padding: 8px 0;
  border-bottom: 1px dashed rgba(23,11,2,0.06);
}
.tx-row-shell:last-child { border-bottom: none; }

.tx-row {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}

.tx-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex: 0 0 auto;
}

.tx-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.tx-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: #170b02;
  line-height: 1.3;
}

.tx-sub {
  font-size: 0.76rem;
  color: #64748b;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 6px;
  align-items: center;
}

.tx-cat {
  background: rgba(23,11,2,0.05);
  color: #475569;
  padding: 1px 8px;
  border-radius: 999px;
  font-weight: 600;
}

.tx-person {
  color: #94a3b8;
}

.tx-amount {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 800;
  font-size: 0.95rem;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.tx-amount.in { color: #16a34a; }
.tx-amount.out { color: #ef4444; }

.tx-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  padding: 10px 0 4px;
  margin-left: 52px;
  border-top: 1px dashed rgba(23,11,2,0.06);
}

.tx-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 7px 6px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: rgba(23,11,2,0.03);
  font-size: 0.74rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.16s ease;
}
.tx-action-btn.view { color: #1a3a7a; background: rgba(26,58,122,0.08); border-color: rgba(26,58,122,0.14); }
.tx-action-btn.view:hover { background: rgba(26,58,122,0.14); }
.tx-action-btn.edit { color: #d76f02; background: rgba(215,111,2,0.08); border-color: rgba(215,111,2,0.18); }
.tx-action-btn.edit:hover { background: rgba(215,111,2,0.14); }
.tx-action-btn.delete { color: #ef4444; background: rgba(239,68,68,0.08); border-color: rgba(239,68,68,0.18); }
.tx-action-btn.delete:hover { background: rgba(239,68,68,0.14); }
.tx-action-btn svg { font-size: 0.95rem; }

.empty-state {
  padding: 30px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 0.88rem;
  text-align: center;
  border-bottom: none;
}
.empty-ic { font-size: 1.5rem; color: #94a3b8; }

.page-bottom-spacer {
  height: 100px;
}

.fab-shell {
  --ion-fab-margin-bottom: calc(84px + env(safe-area-inset-bottom));
  --ion-fab-margin-end: 16px;
  z-index: 10;
}
:deep(.fab-shell .fab-main) {
  --background: linear-gradient(135deg, #d76f02, #e68a33);
  width: 58px;
  height: 58px;
  box-shadow: 0 16px 40px rgba(215,111,2,0.42);
  color: #fff;
}
:deep(.fab-shell ion-fab-button .iconify,
       .fab-shell ion-fab-button svg,
       .fab-shell ion-fab-button [data-icon]) {
  width: 26px !important;
  height: 26px !important;
  max-width: 26px !important;
  max-height: 26px !important;
  display: inline-block !important;
  opacity: 1 !important;
  visibility: visible !important;
}
:deep(.fab-shell .fab-main .iconify,
       .fab-shell .fab-main svg) {
  width: 30px !important;
  height: 30px !important;
  max-width: 30px !important;
  max-height: 30px !important;
}
:deep(.fab-shell .fab-sub) { width: 46px; height: 46px; color: #fff; }
:deep(.fab-shell .fab-sub.green) { --background: linear-gradient(135deg, #16a34a, #22c55e); }
:deep(.fab-shell .fab-sub.red) { --background: linear-gradient(135deg, #ef4444, #f87171); }
:deep(.fab-shell .fab-sub.navy) { --background: linear-gradient(135deg, #1a3a7a, #1e4489); }

@media (min-width: 768px) {
  .content-shell {
    max-width: 860px;
    margin: 0 auto;
    padding: 0 24px;
  }
}

@media print {
  ion-header,
  ion-tab-bar,
  .fab-shell,
  .header-print-btn,
  .tx-actions {
    display: none !important;
  }
  .compta-page,
  .compta-content,
  .content-shell {
    --background: #ffffff !important;
    background: #ffffff !important;
  }
  .compta-hero {
    box-shadow: none !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .bcard,
  .list-block {
    box-shadow: none !important;
    break-inside: avoid;
  }
}
</style>
