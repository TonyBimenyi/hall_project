<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="card story">
        <h2>{{ t('about.generalTitle') }}</h2>
        <p>{{ t('about.generalText') }}</p>
      </div>

      <div class="grid">
        <article class="card item">
          <i class="fas fa-eye"></i>
          <h3>{{ t('about.vision') }}</h3>
          <p>{{ t('about.visionText') }}</p>
        </article>
        <article class="card item">
          <i class="fas fa-bullseye"></i>
          <h3>{{ t('about.mission') }}</h3>
          <p>{{ t('about.missionText') }}</p>
        </article>
        <article class="card item">
          <i class="fas fa-handshake"></i>
          <h3>{{ t('about.values') }}</h3>
          <p>{{ t('about.valuesText') }}</p>
        </article>
      </div>

      <div class="split">
     

        <article class="card list-card">
          <h3>{{ t('about.clients') }}</h3>
          <div class="two-cols">
          
            <div>
              <ul>
                <li>{{ t('about.clientsItems.individuals') }}</li>
                <li>{{ t('about.clientsItems.businesses') }}</li>
                <li>{{ t('about.clientsItems.public') }}</li>
                <li>{{ t('about.clientsItems.travelers') }}</li>
              </ul>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
const { t } = useI18n()
</script>

<style scoped>
.client-page {
  background: #f8fafc;
  min-height: 100vh;
  padding: 5rem 0 3rem;
}

.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1rem;
}

.story {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  margin-bottom: 1rem;
}

.story h2 {
  margin: 0 0 .5rem;
}

.story p {
  margin: 0;
  color: #475569;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.item {
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.item i {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  background: rgba(212, 175, 55, .18);
  color: var(--primary);
  margin-bottom: .75rem;
}

.item h3 {
  margin: 0 0 .35rem;
}

.item p {
  margin: 0;
  color: #64748b;
}

.split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

.list-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.list-card h3 {
  margin-top: 0;
}

.list-card ul {
  margin: 0;
  padding-left: 1.1rem;
  color: #475569;
  line-height: 1.7;
  font-weight: 550;
}

.two-cols {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.mini-title {
  font-weight: 900;
  color: #0f172a;
  margin-bottom: .35rem;
}

@media (max-width: 900px) {
  .split {
    grid-template-columns: 1fr;
  }

  .two-cols {
    grid-template-columns: 1fr;
  }
}
</style>
