<template>
  <div class="auth-container">
    <div class="auth-card">

      <h1>{{ t('auth.login.title') }}</h1>
      <p class="subtitle">{{ t('auth.login.subtitle') }}</p>

      <div class="mode-tabs">
        <button
          class="mode-btn"
          :class="{ active: authMode === 'password' }"
          @click="authMode = 'password'"
          type="button"
        >
          {{ t('auth.login.tabPassword') }}
        </button>
        <button
          class="mode-btn"
          :class="{ active: authMode === 'magic' }"
          @click="authMode = 'magic'"
          type="button"
        >
          {{ t('auth.login.tabMagic') }}
        </button>
      </div>

      <div v-if="authMode === 'password'" class="mode-panel">
        <label>{{ t('auth.login.phoneLabel') }}</label>
        <input v-model="username" type="text" :placeholder="t('auth.login.phonePlaceholder')" />
        <p v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>

        <label>{{ t('auth.login.passwordLabel') }}</label>
        <input v-model="password" type="password" placeholder="••••••••" />
        <p v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>

        <button class="submit-btn" @click="login" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>{{ t('auth.login.submit') }}</span>
        </button>
      </div>

      <div v-else class="mode-panel">
        <label>{{ t('auth.login.emailLabel') }}</label>
        <input v-model="magicEmail" type="email" :placeholder="t('auth.login.emailPlaceholder')" />
        <p v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</p>

        <button class="submit-btn secondary" @click="requestMagicLink" :disabled="magicLoading">
          <span v-if="magicLoading" class="spinner"></span>
          <span v-else>{{ t('auth.login.magicSubmit') }}</span>
        </button>

        <p class="magic-hint">
          {{ t('auth.login.magicHint') }}
        </p>
      </div>

      <p class="switch-text">
        {{ t('auth.login.noAccount') }}
        <NuxtLink :to="localePath('/register')" class="btn-signin">{{ t('auth.login.signUp') }}</NuxtLink>
    
      </p>

      <!-- Notification component -->
      <Notification />
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import Notification from '~/components/Notification.vue'
import { notify } from '~/composables/useNotification'
import { getApiOrigin } from '~/composables/useApi'

const { t } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const router = useRouter()

const authMode = ref('password')
const username = ref('')
const password = ref('')
const magicEmail = ref('')
const fieldErrors = ref({})
const loading = ref(false)
const magicLoading = ref(false)

const login = async () => {
  fieldErrors.value = {}
  if (!username.value) fieldErrors.value.username = t('auth.login.validation.usernameRequired')
  if (!password.value) fieldErrors.value.password = t('auth.login.validation.passwordRequired')
  if (Object.keys(fieldErrors.value).length) return

  loading.value = true
  try {
    const phoneNorm = String(username.value || '').replace(/\s+/g, '').replace(/\D/g, '')
    const loginUsername = phoneNorm || username.value

    const response = await axios.post(`${getApiOrigin()}/api/token/`, {
      username: loginUsername,
      password: password.value
    })

    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)

    const me = await axios.get(`${getApiOrigin()}/api/me/`, {
      headers: { Authorization: `Bearer ${response.data.access}` }
    })
    localStorage.setItem('user', JSON.stringify(me.data))

    notify(t('auth.login.notify.success'), 'success')

    const redirectTo = me.data?.is_staff ? localePath('/admin') : localePath('/dashboard')
    setTimeout(() => {
      router.push(redirectTo).then(() => {
        window.location.reload()
      })
    }, 500)
  } catch (error) {
    if (error.response && error.response.data) {
      notify(error.response.data.detail || t('auth.login.notify.invalidCredentials'), 'danger')
    } else {
      notify(t('auth.login.notify.genericError'), 'danger')
    }
  } finally {
    loading.value = false
  }
}

const requestMagicLink = async () => {
  fieldErrors.value = {}
  if (!magicEmail.value) {
    fieldErrors.value.email = t('auth.login.validation.emailRequired')
    return
  }

  magicLoading.value = true
  try {
    await axios.post(`${getApiOrigin()}/api/auth/magic-link/request/`, { email: magicEmail.value })
    notify(t('auth.login.notify.magicSent'), 'success')
  } catch (error) {
    const detail = error?.response?.data?.detail
    if (detail) {
      notify(detail, 'danger')
    } else {
      notify(t('auth.login.notify.magicSendFail'), 'danger')
    }
  } finally {
    magicLoading.value = false
  }
}

const verifyMagicToken = async (token) => {
  loading.value = true
  try {
    const response = await axios.post(`${getApiOrigin()}/api/auth/magic-link/verify/`, { token })

    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)

    const me = await axios.get(`${getApiOrigin()}/api/me/`, {
      headers: { Authorization: `Bearer ${response.data.access}` }
    })
    localStorage.setItem('user', JSON.stringify(me.data))

    notify(t('auth.login.notify.success'), 'success')

    const redirectTo = me.data?.is_staff ? localePath('/admin') : localePath(response.data.redirect_to || '/dashboard')
    router.replace(localePath('/login'))
    setTimeout(() => {
      router.push(redirectTo).then(() => {
        window.location.reload()
      })
    }, 300)
  } catch (error) {
    notify(error?.response?.data?.detail || t('auth.login.notify.magicInvalid'), 'danger')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const token = route?.query?.token
  if (token) {
    authMode.value = 'magic'
    verifyMagicToken(String(token))
  }
})
</script>

<style scoped>
.auth-container {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  /* background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%); */
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
  background: var(--primary);
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
