<template>
  <ClientOnly>
    <NuxtLoadingIndicator color="#d4af37" :height="3" />
    <AdminAppAdminSideBar v-if="allowed">
      <template #default>
        <slot />
        <Notification />
      </template>
    </AdminAppAdminSideBar>
  </ClientOnly>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from '#imports'
import { canAccessAdmin, canAccessAdminRoute, getDefaultAdminRoute, getStoredUser } from '~/composables/useRoleAccess'
import { initAdminTheme, clearAdminTheme } from '~/composables/useAdminTheme'

const allowed = ref(false)
const router = useRouter()
const route = useRoute()

if (process.client) {
  initAdminTheme()
}

const guardAdminRoute = async () => {
  const user = getStoredUser()
  const isLoggedIn = !!localStorage.getItem('access_token') || !!user.id
  const mustChangePassword = !!user.must_change_password

  if (mustChangePassword) {
    await router.replace('/force-password-change')
    allowed.value = false
    return
  }

  if (!canAccessAdmin(user)) {
    await router.replace(isLoggedIn ? '/dashboard' : '/login')
    allowed.value = false
    return
  }

  if (!canAccessAdminRoute(user, route.path)) {
    await router.replace(getDefaultAdminRoute(user))
    allowed.value = false
    return
  }

  allowed.value = true
}

onMounted(() => {
  guardAdminRoute()
})

watch(() => route.path, () => {
  guardAdminRoute()
})

onBeforeUnmount(() => {
  clearAdminTheme()
})
</script>
