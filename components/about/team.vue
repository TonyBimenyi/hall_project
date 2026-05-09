<template>
  <section class="team-section">
    <div class="container">
      <h2 class="section-title">Our Team</h2>

      <div class="team-content fade-up" ref="teamRef">
        <div class="team-intro">
          <p class="team-text">
            Our dedicated team brings over <strong>50 years</strong> of combined experience in luxury event management and hospitality. 
            We are passionate about turning your vision into flawless, unforgettable celebrations — with seamless planning and heartfelt care every step of the way.
          </p>
        </div>

        <div class="cta-area">
          <h3 class="cta-heading">
            Ready to experience our venue in person?
          </h3>
          <p class="cta-subtext">
            Contact us today to schedule a personal tour and consultation.
          </p>
          <button class="cta-btn" @click="$router.push('/contact')">
            Book a Tour & Consultation
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'TeamSection',

  mounted() {
    this.initScrollAnimation()
  },

  methods: {
    initScrollAnimation() {
      if (!('IntersectionObserver' in window)) {
        if (this.$refs.teamRef) this.$refs.teamRef.classList.add('visible')
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
          threshold: 0.2,
          rootMargin: '0px 0px -100px 0px'
        }
      )

      if (this.$refs.teamRef) observer.observe(this.$refs.teamRef)
    }
  }
}
</script>

<style scoped>
.team-section {
  padding: clamp(4.5rem, 10vw, 8rem) 0;
  background: #f9fbff; /* light elegant background */
  text-align: center;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.section-title {
  font-family: var(--font-secondary);
  font-size: clamp(2.4rem, 6.5vw, 3.8rem);
  font-weight: 700;
  color: #0a1f44;
  margin-bottom: clamp(2.5rem, 6vw, 4.5rem);
  letter-spacing: -0.02em;
}

.team-content {
  background: white;
  border-radius: 20px;
  padding: clamp(2.5rem, 5vw, 4rem);
  box-shadow: 0 10px 40px rgba(10, 31, 68, 0.06);
  max-width: 920px;
  margin: 0 auto;
  transition: all 0.4s ease;
}

.team-content:hover {
  box-shadow: 0 20px 60px rgba(10, 31, 68, 0.1);
  transform: translateY(-6px);
}

.team-intro {
  margin-bottom: 3rem;
}

.team-text {
  font-family: var(--font-primary);
  font-size: clamp(1.1rem, 2.8vw, 1.28rem);
  line-height: 1.75;
  color: #475569;
  max-width: 780px;
  margin: 0 auto;
}

.team-text strong {
  color: #0a1f44;
  font-weight: 600;
}

.cta-area {
  margin-top: 2rem;
}

.cta-heading {
  font-family: var(--font-secondary);
  font-size: clamp(1.6rem, 4vw, 2.1rem);
  color: #0a1f44;
  margin-bottom: 1rem;
  font-weight: 600;
}

.cta-subtext {
  font-size: clamp(1rem, 2.5vw, 1.15rem);
  color: #64748b;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.cta-btn {
  font-family: var(--font-primary);
  font-size: 1.1rem;
  font-weight: 600;
  padding: 1rem 2.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  box-shadow: 0 6px 20px rgba(10, 31, 68, 0.12);
  min-width: 260px;
}

.cta-btn:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(10, 31, 68, 0.2);
  background: #001b4d; /* slightly darker on hover */
}

/* Animation */
.fade-up {
  opacity: 0;
  transform: translateY(50px);
}

.fade-up.visible {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 1s ease-out, transform 1s ease-out;
}

/* Mobile tweaks */
@media (max-width: 640px) {
  .team-content {
    padding: 2rem 1.2rem;
  }
  
  .cta-btn {
    width: 100%;
    max-width: 340px;
  }
}
</style>