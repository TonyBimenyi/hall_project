<template>
  <div v-if="showNotification" :class="['notification', notificationType]">
    {{ notificationMessage }}
  </div>
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
  justify-content: center;
  bottom: 90px;
  left: 50%;
  width: 90%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 8px;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  z-index: 9999;
  transition: all 0.3s ease;
}

.notification.success { background-color: #22c55e; }   /* green */
.notification.danger { background-color: #ef4444; }    /* red */
.notification.warning { background-color: #f59e0b; }   /* yellow */
</style>
