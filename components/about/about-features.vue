<template>
  <section class="why-choose-section">
    <div class="container">
      <h2 class="section-title">Why Choose Elite Reception</h2>

      <div class="features-grid">
        <div
          v-for="(feature, index) in features"
          :key="feature.title"
          class="feature-card fade-up"
          :style="{ transitionDelay: `${index * 120}ms` }"
        >
          <div class="icon-circle">
            <Icon :icon="feature.icon" height="38" color="white" />
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-text">{{ feature.text }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'WhyChooseSection',

  data() {
    return {
      features: [
        {
          icon: 'mdi:calendar-month',
          title: 'Flexible Capacity',
          text: 'Accommodate 50 to 500 guests with flexible room configurations and multiple layout options'
        },
        {
          icon: 'mdi:account-group',
          title: 'Premium Amenities',
          text: 'State-of-the-art AV systems, customizable lighting, high-speed WiFi, and climate control'
        },
        {
          icon: 'mdi:leaf',
          title: 'Eco-Conscious',
          text: 'Energy-efficient systems, waste reduction practices, and sustainable event solutions'
        },
        {
          icon: 'mdi:star-outline',
          title: 'Full-Service Experience',
          text: 'In-house catering, professional décor coordination, and dedicated event planning support'
        }
      ]
    }
  },

  mounted() {
    this.initScrollAnimation()
  },

  methods: {
    initScrollAnimation() {
      if (!('IntersectionObserver' in window)) return

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('visible')
            }
          })
        },
        {
          threshold: 0.18,
          rootMargin: '0px 0px -90px 0px'
        }
      )

      document.querySelectorAll('.feature-card').forEach(card => {
        observer.observe(card)
      })
    }
  }
}
</script>

<style scoped>
.why-choose-section {
  padding: clamp(4.5rem, 9vw, 8rem) 0;
  background: #f9fbff;
  text-align: center;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.section-title {
  font-family: var(--font-secondary);
  font-size: clamp(2.3rem, 6vw, 3.6rem);
  font-weight: 700;
  color: #0a1f44;
  margin-bottom: clamp(2.5rem, 6vw, 5rem);
  letter-spacing: -0.02em;
}

/* ─── GRID LAYOUT ─── */
.features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.6rem;

  @media (min-width: 640px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(4, 1fr);
    gap: 2.2rem;
  }
}

/* Card */
.feature-card {
  background: white;
  border-radius: 16px;
  padding: 2.4rem 1.8rem;
  border: 1px solid #e5edff;
  box-shadow: 0 8px 24px rgba(10, 31, 68, 0.05);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  text-align: center;
}

.feature-card:hover {
  transform: translateY(-12px) scale(1.015);
  box-shadow: 0 20px 40px rgba(10, 31, 68, 0.12);
  border-color: rgba(212, 160, 23, 0.25);
}

.icon-circle {
  width: 80px;
  height: 80px;
  background: #0a1f44;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.6rem;
  transition: all 0.4s ease;
}

.feature-card:hover .icon-circle {
  background: var(--accent-color);
  transform: scale(1.1);
}

.feature-title {
  font-family: var(--font-secondary);
  font-size: 1.38rem;
  font-weight: 600;
  color: #0a1f44;
  margin-bottom: 1rem;
}

.feature-text {
  font-family: var(--font-primary);
  color: #64748b;
  line-height: 1.65;
  font-size: 1.03rem;
}

/* Animation */
.fade-up {
  opacity: 0;
  transform: translateY(45px);
}

.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.95s ease-out, transform 0.95s ease-out;
}
</style>