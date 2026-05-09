<template>
  <footer class="footer">
    <div class="container top">
      <div class="brand">
        <h3>Belta Réception</h3>
        <p>Espaces élégants et service professionnel pour mariages, conférences et événements privés.</p>
      </div>

      <div class="links">
        <h4>Navigation</h4>
        <NuxtLink to="/">Accueil</NuxtLink>
        <NuxtLink to="/about">À propos</NuxtLink>
        <NuxtLink to="/services">Services</NuxtLink>
        <NuxtLink to="/book">Réserver</NuxtLink>
      </div>

      <div class="contact">
        <h4>Contact</h4>
        <p><i class="fas fa-phone"></i> +25779382580</p>
        <p><i class="fas fa-envelope"></i> contact@belta-reception.bi</p>
        <p><i class="fas fa-location-dot"></i> Cibitoke, Burundi</p>
      </div>
    </div>

    <div class="container bottom">
      <span>© {{ currentYear }} Belta Réception</span>
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
  background: #0f172a;
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
