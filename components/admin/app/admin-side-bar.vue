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
        <div v-if="!isCollapsed" class="menu-caption">Navigation</div>
        <NuxtLink
          v-for="item in filteredNavigation"
          :key="item.title"
          :to="item.url"
          class="menu-item"
          :class="{ active: isActive(item.url) }"
          @click="handleNavClick"
        >
          <i :class="item.icon"></i>
          <span v-if="!isCollapsed" class="menu-item-label">{{ item.title }}</span>
          <span v-if="!isCollapsed && isActive(item.url)" class="menu-item-arrow">
            <i class="fas fa-arrow-right"></i>
          </span>
        </NuxtLink>
      </nav>

      <div v-if="!isCollapsed" class="sidebar-footer">
        <div class="sidebar-footer-label">Connecté en tant que</div>
        <div class="sidebar-footer-name">{{ currentUserName }}</div>
        <div class="sidebar-footer-role">{{ currentUserRole }}</div>
      </div>
    </aside>

    <!-- Main -->
    <div class="main">
      <header class="header">
        <div class="header-left">
          <button class="menu-btn" @click="toggleSidebar">
            <i class="fa-solid fa-bars"></i>
          </button>

          <div class="page-heading">
            <span class="page-eyebrow">Admin Space</span>
            <h1 class="page-title">
              {{ currentPageTitle }}
            </h1>
          </div>
        </div>

        <div class="header-right">
          <div class="topbar-chip" v-if="!isMobile">
            <i class="fas fa-shield-halved"></i>
            <span>{{ currentUserRole }}</span>
          </div>

          <!-- Notifications Bell -->
          <NotificationBell />

          <button
            class="theme-switch"
            type="button"
            role="switch"
            :aria-checked="adminTheme === 'dark'"
            :title="adminTheme === 'dark' ? 'Mode clair' : 'Mode sombre'"
            @click="toggleTheme"
          >
            <span class="theme-switch-track">
              <span class="theme-switch-icon theme-switch-icon--moon">
                <i class="fas fa-moon"></i>
              </span>
              <span class="theme-switch-icon theme-switch-icon--sun">
                <i class="fas fa-sun"></i>
              </span>
              <span class="theme-switch-thumb"></span>
            </span>
          </button>

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
              <span class="user-role">{{ currentUserRole }}</span>
            </div>

            <!-- Dropdown -->
            <div v-if="showProfileMenu" class="profile-dropdown">
              <button class="dropdown-item" @click="goToProfile">
                <i class="fas fa-user-circle"></i>
                Mon profil
              </button>
              <button class="dropdown-item logout" @click="logout">
                <i class="fas fa-sign-out-alt"></i>
                Déconnexion
              </button>
            </div>
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
import NotificationBell from '~/components/admin/NotificationBell.vue'
import { filterNavigationByRole, getRoleLabel } from '~/composables/useRoleAccess'
import { getAdminTheme, toggleAdminTheme } from '~/composables/useAdminTheme'

export default {
  components: {
    NotificationBell
  },
  data() {
    return {
      isCollapsed: false,
      isMobile: false,
      isMobileSidebarOpen: false,
      showProfileMenu: false,
      adminTheme: 'light',

      currentUser: {},

      navigation: [
        { title: 'Tableau de bord', url: '/admin', icon: 'fa-solid fa-house' },
        { title: 'Calendrier', url: '/admin/calendar', icon: 'fa-solid fa-calendar-alt' },
        { title: 'Notifications', url: '/admin/notifications', icon: 'fa-solid fa-bell' },
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
    filteredNavigation() {
      return filterNavigationByRole(this.navigation, this.currentUser)
    },

    currentPageTitle() {
      if (this.$route.path === '/admin/profile') return 'Mon profil'
      const item = this.filteredNavigation.find(i =>
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

    currentUserRole() {
      return getRoleLabel(this.currentUser)
    },

    userInitials() {
      const first = this.currentUser?.first_name?.[0] || ''
      const last = this.currentUser?.last_name?.[0] || ''

      return (first + last).toUpperCase() || 'U'
    }
  },

  mounted() {
    if (process.client) {
      this.adminTheme = getAdminTheme()
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
        if (process.client) {
          localStorage.setItem('user', JSON.stringify(res.data))
        }
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

    goToProfile() {
      this.$router.push('/admin/profile')
      this.showProfileMenu = false
    },

    logout() {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      this.$router.push('/login')
      this.showProfileMenu = false
    },

    toggleTheme() {
      this.adminTheme = toggleAdminTheme()
    }
  }
}
</script>
<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background: var(--gray-50);
}

/* Sidebar */
.sidebar {
  width: 280px;
  background:
    radial-gradient(circle at top left, rgba(212, 175, 55, 0.16), transparent 28%),
    linear-gradient(180deg, #081225 0%, #0f172a 52%, #111c31 100%);
  color: #ffffff;
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

.sidebar.is-collapsed .sidebar-header {
  justify-content: center;
  padding: var(--space-6) var(--space-2);
}

.sidebar.is-collapsed .sidebar-footer,
.sidebar.is-collapsed .menu-caption,
.sidebar.is-collapsed .menu-item-arrow {
  display: none !important;
}

.sidebar.is-collapsed .title,
.sidebar.is-collapsed .title .name,
.sidebar.is-collapsed .title .name img,
.sidebar.is-collapsed .title .sub {
  display: none !important;
}

.sidebar-header {
  padding: var(--space-7) var(--space-6) var(--space-5);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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
  color: #ffffff;
}
.title .name img{
  height: 82px;
  background-color: #fbfbf7;
  border-radius: 10px;
  display: block;
  max-width: 100%;
}

.title .sub {
  font-size: 0.7rem;
  opacity: 0.68;
  text-transform: uppercase;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.menu {
  flex: 1;
  padding: var(--space-5) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  min-height: 0;
  -webkit-overflow-scrolling: touch;
  overscroll-behavior: contain;
}

.menu-caption {
  padding: 0 var(--space-3) var(--space-3);
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(226, 232, 240, 0.5);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: 0.9rem 1rem;
  border-radius: 16px;
  color: #94a3b8;
  font-weight: 700;
  transition: var(--transition-fast);
  position: relative;
}

.menu-item i {
  width: 20px;
  font-size: 1rem;
  text-align: center;
}

.menu-item-label {
  flex: 1;
}

.menu-item-arrow {
  opacity: 0.72;
  font-size: 0.75rem;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #ffffff;
  transform: translateX(2px);
}

.menu-item.active {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.96), rgba(192, 143, 17, 0.96));
  color: #0f172a;
  font-weight: 700;
  box-shadow: 0 14px 26px rgba(212, 175, 55, 0.24);
}

.menu-item.active .menu-item-arrow {
  opacity: 1;
}

.sidebar-footer {
  margin: var(--space-4);
  padding: var(--space-4);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
}

.sidebar-footer-label {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(226, 232, 240, 0.56);
}

.sidebar-footer-name {
  margin-top: 8px;
  font-weight: 800;
  color: #ffffff;
}

.sidebar-footer-role {
  margin-top: 4px;
  font-size: 0.82rem;
  color: rgba(226, 232, 240, 0.72);
}

/* Main Area */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  min-height: 82px;
  background: color-mix(in srgb, var(--white) 86%, transparent);
  padding: 0 var(--space-8);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--gray-200);
  z-index: 90;
  position: sticky;
  top: 0;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.header-right {
  margin-left: auto;
}

.menu-btn {
  font-size: 1.25rem;
  color: var(--gray-500);
  width: 44px;
  height: 44px;
  padding: 0;
  border-radius: 14px;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
}

.menu-btn:hover {
  background: var(--gray-50);
  color: var(--primary);
}

.page-heading {
  display: grid;
  gap: 3px;
}

.page-eyebrow {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--gray-400);
}

.page-title {
  font-family: var(--font-sans);
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--gray-800);
  line-height: 1.1;
}

.topbar-chip {
  min-height: 40px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
  color: var(--gray-600);
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  font-size: 0.82rem;
}

.theme-switch {
  margin-right: var(--space-2);
  width: 52px;
  height: 28px;
  padding: 0;
  border-radius: 999px;
  border: none;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.theme-switch-track {
  width: 52px;
  height: 28px;
  border-radius: 999px;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  position: relative;
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
}

.theme-switch-icon {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: var(--gray-500);
  opacity: 0.85;
  pointer-events: none;
}

.theme-switch-icon--moon {
  left: 6px;
}

.theme-switch-icon--sun {
  right: 6px;
}

.theme-switch-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  background: var(--white);
  border: 1px solid var(--gray-200);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.14);
  transition: transform 0.22s ease, border-color 0.22s ease, background-color 0.22s ease;
}

.theme-switch:hover .theme-switch-track {
  border-color: var(--gray-300);
}

.theme-switch:focus-visible .theme-switch-track {
  box-shadow: 0 0 0 4px rgba(212, 175, 55, 0.16), 0 12px 26px rgba(15, 23, 42, 0.10);
  border-color: rgba(212, 175, 55, 0.55);
}

.theme-switch[aria-checked="true"] .theme-switch-track {
  background: rgba(212, 175, 55, 0.22);
  border-color: rgba(212, 175, 55, 0.55);
}

.theme-switch[aria-checked="true"] .theme-switch-thumb {
  transform: translateX(24px);
  border-color: rgba(212, 175, 55, 0.6);
}

html:not([data-admin-theme="dark"]) .theme-switch[aria-checked="true"] .theme-switch-icon--sun {
  color: #92400e;
  opacity: 1;
}

html:not([data-admin-theme="dark"]) .theme-switch[aria-checked="true"] .theme-switch-icon--moon {
  opacity: 0.55;
}

html:not([data-admin-theme="dark"]) .theme-switch[aria-checked="false"] .theme-switch-icon--moon {
  color: #334155;
  opacity: 1;
}

html:not([data-admin-theme="dark"]) .theme-switch[aria-checked="false"] .theme-switch-icon--sun {
  opacity: 0.55;
}

html[data-admin-theme="dark"] .theme-switch {
  background: transparent;
}

html[data-admin-theme="dark"] .theme-switch-thumb {
  box-shadow: 0 12px 26px rgba(0, 0, 0, 0.35);
}

html[data-admin-theme="dark"] .theme-switch-track {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.28);
}

html[data-admin-theme="dark"] .theme-switch:hover .theme-switch-track {
  border-color: rgba(51, 65, 85, 0.95);
}

html[data-admin-theme="dark"] .theme-switch-icon {
  color: rgba(203, 213, 225, 0.85);
}

html[data-admin-theme="dark"] .theme-switch[aria-checked="true"] .theme-switch-icon--sun {
  color: #fde68a;
  opacity: 1;
}

html[data-admin-theme="dark"] .theme-switch[aria-checked="true"] .theme-switch-icon--moon {
  opacity: 0.55;
}

html[data-admin-theme="dark"] .theme-switch[aria-checked="false"] .theme-switch-icon--moon {
  color: #e2e8f0;
  opacity: 1;
}

html[data-admin-theme="dark"] .theme-switch[aria-checked="false"] .theme-switch-icon--sun {
  opacity: 0.55;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 18px;
  border: 1px solid var(--gray-200);
  background: color-mix(in srgb, var(--white) 82%, var(--gray-50));
  transition: var(--transition-fast);
  position: relative;
}

.user-profile:hover {
  background: var(--gray-50);
  border-color: var(--gray-200);
}

.avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.18), rgba(212, 175, 55, 0.34));
  color: #7c5b00;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
  border: 1px solid rgba(212, 175, 55, 0.25);
}

.user-name {
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--gray-600);
}

.user-role {
  display: block;
  font-size: 0.72rem;
  color: var(--gray-400);
  margin-top: 0.15rem;
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
  border: 1px solid var(--gray-200);
}

html[data-admin-theme="dark"] .menu-btn,
html[data-admin-theme="dark"] .topbar-chip,
html[data-admin-theme="dark"] .user-profile {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(30, 41, 59, 0.95);
}

html[data-admin-theme="dark"] .avatar {
  color: #fef3c7;
  border-color: rgba(212, 175, 55, 0.28);
}

.dropdown-item {
  width: 100%;
  text-align: left;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--rounded-lg);
  font-size: 0.85rem;
  color: var(--gray-600);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.dropdown-item:hover {
  background: var(--gray-50);
  color: var(--primary);
}

.dropdown-item.logout {
  color: var(--danger);
  margin-top: var(--space-1);
  border-top: 1px solid var(--gray-100);
  border-radius: 0 0 var(--rounded-lg) var(--rounded-lg);
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-10);
  background-color: var(--gray-50);
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
    min-height: 64px;
    padding: 0 var(--space-4);
    gap: var(--space-3);
  }

  .page-title {
    font-size: 1rem;
    max-width: 52vw;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .page-eyebrow,
  .topbar-chip,
  .sidebar-footer {
    display: none;
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
