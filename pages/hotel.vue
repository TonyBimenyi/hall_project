<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="card coming-soon">
        <div class="pill">Bientot Disponible</div>
        <h2>Hotel LaBertha Villa</h2>
        <p>
          Cette section est en cours de préparation. Très bientôt, vous pourrez découvrir nos chambres,
          nos services et effectuer vos réservations en ligne.
        </p>
        <NuxtLink to="/" class="btn btn-primary btn-sm">Retour à l’accueil</NuxtLink>
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

.coming-soon {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.4rem;
  text-align: center;
}

.pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 0.72rem;
  margin-bottom: 0.9rem;
}

.coming-soon h2 {
  margin: 0 0 0.5rem;
  color: #0f172a;
}

.coming-soon p {
  margin: 0 auto 1rem;
  max-width: 720px;
  color: #64748b;
  line-height: 1.6;
}
</style>
