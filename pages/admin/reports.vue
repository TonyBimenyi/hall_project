<template>
  <div class="admin-reports">
    <div class="header-actions">
      <div>
        <h1>Rapports et Statistiques</h1>
        <p class="subtitle">Analyse des performances et de l'activité</p>
      </div>
      <div class="filters-group">
        <select class="filter-select-clean">
          <option>Ce mois-ci</option>
          <option>Dernier trimestre</option>
          <option>Année 2026</option>
        </select>
        <button class="btn btn-primary btn-sm">
          <i class="fas fa-file-export"></i> Exporter
        </button>
      </div>
    </div>

    <div class="summary-cards mb-8">
      <div class="summary-card card">
        <div class="summary-icon success"><i class="fas fa-wallet"></i></div>
        <div>
          <span class="label">Revenu Net (Mai)</span>
          <span class="value success">+{{ stats.monthly_revenue.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon danger"><i class="fas fa-arrow-trend-down"></i></div>
        <div>
          <span class="label">Dépenses Totales</span>
          <span class="value danger">-{{ stats.monthly_expenses.toLocaleString() }} Fbu</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon primary"><i class="fas fa-percentage"></i></div>
        <div>
          <span class="label">Marge Bénéficiaire</span>
          <span class="value primary">{{ profitMargin }}%</span>
        </div>
      </div>
      <div class="summary-card card">
        <div class="summary-icon info"><i class="fas fa-smile"></i></div>
        <div>
          <span class="label">Satisfaction Client</span>
          <span class="value info">4.8/5</span>
        </div>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card card">
        <div class="card-header">
          <span>Évolution des Revenus</span>
          <i class="fas fa-ellipsis-v more-icon"></i>
        </div>
        <div class="chart-content-clean">
          <div class="bars-container">
            <div class="bar-group" v-for="(h, i) in [40, 60, 45, 80, 65, 90, 70]" :key="i">
              <div class="bar-clean" :style="{ height: h + '%' }">
                <div class="bar-tooltip">{{ (h * 10000).toLocaleString() }}</div>
              </div>
              <span class="bar-label">S{{ i + 1 }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card card">
        <div class="card-header">
          <span>Taux d'Occupation</span>
          <i class="fas fa-ellipsis-v more-icon"></i>
        </div>
        <div class="chart-content-clean pie-layout">
          <div class="pie-sim-clean">
            <div class="pie-inner">{{ totalOccupation }}%</div>
          </div>
          <div class="legend-clean">
            <div class="legend-item" v-for="item in stats.occupation_data" :key="item.type">
              <span class="dot" :class="item.type.toLowerCase()"></span>
              <div class="legend-info">
                <span class="legend-label">{{ item.type }}</span>
                <span class="legend-val">{{ item.percentage }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="static-info">
      <p><i class="fas fa-info-circle"></i> Affichage de données dynamiques (Backend Django)</p>
    </div>
  </div>
</template>

<script setup>
import { api } from '~/composables/useApi'

definePageMeta({ layout: 'admin' })

const stats = ref({
  monthly_revenue: 0,
  monthly_expenses: 0,
  occupation_data: []
})

const fetchStats = async () => {
  try {
    const response = await api.get('summary/')
    stats.value = response.data
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

onMounted(() => {
  fetchStats()
})

const profitMargin = computed(() => {
  if (stats.value.monthly_revenue === 0) return 0
  const margin = ((stats.value.monthly_revenue - stats.value.monthly_expenses) / stats.value.monthly_revenue) * 100
  return Math.max(0, margin.toFixed(1))
})

const totalOccupation = computed(() => {
  return stats.value.occupation_data.reduce((acc, curr) => acc + curr.percentage, 0).toFixed(0)
})
</script>

<style scoped>
.admin-reports {
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
  margin-bottom: 0.25rem;
}

.subtitle {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.filters-group {
  display: flex;
  gap: var(--space-3);
  align-items: center;
}

.filter-select-clean {
  padding: 0.5rem 2rem 0.5rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: var(--rounded-md);
  font-size: 0.85rem;
  background: white;
  color: #475569;
  font-weight: 600;
  cursor: pointer;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
}

.summary-card {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6);
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.summary-icon.success { background: #f0fdf4; color: #22c55e; }
.summary-icon.danger { background: #fef2f2; color: #ef4444; }
.summary-icon.primary { background: #f1f5f9; color: #0f172a; }
.summary-icon.info { background: #f0f9ff; color: #0ea5e9; }

.label {
  display: block;
  font-size: 0.7rem;
  color: #94a3b8;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: var(--space-8);
}

.chart-card {
  padding: var(--space-8);
  min-height: 450px;
  display: flex;
  flex-direction: column;
}

.card-header {
  border: none;
  padding: 0;
  margin-bottom: var(--space-10);
  font-size: 1.1rem;
}

.more-icon {
  color: #cbd5e1;
  cursor: pointer;
}

.chart-content-clean {
  flex: 1;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.bars-container {
  width: 100%;
  height: 250px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 0 var(--space-4);
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.bar-clean {
  width: 32px;
  background: #f1f5f9;
  border-radius: 6px;
  position: relative;
  transition: var(--transition-all);
}

.bar-clean:hover {
  background: #0f172a;
}

.bar-tooltip {
  position: absolute;
  top: -35px;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: #0f172a;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 700;
  opacity: 0;
  pointer-events: none;
  transition: var(--transition-fast);
}

.bar-clean:hover .bar-tooltip {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}

.bar-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
}

.pie-layout {
  align-items: center;
  gap: var(--space-10);
}

.pie-sim-clean {
  width: 180px;
  height: 180px;
  border-radius: 50%;
  background: conic-gradient(
    #0f172a 0% 60%,
    #22c55e 60% 85%,
    #f59e0b 85% 100%
  );
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-inner {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);
}

.legend-clean {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.wedding { background: #0f172a; }
.dot.corporate { background: #22c55e; }
.dot.other { background: #f59e0b; }

.legend-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: #64748b;
}

.legend-val {
  font-size: 1rem;
  font-weight: 800;
  color: #0f172a;
}

.static-info {
  margin-top: var(--space-12);
  color: #cbd5e1;
  font-size: 0.85rem;
  text-align: center;
  font-weight: 600;
}
</style>
