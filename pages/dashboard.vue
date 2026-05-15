<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <!-- LOGIN GATE -->
      <div v-if="!isLoggedIn" class="login-gate card">
        <h2>Connexion requise</h2>
        <p>
          Connectez-vous pour accéder à votre tableau de bord et voir vos réservations.
        </p>
        <div class="login-actions">
          <NuxtLink to="/login" class="btn btn-primary btn-sm">Se connecter</NuxtLink>
          <NuxtLink to="/register" class="btn btn-outline btn-sm">Créer un compte</NuxtLink>
        </div>
      </div>

      <!-- DASHBOARD -->
      <template v-else>
        <div class="head-row">
          <div>
            <h2 class="page-title">Bonjour {{ displayName }}</h2>
            <p class="page-subtitle">
              Suivez vos réservations et vos paiements en un coup d’œil.
            </p>
          </div>

          <NuxtLink to="/book" class="btn btn-primary">
            Nouvelle réservation
          </NuxtLink>
        </div>

        <!-- STATS -->
        <div class="stats-grid">
          <article class="card stat-card">
            <span class="label">Mes réservations</span>
            <strong>{{ myBookings.length }}</strong>
          </article>

          <article class="card stat-card">
            <span class="label">En attente</span>
            <strong>{{ pendingCount }}</strong>
          </article>

          <article class="card stat-card">
            <span class="label">Confirmées</span>
            <strong>{{ confirmedCount }}</strong>
          </article>

          <article class="card stat-card">
            <span class="label">Montant total</span>
            <strong>{{ totalAmount.toLocaleString() }} Fbu</strong>
          </article>
        </div>

        <!-- TABLE -->
        <div class="card table-card">
          <div class="table-head">
            <h3>Historique de réservation</h3>
            <button class="btn btn-outline btn-sm" @click="fetchBookings">
              Actualiser
            </button>
          </div>

          <div class="table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>Référence</th>
                  <th>Événement</th>
                  <th>Période</th>
                  <th>Montant</th>
                  <th>Statut</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="booking in myBookings" :key="booking.id">
                  <td>#BR-{{ booking.id }}</td>
                  <td>{{ booking.event_type }}</td>
                  <td>{{ booking.start_date }} → {{ booking.end_date }}</td>
                  <td>{{ Number(booking.total_price || 0).toLocaleString() }} Fbu</td>
                  <td>
                    <span class="badge" :class="statusClass(booking.status)">
                      {{ statusText(booking.status) }}
                    </span>
                  </td>
                </tr>

                <tr v-if="!loading && myBookings.length === 0">
                  <td colspan="5" class="empty">Aucune réservation trouvée.</td>
                </tr>

                <tr v-if="loading">
                  <td colspan="5" class="empty">Chargement...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card table-card">
          <div class="table-head">
            <h3>Sécurité</h3>
          </div>
          <p class="security-subtitle">
            Optionnel : définissez un mot de passe permanent. Sinon, vous pouvez continuer à vous connecter via lien magique.
          </p>

          <div class="security-form">
            <div class="security-grid">
              <div class="security-field">
                <label>Nouveau mot de passe</label>
                <input type="password" v-model="newPassword" placeholder="Minimum 6 caractères" />
              </div>

              <div class="security-field">
                <label>Confirmer le mot de passe</label>
                <input type="password" v-model="confirmPassword" placeholder="Répétez le mot de passe" />
              </div>
            </div>

            <p v-if="passwordError" class="field-error">{{ passwordError }}</p>

            <div class="security-actions">
              <button class="btn btn-primary btn-sm" @click="setPassword" :disabled="passwordLoading">
                {{ passwordLoading ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script>
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'

export default {
  data() {
    return {
      loading: false,
      bookings: [],
      currentUser: {},
      isLoggedIn: false,
      newPassword: '',
      confirmPassword: '',
      passwordLoading: false,
      passwordError: ''
    }
  },

  computed: {
    myBookings() {
      return this.bookings
    },

    pendingCount() {
      return this.myBookings.filter(b => b.status === 'pending').length
    },

    confirmedCount() {
      return this.myBookings.filter(b => b.status === 'confirmed').length
    },

    totalAmount() {
      return this.myBookings.reduce(
        (sum, b) => sum + Number(b.total_price || 0),
        0
      )
    },

    displayName() {
      const first = this.currentUser?.first_name || ''
      const last = this.currentUser?.last_name || ''

      if (!first && !last) return 'Client'

      const safeFirst = first ? first.charAt(0).toUpperCase() + first.slice(1) : ''
      const safeLast = last ? last.charAt(0).toUpperCase() + last.slice(1) : ''

      return `${safeFirst} ${safeLast}`.trim()
    }
  },

  methods: {
    statusClass(status) {
      if (status === 'confirmed') return 'success'
      if (status === 'cancelled') return 'danger'
      if (status === 'paid') return 'info'
      return 'warning'
    },

    statusText(status) {
      if (status === 'confirmed') return 'Confirmée'
      if (status === 'cancelled') return 'Annulée'
      if (status === 'paid') return 'Payée'
      return 'En attente'
    },

    async fetchBookings() {
      if (!this.isLoggedIn) return

      this.loading = true

      try {
        const response = await api.get('bookings/')
        this.bookings = Array.isArray(response.data) ? response.data : []
      } catch {
        notify('Impossible de charger les réservations', 'danger')
        this.bookings = []
      } finally {
        this.loading = false
      }
    },
    async setPassword() {
      if (!this.isLoggedIn) return
      this.passwordError = ''
      if (!this.newPassword || this.newPassword.length < 6) {
        this.passwordError = 'Mot de passe (min 6 caractères) requis'
        return
      }
      if (this.newPassword !== this.confirmPassword) {
        this.passwordError = 'Les mots de passe ne correspondent pas'
        return
      }

      this.passwordLoading = true
      try {
        await api.post('auth/set-password/', { password: this.newPassword })
        this.newPassword = ''
        this.confirmPassword = ''
        notify('Mot de passe défini avec succès', 'success')
      } catch (e) {
        const msg = e?.response?.data?.password || e?.response?.data?.detail || 'Impossible de définir le mot de passe'
        this.passwordError = msg
        notify(msg, 'danger')
      } finally {
        this.passwordLoading = false
      }
    }
  },

  mounted() {
    try {
      this.currentUser = JSON.parse(localStorage.getItem('user') || '{}')
    } catch {
      this.currentUser = {}
    }

    this.isLoggedIn = !!localStorage.getItem('access_token')

    if (this.isLoggedIn) {
      this.fetchBookings()
    }
  }
}
</script>
<style scoped>
.client-page {
  background: #f8fafc;
  min-height: 100vh;
  padding: 5rem 0 3rem;
}

.container {
  max-width: 1160px;
  margin: 0 auto;
  padding: 0 1rem;
}

.head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.page-title {
  margin: 0;
  font-size: 1.5rem;
  color: #0f172a;
}

.page-subtitle {
  margin-top: .2rem;
  color: #64748b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.stat-card .label {
  color: #64748b;
  font-size: .84rem;
}

.stat-card strong {
  display: block;
  margin-top: .4rem;
  color: #0f172a;
  font-size: 1.35rem;
}

.table-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1rem;
}

.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: .8rem;
}

.table-head h3 {
  margin: 0;
  font-size: 1.1rem;
}

.table-wrap {
  overflow-x: auto;
}

.login-gate {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.2rem;
  margin-bottom: 1rem;
}

.login-gate h2 {
  margin: 0 0 .4rem;
  font-size: 1.1rem;
}

.login-gate p {
  color: #64748b;
  margin: 0 0 .75rem;
}

.login-actions {
  display: flex;
  gap: .6rem;
  flex-wrap: wrap;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 1rem;
}

.security-subtitle {
  margin: 0 0 0.9rem;
  color: #64748b;
  font-size: 0.95rem;
  line-height: 1.35;
}

.security-form {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #ffffff;
  padding: 1rem;
}

.security-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
}

.security-field label {
  display: block;
  font-size: 0.82rem;
  font-weight: 800;
  color: #334155;
  margin-bottom: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.security-field input {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 0.75rem 0.9rem;
  outline: none;
  background: #fff;
}

.security-field input:focus {
  border-color: #cbd5e1;
  box-shadow: 0 0 0 4px rgba(226, 232, 240, 0.7);
}

.security-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 0.9rem;
}

.field-error {
  margin: 0.75rem 0 0;
  color: #b91c1c;
  font-weight: 700;
  font-size: 0.9rem;
}

@media (max-width: 960px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .head-row {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 560px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .security-grid {
    grid-template-columns: 1fr;
  }
}
</style>
