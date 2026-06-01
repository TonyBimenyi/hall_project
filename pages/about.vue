<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="card story">
        <h2>Présentation générale</h2>
        <p>
          LaBertha VILLA est une structure d’hôtellerie et de location de salle de réception située à Karurama,
          dans la commune Cibitoke de la nouvelle province de Bujumbura au Burundi. Elle offre un cadre élégant,
          paisible et sécurisé pour les séjours professionnels, touristiques et l’organisation d’événements privés
          ou institutionnels. À LaBertha VILLA, nous valorisons l’hospitalité burundaise, combinée à des standards
          modernes de confort et d’accueil.
        </p>
      </div>

      <div class="grid">
        <article class="card item">
          <i class="fas fa-eye"></i>
          <h3>Vision</h3>
          <p>
            Devenir une référence régionale en matière d’hôtellerie et d’événementiel, alliant hospitalité
            burundaise, confort moderne et excellence de service.
          </p>
        </article>
        <article class="card item">
          <i class="fas fa-bullseye"></i>
          <h3>Mission</h3>
          <p>
            Offrir des services d’hébergement et d’organisation événementielle de qualité supérieure, adaptés aux
            besoins des particuliers, entreprises et institutions, dans un environnement chaleureux et professionnel.
          </p>
        </article>
        <article class="card item">
          <i class="fas fa-handshake"></i>
          <h3>Valeurs</h3>
          <p>Hospitalité • Qualité de service • Professionnalisme • Intégrité • Satisfaction client</p>
        </article>
      </div>

      <div class="split">
        <article class="card list-card">
          <h3>Nos services</h3>
          <ul>
            <li>Hébergement hôtelier de standing, confortable et soigné</li>
            <li>Salle de réception pour mariages, conférences, séminaires et événements privés</li>
            <li>Restauration et service traiteur sur demande</li>
            <li>Espaces extérieurs pour événements</li>
            <li>Environnement calme, propice à la détente et à la concentration</li>
            <li>Parking sécurisé</li>
            <li>Partenariats ouverts avec entreprises, ONG et institutions</li>
          </ul>
        </article>

        <article class="card list-card">
          <h3>Nos atouts & clients</h3>
          <div class="two-cols">
            <div>
              <div class="mini-title">Atouts</div>
              <ul>
                <li>Localisation stratégique à Karurama (Cibitoke)</li>
                <li>Cadre calme et naturel</li>
                <li>Architecture élégante et moderne</li>
                <li>Personnel accueillant et professionnel</li>
                <li>Excellent rapport qualité/prix</li>
              </ul>
            </div>
            <div>
              <div class="mini-title">Clients</div>
              <ul>
                <li>Particuliers</li>
                <li>Entreprises et ONG</li>
                <li>Institutions publiques</li>
                <li>Voyageurs et touristes</li>
              </ul>
            </div>
          </div>
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
