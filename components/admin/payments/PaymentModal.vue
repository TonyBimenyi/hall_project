<!-- components/admin/payments/PaymentModal.vue -->
<template>
  <div v-if="isVisible" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Ajouter un paiement pour la réservation #{{ booking?.id || '—' }}</h3>
        <button class="modal-close" @click="closeModal">×</button>
      </div>

      <div class="modal-body">
        <!-- Booking summary -->
        <div class="booking-summary" v-if="booking">
          <p><strong>Client :</strong> {{ booking.clients?.first_name }} {{ booking.clients?.last_name }}</p>
          <p><strong>Salle :</strong> {{ booking.halls?.name || 'Salle #' + booking.hall }}</p>
          <p><strong>Période :</strong> {{ formatDate(booking.date_start) }} → {{ formatDate(booking.date_end) }}</p>
          <p><strong>Montant total dû :</strong> ${{ Number(booking.total_cost || 0).toLocaleString() }}</p>
          <p><strong>Déjà payé :</strong> ${{ Number(booking.total_paid || 0).toLocaleString() }}</p>
          <p><strong>Restant :</strong> ${{ Number(booking.remaining_balance || 0).toLocaleString() }}</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="submit" class="payment-form">
          <div class="form-group">
            <label>Montant <span class="required">*</span></label>
            <input
              type="number"
              v-model.number="form.amount"
              step="0.01"
              min="0.01"
              placeholder="0.00"
              required
              :class="{ 'error': errors.amount }"
            />
            <span v-if="errors.amount" class="error-text">{{ errors.amount }}</span>
          </div>

          <div class="form-group">
            <label>Type de paiement <span class="required">*</span></label>
            <select v-model="form.payment_type" required>
              <option value="">Sélectionner le type</option>
              <option value="deposit">Acompte</option>
              <option value="final">Paiement final</option>
              <option value="damage_fee">Frais de dommages</option>
              <option value="replacement_fee">Frais de remplacement</option>
            </select>
          </div>

          <div class="form-group">
            <label>Mode de paiement <span class="required">*</span></label>
            <select v-model="form.payment_method" required>
              <option value="">Sélectionner le mode</option>
              <option value="cash">Espèces</option>
              <option value="card">Carte</option>
              <option value="online">En ligne</option>
            </select>
          </div>

          <div class="form-group">
            <label>Statut <span class="required">*</span></label>
            <select v-model="form.status" required>
              <option value="pending">En attente</option>
              <option value="paid">Payé</option>
              <option value="refunded">Remboursé</option>
            </select>
          </div>

          <div class="form-group">
            <label>Notes</label>
            <textarea
              v-model="form.notes"
              rows="3"
              placeholder="ID de transaction, référence, remarques..."
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="closeModal">
              Annuler
            </button>
            <button
              type="submit"
              class="btn-submit"
              :disabled="submitting || !form.amount || !form.payment_type || !form.payment_method || !form.status"
            >
              <span v-if="submitting">
                <span class="spinner"></span> Traitement...
              </span>
              <span v-else>Enregistrer le paiement</span>
            </button>
          </div>
        </form>

        <!-- Show backend validation errors -->
        <div v-if="Object.keys(errors).length > 0" class="server-errors">
          <p v-for="(err, field) in errors" :key="field" class="error-text">
            <strong>{{ field }}:</strong> {{ Array.isArray(err) ? err[0] : err }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { notify } from '~/composables/useNotification'   // ← ADDED
import { api } from '~/composables/useApi'

export default {
  props: {
    isVisible: {
      type: Boolean,
      required: true
    },
    booking: {
      type: Object,
      default: () => ({})
    }
  },

  data() {
    return {
      form: {
        booking: null,
        amount: null,
        payment_type: '',
        payment_method: '',
        status: 'pending',
        notes: ''
      },
      errors: {},
      submitting: false
    }
  },

  watch: {
    booking: {
      immediate: true,
      handler(newBooking) {
        if (newBooking?.id) {
          this.form.booking = newBooking.id
        }
      }
    }
  },

  methods: {
    async submit() {
      this.errors = {}
      this.submitting = true

      if (!this.form.amount || this.form.amount <= 0) {
        this.errors.amount = 'Le montant doit être supérieur à 0'
        this.submitting = false
        return
      }

      try {
        const response = await api.post('payments/', this.form)

        // Success notification
        notify('Paiement enregistré avec succès !', 'success')

        this.$emit('payment:created', response.data)
        this.closeModal()
      } catch (err) {
        const serverErrors = err.response?.data?.erreurs || err.response?.data
        if (serverErrors) {
          this.errors = serverErrors
          // Show first error message as notification
          const firstError = Object.values(serverErrors)[0]
          notify(Array.isArray(firstError) ? firstError[0] : firstError, 'danger')
        } else {
          notify('Une erreur inattendue est survenue lors de l\'enregistrement du paiement.', 'danger')
        }
        this.$emit('payment:error', err)
      } finally {
        this.submitting = false
      }
    },

    closeModal() {
      this.$emit('close')
    },

    formatDate(dateStr) {
      if (!dateStr) return '—'
      const d = new Date(dateStr)
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
    }
  }
}
</script>

<style scoped>
/* Your existing styles unchanged */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
  margin: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  overflow: hidden;
}

.modal-header {
  padding: 18px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.35rem;
  color: #1f2937;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.8rem;
  color: #6b7280;
  cursor: pointer;
}

.modal-body {
  padding: 24px;
}

.booking-summary {
  background: #f1f5f9;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  font-size: 0.95rem;
}

.booking-summary p {
  margin: 8px 0;
}

.booking-summary strong {
  color: #374151;
}

.payment-form .form-group {
  margin-bottom: 20px;
}

.payment-form label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
}

.payment-form input,
.payment-form select,
.payment-form textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 1rem;
}

.payment-form input:focus,
.payment-form select:focus,
.payment-form textarea:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.1);
}

.required { color: #ef4444; }
.error { border-color: #ef4444 !important; }
.error-text {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 4px;
  display: block;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 28px;
}

.btn-cancel {
  padding: 10px 20px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
}

.btn-submit {
  padding: 10px 24px;
  background: #7c3aed;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Better error visibility */
.server-errors {
  margin-top: 16px;
  padding: 12px;
  background: #fee2e2;
  border-radius: 6px;
  font-size: 0.9rem;
}

.server-errors .error-text {
  margin: 4px 0;
}
</style>
