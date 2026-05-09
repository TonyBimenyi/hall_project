<template>
  <section class="contact-section">
    <div class="container">
      <div class="contact-header">
        <h1 class="page-title">Get in Touch</h1>
        <p class="page-subtitle">
          We're here to help bring your vision to life. Reach out — we'd love to hear from you.
        </p>
      </div>
      <div class="contact-grid">
        <!-- Left: Contact Form -->
        <div class="contact-form card">
          <h2 class="form-title">Send Us a Message</h2>
          <p class="form-subtitle">We'll get back to you within 24–48 hours.</p>
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="name">Full Name <span class="required">*</span></label>
              <input
                id="name"
                v-model="form.name"
                type="text"
                placeholder="John Doe"
                required
                :class="{ 'error': errors.name }"
              />
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>
            <div class="form-group">
              <label for="email">Email Address <span class="required">*</span></label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                placeholder="john@example.com"
                required
                :class="{ 'error': errors.email }"
              />
              <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
            </div>
            <div class="form-group">
              <label for="phone">Phone Number</label>
              <input
                id="phone"
                v-model="form.phone"
                type="tel"
                placeholder="(555) 123-4567"
              />
            </div>
            <div class="form-group">
              <label for="message">Your Message <span class="required">*</span></label>
              <textarea
                id="message"
                v-model="form.message"
                rows="6"
                placeholder="Tell us about your event, dates you're considering, or any questions..."
                required
                :class="{ 'error': errors.message }"
              ></textarea>
              <span v-if="errors.message" class="error-text">{{ errors.message }}</span>
            </div>
            <button
              type="submit"
              class="submit-button"
              :disabled="loading"
            >
              <span v-if="loading">Sending...</span>
              <span v-else>Send Message</span>
            </button>
          </form>
        </div>

        <!-- Right: Contact Information -->
        <div class="contact-info">
          <div class="info-card">
            <div class="info-icon">
              <Icon icon="mdi:map-marker" />
            </div>
            <div class="info-content">
              <h3>Our Location</h3>
              <p>123 Elite Avenue<br>Downtown City, ST 12345</p>
            </div>
          </div>
          <div class="info-card">
            <div class="info-icon">
              <Icon icon="mdi:phone" />
            </div>
            <div class="info-content">
              <h3>Phone</h3>
              <p>Main: (555) 123-4567<br>Events & Bookings: (555) 123-4568</p>
            </div>
          </div>
          <div class="info-card">
            <div class="info-icon">
              <Icon icon="mdi:email-outline" />
            </div>
            <div class="info-content">
              <h3>Email</h3>
              <p>info@elitereception.com<br>bookings@elitereception.com</p>
            </div>
          </div>
          <div class="info-card">
            <div class="info-icon">
              <Icon icon="mdi:clock-outline" />
            </div>
            <div class="info-content">
              <h3>Office Hours</h3>
              <p>Monday–Friday: 9:00 AM – 6:00 PM<br>Saturday: 10:00 AM – 4:00 PM<br>Sunday: Closed</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { notify } from '~/composables/useNotification'

const form = ref({
  name: '',
  email: '',
  phone: '',
  message: ''
})

const errors = ref({})
const loading = ref(false)

const validateForm = () => {
  errors.value = {}
  let isValid = true

  if (!form.value.name.trim()) {
    errors.value.name = 'Full name is required'
    isValid = false
  }
  if (!form.value.email.trim()) {
    errors.value.email = 'Email is required'
    isValid = false
  } else if (!/\S+@\S+\.\S+/.test(form.value.email)) {
    errors.value.email = 'Please enter a valid email'
    isValid = false
  }
  if (!form.value.message.trim()) {
    errors.value.message = 'Message cannot be empty'
    isValid = false
  }

  return isValid
}

const handleSubmit = async () => {
  if (!validateForm()) {
    notify('Please fill in all required fields correctly', 'warning')
    return
  }

  loading.value = true

  try {
    // Replace with your real API endpoint when ready
    // await $fetch('/api/contact', { method: 'POST', body: form.value })

    // Simulate success for now
    await new Promise(resolve => setTimeout(resolve, 1200))

    notify('Thank you! Your message has been sent.', 'success')

    // Reset form
    form.value = { name: '', email: '', phone: '', message: '' }
  } catch (err) {
    notify('Something went wrong. Please try again later.', 'danger')
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.contact-section {
  padding: clamp(5rem, 10vw, 8rem) 0;
  background: #f7f9fc;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1.5rem;
}

.contact-header {
  text-align: center;
  margin-bottom: 4rem;
}

.page-title {
  font-family: var(--font-secondary);
  font-size: clamp(2.5rem, 6.5vw, 3.8rem);
  color: #061b49;
  margin-bottom: 0.8rem;
}

.page-subtitle {
  font-size: clamp(1.1rem, 2.6vw, 1.28rem);
  color: #475569;
  max-width: 680px;
  margin: 0 auto;
}

.contact-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.5rem;
}

@media (min-width: 992px) {
  .contact-grid {
    grid-template-columns: 5fr 4fr;
    gap: 3.5rem;
  }
}

/* ─── Form Card – FIXED RESPONSIVE INPUTS ─── */
.contact-form {
  background: white;
  border-radius: 16px;
  padding: clamp(2rem, 4vw, 2.8rem);
  box-shadow: 0 10px 35px rgba(6, 27, 73, 0.07);
  overflow: hidden; /* ← prevents any child overflow */
}

.form-title {
  font-family: var(--font-secondary);
  font-size: 1.95rem;
  color: #061b49;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #64748b;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.6rem;
  width: 100%;
  max-width: 100%; /* ← containment */
  box-sizing: border-box;
}

label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.55rem;
  color: #374151;
}

.required {
  color: #ef4444;
  margin-left: 4px;
}

/* FIXED: Inputs & Textarea containment */
input,
textarea {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box; /* ← crucial: padding included in width */
  padding: 0.9rem 1.1rem;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus,
textarea:focus {
  outline: none;
  border-color: #3751ff;
  box-shadow: 0 0 0 3px rgba(55,81,255,0.08);
}

.error {
  border-color: #ef4444 !important;
}

.error-text {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.4rem;
  display: block;
}

.submit-button {
  width: 100%;
  padding: 1.15rem;
  background: #061b49;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
  margin-top: 1.2rem;
}

.submit-button:hover:not(:disabled) {
  background: #0a255f;
  transform: translateY(-2px);
}

.submit-button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

/* Info Section */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 1.4rem;
}

.info-card {
  background: white;
  border-radius: 16px;
  padding: 1.6rem;
  display: flex;
  gap: 1.2rem;
  box-shadow: 0 6px 20px rgba(6, 27, 73, 0.06);
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(6, 27, 73, 0.1);
}

.info-icon {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  background: #061b49;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-icon :deep(svg) {
  width: 28px;
  height: 28px;
  color: white;
}

.info-content h3 {
  font-size: 1.28rem;
  color: #061b49;
  margin-bottom: 0.4rem;
  font-weight: 600;
}

.info-content p {
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

/* ──────────────────────────────────
   RESPONSIVE – extra containment
─────────────────────────────────── */
@media (max-width: 991px) {
  .contact-grid {
    grid-template-columns: 1fr;
  }

  .contact-form {
    padding: 2rem 1.5rem; /* slightly less padding on mobile */
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 1rem;
  }

  .page-title {
    font-size: clamp(2.2rem, 7vw, 3rem);
  }

  .form-group label {
    font-size: 0.95rem;
  }

  input,
  textarea {
    font-size: 0.98rem;
    padding: 0.85rem 1rem;
  }

  .submit-button {
    padding: 1rem;
    font-size: 1rem;
  }
}
</style>