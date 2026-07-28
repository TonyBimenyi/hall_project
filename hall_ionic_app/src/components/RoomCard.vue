<template>
  <div class="room-card" :class="[`status-${room.status || 'available'}`]">
    <div class="room-card-top">
      <div class="room-card-main">
        <div class="room-card-number">{{ room.room_number || room.code || (isHall ? 'SAL' : '—') }}</div>
        <div class="room-card-name">{{ room.name || (isHall ? 'Salle' : 'Chambre') }}</div>
      </div>
      <div :class="['room-card-status', `status-${room.status || 'available'}`]">
        {{ statusLabel }}
      </div>
    </div>

    <div class="room-card-divider" aria-hidden="true"></div>

    <div class="room-card-meta">
      <div class="room-card-meta-row">
        <Icon icon="solar:bed-linear" class="room-card-meta-icon" />
        <span>{{ typeLabel }} • {{ capacityLabel }}</span>
      </div>
      <div class="room-card-meta-row">
        <Icon icon="solar:tag-price-linear" class="room-card-meta-icon" />
        <span><strong>{{ priceLabel }}</strong> / {{ isHall ? 'événement' : 'nuit' }}</span>
      </div>
    </div>

    <div v-if="room.additional_services?.length || room.amenities?.length" class="room-card-services">
      <div class="room-card-services-label">Services inclus</div>
      <div class="room-card-services-pills">
        <span v-for="(svc, idx) in servicePreview" :key="idx" class="room-card-pill">
          {{ svc }}
        </span>
        <span v-if="overflowServices > 0" class="room-card-pill ghost">
          +{{ overflowServices }}
        </span>
      </div>
    </div>

    <div class="room-card-actions">
      <button type="button" class="action-btn view" @click.stop="$emit('view', room)">
        <Icon icon="solar:eye-linear" class="action-ic" />
        <span>Voir</span>
      </button>
      <button type="button" class="action-btn edit" @click.stop="$emit('edit', room)">
        <Icon icon="solar:pen-2-linear" class="action-ic" />
        <span>Modifier</span>
      </button>
      <button type="button" class="action-btn del" @click.stop="confirmDelete">
        <Icon icon="solar:trash-bin-minimalistic-linear" class="action-ic" />
        <span>Supprimer</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RoomCard',
  props: {
    room: { type: Object, required: true }
  },
  emits: ['view', 'edit', 'delete'],
  data() {
    return {
      typeLabels: {
        single: 'Simple',
        double: 'Double',
        twin: 'Twin',
        suite: 'Suite',
        family: 'Familiale',
        hall: 'Salle',
        conference: 'Conférence',
        event: 'Événement'
      },
      statusLabels: {
        available: 'Disponible',
        reserved: 'Réservée',
        occupied: 'Occupée',
        cleaning: 'Nettoyage',
        maintenance: 'Maintenance'
      }
    }
  },
  computed: {
    isHall() {
      const t = String(this.room.room_type || this.room.type || '').toLowerCase()
      if (this.room.is_hall === true) return true
      return t === 'hall' || t === 'conference' || t === 'event' || t === 'salle'
    },
    typeLabel() {
      if (this.isHall && !this.typeLabels[this.room.room_type]) {
        return this.room.capacity > 50 ? 'Grande salle' : 'Salle'
      }
      return this.typeLabels[this.room.room_type] || this.room.room_type || (this.isHall ? 'Salle' : 'Standard')
    },
    statusLabel() {
      const s = this.room.status
      if (this.isHall && s === 'available') return 'Disponible'
      return this.statusLabels[s] || s || 'Disponible'
    },
    capacityLabel() {
      const cap = Number(this.room.capacity || 0)
      if (!cap) return '—'
      return this.isHall ? `${cap} pers. max` : `${cap} pers.`
    },
    priceLabel() {
      const n = Number(this.room.price_per_night || this.room.price || 0)
      try {
        return n.toLocaleString('fr-FR') + ' Fbu'
      } catch (_) {
        return `${n.toFixed(0)} Fbu`
      }
    },
    serviceList() {
      const a = Array.isArray(this.room.additional_services) ? this.room.additional_services : []
      const b = Array.isArray(this.room.amenities) ? this.room.amenities : []
      return [...a, ...b]
    },
    servicePreview() {
      return this.serviceList.slice(0, 3).map((s) => s?.name || s || '').filter(Boolean)
    },
    overflowServices() {
      return Math.max(0, this.serviceList.length - 3)
    }
  },
  methods: {
    confirmDelete() {
      const ok = window.confirm(`Supprimer ${this.room.name || 'cette salle/chambre'} ?`)
      if (ok) this.$emit('delete', this.room)
    }
  }
}
</script>

<style scoped>
.room-card {
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  border-radius: 24px;
  padding: 18px 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow:
    0 14px 34px rgba(23, 11, 2, 0.05),
    inset 0 1px 0 rgba(255,255,255,0.9);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  position: relative;
  overflow: hidden;
}

.room-card:active {
  transform: translateY(-1px);
  border-color: rgba(215, 111, 2, 0.2);
  box-shadow:
    0 20px 42px rgba(23, 11, 2, 0.08),
    inset 0 1px 0 rgba(255,255,255,0.9);
}

.room-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.room-card-main {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.room-card-number {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.86rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #ffffff;
  background: linear-gradient(135deg, #1a3a7a, #1e4489);
  padding: 5px 11px;
  border-radius: 11px;
  box-shadow: 0 4px 12px rgba(26,58,122,0.22);
}

.room-card-name {
  color: #170b02;
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.01em;
}

.room-card-status {
  padding: 5px 11px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.03em;
  white-space: nowrap;
  border: 1px solid transparent;
}

.room-card-status.status-available {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
  border-color: rgba(16, 185, 129, 0.2);
}

.room-card-status.status-reserved {
  background: rgba(37, 99, 235, 0.12);
  color: #1d4ed8;
  border-color: rgba(37, 99, 235, 0.2);
}

.room-card-status.status-occupied {
  background: rgba(23, 11, 2, 0.12);
  color: #170b02;
  border-color: rgba(23, 11, 2, 0.2);
}

.room-card-status.status-cleaning {
  background: rgba(212, 175, 55, 0.18);
  color: #a16207;
  border-color: rgba(212, 175, 55, 0.26);
}

.room-card-status.status-maintenance {
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
  border-color: rgba(239, 68, 68, 0.2);
}

.room-card-divider {
  height: 1px;
  background: rgba(23, 11, 2, 0.08);
}

.room-card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.85rem;
  color: #475569;
  font-weight: 500;
}

.room-card-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.room-card-meta-row strong {
  color: #170b02;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.room-card-meta-icon {
  color: #d76f02;
  font-size: 1rem;
}

.room-card-services {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.room-card-services-label {
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #94a3b8;
  font-weight: 800;
}

.room-card-services-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.room-card-pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.74rem;
  font-weight: 700;
  background: rgba(215, 111, 2, 0.07);
  color: #d76f02;
  border: 1px solid rgba(215, 111, 2, 0.12);
}

.room-card-pill.ghost {
  background: rgba(100, 116, 139, 0.08);
  color: #64748b;
  border-color: rgba(100, 116, 139, 0.15);
}

.room-card-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding-top: 12px;
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
.action-btn .action-ic { font-size: 1rem; }

.action-btn.view {
  color: #1a3a7a;
  background: rgba(26, 58, 122, 0.08);
  border-color: rgba(26, 58, 122, 0.16);
}
.action-btn.edit {
  color: #d76f02;
  background: rgba(215, 111, 2, 0.08);
  border-color: rgba(215, 111, 2, 0.2);
}
.action-btn.del {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.06);
  border-color: rgba(239, 68, 68, 0.18);
}
</style>
