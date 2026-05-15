<template>
  <section class="features-section">
    <div class="container">
      <h2 class="section-title">Pourquoi choisir LaBertha Villa</h2>
      
      <div class="features-grid">
        <div
          v-for="(item, index) in features"
          :key="index"
          class="feature-card fade-up"
          :style="{ transitionDelay: `${index * 100}ms` }"
        >
          <div class="icon-circle">
            <Icon :icon="item.icon" height="36" color="var(--accent-color)" />
          </div>
          <h3 class="feature-title">{{ item.title }}</h3>
          <p class="feature-text">{{ item.text }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'FeaturesSection',
  
  data() {
    return {
      features: [
        { 
          icon: "mdi:calendar-month", 
          title: "Planification Flexible", 
          text: "Choisissez votre date idéale avec notre système de réservation adaptable et plusieurs configurations de salle." 
        },
        { 
          icon: "mdi:account-group", 
          title: "50–500 Invités", 
          text: "Des réunions intimes aux grandes célébrations — nous nous adaptons sans effort à votre liste d'invités." 
        },
        { 
          icon: "mdi:trophy-outline", 
          title: "Équipements Premium", 
          text: "Éclairage professionnel, son cristallin, audiovisuel haut de gamme, climatisation et plus encore." 
        },
        { 
          icon: "mdi:star-outline", 
          title: "Service Récompensé", 
          text: "Reconnu comme l'un des lieux les plus fiables et les mieux notés de la ville." 
        }
      ]
    }
  },

  mounted() {
    this.setupScrollAnimation()
  },

  methods: {
    setupScrollAnimation() {
      if (!('IntersectionObserver' in window)) return

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible')
              // observer.unobserve(entry.target) // uncomment if you want one-time animation
            }
          })
        },
        {
          threshold: 0.15,
          rootMargin: '0px 0px -80px 0px'
        }
      )

      const cards = document.querySelectorAll('.feature-card')
      cards.forEach(card => observer.observe(card))
    }
  }
}
</script>

<style scoped>
.features-section {
  padding: var(--space-32) 0;
  background: var(--white);
}

.section-title {
  font-family: var(--font-serif);
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 900;
  text-align: center;
  margin-bottom: var(--space-24);
  position: relative;
  color: var(--primary);
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -24px;
  left: 50%;
  transform: translateX(-50%);
  width: 100px;
  height: 6px;
  background: var(--accent);
  border-radius: var(--rounded-full);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-12);
}

.feature-card {
  padding: var(--space-12) var(--space-8);
  background: var(--gray-50);
  border-radius: var(--rounded-3xl);
  border: 1px solid var(--gray-100);
  transition: var(--transition-all);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.feature-card:hover {
  background: var(--white);
  box-shadow: var(--shadow-xl);
  transform: translateY(-10px);
  border-color: var(--accent);
}

.icon-circle {
  width: 80px;
  height: 80px;
  background: var(--white);
  border-radius: var(--rounded-2xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-md);
  transition: var(--transition-all);
}

.feature-card:hover .icon-circle {
  background: var(--primary);
  transform: rotate(10deg);
}

.feature-title {
  font-family: var(--font-serif);
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--space-4);
  color: var(--primary);
}

.feature-text {
  color: var(--gray-600);
  line-height: 1.7;
}

/* Scroll Animation */
.fade-up {
  opacity: 0;
  transform: translateY(30px);
}

.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
