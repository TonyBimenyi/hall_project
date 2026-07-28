<template>
  <ion-page class="profile-page">
    <HeaderBar title="Mon profil" eyebrow="Compte" :show-menu="false" />

    <ion-content class="profile-content">
      <LoadingOverlay
        :visible="showLoading"
        title="Labertha Villa"
        subtitle="Chargement du profil"
      />
      <div class="content-shell">

        <section class="profile-hero">
          <div class="profile-avatar">{{ userInitials }}</div>
          <div class="profile-copy">
            <div class="profile-name">{{ profile.full_name }}</div>
            <div class="profile-role">{{ profile.role }}</div>
            <div class="profile-pill">{{ profile.station || 'Réception principale' }}</div>
            <div class="profile-contact-row">
              <span v-if="profile.email" class="contact-chip">
                <Icon icon="solar:letter-linear" class="contact-ic" />
                <span class="contact-val">{{ profile.email }}</span>
              </span>
              <span v-if="profile.phone" class="contact-chip">
                <Icon icon="solar:phone-linear" class="contact-ic" />
                <span class="contact-val">{{ profile.phone }}</span>
              </span>
            </div>
          </div>
        </section>

        <section class="user-meta-card">
          <div class="meta-head">
            <div class="meta-kicker">Identifiant</div>
            <h2 class="meta-title">Informations utilisateur</h2>
          </div>
          <div class="meta-divider" aria-hidden="true"></div>
          <ul class="meta-list">
            <li class="meta-row">
              <span class="meta-label">Nom complet</span>
              <span class="meta-value">{{ profile.full_name }}</span>
            </li>
            <li class="meta-row">
              <span class="meta-label">Nom d'utilisateur</span>
              <span class="meta-value mono">{{ profile.username }}</span>
            </li>
            <li class="meta-row">
              <span class="meta-label">Adresse e-mail</span>
              <span class="meta-value">{{ profile.email }}</span>
            </li>
            <li class="meta-row">
              <span class="meta-label">Téléphone</span>
              <span class="meta-value">{{ profile.phone }}</span>
            </li>
            <li class="meta-row">
              <span class="meta-label">Rôle</span>
              <span class="meta-value"><span class="role-tag">{{ profile.role }}</span></span>
            </li>
            <li class="meta-row">
              <span class="meta-label">Poste / Station</span>
              <span class="meta-value">{{ profile.station || '—' }}</span>
            </li>
            <li class="meta-row">
              <span class="meta-label">Compte créé le</span>
              <span class="meta-value">{{ profile.created_label }}</span>
            </li>
          </ul>
        </section>

        <section class="list-block">
          <div class="list-block-kicker"><span class="kicker-chip">Accès rapide</span></div>
          <div class="nav-list">
            <button v-for="item in quickNav" :key="item.key" class="nav-item" @click="goTo(item.path)">
              <span class="nav-icon-wrap" :style="{ background: item.bg, color: item.color }">
                <Icon :icon="item.icon" class="nav-icon" />
              </span>
              <span class="nav-copy">
                <span class="nav-label">{{ item.label }}</span>
                <span class="nav-hint">{{ item.hint }}</span>
              </span>
              <Icon icon="solar:alt-arrow-right-linear" class="nav-arrow" />
            </button>
          </div>
        </section>

        <section class="list-block">
          <div class="list-block-kicker"><span class="kicker-chip">Sécurité</span></div>
          <div class="nav-list">
            <button
              v-for="item in securityItems"
              :key="item.key"
              class="nav-item"
              @click="handleSecurity(item)"
            >
              <span class="nav-icon-wrap" :style="{ background: item.bg, color: item.color }">
                <Icon :icon="item.icon" class="nav-icon" />
              </span>
              <span class="nav-copy">
                <span class="nav-label">{{ item.label }}</span>
                <span class="nav-hint">{{ item.hint }}</span>
              </span>
              <span v-if="item.side" class="nav-side-tag">{{ item.side }}</span>
              <Icon icon="solar:alt-arrow-right-linear" class="nav-arrow" />
            </button>
          </div>
        </section>

        <section class="list-block">
          <div class="list-block-kicker"><span class="kicker-chip">Paramètres</span></div>
          <div class="nav-list">
            <button v-for="item in settings" :key="item.key" class="nav-item" @click="handleSetting(item)">
              <span class="nav-icon-wrap" :style="{ background: item.bg, color: item.color }">
                <Icon :icon="item.icon" class="nav-icon" />
              </span>
              <span class="nav-copy">
                <span class="nav-label">{{ item.label }}</span>
                <span class="nav-hint">{{ item.hint }}</span>
              </span>
              <Icon icon="solar:alt-arrow-right-linear" class="nav-arrow" />
            </button>
          </div>
        </section>

        <section class="logout-block">
          <ion-button expand="block" fill="clear" class="logout-btn" @click="handleLogout">
            <template v-slot:start>
              <Icon icon="solar:logout-2-linear" />
            </template>
            Se déconnecter
          </ion-button>
          <div class="app-version">Labertha Villa • v1.0.0</div>
        </section>

        <div class="page-bottom-spacer" />
      </div>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonButton, IonContent, IonPage } from '@ionic/vue'
import HeaderBar from '@/components/HeaderBar.vue'
import LoadingOverlay from '@/components/LoadingOverlay.vue'
import { endpoints, getStoredUser, clearAuthSession } from '@/lib/api.js'

const ROLE_LABELS = {
  admin: 'Administrateur',
  receptionist: 'Réceptionniste',
  manager: 'Directeur',
  accountant: 'Comptable',
  staff: 'Personnel',
  owner: 'Propriétaire'
}

export default {
  name: 'ProfileView',
  components: {
    IonButton,
    IonContent,
    IonPage,
    HeaderBar,
    LoadingOverlay
  },
  data() {
    return {
      loadingProfile: true,
      profile: {
        full_name: '...',
        role: '...',
        station: '...',
        email: '...',
        phone: '...',
        username: '...',
        created_label: '...'
      },
      quickNav: [
        { key: 'dashboard', label: 'Tableau de bord', hint: 'Vue d\'ensemble', path: '/', icon: 'solar:home-2-linear', bg: 'rgba(26, 58, 122, 0.10)', color: '#1a3a7a' },
        { key: 'bookings', label: 'Réservations', hint: 'Listes et détails', path: '/bookings', icon: 'solar:calendar-linear', bg: 'rgba(215, 111, 2, 0.10)', color: '#d76f02' },
        { key: 'payments', label: 'Paiements', hint: 'Encaissements &amp; factures', path: '/paiements', icon: 'solar:wallet-money-linear', bg: 'rgba(22, 163, 74, 0.10)', color: '#16a34a' },
        { key: 'rooms', label: 'Chambres &amp; salles', hint: 'État et disponibilités', path: '/rooms', icon: 'solar:bed-linear', bg: 'rgba(215, 111, 2, 0.10)', color: '#d76f02' },
        { key: 'reports', label: 'Rapports', hint: 'KPIs et statistiques', path: '/reports', icon: 'solar:chart-2-linear', bg: 'rgba(26, 58, 122, 0.10)', color: '#1a3a7a' }
      ],
      securityItems: [
        { key: 'password', label: 'Modifier le mot de passe', hint: 'Mettre à jour les identifiants de connexion', side: '', icon: 'solar:lock-password-linear', bg: 'rgba(26, 58, 122, 0.10)', color: '#1a3a7a' },
        { key: 'sessions', label: 'Sessions actives', hint: 'Gérer les appareils connectés', side: '2 actives', icon: 'solar:laptop-smartphone-linear', bg: 'rgba(215, 111, 2, 0.10)', color: '#d76f02' },
        { key: 'twofa', label: 'Double authentification', hint: 'Code OTP par e-mail ou application', side: 'Désactivé', icon: 'solar:shield-keyhole-linear', bg: 'rgba(22, 163, 74, 0.10)', color: '#16a34a' },
        { key: 'logs', label: 'Journal d\'activité', hint: 'Historique des actions du compte', side: '', icon: 'solar:clipboard-list-linear', bg: 'rgba(100, 116, 139, 0.10)', color: '#475569' }
      ],
      settings: [
        { key: 'theme', label: 'Apparence', hint: 'Clair / sombre', icon: 'solar:palette-linear', bg: 'rgba(215, 111, 2, 0.10)', color: '#d76f02' },
        { key: 'lang', label: 'Langue', hint: 'Français', icon: 'solar:global-linear', bg: 'rgba(22, 163, 74, 0.1)', color: '#15803d' },
        { key: 'notif', label: 'Notifications', hint: 'Alertes push &amp; e-mail', icon: 'solar:bell-linear', bg: 'rgba(212, 175, 55, 0.12)', color: '#b8860b' },
        { key: 'help', label: 'Aide &amp; support', hint: 'Documentation et contact', icon: 'solar:help-circle-linear', bg: 'rgba(100, 116, 139, 0.1)', color: '#475569' }
      ]
    }
  },
  computed: {
    userInitials() {
      const name = String(this.profile?.full_name || 'LV').trim()
      if (!name) return 'LV'
      const parts = name.split(/\s+/).filter(Boolean)
      return ((parts[0]?.[0] || '') + (parts[1]?.[0] || parts[0]?.[1] || '')).toUpperCase() || 'LV'
    },
    showLoading() {
      return this.loadingProfile
    }
  },
  methods: {
    goTo(path) {
      if (!path) return
      this.$router.push(path).catch(() => {})
    },
    handleSetting(item) {
      if (!item) return
      this.$ionicToast?.show?.({ message: `${item.label} — À implémenter`, duration: 1800, color: 'primary' })
    },
    handleSecurity(item) {
      if (!item) return
      this.$ionicToast?.show?.({ message: `${item.label} — À implémenter`, duration: 1800, color: 'tertiary' })
    },
    handleLogout() {
      clearAuthSession()
      this.$router.replace('/login').catch(() => {
        try { window.location.hash = '#/login' } catch (_e) {}
      })
    },
    mergeProfileData(data) {
      if (!data || typeof data !== 'object') return
      const rawRole = data.role || data.user_type || data.position || data.job_title || data.type || ''
      const roleLabel = rawRole
        ? (ROLE_LABELS[String(rawRole).toLowerCase()] || rawRole)
        : this.profile.role
      const created = data.date_joined || data.created_at || data.created || null
      let createdLabel = '—'
      if (created) {
        try {
          const d = new Date(created)
          if (!Number.isNaN(d.getTime())) {
            createdLabel = d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
          }
        } catch (_) {}
      }
      const resolveFullName = () => {
        const chain = [
          data.full_name,
          [data.first_name, data.last_name].filter(Boolean).join(' '),
          data.name,
          data.username,
          data.login,
          data.email && String(data.email).split('@')[0]
        ]
        for (const v of chain) {
          const s = (v == null ? '' : String(v)).trim()
          if (s) return s.charAt(0).toUpperCase() + s.slice(1)
        }
        return this.profile.full_name && this.profile.full_name !== '...' ? this.profile.full_name : 'Utilisateur'
      }
      const resolveUsername = () => {
        const chain = [data.username, data.login, data.email, data.full_name, data.name]
        for (const v of chain) {
          const s = (v == null ? '' : String(v)).trim()
          if (s) return s
        }
        return this.profile.username && this.profile.username !== '...' ? this.profile.username : '—'
      }
      const resolveEmail = () => {
        const s = (data.email == null ? '' : String(data.email)).trim()
        if (s) return s
        return this.profile.email && this.profile.email !== '...' ? this.profile.email : '—'
      }
      const resolvePhone = () => {
        const chain = [data.phone, data.phone_number, data.mobile, data.tel, data.telephone]
        for (const v of chain) {
          const s = (v == null ? '' : String(v)).trim()
          if (s) return s
        }
        return this.profile.phone && this.profile.phone !== '...' ? this.profile.phone : '—'
      }
      const resolveStation = () => {
        const chain = [data.station, data.branch, data.location, data.site, data.bureau]
        for (const v of chain) {
          const s = (v == null ? '' : String(v)).trim()
          if (s) return s
        }
        return this.profile.station && this.profile.station !== '...' ? this.profile.station : '—'
      }
      this.profile = {
        full_name: resolveFullName(),
        username: resolveUsername(),
        role: roleLabel || '—',
        station: resolveStation(),
        email: resolveEmail(),
        phone: resolvePhone(),
        created_label: createdLabel
      }
    }
  },
  mounted() {
    const cached = getStoredUser()
    if (cached && typeof cached === 'object') {
      this.mergeProfileData(cached)
    }
    this.loadingProfile = true
    endpoints.me()
      .then((data) => {
        if (data && typeof data === 'object') {
          this.mergeProfileData(data)
        }
      })
      .catch(() => {})
      .finally(() => {
        this.loadingProfile = false
      })
  }
}
</script>

<style scoped>
.profile-page {
  background: #fbf7f2;
}

.profile-content {
  --background: #fbf7f2;
}

.content-shell {
  padding: 0 16px 0;
}

.profile-hero {
  margin-top: 18px;
  padding: 22px 20px;
  border-radius: 26px;
  background:
    radial-gradient(circle at top right, rgba(215, 111, 2, 0.38), transparent 50%),
    linear-gradient(135deg, #1a3a7a 0%, #17336b 60%, #d76f02 140%);
  display: flex;
  align-items: center;
  gap: 16px;
  color: #ffffff;
  box-shadow: 0 22px 42px rgba(26, 58, 122, 0.24);
}

.profile-avatar {
  width: 64px;
  height: 64px;
  border-radius: 22px;
  background: linear-gradient(135deg, #d76f02 0%, #e68a33 100%);
  color: #ffffff;
  border: 2px solid rgba(255, 255, 255, 0.22);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  letter-spacing: 0.08em;
  font-size: 1.2rem;
  flex: 0 0 auto;
  box-shadow: 0 10px 22px rgba(215, 111, 2, 0.35);
}

.profile-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1 1 auto;
}

.profile-name {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.22rem;
  font-weight: 800;
  letter-spacing: 0.005em;
  color: #ffffff;
  line-height: 1.2;
}

.profile-role {
  font-size: 0.85rem;
  color: #d4af37;
  font-weight: 600;
}

.profile-pill {
  margin-top: 2px;
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.86);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.profile-contact-row {
  margin-top: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.contact-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.10);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: rgba(255, 255, 255, 0.90);
  font-size: 0.72rem;
  font-weight: 600;
  max-width: 100%;
}

.contact-ic {
  font-size: 0.9rem;
  color: #d4af37;
  flex: 0 0 auto;
}

.contact-val {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.user-meta-card {
  margin-top: 22px;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 24px;
  padding: 18px;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
}

.meta-head {
  padding: 0 2px;
}

.meta-kicker {
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #64748b;
  font-weight: 700;
}

.meta-title {
  margin: 6px 0 0;
  font-size: 1.05rem;
  font-weight: 800;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
}

.meta-divider {
  height: 1px;
  margin: 12px 2px 14px;
  background: rgba(23, 11, 2, 0.08);
}

.meta-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.meta-row {
  display: grid;
  grid-template-columns: 130px 1fr;
  align-items: center;
  gap: 10px;
  padding: 10px 4px;
  border-bottom: 1px dashed rgba(23,11,2,0.06);
}
.meta-row:last-child { border-bottom: none; }

.meta-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: #64748b;
  letter-spacing: 0.01em;
}

.meta-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: #170b02;
  min-width: 0;
  word-break: break-word;
  text-align: right;
}

.meta-value.mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.84rem;
  background: rgba(23,11,2,0.04);
  display: inline-block;
  margin-left: auto;
  padding: 3px 8px;
  border-radius: 10px;
}

.role-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  background: rgba(215,111,2,0.10);
  color: #d76f02;
  font-weight: 700;
  font-size: 0.78rem;
  border: 1px solid rgba(215,111,2,0.22);
}

.list-block {
  margin-top: 22px;
}

.list-block-kicker {
  padding: 0 4px 10px;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 700;
  color: #170b02;
}

.kicker-chip {
  display: inline-block;
  font-size: 0.68rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #d76f02;
  font-weight: 700;
  padding: 4px 10px;
  border: 1px solid rgba(215, 111, 2, 0.35);
  border-radius: 999px;
  background: rgba(215, 111, 2, 0.06);
}

.nav-list {
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 22px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(23, 11, 2, 0.04);
}

.nav-item {
  width: 100%;
  display: grid;
  grid-template-columns: 40px 1fr auto auto;
  align-items: center;
  gap: 14px;
  padding: 15px 16px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(23, 11, 2, 0.08);
  text-align: left;
  cursor: pointer;
  transition: background 0.18s ease;
}

.nav-item:last-child {
  border-bottom: none;
}

.nav-item:active {
  background: rgba(215, 111, 2, 0.05);
}

.nav-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.nav-icon {
  font-size: 1.05rem;
  width: 22px;
  height: 22px;
}

.nav-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-label {
  font-size: 0.95rem;
  font-weight: 700;
  color: #170b02;
}

.nav-hint {
  font-size: 0.78rem;
  color: #64748b;
}

.nav-side-tag {
  padding: 3px 9px;
  border-radius: 999px;
  background: rgba(23,11,2,0.05);
  color: #475569;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  border: 1px solid rgba(23,11,2,0.08);
  white-space: nowrap;
}

.nav-arrow {
  color: #d76f02;
  font-size: 1rem;
  width: 22px;
  height: 22px;
  flex: 0 0 auto;
}

.logout-block {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.logout-btn {
  --color: #d76f02;
  --border-color: #d76f02;
  --background: transparent;
  --background-hover: transparent;
  --background-active: transparent;
  --border-radius: 18px;
  --padding-top: 14px;
  --padding-bottom: 14px;
  font-weight: 700;
  letter-spacing: 0.01em;
  border: 1.5px solid #d76f02;
  color: #d76f02;
  position: relative;
  overflow: hidden;
  z-index: 0;
  transition: color 0.3s ease, border-color 0.3s ease;
}

.logout-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #d76f02 0%, #e68a33 100%);
  opacity: 0;
  z-index: -1;
  transition: opacity 0.3s ease;
}

.logout-btn:hover {
  color: #ffffff;
  border-color: #d76f02;
}

.logout-btn:hover::before {
  opacity: 1;
}

.app-version {
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 700;
}

.page-bottom-spacer {
  height: 60px;
}

@media (min-width: 768px) {
  .content-shell {
    max-width: 680px;
    margin: 0 auto;
    padding: 0 24px;
  }
  .meta-row { grid-template-columns: 170px 1fr; }
}

@media print {
  ion-header,
  ion-tab-bar,
  .logout-block {
    display: none !important;
  }
  .profile-content { --background: #ffffff; }
  .profile-page { background: #ffffff; }
}
</style>
