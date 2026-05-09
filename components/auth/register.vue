<template>
  <div class="auth-container">
    <div class="auth-card">

      <h1>Créer un compte</h1>
      <p class="subtitle">Rejoignez-nous et commencez dès aujourd'hui</p>

      <label>Téléphone (chiffres uniquement)</label>
      <input v-model="username" type="text" placeholder="Ex: 25779382580" />
      <p v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>

      <label>Prénom</label>
      <input v-model="first_name" type="text" placeholder="Jean" />
      <p v-if="fieldErrors.first_name" class="field-error">{{ fieldErrors.first_name }}</p>

      <label>Nom</label>
      <input v-model="last_name" type="text" placeholder="Dupont" />
      <p v-if="fieldErrors.last_name" class="field-error">{{ fieldErrors.last_name }}</p>

      <label>Email</label>
      <input v-model="email" type="email" placeholder="jean.dupont@exemple.com" />
      <p v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</p>

      <label>Mot de passe</label>
      <input v-model="password" type="password" placeholder="••••••••" />
      <p v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>

      <label>Confirmer le mot de passe</label>
      <input v-model="password2" type="password" placeholder="••••••••" />
      <p v-if="fieldErrors.password2" class="field-error">{{ fieldErrors.password2 }}</p>

      <button class="submit-btn" @click="register" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        <span v-else>S'inscrire</span>
      </button>

      <p class="switch-text">
        Vous avez déjà un compte ?
        <NuxtLink to="/login" class="btn-signin">Se connecter</NuxtLink>
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
  name: "RegisterView",
  components: { Notification },
  data() {
    return {
      username: '',
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      password2: '',
      fieldErrors: {},
      loading: false
    }
  },
  methods: {
    async register() {
      this.fieldErrors = {}

      const phone = String(this.username || '').replace(/\s+/g, '')
      const phoneNorm = phone.replace(/\D/g, '')

      // Frontend validation
      if (!phoneNorm) this.fieldErrors.username = 'Le numéro de téléphone est requis'
      else if (phoneNorm.length < 8) this.fieldErrors.username = 'Numéro de téléphone invalide'

      if (!this.first_name) this.fieldErrors.first_name = 'Le prénom est requis'
      if (!this.last_name) this.fieldErrors.last_name = 'Le nom est requis'
      if (!this.email) this.fieldErrors.email = 'L\'email est requis'
      if (!this.password) this.fieldErrors.password = 'Le mot de passe est requis'
      if (!this.password2) this.fieldErrors.password2 = 'La confirmation du mot de passe est requise'
      if (this.password && this.password2 && this.password !== this.password2) {
        this.fieldErrors.password2 = "Les mots de passe ne correspondent pas"
      }

      if (Object.keys(this.fieldErrors).length) return

      this.loading = true

      try {
        await axios.post(`${API_ORIGIN}/api/register/`, {
          phone: phoneNorm,
          first_name: this.first_name,
          last_name: this.last_name,
          email: this.email,
          password: this.password,
        })

        // Show success notification
        notify('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')

        // Redirect to login after a short delay
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (error) {
        if (error.response && error.response.data) {
          // Handle specific field errors from backend if any
          this.fieldErrors = error.response.data
          notify('Échec de l\'inscription. Veuillez vérifier les champs.', 'danger')
        } else {
          notify('Une erreur est survenue. Veuillez réessayer.', 'danger')
        }
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
  padding: var(--space-12) var(--space-6);
}

.auth-card {
  width: 100%;
  max-width: 500px;
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  text-align: left;
}

.form-group {
  margin-bottom: var(--space-4);
}

.form-group.full {
  grid-column: span 2;
}

label {
  display: block;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--gray-700);
  margin-bottom: var(--space-1);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--gray-100);
  border-radius: var(--rounded-lg);
  font-size: 0.95rem;
  transition: var(--transition-fast);
}

input:focus {
  border-color: var(--accent);
  background: var(--gray-50);
}

.field-error {
  color: var(--danger);
  font-size: 0.75rem;
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
  margin-top: var(--space-6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-3);
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

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  .form-group.full {
    grid-column: span 1;
  }
}
</style>
