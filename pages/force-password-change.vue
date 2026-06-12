<template>
  <section class="force-page">
    <div class="force-shell">
      <div class="brand-panel">
        <span class="eyebrow">Accès Sécurisé</span>
        <h1>Créer un nouveau mot de passe</h1>
        <p>
          Votre compte a été créé avec un mot de passe temporaire. Définissez un nouveau mot de passe sécurisé pour continuer.
        </p>
      </div>

      <div class="form-card">
        <div class="form-head">
          <h2>Première connexion</h2>
          <p>Confirmez votre nouveau mot de passe pour activer votre accès au tableau de bord.</p>
        </div>

        <div class="form-grid">
          <label class="field">
            <span>Créer un nouveau mot de passe</span>
            <input v-model="password" type="password" required placeholder="Minimum 8 caractères" />
          </label>

          <label class="field">
            <span>Confirmer le mot de passe</span>
            <input v-model="confirmPassword" type="password" required placeholder="Répétez votre mot de passe" />
          </label>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <button class="btn btn-primary submit-btn" :class="{ 'is-loading': loading }" :disabled="loading" @click="submit">
          {{ loading ? 'Enregistrement...' : 'Continuer vers le tableau de bord' }}
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useRouter } from '#imports'
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'
import { getDefaultAdminRoute } from '~/composables/useRoleAccess'

const router = useRouter()
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const loading = ref(false)

const resolveRedirect = (user) => (user?.is_staff || user?.is_superuser ? getDefaultAdminRoute(user) : '/dashboard')

onMounted(() => {
  if (!process.client) return
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.replace('/login')
    return
  }

  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    if (!user?.must_change_password) {
      router.replace(resolveRedirect(user))
    }
  } catch {
    router.replace('/login')
  }
})

const submit = async () => {
  errorMessage.value = ''
  if (!password.value || password.value.length < 8) {
    errorMessage.value = 'Le mot de passe doit contenir au moins 8 caractères.'
    return
  }
  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  loading.value = true
  try {
    await api.post('auth/set-password/', {
      password: password.value,
      confirm_password: confirmPassword.value,
    })
    const me = await api.get('me/')
    localStorage.setItem('user', JSON.stringify(me.data))
    notify('Mot de passe mis à jour avec succès', 'success')
    await router.replace(resolveRedirect(me.data))
  } catch (error) {
    const data = error?.response?.data || {}
    errorMessage.value = data.password || data.confirm_password || data.detail || 'Impossible de mettre à jour le mot de passe.'
    notify(errorMessage.value, 'danger')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.force-page {
  min-height: 100vh;
  padding: 2rem 1rem;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.14), transparent 28%),
    linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
}

.force-shell {
  width: 100%;
  max-width: 980px;
  display: grid;
  grid-template-columns: 1fr 1.05fr;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 32px;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.08);
  backdrop-filter: blur(14px);
}

.brand-panel {
  padding: 3rem;
  background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  color: #f8fafc;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.76rem;
  font-weight: 700;
}

.brand-panel h1 {
  margin: 1rem 0 0.75rem;
  font-size: clamp(2rem, 4vw, 3rem);
  line-height: 1.05;
}

.brand-panel p {
  margin: 0;
  color: rgba(255, 255, 255, 0.78);
  line-height: 1.6;
  max-width: 28rem;
}

.form-card {
  padding: 3rem;
  background: rgba(255, 255, 255, 0.92);
}

.form-head h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #0f172a;
}

.form-head p {
  margin: 0.45rem 0 0;
  color: #64748b;
  line-height: 1.6;
}

.form-grid {
  display: grid;
  gap: 1rem;
  margin: 2rem 0 1rem;
}

.field {
  display: grid;
  gap: 0.55rem;
}

.field span {
  font-size: 0.84rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #334155;
}

.field input {
  width: 100%;
  min-height: 54px;
  border-radius: 16px;
  border: 1px solid #dbe4f0;
  padding: 0 1rem;
  background: #fff;
  color: #0f172a;
}

.field input:focus {
  outline: none;
  border-color: #d4af37;
  box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.12);
}

.error-text {
  margin: 0 0 1rem;
  color: #dc2626;
  font-weight: 600;
}

.submit-btn {
  width: 100%;
  justify-content: center;
  min-height: 52px;
}

@media (max-width: 860px) {
  .force-shell {
    grid-template-columns: 1fr;
  }

  .brand-panel,
  .form-card {
    padding: 2rem 1.25rem;
  }
}
</style>
