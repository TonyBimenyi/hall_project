<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="services-head card">
        <div>
          <h2>{{ t('services.title') }}</h2>
          <p>
            {{ t('services.intro') }}
          </p>
        </div>
        <div class="services-actions">
          <NuxtLink :to="localePath('/package')" class="btn btn-outline">{{ t('services.viewPackages') }}</NuxtLink>
          <NuxtLink :to="localePath('/book')" class="btn btn-primary">{{ t('services.reserveRoom') }}</NuxtLink>
        </div>
      </div>

      <div class="services-grid">
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-bed"></i>
            <h3>{{ t('services.lodgingTitle') }}</h3>
          </div>
          <p>{{ t('services.lodgingText') }}</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-building"></i>
            <h3>{{ t('services.hallTitle') }}</h3>
          </div>
          <p>{{ t('services.hallText') }}</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-utensils"></i>
            <h3>{{ t('services.cateringTitle') }}</h3>
          </div>
          <p>{{ t('services.cateringText') }}</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-tree"></i>
            <h3>{{ t('services.outdoorTitle') }}</h3>
          </div>
          <p>{{ t('services.outdoorText') }}</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-shield-halved"></i>
            <h3>{{ t('services.securityTitle') }}</h3>
          </div>
          <p>{{ t('services.securityText') }}</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-handshake"></i>
            <h3>{{ t('services.partnershipsTitle') }}</h3>
          </div>
          <p>{{ t('services.partnershipsText') }}</p>
        </article>
      </div>

      <div class="cta card">
        <h2>{{ t('services.ctaTitle') }}</h2>
        <p>{{ t('services.ctaText') }}</p>
        <div class="cta-actions">
          <NuxtLink :to="localePath('/contact')" class="btn btn-outline">{{ t('services.contactUs') }}</NuxtLink>
          <NuxtLink :to="localePath('/package')" class="btn btn-outline">{{ t('services.packages') }}</NuxtLink>
          <NuxtLink :to="localePath('/book')" class="btn btn-primary">{{ t('services.reserve') }}</NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const { t } = useI18n()
const localePath = useLocalePath()
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

.services-head {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.services-head h2 {
  margin: 0 0 0.35rem;
  color: #0f172a;
}

.services-head p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

.services-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.service {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.25rem;
}

.service-top {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 0.55rem;
}

.service-top i {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 175, 55, .18);
  color: #a16207;
}

.service h3 {
  margin: 0 0 .35rem;
  font-size: 17px;
  font-weight: 800;
}

.service p {
  margin: 0;
  color: #64748b;
}

.cta {
  margin-top: 1rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
  text-align: center;
}

.cta h2 {
  margin: 0 0 .35rem;
}

.cta p {
  color: #64748b;
  margin-bottom: .9rem;
}

.cta-actions {
  display: flex;
  justify-content: center;
  gap: .75rem;
  flex-wrap: wrap;
}

@media (max-width: 820px) {
  .services-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .services-actions {
    justify-content: flex-start;
  }
}
</style>
