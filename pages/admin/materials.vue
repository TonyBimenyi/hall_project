<template>
  <div class="admin-materials">
    <div class="header-actions">
      <h1>Gestion du Matériel</h1>
      <div class="header-buttons">
        <button class="btn btn-export btn-sm" @click="exportPdf">
          <i class="fas fa-file-pdf"></i> Export PDF
        </button>
        <button class="btn btn-export btn-sm" @click="exportXls">
          <i class="fas fa-file-excel"></i> Export XLS
        </button>
        <button class="btn btn-primary btn-sm" @click="openAddModal">
          <i class="fas fa-plus"></i> Ajouter du matériel
        </button>
      </div>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-boxes"></i></div>
        <div class="stat-info">
          <span class="stat-label">Articles</span>
          <span class="stat-value">{{ materials.length }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-check-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">En Stock</span>
          <span class="stat-value success">{{ totalAvailable.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-tools"></i></div>
        <div class="stat-info">
          <span class="stat-label">Endommagé</span>
          <span class="stat-value warning">{{ totalDamaged.toLocaleString() }}</span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-times-circle"></i></div>
        <div class="stat-info">
          <span class="stat-label">Perdu</span>
          <span class="stat-value danger">{{ totalLost.toLocaleString() }}</span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <table ref="tableRef" class="admin-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Catégorie</th>
            <th>Quantité Totale</th>
            <th>En Stock</th>
            <th>Endommagé</th>
            <th>Perdu</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in materials" :key="item.id">
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ item.category }}</td>
            <td>{{ item.total_quantity }}</td>
            <td>{{ item.available_quantity }}</td>
            <td>{{ (item.damaged_quantity || 0).toLocaleString() }}</td>
            <td>{{ (item.lost_quantity || 0).toLocaleString() }}</td>
            <td>
              <div class="btn-group">
                <button
                  class="btn-icon"
                  title="Modifier Endommagé"
                  @click="openQtyModal(item, 'damaged')"
                >
                  <i class="fas fa-tools"></i>
                </button>
                <button
                  class="btn-icon"
                  title="Modifier Perdu"
                  @click="openQtyModal(item, 'lost')"
                >
                  <i class="fas fa-times-circle"></i>
                </button>
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
            <input :value="availablePreview" type="number" class="form-input" disabled />
          </div>
        </div>
        <div class="form-group" v-if="isEditing">
          <label class="form-label">Quantités (gestion)</label>
          <div class="qty-hint">
            <span>Endommagé: <strong>{{ (form.damaged_quantity || 0).toLocaleString() }}</strong></span>
            <span>Perdu: <strong>{{ (form.lost_quantity || 0).toLocaleString() }}</strong></span>
            <span class="hint">Utiliser les boutons Endommagé / Perdu dans la liste pour modifier.</span>
          </div>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" @click="saveMaterial">{{ isEditing ? 'Mettre à jour' : 'Ajouter' }}</button>
      </template>
    </AdminAppModal>

    <AdminAppModal v-model="showQtyModal" :title="qtyTitle" width="420px">
      <form class="admin-form" @submit.prevent="saveQty">
        <div v-if="qtyMaterial" class="qty-summary">
          <div><strong>Article:</strong> {{ qtyMaterial.name }}</div>
          <div><strong>Total:</strong> {{ qtyMaterial.total_quantity }}</div>
          <div><strong>En Stock:</strong> {{ qtyMaterial.available_quantity }}</div>
          <div><strong>Endommagé:</strong> {{ qtyMaterial.damaged_quantity || 0 }}</div>
          <div><strong>Perdu:</strong> {{ qtyMaterial.lost_quantity || 0 }}</div>
        </div>
        <div class="form-group">
          <label class="form-label">{{ qtyLabel }}</label>
          <input v-model.number="qtyValue" type="number" min="0" class="form-input" required />
          <small class="form-hint">La quantité disponible est recalculée automatiquement.</small>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showQtyModal = false">Annuler</button>
        <button class="btn btn-primary" @click="saveQty">Enregistrer</button>
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
          <span class="detail-label">Endommagé</span>
          <span class="detail-val">{{ selectedMaterial.damaged_quantity || 0 }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Perdu</span>
          <span class="detail-val">{{ selectedMaterial.lost_quantity || 0 }}</span>
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
const tableRef = ref(null)

const exportXls = () => {
  if (!tableRef.value) return
  const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${tableRef.value.outerHTML}</body></html>`
  const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'materials.xls'
  a.click()
  URL.revokeObjectURL(url)
}

const exportPdf = () => {
  if (!tableRef.value) return
  const win = window.open('', '_blank')
  if (!win) return
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Matériel</title><style>
  body{font-family:Arial, sans-serif; padding:20px}
  table{width:100%; border-collapse:collapse}
  th,td{border:1px solid #e2e8f0; padding:8px; text-align:left; font-size:12px}
  th{background:#f8fafc}
  </style></head><body><h2>Matériel</h2>${tableRef.value.outerHTML}</body></html>`)
  win.document.close()
  win.focus()
  win.print()
  win.close()
}
const showFormModal = ref(false)
const showQtyModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedMaterial = ref(null)
const qtyMaterial = ref(null)
const qtyMode = ref('damaged')
const qtyValue = ref(0)

const form = ref({
  id: null,
  name: '',
  category: 'Mobilier',
  total_quantity: 0,
  damaged_quantity: 0,
  lost_quantity: 0
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
    damaged_quantity: 0,
    lost_quantity: 0
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
  form.value = {
    id: item.id,
    name: item.name,
    category: item.category,
    total_quantity: item.total_quantity,
    damaged_quantity: item.damaged_quantity || 0,
    lost_quantity: item.lost_quantity || 0,
  }
  showFormModal.value = true
}

const confirmDelete = (item) => {
  selectedMaterial.value = item
  showDeleteModal.value = true
}

const saveMaterial = async () => {
  try {
    if (isEditing.value) {
      await api.put(`materials/${form.value.id}/`, {
        id: form.value.id,
        name: form.value.name,
        category: form.value.category,
        total_quantity: form.value.total_quantity,
        damaged_quantity: form.value.damaged_quantity || 0,
        lost_quantity: form.value.lost_quantity || 0,
      })
      notify('Matériel mis à jour avec succès')
    } else {
      await api.post('materials/', {
        name: form.value.name,
        category: form.value.category,
        total_quantity: form.value.total_quantity,
      })
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

const openQtyModal = (item, mode) => {
  qtyMaterial.value = item
  qtyMode.value = mode
  qtyValue.value = mode === 'lost' ? Number(item.lost_quantity || 0) : Number(item.damaged_quantity || 0)
  showQtyModal.value = true
}

const qtyTitle = computed(() => qtyMode.value === 'lost' ? 'Modifier Perdu' : 'Modifier Endommagé')
const qtyLabel = computed(() => qtyMode.value === 'lost' ? 'Quantité perdue' : 'Quantité endommagée')

const availablePreview = computed(() => {
  const total = Number(form.value.total_quantity || 0)
  const damaged = Number(form.value.damaged_quantity || 0)
  const lost = Number(form.value.lost_quantity || 0)
  return Math.max(0, total - damaged - lost)
})

const saveQty = async () => {
  if (!qtyMaterial.value) return
  try {
    const payload = qtyMode.value === 'lost'
      ? { lost_quantity: qtyValue.value }
      : { damaged_quantity: qtyValue.value }
    await api.patch(`materials/${qtyMaterial.value.id}/`, payload)
    notify('Quantité mise à jour', 'success')
    showQtyModal.value = false
    qtyMaterial.value = null
    fetchMaterials()
  } catch (error) {
    const msg = error?.response?.data?.non_field_errors?.[0] || 'Erreur lors de la mise à jour'
    notify(msg, 'danger')
  }
}

const totalAvailable = computed(() => (materials.value || []).reduce((a, m) => a + Number(m.available_quantity || 0), 0))
const totalDamaged = computed(() => (materials.value || []).reduce((a, m) => a + Number(m.damaged_quantity || 0), 0))
const totalLost = computed(() => (materials.value || []).reduce((a, m) => a + Number(m.lost_quantity || 0), 0))
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

.header-buttons {
  display: inline-flex;
  gap: .5rem;
  align-items: center;
  flex-wrap: wrap;
}

.header-actions h1 {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0;
}

.qty-summary {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: .85rem 1rem;
  display: grid;
  gap: .25rem;
  margin-bottom: .75rem;
  color: #0f172a;
  font-weight: 650;
}

.qty-hint {
  display: grid;
  gap: .35rem;
  padding: .75rem 1rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #0f172a;
  font-weight: 650;
}

.qty-hint .hint {
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.85rem;
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
