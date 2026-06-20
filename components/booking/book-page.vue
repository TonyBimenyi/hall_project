<template>
  <section class="booking-section">
    <div class="container">
      <h1 class="page-title">{{ $t('book.page_title') }}</h1>
      <div class="booking-layout">
        <!-- Left: Calendar & Quick Info -->
        <div class="left-panel card">
          <h2 class="panel-title">{{ $t('book.choose_dates') }}</h2>
          <div class="calendar-wrapper">
            <div class="calendar-header">
              <button class="nav-btn prev" @click="prevMonth">{{ $t('book.prev_month') }}</button>
              <div class="month-year" @click="toggleMonthDropdown">
                {{ monthYearLabel }}
              </div>
              <button class="nav-btn next" @click="nextMonth">{{ $t('book.next_month') }}</button>
            </div>
            <transition name="fade">
              <div v-if="showMonthDropdown" class="month-dropdown">
                <div
                  v-for="(month, idx) in monthNames"
                  :key="month"
                  class="month-option"
                  @click="selectMonth(idx)"
                >
                  {{ $t(month) }} {{ viewMonth.getFullYear() }}
                </div>
              </div>
            </transition>
            <div class="weekdays">
              <div v-for="day in weekdays" :key="day" class="weekday">{{ $t(`book.weekdays.${day.toLowerCase()}`) }}</div>
            </div>
            <div class="days-grid">
              <div
                v-for="(cell, idx) in calendarCells"
                :key="idx"
                class="day-cell"
                :class="{
                  'other-month': !cell.currentMonth,
                  'past disabled': isPastDate(cell.date),
                  'reserved disabled': cell.isReserved,
                  'selected-start': isSameDate(cell.date, rangeStart),
                  'selected-end': isSameDate(cell.date, rangeEnd),
                  'in-range': isInRange(cell.date, rangeStart, rangeEnd)
                }"
                @click="!isPastDate(cell.date) && !cell.isReserved && onDayClick(cell.date)"
              >
                <span class="day-number">{{ cell.date.getDate() }}</span>
              </div>
            </div>
            <div class="calendar-legend">
              <div class="legend-item">
                <span class="legend-circle reserved"></span> {{ $t('book.calendar_legend.reserved') }}
              </div>
              <div class="legend-item">
                <span class="legend-circle selected"></span> {{ $t('book.calendar_legend.selected') }}
              </div>
              <div class="legend-item">
                <span class="legend-circle range"></span> {{ $t('book.calendar_legend.in_range') }}
              </div>
            </div>
            <div class="selection-info">
              <button v-if="rangeStart" class="clear-btn" @click="clearRange">
                {{ $t('book.clear_dates') }}
              </button>
              <div class="selected-dates">
                <div><strong>{{ $t('book.from') }}</strong> {{ startDate || $t('book.not_selected') }}</div>
                <div><strong>{{ $t('book.to') }}</strong> {{ endDate || $t('book.not_selected') }}</div>
              </div>
            </div>
          </div>
          <div class="quick-info mt-32">
            <div class="form-group">
              <label>Salle</label>
              <select v-model="hallId" :class="{ 'error-border': fieldErrors.hall }">
                <option v-for="h in halls" :key="h.id" :value="h.id">
                  {{ h.name }}
                </option>
              </select>
              <p v-if="fieldErrors.hall" class="field-error">{{ fieldErrors.hall }}</p>
            </div>
            <div class="form-group">
              <label>{{ $t('book.event_type') }}</label>
              <select v-model="eventType" :class="{ 'error-border': fieldErrors.event_type }">
                <option value="">{{ $t('book.select_event_type') }}</option>
                <option value="mariage">{{ $t('book.event_types.mariage') }}</option>
                <option value="dot">{{ $t('book.event_types.dot') }}</option>
                <option value="conference">{{ $t('book.event_types.conference') }}</option>
                <option value="graduation">{{ $t('book.event_types.graduation') }}</option>
                <option value="autres">{{ $t('book.event_types.autres') }}</option>
              </select>
              <p v-if="fieldErrors.event_type" class="field-error">{{ fieldErrors.event_type }}</p>
            </div>
            <div v-if="hallAdditionalServices.length" class="addons-card">
              <div class="addons-head">
                <strong>Services additionnels</strong>
                <span v-if="addonsTotal > 0" class="addons-total">+ {{ addonsTotal }} Fbu</span>
              </div>
              <div class="addons-list">
                <div v-for="service in hallAdditionalServices" :key="service.name" class="addon-item">
                  <div v-if="!service.has_subservices" class="addon-line">
                    <label class="checkbox-row">
                      <input
                        type="checkbox"
                        :checked="isServiceSelected(service.name)"
                        @change="toggleSimpleService(service)"
                      />
                      <span>{{ service.name }}</span>
                    </label>
                    <strong>{{ Number(service.price || 0).toFixed(2) }} Fbu</strong>
                  </div>
                  <div v-else class="addon-sub-block">
                    <div class="addon-sub-head">
                      <strong>{{ service.name }}</strong>
                      <span class="muted">Sous-services</span>
                    </div>
                    <div class="addon-subs">
                      <label
                        v-for="sub in (service.subservices || [])"
                        :key="`${service.name}-${sub.name}`"
                        class="checkbox-row addon-sub-line"
                      >
                        <input
                          type="checkbox"
                          :checked="isSubserviceSelected(service.name, sub.name)"
                          @change="toggleSubservice(service.name, sub.name)"
                        />
                        <span>{{ sub.name }}</span>
                        <strong>{{ Number(sub.price || 0).toFixed(2) }} Fbu</strong>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="price-display">
              <span class="price-label">{{ $t('book.estimated_total') }}</span>
              <span class="price-value">{{ totalCost }} Fbu</span>
            </div>
          </div>
        </div>

        <!-- Right: Booking Form -->
        <div class="right-panel card">
          <h2 class="panel-title">{{ $t('book.booking_information') }}</h2>
          <div class="form-grid">
            <div class="form-group">
              <label>{{ $t('book.start_date') }}</label>
              <input type="text" :value="startDate" readonly :class="{ 'error-border': fieldErrors.start_date }" />
              <p v-if="fieldErrors.start_date" class="field-error">{{ fieldErrors.start_date }}</p>
            </div>
            <div class="form-group">
              <label>{{ $t('book.end_date') }}</label>
              <input type="text" :value="endDate" readonly :class="{ 'error-border': fieldErrors.end_date }" />
              <p v-if="fieldErrors.end_date" class="field-error">{{ fieldErrors.end_date }}</p>
            </div>
            <div class="form-group">
              <label>{{ $t('book.number_of_guests') }}</label>
              <input
                type="number"
                v-model.number="guestCount"
                min="10"
                :class="{ 'error-border': fieldErrors.guest_count }"
              />
              <p v-if="fieldErrors.guest_count" class="field-error">{{ fieldErrors.guest_count }}</p>
            </div>
            <div class="form-group">
              <label>Prénom</label>
              <input type="text" v-model="firstName" :class="{ 'error-border': fieldErrors.full_name }" />
              <p v-if="fieldErrors.full_name" class="field-error">{{ fieldErrors.full_name }}</p>
            </div>
            <div class="form-group">
              <label>Nom</label>
              <input type="text" v-model="lastName" :class="{ 'error-border': fieldErrors.full_name }" />
              <p v-if="fieldErrors.full_name" class="field-error">{{ fieldErrors.full_name }}</p>
            </div>
            <div class="form-group">
              <label>{{ $t('book.email_address') }}</label>
              <input type="email" v-model="email" :class="{ 'error-border': fieldErrors.email }" />
              <p v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</p>
            </div>
            <div class="form-group">
              <label>{{ $t('book.phone_number') }} <span class="required">*</span></label>
              <input
                type="tel"
                v-model="phone"
                :class="{ 'error-border': fieldErrors.phone }"
              />
              <p v-if="fieldErrors.phone" class="field-error">{{ fieldErrors.phone }}</p>
            </div>
            <div class="form-group full-width">
              <label>{{ $t('book.additional_notes') }}</label>
              <textarea
                v-model="notes"
                rows="4"
                :placeholder="$t('book.notes_placeholder')"
              ></textarea>
              <p v-if="fieldErrors.notes" class="field-error">{{ fieldErrors.notes }}</p>
            </div>
          </div>
          <button
            class="submit-btn"
            @click="submitBooking"
            :disabled="loading || !rangeStart || !rangeEnd"
          >
            <span v-if="loading">
              <span class="spinner"></span> {{ $t('book.processing') }}
            </span>
            <span v-else>{{ $t('book.confirm_booking') }}</span>
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { notify } from '~/composables/useNotification'
import { api } from '~/composables/useApi'

export default {
  data() {
    return {
      viewMonth: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
      weekdays: ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
      monthNames: [
        'months.january','months.february','months.march','months.april','months.may','months.june',
        'months.july','months.august','months.september','months.october','months.november','months.december'
      ],
      showMonthDropdown: false,
      rangeStart: null,
      rangeEnd: null,
      eventType: "",
      guestCount: 100,
      firstName: "",
      lastName: "",
      email: "",
      phone: "",
      notes: "",
      hallPrice: 0,
      hallId: null,
      additional_services_selected: [],
      halls: [],
      fieldErrors: {},
      loading: false,
      reservedDates: [],
    }
  },
  computed: {
    monthYearLabel() {
      return this.viewMonth.toLocaleString(undefined, { month: 'long', year: 'numeric' })
    },
    calendarCells() {
      const first = new Date(this.viewMonth.getFullYear(), this.viewMonth.getMonth(), 1)
      const startDate = new Date(first)
      startDate.setDate(first.getDate() - first.getDay())
      return Array.from({ length: 42 }, (_, i) => {
        const d = new Date(startDate)
        d.setDate(startDate.getDate() + i)
        const formatted = this.formatYMD(d)
        return {
          date: d,
          currentMonth: d.getMonth() === this.viewMonth.getMonth(),
          isReserved: this.reservedDates.includes(formatted)
        }
      })
    },
    startDate() {
      return this.rangeStart ? this.formatYMD(this.rangeStart) : ""
    },
    endDate() {
      return this.rangeEnd ? this.formatYMD(this.rangeEnd) : ""
    },
    selectedHall() {
      return this.halls.find(h => String(h.id) === String(this.hallId)) || null
    },
    hallAdditionalServices() {
      return Array.isArray(this.selectedHall?.additional_services)
        ? this.selectedHall.additional_services
        : []
    },
    addonsTotal() {
      const services = this.hallAdditionalServices
      const selected = Array.isArray(this.additional_services_selected)
        ? this.additional_services_selected
        : []
      if (!services.length || !selected.length) return 0

      const serviceIndex = new Map(services.map(s => [String(s?.name || ''), s]))
      let total = 0
      for (const item of selected) {
        const name = String(item?.name || '')
        const cfg = serviceIndex.get(name)
        if (!cfg) continue
        if (cfg.has_subservices) {
          const subs = Array.isArray(item?.subservices) ? item.subservices : []
          const subIndex = new Map((cfg.subservices || []).map(sub => [String(sub?.name || ''), Number(sub?.price || 0)]))
          for (const sub of subs) {
            total += subIndex.get(String(sub?.name || '')) || 0
          }
        } else {
          total += Number(cfg.price || 0)
        }
      }
      return Math.round(total)
    },
    totalCost() {
      if (!this.rangeStart || !this.rangeEnd) return 0
      const days = (this.rangeEnd - this.rangeStart) / (1000 * 60 * 60 * 24) + 1
      return (days * this.hallPrice + this.addonsTotal).toFixed(2)
    }
  },
  watch: {
    hallId() {
      this.updateHallPrice()
      this.clearRange()
      this.fetchReservedDates()
      this.additional_services_selected = []
    }
  },
  mounted() {
    let user = {}
    try {
      user = JSON.parse(localStorage.getItem('user') || '{}')
    } catch {
      user = {}
    }
    this.firstName = String(user.first_name || '').trim()
    this.lastName = String(user.last_name || '').trim()
    this.email = user.email || ''
    this.fetchHalls()
  },
  methods: {
    async fetchHalls() {
      try {
        const res = await api.get('halls/')
        this.halls = Array.isArray(res.data) ? res.data : []
        if (!this.hallId && this.halls.length) {
          this.hallId = this.halls[0].id
        } else {
          this.updateHallPrice()
          this.fetchReservedDates()
        }
      } catch (err) {
        console.error('Failed to fetch hall', err)
      }
    },
    updateHallPrice() {
      const hall = this.halls.find(h => h.id === this.hallId)
      this.hallPrice = hall ? Number(hall.price_per_day) : 0
    },
    isServiceSelected(serviceName) {
      return (this.additional_services_selected || []).some(
        s => String(s?.name || '') === String(serviceName || '')
      )
    },
    toggleSimpleService(service) {
      const name = String(service?.name || '').trim()
      if (!name) return
      const selected = Array.isArray(this.additional_services_selected)
        ? [...this.additional_services_selected]
        : []
      const idx = selected.findIndex(s => String(s?.name || '') === name)
      if (idx >= 0) selected.splice(idx, 1)
      else selected.push({ name })
      this.additional_services_selected = selected
    },
    isSubserviceSelected(serviceName, subName) {
      const item = (this.additional_services_selected || []).find(
        s => String(s?.name || '') === String(serviceName || '')
      )
      const subs = Array.isArray(item?.subservices) ? item.subservices : []
      return subs.some(sub => String(sub?.name || '') === String(subName || ''))
    },
    toggleSubservice(serviceName, subName) {
      const name = String(serviceName || '').trim()
      const sub = String(subName || '').trim()
      if (!name || !sub) return
      const selected = Array.isArray(this.additional_services_selected)
        ? [...this.additional_services_selected]
        : []
      let item = selected.find(s => String(s?.name || '') === name)
      if (!item) {
        selected.push({ name, subservices: [{ name: sub }] })
        this.additional_services_selected = selected
        return
      }
      const subs = Array.isArray(item.subservices) ? [...item.subservices] : []
      const idx = subs.findIndex(s => String(s?.name || '') === sub)
      if (idx >= 0) subs.splice(idx, 1)
      else subs.push({ name: sub })
      if (subs.length === 0) {
        this.additional_services_selected = selected.filter(
          s => String(s?.name || '') !== name
        )
      } else {
        item.subservices = subs
        this.additional_services_selected = selected
      }
    },
    async submitBooking() {
      this.fieldErrors = {}
      if (!this.rangeStart) this.fieldErrors.start_date = 'Date début requise'
      if (!this.rangeEnd) this.fieldErrors.end_date = 'Date fin requise'
      if (!this.eventType) this.fieldErrors.event_type = "Type d'événement requis"
      if (!this.hallId) this.fieldErrors.hall = 'Salle requise'
      if (!this.firstName || !this.lastName) this.fieldErrors.full_name = 'Nom et prénom requis'
      if (!this.email) this.fieldErrors.email = 'Email requis'
      if (!this.phone) this.fieldErrors.phone = 'Téléphone requis'
      if (Object.keys(this.fieldErrors).length) {
        notify('Veuillez corriger les erreurs du formulaire.', 'danger')
        return
      }
      try {
        this.loading = true
        const response = await api.post('bookings/guest/', {
          hall: this.hallId,
          full_name: `${String(this.firstName || '').trim()} ${String(this.lastName || '').trim()}`.trim(),
          email: this.email,
          phone: this.phone,
          event_type: this.eventType,
          start_date: this.startDate,
          end_date: this.endDate,
          additional_services_selected: this.additional_services_selected,
        })
        notify(response?.data?.message || 'Réservation confirmée. Vérifiez votre email.', 'success')
        this.clearRange()
        this.eventType = ''
        this.guestCount = 100
        this.phone = ''
        this.notes = ''
        this.additional_services_selected = []
      } catch (err) {
        if (err.response && err.response.data) {
          const data = err.response.data
          Object.keys(data).forEach(key => {
            if (Array.isArray(data[key])) {
              const msg = data[key][0]
              if (key === 'hall') {
                this.fieldErrors.hall = msg
                notify(msg, 'danger')
              } else {
                this.fieldErrors[key] = msg
                notify(msg, 'danger')
              }
            } else if (typeof data[key] === 'string') {
              this.fieldErrors[key] = data[key]
              notify(data[key], 'danger')
            }
          })
        } else {
          notify(this.$t('book.booking_failed'), 'danger')
        }
      } finally {
        this.loading = false
        this.fetchReservedDates()
      }
    },
    async fetchReservedDates() {
      try {
        if (!this.hallId) {
          this.reservedDates = []
          return
        }
        const res = await api.get(`bookings/calendar/?hall=${this.hallId}`)
        this.reservedDates = (Array.isArray(res.data) ? res.data : []).flatMap(b => {
          const start = new Date(b.start_date)
          const end = new Date(b.end_date)
          const dates = []
          for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
            dates.push(this.formatYMD(new Date(d)))
          }
          return dates
        })
      } catch (err) {
        console.error('Failed to fetch reserved dates', err)
      }
    },
    prevMonth() { this.viewMonth = new Date(this.viewMonth.getFullYear(), this.viewMonth.getMonth() - 1, 1) },
    nextMonth() { this.viewMonth = new Date(this.viewMonth.getFullYear(), this.viewMonth.getMonth() + 1, 1) },
    toggleMonthDropdown() { this.showMonthDropdown = !this.showMonthDropdown },
    selectMonth(i) { this.viewMonth = new Date(this.viewMonth.getFullYear(), i, 1); this.showMonthDropdown = false },
    onDayClick(d) {
      if (!this.rangeStart || (this.rangeStart && this.rangeEnd)) {
        this.rangeStart = d
        this.rangeEnd = null
      } else if (d >= this.rangeStart) {
        this.rangeEnd = d
      }
    },
    clearRange() { this.rangeStart = this.rangeEnd = null },
    formatYMD(d) {
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    },
    isSameDate(a,b){ return a && b && a.toDateString() === b.toDateString() },
    isInRange(d,s,e){ return s && e && d >= s && d <= e },
    isPastDate(d){ return d < new Date().setHours(0,0,0,0) }
  }
}
</script>

<style scoped>
.booking-section {
  padding: clamp(4.5rem, 9vw, 8rem) 0;
  background: #f8faff;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.page-title {
  font-family: var(--font-secondary);
  font-size: clamp(2.3rem, 6vw, 3.4rem);
  color: #061b49;
  text-align: center;
  margin-bottom: 3.5rem;
}

/* ─── Layout ─── */
.booking-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}

@media (min-width: 992px) {
  .booking-layout {
    grid-template-columns: 5fr 6fr;
    gap: 3rem;
  }
}

.card {
  background: white;
  border-radius: 16px;
  padding: 2.2rem;
  box-shadow: 0 10px 35px rgba(6, 27, 73, 0.07);
  overflow: hidden; /* ← important: prevents children overflow */
}

.panel-title {
  font-family: var(--font-secondary);
  font-size: 1.85rem;
  color: #061b49;
  margin-bottom: 1.8rem;
}

/* Calendar (unchanged) */
.calendar-wrapper {
  background: #ffffff;
  border-radius: 12px;
  padding: 1.4rem;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.04);
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.4rem;
}

.month-year {
  font-weight: 600;
  font-size: 1.18rem;
  color: #061b49;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
}

.month-year:hover {
  background: #f0f5ff;
}

.nav-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--accent-color);
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  transition: background 0.2s;
}

.nav-btn:hover {
  background: #d4a017cc;
}

.month-dropdown {
  position: absolute;
  z-index: 10;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  max-height: 240px;
  overflow-y: auto;
  width: 180px;
}

.month-option {
  padding: 10px 14px;
  cursor: pointer;
}

.month-option:hover {
  background: #f0f7ff;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-size: 0.9rem;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 0.8rem;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

.day-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  transition: all 0.18s;
  font-size: 0.98rem;
  cursor: pointer;
}

.day-cell:hover:not(.past):not(.reserved) {
  background: #f0f7ff;
  transform: scale(1.06);
}

.past, .reserved {
  opacity: 0.45;
  cursor: not-allowed;
}

.reserved {
  background: #fee2e2;
  color: #991b1b;
}

.selected-start, .selected-end {
  background: var(--primary-color) !important;
  color: white !important;
  font-weight: bold;
  box-shadow: 0 0 0 3px rgba(6,27,73,0.15);
}

.in-range {
  background: #eff6ff;
}

.day-number {
  padding: 10px 12px;
  border-radius: 8px;
}

.calendar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem;
  margin: 1.2rem 0;
  font-size: 0.9rem;
  color: #4b5563;
}

.legend-circle {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1px solid #d1d5db;
}

.legend-circle.reserved { background: #fee2e2; }
.legend-circle.selected { background: var(--primary-color); }
.legend-circle.range { background: #dbeafe; }

.selection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.clear-btn {
  background: var(--accent-color);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
}

.selected-dates {
  display: flex;
  gap: 2rem;
  font-size: 0.95rem;
  color: #374151;
}

/* Quick Info & Form – FIXED RESPONSIVE INPUTS */
.quick-info {
  margin-top: 2.2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.4rem;
}

@media (min-width: 480px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.form-group {
  width: 100%;
  max-width: 100%; /* ← prevent overflow */
  box-sizing: border-box;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

/* FIXED: Inputs, selects, textareas now stay inside card */
input,
select,
textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box; /* ← crucial fix */
  padding: 0.85rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: #3751ff;
  box-shadow: 0 0 0 3px rgba(55,81,255,0.1);
}

.error-border {
  border-color: #ef4444 !important;
}

.field-error {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.4rem;
}

/* Price display */
.price-display {
  margin-top: 1.8rem;
  padding: 1.2rem;
  background: #f0f7ff;
  border-radius: 12px;
  text-align: center;
}

.price-label {
  font-size: 1.05rem;
  color: #4b5563;
}

.price-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--primary-color);
  display: block;
  margin-top: 0.4rem;
}

/* Submit button */
.submit-btn {
  width: 100%;
  margin-top: 2rem;
  padding: 1.15rem;
  background: #061b49;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}

.submit-btn:hover:not(:disabled) {
  background: #0a255f;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Spinner */
.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.addons-card {
  margin-top: 1rem;
  border-top: 1px solid #eef2f7;
  padding-top: 1rem;
}

.addons-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}

.addons-total {
  font-weight: 800;
  color: #061b49;
}

.addons-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.addon-item {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 14px;
  padding: 12px 14px;
}

.addon-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.addon-sub-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 10px;
}

.addon-subs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.addon-sub-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.addon-sub-line input {
  margin-right: 10px;
}

.muted {
  color: #64748b;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Responsive – prevent overflow even more aggressively */
@media (max-width: 991px) {
  .booking-layout {
    grid-template-columns: 1fr;
  }

  .card {
    padding: 1.8rem; /* slightly less padding on mobile */
  }

  input, select, textarea {
    font-size: 0.98rem; /* slightly smaller to fit better */
    padding: 0.8rem 0.9rem;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 1rem;
  }

  .page-title {
    font-size: clamp(2rem, 7vw, 2.8rem);
  }

  .form-grid {
    gap: 1.2rem;
  }

  .form-group label {
    font-size: 0.95rem;
  }
}
</style>
