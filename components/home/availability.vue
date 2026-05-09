<template>
  <section class="features-section">
    <h2 class="section-title">Vérifier la disponibilité</h2>

    <div class="features-flex " >
      <div class="feature-card fade-up" ref="cards">
        <p class="feature-text">
          Trouvez la date parfaite pour votre événement. Notre calendrier de réservation affiche la disponibilité en temps réel.
        </p>

        <button>Voir les dates disponibles</button>
      </div>
    </div>
  </section>
</template>


<script>


export default {
  mounted() {
    const { animateOnScroll } = useScrollAnimation()

    // Your composable expects an array of elements
    animateOnScroll([this.$refs.cards])
  }
}
</script>


<style scoped>
.features-section {
  padding: var(--space-32) 0;
  text-align: center;
  background-color: var(--gray-50);
}

.section-title {
  font-family: var(--font-serif);
  font-size: clamp(2.5rem, 5vw, 4rem);
  margin-bottom: var(--space-20);
  color: var(--primary);
  font-weight: 900;
}

.feature-card {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-16) var(--space-10);
  background: var(--white);
  border-radius: var(--rounded-3xl);
  box-shadow: var(--shadow-lg);
}

.feature-text {
  color: var(--gray-600);
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: var(--space-8);
}

.btn-check {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 700;
}

/* Scroll Animation */
.fade-up {
  opacity: 0;
  transform: translateY(30px);
  transition: var(--transition-all);
}

.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
