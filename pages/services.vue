<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="services-grid">
        <article class="card service">
          <h3>Location de salle</h3>
          <p>Espaces adaptés à différents formats d’événements.</p>
        </article>
        <article class="card service">
          <h3>Organisation événementielle</h3>
          <p>Coordination complète et gestion logistique personnalisée.</p>
        </article>
        <article class="card service">
          <h3>Équipement technique</h3>
          <p>Sonorisation, projection, éclairage et support audiovisuel.</p>
        </article>
        <article class="card service">
          <h3>Accueil & service client</h3>
          <p>Équipe dédiée pour l’accueil des invités et le suivi sur place.</p>
        </article>
      </div>

      <div class="cta card">
        <h2>Besoin d’une offre personnalisée ?</h2>
        <p>Contactez-nous ou réservez directement en ligne.</p>
        <div class="cta-actions">
          <NuxtLink to="/contact" class="btn btn-outline">Nous contacter</NuxtLink>
          <NuxtLink to="/book" class="btn btn-primary">Réserver</NuxtLink>
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

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1rem;
}

.service {
  border: 1px solid #e2e8f0;
  box-shadow: none;
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
</style>
