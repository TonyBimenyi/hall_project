<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside :class="['sidebar', { 'is-collapsed': isCollapsed, 'is-mobile-open': isMobile && isMobileSidebarOpen }]">
      <div class="sidebar-header">
 

        <div class="title" v-if="!isCollapsed">
          <span class="name"><img src="../../../Belta2.png" alt="LaBertha Villa"></span>

        </div>
      </div>

      <nav class="menu">
        <NuxtLink
          v-for="item in navigation"
          :key="item.title"
          :to="item.url"
          class="menu-item"
          :class="{ active: isActive(item.url) }"
          @click="handleNavClick"
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
      v-if="isMobileSidebarOpen && isMobile"
      class="mobile-overlay"
      @click="closeMobileSidebar"
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
      isMobileSidebarOpen: false,
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
      this.isMobileSidebarOpen = false
      if (this.isMobile) this.isCollapsed = false

      window.addEventListener('resize', this.handleResize)
      document.addEventListener('click', this.handleOutsideClick)
    }

    this.fetchMe()
  },

  beforeUnmount() {
    if (process.client) {
      window.removeEventListener('resize', this.handleResize)
      document.body.style.overflow = ''
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
      if (this.isMobile) {
        this.isMobileSidebarOpen = !this.isMobileSidebarOpen
        document.body.style.overflow = this.isMobileSidebarOpen ? 'hidden' : ''
        return
      }

      this.isCollapsed = !this.isCollapsed
    },

    closeMobileSidebar() {
      if (!this.isMobile) return
      this.isMobileSidebarOpen = false
      document.body.style.overflow = ''
    },

    handleNavClick() {
      if (!this.isMobile) return
      this.closeMobileSidebar()
    },

    isActive(url) {
      if (url === '/admin') {
        return this.$route.path === '/admin'
      }
      return this.$route.path.startsWith(url)
    },

    handleResize() {
      const nextIsMobile = window.innerWidth <= 992

      if (nextIsMobile !== this.isMobile) {
        this.isMobile = nextIsMobile
        this.isMobileSidebarOpen = false
        document.body.style.overflow = ''
        if (this.isMobile) this.isCollapsed = false
      } else {
        this.isMobile = nextIsMobile
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
  overflow: hidden;
}

.sidebar.is-collapsed {
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
.title .name img{
  height: 82px;
  background-color: #fbfbf7;
  border-radius: 10px;
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
  overflow-y: auto;
  min-height: 0;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
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
    top: 0;
    left: 0;
    transform: translateX(-100%);
    transition: transform .25s ease;
    box-shadow: 0 18px 40px rgba(2, 6, 23, 0.35);
    overflow: hidden;
  }
  
  .sidebar.is-collapsed {
    width: 280px;
  }

  .sidebar.is-mobile-open {
    transform: translateX(0);
  }

  .sidebar-header {
    flex: 0 0 auto;
  }

  .menu {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }

  .header {
    height: 64px;
    padding: 0 var(--space-4);
    gap: var(--space-3);
  }

  .page-title {
    font-size: 1rem;
    max-width: 48vw;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .user-profile {
    padding: var(--space-1) var(--space-2);
  }

  .user-info {
    display: none;
  }

  .content {
    padding: var(--space-4);
  }

  .content :deep(.table-container) {
    width: 100%;
  }

  .content :deep(.admin-table) {
    display: block;
    width: 100%;
    overflow-x: auto;
  }

  .content :deep(.admin-table th),
  .content :deep(.admin-table td) {
    padding: 0.85rem 0.95rem;
  }

  .content :deep(.filters-group),
  .content :deep(.filters),
  .content :deep(.header-actions) {
    flex-wrap: wrap;
    gap: var(--space-3);
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
