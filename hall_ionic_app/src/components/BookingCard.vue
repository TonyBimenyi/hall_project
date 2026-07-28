<template>
  <div
    class="booking-card"
    :class="[`status-${booking.status || 'pending'}`, { clickable: clickable }]"
  >
    <div class="booking-card-head">
      <div class="booking-card-head-left">
        <div class="booking-card-code">{{ displayCode }}</div>
        <div class="booking-card-customer">{{ booking.customer_name || 'Client inconnu' }}</div>
      </div>
      <div :class="['booking-card-status', `status-${booking.status || 'pending'}`]">
        {{ statusLabel }}
      </div>
    </div>

    <div class="booking-card-space">{{ bookingTypeLabel }} • {{ bookingItemLabel }}</div>

    <div class="booking-card-dates">
      <Icon icon="solar:calendar-linear" class="booking-card-inline-icon" />
      <span>{{ periodLabel }}</span>
    </div>

    <div class="booking-card-divider" aria-hidden="true"></div>

    <div class="booking-card-foot">
      <div class="booking-card-total">
        <span class="booking-card-total-label">Total</span>
        <strong class="booking-card-total-value">{{ formatMoney(booking.total_price) }}</strong>
      </div>
    </div>

    <div v-if="showActions" class="booking-card-actions">
      <button type="button" class="action-btn view" @click.stop="$emit('view', booking)">
        <Icon icon="solar:eye-linear" class="action-ic" />
        <span>Voir</span>
      </button>
      <button type="button" class="action-btn edit" @click.stop="$emit('edit', booking)">
        <Icon icon="solar:pen-2-linear" class="action-ic" />
        <span>Modifier</span>
      </button>
      <button type="button" class="action-btn del" @click.stop="confirmDelete">
        <Icon icon="solar:trash-bin-minimalistic-linear" class="action-ic" />
        <span>Supprimer</span>
      </button>
    </div>

    <div class="booking-card-ribbon" aria-hidden="true"></div>
  </div>
</template>

<script>
export default {
  name: 'BookingCard',
  props: {
    booking: { type: Object, required: true },
    clickable: { type: Boolean, default: true },
    showActions: { type: Boolean, default: true }
  },
  emits: ['click', 'view', 'edit', 'delete'],
  data() {
    return {
      statusMap: {
        pending: 'En attente',
        confirmed: 'Confirmée',
        paid: 'Payée',
        cancelled: 'Annulée'
      }
    }
  },
  computed: {
    displayCode() {
      return this.booking.code || this.booking.display_id || `#${this.booking.id || ''}`
    },
    statusLabel() {
      return this.statusMap[this.booking.status] || this.booking.status || 'Inconnu'
    },
    bookingTypeLabel() {
      return String(this.booking.booking_type || '') === 'room' ? 'Chambre' : 'Salle'
    },
    bookingItemLabel() {
      if (this.booking.booking_type === 'room') return this.booking.room_display || '-'
      return this.booking.hall_name || '-'
    },
    periodLabel() {
      const start = String(this.booking.start_date || '').slice(0, 10)
      const end = String(this.booking.end_date || '').slice(0, 10)
      if (!start && !end) return 'Période non définie'
      if (start === end) return start
      return `${start} → ${end}`
    }
  },
  methods: {
    formatMoney(raw) {
      const n = Number(raw || 0)
      try {
        return n.toLocaleString('fr-FR') + ' Fbu'
      } catch (_) {
        return `${n.toFixed(0)} Fbu`
      }
    },
    confirmDelete() {
      const ok = window.confirm(`Supprimer la réservation ${this.displayCode} ?`)
      if (ok) this.$emit('delete', this.booking)
    }
  }
}
</script>

<style scoped>
.booking-card {
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 24px;
  padding: 18px 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow:
    0 14px 34px rgba(23, 11, 2, 0.05),
    inset 0 1px 0 rgba(255,255,255,0.9);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
  overflow: hidden;
}

.booking-card.clickable:active {
  transform: translateY(-1px);
  border-color: rgba(215, 111, 2, 0.25);
  box-shadow:
    0 20px 42px rgba(23, 11, 2, 0.08),
    inset 0 1px 0 rgba(255,255,255,0.9);
}

.booking-card-ribbon {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #d76f02;
  opacity: 0.9;
}
.booking-card.status-paid .booking-card-ribbon { background: #10b981; }
.booking-card.status-pending .booking-card-ribbon { background: #f59e0b; }
.booking-card.status-confirmed .booking-card-ribbon { background: #2563eb; }
.booking-card.status-cancelled .booking-card-ribbon { background: #ef4444; }

.booking-card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding-left: 10px;
}

.booking-card-head-left {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.booking-card-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.76rem;
  letter-spacing: 0.14em;
  color: #64748b;
  font-weight: 800;
}

.booking-card-customer {
  color: #170b02;
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.005em;
}

.booking-card-status {
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.booking-card-status.status-pending {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
  border: 1px solid rgba(245, 158, 11, 0.22);
}

.booking-card-status.status-confirmed {
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
  border: 1px solid rgba(37, 99, 235, 0.2);
}

.booking-card-status.status-paid {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.22);
}

.booking-card-status.status-cancelled {
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.booking-card-space {
  color: #475569;
  font-size: 0.84rem;
  font-weight: 600;
  padding-left: 10px;
}

.booking-card-dates {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #334155;
  font-size: 0.86rem;
  font-weight: 500;
  padding-left: 10px;
  padding-top: 2px;
}

.booking-card-inline-icon {
  color: #d76f02;
  font-size: 1rem;
}

.booking-card-divider {
  height: 1px;
  margin: 4px 0 0;
  background: rgba(23, 11, 2, 0.08);
}

.booking-card-foot {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
  padding-left: 10px;
  padding-top: 6px;
}

.booking-card-total {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.booking-card-total-label {
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 800;
}

.booking-card-total-value {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.18rem;
  font-weight: 800;
  letter-spacing: 0.005em;
  color: #170b02;
}

.booking-card-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
  padding: 12px 0 2px 10px;
  border-top: 1px dashed rgba(23,11,2,0.08);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 8px;
  border-radius: 12px;
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid transparent;
  cursor: pointer;
  background: transparent;
  transition: all 0.15s ease;
  letter-spacing: 0.01em;
}
.action-btn .action-ic {
  font-size: 1rem;
}

.action-btn.view {
  color: #1a3a7a;
  background: rgba(26, 58, 122, 0.08);
  border-color: rgba(26, 58, 122, 0.16);
}
.action-btn.view:active { background: rgba(26, 58, 122, 0.14); }

.action-btn.edit {
  color: #d76f02;
  background: rgba(215, 111, 2, 0.08);
  border-color: rgba(215, 111, 2, 0.2);
}
.action-btn.edit:active { background: rgba(215, 111, 2, 0.14); }

.action-btn.del {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.06);
  border-color: rgba(239, 68, 68, 0.18);
}
.action-btn.del:active { background: rgba(239, 68, 68, 0.12); }
</style>
