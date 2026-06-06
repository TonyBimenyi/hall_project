<template>
  <div class="default-layout">
    <NuxtLoadingIndicator color="#d4af37" :height="3" />
    <AppClientNavBar />
    <section class="main-content">
      <slot />
    </section>
    <Notification />
    <AppClientFooter />
  </div>
</template>

<style scoped>
.default-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.main-content {
  flex: 1;
  margin-top: 0;
  padding-top: 0;
  padding-bottom: 0;
  min-height: auto;
}
</style>
