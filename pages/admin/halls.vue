<template>
  <div class="admin-halls">
    <div class="header-actions">
      <div class="page-title">
        <h1>Gestion des Salles</h1>
        <p>Créer, modifier et suivre les capacités et tarifs des salles</p>
      </div>
      <button class="btn btn-primary btn-sm" @click="openAddModal">
        <i class="fas fa-plus"></i> Ajouter une salle
      </button>
    </div>

    <div class="stats-grid mb-8">
      <div class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-building"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total Salles</span>
          <span class="stat-value">
            <span v-if="loadingHalls" class="skeleton-line skeleton-w-30"></span>
            <template v-else>{{ displayTotalHalls }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-users"></i></div>
        <div class="stat-info">
          <span class="stat-label">Capacité Totale</span>
          <span class="stat-value info">
            <span v-if="loadingHalls" class="skeleton-line skeleton-w-40"></span>
            <template v-else>{{ displayTotalCapacity }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-coins"></i></div>
        <div class="stat-info">
          <span class="stat-label">Prix Moyen / Jour</span>
          <span class="stat-value success">
            <span v-if="loadingHalls" class="skeleton-line skeleton-w-60"></span>
            <template v-else>{{ formatMoney(displayAverageDailyPrice) }}</template>
          </span>
        </div>
      </div>
      <div class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-crown"></i></div>
        <div class="stat-info">
          <span class="stat-label">Plus Haute Tarification</span>
          <span class="stat-value warning">
            <span v-if="loadingHalls" class="skeleton-line skeleton-w-60"></span>
            <template v-else>{{ formatMoney(displayHighestDailyPrice) }}</template>
          </span>
        </div>
      </div>
    </div>

    <div class="table-container card">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; margin-bottom: var(--space-4);">
        <h2 class="table-title" style="margin-bottom:0;">Toutes les salles ({{ loadingHalls ? '...' : halls.length }})</h2>
        <AdminAppTablePagination
          :start="hallsStartIndex"
          :end="hallsEndIndex"
          :total="hallsTotalItems"
          :can-prev="hallsCanPrev"
          :can-next="hallsCanNext"
          :disabled="loadingHalls"
          @prev="hallsPrevPage"
          @next="hallsNextPage"
        />
      </div>
      <div v-if="isMobile" class="admin-cards">
        <template v-if="loadingHalls">
          <div v-for="n in 6" :key="`sk-card-${n}`" class="admin-card">
            <div class="admin-card-head">
              <div style="width: 100%;">
                <div class="skeleton-line skeleton-w-70"></div>
                <div style="margin-top: 8px;" class="skeleton-line skeleton-w-50"></div>
              </div>
            </div>
            <div class="admin-card-body">
              <div class="skeleton-line skeleton-w-60"></div>
              <div class="skeleton-line skeleton-w-40"></div>
              <div class="skeleton-line skeleton-w-50"></div>
            </div>
          </div>
        </template>
        <template v-else>
          <div v-for="hall in paginatedHalls" :key="hall.id" class="admin-card">
            <div class="admin-card-head">
              <div>
                <div class="admin-card-title">{{ hall.name }}</div>
                <div class="admin-card-subtitle">{{ hall.capacity }} pers. • {{ formatMoney(hall.price_per_day) }}/jour</div>
              </div>

              <div class="actions-dropdown">
                <button class="btn-icon details" title="Détails" @click.stop="toggleActions(hall.id)">
                  <i class="fas fa-ellipsis-vertical"></i>
                </button>
                <div v-if="openActionsId === hall.id" class="actions-menu" @click.stop>
                  <button class="actions-item" @click="viewHall(hall)">
                    <i class="fas fa-eye"></i> Voir
                  </button>
                  <button class="actions-item" @click="editHall(hall)">
                    <i class="fas fa-edit"></i> Modifier
                  </button>
                  <button class="actions-item danger" @click="confirmDelete(hall)">
                    <i class="fas fa-trash-alt"></i> Supprimer
                  </button>
                </div>
              </div>
            </div>

            <div class="admin-card-body">
              <div class="admin-kv">
                <span class="k">Capacité</span>
                <span class="v">{{ hall.capacity }} pers.</span>
              </div>
              <div class="admin-kv">
                <span class="k">Prix / Jour</span>
                <span class="v">{{ formatMoney(hall.price_per_day) }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!loadingHalls && halls.length === 0" class="empty-cell">Aucune salle disponible</div>
      </div>

      <table v-else class="admin-table">
        <thead>
          <tr>
            <th><button class="table-sort-btn" :class="{ active: isHallSortActive('name') }" @click="toggleHallSort('name')">Nom <i :class="hallSortIconClass('name')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isHallSortActive('capacity') }" @click="toggleHallSort('capacity')">Capacité <i :class="hallSortIconClass('capacity')"></i></button></th>
            <th><button class="table-sort-btn" :class="{ active: isHallSortActive('price_per_day') }" @click="toggleHallSort('price_per_day')">Prix / Jour <i :class="hallSortIconClass('price_per_day')"></i></button></th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <template v-if="loadingHalls">
            <tr v-for="n in 6" :key="`sk-${n}`">
              <td><div class="skeleton-line skeleton-w-60"></div></td>
              <td><div class="skeleton-line skeleton-w-30"></div></td>
              <td><div class="skeleton-line skeleton-w-50"></div></td>
              <td><div class="skeleton-line skeleton-w-40"></div></td>
            </tr>
          </template>
          <template v-else>
            <tr v-for="hall in paginatedHalls" :key="hall.id">
              <td><strong>{{ hall.name }}</strong></td>
              <td>{{ hall.capacity }} pers.</td>
              <td>{{ formatMoney(hall.price_per_day) }}</td>
              <td class="actions-cell">
                <div class="actions-dropdown">
                  <button class="btn-icon details" title="Détails" @click.stop="toggleActions(hall.id)">
                    <i class="fas fa-ellipsis-vertical"></i>
                  </button>
                  <div v-if="openActionsId === hall.id" class="actions-menu" @click.stop>
                    <button class="actions-item" @click="viewHall(hall)">
                      <i class="fas fa-eye"></i> Voir
                    </button>
                    <button class="actions-item" @click="editHall(hall)">
                      <i class="fas fa-edit"></i> Modifier
                    </button>
                    <button class="actions-item danger" @click="confirmDelete(hall)">
                      <i class="fas fa-trash-alt"></i> Supprimer
                    </button>
                  </div>
                </div>
              </td>
            </tr>
          </template>
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
            <input v-model="pricePerDayInput" inputmode="numeric" type="text" class="form-input" placeholder="0" required />
          </div>
        </div>
        <div class="services-section">
          <div class="services-head">
            <div>
              <h3>Services additionnels</h3>
              <p>Ajoutez les options payantes de cette salle avec ou sans sous-services.</p>
            </div>
            <button type="button" class="btn btn-outline btn-sm" @click="addService">
              <i class="fas fa-plus"></i> Ajouter un service
            </button>
          </div>

          <div v-if="form.additional_services.length === 0" class="services-empty">
            Aucun service additionnel pour cette salle.
          </div>

          <div v-for="(service, serviceIndex) in form.additional_services" :key="service.id" class="service-card">
            <div class="service-card-head">
              <strong>Service {{ serviceIndex + 1 }}</strong>
              <button type="button" class="btn-icon delete" title="Supprimer" @click="removeService(serviceIndex)">
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Nom du service</label>
                <input v-model="service.name" list="default-service-options" type="text" class="form-input" placeholder="Ex: Sonorisation" />
              </div>
              <div class="form-group">
                <label class="checkbox-row service-checkbox">
                  <input v-model="service.has_subservices" type="checkbox" @change="onServiceHasSubservicesChange(service)" />
                  <span>Ce service a des sous-services</span>
                </label>
              </div>
            </div>

            <div v-if="!service.has_subservices" class="form-group">
              <label class="form-label">Prix du service (Fbu)</label>
              <input v-model="buildServicePriceModel(service).value" inputmode="numeric" type="text" class="form-input" placeholder="0" />
            </div>

            <div v-else class="subservices-section">
              <div class="subservices-head">
                <strong>Sous-services</strong>
                <button type="button" class="btn btn-outline btn-sm" @click="addSubservice(service)">
                  <i class="fas fa-plus"></i> Ajouter un sous-service
                </button>
              </div>

              <div
                v-for="(subservice, subIndex) in service.subservices"
                :key="subservice.id"
                class="subservice-row"
              >
                <input v-model="subservice.name" type="text" class="form-input" :placeholder="`Sous-service ${subIndex + 1}`" />
                <input v-model="buildSubservicePriceModel(subservice).value" inputmode="numeric" type="text" class="form-input" placeholder="Prix (Fbu)" />
                <button type="button" class="btn-icon delete" title="Supprimer" @click="removeSubservice(service, subIndex)">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </div>
          </div>
          <datalist id="default-service-options">
            <option v-for="serviceName in defaultServiceOptions" :key="serviceName" :value="serviceName"></option>
          </datalist>
        </div>
      </form>
      <template #footer>
        <button class="btn btn-outline" @click="showFormModal = false">Annuler</button>
        <button class="btn btn-primary" :class="{ 'is-loading': savingHall }" :disabled="savingHall" @click="saveHall">
          {{ isEditing ? 'Mettre à jour' : 'Ajouter' }}
        </button>
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
          <span class="detail-val">{{ formatMoney(selectedHall.price_per_day) }}</span>
        </div>
        <div class="detail-block">
          <span class="detail-label">Services additionnels</span>
          <div v-if="!selectedHall.additional_services?.length" class="detail-val muted-block">Aucun service additionnel</div>
          <div v-else class="services-preview">
            <div v-for="(service, index) in selectedHall.additional_services" :key="`${service.name}-${index}`" class="service-preview-item">
              <div class="service-preview-title">
                <strong>{{ service.name }}</strong>
                <span v-if="!service.has_subservices">{{ formatMoney(service.price) }}</span>
              </div>
              <div v-if="service.has_subservices" class="service-preview-subs">
                <div v-for="(subservice, subIndex) in service.subservices || []" :key="`${service.name}-${subIndex}`" class="service-preview-sub">
                  <span>{{ subservice.name }}</span>
                  <strong>{{ formatMoney(subservice.price) }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="detail-item">
          <span class="detail-label">Créé par</span>
          <span class="detail-val">{{ selectedHall.created_by_name || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Dernière action par</span>
          <span class="detail-val">{{ selectedHall.updated_by_name || selectedHall.created_by_name || '-' }}</span>
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
        <button class="btn btn-danger" :class="{ 'is-loading': deletingHall }" :disabled="deletingHall" @click="deleteHall">
          Supprimer
        </button>
      </template>
    </AdminAppModal>
  </div>
</template>

<script setup>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { usePagination } from '~/composables/usePagination'
import { useTableSort } from '~/composables/useTableSort'

definePageMeta({ layout: 'admin' })
const { formatMoney, moneyInputModel, parseMoney, formatNumberSpaces } = useMoney()

const halls = ref([])
const loadingHalls = ref(false)
const showFormModal = ref(false)
const showViewModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const selectedHall = ref(null)
const openActionsId = ref(null)
const isMobile = ref(false)
const savingHall = ref(false)
const deletingHall = ref(false)

const form = ref({
  id: null,
  name: '',
  capacity: 1,
  price_per_day: 0,
  additional_services: [],
})
const pricePerDayInput = moneyInputModel(form, 'price_per_day')
const defaultServiceOptions = ['Sonorisation', 'Décoration', 'Boissons', 'Lieu de prise des photos', 'Autre']
const {
  sortedItems: sortedHalls,
  toggleSort: toggleHallSort,
  isSortActive: isHallSortActive,
  sortIconClass: hallSortIconClass,
} = useTableSort(computed(() => halls.value), {
  initialKey: 'id',
  initialDirection: 'desc',
  accessors: {
    capacity: hall => Number(hall?.capacity || 0),
    price_per_day: hall => Number(hall?.price_per_day || 0),
  },
})
const {
  paginatedItems: paginatedHalls,
  totalItems: hallsTotalItems,
  startIndex: hallsStartIndex,
  endIndex: hallsEndIndex,
  canPrev: hallsCanPrev,
  canNext: hallsCanNext,
  prevPage: hallsPrevPage,
  nextPage: hallsNextPage,
} = usePagination(sortedHalls, 50)

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

const displayTotalHalls = ref(0)
const displayTotalCapacity = ref(0)
const displayAverageDailyPrice = ref(0)
const displayHighestDailyPrice = ref(0)

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
    if (p < 1) rafMap.set(outRef, requestAnimationFrame(step))
  }

  rafMap.set(outRef, requestAnimationFrame(step))
}

watch(() => halls.value.length, (v) => animateCounter(displayTotalHalls, v), { immediate: true })
watch(totalCapacity, (v) => animateCounter(displayTotalCapacity, v), { immediate: true })
watch(averageDailyPrice, (v) => animateCounter(displayAverageDailyPrice, v), { immediate: true })
watch(highestDailyPrice, (v) => animateCounter(displayHighestDailyPrice, v), { immediate: true })

onBeforeUnmount(() => {
  for (const id of rafMap.values()) cancelAnimationFrame(id)
})

const fetchHalls = async () => {
  loadingHalls.value = true
  try {
    const response = await api.get('halls/')
    halls.value = Array.isArray(response.data) ? response.data : []
  } catch (error) {
    notify('Erreur lors du chargement des salles', 'danger')
  } finally {
    loadingHalls.value = false
  }
}

onMounted(() => {
  fetchHalls()
  if (process.client) {
    const update = () => { isMobile.value = window.innerWidth <= 992 }
    update()
    window.addEventListener('resize', update)
    onBeforeUnmount(() => window.removeEventListener('resize', update))

    const onDocClick = () => { openActionsId.value = null }
    document.addEventListener('click', onDocClick)
    onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
  }
})

const toggleActions = (id) => {
  openActionsId.value = openActionsId.value === id ? null : id
}

const createSubservice = (values = {}) => ({
  id: `sub-${Math.random().toString(36).slice(2, 10)}`,
  name: values.name || '',
  price: Number(values.price || 0),
})

const createService = (values = {}) => ({
  id: `svc-${Math.random().toString(36).slice(2, 10)}`,
  name: values.name || defaultServiceOptions[0],
  price: Number(values.price || 0),
  has_subservices: !!values.has_subservices,
  subservices: Array.isArray(values.subservices) ? values.subservices.map(createSubservice) : [],
})

const buildServicePriceModel = (service) => computed({
  get: () => (service.price ? formatNumberSpaces(service.price) : ''),
  set: (value) => {
    service.price = parseMoney(value)
  },
})

const buildSubservicePriceModel = (subservice) => computed({
  get: () => (subservice.price ? formatNumberSpaces(subservice.price) : ''),
  set: (value) => {
    subservice.price = parseMoney(value)
  },
})

const addService = () => {
  form.value.additional_services.push(createService())
}

const removeService = (index) => {
  form.value.additional_services.splice(index, 1)
}

const addSubservice = (service) => {
  service.subservices.push(createSubservice())
}

const removeSubservice = (service, index) => {
  service.subservices.splice(index, 1)
}

const onServiceHasSubservicesChange = (service) => {
  if (service.has_subservices) {
    service.price = 0
    if (!service.subservices.length) {
      service.subservices.push(createSubservice())
    }
    return
  }
  service.subservices = []
}

const normalizeAdditionalServices = (services) => {
  if (!Array.isArray(services)) return []
  return services
    .map((service) => {
      const name = String(service?.name || '').trim()
      if (!name) return null
      const hasSubservices = !!service?.has_subservices
      if (hasSubservices) {
        const subservices = Array.isArray(service?.subservices)
          ? service.subservices
            .map((subservice) => {
              const subName = String(subservice?.name || '').trim()
              if (!subName) return null
              return {
                name: subName,
                price: parseMoney(subservice?.price || 0),
              }
            })
            .filter(Boolean)
          : []
        return {
          name,
          price: 0,
          has_subservices: true,
          subservices,
        }
      }
      return {
        name,
        price: parseMoney(service?.price || 0),
        has_subservices: false,
        subservices: [],
      }
    })
    .filter(Boolean)
}

const resetForm = () => {
  form.value = {
    id: null,
    name: '',
    capacity: 1,
    price_per_day: 0,
    additional_services: [],
  }
}

const openAddModal = () => {
  isEditing.value = false
  resetForm()
  showFormModal.value = true
}

const viewHall = (hall) => {
  openActionsId.value = null
  selectedHall.value = hall
  showViewModal.value = true
}

const editHall = (hall) => {
  openActionsId.value = null
  isEditing.value = true
  form.value = {
    ...hall,
    capacity: Number(hall.capacity),
    price_per_day: Number(hall.price_per_day),
    additional_services: normalizeAdditionalServices(hall.additional_services).map(createService),
  }
  showFormModal.value = true
}

const confirmDelete = (hall) => {
  openActionsId.value = null
  selectedHall.value = hall
  showDeleteModal.value = true
}

const saveHall = async () => {
  if (savingHall.value) return
  savingHall.value = true
  try {
    const payload = {
      name: String(form.value.name || '').trim(),
      capacity: Number(form.value.capacity || 0),
      price_per_day: Number(form.value.price_per_day || 0),
      additional_services: normalizeAdditionalServices(form.value.additional_services),
    }
    if (isEditing.value) {
      await api.put(`halls/${form.value.id}/`, payload)
      notify('Salle mise à jour avec succès', 'success')
    } else {
      await api.post('halls/', payload)
      notify('Nouvelle salle ajoutée avec succès', 'success')
    }
    showFormModal.value = false
    fetchHalls()
  } catch (error) {
    const data = error?.response?.data || {}
    notify(data.additional_services || data.detail || 'Erreur lors de l\'enregistrement', 'danger')
  } finally {
    savingHall.value = false
  }
}

const deleteHall = async () => {
  if (deletingHall.value || !selectedHall.value?.id) return
  deletingHall.value = true
  try {
    await api.delete(`halls/${selectedHall.value.id}/`)
    notify('Salle supprimée', 'danger')
    showDeleteModal.value = false
    fetchHalls()
  } catch (error) {
    notify('Erreur lors de la suppression', 'danger')
  } finally {
    deletingHall.value = false
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
  align-items: flex-start;
  margin-bottom: var(--space-8);
  gap: var(--space-4);
  flex-wrap: wrap;
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

.actions-cell {
  width: 1%;
  white-space: nowrap;
}

.actions-dropdown {
  position: relative;
  display: inline-flex;
}

.actions-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 190px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12);
  padding: 6px;
  z-index: 30;
}

.actions-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  color: #334155;
  font-weight: 700;
  font-size: 0.9rem;
  text-align: left;
}

.actions-item:hover {
  background: #f8fafc;
  color: #0f172a;
}

.actions-item.danger {
  color: #dc2626;
}

.actions-item.danger:hover {
  background: #fef2f2;
  color: #b91c1c;
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

.services-section {
  margin-top: 1rem;
  border-top: 1px solid #eef2f7;
  padding-top: 1rem;
}

.services-head,
.subservices-head,
.service-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.services-head h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
}

.services-head p {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 0.88rem;
}

.services-empty {
  margin-top: 0.75rem;
  padding: 1rem;
  border: 1px dashed #cbd5e1;
  border-radius: 14px;
  color: #64748b;
  font-weight: 600;
  background: #f8fafc;
}

.service-card {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #fafcff;
}

.service-card-head {
  margin-bottom: 0.9rem;
}

.service-checkbox {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

.subservices-section {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px dashed #dbe3ee;
}

.subservice-row {
  display: grid;
  grid-template-columns: 1.3fr 1fr auto;
  gap: 10px;
  align-items: center;
  margin-top: 0.75rem;
}

.btn-icon.delete:hover {
  color: var(--danger);
}

.detail-block {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  padding-bottom: var(--space-3);
  border-bottom: 1px solid #f1f5f9;
}

.muted-block {
  color: #64748b;
}

.services-preview {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.service-preview-item {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.85rem 1rem;
  background: #f8fafc;
}

.service-preview-title,
.service-preview-sub {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.service-preview-title {
  color: #0f172a;
}

.service-preview-subs {
  margin-top: 0.55rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  color: #475569;
}

@media (max-width: 900px) {
  .header-actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .subservice-row {
    grid-template-columns: 1fr;
  }
}
</style>
