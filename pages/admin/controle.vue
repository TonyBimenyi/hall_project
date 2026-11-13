<!-- pages/admin/controle.vue -->
<template>
  <div class="controle-page">

    <!-- ══════════════════ HERO HEADER ══════════════════ -->
    <div class="ctrl-hero">
      <div class="ctrl-hero-left">
        <div class="ctrl-hero-badge"><i class="fas fa-clipboard-check"></i></div>
        <div>
          <h1 class="ctrl-hero-title">Contrôle <span>&amp;</span> Qualité</h1>
          <p class="ctrl-hero-sub">Checklists journalières, fiches de contrôle qualité et rapport de gestion</p>
        </div>
      </div>
      <div class="ctrl-hero-actions">
        <button class="ctrl-btn ctrl-btn-outline" @click="resetAll">
          <i class="fas fa-rotate-left"></i> Réinitialiser
        </button>
        <button class="ctrl-btn ctrl-btn-primary" @click="printPage">
          <i class="fas fa-print"></i> Imprimer
        </button>
      </div>
    </div>

    <!-- ══════════════════ SUMMARY CARDS ══════════════════ -->
    <div class="ctrl-stats">
      <div class="ctrl-stat-card">
        <div class="ctrl-stat-icon icon-blue"><i class="fas fa-clipboard-list"></i></div>
        <div class="ctrl-stat-info">
          <span class="ctrl-stat-label">Total éléments</span>
          <span class="ctrl-stat-value">{{ totalChecklists }}</span>
        </div>
      </div>
      <div class="ctrl-stat-card">
        <div class="ctrl-stat-icon icon-green"><i class="fas fa-circle-check"></i></div>
        <div class="ctrl-stat-info">
          <span class="ctrl-stat-label">Complétés</span>
          <span class="ctrl-stat-value text-green">{{ totalDone }}</span>
        </div>
      </div>
      <div class="ctrl-stat-card">
        <div class="ctrl-stat-icon icon-amber"><i class="fas fa-hourglass-half"></i></div>
        <div class="ctrl-stat-info">
          <span class="ctrl-stat-label">En attente</span>
          <span class="ctrl-stat-value text-amber">{{ totalPending }}</span>
        </div>
      </div>
      <div class="ctrl-stat-card">
        <div class="ctrl-stat-icon icon-purple"><i class="fas fa-gauge-high"></i></div>
        <div class="ctrl-stat-info">
          <span class="ctrl-stat-label">Progression globale</span>
          <span class="ctrl-stat-value text-purple">
            {{ totalChecklists ? Math.round(totalDone / totalChecklists * 100) : 0 }}%
          </span>
        </div>
      </div>
    </div>

    <!-- ══════════════════ META BAR ══════════════════ -->
    <div class="ctrl-meta card">
      <div class="ctrl-meta-field">
        <label><i class="fas fa-calendar-day"></i> Date</label>
        <input v-model="form.date" type="date" class="ctrl-input" />
      </div>
      <div class="ctrl-meta-field">
        <label><i class="fas fa-user-pen"></i> Nom du contrôleur</label>
        <input v-model="form.controleur" type="text" class="ctrl-input" placeholder="Votre nom…" />
      </div>
      <div class="ctrl-meta-field">
        <label><i class="fas fa-clock"></i> Session</label>
        <select v-model="form.session" class="ctrl-input">
          <option value="matin">Matin</option>
          <option value="apres_midi">Après-midi</option>
          <option value="soir">Soir</option>
          <option value="journee">Journée complète</option>
        </select>
      </div>
    </div>

    <!-- ══════════════════ PROGRESS BAR ══════════════════ -->
    <div class="ctrl-progress-bar card">
      <div class="ctrl-progress-info">
        <span class="ctrl-progress-label">
          <i class="fas fa-chart-line"></i> Progression — {{ activeTabLabel }}
        </span>
        <strong class="ctrl-progress-count">{{ activeProgress.done }} / {{ activeProgress.total }}</strong>
      </div>
      <div class="ctrl-progress-track">
        <div
          class="ctrl-progress-fill"
          :style="{ width: activeProgress.pct + '%' }"
          :class="{ 'fill-done': activeProgress.pct === 100 }"
        ></div>
      </div>
      <span class="ctrl-progress-pct">{{ activeProgress.pct }}%</span>
    </div>

    <!-- ══════════════════ TAB NAVIGATION ══════════════════ -->
    <div class="ctrl-tabs card">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['ctrl-tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        <i :class="tab.icon"></i>
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- ══════════════════ SALLE ══════════════════ -->
    <div v-if="activeTab === 'salle'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-champagne-glasses"></i>
        Checklist – Salle de réception (Jour de l'événement)
      </div>
      <div class="checklist-grid">
        <ChecklistGroup title="Avant événement" :items="checklists.salle.avant" @toggle="toggle('salle', 'avant', $event)" />
        <ChecklistGroup title="Pendant événement" :items="checklists.salle.pendant" @toggle="toggle('salle', 'pendant', $event)" />
        <ChecklistGroup title="Après événement" :items="checklists.salle.apres" @toggle="toggle('salle', 'apres', $event)" />
      </div>
    </div>

    <!-- ══════════════════ RÉCEPTION ══════════════════ -->
    <div v-if="activeTab === 'reception'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-concierge-bell"></i>
        Checklist – Réception
      </div>
      <div class="checklist-grid">
        <ChecklistGroup title="Ouverture" :items="checklists.reception.ouverture" @toggle="toggle('reception', 'ouverture', $event)" />
        <ChecklistGroup title="Accueil client" :items="checklists.reception.accueil" @toggle="toggle('reception', 'accueil', $event)" />
        <ChecklistGroup title="Durant la journée" :items="checklists.reception.journee" @toggle="toggle('reception', 'journee', $event)" />
        <ChecklistGroup title="Fermeture" :items="checklists.reception.fermeture" @toggle="toggle('reception', 'fermeture', $event)" />
      </div>
    </div>

    <!-- ══════════════════ HOUSEKEEPING ══════════════════ -->
    <div v-if="activeTab === 'housekeeping'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-broom"></i>
        Checklist – Housekeeping (Propreté)
      </div>

      <div class="hk-rooms-section">
        <div class="hk-rooms-title"><i class="fas fa-door-open"></i> Chambres</div>
        <div class="hk-rooms-grid">
          <div v-for="room in hkRooms" :key="room.number" class="hk-room-card card">
            <div class="hk-room-head">
              <span class="hk-room-number">{{ room.number }}</span>
              <span :class="['hk-room-status', hkRoomStatus(room)]">
                <i :class="hkRoomStatusIcon(room)"></i> {{ hkRoomStatusLabel(room) }}
              </span>
            </div>
            <div class="hk-checklist">
              <label v-for="item in hkRoomItems" :key="item" class="hk-item">
                <input v-model="room.checks[item]" type="checkbox" />
                <span>{{ item }}</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <div class="checklist-grid" style="margin-top: var(--space-4)">
        <ChecklistGroup title="Espaces communs" :items="checklists.housekeeping.communs" @toggle="toggle('housekeeping', 'communs', $event)" />
        <ChecklistGroup title="Contrôle final" :items="checklists.housekeeping.controle_final" @toggle="toggle('housekeeping', 'controle_final', $event)" />
      </div>
    </div>

    <!-- ══════════════════ CUISINE ══════════════════ -->
    <div v-if="activeTab === 'cuisine'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-utensils"></i>
        Checklist – Cuisine / Restauration
      </div>
      <div class="checklist-grid">
        <ChecklistGroup title="Avant service" :items="checklists.cuisine.avant" @toggle="toggle('cuisine', 'avant', $event)" />
        <ChecklistGroup title="Pendant service" :items="checklists.cuisine.pendant" @toggle="toggle('cuisine', 'pendant', $event)" />
        <ChecklistGroup title="Après service" :items="checklists.cuisine.apres" @toggle="toggle('cuisine', 'apres', $event)" />
      </div>
    </div>

    <!-- ══════════════════ SÉCURITÉ ══════════════════ -->
    <div v-if="activeTab === 'securite'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-shield-halved"></i>
        Checklist – Sécurité
      </div>
      <div class="checklist-grid">
        <ChecklistGroup title="Surveillance" :items="checklists.securite.surveillance" @toggle="toggle('securite', 'surveillance', $event)" />
        <ChecklistGroup title="Incidents" :items="checklists.securite.incidents" @toggle="toggle('securite', 'incidents', $event)" />
      </div>
    </div>

    <!-- ══════════════════ GÉRANT ══════════════════ -->
    <div v-if="activeTab === 'gerant'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-user-tie"></i>
        Checklist – Gérant (Quotidien)
      </div>
      <div class="checklist-grid">
        <ChecklistGroup title="Points à valider" :items="checklists.gerant.daily" @toggle="toggle('gerant', 'daily', $event)" />
      </div>
    </div>

    <!-- ══════════════════ QUALITÉ ══════════════════ -->
    <div v-if="activeTab === 'qualite'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-clipboard-check"></i>
        Fiche – Contrôle Qualité Journalier
      </div>

      <div class="qualite-grid">
        <div v-for="zone in qualiteZones" :key="zone.key" class="qualite-row card">
          <div class="qualite-zone">{{ zone.label }}</div>
          <div class="qualite-etat">
            <label class="qualite-opt ok">
              <input type="radio" :name="`zone_${zone.key}`" value="ok" v-model="qualiteForm[zone.key].etat" />
              <i class="fas fa-circle-check"></i> OK
            </label>
            <label class="qualite-opt nok">
              <input type="radio" :name="`zone_${zone.key}`" value="nok" v-model="qualiteForm[zone.key].etat" />
              <i class="fas fa-circle-xmark"></i> NOK
            </label>
          </div>
          <div class="qualite-obs">
            <input type="text" v-model="qualiteForm[zone.key].obs" class="ctrl-input" placeholder="Observations…" />
          </div>
        </div>
      </div>

      <div class="appreciation-bar card">
        <strong>Appréciation globale :</strong>
        <label
          v-for="lvl in appreciations"
          :key="lvl.value"
          :class="['appr-opt', lvl.cls, { active: qualiteGlobal === lvl.value }]"
        >
          <input type="radio" :value="lvl.value" v-model="qualiteGlobal" />
          <i :class="lvl.icon"></i> {{ lvl.label }}
        </label>
      </div>

      <div class="ctrl-section-title" style="margin-top: var(--space-6)">
        <i class="fas fa-soap"></i>
        Fiche – Contrôle Propreté Détaillé
      </div>
      <div class="proprete-grid">
        <div v-for="zone in propreteZones" :key="zone" class="proprete-item card">
          <div class="proprete-zone">{{ zone }}</div>
          <div class="proprete-checks">
            <label :class="['prp-opt', { ok: propreteForm[zone] === 'conforme' }]">
              <input type="radio" :name="`prp_${zone}`" value="conforme" v-model="propreteForm[zone]" />
              <span>Conforme</span>
            </label>
            <label :class="['prp-opt', { nok: propreteForm[zone] === 'non_conforme' }]">
              <input type="radio" :name="`prp_${zone}`" value="non_conforme" v-model="propreteForm[zone]" />
              <span>Non conforme</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════ SATISFACTION ══════════════════ -->
    <div v-if="activeTab === 'satisfaction'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-face-smile"></i>
        Fiche – Satisfaction Client
      </div>
      <div class="satisfaction-form card">
        <div class="sat-row">
          <strong>Note :</strong>
          <label
            v-for="lvl in satisfactionLevels"
            :key="lvl.value"
            :class="['sat-opt', lvl.cls, { active: satForm.note === lvl.value }]"
          >
            <input type="radio" :value="lvl.value" v-model="satForm.note" />
            <i :class="lvl.icon"></i> {{ lvl.label }}
          </label>
        </div>
        <div class="sat-row">
          <strong>Service reçu :</strong>
          <input type="text" v-model="satForm.service" class="ctrl-input" placeholder="Description du service…" />
        </div>
        <div class="sat-row">
          <strong>Remarques client :</strong>
          <textarea v-model="satForm.remarques" class="ctrl-textarea" rows="3" placeholder="Remarques éventuelles…"></textarea>
        </div>
        <div class="sat-row">
          <strong>Responsable :</strong>
          <input type="text" v-model="satForm.responsable" class="ctrl-input" placeholder="Nom du responsable…" />
        </div>
      </div>
    </div>

    <!-- ══════════════════ RAPPORT ══════════════════ -->
    <div v-if="activeTab === 'rapport'" class="ctrl-section">
      <div class="ctrl-section-title">
        <i class="fas fa-file-lines"></i>
        Fiche – Rapport Journalier de Gestion
      </div>
      <div class="rapport-form card">
        <div class="rapport-grid">
          <div class="rpt-field">
            <label>Nombre de clients</label>
            <input type="number" v-model="rapportForm.nb_clients" class="ctrl-input" min="0" />
          </div>
          <div class="rpt-field">
            <label>Taux d'occupation (%)</label>
            <input type="number" v-model="rapportForm.taux_occupation" class="ctrl-input" min="0" max="100" />
          </div>
          <div class="rpt-field">
            <label>Événements</label>
            <input type="number" v-model="rapportForm.evenements" class="ctrl-input" min="0" />
          </div>
          <div class="rpt-field">
            <label>Incidents</label>
            <input type="number" v-model="rapportForm.incidents" class="ctrl-input" min="0" />
          </div>
        </div>
        <div class="rpt-field" style="margin-top: var(--space-3)">
          <strong>Situation globale :</strong>
          <div class="situation-opts">
            <label
              v-for="sit in situations"
              :key="sit.value"
              :class="['sit-opt', sit.cls, { active: rapportForm.situation === sit.value }]"
            >
              <input type="radio" :value="sit.value" v-model="rapportForm.situation" />
              <i :class="sit.icon"></i> {{ sit.label }}
            </label>
          </div>
        </div>
        <div class="rpt-field" style="margin-top: var(--space-3)">
          <label>Décisions prises</label>
          <textarea v-model="rapportForm.decisions" class="ctrl-textarea" rows="4" placeholder="Décisions, actions à mener…"></textarea>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, defineComponent } from 'vue'

definePageMeta({ layout: 'admin' })

const ChecklistGroup = defineComponent({
  name: 'ChecklistGroup',
  props: {
    title: { type: String, default: '' },
    items: { type: Array, default: () => [] },
  },
  emits: ['toggle'],
  template: `
    <div class="checklist-group card">
      <div class="cg-title"><i class="fas fa-caret-right cg-title-icon"></i> {{ title }}</div>
      <label
        v-for="(item, idx) in items"
        :key="idx"
        :class="['cg-item', { done: item.done }]"
        @click.prevent="$emit('toggle', idx)"
      >
        <span class="cg-box">
          <i v-if="item.done" class="fas fa-square-check"></i>
          <i v-else class="far fa-square"></i>
        </span>
        <span class="cg-label">{{ item.label }}</span>
      </label>
    </div>
  `,
})

// ─── Meta ────────────────────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10)
const form = reactive({ date: today, controleur: '', session: 'journee' })

// ─── Tabs ─────────────────────────────────────────────────────────────────────
const tabs = [
  { id: 'salle',       label: 'Salle',        icon: 'fas fa-champagne-glasses' },
  { id: 'reception',   label: 'Réception',    icon: 'fas fa-concierge-bell' },
  { id: 'housekeeping',label: 'Housekeeping', icon: 'fas fa-broom' },
  { id: 'cuisine',     label: 'Cuisine',      icon: 'fas fa-utensils' },
  { id: 'securite',    label: 'Sécurité',     icon: 'fas fa-shield-halved' },
  { id: 'gerant',      label: 'Gérant',       icon: 'fas fa-user-tie' },
  { id: 'qualite',     label: 'Qualité',      icon: 'fas fa-clipboard-check' },
  { id: 'satisfaction',label: 'Satisfaction', icon: 'fas fa-face-smile' },
  { id: 'rapport',     label: 'Rapport',      icon: 'fas fa-file-lines' },
]

const activeTab = ref('salle')
const activeTabLabel = computed(() => tabs.find(t => t.id === activeTab.value)?.label || '')

// ─── Checklist factory ────────────────────────────────────────────────────────
const mkItems = (labels) => reactive(labels.map(l => ({ label: l, done: false })))

const checklists = reactive({
  salle: {
    avant:   mkItems(['Toilettes nettoyées', 'Sonorisation testée', 'Chaises propres', 'Tables installées', 'Décoration prête', 'Boissons disponibles']),
    pendant: mkItems(['Accueil organisé', 'Personnel présent et au service des clients', 'Porte Jardin fermée', 'Suivi du déroulement', 'Ronde de nettoyage Toilettes']),
    apres:   mkItems(['Nettoyage complet', 'Inventaire matériel', 'Inventaire boissons', "Rapport d'événement"]),
  },
  reception: {
    ouverture: mkItems(['Poste propre et organisé', 'Registre de réservation à jour', 'Téléphone fonctionnel', 'Clés disponibles']),
    accueil:   mkItems(['Sourire et salutation systématique', 'Vérification réservation', 'Enregistrement client complet', 'Explication claire des services']),
    journee:   mkItems(['Réservations mises à jour', 'Réponse rapide aux appels', 'Demandes clients traitées']),
    fermeture: mkItems(['Caisse équilibrée', 'Registre mis à jour', 'Rapport journalier transmis']),
  },
  housekeeping: {
    communs: mkItems([
      'Cuisine nettoyée', 'Couloirs étage nettoyés', 'Escaliers nettoyés',
      'Petite salle VIP BIMBO VIP Residence Hall impeccable',
      'Couloirs Rez-de-chaussée nettoyés', 'Cour Hôtel propre', 'Espace linge propre',
      'Nettoyage linge', 'Grande cour propre',
      'Grande Salle LaGombo Conference Hall impeccable',
      "Jardin Matrona Garden propre", 'Parking Extérieur propre',
      "Petite salle Back'Lea Conference Hall propre",
    ]),
    controle_final: mkItems(['Aucune trace de déchet visible', 'Aucun oubli', 'Vérification par superviseur']),
  },
  cuisine: {
    avant:   mkItems(['Mains lavées', 'Plan de travail propre', 'Ingrédients disponibles', 'Tenue propre']),
    pendant: mkItems(['Respect hygiène', 'Cuisson correcte', 'Présentation soignée', 'Rapidité du service']),
    apres:   mkItems(['Cuisine nettoyée', 'Déchets évacués', 'Stock mis à jour']),
  },
  securite: {
    surveillance: mkItems(['Accès contrôlé', 'Ronde effectuée', 'Parking sécurisé']),
    incidents:    mkItems(['Intervention rapide', 'Gérant informé', 'Rapport rédigé']),
  },
  gerant: {
    daily: mkItems([
      'Inspection générale faite', 'Personnel présent et discipliné',
      'Réservations vérifiées', 'Propreté validée', 'Cuisine contrôlée',
      'Événements suivis', 'Caisse vérifiée', 'Clients satisfaits',
    ]),
  },
})

const toggle = (section, group, idx) => {
  checklists[section][group][idx].done = !checklists[section][group][idx].done
}

// ─── Housekeeping chambres ────────────────────────────────────────────────────
const hkRoomItems = [
  'Lit bien fait (draps propres)',
  'Sol propre',
  'Salle de bain désinfectée',
  'Odeur agréable',
  'Poubelles vidées',
  'Meubles et appareils nettoyés',
  'Vitres et Murs nettoyés',
]
const hkRoomNumbers = ['100','101','102','103','104','200','201','202','203','204','VIP1','VIP2']
const hkRooms = reactive(hkRoomNumbers.map(n => ({
  number: n,
  checks: Object.fromEntries(hkRoomItems.map(i => [i, false])),
})))

const hkRoomStatus = (room) => {
  const vals = Object.values(room.checks)
  const done = vals.filter(Boolean).length
  if (done === 0) return 'pending'
  if (done === vals.length) return 'done'
  return 'partial'
}
const hkRoomStatusLabel = (room) => {
  const s = hkRoomStatus(room)
  if (s === 'done') return 'Terminé'
  if (s === 'partial') return 'En cours'
  return 'À faire'
}
const hkRoomStatusIcon = (room) => {
  const s = hkRoomStatus(room)
  if (s === 'done') return 'fas fa-circle-check'
  if (s === 'partial') return 'fas fa-spinner'
  return 'far fa-square'
}

// ─── Qualité zones ────────────────────────────────────────────────────────────
const qualiteZones = [
  { key: 'reception',   label: 'Réception' },
  { key: 'chambres',    label: 'Chambres' },
  { key: 'sanitaires',  label: 'Sanitaires' },
  { key: 'cuisine',     label: 'Cuisine' },
  { key: 'salle_recep', label: 'Salle réception' },
  { key: 'exterieurs',  label: 'Extérieurs' },
]
const qualiteForm = reactive(Object.fromEntries(qualiteZones.map(z => [z.key, { etat: '', obs: '' }])))
const qualiteGlobal = ref('')
const appreciations = [
  { value: 'excellent',    label: 'Excellent',    cls: 'excellent',    icon: 'fas fa-circle-check' },
  { value: 'bon',          label: 'Bon',          cls: 'bon',          icon: 'fas fa-thumbs-up' },
  { value: 'ameliorer',   label: 'À améliorer',  cls: 'ameliorer',    icon: 'fas fa-triangle-exclamation' },
  { value: 'inacceptable', label: 'Inacceptable', cls: 'inacceptable', icon: 'fas fa-ban' },
]

// ─── Propreté détaillée ───────────────────────────────────────────────────────
const propreteZones = [
  'Grande salle', 'Petite salle', 'Petite Salle VIP',
  'Toilettes Hommes grande salle', 'Toilettes Femmes grande salle',
  'Toilette Hommes petite salle', 'Toilette Femmes petite salle',
  'Cour devant les Chambres en étage', 'Escalier droit', 'Escalier gauche',
  'Corridor étage', 'Corridor Rez-de-chaussée', 'Cour devant grande salle',
  'Parking extérieur', 'Réception', 'Cuisine', 'Restaurant', 'Veranda Restaurant',
  'Corridor chambres arrières', 'Escalier arrière', 'Toilette visiteurs VIP',
  'Corridors résidence', 'Espace Linge', 'Toilettes arrières', 'Corridor cuisine',
]
const propreteForm = reactive(Object.fromEntries(propreteZones.map(z => [z, ''])))

// ─── Satisfaction ─────────────────────────────────────────────────────────────
const satisfactionLevels = [
  { value: 'tres_satisfait', label: 'Très satisfait', cls: 'excellent',    icon: 'fas fa-face-grin-stars' },
  { value: 'satisfait',      label: 'Satisfait',       cls: 'bon',          icon: 'fas fa-face-smile' },
  { value: 'moyen',          label: 'Moyen',           cls: 'ameliorer',    icon: 'fas fa-face-meh' },
  { value: 'insatisfait',    label: 'Insatisfait',     cls: 'inacceptable', icon: 'fas fa-face-frown' },
]
const satForm = reactive({ note: '', service: '', remarques: '', responsable: '' })

// ─── Rapport journalier ───────────────────────────────────────────────────────
const situations = [
  { value: 'bonne',    label: 'Bonne',   cls: 'excellent',    icon: 'fas fa-circle-check' },
  { value: 'moyenne',  label: 'Moyenne', cls: 'ameliorer',    icon: 'fas fa-circle-half-stroke' },
  { value: 'critique', label: 'Critique',cls: 'inacceptable', icon: 'fas fa-circle-exclamation' },
]
const rapportForm = reactive({ nb_clients: '', taux_occupation: '', evenements: '', incidents: '', situation: '', decisions: '' })

// ─── Totals ───────────────────────────────────────────────────────────────────
const totalChecklists = computed(() =>
  Object.values(checklists).reduce(
    (total, section) => total + Object.values(section).reduce((sum, group) => sum + group.length, 0),
    0
  ) + hkRooms.length * hkRoomItems.length
)
const totalDone = computed(() =>
  Object.values(checklists).reduce(
    (total, section) => total + Object.values(section).reduce((sum, group) => sum + group.filter(item => item.done).length, 0),
    0
  ) + hkRooms.reduce((sum, room) => sum + Object.values(room.checks).filter(Boolean).length, 0)
)
const totalPending = computed(() => totalChecklists.value - totalDone.value)

// ─── Progress ─────────────────────────────────────────────────────────────────
const countSection = (section) => {
  const groups = Object.values(checklists[section] || {})
  const total = groups.reduce((s, g) => s + g.length, 0)
  const done  = groups.reduce((s, g) => s + g.filter(i => i.done).length, 0)
  return { total, done }
}

const activeProgress = computed(() => {
  const tab = activeTab.value
  if (['salle','reception','housekeeping','cuisine','securite','gerant'].includes(tab)) {
    const { total, done } = countSection(tab)
    return { total, done, pct: total ? Math.round(done / total * 100) : 0 }
  }
  if (tab === 'qualite') {
    const total = qualiteZones.length + propreteZones.length
    const done  = qualiteZones.filter(z => qualiteForm[z.key].etat).length
                + propreteZones.filter(z => propreteForm[z]).length
    return { total, done, pct: total ? Math.round(done / total * 100) : 0 }
  }
  if (tab === 'satisfaction') {
    const fields = [satForm.note, satForm.service, satForm.remarques, satForm.responsable]
    const done = fields.filter(f => !!f).length
    return { total: 4, done, pct: Math.round(done / 4 * 100) }
  }
  if (tab === 'rapport') {
    const fields = [rapportForm.nb_clients, rapportForm.taux_occupation, rapportForm.evenements, rapportForm.incidents, rapportForm.situation, rapportForm.decisions]
    const done = fields.filter(f => f !== '' && f !== null && f !== undefined).length
    return { total: 6, done, pct: Math.round(done / 6 * 100) }
  }
  return { total: 0, done: 0, pct: 0 }
})

// ─── Reset ────────────────────────────────────────────────────────────────────
const resetAll = () => {
  if (!confirm('Réinitialiser tous les champs de cette session ?')) return
  Object.keys(checklists).forEach(sec => {
    Object.values(checklists[sec]).forEach(group => group.forEach(item => { item.done = false }))
  })
  hkRooms.forEach(room => hkRoomItems.forEach(i => { room.checks[i] = false }))
  qualiteZones.forEach(z => { qualiteForm[z.key] = { etat: '', obs: '' } })
  propreteZones.forEach(z => { propreteForm[z] = '' })
  qualiteGlobal.value = ''
  Object.assign(satForm, { note: '', service: '', remarques: '', responsable: '' })
  Object.assign(rapportForm, { nb_clients: '', taux_occupation: '', evenements: '', incidents: '', situation: '', decisions: '' })
}

// ─── Print ────────────────────────────────────────────────────────────────────
const printPage = () => window.print()
</script>

<style scoped>
/* ══════════════════════════════════════════════════════════════════════════════
   PAGE LAYOUT
══════════════════════════════════════════════════════════════════════════════ */
.controle-page {
  padding: var(--space-4) var(--space-5);
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* ══════════════════════════════════════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════════════════════════════════════ */
.ctrl-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  background: linear-gradient(135deg, #1a1f36 0%, #12192b 100%);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: var(--space-4) var(--space-5);
  position: relative;
  overflow: hidden;
}
.ctrl-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at top right, rgba(251,146,60,0.15) 0%, transparent 60%);
  pointer-events: none;
}
.ctrl-hero-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  position: relative;
}
.ctrl-hero-badge {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #f97316, #ea580c);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(249,115,22,0.4);
}
.ctrl-hero-title {
  font-size: 1.75rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 4px;
  letter-spacing: -0.5px;
}
.ctrl-hero-title span { color: #f97316; }
.ctrl-hero-sub {
  font-size: 0.875rem;
  color: rgba(255,255,255,0.55);
  margin: 0;
}
.ctrl-hero-actions {
  display: flex;
  gap: var(--space-2);
  flex-wrap: wrap;
  position: relative;
}

/* Buttons */
.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  border: none;
}
.ctrl-btn-primary {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: white;
  box-shadow: 0 2px 8px rgba(249,115,22,0.35);
}
.ctrl-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(249,115,22,0.45); }
.ctrl-btn-outline {
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.85);
  border: 1px solid rgba(255,255,255,0.15);
}
.ctrl-btn-outline:hover { background: rgba(255,255,255,0.14); }

/* ══════════════════════════════════════════════════════════════════════════════
   STATS CARDS
══════════════════════════════════════════════════════════════════════════════ */
.ctrl-stats {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-3);
}
.ctrl-stat-card {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: transform 0.15s, box-shadow 0.15s;
}
.ctrl-stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.ctrl-stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.icon-blue   { background: rgba(59,130,246,0.15); color: #3b82f6; }
.icon-green  { background: rgba(34,197,94,0.15);  color: #22c55e; }
.icon-amber  { background: rgba(245,158,11,0.15); color: #f59e0b; }
.icon-purple { background: rgba(168,85,247,0.15); color: #a855f7; }
.ctrl-stat-info { display: flex; flex-direction: column; gap: 2px; }
.ctrl-stat-label { font-size: 0.75rem; color: var(--text-secondary); font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }
.ctrl-stat-value { font-size: 1.5rem; font-weight: 700; color: var(--text); line-height: 1; }
.text-green  { color: #22c55e; }
.text-amber  { color: #f59e0b; }
.text-purple { color: #a855f7; }

/* ══════════════════════════════════════════════════════════════════════════════
   META BAR
══════════════════════════════════════════════════════════════════════════════ */
.ctrl-meta {
  display: flex;
  gap: var(--space-4);
  flex-wrap: wrap;
  padding: var(--space-4) var(--space-5);
  align-items: flex-end;
  border-radius: 14px;
}
.ctrl-meta-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 170px;
  flex: 1;
}
.ctrl-meta-field label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 5px;
}
.ctrl-input {
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.ctrl-input:focus {
  outline: none;
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249,115,22,0.15);
}
.ctrl-textarea {
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  color: var(--text);
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  transition: border-color 0.15s;
}
.ctrl-textarea:focus { outline: none; border-color: #f97316; }

/* ══════════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════════════════════════════════════ */
.ctrl-progress-bar {
  padding: var(--space-3) var(--space-5);
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}
.ctrl-progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-width: 200px;
  flex: 1;
}
.ctrl-progress-label { font-size: 0.875rem; color: var(--text-secondary); }
.ctrl-progress-label i { color: #f97316; }
.ctrl-progress-count { font-weight: 700; color: var(--text); font-size: 0.875rem; }
.ctrl-progress-track {
  flex: 3;
  height: 10px;
  background: var(--border);
  border-radius: 999px;
  overflow: hidden;
  min-width: 100px;
}
.ctrl-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f97316, #ea580c);
  border-radius: 999px;
  transition: width 0.4s ease;
}
.ctrl-progress-fill.fill-done { background: linear-gradient(90deg, #22c55e, #16a34a); }
.ctrl-progress-pct {
  font-weight: 700;
  font-size: 0.875rem;
  color: #f97316;
  min-width: 36px;
  text-align: right;
}

/* ══════════════════════════════════════════════════════════════════════════════
   TAB NAVIGATION
══════════════════════════════════════════════════════════════════════════════ */
.ctrl-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: var(--space-2) var(--space-3);
  border-radius: 14px;
}
.ctrl-tab-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.8375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.ctrl-tab-btn:hover {
  background: var(--bg-hover);
  color: var(--text);
  border-color: var(--border-hover, var(--border));
}
.ctrl-tab-btn.active {
  background: linear-gradient(135deg, #f97316, #ea580c);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 2px 8px rgba(249,115,22,0.3);
}

/* ══════════════════════════════════════════════════════════════════════════════
   SECTION
══════════════════════════════════════════════════════════════════════════════ */
.ctrl-section { display: flex; flex-direction: column; gap: var(--space-3); }
.ctrl-section-title {
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 10px;
}
.ctrl-section-title i { color: #f97316; }

/* ══════════════════════════════════════════════════════════════════════════════
   CHECKLIST GROUP
══════════════════════════════════════════════════════════════════════════════ */
.checklist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-3);
}
:deep(.checklist-group) {
  padding: var(--space-3);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
:deep(.cg-title) {
  font-size: 0.8125rem;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: var(--space-2);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
:deep(.cg-item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.12s;
  user-select: none;
}
:deep(.cg-item:hover) { background: var(--bg-hover); }
:deep(.cg-item.done .cg-label) { text-decoration: line-through; color: var(--text-secondary); }
:deep(.cg-box) { font-size: 1rem; color: #f97316; min-width: 18px; }
:deep(.cg-item.done .cg-box) { color: #22c55e; }
:deep(.cg-label) { font-size: 0.875rem; color: var(--text); }

/* ══════════════════════════════════════════════════════════════════════════════
   HOUSEKEEPING ROOMS
══════════════════════════════════════════════════════════════════════════════ */
.hk-rooms-section { margin-bottom: var(--space-2); }
.hk-rooms-title { font-size: 0.9rem; font-weight: 700; color: var(--text-secondary); margin-bottom: var(--space-2); }
.hk-rooms-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--space-3); }
.hk-room-card { padding: var(--space-3); border-radius: 14px; }
.hk-room-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-2); }
.hk-room-number { font-size: 1rem; font-weight: 700; color: var(--text); }
.hk-room-status { font-size: 0.72rem; padding: 3px 10px; border-radius: 999px; font-weight: 600; }
.hk-room-status.pending  { background: rgba(100,100,120,0.15); color: var(--text-secondary); }
.hk-room-status.partial  { background: rgba(245,158,11,0.15); color: #d97706; }
.hk-room-status.done     { background: rgba(34,197,94,0.15);  color: #16a34a; }
.hk-checklist { display: flex; flex-direction: column; gap: 4px; }
.hk-item { display: flex; align-items: center; gap: 8px; font-size: 0.8125rem; color: var(--text); cursor: pointer; padding: 3px 0; }
.hk-item input { accent-color: #f97316; }

/* ══════════════════════════════════════════════════════════════════════════════
   QUALITÉ
══════════════════════════════════════════════════════════════════════════════ */
.qualite-grid { display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-3); }
.qualite-row { display: grid; grid-template-columns: 160px auto 1fr; align-items: center; gap: var(--space-3); padding: var(--space-2) var(--space-3); border-radius: 12px; }
.qualite-zone { font-weight: 600; font-size: 0.875rem; }
.qualite-etat { display: flex; gap: var(--space-2); }
.qualite-opt { display: flex; align-items: center; gap: 5px; font-size: 0.875rem; cursor: pointer; padding: 4px 10px; border-radius: 8px; }
.qualite-opt.ok  { background: rgba(34,197,94,0.1);  color: #16a34a; }
.qualite-opt.nok { background: rgba(239,68,68,0.1);  color: #dc2626; }
.qualite-opt input { accent-color: currentColor; }

.appreciation-bar { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; padding: var(--space-3) var(--space-4); border-radius: 14px; }
.appr-opt { display: flex; align-items: center; gap: 6px; font-size: 0.875rem; font-weight: 600; padding: 6px 14px; border-radius: 10px; cursor: pointer; border: 2px solid transparent; transition: all 0.15s; }
.appr-opt:has(input:checked), .appr-opt.active { border-color: currentColor; }
.appr-opt.excellent    { background: rgba(34,197,94,0.1);  color: #16a34a; }
.appr-opt.bon          { background: rgba(59,130,246,0.1); color: #2563eb; }
.appr-opt.ameliorer    { background: rgba(245,158,11,0.1); color: #d97706; }
.appr-opt.inacceptable { background: rgba(239,68,68,0.1);  color: #dc2626; }
.appr-opt input { display: none; }

.proprete-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: var(--space-2); }
.proprete-item { padding: var(--space-2) var(--space-3); display: flex; justify-content: space-between; align-items: center; gap: var(--space-2); border-radius: 10px; }
.proprete-zone { font-size: 0.8125rem; color: var(--text); flex: 1; }
.proprete-checks { display: flex; gap: 6px; }
.prp-opt { font-size: 0.75rem; padding: 4px 10px; border-radius: 8px; cursor: pointer; border: 1px solid var(--border); background: var(--bg); color: var(--text-secondary); transition: all 0.12s; }
.prp-opt:has(input:checked).ok  { background: rgba(34,197,94,0.1);  color: #16a34a; border-color: #86efac; }
.prp-opt:has(input:checked).nok { background: rgba(239,68,68,0.1);  color: #dc2626; border-color: #fca5a5; }
.prp-opt input { display: none; }

/* ══════════════════════════════════════════════════════════════════════════════
   SATISFACTION
══════════════════════════════════════════════════════════════════════════════ */
.satisfaction-form { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); border-radius: 14px; }
.sat-row { display: flex; align-items: flex-start; gap: var(--space-3); flex-wrap: wrap; }
.sat-row strong { min-width: 130px; font-size: 0.875rem; padding-top: 8px; }
.sat-opt { display: flex; align-items: center; gap: 6px; font-size: 0.875rem; font-weight: 600; padding: 7px 14px; border-radius: 10px; cursor: pointer; border: 2px solid transparent; transition: all 0.15s; }
.sat-opt:has(input:checked), .sat-opt.active { border-color: currentColor; }
.sat-opt.excellent    { background: rgba(34,197,94,0.1);  color: #16a34a; }
.sat-opt.bon          { background: rgba(59,130,246,0.1); color: #2563eb; }
.sat-opt.ameliorer    { background: rgba(245,158,11,0.1); color: #d97706; }
.sat-opt.inacceptable { background: rgba(239,68,68,0.1);  color: #dc2626; }
.sat-opt input { display: none; }

/* ══════════════════════════════════════════════════════════════════════════════
   RAPPORT
══════════════════════════════════════════════════════════════════════════════ */
.rapport-form { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-3); border-radius: 14px; }
.rapport-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--space-3); }
.rpt-field { display: flex; flex-direction: column; gap: 6px; }
.rpt-field label, .rpt-field strong { font-size: 0.8125rem; font-weight: 600; color: var(--text-secondary); }
.situation-opts { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 6px; }
.sit-opt { display: flex; align-items: center; gap: 6px; font-size: 0.875rem; font-weight: 600; padding: 7px 16px; border-radius: 10px; cursor: pointer; border: 2px solid transparent; transition: all 0.15s; }
.sit-opt:has(input:checked), .sit-opt.active { border-color: currentColor; }
.sit-opt.excellent    { background: rgba(34,197,94,0.1);  color: #16a34a; }
.sit-opt.ameliorer    { background: rgba(245,158,11,0.1); color: #d97706; }
.sit-opt.inacceptable { background: rgba(239,68,68,0.1);  color: #dc2626; }
.sit-opt input { display: none; }

/* ══════════════════════════════════════════════════════════════════════════════
   PRINT
══════════════════════════════════════════════════════════════════════════════ */
@media print {
  .ctrl-hero-actions,
  .ctrl-tabs,
  .ctrl-progress-bar { display: none !important; }
  .checklist-grid  { grid-template-columns: repeat(2, 1fr); }
  .proprete-grid   { grid-template-columns: repeat(2, 1fr); }
  .hk-rooms-grid   { grid-template-columns: repeat(3, 1fr); }
  .rapport-grid    { grid-template-columns: repeat(2, 1fr); }
}
</style>
