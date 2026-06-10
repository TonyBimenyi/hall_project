<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <!-- LOGIN GATE -->
      <div v-if="!isLoggedIn" class="login-gate card">
        <h2>{{ $t('dashboard.loginRequired') }}</h2>
        <p>{{ $t('dashboard.loginText') }}</p>
        <div class="login-actions">
          <NuxtLink :to="localePath('/login')" class="btn btn-primary btn-sm">{{ $t('dashboard.signIn') }}</NuxtLink>
          <NuxtLink :to="localePath('/register')" class="btn btn-outline btn-sm">{{ $t('dashboard.createAccount') }}</NuxtLink>
        </div>
      </div>

      <!-- DASHBOARD -->
      <template v-else>
        <div class="head-row">
          <div>
            <h2 class="page-title">{{ $t('dashboard.hello', { name: displayName }) }}</h2>
            <p class="page-subtitle">{{ $t('dashboard.subtitle') }}</p>
          </div>

          <NuxtLink :to="localePath('/book')" class="btn btn-primary">{{ $t('dashboard.newBooking') }}</NuxtLink>
        </div>

        <!-- STATS -->
        <div class="stats-grid">
          <article class="card stat-card">
            <span class="label">{{ $t('dashboard.myBookings') }}</span>
            <strong>{{ displayBookingsCount }}</strong>
          </article>

          <article class="card stat-card">
            <span class="label">{{ $t('dashboard.pending') }}</span>
            <strong>{{ displayPendingCount }}</strong>
          </article>

          <article class="card stat-card">
            <span class="label">{{ $t('dashboard.confirmed') }}</span>
            <strong>{{ displayConfirmedCount }}</strong>
          </article>

          <article class="card stat-card">
            <span class="label">{{ $t('dashboard.totalAmount') }}</span>
            <strong>{{ formatMoney(displayTotalAmount) }}</strong>
          </article>
        </div>

        <!-- TABLE -->
        <div class="card table-card">
          <div class="table-head">
            <h3>{{ $t('dashboard.history') }}</h3>
            <button class="btn btn-outline btn-sm" @click="fetchBookings">
              {{ $t('dashboard.refresh') }}
            </button>
          </div>

          <div class="table-wrap">
            <table class="admin-table">
              <thead>
                <tr>
                  <th>{{ $t('dashboard.table.reference') }}</th>
                  <th>{{ $t('dashboard.table.event') }}</th>
                  <th>{{ $t('dashboard.table.period') }}</th>
                  <th>{{ $t('dashboard.table.amount') }}</th>
                  <th>{{ $t('dashboard.table.status') }}</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="booking in myBookings" :key="booking.id">
                  <td>#LV-{{ booking.id }}</td>
                  <td>{{ eventTypeText(booking.event_type) }}</td>
                  <td>{{ booking.start_date }} → {{ booking.end_date }}</td>
                  <td>{{ formatMoney(booking.total_price) }}</td>
                  <td>
                    <span class="badge" :class="statusClass(booking.status)">
                      {{ statusText(booking.status) }}
                    </span>
                  </td>
                </tr>

                <tr v-if="!loading && myBookings.length === 0">
                  <td colspan="5" class="empty">{{ $t('dashboard.empty') }}</td>
                </tr>

                <tr v-if="loading">
                  <td colspan="5" class="empty">{{ $t('dashboard.loading') }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="card table-card">
          <div class="table-head">
            <h3>{{ $t('dashboard.security') }}</h3>
          </div>
          <p class="security-subtitle">
            {{ $t('dashboard.securitySubtitle') }}
          </p>

          <div class="security-form">
            <div class="security-grid">
              <div class="security-field">
                <label>{{ $t('dashboard.newPassword') }}</label>
                <input type="password" v-model="newPassword" :placeholder="$t('dashboard.minChars')" />
              </div>

              <div class="security-field">
                <label>{{ $t('dashboard.confirmPassword') }}</label>
                <input type="password" v-model="confirmPassword" :placeholder="$t('dashboard.repeatPassword')" />
              </div>
            </div>

            <p v-if="passwordError" class="field-error">{{ passwordError }}</p>

            <div class="security-actions">
              <button class="btn btn-primary btn-sm" @click="setPassword" :disabled="passwordLoading">
                {{ passwordLoading ? $t('dashboard.saving') : $t('dashboard.save') }}
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </section>
</template>

<script setup>
import { useMoney } from '~/composables/useMoney'

const { formatMoney } = useMoney()
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'

const localePath = useLocalePath()
const { t } = useI18n()

const loading = ref(false)
const bookings = ref([])
const currentUser = ref({})
const isLoggedIn = ref(false)

const newPassword = ref('')
const confirmPassword = ref('')
const passwordLoading = ref(false)
const passwordError = ref('')

const myBookings = computed(() => bookings.value)

const pendingCount = computed(() => myBookings.value.filter(b => b.status === 'pending').length)
const confirmedCount = computed(() => myBookings.value.filter(b => b.status === 'confirmed').length)
const totalAmount = computed(() => myBookings.value.reduce((sum, b) => sum + Number(b.total_price || 0), 0))

const displayBookingsCount = ref(0)
const displayPendingCount = ref(0)
const displayConfirmedCount = ref(0)
const displayTotalAmount = ref(0)

const rafMap = new Map()
const animateCounter = (outRef, toValue) => {
  if (typeof requestAnimationFrame === 'undefined' || typeof cancelAnimationFrame === 'undefined') {
    outRef.value = Math.round(Number(toValue || 0))
    return
  }

  const from = Number(outRef.value || 0)
  const to = Number(toValue || 0)
  const duration = 750
  const start = (typeof performance !== 'undefined' && typeof performance.now === 'function') ? performance.now() : Date.now()
  const existing = rafMap.get(outRef)
  if (existing) cancelAnimationFrame(existing)

  const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3)
  const step = (now) => {
    const p = Math.min(1, (now - start) / duration)
    const eased = easeOutCubic(p)
    const current = from + (to - from) * eased
    outRef.value = Math.round(current)
    if (p < 1) {
      rafMap.set(outRef, requestAnimationFrame(step))
    }
  }
  rafMap.set(outRef, requestAnimationFrame(step))
}

watch(() => myBookings.value.length, (v) => animateCounter(displayBookingsCount, v), { immediate: true })
watch(pendingCount, (v) => animateCounter(displayPendingCount, v), { immediate: true })
watch(confirmedCount, (v) => animateCounter(displayConfirmedCount, v), { immediate: true })
watch(totalAmount, (v) => animateCounter(displayTotalAmount, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const displayName = computed(() => {
  const first = currentUser.value?.first_name || ''
  const last = currentUser.value?.last_name || ''
  if (!first && !last) return t('dashboard.client')

  const safeFirst = first ? first.charAt(0).toUpperCase() + first.slice(1) : ''
  const safeLast = last ? last.charAt(0).toUpperCase() + last.slice(1) : ''
  return `${safeFirst} ${safeLast}`.trim()
})

const statusClass = (status) => {
  if (status === 'confirmed') return 'success'
  if (status === 'cancelled') return 'danger'
  if (status === 'paid') return 'info'
  return 'warning'
}

const statusText = (status) => {
  const safe = status || 'pending'
  return t(`dashboard.statusText.${safe}`)
}

const eventTypeText = (eventType) => {
  if (!eventType) return '-'
  if (['wedding', 'seminar', 'conference', 'birthday', 'meeting', 'other'].includes(eventType)) {
    return t(`booking.eventTypes.${eventType}`)
  }
  return String(eventType)
}

const fetchBookings = async () => {
  if (!isLoggedIn.value) return

  loading.value = true
  try {
    const response = await api.get('bookings/')
    bookings.value = Array.isArray(response.data) ? response.data : []
  } catch {
    notify(t('dashboard.notify.loadBookingsFail'), 'danger')
    bookings.value = []
  } finally {
    loading.value = false
  }
}

const setPassword = async () => {
  if (!isLoggedIn.value) return
  passwordError.value = ''

  if (!newPassword.value || newPassword.value.length < 6) {
    passwordError.value = t('dashboard.notify.passwordMin')
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = t('dashboard.notify.passwordMismatch')
    return
  }

  passwordLoading.value = true
  try {
    await api.post('auth/set-password/', { password: newPassword.value })
    newPassword.value = ''
    confirmPassword.value = ''
    notify(t('dashboard.notify.passwordSetSuccess'), 'success')
  } catch (e) {
    const msg = e?.response?.data?.password || e?.response?.data?.detail || t('dashboard.notify.passwordSetFail')
    passwordError.value = msg
    notify(msg, 'danger')
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  try {
    currentUser.value = JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    currentUser.value = {}
  }

  isLoggedIn.value = !!localStorage.getItem('access_token')
  if (isLoggedIn.value) fetchBookings()
})
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
