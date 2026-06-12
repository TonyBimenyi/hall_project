<template>
  <div class="profile-page">
    <div class="page-header">
      <div>
        <h1>Mon profil</h1>
        <p>Gérez vos informations personnelles et la sécurité de votre compte.</p>
      </div>
    </div>

    <div class="profile-grid">
      <section class="card profile-card identity-card">
        <div class="identity-top">
          <div class="identity-avatar">{{ initials }}</div>
          <div>
            <h2>{{ fullName || 'Utilisateur' }}</h2>
            <p>{{ roleLabel }}</p>
          </div>
        </div>

        <div class="meta-grid">
          <div class="meta-item">
            <span class="meta-label">Compte</span>
            <strong>{{ profile.username || '-' }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">Email</span>
            <strong>{{ profile.email || '-' }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">Téléphone</span>
            <strong>{{ profile.phone || '-' }}</strong>
          </div>
          <div class="meta-item">
            <span class="meta-label">Accès</span>
            <strong>{{ roleLabel }}</strong>
          </div>
        </div>
      </section>

      <section class="card profile-card">
        <div class="section-head">
          <h3>Informations personnelles</h3>
          <p>Mettez à jour votre nom, email et téléphone.</p>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>Prénom</span>
            <input v-model="form.first_name" type="text" placeholder="Prénom" />
          </label>
          <label class="field">
            <span>Nom</span>
            <input v-model="form.last_name" type="text" placeholder="Nom" />
          </label>
          <label class="field">
            <span>Email</span>
            <input v-model="form.email" type="email" placeholder="email@exemple.com" />
          </label>
          <label class="field">
            <span>Nom d'utilisateur</span>
            <input v-model="form.username" type="text" placeholder="Ex: reception-01" />
          </label>
          <label class="field">
            <span>Téléphone (optionnel)</span>
            <input v-model="form.phone" type="text" :disabled="!canEditPhone" placeholder="+257 ..." />
          </label>
        </div>

        <p v-if="!canEditPhone" class="hint-text">Le numéro de téléphone est géré depuis votre compte administrateur principal.</p>

        <div class="section-actions">
          <button class="btn btn-primary" :class="{ 'is-loading': savingProfile }" :disabled="savingProfile" @click="saveProfile">
            {{ savingProfile ? 'Enregistrement...' : 'Enregistrer les modifications' }}
          </button>
        </div>
      </section>

      <section class="card profile-card">
        <div class="section-head">
          <h3>Sécurité</h3>
          <p>Changez votre mot de passe à tout moment.</p>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>Nouveau mot de passe</span>
            <input v-model="security.password" type="password" placeholder="Minimum 8 caractères" />
          </label>
          <label class="field">
            <span>Confirmer le mot de passe</span>
            <input v-model="security.confirm_password" type="password" placeholder="Répétez le mot de passe" />
          </label>
        </div>

        <div class="section-actions">
          <button class="btn btn-outline" :class="{ 'is-loading': savingPassword }" :disabled="savingPassword" @click="savePassword">
            {{ savingPassword ? 'Mise à jour...' : 'Mettre à jour le mot de passe' }}
          </button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'
import { getRoleLabel } from '~/composables/useRoleAccess'

definePageMeta({ layout: 'admin' })

const profile = ref({})
const savingProfile = ref(false)
const savingPassword = ref(false)

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  username: '',
  phone: '',
})

const security = ref({
  password: '',
  confirm_password: '',
})

const fullName = computed(() => `${form.value.first_name} ${form.value.last_name}`.trim())
const initials = computed(() => `${form.value.first_name?.[0] || ''}${form.value.last_name?.[0] || ''}`.toUpperCase() || 'U')
const canEditPhone = computed(() => !!profile.value?.personnel_id)
const roleLabel = computed(() => getRoleLabel(profile.value))

const applyProfile = (data) => {
  profile.value = data || {}
  form.value = {
    first_name: data?.first_name || '',
    last_name: data?.last_name || '',
    email: data?.email || '',
    username: data?.username || '',
    phone: data?.phone || '',
  }
  if (process.client) {
    localStorage.setItem('user', JSON.stringify(profile.value))
  }
}

const fetchProfile = async () => {
  try {
    const res = await api.get('me/')
    applyProfile(res.data)
  } catch {
    notify('Impossible de charger le profil', 'danger')
  }
}

const saveProfile = async () => {
  savingProfile.value = true
  try {
    const payload = {
      first_name: form.value.first_name,
      last_name: form.value.last_name,
      email: form.value.email,
      username: form.value.username,
      phone: form.value.phone,
    }
    const res = await api.patch('me/', payload)
    applyProfile(res.data)
    notify('Profil mis à jour avec succès', 'success')
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.detail || data.username || data.email || data.phone || 'Impossible de mettre à jour le profil', 'danger')
  } finally {
    savingProfile.value = false
  }
}

const savePassword = async () => {
  savingPassword.value = true
  try {
    await api.post('auth/set-password/', {
      password: security.value.password,
      confirm_password: security.value.confirm_password,
    })
    security.value.password = ''
    security.value.confirm_password = ''
    const res = await api.get('me/')
    applyProfile(res.data)
    notify('Mot de passe mis à jour avec succès', 'success')
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.password || data.confirm_password || data.detail || 'Impossible de mettre à jour le mot de passe', 'danger')
  } finally {
    savingPassword.value = false
  }
}

onMounted(fetchProfile)
</script>

<style scoped>
.profile-page {
  padding: 0;
  --profile-meta-bg: var(--gray-100);
  --profile-meta-border: var(--gray-200);
  --profile-meta-shadow: none;
}

.page-header {
  margin-bottom: var(--space-8);
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--gray-900);
}

.page-header p {
  margin-top: 0.35rem;
  color: var(--gray-500);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.4fr;
  gap: var(--space-6);
}

.profile-card {
  padding: 1.5rem;
  border: 1px solid var(--gray-200);
  box-shadow: none;
}

.identity-card {
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.16), transparent 30%),
    linear-gradient(180deg, var(--white) 0%, var(--gray-50) 100%);
}

.identity-top {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.identity-avatar {
  width: 64px;
  height: 64px;
  border-radius: 22px;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #ffffff;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 1.15rem;
  letter-spacing: 0.06em;
  border: 1px solid rgba(15, 23, 42, 0.08);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.16);
  position: relative;
  overflow: hidden;
}

.identity-avatar::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.18), transparent 55%);
  pointer-events: none;
}

.identity-top h2 {
  margin: 0;
  color: var(--gray-900);
}

.identity-top p {
  margin: 0.3rem 0 0;
  color: var(--gray-500);
}

.meta-grid {
  display: grid;
  gap: 0.85rem;
}

.meta-item {
  padding: 0.95rem 1rem;
  border-radius: 16px;
  background: var(--profile-meta-bg);
  border: 1px solid var(--profile-meta-border);
  box-shadow: var(--profile-meta-shadow);
}

.meta-label {
  display: block;
  color: var(--gray-500);
  font-size: 0.82rem;
  margin-bottom: 0.35rem;
}

.meta-item strong {
  color: var(--gray-900);
}

.section-head {
  margin-bottom: 1.25rem;
}

.section-head h3 {
  margin: 0;
  font-size: 1.15rem;
  color: var(--gray-900);
}

.section-head p {
  margin: 0.35rem 0 0;
  color: var(--gray-500);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.field {
  display: grid;
  gap: 0.45rem;
}

.field span {
  font-size: 0.8rem;
  font-weight: 800;
  color: var(--gray-600);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field input {
  width: 100%;
  min-height: 50px;
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  padding: 0 0.95rem;
  background: var(--white);
  color: var(--gray-900);
}

.field input:focus {
  outline: none;
  border-color: #d4af37;
  box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.12);
}

.field input:disabled {
  background: var(--gray-50);
  color: var(--gray-400);
}

.hint-text {
  margin: 0.85rem 0 0;
  color: var(--gray-500);
  font-size: 0.88rem;
}

:global(html[data-admin-theme="dark"]) .profile-page .profile-card {
  border-color: rgba(30, 41, 59, 0.95);
}

:global(html[data-admin-theme="dark"]) .profile-page {
  --profile-meta-bg: rgba(15, 23, 42, 0.88);
  --profile-meta-border: rgba(30, 41, 59, 0.95);
  --profile-meta-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

:global(html[data-admin-theme="dark"]) .profile-page .identity-card {
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.12), transparent 30%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(11, 18, 32, 0.96) 100%) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .meta-item {
  background: var(--profile-meta-bg) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03), 0 10px 24px rgba(0, 0, 0, 0.16) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .meta-label {
  color: rgba(203, 213, 225, 0.78) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .meta-grid .meta-item,
:global(html[data-admin-theme="dark"]) .profile-page .identity-card .meta-item {
  background: var(--profile-meta-bg) !important;
  border: 1px solid rgba(30, 41, 59, 0.95) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .meta-grid .meta-item strong,
:global(html[data-admin-theme="dark"]) .profile-page .identity-card .meta-item strong {
  color: rgba(248, 250, 252, 0.96) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .meta-grid .meta-item .meta-label,
:global(html[data-admin-theme="dark"]) .profile-page .identity-card .meta-item .meta-label {
  color: rgba(203, 213, 225, 0.78) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .meta-item strong,
:global(html[data-admin-theme="dark"]) .profile-page .identity-top h2,
:global(html[data-admin-theme="dark"]) .profile-page .section-head h3 {
  color: rgba(248, 250, 252, 0.96) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .identity-top p,
:global(html[data-admin-theme="dark"]) .profile-page .page-header p,
:global(html[data-admin-theme="dark"]) .profile-page .section-head p,
:global(html[data-admin-theme="dark"]) .profile-page .hint-text {
  color: rgba(203, 213, 225, 0.78) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .identity-avatar {
  background:
    radial-gradient(circle at top left, rgba(255, 255, 255, 0.18), transparent 34%),
    linear-gradient(135deg, rgba(212, 175, 55, 0.96) 0%, rgba(192, 143, 17, 0.96) 52%, rgba(15, 23, 42, 0.96) 100%) !important;
  color: #ffffff !important;
  border-color: rgba(212, 175, 55, 0.34) !important;
  box-shadow:
    0 18px 38px rgba(0, 0, 0, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.14) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .field input {
  background: rgba(15, 23, 42, 0.88) !important;
  border-color: rgba(30, 41, 59, 0.95) !important;
}

:global(html[data-admin-theme="dark"]) .profile-page .field input:disabled {
  background: rgba(255, 255, 255, 0.04) !important;
}

.section-actions {
  margin-top: 1.25rem;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1100px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .profile-card {
    padding: 1rem;
  }
}
</style>
