<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="card story">
        <h2>Notre mission</h2>
        <p>
          Offrir une expérience événementielle élégante, fiable et sans stress à chaque client. Nous combinons des espaces modernes, une équipe professionnelle et une organisation rigoureuse.
        </p>
      </div>

      <div class="grid">
        <article class="card item">
          <i class="fas fa-medal"></i>
          <h3>Qualité de service</h3>
          <p>Accompagnement attentif du premier contact jusqu’à la fin de l’événement.</p>
        </article>
        <article class="card item">
          <i class="fas fa-clock"></i>
          <h3>Organisation maîtrisée</h3>
          <p>Processus clair, planning précis et communication transparente.</p>
        </article>
        <article class="card item">
          <i class="fas fa-users"></i>
          <h3>Équipe dédiée</h3>
          <p>Personnel expérimenté pour répondre à vos besoins techniques et logistiques.</p>
        </article>
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
  background: #eef2ff;
  color: #4338ca;
  margin-bottom: .75rem;
}

.item h3 {
  margin: 0 0 .35rem;
}

.item p {
  margin: 0;
  color: #64748b;
}
</style>
