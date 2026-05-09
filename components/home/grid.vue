<template>
  <section class="gallery-section">
    <div class="container">
      <h2 class="section-title">Our Spaces</h2>

      <!-- Main Hall -->
      <h3 class="gallery-subtitle">Main Hall</h3>
      <div class="gallery-grid">
        <div
          v-for="(hall, index) in mainHalls"
          :key="`main-${index}`"
          class="gallery-card"
          @click="showDetails(hall)"
        >
          <div
            class="card-bg"
            :style="{ backgroundImage: `url(${hall.image})` }"
          ></div>
          <div class="overlay"></div>
          <div class="content">
            <h4 class="title">{{ hall.title }}</h4>
            <p class="subtitle">{{ hall.subtitle }}</p>
          </div>
        </div>
      </div>

      <!-- Outdoor Spaces -->
      <h3 class="gallery-subtitle">Outdoor Spaces</h3>
      <div class="gallery-grid">
        <div
          v-for="(space, index) in outdoorSpaces"
          :key="`outdoor-${index}`"
          class="gallery-card"
          @click="showDetails(space)"
        >
          <div
            class="card-bg"
            :style="{ backgroundImage: `url(${space.image})` }"
          ></div>
          <div class="overlay"></div>
          <div class="content">
            <h4 class="title">{{ space.title }}</h4>
            <p class="subtitle">{{ space.subtitle }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const mainHalls = [
  {
    title: "Grand Chandelier Hall",
    subtitle: "Timeless elegance with dramatic ceilings",
    image: "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&w=1200&q=80"
  },
  {
    title: "Royal Ballroom",
    subtitle: "Spacious & majestic for large celebrations",
    image: "https://images.unsplash.com/photo-1502672023488-70e25813eb80?auto=format&fit=crop&w=1200&q=80"
  },
  {
    title: "Crystal Ballroom",
    subtitle: "Sophisticated lighting & refined details",
    image: "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?auto=format&fit=crop&w=1200&q=80"
  },
  {
    title: "Classic Banquet Hall",
    subtitle: "Warm ambiance & versatile layout",
    image: "https://images.unsplash.com/photo-1529635572221-2d88b4f797d9?auto=format&fit=crop&w=1200&q=80"
  }
]

const outdoorSpaces = [
  {
    title: "Garden Terrace",
    subtitle: "Romantic open-air setting with city views",
    image: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80"
  },
  {
    title: "Lawn Pavilion",
    subtitle: "Perfect for ceremonies & cocktail hours",
    image: "https://images.unsplash.com/photo-1562183241-b937e1de65e4?auto=format&fit=crop&w=1200&q=80"
  },
  {
    title: "Courtyard Fountain",
    subtitle: "Intimate & serene outdoor space",
    image: "https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&w=1200&q=80"
  },
  {
    title: "Rooftop Lounge",
    subtitle: "Stunning sunset views & modern vibe",
    image: "https://images.unsplash.com/photo-1519167758481-83f269a2a4a0?auto=format&fit=crop&w=1200&q=80"
  }
]

const showDetails = (item) => {
  // You can open modal, go to detail page, etc.
  console.log('Selected:', item.title)
  // Example: this.$router.push(`/gallery/${item.title.toLowerCase().replace(/\s+/g, '-')}`)
}
</script>

<style scoped>
.gallery-section {
  padding: clamp(4.5rem, 9vw, 8rem) 0;
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
  margin-bottom: clamp(3rem, 7vw, 5rem);
  letter-spacing: -0.02em;
}

.gallery-subtitle {
  font-family: var(--font-secondary);
  font-size: clamp(1.8rem, 4.5vw, 2.4rem);
  color: #0a1f44;
  margin: 0 0 2.2rem;
  font-weight: 600;
  text-align: center;
  margin-top: 100px;
}

/* ─── GRID ─── */
.gallery-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.6rem;

  @media (min-width: 640px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }

  @media (min-width: 1280px) {
    grid-template-columns: repeat(4, 1fr);
  }
}

.gallery-card {
  position: relative;
  aspect-ratio: 4 / 3;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(10, 31, 68, 0.08);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.gallery-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow: 0 20px 40px rgba(10, 31, 68, 0.14);
}

.card-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transition: transform 0.6s ease;
}

.gallery-card:hover .card-bg {
  transform: scale(1.08);
}

.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.72) 100%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.gallery-card:hover .overlay {
  opacity: 1;
}

.content {
  position: absolute;
  inset: 0;
  padding: 1.8rem;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  z-index: 2;
  color: white;
}

.title {
  font-family: var(--font-secondary);
  font-size: clamp(1.3rem, 2.8vw, 1.65rem);
  font-weight: 600;
  margin: 0 0 0.5rem;
  transform: translateY(10px);
  transition: transform 0.4s ease;
}

.subtitle {
  font-size: clamp(0.95rem, 2vw, 1.08rem);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease 0.1s;
}

.gallery-card:hover .title {
  transform: translateY(0);
}

.gallery-card:hover .subtitle {
  opacity: 0.95;
  transform: translateY(0);
}

/* Mobile fine-tuning */
@media (max-width: 640px) {
  .gallery-subtitle {
    text-align: center;
    margin-bottom: 1.5rem;
  }
}
</style>