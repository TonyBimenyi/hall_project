<template>
  <header class="navbar" :class="{ scrolled: isScrolled }">
    <nav class="container">
      <NuxtLink :to="localePath('/')" class="logo">
        <span class="mark"><img src="../../Belta2.png" alt="LaBertha Villa"></span>
        <!-- <span class="name">LaBertha Villa</span> -->
      </NuxtLink>

      <ul class="links desktop-only">
        <li v-for="link in navLinks" :key="link.key">
          <template v-if="link.children">
            <div class="dropdown" :class="{ active: isGroupActive(link) }">
              <div class="dropdown-trigger" tabindex="0">
                <span>{{ $t(link.key) }}</span>
                <i class="fas fa-chevron-down"></i>
              </div>
              <div class="dropdown-menu">
                <NuxtLink
                  v-for="child in link.children"
                  :key="child.key"
                  :to="localePath(child.to)"
                  active-class="active"
                >
                  {{ $t(child.key) }}
                </NuxtLink>
              </div>
            </div>
          </template>
          <template v-else>
            <NuxtLink :to="localePath(link.to)" active-class="active">{{ $t(link.key) }}</NuxtLink>
          </template>
        </li>
      </ul>

      <div class="right desktop-only">
        <div class="lang">
          <NuxtLink :to="switchLocalePath('fr')" class="lang-btn" :class="{ active: locale === 'fr' }">FR</NuxtLink>
          <NuxtLink :to="switchLocalePath('en')" class="lang-btn" :class="{ active: locale === 'en' }">EN</NuxtLink>
        </div>

        <NuxtLink v-if="!isLoggedIn" :to="localePath('/login')" class="btn btn-outline btn-sm">{{ $t('nav.signIn') }}</NuxtLink>
        <template v-else>
          <NuxtLink :to="localePath('/dashboard')" class="btn btn-outline btn-sm">{{ $t('nav.dashboard') }}</NuxtLink>
          <button class="btn btn-danger btn-sm" @click="logout">{{ $t('nav.logout') }}</button>
        </template>
      </div>

      <button class="mobile-toggle" @click="isMenuOpen = !isMenuOpen">
        <i :class="isMenuOpen ? 'fas fa-times' : 'fas fa-bars'"></i>
      </button>
    </nav>

    <div class="mobile-menu" :class="{ open: isMenuOpen }">
      <template v-for="link in navLinks" :key="link.key">
        <template v-if="link.children">
          <div class="mobile-group">
            <div class="mobile-group-title">{{ $t(link.key) }}</div>
            <NuxtLink
              v-for="child in link.children"
              :key="child.key"
              :to="localePath(child.to)"
              class="mobile-sub-link"
              @click="isMenuOpen = false"
            >
              {{ $t(child.key) }}
            </NuxtLink>
          </div>
        </template>
        <template v-else>
          <NuxtLink :to="localePath(link.to)" @click="isMenuOpen = false">
            {{ $t(link.key) }}
          </NuxtLink>
        </template>
      </template>
      <div class="mobile-lang">
        <NuxtLink :to="switchLocalePath('fr')" @click="isMenuOpen = false" class="mobile-lang-btn" :class="{ active: locale === 'fr' }">FR</NuxtLink>
        <NuxtLink :to="switchLocalePath('en')" @click="isMenuOpen = false" class="mobile-lang-btn" :class="{ active: locale === 'en' }">EN</NuxtLink>
      </div>
      <NuxtLink v-if="!isLoggedIn" :to="localePath('/login')" @click="isMenuOpen = false">{{ $t('nav.signIn') }}</NuxtLink>
      <NuxtLink v-else :to="localePath('/dashboard')" @click="isMenuOpen = false">{{ $t('nav.dashboard') }}</NuxtLink>
      <button v-if="isLoggedIn" @click="logout">{{ $t('nav.logout') }}</button>
    </div>
  </header>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const localePath = useLocalePath()
const switchLocalePath = useSwitchLocalePath()

const isScrolled = ref(false)
const isMenuOpen = ref(false)
const isLoggedIn = ref(false)

const navLinks = computed(() => [
  { key: 'nav.home', to: '/' },
  { key: 'nav.about', to: '/about' },
  { key: 'nav.services', to: '/services' },
  {
    key: 'nav.rooms',
    children: [
      { key: 'nav.bookRoom', to: '/book' },
      { key: 'nav.gallery', to: '/gallery' },
      { key: 'nav.package', to: '/package' }
    ]
  },
  { key: 'nav.hotel', to: '/hotel' },
  { key: 'nav.contact', to: '/contact' }
])

const handleScroll = () => {
  isScrolled.value = window.scrollY > 14
}

const checkLogin = () => {
  isLoggedIn.value = !!localStorage.getItem('user')
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  isLoggedIn.value = false
  isMenuOpen.value = false
  router.push(localePath('/login'))
}

const isGroupActive = (link) => {
  if (!link || !Array.isArray(link.children)) return false
  const current = route.path || ''
  return link.children.some(child => localePath(child.to) === current)
}

onMounted(() => {
  handleScroll()
  window.addEventListener('scroll', handleScroll)
  checkLogin()
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
})
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

.lang {
  display: inline-flex;
  align-items: center;
  gap: .35rem;
  margin-right: .25rem;
}

.lang-btn {
  padding: .35rem .55rem;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #0f172a;
  font-weight: 800;
  font-size: .75rem;
}

.lang-btn.active {
  background: rgba(212, 175, 55, .18);
  border-color: rgba(212, 175, 55, .35);
  color: #a16207;
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

.mobile-lang {
  display: flex;
  gap: .5rem;
  padding: .6rem .2rem;
  border-top: 1px solid #e2e8f0;
}

.mobile-lang-btn {
  padding: .35rem .55rem;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #0f172a;
  font-weight: 800;
  font-size: .8rem;
}

.mobile-lang-btn.active {
  background: rgba(212, 175, 55, .18);
  border-color: rgba(212, 175, 55, .35);
  color: #a16207;
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
