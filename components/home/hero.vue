<template>
  <section class="hero">
    <div class="overlay"></div>
    <div class="content">
      <h1 class="title">
        Où les moments deviennent
        <span class="highlight">Souvenirs</span>
      </h1>
      <p class="subtitle">
        Belta Réception & Salle de Conférence – Votre destination privilégiée pour les mariages, les événements d'entreprise et les célébrations inoubliables
      </p>
      <div class="buttons">
        <NuxtLink to="/book" class="btn-dashboard">
           <button class="btn btn-primary">Réserver maintenant</button>
        </NuxtLink>
       <NuxtLink to="/gallery" class="btn-dashboard">
         <button class="btn btn-secondary">Voir la galerie</button>
       </NuxtLink>
       
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'HeroSection'
}
</script>

<style scoped>
.hero {
  position: relative;
  width: 100%;
  height: 100vh;
  background-image: url('https://images.unsplash.com/photo-1519167758481-83f550bb49b3?auto=format&fit=crop&w=1900&q=80');
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(6, 27, 73, 0.85),
    rgba(6, 27, 73, 0.6)
  );
  backdrop-filter: blur(2px);
}

.content {
  position: relative;
  z-index: 2;
  max-width: 900px;
  padding: 0 var(--space-6);
  animation: fadeInUp 1s ease-out;
}

.title {
  font-family: var(--font-serif);
  font-size: clamp(3rem, 8vw, 5rem);
  font-weight: 900;
  line-height: 1.1;
  margin-bottom: var(--space-6);
  color: var(--white);
  letter-spacing: -0.02em;
}

.highlight {
  color: var(--accent);
  display: inline-block;
  position: relative;
}

.highlight::after {
  content: '';
  position: absolute;
  bottom: 10px;
  left: 0;
  width: 100%;
  height: 8px;
  background: rgba(212, 175, 55, 0.3);
  z-index: -1;
}

.subtitle {
  font-size: clamp(1.1rem, 3vw, 1.4rem);
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
  max-width: 700px;
  margin: 0 auto var(--space-12);
  font-weight: 400;
}

.buttons {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
}

.btn-lg {
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .buttons {
    flex-direction: column;
  }
  
  .btn-lg {
    width: 100%;
  }
}
</style>