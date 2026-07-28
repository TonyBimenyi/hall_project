<template>
  <transition name="load-fade">
    <div v-if="visible" class="load-overlay" :class="{ 'load-scrim': scrim }">
      <div class="load-card">
        <div class="load-orbit" aria-hidden="true">
          <span class="orb o1"></span>
          <span class="orb o2"></span>
          <span class="orb o3"></span>
        </div>
        <div class="load-seal" aria-hidden="true">
          <div class="seal-ring">
            <div class="seal-core">
              <span class="seal-lv">LV</span>
            </div>
          </div>
        </div>
        <div class="load-copy">
          <div class="load-title">{{ title }}</div>
          <div class="load-dots">
            <span>Chargement</span>
            <span class="dots">
              <span class="d1">•</span><span class="d2">•</span><span class="d3">•</span>
            </span>
          </div>
          <div class="load-sub" v-if="subtitle">{{ subtitle }}</div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'LoadingOverlay',
  props: {
    visible: { type: Boolean, default: false },
    title: { type: String, default: 'Labertha Villa' },
    subtitle: { type: String, default: '' },
    scrim: { type: Boolean, default: true }
  }
}
</script>

<style scoped>
.load-overlay {
  position: absolute;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}

.load-scrim {
  background:
    radial-gradient(circle at 30% 20%, rgba(215, 111, 2, 0.14), transparent 55%),
    radial-gradient(circle at 75% 80%, rgba(26, 58, 122, 0.16), transparent 55%),
    rgba(251, 247, 242, 0.92);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.load-card {
  position: relative;
  width: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.load-orbit {
  position: absolute;
  inset: -8px 0 auto;
  margin: auto;
  width: 140px;
  height: 140px;
}

.orb {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  border: 2px dashed transparent;
  animation: orbSpin 2.4s linear infinite;
}
.orb::before {
  content: "";
  position: absolute;
  width: 10px;
  height: 10px;
  border-radius: 999px;
  top: -5px;
  left: 50%;
  transform: translateX(-50%);
  filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.12));
}

.o1 {
  inset: 0;
  border-color: rgba(215, 111, 2, 0.35);
  animation-duration: 2.2s;
}
.o1::before { background: linear-gradient(135deg, #ffaa55, #d76f02); }

.o2 {
  inset: 16px;
  border-color: rgba(26, 58, 122, 0.38);
  animation-direction: reverse;
  animation-duration: 3s;
}
.o2::before { background: linear-gradient(135deg, #2f55a0, #1a3a7a); }

.o3 {
  inset: 32px;
  border-color: rgba(212, 175, 55, 0.45);
  animation-duration: 2.6s;
}
.o3::before { background: linear-gradient(135deg, #e8cf76, #b8860b); width: 8px; height: 8px; top: -4px; }

.load-seal {
  position: relative;
  width: 96px;
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.seal-ring {
  width: 100%;
  height: 100%;
  border-radius: 999px;
  background:
    conic-gradient(from 0deg, #d76f02, #d4af37, #1a3a7a, #d76f02);
  padding: 2px;
  animation: ringPulse 2s ease-in-out infinite;
  box-shadow:
    0 10px 30px rgba(215, 111, 2, 0.26),
    0 0 0 6px rgba(255, 255, 255, 0.65);
}

.seal-core {
  width: 100%;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(160deg, #1a3a7a 0%, #17336b 60%, #1a3a7a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.seal-lv {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 800;
  font-size: 2rem;
  letter-spacing: 0.08em;
  color: #d4af37;
  animation: lvBreath 2.2s ease-in-out infinite;
}

.load-copy {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
  min-width: 0;
  width: 100%;
  margin-top: 2px;
}

.load-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: #170b02;
}

.load-dots {
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #64748b;
  display: inline-flex;
  align-items: baseline;
  gap: 0;
}

.dots {
  display: inline-flex;
  gap: 1px;
  margin-left: 2px;
}

.dots > span {
  font-size: 1.1rem;
  line-height: 0.6;
  opacity: 0;
  animation: dotBlink 1.4s ease-in-out infinite;
  color: #d76f02;
  transform: translateY(1px);
  display: inline-block;
}
.d1 { animation-delay: 0s; }
.d2 { animation-delay: 0.18s; }
.d3 { animation-delay: 0.36s; }

.load-sub {
  font-size: 0.72rem;
  color: #94a3b8;
  letter-spacing: 0.01em;
  max-width: 22ch;
}

@keyframes orbSpin {
  to { transform: rotate(360deg); }
}

@keyframes ringPulse {
  0%, 100% { transform: scale(1); filter: saturate(1); }
  50% { transform: scale(1.05); filter: saturate(1.2); }
}

@keyframes lvBreath {
  0%, 100% { opacity: 1; transform: scale(1); text-shadow: 0 0 0 rgba(212, 175, 55, 0); }
  50% { opacity: 1; transform: scale(1.04); text-shadow: 0 0 16px rgba(212, 175, 55, 0.5); }
}

@keyframes dotBlink {
  0%, 100% { opacity: 0.1; transform: translateY(1px); }
  50% { opacity: 1; transform: translateY(-2px); }
}

.load-fade-enter-active,
.load-fade-leave-active {
  transition: opacity 320ms ease;
}
.load-fade-enter-from,
.load-fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .orb,
  .seal-ring,
  .seal-lv,
  .dots > span { animation: none !important; }
  .o1::before, .o2::before, .o3::before { display: none; }
}
</style>
