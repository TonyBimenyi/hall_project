<template>
  <div class="auth-container">
    <div class="auth-card">

      <h1>{{ t('auth.register.title') }}</h1>
      <p class="subtitle">{{ t('auth.register.subtitle') }}</p>

      <label>{{ t('auth.register.phoneLabel') }}</label>
      <input v-model="username" type="text" :placeholder="t('auth.register.phonePlaceholder')" />
      <p v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</p>

      <label>{{ t('auth.register.firstName') }}</label>
      <input v-model="first_name" type="text" placeholder="Jean" />
      <p v-if="fieldErrors.first_name" class="field-error">{{ fieldErrors.first_name }}</p>

      <label>{{ t('auth.register.lastName') }}</label>
      <input v-model="last_name" type="text" placeholder="Dupont" />
      <p v-if="fieldErrors.last_name" class="field-error">{{ fieldErrors.last_name }}</p>

      <label>{{ t('auth.register.email') }}</label>
      <input v-model="email" type="email" placeholder="jean.dupont@exemple.com" />
      <p v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</p>

      <label>{{ t('auth.register.password') }}</label>
      <input v-model="password" type="password" placeholder="••••••••" />
      <p v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</p>

      <label>{{ t('auth.register.password2') }}</label>
      <input v-model="password2" type="password" placeholder="••••••••" />
      <p v-if="fieldErrors.password2" class="field-error">{{ fieldErrors.password2 }}</p>

      <button class="submit-btn" @click="register" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        <span v-else>{{ t('auth.register.submit') }}</span>
      </button>

      <p class="switch-text">
        {{ t('auth.register.haveAccount') }}
        <NuxtLink :to="localePath('/login')" class="btn-signin">{{ t('auth.register.signIn') }}</NuxtLink>
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
import { API_ORIGIN } from '~/composables/useApi'

const { t } = useI18n()
const localePath = useLocalePath()
const router = useRouter()

const username = ref('')
const first_name = ref('')
const last_name = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
const fieldErrors = ref({})
const loading = ref(false)

const register = async () => {
  fieldErrors.value = {}

  const phone = String(username.value || '').replace(/\s+/g, '')
  const phoneNorm = phone.replace(/\D/g, '')

  if (!phoneNorm) fieldErrors.value.username = t('auth.register.validation.phoneRequired')
  else if (phoneNorm.length < 8) fieldErrors.value.username = t('auth.register.validation.phoneInvalid')

  if (!first_name.value) fieldErrors.value.first_name = t('auth.register.validation.firstNameRequired')
  if (!last_name.value) fieldErrors.value.last_name = t('auth.register.validation.lastNameRequired')
  if (!email.value) fieldErrors.value.email = t('auth.register.validation.emailRequired')
  if (!password.value) fieldErrors.value.password = t('auth.register.validation.passwordRequired')
  if (!password2.value) fieldErrors.value.password2 = t('auth.register.validation.password2Required')
  if (password.value && password2.value && password.value !== password2.value) {
    fieldErrors.value.password2 = t('auth.register.validation.passwordMismatch')
  }

  if (Object.keys(fieldErrors.value).length) return

  loading.value = true
  try {
    await axios.post(`${API_ORIGIN}/api/register/`, {
      phone: phoneNorm,
      first_name: first_name.value,
      last_name: last_name.value,
      email: email.value,
      password: password.value,
    })

    notify(t('auth.register.notify.success'), 'success')

    setTimeout(() => {
      router.push(localePath('/login'))
    }, 2000)
  } catch (error) {
    if (error.response && error.response.data) {
      fieldErrors.value = error.response.data
      notify(t('auth.register.notify.failed'), 'danger')
    } else {
      notify(t('auth.register.notify.genericError'), 'danger')
    }
  } finally {
    loading.value = false
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
