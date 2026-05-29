<template>
  <header class="navbar" :class="{ scrolled: isScrolled }">
    <nav class="container">
      <NuxtLink to="/" class="logo">
        <!-- <span class="mark"><img src="../../labertha-logo.png" alt=""></span> -->
         <span class="mark"><img src="../../Belta2.png" alt=""></span> 
        <!-- <span class="name">LaBertha Villa</span> -->
      </NuxtLink>

      <ul class="links desktop-only">
        <li v-for="link in navLinks" :key="link.name">
          <template v-if="link.children">
            <div class="dropdown" :class="{ active: isGroupActive(link) }">
              <div class="dropdown-trigger" tabindex="0">
                <span>{{ link.name }}</span>
                <i class="fas fa-chevron-down"></i>
              </div>
              <div class="dropdown-menu">
                <NuxtLink
                  v-for="child in link.children"
                  :key="child.name"
                  :to="child.to"
                  active-class="active"
                >
                  {{ child.name }}
                </NuxtLink>
              </div>
            </div>
          </template>
          <template v-else>
            <NuxtLink :to="link.to" active-class="active">{{ link.name }}</NuxtLink>
          </template>
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
      <template v-for="link in navLinks" :key="link.name">
        <template v-if="link.children">
          <div class="mobile-group">
            <div class="mobile-group-title">{{ link.name }}</div>
            <NuxtLink
              v-for="child in link.children"
              :key="child.name"
              :to="child.to"
              class="mobile-sub-link"
              @click="isMenuOpen = false"
            >
              {{ child.name }}
            </NuxtLink>
          </div>
        </template>
        <template v-else>
          <NuxtLink :to="link.to" @click="isMenuOpen = false">
            {{ link.name }}
          </NuxtLink>
        </template>
      </template>
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
        { name: 'A Propos', to: '/about' },
        { name: 'Services', to: '/services' },
      
        {
          name: 'Salles',
          children: [
            { name: 'Reserver la salle', to: '/book' },
            { name: 'Gallerie', to: '/gallery' },
            { name: 'Package', to: '/package' }
          ]
        },
        { name: 'Hotel', to: '/hotel' },
        { name: 'Contact', to: '/contact' },
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
    },
    isGroupActive(link) {
      if (!link || !Array.isArray(link.children)) return false
      const current = this.$route?.path || ''
      return link.children.some(child => child.to === current)
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

.mark img {
  width: 122px;
  height:122px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  /* background: #d4af37; */
  color: #0f172a;
  margin-top: 5px;
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
  align-items: center;
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

.dropdown {
  position: relative;
  display: inline-flex;
}

.dropdown-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: .45rem .8rem;
  border-radius: 8px;
  color: #334155;
  font-weight: 600;
  font-size: .92rem;
  cursor: pointer;
  user-select: none;
}

.dropdown.active .dropdown-trigger,
.dropdown-trigger:hover {
  background: rgba(212, 175, 55, .18);
  color: #d4af37;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  min-width: 220px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 14px 35px rgba(15, 23, 42, 0.12);
  padding: 0.45rem;
  display: none;
  z-index: 30;
}

.dropdown-menu::before {
  content: "";
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  height: 10px;
}

.dropdown:hover .dropdown-menu,
.dropdown:focus-within .dropdown-menu {
  display: grid;
  gap: 0.2rem;
}

.dropdown-menu a {
  padding: 0.55rem 0.7rem;
  border-radius: 10px;
  color: #334155;
  font-weight: 700;
  font-size: 0.9rem;
}

.dropdown-menu a:hover,
.dropdown-menu a.active {
  background: #f8fafc;
  color: #0f172a;
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

.mobile-group {
  padding: .55rem .2rem;
  border-bottom: 1px solid #e2e8f0;
}

.mobile-group-title {
  font-weight: 900;
  color: #0f172a;
  margin-bottom: 0.35rem;
}

.mobile-sub-link {
  padding-left: 0.9rem;
  font-weight: 600;
  color: #475569;
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
