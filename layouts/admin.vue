<template>
  <ClientOnly>
    <AdminAppAdminSideBar v-if="allowed">
      <template #default>
        <slot />
        <Notification />
      </template>
    </AdminAppAdminSideBar>
  </ClientOnly>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const allowed = ref(false)
const router = useRouter()

onMounted(() => {
  let user = {}
  try {
    user = JSON.parse(localStorage.getItem('user') || '{}') || {}
  } catch {
    user = {}
  }

  const isAdmin = !!user.is_staff || !!user.is_superuser
  const isLoggedIn = !!localStorage.getItem('access_token') || !!user.id

  if (!isAdmin) {
    router.replace(isLoggedIn ? '/dashboard' : '/login')
    allowed.value = false
    return
  }

  allowed.value = true
})
</script>
