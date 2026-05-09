<template>
  <div class="admin-halls">
    <div class="header-actions">
      <div class="page-title">
        <h1>Gestion des Salles</h1>
        <p>Créer, modifier et suivre les capacités et tarifs des salles</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="fas fa-plus"></i> Ajouter une salle
      </button>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-building"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total Salles</span>
          <span class="stat-value">{{ halls.length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <span class="stat-label">Capacité Totale</span>
          <span class="stat-value info">{{ totalCapacity }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-coins"></i></div>
        <div class="stat-info">
          <span class="stat-label">Prix Moyen / Jour</span>
          <span class="stat-value success">{{ averageDailyPrice.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-crown"></i></div>
        <div class="stat-info">
          <span class="stat-label">Plus Haute Tarification</span>
          <span class="stat-value warning">{{ highestDailyPrice.toLocaleString() }} Fbu</span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <h2 class="table-title">Toutes les salles ({{ halls.length }})</h2>
      <table class="admin-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Capacité</th>
            <th>Prix / Jour</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="hall in halls" :key="hall.id">
            <td><strong>{{ hall.name }}</strong></td>
            <td>{{ hall.capacity }} pers.</td>
            <td>{{ Number(hall.price_per_day || 0).toLocaleString() }} Fbu</td>
            <td>
              <div class="btn-group">
                <button class="btn-icon view" title="Voir détails" @click="viewHall(hall)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon edit" title="Modifier" @click="editHall(hall)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete" title="Supprimer" @click="confirmDelete(hall)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="halls.length === 0">
            <td colspan="4" class="empty-cell">Aucune salle disponible</td>
          </tr>
        </tbody>
      </table>
    </div>

    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier la salle' : 'Ajouter une salle'" width="500px">
      <form @submit.prevent="saveHall" class="admin-form">
        <div class="form-group">
          <label class="form-label">Nom de la salle</label>
          <input v-model="form.name" type="text" class="form-input" required placeholder="Ex: Grande Salle A" />
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Capacité</label>
            <input v-model.number="form.capacity" type="number" class="form-input" min="1" required />
          </div>
          <div class="form-group">
            <label class="form-label">Prix / Jour (Fbu)</label>
            <input v-model.number="form.price_per_day" type="number" class="form-input" min="0" required />
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" @click="saveHall">{{ isEditing ? 'Mettre à jour' : 'Ajouter' }}</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showViewModal" title="Détails de la salle" width="400px">
      <div v-if="selectedHall" class="view-details">
        <div class="detail-item">
          <span class="detail-label">Nom</span>
          <span class="detail-val">{{ selectedHall.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Capacité</span>
          <span class="detail-val">{{ selectedHall.capacity }} pers.</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Prix / Jour</span>
          <span class="detail-val">{{ Number(selectedHall.price_per_day || 0).toLocaleString() }} Fbu</span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer <strong>{{ selectedHall?.name }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" @click="deleteHall">Supprimer</button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const halls = ref([])
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedHall = ref(null)

const form = ref({
  id: null,
  name: '',
  capacity: 1,
  price_per_day: 0
})

const totalCapacity = computed(() => halls.value.reduce((sum, hall) => sum + Number(hall.capacity || 0), 0))
const averageDailyPrice = computed(() => {
  if (!halls.value.length) return 0
  const total = halls.value.reduce((sum, hall) => sum + Number(hall.price_per_day || 0), 0)
  return Math.round(total / halls.value.length)
})
const highestDailyPrice = computed(() => {
  if (!halls.value.length) return 0
  return Math.max(...halls.value.map(hall => Number(hall.price_per_day || 0)))
})

const fetchHalls = async () => {
  try {
    const response = await api.get('halls/')
    halls.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement des salles', 'danger')
  }
}

onMounted(() => {
  fetchHalls()
})

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    capacity: 1,
    price_per_day: 0
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewHall = (hall) => {
  selectedHall.value = hall
  showViewModal.value = true
}

const editHall = (hall) => {
  isEditing.value = true
  form.value = { ...hall, capacity: Number(hall.capacity), price_per_day: Number(hall.price_per_day) }
  showFormModal.value = true
}

const confirmDelete = (hall) => {
  selectedHall.value = hall
  showDeleteModal.value = true
}

const saveHall = async () => {
  try {
    if (isEditing.value) {
      await api.put(`halls/${form.value.id}/`, form.value)
      notify('Salle mise à jour avec succès', 'success')
    } else {
      await api.post('halls/', form.value)
      notify('Nouvelle salle ajoutée avec succès', 'success')
    }
    showFormModal.value = false
    fetchHalls()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  }
}

const deleteHall = async () => {
  try {
    await api.delete(`halls/${selectedHall.value.id}/`)
    notify('Salle supprimée', 'danger')
    showDeleteModal.value = false
    fetchHalls()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  }
}
</script>

<style scoped>
.admin-halls {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-8);
  gap: var(--space-4);
}

.page-title h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
}

.page-title p {
  margin-top: 0.35rem;
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
  border: 1px solid #eef2f7;
  box-shadow: none;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.stat-icon.primary { background: #eef2ff; color: #4338ca; }
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.warning { background: #fffbeb; color: #f59e0b; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.72rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 800;
  color: #0f172a;
}

.stat-value.info { color: #0ea5e9; }
.stat-value.success { color: #22c55e; }
.stat-value.warning { color: #f59e0b; }

.table-title {
  font-size: 1rem;
  font-weight: 800;
  margin-bottom: var(--space-5);
  color: #1e293b;
}

.btn-icon {
  width: 34px;
  height: 34px;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.view:hover { color: var(--info); }
.btn-icon.edit:hover { color: var(--primary); }
.btn-icon.delete:hover { color: var(--danger); }

.empty-cell {
  text-align: center;
  color: #94a3b8;
  font-weight: 600;
  padding: var(--space-4) 0;
}

.view-details {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid #f1f5f9;
}

@media (max-width: 900px) {
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
