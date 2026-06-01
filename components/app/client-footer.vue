<template>
  <footer class="footer">
    <div class="container top">
      <div class="brand">
        <!-- <h3>LaBertha Villa</h3> -->
         <img src="../../labertha-logo.png" alt="">
        <p>
          Hébergement hôtelier et location de salle de réception à Karurama (Cibitoke), dans la nouvelle province de Bujumbura, Burundi.
        </p>
      </div>

      <div class="links">
        <h4>Navigation</h4>
        <NuxtLink to="/">Accueil</NuxtLink>
        <NuxtLink to="/about">A Propos</NuxtLink>
        <NuxtLink to="/services">Services</NuxtLink>
        <NuxtLink to="/book">Reserver la salle</NuxtLink>
        <NuxtLink to="/gallery">Gallerie</NuxtLink>
        <NuxtLink to="/package">Package</NuxtLink>
        <NuxtLink to="/hotel">Hotel</NuxtLink>
      </div>

      <div class="contact">
        <h4>Contact</h4>
        <p><i class="fas fa-phone"></i> +257 66 47 66 43</p>
        <p><i class="fas fa-phone"></i> +257 76 65 39 31</p>
        <p><i class="fas fa-envelope"></i> info@labertha-villa.com</p>
        <p><i class="fas fa-globe"></i> labertha-villa.com</p>
        <p><i class="fas fa-location-dot"></i> Karurama, Cibitoke, Bujumbura, Burundi</p>
        <p><i class="fab fa-facebook"></i> LaBertha Villa</p>
        <p><i class="fab fa-linkedin"></i> LaBertha Villa</p>
      </div>
    </div>

    <div class="container bottom">
      <span>© {{ currentYear }} LaBertha Villa</span>
      <span>Tous droits réservés</span>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'SiteFooter',
  data() {
    return {
      currentYear: new Date().getFullYear()
    }
  },
  methods: {}
}
</script>

<style scoped>
.footer {
  margin-top: 3rem;
  background: var(--primary-dark);
  color: #e2e8f0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1rem;
}

.top {
  padding: 2.2rem 1rem;
  display: grid;
  grid-template-columns: 1.4fr .9fr 1fr;
  gap: 1rem;
}

.brand h3 {
  margin: 0 0 .5rem;
  color: #fff;
}
.brand img{
  height: 102px;
  width: 102px;
}

.brand p {
  margin: 0;
  color: #94a3b8;
  line-height: 1.7;
}

.links,
.contact {
  display: grid;
  gap: .35rem;
  align-content: flex-start;
}

.links h4,
.contact h4 {
  margin: 0 0 .35rem;
  color: #fff;
}

.links a {
  color: #94a3b8;
}

.links a:hover {
  color: #d4af37;
}

.contact p {
  margin: 0;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: .45rem;
}

.bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding: .9rem 1rem;
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: .86rem;
}

@media (max-width: 900px) {
  .top {
    grid-template-columns: 1fr;
  }

  .bottom {
    flex-direction: column;
    gap: .25rem;
    align-items: center;
  }
}

</style>
