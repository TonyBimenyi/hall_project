<!-- pages/admin/personnel.vue -->
<template>
  <div class="personnel-page">
    <div class="page-header">
      <div>
        <h1>Gestion du Personnel</h1>
        <p>Suivi des employés et assignation des tâches</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="fas fa-user-plus"></i> Ajouter un employé
      </button>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <span class="label">Total Personnel</span>
          <span class="value">{{ personnel.length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-user-check"></i></div>
        <div class="stat-info">
          <span class="label">En service</span>
          <span class="value success">{{ personnel.filter(p => p.status === 'on_duty').length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-tasks"></i></div>
        <div class="stat-info">
          <span class="label">Disponibles</span>
          <span class="value info">{{ personnel.filter(p => p.status === 'available').length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-user-clock"></i></div>
        <div class="stat-info">
          <span class="label">En congé</span>
          <span class="value warning">{{ personnel.filter(p => p.status === 'off_duty').length }}</span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Employé</th>
            <th>Rôle</th>
            <th>Contact</th>
            <th>Disponibilité</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="staff in personnel" :key="staff.id">
            <td class="staff-cell">
              <div class="avatar">{{ staff.name.charAt(0) }}</div>
              <div class="staff-info">
                <div class="name">{{ staff.name }}</div>
                <div class="id">ID: #{{ staff.id }}</div>
              </div>
            </td>
            <td>{{ staff.role }}</td>
            <td>{{ staff.phone }}</td>
            <td>
              <span :class="['badge', getBadgeClass(staff.status)]">
                {{ translateStatus(staff.status) }}
              </span>
            </td>
            <td>
              <div class="btn-group">
                <button class="btn-icon view" title="Voir détails" @click="viewStaff(staff)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon edit" title="Modifier" @click="editStaff(staff)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete" title="Supprimer" @click="confirmDelete(staff)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier l\'employé' : 'Ajouter un employé'" width="500px">
      <form @submit.prevent="saveStaff" class="admin-form">
        <div class="form-group">
          <label class="form-label">Nom complet</label>
          <input v-model="form.name" type="text" class="form-input" required placeholder="Ex: Jean Dupont" />
        </div>
        <div class="form-group">
          <label class="form-label">Rôle</label>
          <select v-model="form.role" class="form-select" required>
            <option value="Réceptionniste">Réceptionniste</option>
            <option value="Sécurité">Sécurité</option>
            <option value="Chef Cuisine">Chef Cuisine</option>
            <option value="Entretien">Entretien</option>
            <option value="Technicien AV">Technicien AV</option>
            <option value="Serveur">Serveur</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Téléphone</label>
          <input v-model="form.phone" type="text" class="form-input" required placeholder="+225 07..." />
        </div>
        <div class="form-group">
          <label class="form-label">Statut</label>
          <select v-model="form.status" class="form-select" required>
            <option value="available">Disponible</option>
            <option value="on_duty">En service</option>
            <option value="off_duty">En congé</option>
          </select>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" @click="saveStaff">{{ isEditing ? 'Mettre à jour' : 'Ajouter' }}</button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails de l'employé" width="400px">
      <div v-if="selectedStaff" class="view-details">
        <div class="detail-item">
          <span class="detail-label">Nom</span>
          <span class="detail-val">{{ selectedStaff.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Rôle</span>
          <span class="detail-val">{{ selectedStaff.role }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Contact</span>
          <span class="detail-val">{{ selectedStaff.phone }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Statut</span>
          <span :class="['badge', getBadgeClass(selectedStaff.status)]">
            {{ translateStatus(selectedStaff.status) }}
          </span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer l'employé <strong>{{ selectedStaff?.name }}</strong> ? Cette action est irréversible.</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" @click="deleteStaff">Supprimer</button>
      </template>
    </AdminAppModal>

    <div class="static-info">
      <p><i class="fas fa-info-circle"></i> Affichage de données statiques (Mode Démo)</p>
    </div>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const personnel = ref([])
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedStaff = ref(null)

const form = ref({
  id: null,
  name: '',
  role: 'Serveur',
  phone: '',
  status: 'available'
})

const fetchPersonnel = async () => {
  try {
    const response = await api.get('personnel/')
    personnel.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement du personnel', 'danger')
  }
}

onMounted(() => {
  fetchPersonnel()
})

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    role: 'Serveur',
    phone: '',
    status: 'available'
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewStaff = (staff) => {
  selectedStaff.value = staff
  showViewModal.value = true
}

const editStaff = (staff) => {
  isEditing.value = true
  form.value = { ...staff }
  showFormModal.value = true
}

const confirmDelete = (staff) => {
  selectedStaff.value = staff
  showDeleteModal.value = true
}

const saveStaff = async () => {
  try {
    if (isEditing.value) {
      await api.put(`personnel/${form.value.id}/`, form.value)
      notify('Personnel mis à jour avec succès')
    } else {
      await api.post('personnel/', form.value)
      notify('Nouvel employé ajouté avec succès')
    }
    showFormModal.value = false
    fetchPersonnel()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  }
}

const deleteStaff = async () => {
  try {
    await api.delete(`personnel/${selectedStaff.value.id}/`)
    notify('Employé supprimé', 'danger')
    showDeleteModal.value = false
    fetchPersonnel()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  }
}

const translateStatus = (status) => {
  const map = {
    available: 'Disponible',
    on_duty: 'En service',
    off_duty: 'En congé'
  }
  return map[status] || status
}

const getBadgeClass = (status) => {
  const map = {
    available: 'badge-info',
    on_duty: 'badge-success',
    off_duty: 'badge-warning'
  }
  return map[status] || ''
}
</script>

<style scoped>
.personnel-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-10);
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
}

.page-header p {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-10);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
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

.stat-icon.primary { background: #f1f5f9; color: #0f172a; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.warning { background: #fffbeb; color: #f59e0b; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-card .label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.125rem;
}

.stat-card .value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.value.success { color: #22c55e; }
.value.info { color: #0ea5e9; }
.value.warning { color: #f59e0b; }

.staff-cell {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.avatar {
  width: 36px;
  height: 36px;
  background: #f1f5f9;
  color: #475569;
  border-radius: var(--rounded-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.8rem;
}

.staff-info .name {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.95rem;
}

.staff-info .id {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
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

.btn-icon.info:hover { color: var(--info); }

.static-info {
  margin-top: var(--space-12);
  color: #cbd5e1;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 600;
}
</style>
