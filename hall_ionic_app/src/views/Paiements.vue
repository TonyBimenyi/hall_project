<template>
  <ion-page class="paiements-page">
    <HeaderBar title="Paiements" eyebrow="Encaissements" :show-menu="false">
      <template v-slot:actions>
        <ion-button fill="clear" class="header-print-btn" @click="handlePrint">
          <Icon icon="solar:printer-linear" class="header-icon" />
        </ion-button>
      </template>
    </HeaderBar>

    <ion-content class="paiements-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement des paiements"
      />
      <div class="content-shell">

        <section class="paiements-hero">
          <div class="hero-col">
            <small class="hero-eyebrow">{{ periodLabel }}</small>
            <h1 class="hero-title">Encaissements</h1>
            <div class="hero-balance pos">{{ totalAllLabel }}</div>
          </div>
          <div class="hero-marks" aria-hidden="true">
            <div class="mark-row pos"><span class="mark-swatch in"></span><span>Encaissés</span><span class="mark-val">{{ totals.collected }}</span></div>
            <div class="mark-row wait"><span class="mark-swatch pend"></span><span>À encaisser</span><span class="mark-val">{{ totals.pending }}</span></div>
          </div>
        </section>

        <section class="balance-cards">
          <div class="bcard in">
            <div class="bcard-head">
              <Icon icon="solar:wallet-money-linear" class="bcard-icon" />
              <span class="bcard-kicker">Total encaissé</span>
            </div>
            <div class="bcard-value">{{ totals.collected }}</div>
            <div class="bcard-sub">{{ countCollected }} paiement{{ countCollected > 1 ? 's' : '' }}</div>
          </div>
          <div class="bcard pend">
            <div class="bcard-head">
              <Icon icon="solar:clock-circle-linear" class="bcard-icon" />
              <span class="bcard-kicker">En attente</span>
            </div>
            <div class="bcard-value">{{ totals.pending }}</div>
            <div class="bcard-sub">{{ countPending }} facture{{ countPending > 1 ? 's' : '' }}</div>
          </div>
        </section>

        <section class="filter-shell">
          <div class="filter-row">
            <div class="search-wrap">
              <Icon icon="solar:magnifer-linear" class="search-ic" />
              <input
                v-model="searchQuery"
                class="search-input"
                type="search"
                placeholder="Rechercher un paiement, réservation, client..."
              />
            </div>
          </div>
          <div class="chips-row">
            <button
              v-for="chip in methodChips"
              :key="chip.key"
              type="button"
              class="chip"
              :class="{ active: activeFilter === chip.key }"
              @click="activeFilter = chip.key"
            >
              <Icon v-if="chip.icon" :icon="chip.icon" class="chip-ic" />
              <span>{{ chip.label }}</span>
              <span class="chip-count">{{ chip.count }}</span>
            </button>
          </div>
        </section>

        <section class="list-block">
          <div class="list-head-row">
            <div>
              <div class="list-kicker">Paiements filtrés</div>
              <h2 class="list-title">{{ filteredCount }} ligne{{ filteredCount > 1 ? 's' : '' }} • {{ filteredTotal }}</h2>
            </div>
            <button type="button" class="sort-btn" @click="toggleSort">
              <Icon icon="solar:sort-from-a-to-z-linear" class="sort-ic" />
              <span>{{ sortLabel }}</span>
            </button>
          </div>
          <div class="list-hairline" aria-hidden="true"></div>

          <div v-if="filteredPayments.length === 0" class="empty-state">
            <Icon icon="solar:wallet-money-linear" class="empty-ic" />
            <div class="empty-title">Aucun paiement trouvé</div>
            <div class="empty-sub">Aucun enregistrement ne correspond aux filtres sélectionnés.</div>
          </div>

          <ul v-else class="tx-list">
            <li v-for="tx in filteredPayments" :key="tx.id" class="tx-item">
              <div class="tx-ic-shell" :style="{ background: tx.iconBg }">
                <Icon :icon="tx.icon" class="tx-ic" :style="{ color: tx.iconColor }" />
              </div>
              <div class="tx-body">
                <div class="tx-head">
                  <h3 class="tx-title">{{ tx.title }}</h3>
                  <span class="tx-amount" :class="tx.status === 'pending' ? 'pend' : 'pos'">{{ tx.amountLabel }}</span>
                </div>
                <div class="tx-meta">
                  <span class="tx-chip method">{{ tx.methodLabel }}</span>
                  <span v-if="tx.booking_code" class="tx-chip booking">{{ tx.booking_code }}</span>
                  <span class="tx-date">
                    <Icon icon="solar:calendar-linear" class="meta-ic" />
                    {{ tx.dateLabel }}
                  </span>
                </div>
                <div v-if="tx.customer_name || tx.reference" class="tx-sub">
                  <span v-if="tx.customer_name">{{ tx.customer_name }}</span>
                  <span v-if="tx.customer_name && tx.reference"> · </span>
                  <span v-if="tx.reference">Ref. {{ tx.reference }}</span>
                </div>
                <div class="tx-actions">
                  <button type="button" class="tx-btn navy" @click="toastView(tx)">
                    <Icon icon="solar:eye-linear" class="tx-btn-ic" />
                    <span>Voir</span>
                  </button>
                  <button type="button" class="tx-btn orange" @click="toastEdit(tx)">
                    <Icon icon="solar:pen-linear" class="tx-btn-ic" />
                    <span>Modifier</span>
                  </button>
                  <button type="button" class="tx-btn red" @click="handleDelete(tx)">
                    <Icon icon="solar:trash-bin-trash-linear" class="tx-btn-ic" />
                    <span>Supprimer</span>
                  </button>
                </div>
              </div>
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
          <ion-fab-button class="fab-sub navy" @click="handlePrint">
            <Icon icon="solar:printer-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
          <ion-fab-button class="fab-sub gold" @click="toastExport">
            <Icon icon="solar:document-linear" width="26" height="26" style="width:26px;height:26px;display:block" />
          </ion-fab-button>
        </ion-fab-list>
      </ion-fab>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonContent, IonPage, IonButton, IonFab, IonFabButton, IonFabList } from '@ionic/vue'
import HeaderBar from '@/components/HeaderBar.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { endpoints } from '@/lib/api.js'

const METHOD_META = {
  mtn: { label: 'MTN MoMo', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#16a34a' },
  mtn_momo: { label: 'MTN MoMo', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#16a34a' },
  'mtn momo': { label: 'MTN MoMo', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#16a34a' },
  orange: { label: 'Orange Money', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(215,111,2,0.10)', iconColor: '#d76f02' },
  orange_money: { label: 'Orange Money', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(215,111,2,0.10)', iconColor: '#d76f02' },
  'orange money': { label: 'Orange Money', icon: 'solar:smartphone-rotate-2-linear', iconBg: 'rgba(215,111,2,0.10)', iconColor: '#d76f02' },
  cash: { label: 'Espèces', icon: 'solar:money-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#15803d' },
  especes: { label: 'Espèces', icon: 'solar:money-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#15803d' },
  espèces: { label: 'Espèces', icon: 'solar:money-linear', iconBg: 'rgba(22,163,74,0.10)', iconColor: '#15803d' },
  bank: { label: 'Virement bancaire', icon: 'solar:card-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
  transfer: { label: 'Virement bancaire', icon: 'solar:card-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
  virement: { label: 'Virement bancaire', icon: 'solar:card-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
  cheque: { label: 'Chèque', icon: 'solar:checklist-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' },
  check: { label: 'Chèque', icon: 'solar:checklist-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' },
  card: { label: 'Carte bancaire', icon: 'solar:card-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' },
  pending: { label: 'À encaisser', icon: 'solar:clock-circle-linear', iconBg: 'rgba(212,175,55,0.12)', iconColor: '#b8860b' }
}

const DEFAULT_META = { label: 'Paiement', icon: 'solar:wallet-money-linear', iconBg: 'rgba(26,58,122,0.10)', iconColor: '#1a3a7a' }

export default {
  name: 'PaiementsView',
  components: {
    IonContent,
    IonPage,
    IonButton,
    IonFab,
    IonFabButton,
    IonFabList,
    HeaderBar,
    LoadingOverlay
  },
  data() {
    return {
      loadingPayments: true,
      searchQuery: '',
      activeFilter: 'all',
      sortDir: 'desc',
      payments: []
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
    methodChips() {
      const countByMethod = (key) => {
        return this.payments.filter((p) => {
          if (key === 'all') return true
          if (key === 'pending') return p.status === 'pending'
          if (key === 'mobile') return ['mtn', 'orange', 'mtn_momo', 'orange_money'].indexOf(p.methodKey) !== -1
          return p.methodKey === key
        }).length
      }
      return [
        { key: 'all', label: 'Tous', icon: 'solar:layers-linear', count: countByMethod('all') },
        { key: 'mtn', label: 'MTN MoMo', icon: 'solar:smartphone-rotate-2-linear', count: countByMethod('mtn') },
        { key: 'orange', label: 'Orange Money', icon: 'solar:smartphone-rotate-2-linear', count: countByMethod('orange') },
        { key: 'cash', label: 'Espèces', icon: 'solar:money-linear', count: countByMethod('cash') },
        { key: 'bank', label: 'Banque', icon: 'solar:card-linear', count: countByMethod('bank') },
        { key: 'cheque', label: 'Chèque', icon: 'solar:checklist-linear', count: countByMethod('cheque') },
        { key: 'pending', label: 'À encaisser', icon: 'solar:clock-circle-linear', count: countByMethod('pending') }
      ]
    },
    filteredPayments() {
      const q = String(this.searchQuery || '').trim().toLowerCase()
      let list = this.payments.filter((p) => {
        if (this.activeFilter === 'pending') {
          if (p.status !== 'pending') return false
        } else if (this.activeFilter !== 'all') {
          if (this.activeFilter === 'mobile') {
            if (['mtn', 'orange', 'mtn_momo', 'orange_money'].indexOf(p.methodKey) === -1) return false
          } else if (p.methodKey !== this.activeFilter) {
            return false
          }
        }
        if (!q) return true
        const haystack = [p.title, p.booking_code, p.customer_name, p.reference, p.methodLabel, p.note, p.email, p.phone]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
        return haystack.indexOf(q) !== -1
      })
      list = [...list].sort((a, b) => {
        const ad = new Date(a.date || 0).getTime()
        const bd = new Date(b.date || 0).getTime()
        return this.sortDir === 'desc' ? bd - ad : ad - bd
      })
      return list
    },
    filteredCount() {
      return this.filteredPayments.length
    },
    filteredTotal() {
      const sum = this.filteredPayments.reduce((s, t) => s + Number(t.amount || 0), 0)
      return this.formatCurrency(sum)
    },
    countCollected() {
      return this.payments.filter((p) => p.status !== 'pending').length
    },
    countPending() {
      return this.payments.filter((p) => p.status === 'pending').length
    },
    totals() {
      const col = this.payments.filter((p) => p.status !== 'pending').reduce((s, t) => s + Number(t.amount || 0), 0)
      const pend = this.payments.filter((p) => p.status === 'pending').reduce((s, t) => s + Number(t.amount || 0), 0)
      return {
        collected: this.formatCurrency(col),
        pending: this.formatCurrency(pend)
      }
    },
    totalAllLabel() {
      const all = this.payments.reduce((s, t) => s + Number(t.amount || 0), 0)
      return this.formatCurrency(all)
    },
    sortLabel() {
      return this.sortDir === 'desc' ? 'Plus récent' : 'Plus ancien'
    },
    showLoading() {
      return this.loadingPayments
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
    normalizeMethod(raw) {
      const key = String(raw || '').toLowerCase().replace(/[\s_-]+/g, '_')
      if (METHOD_META[key]) return { key, ...METHOD_META[key] }
      const altKey = String(raw || '').toLowerCase()
      if (METHOD_META[altKey]) return { key: altKey, ...METHOD_META[altKey] }
      const cleanKey = String(raw || '').toLowerCase().split(/[\s_-]/)[0]
      if (METHOD_META[cleanKey]) return { key: cleanKey, ...METHOD_META[cleanKey] }
      return { key: 'other', ...DEFAULT_META, label: raw || DEFAULT_META.label }
    },
    detectStatus(p) {
      const s = String(p.status || p.state || p.statut || 'paid').toLowerCase()
      if (['pending', 'attente', 'en_attente', 'unpaid', 'impaye', 'impayé', 'à_encaisser', 'a_encaisser'].indexOf(s) !== -1) {
        return 'pending'
      }
      return 'collected'
    },
    mapPayment(raw) {
      if (!raw || typeof raw !== 'object') return null
      const methodRaw = raw.payment_method || raw.method || raw.mode || raw.methode || 'other'
      const method = this.normalizeMethod(methodRaw)
      const status = this.detectStatus(raw)
      const amount = Number(raw.amount || raw.amount_paid || raw.montant || raw.total || raw.value || 0)
      const bookingCode = raw.booking_code || raw.booking_ref || raw.booking_display_id || raw.display_id || (raw.booking && (raw.booking.display_id || raw.booking.code)) || ''
      const customerName = raw.customer_name || raw.client || (raw.customer && (raw.customer.full_name || raw.customer.name || raw.customer.username)) || ''
      const date = raw.payment_date || raw.date_paid || raw.date || raw.created_at || raw.date_paiement || ''
      const title = bookingCode
        ? `Paiement — ${bookingCode}`
        : (customerName ? `Paiement · ${customerName}` : method.label)
      const effectiveMethodKey = status === 'pending' ? 'pending' : method.key
      const effectiveMeta = status === 'pending'
        ? { icon: METHOD_META.pending.icon, iconBg: METHOD_META.pending.iconBg, iconColor: METHOD_META.pending.iconColor, label: method.label }
        : method
      return {
        id: raw.id || `${date}-${amount}-${Math.random().toString(36).slice(2, 7)}`,
        title,
        amount,
        amountLabel: this.formatCurrency(amount),
        methodKey: effectiveMethodKey,
        methodLabel: effectiveMeta.label,
        icon: effectiveMeta.icon,
        iconBg: effectiveMeta.iconBg,
        iconColor: effectiveMeta.iconColor,
        status,
        booking_code: bookingCode,
        customer_name: customerName,
        reference: raw.reference || raw.ref || raw.numero || raw.receipt_no || '',
        note: raw.note || raw.memo || raw.notes || raw.commentaire || '',
        email: raw.email || (raw.customer && raw.customer.email) || '',
        phone: raw.phone || (raw.customer && raw.customer.phone) || '',
        date,
        dateLabel: this.formatDate(date),
        _raw: raw
      }
    },
    pluckArray(result) {
      if (Array.isArray(result)) return result
      if (result && Array.isArray(result.results)) return result.results
      if (result && Array.isArray(result.data)) return result.data
      return []
    },
    async loadData() {
      this.loadingPayments = true
      try {
        const result = await endpoints.payments({ page_size: 200, ordering: '-created_at' }).catch(() => null)
        const list = this.pluckArray(result)
        const mapped = list.map((r) => this.mapPayment(r)).filter(Boolean)
        this.payments = mapped
      } catch (_) {
        this.payments = []
      } finally {
        this.loadingPayments = false
      }
    },
    toggleSort() {
      this.sortDir = this.sortDir === 'desc' ? 'asc' : 'desc'
    },
    handlePrint() {
      if (typeof window !== 'undefined' && typeof window.print === 'function') {
        window.print()
      }
    },
    toastView(tx) {
      const msg = tx?.booking_code ? `Voir paiement ${tx.booking_code}` : (tx?.title ? `Voir : ${tx.title}` : 'Voir détails')
      this.$ionicToast?.show?.({ message: msg, duration: 1800, color: 'tertiary' })
    },
    toastEdit(tx) {
      const msg = tx?.booking_code ? `Modifier ${tx.booking_code}` : 'Modifier paiement'
      this.$ionicToast?.show?.({ message: msg, duration: 1800, color: 'primary' })
    },
    toastNewPayment() {
      this.$ionicToast?.show?.({ message: 'Nouveau paiement — À implémenter', duration: 2000, color: 'success' })
    },
    toastExport() {
      this.$ionicToast?.show?.({ message: 'Export PDF — À implémenter', duration: 2000, color: 'primary' })
    },
    handleDelete(tx) {
      if (typeof window !== 'undefined' && typeof window.confirm === 'function') {
        const ok = window.confirm(`Supprimer ce paiement : "${tx?.title || 'élément'}" ?`)
        if (!ok) return
      }
      const id = tx?.id
      if (!id) return
      this.payments = this.payments.filter((x) => x.id !== id)
    }
  },
  mounted() {
    this.loadData()
  }
}
</script>

<style scoped>
.paiements-page {
  background: #fbf7f2;
}

.paiements-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
  position: relative;
  z-index: 1;
}

.header-print-btn {
  --padding-start: 8px;
  --padding-end: 8px;
  color: #1a3a7a;
}

.header-icon {
  width: 20px;
  height: 20px;
  display: block;
}

.paiements-hero {
  margin-top: 18px;
  margin-bottom: 18px;
  padding: 22px 20px 20px;
  border-radius: 22px;
  background: linear-gradient(135deg, #1a3a7a 0%, #224b9e 62%, #d4af37 180%);
  color: #fff;
  box-shadow: 0 16px 40px -18px rgba(26, 58, 122, 0.55);
  position: relative;
  overflow: hidden;
}

.paiements-hero::before {
  content: "";
  position: absolute;
  top: -40%;
  right: -18%;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.26) 0%, rgba(212, 175, 55, 0) 65%);
  border-radius: 50%;
  pointer-events: none;
}

.paiements-hero::after {
  content: "";
  position: absolute;
  inset: 0;
  background:
    linear-gradient(115deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0) 48%),
    repeating-linear-gradient(45deg, rgba(255,255,255,0.035) 0 2px, transparent 2px 9px);
  pointer-events: none;
}

.hero-col {
  position: relative;
  z-index: 1;
}

.hero-eyebrow {
  display: inline-block;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 6px;
}

.hero-title {
  margin: 0 0 8px;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 600;
  font-size: 1.48rem;
  letter-spacing: 0.005em;
  color: #fff;
}

.hero-balance {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  line-height: 1.05;
  font-variant-numeric: tabular-nums;
}

.hero-balance.pos { color: #fff; }
.hero-balance.neg { color: #fecaca; }

.hero-marks {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 16px;
  position: relative;
  z-index: 1;
}

.mark-row {
  display: grid;
  grid-template-columns: 14px 1fr auto;
  align-items: center;
  gap: 10px;
  font-size: 0.78rem;
  color: rgba(255, 255, 255, 0.82);
}

.mark-row.wait { color: rgba(255, 255, 255, 0.86); }

.mark-swatch {
  width: 12px;
  height: 12px;
  border-radius: 4px;
}

.mark-swatch.in {
  background: linear-gradient(135deg, #4ade80, #16a34a);
}

.mark-swatch.out {
  background: linear-gradient(135deg, #fca5a5, #ef4444);
}

.mark-swatch.pend {
  background: linear-gradient(135deg, #fde68a, #d4af37);
}

.mark-val {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #fff;
}

.balance-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}

.bcard {
  padding: 16px 14px;
  border-radius: 18px;
  background: #fff;
  border: 1px solid rgba(23, 11, 2, 0.05);
  box-shadow: 0 10px 24px -16px rgba(23, 11, 2, 0.18);
}

.bcard-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.bcard-icon {
  width: 20px;
  height: 20px;
  display: block;
}

.bcard.in .bcard-icon { color: #16a34a; }
.bcard.pend .bcard-icon { color: #b8860b; }

.bcard-kicker {
  font-size: 0.72rem;
  letter-spacing: 0.03em;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}

.bcard-value {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 700;
  font-size: 1.12rem;
  letter-spacing: 0.005em;
  color: #170b02;
  font-variant-numeric: tabular-nums;
  margin-bottom: 4px;
}

.bcard-sub {
  font-size: 0.72rem;
  color: #64748b;
  letter-spacing: 0.01em;
}

.filter-shell {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  background: #fff;
  border: 1px solid rgba(23, 11, 2, 0.07);
  border-radius: 14px;
  padding: 0 12px 0 40px;
  box-shadow: 0 8px 22px -18px rgba(23, 11, 2, 0.25);
}

.search-ic {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: #94a3b8;
}

.search-input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  padding: 13px 0;
  font-size: 0.88rem;
  color: #170b02;
  font-family: inherit;
}

.search-input::placeholder {
  color: #94a3b8;
}

.chips-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid rgba(23, 11, 2, 0.07);
  color: #475569;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
  font-family: inherit;
}

.chip-ic {
  width: 15px;
  height: 15px;
}

.chip-count {
  padding: 1px 7px;
  border-radius: 999px;
  background: rgba(23, 11, 2, 0.05);
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 700;
}

.chip.active {
  background: linear-gradient(135deg, #1a3a7a, #224b9e);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 10px 24px -14px rgba(26, 58, 122, 0.55);
}

.chip.active .chip-count {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.list-block {
  background: #fff;
  border-radius: 22px;
  padding: 16px 16px 4px;
  border: 1px solid rgba(23, 11, 2, 0.05);
  box-shadow: 0 12px 30px -20px rgba(23, 11, 2, 0.2);
}

.list-head-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  padding: 4px 4px 12px;
}

.list-kicker {
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 700;
  margin-bottom: 4px;
}

.list-title {
  margin: 0;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 600;
  font-size: 1.12rem;
  color: #170b02;
  letter-spacing: 0.005em;
}

.sort-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: 10px;
  border: 1px solid rgba(23, 11, 2, 0.07);
  background: rgba(23, 11, 2, 0.02);
  color: #475569;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
}

.sort-ic {
  width: 15px;
  height: 15px;
}

.list-hairline {
  height: 1px;
  background: linear-gradient(90deg, rgba(23,11,2,0) 0%, rgba(23,11,2,0.08) 15%, rgba(23,11,2,0.08) 85%, rgba(23,11,2,0) 100%);
  margin: 0 -16px 8px;
}

.empty-state {
  padding: 44px 16px 36px;
  text-align: center;
}

.empty-ic {
  width: 42px;
  height: 42px;
  display: block;
  margin: 0 auto 12px;
  color: #cbd5e1;
}

.empty-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 600;
  font-size: 1.02rem;
  color: #475569;
  margin-bottom: 4px;
}

.empty-sub {
  font-size: 0.78rem;
  color: #94a3b8;
}

.tx-list {
  list-style: none;
  margin: 0;
  padding: 4px 0 8px;
  display: flex;
  flex-direction: column;
}

.tx-item {
  display: grid;
  grid-template-columns: 46px 1fr;
  gap: 12px;
  padding: 14px 4px 16px;
  border-bottom: 1px solid rgba(23, 11, 2, 0.05);
}

.tx-item:last-child {
  border-bottom: none;
}

.tx-ic-shell {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tx-ic {
  width: 22px;
  height: 22px;
  display: block;
}

.tx-body {
  min-width: 0;
}

.tx-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}

.tx-title {
  margin: 0;
  font-weight: 700;
  font-size: 0.92rem;
  color: #170b02;
  letter-spacing: 0.005em;
  line-height: 1.25;
}

.tx-amount {
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  font-size: 0.92rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.tx-amount.pos { color: #16a34a; }
.tx-amount.pend { color: #b8860b; }

.tx-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  margin-bottom: 4px;
}

.tx-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 8px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.tx-chip.method {
  background: rgba(26, 58, 122, 0.08);
  color: #1a3a7a;
}

.tx-chip.booking {
  background: rgba(215, 111, 2, 0.08);
  color: #d76f02;
}

.tx-date {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.72rem;
  color: #64748b;
}

.meta-ic {
  width: 13px;
  height: 13px;
}

.tx-sub {
  font-size: 0.76rem;
  color: #64748b;
  margin-bottom: 10px;
}

.tx-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.tx-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 8px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: rgba(23, 11, 2, 0.03);
  color: #475569;
  font-size: 0.74rem;
  font-weight: 700;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.16s ease;
}

.tx-btn-ic {
  width: 14px;
  height: 14px;
}

.tx-btn.navy { background: rgba(26, 58, 122, 0.08); color: #1a3a7a; }
.tx-btn.orange { background: rgba(215, 111, 2, 0.08); color: #d76f02; }
.tx-btn.red { background: rgba(239, 68, 68, 0.08); color: #dc2626; }

.page-bottom-spacer {
  height: 120px;
}
</style>
