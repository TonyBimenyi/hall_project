import { ref } from 'vue'

// make these global so all components share the same state
export const showNotification = ref(false)
export const notificationMessage = ref('')
export const notificationType = ref('success')
let notificationTimeout = null

export function notify(message, type = 'success', duration = 3000) {
  notificationMessage.value = message
  notificationType.value = type
  showNotification.value = true

  if (notificationTimeout) clearTimeout(notificationTimeout)
  notificationTimeout = setTimeout(() => {
    showNotification.value = false
    notificationMessage.value = ''
  }, duration)
}
