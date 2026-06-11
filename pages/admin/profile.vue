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
            <p>{{ profile.personnel_role || roleLabel }}</p>
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
const roleLabel = computed(() => {
  if (profile.value?.is_superuser) return 'Super Admin'
  if (profile.value?.personnel_role) return profile.value.personnel_role
  if (profile.value?.is_staff) return 'Admin'
  return 'Utilisateur'
})

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
}

.page-header {
  margin-bottom: var(--space-8);
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
}

.page-header p {
  margin-top: 0.35rem;
  color: #64748b;
}

.profile-grid {
  display: grid;
  grid-template-columns: 1.1fr 1.4fr;
  gap: var(--space-6);
}

.profile-card {
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.identity-card {
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.16), transparent 30%),
    linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
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
  border-radius: 20px;
  background: #0f172a;
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 1.15rem;
}

.identity-top h2 {
  margin: 0;
  color: #0f172a;
}

.identity-top p {
  margin: 0.3rem 0 0;
  color: #64748b;
}

.meta-grid {
  display: grid;
  gap: 0.85rem;
}

.meta-item {
  padding: 0.95rem 1rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
}

.meta-label {
  display: block;
  color: #64748b;
  font-size: 0.82rem;
  margin-bottom: 0.35rem;
}

.section-head {
  margin-bottom: 1.25rem;
}

.section-head h3 {
  margin: 0;
  font-size: 1.15rem;
  color: #0f172a;
}

.section-head p {
  margin: 0.35rem 0 0;
  color: #64748b;
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
  color: #334155;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field input {
  width: 100%;
  min-height: 50px;
  border-radius: 14px;
  border: 1px solid #dbe4f0;
  padding: 0 0.95rem;
  background: #fff;
}

.field input:focus {
  outline: none;
  border-color: #d4af37;
  box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.12);
}

.field input:disabled {
  background: #f8fafc;
  color: #94a3b8;
}

.hint-text {
  margin: 0.85rem 0 0;
  color: #64748b;
  font-size: 0.88rem;
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
