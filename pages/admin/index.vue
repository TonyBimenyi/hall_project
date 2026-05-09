<template>
<div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Tableau de bord Admin</h1>
      <p>Bienvenue ! Voici un aperçu de l'activité d'aujourd'hui.</p>
      <div class="quick-actions">
        <NuxtLink to="/admin/bookings" class="btn btn-outline btn-sm"><i class="fas fa-calendar-check"></i> Réservations</NuxtLink>
        <NuxtLink to="/admin/payments" class="btn btn-primary btn-sm"><i class="fas fa-coins"></i> Paiements</NuxtLink>
      </div>
    </div>
    
    <AdminDashboardDetails />
    
    <div class="dashboard-grid">
      <div class="grid-item">
        <AdminDashboardRecentBookings />
      </div>
      <div class="grid-item card calendar-preview">
        <h3>Aperçu du Calendrier</h3>
        <div class="calendar-placeholder">
          <i class="fas fa-calendar-alt fa-3x"></i>
          <p>Voir rapidement les réservations planifiées</p>
          <NuxtLink to="/admin/calendar" class="btn btn-outline btn-sm">Ouvrir le calendrier</NuxtLink>
        </div>
      </div>
    </div>
</div>
</template>

<style scoped>
.dashboard-container {
  padding: 0;
}

.dashboard-header {
  margin-bottom: var(--space-10);
}

.quick-actions {
  margin-top: var(--space-4);
  display: flex;
  gap: var(--space-3);
}

.dashboard-header h1 {
  font-size: 1.75rem;
  font-weight: 800;
  margin-bottom: var(--space-1);
  color: #0f172a;
}

.dashboard-header p {
  color: #64748b;
  font-size: 0.95rem;
  font-weight: 500;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: var(--space-8);
  margin-top: var(--space-12);
  align-items: start;
}

.calendar-preview {
  display: flex;
  flex-direction: column;
}

.calendar-preview h3 {
  margin-bottom: var(--space-6);
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
}

.calendar-placeholder {
  flex: 1;
  height: 450px;
  background: var(--white);
  border-radius: var(--rounded-2xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  gap: var(--space-4);
  border: 2px dashed #e2e8f0;
}

.calendar-placeholder i {
  color: #cbd5e1;
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup>
definePageMeta({ layout: 'admin' })
</script>
