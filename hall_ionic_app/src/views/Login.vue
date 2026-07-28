<template>
  <ion-page class="login-page">
    <ion-content class="login-content" fullscreen>
      <div class="login-shell">
        <div class="login-brand">
          <div class="login-logo-img">
            <img src="/logo.png" alt="Labertha Villa" class="login-logo" />
          </div>
          <div class="login-headlines">
            <div class="login-eyebrow">Administration</div>
            <h1 class="login-title">Labertha Villa</h1>
            <p class="login-subtitle">Connectez-vous pour gérer les réservations, l'inventaire et les revenus.</p>
          </div>
        </div>

        <div class="login-card">
          <div v-if="error" class="login-error">
            <Icon icon="solar:danger-triangle-linear" class="login-error-icon" />
            <span>{{ error }}</span>
          </div>

          <form @submit.prevent="handleLogin" class="login-form" novalidate>
            <div class="field">
              <label class="field-label">Identifiant</label>
              <div class="field-control">
                <Icon icon="solar:user-linear" class="field-prefix" />
                <input
                  ref="usernameInput"
                  v-model.trim="form.username"
                  type="text"
                  autocomplete="username"
                  class="field-input"
                  placeholder="Nom d'utilisateur, email ou téléphone"
                  :disabled="submitting"
                  required
                />
              </div>
            </div>

            <div class="field">
              <label class="field-label">Mot de passe</label>
              <div class="field-control">
                <Icon icon="solar:lock-password-linear" class="field-prefix" />
                <input
                  v-model="form.password"
                  :type="passwordVisible ? 'text' : 'password'"
                  autocomplete="current-password"
                  class="field-input"
                  placeholder="Mot de passe"
                  :disabled="submitting"
                  required
                  @keyup.enter="$event.preventDefault(); handleLogin()"
                />
                <button type="button" class="field-suffix" @click="togglePassword" aria-label="Afficher / masquer le mot de passe">
                  <Icon :icon="passwordVisible ? 'solar:eye-closed-linear' : 'solar:eye-linear'" class="field-suffix-icon" />
                </button>
              </div>
            </div>

            <button type="submit" class="login-submit" :disabled="submitting || !canSubmit">
              <span v-if="!submitting" class="login-submit-label">
                <Icon icon="solar:login-3-linear" class="login-submit-icon" />
                Se connecter
              </span>
              <span v-else class="login-submit-loading">
                <Icon icon="solar:loader-linear" class="spin" />
                Connexion en cours…
              </span>
            </button>
          </form>

          <div class="login-foot">
            <Icon icon="solar:shield-check-linear" class="login-foot-icon" />
            <span>Connexion sécurisée · Même compte que le portail web</span>
          </div>
        </div>
      </div>
    </ion-content>
  </ion-page>
</template>

<script>
import { IonContent, IonPage } from '@ionic/vue'
import { loginWithPassword } from '@/lib/api.js'

export default {
  name: 'Login',
  components: {
    IonContent,
    IonPage
  },
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      passwordVisible: false,
      submitting: false,
      error: ''
    }
  },
  computed: {
    canSubmit() {
      return this.form.username.length > 0 && this.form.password.length > 0
    }
  },
  methods: {
    togglePassword() {
      this.passwordVisible = !this.passwordVisible
    },
    async handleLogin() {
      if (!this.canSubmit || this.submitting) return
      this.submitting = true
      this.error = ''

      try {
        const result = await loginWithPassword({
          username: this.form.username,
          password: this.form.password
        })
        const hasUser = !!(result && result.user)
        const redirectTo = '/'
        if (hasUser) {
          this.$router.replace(redirectTo).catch(() => {})
          return
        }
        this.$router.replace(redirectTo).catch(() => {})
      } catch (err) {
        const status = err?.response?.status
        const detail = err?.response?.data?.detail
        const message = err?.message || ''

        if (status === 400 || status === 401 || status === 403) {
          if (detail && typeof detail === 'string') {
            this.error = detail
          } else if (typeof detail === 'object' && detail) {
            const first = Object.values(detail)[0]
            this.error = Array.isArray(first) ? first[0] : (first || 'Identifiants incorrects.')
          } else {
            this.error = 'Identifiants incorrects. Vérifiez votre nom d’utilisateur et votre mot de passe.'
          }
        } else if (!status && /Network Error|timeout|timed out|Failed to fetch/i.test(message)) {
          this.error = 'Impossible de contacter le serveur. Vérifiez votre connexion internet.'
        } else if (status && (status === 404 || status >= 500)) {
          this.error = `Le serveur a renvoyé une erreur (${status}). Veuillez réessayer plus tard.`
        } else {
          this.error = message || 'Une erreur est survenue lors de la connexion.'
        }
      } finally {
        this.submitting = false
      }
    }
  },
  mounted() {
    try {
      if (this.$refs?.usernameInput) {
        this.$refs.usernameInput.focus()
      }
    } catch (_e) {}
  }
}
</script>

<style scoped>
.login-page,
.login-content {
  --background: transparent;
  background:
    radial-gradient(1200px 800px at -10% -20%, rgba(26, 58, 122, 0.22), transparent 60%),
    radial-gradient(900px 700px at 110% 10%, rgba(215, 111, 2, 0.16), transparent 55%),
    radial-gradient(700px 500px at 50% 110%, rgba(212, 175, 55, 0.12), transparent 60%),
    linear-gradient(180deg, #fbf7f2 0%, #f6f0e7 55%, #f0e7d7 100%);
}

.login-shell {
  min-height: 100vh;
  padding: 44px 22px calc(40px + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  gap: 32px;
  max-width: 460px;
  margin: 0 auto;
}

.login-brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 16px;
}

.login-logo-img {
  width: 88px;
  height: 88px;
  border-radius: 22px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(23, 11, 2, 0.08);
  box-shadow: 0 18px 40px -18px rgba(215, 111, 2, 0.35), 0 10px 24px rgba(23, 11, 2, 0.08);
  padding: 10px;
}

.login-logo {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
}

.login-headlines {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.login-eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 0.66rem;
  font-weight: 700;
  color: var(--primary, #d76f02);
}

.login-title {
  margin: 0;
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 800;
  font-size: 2.25rem;
  letter-spacing: -0.015em;
  color: var(--primary, #d76f02);
}

.login-subtitle {
  margin: 0;
  font-size: 0.94rem;
  line-height: 1.55;
  color: var(--gray-600, #475569);
  max-width: 36ch;
}

.login-card {
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 22px;
  padding: 24px 22px;
  border: 1px solid rgba(23, 11, 2, 0.07);
  box-shadow:
    0 24px 60px -22px rgba(23, 11, 2, 0.22),
    0 0 0 1px rgba(255, 255, 255, 0.6) inset;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.login-error {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.22);
  color: #991b1b;
  font-size: 0.86rem;
  line-height: 1.45;
}

.login-error-icon {
  width: 18px;
  height: 18px;
  flex: 0 0 18px;
  margin-top: 1px;
  color: #dc2626;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--primary-dark, #170b02);
  text-transform: uppercase;
  margin-left: 2px;
}

.field-control {
  position: relative;
  display: flex;
  align-items: center;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.12);
  border-radius: 13px;
  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.field-control:focus-within {
  border-color: rgba(215, 111, 2, 0.7);
  box-shadow: 0 0 0 4px rgba(215, 111, 2, 0.10);
  background: #ffffff;
}

.field-prefix {
  position: absolute;
  left: 13px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--gray-500, #64748b);
}

.field-input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  padding: 14px 42px 14px 42px;
  font-size: 0.96rem;
  color: var(--primary-dark, #170b02);
  font-family: inherit;
  letter-spacing: 0.005em;
}

.field-input::placeholder {
  color: var(--gray-400, #94a3b8);
}

.field-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.field-suffix {
  position: absolute;
  right: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: transparent;
  border: 0;
  display: grid;
  place-items: center;
  cursor: pointer;
  color: var(--gray-500, #64748b);
  transition: background 0.15s ease, color 0.15s ease;
}

.field-suffix:hover,
.field-suffix:active {
  background: rgba(23, 11, 2, 0.06);
  color: var(--primary-dark, #170b02);
}

.field-suffix-icon {
  width: 18px;
  height: 18px;
}

.login-submit {
  margin-top: 4px;
  min-height: 50px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--primary, #d76f02) 0%, #b85e02 100%);
  color: #ffffff;
  font-size: 0.96rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 14px 30px -10px rgba(215, 111, 2, 0.55), 0 1px 0 rgba(255, 255, 255, 0.25) inset;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.login-submit:hover,
.login-submit:active {
  transform: translateY(-1px);
  box-shadow: 0 18px 34px -10px rgba(215, 111, 2, 0.58);
}

.login-submit:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.login-submit-icon {
  width: 18px;
  height: 18px;
}

.login-submit-loading,
.login-submit-label {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.login-submit .spin {
  animation: login-spin 0.9s linear infinite;
  width: 18px;
  height: 18px;
}

@keyframes login-spin {
  to { transform: rotate(360deg); }
}

.login-foot {
  margin-top: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--gray-500, #64748b);
  font-size: 0.78rem;
  text-align: center;
  line-height: 1.4;
}

.login-foot-icon {
  width: 16px;
  height: 16px;
  color: var(--accent-dark, #b8860b);
}
</style>
