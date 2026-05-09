<template>
  <section class="perfect-for-section">
    <div class="container">
      <h2 class="section-title">Perfect For Every Occasion</h2>
      
      <p class="section-subtitle">
        From intimate celebrations to large-scale professional events — 
        our versatile spaces adapt beautifully to your vision.
      </p>

      <div class="perfect-grid">
        <div
          v-for="(item, index) in items"
          :key="index"
          class="perfect-item"
          :class="{ 'highlight': item.highlight }"
        >
          <div class="item-content">
            <span class="item-label">{{ item.label }}</span>
            <span v-if="item.highlight" class="highlight-tag">Featured</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const items = [
  { label: "Weddings" },
  { label: "Corporate Events" },
  { label: "Conferences" },
  { label: "Seminars & Trainings" },
  { label: "Birthday Parties" },
  { label: "Anniversary Celebrations" },
  { label: "Engagement Parties", highlight: true },
  { label: "Holiday & Seasonal Parties" },
  { label: "Fundraisers & Galas" },
  { label: "Award Ceremonies" },
  { label: "Product Launches" },
  { label: "Networking Events & Mixers" },
  { label: "Baby Showers" },
  { label: "Reunions" }
];
</script>

<style scoped>
.perfect-for-section {
  padding: clamp(5rem, 10vw, 8.5rem) 0;
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
  color: #0a1f44;
  text-align: center;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.section-subtitle {
  text-align: center;
  font-size: clamp(1.05rem, 2.6vw, 1.25rem);
  color: #64748b;
  max-width: 720px;
  margin: 0 auto 3.5rem;
  line-height: 1.6;
}

.perfect-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.4rem;

  @media (min-width: 640px) {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.6rem;
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 1.8rem;
  }

  @media (min-width: 1280px) {
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
  }
}

.perfect-item {
  background: white;
  border-radius: 16px;
  padding: 1.8rem 1.2rem;
  text-align: center;
  box-shadow: 0 6px 20px rgba(10, 31, 68, 0.05);
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.perfect-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 16px 36px rgba(10, 31, 68, 0.12);
}

.item-content {
  position: relative;
  z-index: 2;
}

.item-label {
  font-family: var(--font-primary);
  font-size: clamp(1.05rem, 2.4vw, 1.22rem);
  font-weight: 600;
  color: #0a1f44;
  line-height: 1.4;
}

.highlight {
  background: linear-gradient(135deg, #fffaf0 0%, #fff5e6 100%);
  border: 2px solid var(--accent-color);
  box-shadow: 0 8px 28px rgba(212, 160, 23, 0.12);
}

.highlight .item-label {
  color: #b8860b;
  font-weight: 700;
}

.highlight-tag {
  position: absolute;
  top: 12px;
  right: 12px;
  background: var(--accent-color);
  color: white;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.35rem 0.8rem;
  border-radius: 50px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transform: rotate(12deg);
}

/* Optional subtle background pattern for highlighted card */
.highlight::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 20% 30%, rgba(212,160,23,0.04) 0%, transparent 60%);
  opacity: 0.6;
  pointer-events: none;
  z-index: 1;
}
</style>