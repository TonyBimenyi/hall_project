<template>
  <div class="dashboard_details">
    <div class="cards">
      <div class="card">
        <div class="card_info">
          <div class="p">Total des réservations</div>
          <div class="number">{{ totalBookings.toLocaleString() }}</div>
          <div class="trend">Mis à jour à l'instant</div>
        </div>
        <div class="icon">
          <i class="fas fa-calendar-check"></i>
        </div>
      </div>

      <div class="card">
        <div class="card_info">
          <div class="p">Salles actives</div>
          <div class="number">{{ activeHalls }}</div>
          <div class="trend">Disponible à la réservation</div>
        </div>
        <div class="icon">
          <i class="fas fa-building"></i>
        </div>
      </div>

      <div class="card">
        <div class="card_info">
          <div class="p">Revenu total</div>
          <div class="number">{{ Number(totalRevenue).toLocaleString() }} Fbu</div>
          <div class="trend">Depuis toujours</div>
        </div>
        <div class="icon">
          <i class="fas fa-wallet"></i>
        </div>
      </div>

      <div class="card">
        <div class="card_info">
          <div class="p">Dépenses du mois</div>
          <div class="number">{{ Number(monthlyExpenses).toLocaleString() }} Fbu</div>
          <div class="trend negative">
            +5% par rapport au mois dernier
          </div>
        </div>
        <div class="icon">
          <i class="fas fa-money-bill-wave"></i>
        </div>
      </div>

      <div class="card">
        <div class="card_info">
          <div class="p">Paiements en attente</div>
          <div class="number">{{ pendingPayments }}</div>
          <div class="trend" :class="{ negative: pendingPayments > 5 }">
            {{ pendingPayments > 5 ? 'Nécessite une attention particulière' : 'À gérer bientôt' }}
          </div>
        </div>
        <div class="icon">
          <i class="fas fa-exclamation-circle"></i>
        </div>
      </div>

      <div class="card">
        <div class="card_info">
          <div class="p">Pertes de matériel</div>
          <div class="number">{{ materialLosses }}</div>
          <div class="trend negative">Articles à remplacer</div>
        </div>
        <div class="icon">
          <i class="fas fa-box-open"></i>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '~/composables/useApi'

export default {
  data() {
    return {
      totalBookings: 0,
      activeHalls: 0,
      totalRevenue: 0,
      pendingPayments: 0,
      monthlyExpenses: 0,
      materialLosses: 0
    }
  },
  async mounted() {
    try {
      const response = await api.get('summary/')
      this.totalBookings = response.data.total_bookings
      this.activeHalls = response.data.active_halls
      this.totalRevenue = response.data.total_revenue
      this.monthlyExpenses = response.data.monthly_expenses
      this.pendingPayments = response.data.pending_payments
      this.materialLosses = response.data.material_losses
    } catch (error) {
      console.error('Error fetching dashboard summary:', error)
    }
  }
}
</script>

<style scoped>
.dashboard_details {
  margin-top: 0;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-6);
}

.card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: var(--space-8);
  position: relative;
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--primary);
  opacity: 0.1;
}

.card:hover::before {
  opacity: 1;
}

.card_info {
  width: 100%;
}

.card_info .p {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-4);
}

.card_info .number {
  font-size: 1.75rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: var(--space-2);
  line-height: 1;
}

.card_info .trend {
  font-size: 0.8rem;
  font-weight: 600;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.card_info .trend.negative {
  color: var(--danger);
}

.icon {
  position: absolute;
  top: var(--space-6);
  right: var(--space-6);
  width: 40px;
  height: 40px;
  background: #f1f5f9;
  color: #475569;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: var(--transition-fast);
}

.card:hover .icon {
  background: var(--primary);
  color: var(--white);
}

@media (max-width: 640px) {
  .cards {
    grid-template-columns: 1fr;
  }
}
</style>
