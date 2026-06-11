<template>
  <section class="book-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="book-layout">
        <!-- CALENDAR -->
        <article class="card calendar-card">
          <div class="calendar-top">
            <h2>{{ $t('booking.calendar') }}</h2>
            <div class="calendar-nav">
              <button class="icon-btn" @click="prevMonth">
                <i class="fas fa-chevron-left"></i>
              </button>
              <strong>{{ monthLabel }}</strong>
              <button class="icon-btn" @click="nextMonth">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>

          <div class="weekday-row">
            <span v-for="d in weekdays" :key="d">{{ $t(`booking.weekdays.${d}`) }}</span>
          </div>

          <div class="calendar-grid">
            <button
              v-for="cell in calendarCells"
              :key="cell.key"
              class="day-cell"
              :class="{
                muted: !cell.currentMonth,
                disabled: cell.isPast || cell.isBooked,
                start: isSameDate(cell.date, rangeStart),
                end: isSameDate(cell.date, rangeEnd),
                inrange: isInRange(cell.date, rangeStart, rangeEnd),
                booked: cell.isBooked
              }"
              :disabled="cell.isPast || cell.isBooked"
              @click="onDayClick(cell.date)"
            >
              {{ cell.date.getDate() }}
            </button>
          </div>

          <div class="calendar-legend">
            <span><i class="dot booked"></i> {{ $t('booking.booked') }}</span>
            <span><i class="dot selected"></i> {{ $t('booking.selection') }}</span>
            <span><i class="dot range"></i> {{ $t('booking.range') }}</span>
          </div>

          <div class="summary-item">
            <span>{{ $t('booking.start') }}</span>
            <strong>{{ startDate || $t('booking.notSelected') }}</strong>
          </div>

          <div class="summary-item">
            <span>{{ $t('booking.end') }}</span>
            <strong>{{ endDate || startDate || $t('booking.notSelected') }}</strong>
          </div>

          <div class="summary-item controls">
            <button class="btn btn-outline btn-sm" @click="clearDates">
              {{ $t('booking.clear') }}
            </button>
          </div>
        </article>

        <!-- SUMMARY -->
        <article class="card summary-card">
          <h2>{{ $t('booking.bookingSummary') }}</h2>

          <div class="summary-item">
            <span>{{ $t('booking.hall') }}</span>
            <strong>{{ selectedHall?.name || $t('booking.selectHall') }}</strong>
          </div>

          <div class="summary-item">
            <span>{{ $t('booking.capacity') }}</span>
            <strong>
              {{ selectedHall ? `${selectedHall.capacity} ${$t('booking.personsShort')}` : '-' }}
            </strong>
          </div>

          <div class="summary-item">
            <span>{{ $t('booking.pricePerDay') }}</span>
            <strong>
              {{
                selectedHall
                  ? formatMoney(selectedHall.price_per_day)
                  : '-'
              }}
            </strong>
          </div>

          <div class="summary-item">
            <span>{{ $t('booking.duration') }}</span>
            <strong>{{ totalDays }} {{ $t('booking.daysSuffix') }}</strong>
          </div>

          <div class="summary-total">
            <span>{{ $t('booking.totalEstimated') }}</span>
            <strong>{{ formatMoney(totalPrice) }}</strong>
          </div>
        </article>

        <!-- FORM -->
        <article class="card form-card">
          <h2>{{ $t('booking.customerInfo') }}</h2>

          <form class="admin-form" @submit.prevent="submitBooking">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Prénom</label>
                <input
                  v-model="form.customer_first_name"
                  class="form-input"
                  required
                />
              </div>
              <div class="form-group">
                <label class="form-label">Nom</label>
                <input
                  v-model="form.customer_last_name"
                  class="form-input"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">{{ $t('booking.email') }}</label>
                <input
                  v-model="form.customer_email"
                  type="email"
                  class="form-input"
                  required
                />
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">{{ $t('booking.phone') }}</label>
                <input
                  v-model="form.customer_phone"
                  class="form-input"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">{{ $t('booking.hall') }}</label>
                <select
                  v-model.number="form.hall"
                  class="form-select"
                  required
                  @change="clearDates"
                >
                  <option disabled value="">{{ $t('booking.hallPlaceholder') }}</option>
                  <option
                    v-for="hall in halls"
                    :key="hall.id"
                    :value="hall.id"
                  >
                    {{ hall.name }} -
                    {{ formatNumberSpaces(hall.price_per_day) }}
                    {{ $t('booking.hallPriceSuffix') }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">{{ $t('booking.eventType') }}</label>
                <select v-model="form.event_type" class="form-select">
                  <option value="wedding">{{ $t('booking.eventTypes.wedding') }}</option>
                  <option value="seminar">{{ $t('booking.eventTypes.seminar') }}</option>
                  <option value="conference">{{ $t('booking.eventTypes.conference') }}</option>
                  <option value="birthday">{{ $t('booking.eventTypes.birthday') }}</option>
                  <option value="meeting">{{ $t('booking.eventTypes.meeting') }}</option>
                  <option value="other">{{ $t('booking.eventTypes.other') }}</option>
                </select>
              </div>
            </div>

            <div v-if="hallAdditionalServices.length" class="addons-section">
              <div class="addons-head">
                <strong>Services additionnels</strong>
                <span v-if="addonsTotal > 0" class="addons-total">+ {{ formatMoney(addonsTotal) }}</span>
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
                    <strong>{{ formatMoney(service.price) }}</strong>
                  </div>
                  <div v-else class="addon-sub-block">
                    <div class="addon-sub-head">
                      <strong>{{ service.name }}</strong>
                      <span class="muted-line">Choisissez les sous-services</span>
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
                        <strong>{{ formatMoney(sub.price) }}</strong>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">{{ $t('booking.startDate') }}</label>
                <input :value="startDate" class="form-input" readonly />
              </div>

              <div class="form-group">
                <label class="form-label">{{ $t('booking.endDate') }}</label>
                <input :value="endDate || startDate" class="form-input" readonly />
              </div>
            </div>

            <div class="actions">
              <button
                class="btn btn-primary"
                :disabled="isSubmitting"
              >
                {{
                  isSubmitting ? $t('booking.submit.sending') : $t('booking.submit.confirm')
                }}
              </button>
            </div>
          </form>
        </article>
      </div>
    </div>
  </section>
</template>

<script>
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'
import { useMoney } from '~/composables/useMoney'

const { formatMoney, formatNumberSpaces } = useMoney()

export default {
  data() {
    return {
      halls: [],
      calendarRanges: [],
      isSubmitting: false,
      isLoggedIn: false,
      viewMonth: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
      rangeStart: null,
      rangeEnd: null,
      currentUser: {},
      form: {
        customer_first_name: '',
        customer_last_name: '',
        customer_email: '',
        customer_phone: '',
        hall: '',
        event_type: 'wedding',
        additional_services_selected: [],
        status: 'pending'
      },
      weekdays: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    }
  },

  computed: {
    selectedHall() {
      return this.halls.find(h => h.id === this.form.hall)
    },

    hallAdditionalServices() {
      return Array.isArray(this.selectedHall?.additional_services)
        ? this.selectedHall.additional_services
        : []
    },

    addonsTotal() {
      const services = this.hallAdditionalServices
      const selected = Array.isArray(this.form.additional_services_selected)
        ? this.form.additional_services_selected
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
      return total
    },

    startDate() {
      return this.rangeStart ? this.formatYMD(this.rangeStart) : ''
    },

    endDate() {
      return this.rangeEnd ? this.formatYMD(this.rangeEnd) : ''
    },

    monthLabel() {
      const locale = this.$i18n?.locale === 'en' ? 'en-US' : 'fr-FR'
      return this.viewMonth.toLocaleDateString(locale, {
        month: 'long',
        year: 'numeric'
      })
    },

    bookedSet() {
      const set = new Set()
      if (!this.form.hall) return set

      const ranges = this.calendarRanges.filter(
        r => Number(r.hall_id) === Number(this.form.hall)
      )

      for (const r of ranges) {
        const start = new Date(r.start_date)
        const end = new Date(r.end_date)

        for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
          set.add(this.formatYMD(new Date(d)))
        }
      }
      return set
    },

    calendarCells() {
      const first = new Date(
        this.viewMonth.getFullYear(),
        this.viewMonth.getMonth(),
        1
      )

      const firstWeekday = (first.getDay() + 6) % 7
      const start = new Date(first)
      start.setDate(first.getDate() - firstWeekday)

      const today = new Date()
      today.setHours(0, 0, 0, 0)

      return Array.from({ length: 42 }, (_, i) => {
        const d = new Date(start)
        d.setDate(start.getDate() + i)

        const ymd = this.formatYMD(d)

        return {
          key: ymd + '-' + i,
          date: d,
          currentMonth: d.getMonth() === this.viewMonth.getMonth(),
          isPast: d < today,
          isBooked: this.bookedSet.has(ymd)
        }
      })
    },

    totalDays() {
      if (!this.rangeStart) return 0
      if (!this.rangeEnd) return 1

      return (
        Math.floor(
          (this.rangeEnd - this.rangeStart) / (1000 * 60 * 60 * 24)
        ) + 1
      )
    },

    totalPrice() {
      if (!this.selectedHall || this.totalDays <= 0) return 0
      const base = Number(this.selectedHall.price_per_day || 0) * this.totalDays
      return Math.round(base + Number(this.addonsTotal || 0))
    }
  },

  methods: {
    formatMoney,
    formatNumberSpaces,
    formatYMD(d) {
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(
        2,
        '0'
      )}-${String(d.getDate()).padStart(2, '0')}`
    },

    isSameDate(a, b) {
      return (
        a &&
        b &&
        this.formatYMD(a) === this.formatYMD(b)
      )
    },

    isInRange(d, s, e) {
      return s && e && d > s && d < e
    },

    isServiceSelected(serviceName) {
      return (this.form.additional_services_selected || []).some(
        s => String(s?.name || '') === String(serviceName || '')
      )
    },

    toggleSimpleService(service) {
      const name = String(service?.name || '').trim()
      if (!name) return
      const selected = Array.isArray(this.form.additional_services_selected)
        ? [...this.form.additional_services_selected]
        : []
      const idx = selected.findIndex(s => String(s?.name || '') === name)
      if (idx >= 0) selected.splice(idx, 1)
      else selected.push({ name })
      this.form.additional_services_selected = selected
    },

    isSubserviceSelected(serviceName, subName) {
      const item = (this.form.additional_services_selected || []).find(
        s => String(s?.name || '') === String(serviceName || '')
      )
      const subs = Array.isArray(item?.subservices) ? item.subservices : []
      return subs.some(sub => String(sub?.name || '') === String(subName || ''))
    },

    toggleSubservice(serviceName, subName) {
      const name = String(serviceName || '').trim()
      const sub = String(subName || '').trim()
      if (!name || !sub) return
      const selected = Array.isArray(this.form.additional_services_selected)
        ? [...this.form.additional_services_selected]
        : []
      let item = selected.find(s => String(s?.name || '') === name)
      if (!item) {
        selected.push({ name, subservices: [{ name: sub }] })
        this.form.additional_services_selected = selected
        return
      }
      const subs = Array.isArray(item.subservices) ? [...item.subservices] : []
      const idx = subs.findIndex(s => String(s?.name || '') === sub)
      if (idx >= 0) subs.splice(idx, 1)
      else subs.push({ name: sub })
      if (subs.length === 0) {
        this.form.additional_services_selected = selected.filter(
          s => String(s?.name || '') !== name
        )
      } else {
        item.subservices = subs
        this.form.additional_services_selected = selected
      }
    },

    prevMonth() {
      this.viewMonth = new Date(
        this.viewMonth.getFullYear(),
        this.viewMonth.getMonth() - 1,
        1
      )
    },

    nextMonth() {
      this.viewMonth = new Date(
        this.viewMonth.getFullYear(),
        this.viewMonth.getMonth() + 1,
        1
      )
    },


    clearDates() {
      this.rangeStart = null
      this.rangeEnd = null
    },

    hasConflict(start, end) {
      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (this.bookedSet.has(this.formatYMD(new Date(d)))) return true
      }
      return false
    },

    onDayClick(date) {
      if (!this.rangeStart || this.rangeEnd) {
        this.rangeStart = date
        this.rangeEnd = null
        return
      }

      if (date < this.rangeStart) {
        this.rangeStart = date
        this.rangeEnd = null
        return
      }

      if (this.hasConflict(this.rangeStart, date)) {
        notify(this.$t('booking.notify.hasBookedDates'), 'warning')
        return
      }

      this.rangeEnd = date
    },

    async fetchHalls() {
      try {
        const res = await api.get('halls/')
        this.halls = res.data

        if (this.halls.length && !this.form.hall) {
          this.form.hall = this.halls[0].id
        }
      } catch {
        notify(this.$t('booking.notify.loadHallsFail'), 'danger')
      }
    },

    async fetchCalendar() {
      try {
        const res = await api.get('bookings/calendar/', {
          params: this.form.hall ? { hall: this.form.hall } : {}
        })
        this.calendarRanges = Array.isArray(res.data) ? res.data : []
      } catch {
        this.calendarRanges = []
      }
    },

    async fetchMe() {
      try {
        const res = await api.get('me/')
        this.currentUser = res.data

        if (!this.form.customer_email && res.data?.email) {
          this.form.customer_email = res.data.email
        }

        if (!this.form.customer_first_name && res.data?.first_name) {
          this.form.customer_first_name = res.data.first_name
        }
        if (!this.form.customer_last_name && res.data?.last_name) {
          this.form.customer_last_name = res.data.last_name
        }
      } catch {
        this.currentUser = {}
      }
    },

    async submitBooking() {
      if (!this.rangeStart) {
        notify(this.$t('booking.notify.selectAtLeastOneDate'), 'warning')
        return
      }

      try {
        this.isSubmitting = true

        const finalEnd = this.rangeEnd || this.rangeStart

        if (this.hasConflict(this.rangeStart, finalEnd)) {
        notify(this.$t('booking.notify.periodAlreadyBooked'), 'warning')
          this.isSubmitting = false
          return
        }

        const response = await api.post('bookings/guest/', {
          hall: this.form.hall,
          full_name: `${String(this.form.customer_first_name || '').trim()} ${String(this.form.customer_last_name || '').trim()}`.trim(),
          email: this.form.customer_email,
          phone: this.form.customer_phone,
          event_type: this.form.event_type,
          start_date: this.formatYMD(this.rangeStart),
          end_date: this.formatYMD(finalEnd),
          additional_services_selected: this.form.additional_services_selected,
        })

        notify(response?.data?.message || this.$t('booking.notify.bookingSuccess'), 'success')

        this.form.customer_first_name = ''
        this.form.customer_last_name = ''
        this.form.customer_email = ''
        this.form.customer_phone = ''
        this.form.event_type = 'wedding'
        this.form.additional_services_selected = []
        this.clearDates()

        await this.fetchCalendar()
      } catch {
        notify(this.$t('booking.notify.bookingFail'), 'danger')
      } finally {
        this.isSubmitting = false
      }
    }
  },

  mounted() {
    this.isLoggedIn = !!localStorage.getItem('access_token')
    this.fetchHalls()
    this.fetchCalendar()

    if (this.isLoggedIn) this.fetchMe()
  },

  watch: {
    'form.hall'() {
      this.fetchCalendar()
      this.form.additional_services_selected = []
    }
  }
}
</script>
<style scoped>
.book-page {
  background: #f8fafc;
  min-height: 100vh;
  padding: 5rem 0 3rem;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.book-layout {
  display: grid;
  grid-template-columns: 1.2fr .95fr 1.3fr;
  gap: 1rem;
}

.calendar-card, .summary-card, .form-card {
  border: 1px solid #e2e8f0;
  box-shadow: none;
  padding: 1.25rem;
}

.calendar-card h2, .summary-card h2, .form-card h2 {
  margin: 0 0 .9rem;
  font-size: 1.1rem;
}

.calendar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: .7rem;
}

.calendar-nav {
  display: flex;
  align-items: center;
  gap: .5rem;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #334155;
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: .25rem;
  margin-bottom: .3rem;
}

.weekday-row span {
  text-align: center;
  font-size: .75rem;
  font-weight: 700;
  color: #94a3b8;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: .25rem;
}
button:disabled {
  pointer-events: none;
  opacity: 0.6;
  cursor: not-allowed;
}
.day-cell {
  height: 38px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  color: #0f172a;
  font-weight: 600;
}

.day-cell.muted {
  color: #cbd5e1;
  background: #f8fafc;
}

.day-cell.disabled,
.day-cell:disabled {
  cursor: not-allowed;
  opacity: .55;
}

.day-cell.booked {
  background: #fee2e2;
  border-color: #fecaca;
  color: #b91c1c;
}

.day-cell.start,
.day-cell.end {
  background: #0f172a;
  color: #fff;
  border-color: #0f172a;
}

.day-cell.inrange {
  background: #e2e8f0;
  border-color: #cbd5e1;
}

.calendar-legend {
  display: flex;
  gap: .75rem;
  flex-wrap: wrap;
  margin-top: .75rem;
  font-size: .8rem;
  color: #64748b;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  display: inline-block;
  margin-right: .3rem;
}

.dot.booked { background: #ef4444; }
.dot.selected { background: #0f172a; }
.dot.range { background: #94a3b8; }

.summary-item, .summary-total {
  display: flex;
  justify-content: space-between;
  padding: .55rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.summary-item span, .summary-total span {
  color: #64748b;
}

.addons-section {
  border-top: 1px solid #eef2f7;
  padding-top: 14px;
  margin-top: 8px;
}
.addons-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}
.addons-total {
  color: #0f172a;
  font-weight: 900;
}
.addons-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.addon-item {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 12px 14px;
  background: #f8fafc;
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
}

.summary-item.controls {
  border-bottom: 0;
  padding-top: .75rem;
}

.summary-total {
  border-bottom: 0;
  padding-top: .9rem;
  font-size: 1.05rem;
}

.summary-total strong {
  color: #0f766e;
}

.actions {
  margin-top: .9rem;
}

.login-gate {
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 12px;
  padding: .9rem;
  margin-bottom: .9rem;
}

.login-gate-title {
  font-weight: 800;
  color: #0f172a;
  margin-bottom: .25rem;
}

.login-gate-text {
  color: #64748b;
  font-size: .92rem;
}

.login-gate-actions {
  margin-top: .65rem;
  display: flex;
  gap: .6rem;
  flex-wrap: wrap;
}

@media (max-width: 960px) {
  .book-layout {
    grid-template-columns: 1fr;
  }
}
</style>
