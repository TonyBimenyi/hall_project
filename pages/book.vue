<template>
  <section class="book-page">
    <div class="container">
      <ReusablePageHeader />

      <div class="book-layout">
        <!-- CALENDAR -->
        <article class="card calendar-card">
          <div class="calendar-top">
            <h2>Calendrier</h2>
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
            <span v-for="d in weekdays" :key="d">{{ d }}</span>
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
            <span><i class="dot booked"></i> Réservé</span>
            <span><i class="dot selected"></i> Sélection</span>
            <span><i class="dot range"></i> Intervalle</span>
          </div>

          <div class="summary-item">
            <span>Début</span>
            <strong>{{ startDate || 'Non sélectionné' }}</strong>
          </div>

          <div class="summary-item">
            <span>Fin</span>
            <strong>{{ endDate || startDate || 'Non sélectionné' }}</strong>
          </div>

          <div class="summary-item controls">
            <button class="btn btn-outline btn-sm" @click="clearDates">
              Effacer
            </button>
          </div>
        </article>

        <!-- SUMMARY -->
        <article class="card summary-card">
          <h2>Résumé de réservation</h2>

          <div class="summary-item">
            <span>Salle</span>
            <strong>{{ selectedHall?.name || 'Sélectionnez une salle' }}</strong>
          </div>

          <div class="summary-item">
            <span>Capacité</span>
            <strong>
              {{ selectedHall ? `${selectedHall.capacity} pers.` : '-' }}
            </strong>
          </div>

          <div class="summary-item">
            <span>Prix / jour</span>
            <strong>
              {{
                selectedHall
                  ? `${Number(selectedHall.price_per_day || 0).toLocaleString()} Fbu`
                  : '-'
              }}
            </strong>
          </div>

          <div class="summary-item">
            <span>Durée</span>
            <strong>{{ totalDays }} jour(s)</strong>
          </div>

          <div class="summary-total">
            <span>Total estimé</span>
            <strong>{{ totalPrice.toLocaleString() }} Fbu</strong>
          </div>
        </article>

        <!-- FORM -->
        <article class="card form-card">
          <h2>Informations client</h2>

          <div v-if="!isLoggedIn" class="login-gate">
            <div class="login-gate-title">Connexion requise</div>
            <div class="login-gate-text">
              Veuillez vous connecter pour confirmer une réservation en ligne.
            </div>
            <div class="login-gate-actions">
              <NuxtLink to="/login" class="btn btn-primary btn-sm"
                >Se connecter</NuxtLink
              >
              <NuxtLink to="/register" class="btn btn-outline btn-sm"
                >Créer un compte</NuxtLink
              >
            </div>
          </div>

          <form class="admin-form" @submit.prevent="submitBooking">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Nom complet</label>
                <input
                  v-model="form.customer_name"
                  class="form-input"
                  required
                />
              </div>

              <div class="form-group">
                <label class="form-label">Email</label>
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
                <label class="form-label">Salle</label>
                <select
                  v-model.number="form.hall"
                  class="form-select"
                  required
                  @change="clearDates"
                >
                  <option disabled value="">Sélectionner une salle</option>
                  <option
                    v-for="hall in halls"
                    :key="hall.id"
                    :value="hall.id"
                  >
                    {{ hall.name }} -
                    {{ Number(hall.price_per_day || 0).toLocaleString() }}
                    Fbu/jour
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">Type d'événement</label>
                <select v-model="form.event_type" class="form-select">
                  <option value="Mariage">Mariage</option>
                  <option value="Séminaire">Séminaire</option>
                  <option value="Conférence">Conférence</option>
                  <option value="Anniversaire">Anniversaire</option>
                  <option value="Réunion">Réunion</option>
                  <option value="Autre">Autre</option>
                </select>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Date début</label>
                <input :value="startDate" class="form-input" readonly />
              </div>

              <div class="form-group">
                <label class="form-label">Date fin</label>
                <input :value="endDate || startDate" class="form-input" readonly />
              </div>
            </div>

            <div class="actions">
              <button
                class="btn btn-primary"
                :disabled="isSubmitting || !isLoggedIn"
              >
                {{
                  !isLoggedIn
                    ? 'Connectez-vous pour réserver'
                    : isSubmitting
                    ? 'Envoi en cours...'
                    : 'Confirmer la réservation'
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
        customer_name: '',
        customer_email: '',
        hall: '',
        event_type: 'Mariage',
        status: 'pending'
      },
      weekdays: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    }
  },

  computed: {
    selectedHall() {
      return this.halls.find(h => h.id === this.form.hall)
    },

    startDate() {
      return this.rangeStart ? this.formatYMD(this.rangeStart) : ''
    },

    endDate() {
      return this.rangeEnd ? this.formatYMD(this.rangeEnd) : ''
    },

    monthLabel() {
      return this.viewMonth.toLocaleDateString('fr-FR', {
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
      return Math.round(
        Number(this.selectedHall.price_per_day || 0) * this.totalDays
      )
    }
  },

  methods: {
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
        notify('Cette période contient des dates déjà réservées', 'warning')
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
        notify('Impossible de charger les salles', 'danger')
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

        const fullName =
          `${res.data?.first_name || ''} ${res.data?.last_name || ''}`.trim()

        if (!this.form.customer_name && fullName) {
          this.form.customer_name = fullName
        }
      } catch {
        this.currentUser = {}
      }
    },

    async submitBooking() {
      if (!this.isLoggedIn) {
        notify('Veuillez vous connecter pour réserver', 'warning')
        this.$router.push('/login')
        return
      }

      if (!this.rangeStart) {
        notify('Veuillez sélectionner au moins une date', 'warning')
        return
      }

      try {
        this.isSubmitting = true

        const finalEnd = this.rangeEnd || this.rangeStart

        if (this.hasConflict(this.rangeStart, finalEnd)) {
          notify('Cette période est déjà réservée', 'warning')
          this.isSubmitting = false
          return
        }

        await api.post('bookings/', {
          ...this.form,
          start_date: this.formatYMD(this.rangeStart),
          end_date: this.formatYMD(finalEnd),
          total_price: this.totalPrice
        })

        notify('Réservation enregistrée avec succès', 'success')

        this.form.customer_name = ''
        this.form.customer_email = ''
        this.form.event_type = 'Mariage'
        this.clearDates()

        await this.fetchCalendar()
      } catch {
        notify('Échec de la réservation', 'danger')
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
