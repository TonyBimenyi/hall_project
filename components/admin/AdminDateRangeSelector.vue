<template>
  <div class="date-range-selector">
    <div class="calendar-top">
      <strong>{{ calendarMonthLabel }}</strong>
      <div class="calendar-nav">
        <button class="icon-btn" type="button" @click="prevCalendarMonth">
          <i class="fas fa-chevron-left"></i>
        </button>
        <button class="icon-btn" type="button" @click="nextCalendarMonth">
          <i class="fas fa-chevron-right"></i>
        </button>
        <button class="btn btn-outline btn-sm" type="button" @click="clearCalendarDates">
          Effacer
        </button>
      </div>
    </div>
    <div class="weekday-row">
      <span v-for="d in calendarWeekdays" :key="d">{{ d }}</span>
    </div>
    <div class="calendar-grid-admin">
      <button
        v-for="cell in adminCalendarCells"
        :key="cell.key"
        class="day-cell"
        :class="{
          muted: !cell.currentMonth,
          disabled: cell.isPast || (!isEditing && cell.isBooked),
          start: isSameCalendarDate(cell.date, rangeStart),
          end: isSameCalendarDate(cell.date, rangeEnd),
          inrange: isCalendarInRange(cell.date, rangeStart, rangeEnd),
          booked: cell.isBooked
        }"
        :disabled="cell.isPast || (!isEditing && cell.isBooked)"
        type="button"
        @click="onDayClick(cell.date)"
      >
        {{ cell.date.getDate() }}
      </button>
    </div>
    <div class="calendar-legend">
      <span><i class="dot booked"></i> Réservé</span>
      <span><i class="dot selected"></i> Début/Fin</span>
      <span><i class="dot range"></i> Période</span>
    </div>
    <div class="selected-period-card">
      <div class="selected-period-label">Période sélectionnée</div>
      <div class="selected-period-value">{{ selectedPeriodLabel }}</div>
      <div class="selected-period-hint">{{ selectedPeriodHint }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  startDate: { type: String, default: '' },
  endDate: { type: String, default: '' },
  bookedDates: { type: Array, default: () => [] }, // Array of {start_date, end_date}
  isEditing: { type: Boolean, default: false },
  bookingType: { type: String, default: 'room' } // 'room' or 'hall'
})

const emit = defineEmits(['update:startDate', 'update:endDate'])

const calendarViewMonth = ref(new Date())
const calendarWeekdays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

// Sync local view month with props if provided
watch(() => props.startDate, (newVal) => {
  if (newVal) {
    const d = new Date(newVal)
    if (!isNaN(d.getTime())) {
      calendarViewMonth.value = new Date(d.getFullYear(), d.getMonth(), 1)
    }
  }
}, { immediate: true })

const rangeStart = computed(() => props.startDate ? new Date(props.startDate) : null)
const rangeEnd = computed(() => props.endDate ? new Date(props.endDate) : null)

const formatCalendarYMD = (d) => {
  if (!d) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const isSameCalendarDate = (a, b) => !!(a && b && formatCalendarYMD(a) === formatCalendarYMD(b))
const isCalendarInRange = (d, s, e) => !!(s && e && d > s && d < e)

const calendarMonthLabel = computed(() => {
  return calendarViewMonth.value.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
})

const bookedSet = computed(() => {
  const set = new Set()
  for (const r of props.bookedDates) {
    const start = new Date(r.start_date)
    const end = new Date(r.end_date)
    for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
      set.add(formatCalendarYMD(new Date(d)))
    }
  }
  return set
})

const adminCalendarCells = computed(() => {
  const first = new Date(calendarViewMonth.value.getFullYear(), calendarViewMonth.value.getMonth(), 1)
  const firstWeekday = (first.getDay() + 6) % 7
  const start = new Date(first)
  start.setDate(first.getDate() - firstWeekday)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const ymd = formatCalendarYMD(d)
    return {
      key: `${ymd}-${i}`,
      date: d,
      currentMonth: d.getMonth() === calendarViewMonth.value.getMonth(),
      isPast: d < today,
      isBooked: bookedSet.value.has(ymd),
    }
  })
})

const prevCalendarMonth = () => {
  calendarViewMonth.value = new Date(calendarViewMonth.value.getFullYear(), calendarViewMonth.value.getMonth() - 1, 1)
}

const nextCalendarMonth = () => {
  calendarViewMonth.value = new Date(calendarViewMonth.value.getFullYear(), calendarViewMonth.value.getMonth() + 1, 1)
}

const clearCalendarDates = () => {
  emit('update:startDate', '')
  emit('update:endDate', '')
}

const hasCalendarConflict = (start, end) => {
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    if (bookedSet.value.has(formatCalendarYMD(new Date(d)))) return true
  }
  return false
}

const onDayClick = (date) => {
  date.setHours(0, 0, 0, 0)
  
  if (!props.startDate || props.endDate) {
    emit('update:startDate', formatCalendarYMD(date))
    emit('update:endDate', '')
    return
  }

  const start = new Date(props.startDate)
  if (date < start) {
    emit('update:startDate', formatCalendarYMD(date))
    emit('update:endDate', '')
    return
  }

  if (!props.isEditing && hasCalendarConflict(start, date)) {
    // We can emit a warning or handle it outside
    return
  }

  emit('update:endDate', formatCalendarYMD(date))
}

const daysCount = computed(() => {
  if (!props.startDate || !props.endDate) return 0
  const s = new Date(props.startDate)
  const e = new Date(props.endDate)
  const diff = Math.ceil((e - s) / (1000 * 60 * 60 * 24))
  return props.bookingType === 'hall' ? diff + 1 : diff
})

const selectedPeriodLabel = computed(() => {
  if (!props.startDate) return 'Aucune date sélectionnée'
  const s = new Date(props.startDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
  if (!props.endDate) return `Du ${s} (En attente de fin)`
  const e = new Date(props.endDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
  return `Du ${s} au ${e}`
})

const selectedPeriodHint = computed(() => {
  if (!props.startDate || !props.endDate) return 'Veuillez choisir les dates de début et de fin.'
  const count = daysCount.value
  const label = props.bookingType === 'hall' ? 'jour' : 'nuit'
  return `Séjour de ${count} ${label}${count > 1 ? 's' : ''}.`
})
</script>

<style scoped>
.calendar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.calendar-top strong {
  text-transform: capitalize;
  font-size: 1rem;
  font-weight: 800;
  line-height: 1.3;
}

:global(html[data-admin-theme="dark"]) .calendar-top strong {
  color: #f8fafc;
}
.calendar-nav {
  display: flex;
  gap: 8px;
  align-items: center;
}
.icon-btn {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  color: #475569;
}
.icon-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}
.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}
.calendar-grid-admin {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}
.day-cell {
  height: 38px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  font-weight: 800;
  color: var(--gray-600);
  cursor: pointer;
  transition: all 0.2s;
}
.day-cell:hover:not(:disabled) {
  border-color: #d4af37;
  background: rgba(212, 175, 55, 0.05);
}
.day-cell.muted {
  opacity: 0.55;
}
.day-cell.booked {
  background: rgba(220, 38, 38, 0.08);
  border-color: rgba(220, 38, 38, 0.18);
  color: #991b1b;
}
.day-cell.disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.day-cell.start,
.day-cell.end {
  background: rgba(212, 175, 55, 0.18) !important;
  border-color: rgba(212, 175, 55, 0.35) !important;
  color: var(--gray-600) !important;
}
.day-cell.inrange {
  background: rgba(212, 175, 55, 0.12);
  border-color: rgba(212, 175, 55, 0.22);
}
.calendar-legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin-top: 12px;
  color: #64748b;
  font-weight: 700;
  font-size: 0.85rem;
}
.calendar-legend .dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  margin-right: 6px;
  vertical-align: middle;
}
.calendar-legend .dot.booked { background: #dc2626; }
.calendar-legend .dot.selected { background: #d4af37; }
.calendar-legend .dot.range { background: rgba(212, 175, 55, 0.45); }
.selected-period-card {
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid #e2e8f0;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}
.selected-period-label {
  color: #64748b;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.selected-period-value {
  margin-top: 0.35rem;
  color: #0f172a;
  font-size: 1rem;
  font-weight: 800;
}
.selected-period-hint {
  margin-top: 0.35rem;
  color: #64748b;
  font-size: 0.85rem;
  line-height: 1.45;
}
</style>
