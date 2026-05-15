<template>
  <section class="about-section">
    <div class="container">
      <div class="title fade-up" ref="titleEl">
        <h1>Notre Histoire</h1>
      </div>

      <div class="story-content fade-up" ref="storyEl">
        <p>
          Fondée en 2013, <strong>LaBertha Villa</strong> est devenue le lieu le plus fiable et le plus apprécié de la ville pour les célébrations les plus marquantes de la vie.
        </p>
        <p>
          Ce qui a commencé comme une vision passionnée pour créer un espace où naissent des souvenirs inoubliables a évolué en un chef-d'œuvre d'élégance et de fonctionnalité de plus de 2 000 mètres carrés.
        </p>
        <p>
          Nous mélangeons harmonieusement la sophistication intemporelle avec des équipements de pointe, offrant le cadre parfait pour :
        </p>
        <ul>
          <li>Mariages et réceptions exquis</li>
          <li>Conférences professionnelles et séminaires d'entreprise</li>
          <li>Anniversaires, fêtes et célébrations marquantes</li>
          <li>Lancements de produits, galas et occasions spéciales</li>
        </ul>
        <p>
          Notre équipe dévouée s'engage à offrir un service personnalisé exceptionnel et une attention méticuleuse aux détails. Nous travaillons en étroite collaboration avec chaque client pour transformer leur vision unique en une expérience événementielle extraordinaire et sans faille.
        </p>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'AboutSection',

  mounted() {
    this.setupScrollAnimation()
  },

  methods: {
    setupScrollAnimation() {
      if (!('IntersectionObserver' in window)) {
        // Fallback for very old browsers
        [this.$refs.titleEl, this.$refs.storyEl].forEach(el => {
          if (el) el.classList.add('visible')
        })
        return
      }

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible')
            }
          })
        },
        {
          threshold: 0.15,
          rootMargin: '0px 0px -80px 0px'
        }
      )

      if (this.$refs.titleEl) observer.observe(this.$refs.titleEl)
      if (this.$refs.storyEl) observer.observe(this.$refs.storyEl)
    }
  }
}
</script>

<style scoped>
.about-section {
  padding: clamp(4rem, 9vw, 7.5rem) 0;
  background: #f9fbff;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.title {
  text-align: center;
  margin-bottom: clamp(2.5rem, 6vw, 4.5rem);
}

.title h1 {
  font-family: var(--font-secondary);
  font-size: clamp(2.6rem, 6.8vw, 4.2rem);
  font-weight: 700;
  color: #0a1f44;
  letter-spacing: -0.02em;
  margin: 0;
}

.story-content {
  font-family: var(--font-primary);
  color: #334155;
  font-size: clamp(1.05rem, 2.8vw, 1.22rem);
  line-height: 1.78;
  text-align: left;
}

.story-content p {
  margin-bottom: 1.6rem;
}

.story-content strong {
  color: #0a1f44;
  font-weight: 600;
}

.story-content ul {
  list-style: none;
  padding-left: 0;
  margin: 1.8rem 0 2.2rem;
}

.story-content ul li {
  position: relative;
  padding-left: 1.8rem;
  margin-bottom: 0.9rem;
}

.story-content ul li::before {
  content: "•";
  color: var(--accent-color);
  position: absolute;
  left: 0;
  font-size: 1.4rem;
  line-height: 1;
}

/* Animation */
.fade-up {
  opacity: 0;
  transform: translateY(40px);
}

.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.9s ease-out, transform 0.9s ease-out;
}

/* Stagger slightly */
.title.visible {
  transition-delay: 0.1s;
}

.story-content.visible {
  transition-delay: 0.3s;
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .story-content {
    font-size: clamp(1.05rem, 3.8vw, 1.15rem);
  }
  
  .story-content ul {
    padding-left: 0.5rem;
  }
}
</style>
