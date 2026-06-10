<template>
  <div class="table-pagination" :class="{ 'is-disabled': disabled }">
    <span class="table-pagination__range">{{ rangeLabel }}</span>
    <div class="table-pagination__actions">
      <button
        class="table-pagination__btn"
        type="button"
        :disabled="disabled || !canPrev"
        title="Précédent"
        @click="$emit('prev')"
      >
        <i class="fas fa-chevron-left"></i>
      </button>
      <button
        class="table-pagination__btn"
        type="button"
        :disabled="disabled || !canNext"
        title="Suivant"
        @click="$emit('next')"
      >
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  start: { type: Number, default: 0 },
  end: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
  canPrev: { type: Boolean, default: false },
  canNext: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

defineEmits(['prev', 'next'])

const rangeLabel = computed(() => {
  if (props.total <= 0) return '0-0 sur 0'
  return `${props.start}-${props.end} sur ${props.total}`
})
</script>

<style scoped>
.table-pagination {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
  padding: 0.55rem 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 999px;
  background: #f8fafc;
}

.table-pagination.is-disabled {
  opacity: 0.7;
}

.table-pagination__range {
  font-size: 0.9rem;
  font-weight: 700;
  color: #475569;
  white-space: nowrap;
}

.table-pagination__actions {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.table-pagination__btn {
  width: 2rem;
  height: 2rem;
  border: 0;
  border-radius: 999px;
  background: #ffffff;
  color: #0f172a;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
  transition: transform 0.18s ease, background-color 0.18s ease, color 0.18s ease;
}

.table-pagination__btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #0f172a;
  color: #ffffff;
}

.table-pagination__btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
  box-shadow: none;
}

@media (max-width: 768px) {
  .table-pagination {
    width: 100%;
    justify-content: space-between;
    margin-left: 0;
  }
}
</style>
