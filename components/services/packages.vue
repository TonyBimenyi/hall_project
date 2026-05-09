<template>
  <section class="packages-section">
    <div class="container">
      <h2 class="section-title">Our Event Packages</h2>
      <p class="section-subtitle">
        Choose the perfect package for your occasion — or let us create a custom one just for you.
      </p>

      <div class="packages-grid fade-up" ref="packagesRef">
        <!-- Basic Conference -->
        <div class="pricing-card">
          <h3 class="card-title">Basic Conference</h3>
          <p class="card-subtitle">Perfect for meetings, seminars & trainings</p>
          
          <div class="price">
            $500<span>/day</span>
          </div>

          <ul class="features-list">
            <li>Conference room (up to 100 guests)</li>
            <li>Basic AV (projector, screen, mic)</li>
            <li>High-speed WiFi</li>
            <li>Standard setup (tables & chairs)</li>
            <li>Complimentary parking</li>
            <li>8-hour rental</li>
          </ul>

          <button class="btn-outline" @click="$router.push('/book?package=basic')">
            Book Now
          </button>
        </div>

        <!-- Premium Event (highlighted) -->
        <div class="pricing-card popular">
          <div class="popular-badge">Most Popular</div>
          <h3 class="card-title">Premium Event</h3>
          <p class="card-subtitle">Ideal for celebrations & medium events</p>
          
          <div class="price">
            $1,200<span>/day</span>
          </div>

          <ul class="features-list">
            <li>Main hall (up to 250 guests)</li>
            <li>Premium AV & dynamic lighting</li>
            <li>Dance floor + stage setup</li>
            <li>Decorated entrance lobby</li>
            <li>Dedicated event coordinator</li>
            <li>Bridal suite access</li>
            <li>12-hour rental</li>
          </ul>

          <button class="btn-primary" @click="$router.push('/book?package=premium')">
            Book Now
          </button>
        </div>

        <!-- Luxury Wedding -->
        <div class="pricing-card">
          <h3 class="card-title">Luxury Wedding</h3>
          <p class="card-subtitle">All-inclusive premium wedding experience</p>
          
          <div class="price">
            $2,000<span>+ / customized</span>
          </div>

          <ul class="features-list">
            <li>Full venue access (up to 500 guests)</li>
            <li>Complete AV & custom lighting</li>
            <li>Ceremony + reception spaces</li>
            <li>Premium décor package</li>
            <li>Dedicated wedding planner</li>
            <li>Bridal suite & groom’s room</li>
            <li>Rehearsal access</li>
            <li>Flexible event timing</li>
          </ul>

          <button class="btn-outline" @click="$router.push('/book?package=luxury')">
            Get Quote
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const packagesRef = ref(null)

onMounted(() => {
  if (!('IntersectionObserver' in window)) {
    if (packagesRef.value) packagesRef.value.classList.add('visible')
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

  if (packagesRef.value) observer.observe(packagesRef.value)
})
</script>

<style scoped>
.packages-section {
  padding: clamp(5rem, 10vw, 9rem) 0;
  background: #f9fbff;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.section-title {
  font-family: var(--font-secondary);
  font-size: clamp(2.4rem, 6.5vw, 3.8rem);
  font-weight: 700;
  color: #0b234a;
  text-align: center;
  margin-bottom: 1rem;
}

.section-subtitle {
  text-align: center;
  font-size: clamp(1.1rem, 2.8vw, 1.3rem);
  color: #64748b;
  max-width: 680px;
  margin: 0 auto 4rem;
  line-height: 1.6;
}

.packages-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;

  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 2.5rem;
  }
}

.pricing-card {
  background: white;
  border-radius: 16px;
  padding: 2.2rem 1.8rem;
  border: 1px solid #edf2ff;
  box-shadow: 0 8px 24px rgba(11, 35, 74, 0.06);
  text-align: center;
  position: relative;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.pricing-card:hover {
  transform: translateY(-12px);
  box-shadow: 0 20px 40px rgba(11, 35, 74, 0.12);
}

.popular {
  border: 2px solid var(--accent-color);
  background: linear-gradient(145deg, #ffffff 0%, #f8fbff 100%);
  transform: scale(1.04);
  z-index: 2;
}

.popular:hover {
  transform: translateY(-12px) scale(1.06);
}

.popular-badge {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent-color);
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.45rem 1.2rem;
  border-radius: 50px;
  box-shadow: 0 4px 12px rgba(212, 160, 23, 0.25);
}

.card-title {
  font-family: var(--font-secondary);
  font-size: 1.65rem;
  font-weight: 700;
  color: #0b234a;
  margin-bottom: 0.6rem;
}

.card-subtitle {
  font-size: 1.05rem;
  color: #64748b;
  margin-bottom: 1.8rem;
  min-height: 2.8em;
}

.price {
  font-size: 2.6rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 1.2rem 0 2rem;
}

.price span {
  font-size: 1rem;
  font-weight: 400;
  color: #64748b;
  vertical-align: middle;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0 0 2.2rem;
  text-align: left;
}

.features-list li {
  font-size: 1.03rem;
  color: #37445b;
  margin-bottom: 1rem;
  padding-left: 1.8rem;
  position: relative;
  line-height: 1.5;
}

.features-list li::before {
  content: "✔";
  position: absolute;
  left: 0;
  color: var(--accent-color);
  font-weight: bold;
}

/* Buttons */
.btn-outline,
.btn-primary {
  width: 100%;
  padding: 1rem 1.5rem;
  border-radius: 50px;
  font-size: 1.05rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-outline {
  background: white;
  border: 2px solid var(--primary-color);
  color: var(--primary-color);
}

.btn-outline:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-3px);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: #001b4d;
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(11, 35, 74, 0.2);
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
</style>