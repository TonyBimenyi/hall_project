<template>
  <transition name="toast">
    <div
      v-if="showNotification"
      :class="['notification', notificationType]"
      role="status"
      aria-live="polite"
    >
      <span class="notification__badge"></span>
      <span class="notification__message">{{ notificationMessage }}</span>
    </div>
  </transition>
</template>

<script>
import { showNotification, notificationMessage, notificationType } from '~/composables/useNotification'

export default {
  setup() {
    return { showNotification, notificationMessage, notificationType }
  }
}
</script>

<style scoped>
.notification {
  position: fixed;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  top: 20px;
  right: 20px;
  width: min(360px, calc(100vw - 32px));
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  line-height: 1.45;
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.24);
  backdrop-filter: blur(14px);
  z-index: 9999;
}

.notification__badge {
  flex-shrink: 0;
  width: 10px;
  height: 10px;
  margin-top: 5px;
  border-radius: 999px;
  background: currentColor;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.12);
}

.notification__message {
  flex: 1;
}

.notification.success {
  background: rgba(20, 83, 45, 0.94);
  color: #bbf7d0;
}

.notification.danger {
  background: rgba(127, 29, 29, 0.94);
  color: #fecaca;
}

.notification.warning {
  background: rgba(120, 53, 15, 0.94);
  color: #fde68a;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translate3d(0, -10px, 0) scale(0.98);
}

@media (max-width: 640px) {
  .notification {
    top: 14px;
    right: 14px;
    width: min(100%, calc(100vw - 20px));
    padding: 13px 14px;
    border-radius: 12px;
  }
}
</style>
