<template>
  <section class="cta-section fade-up" ref="ctaBox">
    <div class="container">
      <h2 class="cta-title">Prêt à planifier votre événement parfait ?</h2>
      <p class="cta-subtitle">
        Laissez-nous vous aider à créer une expérience inoubliable — qu'il s'agisse d'un mariage de rêve,
        d'un gala d'entreprise ou d'une célébration marquante.
      </p>
      <div class="cta-buttons">
        <button class="cta-btn primary" @click="$router.push('/book')">
          Réserver votre date
        </button>
        <button class="cta-btn outline" @click="$router.push('/contact')">
          Contactez-nous
        </button>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'CTASection',
  mounted() {
    this.setupScrollAnimation()
  },
  methods: {
    setupScrollAnimation() {
      if (!('IntersectionObserver' in window)) {
        if (this.$refs.ctaBox) {
          this.$refs.ctaBox.classList.add('visible')
        }
        return
      }
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible')
              // observer.unobserve(entry.target) // uncomment if you want animation only once
            }
          })
        },
        {
          threshold: 0.2,
          rootMargin: '0px 0px -100px 0px'
        }
      )
      if (this.$refs.ctaBox) {
        observer.observe(this.$refs.ctaBox)
      }
    }
  }
}
</script>

<style scoped>
.cta-section {
  width: 100%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  padding: var(--space-32) 0;
  color: var(--white);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 var(--space-6);
  position: relative;
  z-index: 2;
}

.cta-title {
  font-family: var(--font-serif);
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 900;
  margin-bottom: var(--space-8);
  line-height: 1.1;
}

.cta-subtitle {
  font-size: 1.25rem;
  line-height: 1.7;
  margin-bottom: var(--space-16);
  color: rgba(255, 255, 255, 0.9);
}

.cta-buttons {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
}

.cta-btn {
  padding: 1rem 2.5rem;
  font-size: 1.1rem;
  font-weight: 700;
  border-radius: var(--rounded-md);
}

.cta-btn.primary {
  background: var(--accent);
  color: var(--primary);
}

.cta-btn.primary:hover {
  background: var(--accent-light);
  transform: translateY(-3px);
}

.cta-btn.outline {
  border: 2px solid var(--white);
  color: var(--white);
}

.cta-btn.outline:hover {
  background: var(--white);
  color: var(--primary);
  transform: translateY(-3px);
}

@media (max-width: 768px) {
  .cta-buttons {
    flex-direction: column;
  }
  
  .cta-btn {
    width: 100%;
  }
}

.fade-up {
  opacity: 0;
  transform: translateY(30px);
}

.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
  transition: var(--transition-all);
}
</style>