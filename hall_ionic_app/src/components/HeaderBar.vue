<template>
  <ion-header :translucent="translucent" class="app-header" :class="modifierClass">
    <ion-toolbar class="app-toolbar">
      <ion-buttons :slot="'start'">
        <ion-button v-if="showMenu" :fill="'clear'" class="header-menu-btn" @click="openMenu">
          <Icon icon="solar:hamburger-menu-linear" class="header-icon" />
        </ion-button>
        <ion-button v-if="showBack" :fill="'clear'" class="header-back-btn" @click="goBack">
          <Icon icon="solar:arrow-left-linear" class="header-icon" />
        </ion-button>
      </ion-buttons>

      <ion-title class="app-header-title">
        <div v-if="title" class="app-header-title-text">
          <small v-if="eyebrow" class="app-header-eyebrow">{{ eyebrow }}</small>
          <span>{{ title }}</span>
        </div>
        <slot name="title" v-else />
      </ion-title>

      <ion-buttons :slot="'end'" class="header-end-buttons">
        <slot name="actions" />
      </ion-buttons>
    </ion-toolbar>
    <div v-if="showDivider" class="app-header-divider" aria-hidden="true"></div>
  </ion-header>
</template>

<script>
import {
  IonButton,
  IonButtons,
  IonHeader,
  IonTitle,
  IonToolbar
} from '@ionic/vue'

export default {
  name: 'HeaderBar',
  components: {
    IonButton,
    IonButtons,
    IonHeader,
    IonTitle,
    IonToolbar
  },
  props: {
    title: { type: String, default: '' },
    eyebrow: { type: String, default: '' },
    showMenu: { type: Boolean, default: true },
    showBack: { type: Boolean, default: false },
    backHref: { type: String, default: '/' },
    translucent: { type: Boolean, default: false },
    showDivider: { type: Boolean, default: true },
    variant: { type: String, default: 'default' }
  },
  data() {
    return {}
  },
  computed: {
    modifierClass() {
      return `app-header-${this.variant || 'default'}`
    }
  },
  methods: {
    openMenu() {
      this.$emit('openMenu')
    },
    goBack() {
      this.$router.push(this.backHref)
    }
  }
}
</script>

<style scoped>
.app-header {
  --background: rgba(255, 255, 255, 0.88);
}

.app-toolbar {
  --min-height: 60px;
  --padding-start: 12px;
  --padding-end: 12px;
  --padding-top: 8px;
  --padding-bottom: 8px;
  --background: transparent;
  --border-width: 0;
  --color: #170b02;
}

.app-header-title {
  text-align: center;
}

:deep(.app-header-title) {
  font-size: 1.02rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  color: #170b02;
}

.app-header-title-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.app-header-eyebrow {
  display: block;
  font-size: 0.65rem;
  letter-spacing: 0.16em;
  color: #64748b;
  text-transform: uppercase;
  font-weight: 600;
}

.header-menu-btn,
.header-back-btn {
  --background-hover: rgba(23, 11, 2, 0.06);
  --background-activated: rgba(23, 11, 2, 0.12);
  --border-radius: 14px;
  --color: #170b02;
  height: 40px;
}

.header-icon {
  color: #170b02;
  font-size: 1.35rem;
}

.app-header-divider {
  height: 1px;
  margin: 0 18px;
  background: rgba(23, 11, 2, 0.08);
  opacity: 0.9;
}
</style>
