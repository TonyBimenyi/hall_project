<template>
  <ion-app>
    <ion-tabs class="app-tabs" @ionTabsDidChange="onTabsDidChange">
      <ion-router-outlet id="main-content" />

      <ion-tab-bar slot="bottom" class="app-tab-bar" translucent :class="{ 'tab-bar-hidden': hideTabBar }">
        <ion-tab-button tab="home" href="/" :class="{ active: activePath === '/' }">
          <Icon icon="solar:home-2-linear" class="tab-bar-icon" />
          <ion-label>Accueil</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="bookings" href="/bookings" :class="{ active: activePath.startsWith('/bookings') }">
          <Icon icon="solar:calendar-linear" class="tab-bar-icon" />
          <ion-label>Réservations</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="reports" href="/reports" :class="{ active: activePath === '/reports' }">
          <Icon icon="solar:chart-2-linear" class="tab-bar-icon" />
          <ion-label>Rapports</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="rooms" href="/rooms" :class="{ active: activePath === '/rooms' }">
          <Icon icon="solar:bed-linear" class="tab-bar-icon" />
          <ion-label>Chambres</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="compta" href="/compta" :class="{ active: activePath === '/compta' }">
          <Icon icon="solar:wallet-money-linear" class="tab-bar-icon" />
          <ion-label>Compta</ion-label>
        </ion-tab-button>

        <ion-tab-button tab="profile" href="/profile" :class="{ active: activePath === '/profile' }">
          <Icon icon="solar:user-circle-linear" class="tab-bar-icon" />
          <ion-label>Profil</ion-label>
        </ion-tab-button>
      </ion-tab-bar>
    </ion-tabs>
  </ion-app>
</template>

<script>
import { IonApp, IonLabel, IonRouterOutlet, IonTabBar, IonTabButton, IonTabs } from '@ionic/vue'

export default {
  name: 'App',
  components: {
    IonApp,
    IonLabel,
    IonRouterOutlet,
    IonTabBar,
    IonTabButton,
    IonTabs
  },
  data() {
    return {
      activePath: '/',
      hideTabBar: false
    }
  },
  watch: {
    $route(to) {
      this.activePath = to.path
      this.hideTabBar = to.path === '/login'
    }
  },
  methods: {
    onTabsDidChange(ev) {
      const tab = ev?.detail?.tab
      if (tab === 'home') this.activePath = '/'
      if (tab === 'bookings') this.activePath = '/bookings'
      if (tab === 'reports') this.activePath = '/reports'
      if (tab === 'rooms') this.activePath = '/rooms'
      if (tab === 'compta') this.activePath = '/compta'
      if (tab === 'profile') this.activePath = '/profile'
    }
  },
  mounted() {
    this.activePath = this.$route?.path || '/'
    this.hideTabBar = this.activePath === '/login'
  }
}
</script>

<style>
html, body, #app {
  height: 100%;
  background: #fbf7f2;
}

body {
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: 0.005em;
}

.app-tabs {
  --background: #fbf7f2;
}

ion-tab-bar.app-tab-bar {
  --background: rgba(255, 255, 255, 0.94);
  --border: 1px 0 0 0 rgba(23, 11, 2, 0.07);
  padding-top: 6px;
  padding-bottom: calc(6px + env(safe-area-inset-bottom));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.app-tab-bar::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 1px;
  background: linear-gradient(90deg, rgba(23,11,2,0) 0%, rgba(23,11,2,0.12) 20%, rgba(23,11,2,0.12) 80%, rgba(23,11,2,0) 100%);
}

.tab-bar-icon {
  font-size: 19px;
  width: 21px;
  height: 21px;
  display: block;
  margin: 0 auto;
  color: #64748b;
  transition: color 0.2s ease, transform 0.2s ease;
}

ion-tab-button {
  --color: #64748b;
  --color-checked: var(--app-primary, #d76f02);
  --padding-start: 2px;
  --padding-end: 2px;
  --padding-top: 5px;
  --padding-bottom: 3px;
  font-size: 0.62rem;
  letter-spacing: 0.005em;
  min-width: 0;
  flex: 1 1 0;
}

ion-tab-button .tab-native {
  border-radius: 14px;
}

ion-tab-button.active .tab-bar-icon,
ion-tab-button.tab-selected .tab-bar-icon {
  color: var(--app-primary, #d76f02);
  transform: translateY(-1px) scale(1.03);
}

ion-tab-button.active ion-label,
ion-tab-button.tab-selected ion-label {
  color: var(--app-primary, #d76f02);
  font-weight: 700;
}

.tab-bar-hidden {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

ion-fab-button svg,
ion-fab-button .iconify,
ion-fab-button [data-icon],
ion-fab-button ::slotted(svg) {
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  min-height: 26px !important;
  display: block !important;
}

ion-fab-button.fab-main svg,
ion-fab-button.fab-main .iconify,
ion-fab-button.fab-main [data-icon],
ion-fab-button.fab-main ::slotted(svg) {
  width: 30px !important;
  height: 30px !important;
  min-width: 30px !important;
  min-height: 30px !important;
}
</style>
