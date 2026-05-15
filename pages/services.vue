<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="services-head card">
        <div>
          <h2>Nos services</h2>
          <p>
            Des prestations flexibles pour accompagner votre événement, de la location à la coordination.
          </p>
        </div>
        <div class="services-actions">
          <NuxtLink to="/package" class="btn btn-outline">Voir les packages</NuxtLink>
          <NuxtLink to="/book" class="btn btn-primary">Reserver la salle</NuxtLink>
        </div>
      </div>

      <div class="services-grid">
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-building"></i>
            <h3>Location de salle</h3>
          </div>
          <p>Espaces adaptés à différents formats d’événements, avec configuration selon vos besoins.</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-list-check"></i>
            <h3>Organisation événementielle</h3>
          </div>
          <p>Coordination complète et gestion logistique personnalisée pour un déroulement sans stress.</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-volume-high"></i>
            <h3>Équipement technique</h3>
          </div>
          <p>Sonorisation, projection, éclairage et support audiovisuel pour une ambiance réussie.</p>
        </article>
        <article class="card service">
          <div class="service-top">
            <i class="fas fa-headset"></i>
            <h3>Accueil & service client</h3>
          </div>
          <p>Équipe dédiée pour l’accueil des invités et le suivi sur place pendant l’événement.</p>
        </article>
      </div>

      <div class="cta card">
        <h2>Besoin d’une offre personnalisée ?</h2>
        <p>Contactez-nous ou réservez directement en ligne.</p>
        <div class="cta-actions">
          <NuxtLink to="/contact" class="btn btn-outline">Nous contacter</NuxtLink>
          <NuxtLink to="/package" class="btn btn-outline">Packages</NuxtLink>
          <NuxtLink to="/book" class="btn btn-primary">Reserver</NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.client-page {
  background: #f8fafc;
  min-height: 100vh;
  padding: 5rem 0 3rem;
}

.container {
  max-width: 1160px;
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
