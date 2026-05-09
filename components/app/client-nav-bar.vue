<template>
  <header class="navbar" :class="{ scrolled: isScrolled }">
    <nav class="container">
      <NuxtLink to="/" class="logo">
        <span class="mark">BR</span>
        <span class="name">Belta Réception</span>
      </NuxtLink>

      <ul class="links desktop-only">
        <li v-for="link in navLinks" :key="link.name">
          <NuxtLink :to="link.to" active-class="active">{{ link.name }}</NuxtLink>
        </li>
      </ul>

      <div class="right desktop-only">
        <NuxtLink v-if="!isLoggedIn" to="/login" class="btn btn-outline btn-sm">Se connecter</NuxtLink>
        <template v-else>
          <NuxtLink to="/dashboard" class="btn btn-outline btn-sm">Tableau de bord</NuxtLink>
          <button class="btn btn-danger btn-sm" @click="logout">Déconnexion</button>
        </template>
      </div>

      <button class="mobile-toggle" @click="isMenuOpen = !isMenuOpen">
        <i :class="isMenuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
      </button>
    </nav>

    <div class="mobile-menu" :class="{ open: isMenuOpen }">
      <NuxtLink v-for="link in navLinks" :key="link.name" :to="link.to" @click="isMenuOpen = false">
        {{ link.name }}
      </NuxtLink>
      <NuxtLink v-if="!isLoggedIn" to="/login" @click="isMenuOpen = false">Se connecter</NuxtLink>
      <NuxtLink v-else to="/dashboard" @click="isMenuOpen = false">Tableau de bord</NuxtLink>
      <button v-if="isLoggedIn" @click="logout">Déconnexion</button>
    </div>
  </header>
</template>

<script>
export default {
  data() {
    return {
      isScrolled: false,
      isMenuOpen: false,
      isLoggedIn: false,
      navLinks: [
        { name: 'Accueil', to: '/' },
        { name: 'À propos', to: '/about' },
        { name: 'Services', to: '/services' },
        { name: 'Galerie', to: '/gallery' },
        { name: 'Réserver', to: '/book' },
        { name: 'Contact', to: '/contact' }
      ]
    }
  },
  mounted() {
    this.handleScroll()
    window.addEventListener('scroll', this.handleScroll)
    this.checkLogin()
  },
  beforeUnmount() {
    window.removeEventListener('scroll', this.handleScroll)
  },
  methods: {
    handleScroll() {
      this.isScrolled = window.scrollY > 14
    },
    checkLogin() {
      this.isLoggedIn = !!localStorage.getItem('user')
    },
    logout() {
      localStorage.removeItem('user')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      this.isLoggedIn = false
      this.isMenuOpen = false
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  height: 72px;
  display: flex;
  align-items: center;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  transition: .25s ease;
}

.navbar.scrolled {
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08);
}

.container {
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: .6rem;
}

.mark {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #d4af37;
  color: #0f172a;
  font-weight: 800;
  font-size: .8rem;
}

.name {
  font-weight: 800;
  color: #0f172a;
}

.links {
  display: flex;
  gap: .2rem;
}

.links a {
  padding: .45rem .8rem;
  border-radius: 8px;
  color: #334155;
  font-weight: 600;
  font-size: .92rem;
}

.links a.active,
.links a:hover {
  background: rgba(212, 175, 55, .18);
  color: #d4af37;
}

.right {
  display: inline-flex;
  align-items: center;
  gap: .45rem;
}

.btn-sm {
  padding: .45rem .75rem;
  font-size: .8rem;
}

.mobile-toggle {
  display: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border-color: #cbd5e1;
  color: #334155;
}

.mobile-menu {
  position: fixed;
  top: 72px;
  left: 0;
  right: 0;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
  display: grid;
  gap: .4rem;
  padding: 0 .9rem;
  max-height: 0;
  overflow: hidden;
  transition: .2s ease;
}

.mobile-menu.open {
  max-height: 360px;
  padding: .9rem;
}

.mobile-menu a,
.mobile-menu button {
  text-align: left;
  padding: .55rem .2rem;
  color: #334155;
  font-weight: 600;
}

@media (max-width: 1024px) {
  .desktop-only {
    display: none;
  }
  .mobile-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
