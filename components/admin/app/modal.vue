<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="modelValue" class="modal-overlay" @click.self="$emit('update:modelValue', false)">
        <Transition name="zoom">
          <div v-if="modelValue" class="modal-content" :style="{ maxWidth: width }">
            <div class="modal-header">
              <h3>{{ title }}</h3>
              <button class="close-btn" @click="$emit('update:modelValue', false)">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <div class="modal-body">
              <slot />
            </div>
            <div v-if="$slots.footer" class="modal-footer">
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  title: String,
  width: {
    type: String,
    default: '500px'
  }
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: var(--space-4);
}

.modal-content {
  background: var(--white);
  width: 100%;
  border-radius: var(--rounded-2xl);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  border: 1px solid var(--gray-200);
}

.modal-header {
  padding: var(--space-6) var(--space-8);
  border-bottom: 1px solid var(--gray-100);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--gray-900);
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-400);
  transition: var(--transition-fast);
}

.close-btn:hover {
  background: var(--gray-100);
  color: var(--danger);
}

.modal-body {
  padding: var(--space-8);
  overflow-y: auto;
}

.modal-footer {
  padding: var(--space-6) var(--space-8);
  border-top: 1px solid var(--gray-100);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-4);
}

/* Animations */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.zoom-enter-active, .zoom-leave-active { transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.zoom-enter-from, .zoom-leave-to { transform: scale(0.9); }
</style>
