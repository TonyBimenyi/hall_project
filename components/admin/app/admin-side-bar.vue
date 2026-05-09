<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside :class="['sidebar', { collapsed: isCollapsed }]">
      <div class="sidebar-header">
        <div class="logo">
          <i class="fa-solid fa-building"></i>
        </div>

        <div class="title" v-if="!isCollapsed">
          <span class="name">Admin Hall</span>
          <span class="sub">Tableau de bord Réception</span>
        </div>
      </div>

      <nav class="menu">
        <NuxtLink
          v-for="item in navigation"
          :key="item.title"
          :to="item.url"
          class="menu-item"
          :class="{ active: isActive(item.url) }"
        >
          <i :class="item.icon"></i>
          <span v-if="!isCollapsed">{{ item.title }}</span>
        </NuxtLink>
      </nav>
    </aside>

    <!-- Main -->
    <div class="main">
      <header class="header">
        <button class="menu-btn" @click="toggleSidebar">
          <i class="fa-solid fa-bars"></i>
        </button>

        <h1 class="page-title">
          {{ currentPageTitle }}
        </h1>

        <!-- USER -->
        <div class="user-profile" @click="showProfileMenu = !showProfileMenu">
          <div class="avatar-wrapper">
            <div class="avatar">
              {{ userInitials }}
            </div>
            <div class="status-dot"></div>
          </div>

          <div class="user-info">
            <span class="user-name">
              {{ currentUserName }}
              <i class="fas fa-chevron-down"></i>
            </span>
          </div>

          <!-- Dropdown -->
          <div v-if="showProfileMenu" class="profile-dropdown">
            <button class="dropdown-item logout" @click="logout">
              <i class="fas fa-sign-out-alt"></i>
              Déconnexion
            </button>
          </div>
        </div>
      </header>

      <main class="content">
        <slot />
      </main>
    </div>

    <!-- Mobile overlay -->
    <div
      v-if="!isCollapsed && isMobile"
      class="mobile-overlay"
      @click="toggleSidebar"
    ></div>
  </div>
</template>

<script>
import { api } from '~/composables/useApi'

export default {
  data() {
    return {
      isCollapsed: false,
      isMobile: false,
      showProfileMenu: false,

      currentUser: {},

      navigation: [
        { title: 'Tableau de bord', url: '/admin', icon: 'fa-solid fa-house' },
        { title: 'Calendrier', url: '/admin/calendar', icon: 'fa-solid fa-calendar-alt' },
        { title: 'Salles', url: '/admin/halls', icon: 'fa-solid fa-building' },
        { title: 'Réservations', url: '/admin/bookings', icon: 'fa-solid fa-calendar-days' },
        { title: 'Paiements', url: '/admin/payments', icon: 'fa-solid fa-credit-card' },
        { title: 'Matériel', url: '/admin/materials', icon: 'fa-solid fa-box-open' },
        { title: 'Dépenses', url: '/admin/expenses', icon: 'fa-solid fa-money-bill-transfer' },
        { title: 'Personnel', url: '/admin/personnel', icon: 'fa-solid fa-users' },
        { title: 'Rapports', url: '/admin/reports', icon: 'fa-solid fa-chart-line' }
      ]
    }
  },

  computed: {
    currentPageTitle() {
      const item = this.navigation.find(i =>
        this.$route.path === i.url ||
        this.$route.path.startsWith(i.url + '/')
      )
      return item ? item.title : 'Tableau de bord'
    },

    currentUserName() {
      if (!this.currentUser) return 'Utilisateur'

      const first = this.currentUser.first_name || ''
      const last = this.currentUser.last_name || ''

      const full = `${first} ${last}`.trim()

      return full || this.currentUser.email || 'Utilisateur'
    },

    userInitials() {
      const first = this.currentUser?.first_name?.[0] || ''
      const last = this.currentUser?.last_name?.[0] || ''

      return (first + last).toUpperCase() || 'U'
    }
  },

  mounted() {
    if (process.client) {
      this.isMobile = window.innerWidth <= 992
      if (this.isMobile) this.isCollapsed = true

      window.addEventListener('resize', this.handleResize)
      document.addEventListener('click', this.handleOutsideClick)
    }

    this.fetchMe()
  },

  beforeDestroy() {
    if (process.client) {
      window.removeEventListener('resize', this.handleResize)
    }
    document.removeEventListener('click', this.handleOutsideClick)
  },

  methods: {
    async fetchMe() {
      try {
        const res = await api.get('me/')
        this.currentUser = res.data
      } catch {
        this.currentUser = {}
      }
    },

    toggleSidebar() {
      this.isCollapsed = !this.isCollapsed
    },

    isActive(url) {
      if (url === '/admin') {
        return this.$route.path === '/admin'
      }
      return this.$route.path.startsWith(url)
    },

    handleResize() {
      this.isMobile = window.innerWidth <= 992
      if (this.isMobile && !this.isCollapsed) {
        this.isCollapsed = true
      }
    },

    handleOutsideClick(e) {
      if (!this.$el.contains(e.target)) {
        this.showProfileMenu = false
      }
    },

    logout() {
      localStorage.removeItem('access_token')
      this.$router.push('/login')
      this.showProfileMenu = false
    }
  }
}
</script>
<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background: #f8fafc; /* Very light gray/blue background */
}

/* Sidebar */
.sidebar {
  width: 280px;
  background: #0f172a; /* Darker, cleaner navy */
  color: var(--white);
  transition: var(--transition-all);
  position: relative;
  z-index: 100;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: var(--space-8) var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.logo {
  width: 40px;
  height: 40px;
  background: var(--accent);
  color: #0f172a;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3);
}

.title .name {
  display: block;
  font-weight: 800;
  font-size: 1.1rem;
  letter-spacing: 0.02em;
  color: var(--white);
}

.title .sub {
  font-size: 0.7rem;
  opacity: 0.5;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.menu {
  flex: 1;
  padding: var(--space-6) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--rounded-lg);
  color: #94a3b8; /* Muted text */
  font-weight: 500;
  transition: var(--transition-fast);
}

.menu-item i {
  width: 20px;
  font-size: 1rem;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.03);
  color: var(--white);
}

.menu-item.active {
  background: var(--accent);
  color: #0f172a;
  font-weight: 700;
  box-shadow: 0 4px 15px rgba(212, 175, 55, 0.2);
}

/* Main Area */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  height: 80px;
  background: var(--white);
  padding: 0 var(--space-10);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e2e8f0;
  z-index: 90;
  position: sticky;
  top: 0;
}

.menu-btn {
  font-size: 1.25rem;
  color: #64748b;
  padding: var(--space-2);
  border-radius: var(--rounded-md);
}

.menu-btn:hover {
  background: var(--gray-50);
  color: var(--primary);
}

.page-title {
  font-family: var(--font-sans); /* Cleaner than serif for admin headers */
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--rounded-full);
  border: 1px solid #f1f5f9;
  transition: var(--transition-fast);
  position: relative;
}

.user-profile:hover {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.avatar {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  color: var(--primary);
  border-radius: var(--rounded-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
  border: none;
}

.user-name {
  font-weight: 600;
  font-size: 0.85rem;
  color: #475569;
}

.profile-dropdown {
  position: absolute;
  top: 120%;
  right: 0;
  background: var(--white);
  width: 220px;
  border-radius: var(--rounded-xl);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
  padding: var(--space-2);
  border: 1px solid #e2e8f0;
}

.dropdown-item {
  width: 100%;
  text-align: left;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--rounded-lg);
  font-size: 0.85rem;
  color: #475569;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dropdown-item:hover {
  background: #f8fafc;
  color: var(--primary);
}

.dropdown-item.logout {
  color: var(--danger);
  margin-top: var(--space-1);
  border-top: 1px solid #f1f5f9;
  border-radius: 0 0 var(--rounded-lg) var(--rounded-lg);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-10);
  background-color: #f8fafc;
}

/* Mobile */
@media (max-width: 992px) {
  .sidebar {
    position: fixed;
    height: 100vh;
    left: -280px;
  }
  
  .sidebar.collapsed {
    left: 0;
    width: 280px;
  }
  
  .mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.5);
    z-index: 95;
    backdrop-filter: blur(4px);
  }
}
</style>
