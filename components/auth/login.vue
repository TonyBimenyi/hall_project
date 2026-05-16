<template>
  <div class="auth-container">
    <div class="auth-card">

      <h1>Bon retour</h1>
      <p class="subtitle">Connectez-vous pour accéder à votre tableau de bord</p>

      <div class="mode-tabs">
        <button
          class="mode-btn"
          :class="{ active: authMode === 'password' }"
          @click="authMode = 'password'"
          type="button"
        >
          Téléphone + mot de passe
        </button>
        <button
          class="mode-btn"
          :class="{ active: authMode === 'magic' }"
          @click="authMode = 'magic'"
          type="button"
        >
          Lien magique (email)
        </button>
      </div>

      <div v-if="authMode === 'password'" class="mode-panel">
        <label>Téléphone (username)</label>
        <input v-model="username" type="text" placeholder="Ex: 25779382580" />
        <p v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>

        <label>Mot de passe</label>
        <input v-model="password" type="password" placeholder="••••••••" />
        <p v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>

        <button class="submit-btn" @click="login" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Se connecter</span>
        </button>
      </div>

      <div v-else class="mode-panel">
        <label>Email</label>
        <input v-model="magicEmail" type="email" placeholder="Ex: tony@email.com" />
        <p v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</p>

        <button class="submit-btn secondary" @click="requestMagicLink" :disabled="magicLoading">
          <span v-if="magicLoading" class="spinner"></span>
          <span v-else>Recevoir un lien de connexion</span>
        </button>

        <p class="magic-hint">
          Vous recevrez un lien de connexion sécurisé valable 15 minutes.
        </p>
      </div>

      <p class="switch-text">
        Vous n'avez pas de compte ?
        <NuxtLink to="/register" class="btn-signin">S'inscrire</NuxtLink>
    
      </p>

      <!-- Notification component -->
      <Notification />
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import Notification from '~/components/Notification.vue'
import { notify } from '~/composables/useNotification'
import { API_ORIGIN } from '~/composables/useApi'

export default {
  name: "LoginView",
  components: { Notification },
  data() {
    return {
      authMode: 'password',
      username: '',
      password: '',
      magicEmail: '',
      fieldErrors: {},
      loading: false,
      magicLoading: false
    }
  },
  mounted() {
    const token = this.$route?.query?.token
    if (token) {
      this.authMode = 'magic'
      this.verifyMagicToken(String(token))
    }
  },
  methods: {
    async login() {
      // Reset field errors
      this.fieldErrors = {}

      // Simple frontend validation
      if (!this.username) this.fieldErrors.username = 'Le nom d\'utilisateur est requis'
      if (!this.password) this.fieldErrors.password = 'Le mot de passe est requis'
      if (Object.keys(this.fieldErrors).length) return

      this.loading = true
      
      try {
        const phoneNorm = String(this.username || '').replace(/\s+/g, '').replace(/\D/g, '')
        const loginUsername = phoneNorm || this.username

        const response = await axios.post(`${API_ORIGIN}/api/token/`, {
          username: loginUsername,
          password: this.password
        })

        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)

        const me = await axios.get(`${API_ORIGIN}/api/me/`, {
          headers: { Authorization: `Bearer ${response.data.access}` }
        })
        localStorage.setItem('user', JSON.stringify(me.data))

        // Show success notification
        notify('Connexion réussie !', 'success')

        const redirectTo = me.data?.is_staff ? '/admin' : '/dashboard'

        // Redirect to dashboard after a short delay and refresh page
        setTimeout(() => {
          this.$router.push(redirectTo).then(() => {
            window.location.reload()
          })
        }, 500)
      } catch (error) {
        if (error.response && error.response.data) {
          notify(error.response.data.detail || 'Identifiants invalides', 'danger')
        } else {
          notify('Une erreur est survenue. Veuillez réessayer.', 'danger')
        }
      } finally {
        this.loading = false
      }
    },
    async requestMagicLink() {
      this.fieldErrors = {}
      if (!this.magicEmail) {
        this.fieldErrors.email = 'Email requis'
        return
      }

      this.magicLoading = true
      try {
        await axios.post(`${API_ORIGIN}/api/auth/magic-link/request/`, { email: this.magicEmail })
        notify("Lien de connexion envoyé par email.", 'success')
      } catch (error) {
        const detail = error?.response?.data?.detail
        if (detail) {
          notify(detail, 'danger')
        } else {
          notify("Impossible d'envoyer le lien. Réessayez.", 'danger')
        }
      } finally {
        this.magicLoading = false
      }
    },
    async verifyMagicToken(token) {
      this.loading = true
      try {
        const response = await axios.post(`${API_ORIGIN}/api/auth/magic-link/verify/`, { token })

        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)

        const me = await axios.get(`${API_ORIGIN}/api/me/`, {
          headers: { Authorization: `Bearer ${response.data.access}` }
        })
        localStorage.setItem('user', JSON.stringify(me.data))

        notify('Connexion réussie !', 'success')

        const redirectTo = me.data?.is_staff ? '/admin' : (response.data.redirect_to || '/dashboard')
        this.$router.replace({ path: '/login' })
        setTimeout(() => {
          this.$router.push(redirectTo).then(() => {
            window.location.reload()
          })
        }, 300)
      } catch (error) {
        notify(error?.response?.data?.detail || 'Lien invalide ou expiré', 'danger')
      } finally {
        this.loading = false
      }
    }

  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  padding: var(--space-6);
}

.auth-card {
  width: 100%;
  max-width: 450px;
  background: var(--white);
  padding: var(--space-12);
  border-radius: var(--rounded-2xl);
  box-shadow: var(--shadow-xl);
  text-align: center;
}

h1 {
  font-family: var(--font-serif);
  font-size: 2.5rem;
  color: var(--primary);
  margin-bottom: var(--space-2);
}

.subtitle {
  color: var(--gray-500);
  margin-bottom: var(--space-8);
}

.form-group {
  text-align: left;
  margin-bottom: var(--space-6);
}

label {
  display: block;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--gray-700);
  margin-bottom: var(--space-2);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 2px solid var(--gray-100);
  border-radius: var(--rounded-lg);
  font-size: 1rem;
  transition: var(--transition-fast);
}

input:focus {
  border-color: var(--accent);
  background: var(--gray-50);
}

.mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
  margin: 1.2rem 0 1.1rem;
}

.mode-btn {
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
  color: var(--gray-700);
  padding: 0.75rem 0.9rem;
  border-radius: var(--rounded-lg);
  font-weight: 800;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: var(--transition-fast);
}

.mode-btn:hover {
  border-color: var(--accent);
}

.mode-btn.active {
  background: var(--primary);
  color: var(--white);
  border-color: var(--primary);
}

.mode-panel {
  text-align: left;
}

.field-error {
  color: var(--danger);
  font-size: 0.8rem;
  margin-top: var(--space-1);
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: var(--primary);
  color: var(--white);
  border-radius: var(--rounded-lg);
  font-weight: 700;
  font-size: 1.1rem;
  margin-top: var(--space-4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
}

.submit-btn.secondary {
  background: var(--accent);
}

.magic-hint {
  margin: 0.75rem 0 0;
  color: var(--gray-500);
  font-size: 0.92rem;
  line-height: 1.35;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.switch-text {
  margin-top: var(--space-8);
  color: var(--gray-500);
  font-size: 0.9rem;
}

.btn-signin {
  color: var(--primary);
  font-weight: 700;
  margin-left: var(--space-2);
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--white);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
