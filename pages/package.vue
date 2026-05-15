<template>
  <section class="client-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="intro card">
        <div class="intro-left">
          <div class="pill">Package</div>
          <h2>Des formules simples, claires et modernes</h2>
          <p>
            Choisissez un package selon votre budget et le type d’événement. Chaque formule peut être ajustée
            sur demande (décoration, sonorisation, disposition, etc.).
          </p>
        </div>
        <div class="intro-right">
          <div class="meta">
            <div class="meta-item">
              <div class="meta-label">Réservation</div>
              <div class="meta-value">En ligne</div>
            </div>
            <div class="meta-item">
              <div class="meta-label">Confirmation</div>
              <div class="meta-value">Par email</div>
            </div>
            <div class="meta-item">
              <div class="meta-label">Support</div>
              <div class="meta-value">Dédié</div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid">
        <article class="pkg card">
          <div class="pkg-top">
            <h3>Essentiel</h3>
            <div class="tag">Populaire</div>
          </div>
          <p class="pkg-desc">
            Idéal pour une réservation rapide avec les besoins principaux.
          </p>
          <ul class="pkg-list">
            <li>Salle + disposition standard</li>
            <li>Nettoyage inclus</li>
            <li>Assistance de base sur place</li>
            <li>Accès calendrier des disponibilités</li>
          </ul>
          <NuxtLink to="/book" class="btn btn-primary btn-sm">Reserver la salle</NuxtLink>
        </article>

        <article class="pkg card highlighted">
          <div class="pkg-top">
            <h3>Premium</h3>
            <div class="tag dark">Recommandé</div>
          </div>
          <p class="pkg-desc">
            Une formule complète pour une expérience fluide et élégante.
          </p>
          <ul class="pkg-list">
            <li>Décoration de base + éclairage</li>
            <li>Sonorisation (standard)</li>
            <li>Accompagnement avant événement</li>
            <li>Priorité support</li>
          </ul>
          <NuxtLink to="/contact" class="btn btn-primary btn-sm">Demander un devis</NuxtLink>
        </article>

        <article class="pkg card">
          <div class="pkg-top">
            <h3>Signature</h3>
            <div class="tag">Sur mesure</div>
          </div>
          <p class="pkg-desc">
            Pour les grands événements et une personnalisation totale.
          </p>
          <ul class="pkg-list">
            <li>Décoration avancée</li>
            <li>Sonorisation + lumière améliorées</li>
            <li>Coordination événementielle</li>
            <li>Options additionnelles à la carte</li>
          </ul>
          <NuxtLink to="/contact" class="btn btn-outline btn-sm">Parler à un conseiller</NuxtLink>
        </article>
      </div>

      <div class="cta card">
        <div>
          <h3>Besoin d’un package personnalisé ?</h3>
          <p>Contactez-nous et recevez une proposition adaptée à votre événement.</p>
        </div>
        <div class="cta-actions">
          <NuxtLink to="/contact" class="btn btn-primary">Nous contacter</NuxtLink>
          <NuxtLink to="/gallery" class="btn btn-outline">Voir la gallerie</NuxtLink>
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

.intro {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: rgba(212, 175, 55, .18);
  color: #a16207;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  font-size: 0.72rem;
  margin-bottom: 0.75rem;
}

.intro h2 {
  margin: 0 0 0.5rem;
  color: #0f172a;
  font-size: clamp(1.4rem, 2.6vw, 1.9rem);
  line-height: 1.2;
}

.intro p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
}

.meta {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 0.9rem;
  background: #ffffff;
  display: grid;
  gap: 0.75rem;
}

.meta-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.meta-label {
  color: #64748b;
  font-weight: 800;
  font-size: 0.82rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.meta-value {
  color: #0f172a;
  font-weight: 900;
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.pkg {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.25rem;
  display: grid;
  gap: 0.8rem;
}

.pkg.highlighted {
  border-color: rgba(212, 175, 55, 0.65);
  box-shadow: 0 18px 35px rgba(15, 23, 42, 0.10);
}

.pkg-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.pkg h3 {
  margin: 0;
  color: #0f172a;
  font-size: 1.1rem;
}

.tag {
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-weight: 900;
  font-size: 0.72rem;
  color: #334155;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.tag.dark {
  border-color: #0f172a;
  background: #0f172a;
  color: #fff;
}

.pkg-desc {
  margin: 0;
  color: #64748b;
  line-height: 1.55;
}

.pkg-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.45rem;
  color: #334155;
  font-weight: 600;
  font-size: 0.95rem;
}

.pkg-list li {
  display: flex;
  gap: 0.55rem;
  align-items: flex-start;
}

.pkg-list li::before {
  content: "•";
  color: #d4af37;
  font-weight: 900;
  line-height: 1.2;
}

.cta {
  margin-top: 1rem;
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.cta h3 {
  margin: 0 0 0.25rem;
  color: #0f172a;
}

.cta p {
  margin: 0;
  color: #64748b;
}

.cta-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

@media (max-width: 1000px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .intro {
    grid-template-columns: 1fr;
  }

  .cta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
