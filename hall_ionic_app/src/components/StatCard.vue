<template>
  <div class="stat-card" :class="[`variant-${variant}`]">
    <div class="stat-card-bg" aria-hidden="true"></div>
    <div class="stat-card-eyebrow">
      <span class="stat-card-label">{{ label }}</span>
      <div v-if="icon" class="stat-card-icon-wrap">
        <Icon :icon="icon" class="stat-card-icon" />
      </div>
    </div>
    <div class="stat-card-main">
      <div class="stat-card-value">{{ displayValue }}</div>
      <div v-if="caption || delta" class="stat-card-meta">
        <span v-if="caption" class="stat-card-caption">{{ caption }}</span>
        <span v-if="delta" :class="['stat-card-delta', deltaClass]">{{ delta }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: { type: String, default: '' },
    value: { type: [String, Number], default: 0 },
    caption: { type: String, default: '' },
    delta: { type: String, default: '' },
    deltaTone: { type: String, default: 'neutral' },
    icon: { type: String, default: '' },
    variant: { type: String, default: 'default' }
  },
  data() {
    return {}
  },
  computed: {
    displayValue() {
      return this.value == null ? '—' : this.value
    },
    deltaClass() {
      return `delta-${this.deltaTone || 'neutral'}`
    }
  }
}
</script>

<style scoped>
.stat-card {
  padding: 18px 18px 18px;
  border-radius: 24px;
  background: #ffffff;
  border: 1px solid rgba(23, 11, 2, 0.08);
  display: flex;
  flex-direction: column;
  gap: 14px;
  position: relative;
  overflow: hidden;
  box-shadow:
    0 14px 34px rgba(23, 11, 2, 0.05),
    inset 0 1px 0 rgba(255,255,255,0.8);
}

.stat-card-bg {
  position: absolute;
  inset: auto -20px -30px auto;
  width: 150px;
  height: 150px;
  border-radius: 999px;
  background: radial-gradient(closest-side, rgba(215,111,2,0.08), transparent 70%);
  pointer-events: none;
}

.stat-card.variant-primary {
  background:
    radial-gradient(circle at 92% 8%, rgba(255,255,255,0.22), transparent 42%),
    linear-gradient(145deg, #d76f02 0%, #e68a33 55%, #d76f02 100%);
  border-color: rgba(215, 111, 2, 0.9);
  color: #ffffff;
  box-shadow:
    0 22px 46px rgba(215, 111, 2, 0.28),
    inset 0 1px 0 rgba(255,255,255,0.28);
}
.stat-card.variant-primary .stat-card-bg {
  background: radial-gradient(closest-side, rgba(255,255,255,0.18), transparent 70%);
}

.stat-card.variant-gold {
  background:
    radial-gradient(circle at 12% 100%, rgba(212, 175, 55, 0.18), transparent 50%),
    linear-gradient(180deg, #ffffff 0%, #fdfaef 100%);
  border-color: rgba(212, 175, 55, 0.35);
}

.stat-card.variant-default {
  background:
    radial-gradient(circle at 100% 0%, rgba(26, 58, 122, 0.06), transparent 45%),
    linear-gradient(180deg, #ffffff 0%, #fcf8f3 100%);
}

.stat-card.variant-teal {
  background:
    radial-gradient(circle at 0% 100%, rgba(15, 118, 110, 0.08), transparent 45%),
    linear-gradient(180deg, #ffffff 0%, #fafbfb 100%);
  border-color: rgba(15, 118, 110, 0.15);
}

.stat-card-eyebrow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.stat-card-label {
  letter-spacing: 0.14em;
  font-size: 0.66rem;
  color: #64748b;
  font-weight: 800;
  text-transform: uppercase;
}

.variant-primary .stat-card-label {
  color: rgba(255, 255, 255, 0.82);
}

.stat-card-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(215, 111, 2, 0.10);
  color: #d76f02;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
}

.variant-primary .stat-card-icon-wrap {
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.24);
}

.variant-gold .stat-card-icon-wrap {
  background: rgba(212, 175, 55, 0.18);
  color: #b8860b;
}

.variant-teal .stat-card-icon-wrap {
  background: rgba(15, 118, 110, 0.12);
  color: #0f766e;
}

.stat-card-icon {
  font-size: 1.08rem;
}

.stat-card-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.stat-card-value {
  font-size: 1.9rem;
  font-weight: 800;
  letter-spacing: -0.015em;
  line-height: 1;
  color: #170b02;
  font-family: 'Playfair Display', Georgia, serif;
}

.variant-primary .stat-card-value {
  color: #ffffff;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.1);
}

.stat-card-meta {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 0.78rem;
}

.stat-card-caption {
  color: #64748b;
  font-weight: 500;
}

.variant-primary .stat-card-caption {
  color: rgba(255, 255, 255, 0.78);
}

.stat-card-delta {
  font-weight: 800;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.7rem;
  letter-spacing: 0.02em;
}

.stat-card-delta.delta-positive {
  background: rgba(22, 163, 74, 0.12);
  color: #15803d;
}
.variant-primary .stat-card-delta.delta-positive {
  background: rgba(187, 247, 208, 0.18);
  color: #bbf7d0;
}

.stat-card-delta.delta-negative {
  background: rgba(220, 38, 38, 0.12);
  color: #b91c1c;
}

.stat-card-delta.delta-neutral {
  background: rgba(100, 116, 139, 0.12);
  color: #475569;
}
.variant-primary .stat-card-delta.delta-neutral {
  background: rgba(255,255,255,0.18);
  color: #ffffff;
}
</style>
