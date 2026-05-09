<template>
  <div class="admin-materials">
    <div class="header-actions">
      <h1>Gestion du Matériel</h1>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="fas fa-plus"></i> Ajouter du matériel
      </button>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-boxes"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total Articles</span>
          <span class="stat-value">{{ materials.length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Bon état</span>
          <span class="stat-value success">{{ materials.filter(m => m.status === 'good').length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-tools"></i></div>
        <div class="stat-info">
          <span class="stat-label">Endommagé</span>
          <span class="stat-value warning">{{ materials.filter(m => m.status === 'damaged').length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-times-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Perdu</span>
          <span class="stat-value danger">{{ materials.filter(m => m.status === 'lost').length }}</span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <table class="admin-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Catégorie</th>
            <th>Quantité Totale</th>
            <th>En Stock</th>
            <th>État</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in materials" :key="item.id">
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ item.category }}</td>
            <td>{{ item.total_quantity }}</td>
            <td>{{ item.available_quantity }}</td>
            <td>
              <span :class="['badge', getBadgeClass(item.status)]">
                {{ translateStatus(item.status) }}
              </span>
            </td>
            <td>
              <div class="btn-group">
                <button class="btn-icon view" title="Voir détails" @click="viewMaterial(item)">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="btn-icon edit" title="Modifier" @click="editMaterial(item)">
                  <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon delete" title="Supprimer" @click="confirmDelete(item)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Modal -->
    <AdminAppModal v-model="showFormModal" :title="isEditing ? 'Modifier le matériel' : 'Ajouter du matériel'" width="500px">
      <form @submit.prevent="saveMaterial" class="admin-form">
        <div class="form-group">
          <label class="form-label">Nom de l'article</label>
          <input v-model="form.name" type="text" class="form-input" required placeholder="Ex: Chaises Napoléon" />
        </div>
        <div class="form-group">
          <label class="form-label">Catégorie</label>
          <select v-model="form.category" class="form-select" required>
            <option value="Mobilier">Mobilier</option>
            <option value="Audiovisuel">Audiovisuel</option>
            <option value="Linge">Linge</option>
            <option value="Décoration">Décoration</option>
            <option value="Cuisine">Cuisine</option>
          </select>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Quantité Totale</label>
            <input v-model.number="form.total_quantity" type="number" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Quantité Disponible</label>
            <input v-model.number="form.available_quantity" type="number" class="form-input" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">État</label>
          <select v-model="form.status" class="form-select" required>
            <option value="good">Bon état</option>
            <option value="damaged">Endommagé</option>
            <option value="lost">Perdu</option>
          </select>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" @click="saveMaterial">{{ isEditing ? 'Mettre à jour' : 'Ajouter' }}</button>
      </template>
    </AdminAppModal>

    <!-- View Modal -->
    <AdminAppModal v-model="showViewModal" title="Détails du matériel" width="400px">
      <div v-if="selectedMaterial" class="view-details">
        <div class="detail-item">
          <span class="detail-label">Nom</span>
          <span class="detail-val">{{ selectedMaterial.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Catégorie</span>
          <span class="detail-val">{{ selectedMaterial.category }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Quantité Totale</span>
          <span class="detail-val">{{ selectedMaterial.total_quantity }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">En Stock</span>
          <span class="detail-val">{{ selectedMaterial.available_quantity }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">État</span>
          <span :class="['badge', getBadgeClass(selectedMaterial.status)]">
            {{ translateStatus(selectedMaterial.status) }}
          </span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-primary" @click="showViewModal = false">Fermer</button>
      </template>
    </AdminAppModal>

    <!-- Delete Confirmation Modal -->
    <AdminAppModal v-model="showDeleteModal" title="Confirmer la suppression" width="400px">
      <p>Êtes-vous sûr de vouloir supprimer <strong>{{ selectedMaterial?.name }}</strong> ?</p>
      <template #footer>
        <button class="btn btn-outline" @click="showDeleteModal = false">Annuler</button>
        <button class="btn btn-danger" @click="deleteMaterial">Supprimer</button>
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

const materials = ref([])
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedMaterial = ref(null)

const form = ref({
  id: null,
  name: '',
  category: 'Mobilier',
  total_quantity: 0,
  available_quantity: 0,
  status: 'good'
})

const fetchMaterials = async () => {
  try {
    const response = await api.get('materials/')
    materials.value = response.data
  } catch (error) {
    notify('Erreur lors du chargement du matériel', 'danger')
  }
}

onMounted(() => {
  fetchMaterials()
})

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    category: 'Mobilier',
    total_quantity: 0,
    available_quantity: 0,
    status: 'good'
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewMaterial = (item) => {
  selectedMaterial.value = item
  showViewModal.value = true
}

const editMaterial = (item) => {
  isEditing.value = true
  form.value = { ...item }
  showFormModal.value = true
}

const confirmDelete = (item) => {
  selectedMaterial.value = item
  showDeleteModal.value = true
}

const saveMaterial = async () => {
  try {
    if (isEditing.value) {
      await api.put(`materials/${form.value.id}/`, form.value)
      notify('Matériel mis à jour avec succès')
    } else {
      await api.post('materials/', form.value)
      notify('Nouveau matériel ajouté avec succès')
    }
    showFormModal.value = false
    fetchMaterials()
  } catch (error) {
    notify('Erreur lors de l\'enregistrement', 'danger')
  }
}

const deleteMaterial = async () => {
  try {
    await api.delete(`materials/${selectedMaterial.value.id}/`)
    notify('Matériel supprimé', 'danger')
    showDeleteModal.value = false
    fetchMaterials()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  }
}

const translateStatus = (status) => {
  const map = {
    good: 'Bon état',
    damaged: 'Endommagé',
    lost: 'Perdu'
  }
  return map[status] || status
}

const getBadgeClass = (status) => {
  const map = {
    good: 'badge-success',
    damaged: 'badge-warning',
    lost: 'badge-danger'
  }
  return map[status] || ''
}
</script>

<style scoped>
.admin-materials {
  padding: 0;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-10);
}

.header-actions h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
.stat-icon.info { background: #f0f9ff; color: #0ea5e9; }
.stat-icon.success { background: #f0fdf4; color: #22c55e; }
.stat-icon.warning { background: #fffbeb; color: #f59e0b; }
.stat-icon.danger { background: #fef2f2; color: #ef4444; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.125rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.value.success { color: #22c55e; }
.value.warning { color: #f59e0b; }
.value.danger { color: #ef4444; }

.btn-icon {
  width: 34px;
  height: 34px;
  background: #f8fafc;
  color: #94a3b8;
}

.btn-icon:hover {
  background: #f1f5f9;
}

.btn-icon.warning:hover { color: var(--warning); }
.btn-icon.info:hover { color: var(--info); }

.static-info {
  margin-top: var(--space-12);
  color: #cbd5e1;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 600;
}
</style>
