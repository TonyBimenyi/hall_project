<!-- pages/admin/controle.vue -->
<template>
  <div class="ctrl">

    <!-- ═════════ HEADER ═════════ -->
    <header class="hero">
      <div class="hero-top">
        <div class="hero-title">
          <span class="hero-badge"><i class="fas fa-clipboard-check"></i></span>
          <div>
            <h1>Contrôle et qualité</h1>
            <p>Checklists du jour, fiches qualité et rapport de gestion</p>
          </div>
        </div>
        <div class="hero-actions no-print">
          <button class="btn btn-brass" type="button" :disabled="saving" @click="saveControle">
            <i :class="saving ? 'fas fa-spinner fa-spin' : 'fas fa-floppy-disk'"></i>
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
          <button class="btn btn-ghost" @click="resetAll"><i class="fas fa-rotate-left"></i> Réinitialiser</button>
          <button class="btn btn-brass" @click="printPage"><i class="fas fa-print"></i> Imprimer</button>
        </div>
      </div>

      <div class="hero-progress">
        <div class="hp-figures">
          <div><strong>{{ totalDone }}</strong><span>validés</span></div>
          <div><strong>{{ totalPending }}</strong><span>en attente</span></div>
          <div><strong>{{ totalChecklists }}</strong><span>points de contrôle</span></div>
        </div>
        <div class="hp-bar">
          <div class="hp-track"><div class="hp-fill" :style="{ width: globalPct + '%' }"></div></div>
          <b>{{ globalPct }}%</b>
        </div>
      </div>
    </header>

    <!-- ═════════ META ═════════ -->
    <section class="panel meta">
      <label class="field">
        <span><i class="fas fa-calendar-day"></i> Date</span>
        <input v-model="form.date" type="date" class="input" />
      </label>
      <label class="field grow">
        <span><i class="fas fa-user-pen"></i> Contrôleur</span>
        <input :value="controleurName" type="text" class="input" readonly />
      </label>
      <label class="field">
        <span><i class="fas fa-clock"></i> Session</span>
        <select v-model="form.session" class="input">
          <option value="matin">Matin</option>
          <option value="apres_midi">Après-midi</option>
          <option value="soir">Soir</option>
          <option value="journee">Journée complète</option>
        </select>
      </label>
    </section>

    <section class="panel history no-print">
      <header class="history-head">
        <div>
          <h2>Historique des contrôles</h2>
          <p>Rechercher les contrôles par date ou par contrôleur.</p>
        </div>
        <button class="btn btn-ghost history-refresh" type="button" :disabled="loadingHistory" @click="fetchHistory">
          <i :class="loadingHistory ? 'fas fa-spinner fa-spin' : 'fas fa-rotate'"></i>
          Actualiser
        </button>
      </header>
      <form class="history-filters" @submit.prevent="fetchHistory">
        <label class="field">
          <span><i class="fas fa-calendar-day"></i> Date</span>
          <input v-model="historyFilters.date" type="date" class="input" />
        </label>
        <label class="field grow">
          <span><i class="fas fa-user-pen"></i> Contrôleur</span>
          <input v-model="historyFilters.controleur" type="search" class="input" placeholder="Nom du contrôleur" />
        </label>
        <div class="history-filter-actions">
          <button class="btn btn-brass" type="submit" :disabled="loadingHistory">
            <i class="fas fa-magnifying-glass"></i> Rechercher
          </button>
          <button class="btn btn-outline" type="button" :disabled="loadingHistory" @click="clearHistoryFilters">
            Effacer
          </button>
        </div>
      </form>

      <p v-if="loadingHistory" class="history-empty">Chargement de l’historique…</p>
      <p v-else-if="!historyRecords.length" class="history-empty">Aucun contrôle trouvé.</p>
      <div v-else class="history-list">
        <details v-for="record in historyRecords" :key="record.id" class="history-record">
          <summary>
            <span class="history-record-date">{{ record.date }}</span>
            <span>{{ record.controleur || 'Contrôleur inconnu' }}</span>
            <span class="history-session">{{ sessionLabel(record.session) }}</span>
            <i class="fas fa-chevron-down"></i>
          </summary>
          <div class="history-details">
            <div v-for="(groups, section) in record.data?.checklists || {}" :key="section" class="history-section">
              <h3>{{ sectionLabel(section) }}</h3>
              <div v-for="(items, group) in groups" :key="group" class="history-group">
                <h4>{{ group }}</h4>
                <ul>
                  <li v-for="(item, index) in items" :key="index">
                    <i :class="item.done ? 'fas fa-circle-check history-done' : 'far fa-circle'"></i>
                    {{ item.label }}
                  </li>
                </ul>
              </div>
            </div>
            <div v-if="record.data?.chambres?.length" class="history-section">
              <h3>Chambres</h3>
              <p v-for="room in record.data.chambres" :key="room.number">
                <strong>{{ room.number }} :</strong>
                {{ Object.values(room.checks || {}).filter(Boolean).length }} / {{ Object.keys(room.checks || {}).length }} points validés
              </p>
            </div>
            <div v-if="record.data?.qualite" class="history-section">
              <h3>Qualité et propreté</h3>
              <p v-if="record.data.qualite.appreciation">
                Appréciation : {{ record.data.qualite.appreciation }}
              </p>
              <p v-for="(zone, key) in record.data.qualite.zones || {}" :key="key">
                <strong>{{ key }} :</strong> {{ zone.etat || 'Non renseigné' }}
                <span v-if="zone.obs"> — {{ zone.obs }}</span>
              </p>
              <p v-for="(etat, zone) in record.data.qualite.proprete || {}" :key="zone">
                <strong>{{ zone }} :</strong> {{ etat || 'Non renseigné' }}
              </p>
            </div>
            <div v-if="record.data?.satisfaction" class="history-section">
              <h3>Satisfaction</h3>
              <p>Note : {{ record.data.satisfaction.note || 'Non renseignée' }}</p>
              <p v-if="record.data.satisfaction.service">Service : {{ record.data.satisfaction.service }}</p>
              <p v-if="record.data.satisfaction.remarques">Remarques : {{ record.data.satisfaction.remarques }}</p>
              <p v-if="record.data.satisfaction.responsable">Responsable : {{ record.data.satisfaction.responsable }}</p>
            </div>
            <div v-if="record.data?.rapport" class="history-section">
              <h3>Rapport</h3>
              <p v-for="field in rapportFields" :key="field.key">
                <strong>{{ field.label }} :</strong> {{ record.data.rapport[field.key] || '—' }}
              </p>
              <p v-if="record.data.rapport.situation">
                <strong>Situation :</strong> {{ record.data.rapport.situation }}
              </p>
              <p v-if="record.data.rapport.decisions">
                <strong>Décisions :</strong> {{ record.data.rapport.decisions }}
              </p>
            </div>
          </div>
        </details>
      </div>
    </section>

    <!-- ═════════ ZONE STRIP (navigation + progression) ═════════ -->
    <nav class="strip no-print" aria-label="Zones de contrôle">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="['strip-tab', { active: activeTab === tab.id, complete: progressOf(tab.id).pct === 100 }]"
        @click="activeTab = tab.id"
      >
        <i :class="progressOf(tab.id).pct === 100 ? 'fas fa-circle-check' : tab.icon"></i>
        <span class="st-label">{{ tab.label }}</span>
        <span class="st-count">{{ progressOf(tab.id).done }}/{{ progressOf(tab.id).total }}</span>
        <span class="st-bar"><span :style="{ width: progressOf(tab.id).pct + '%' }"></span></span>
      </button>
    </nav>

    <!-- ═════════ SECTION HEAD ═════════ -->
    <div class="section-head">
      <span class="sh-icon"><i :class="current.icon"></i></span>
      <div class="sh-text">
        <h2>{{ current.title }}</h2>
        <p>{{ activeProgress.done }} sur {{ activeProgress.total }} points renseignés</p>
      </div>
      <div class="sh-pct" :class="{ full: activeProgress.pct === 100 }">{{ activeProgress.pct }}%</div>
    </div>

    <!-- ═════════ HOUSEKEEPING : CHAMBRES ═════════ -->
    <section v-if="activeTab === 'housekeeping'" class="block">
      <h3 class="block-title">Chambres</h3>
      <div class="rooms">
        <article v-for="room in hkRooms" :key="room.number" class="panel room">
          <header>
            <span class="room-number">{{ room.number }}</span>
            <span :class="['chip', hkRoomStatus(room)]">
              <i :class="hkRoomStatusIcon(room)"></i> {{ hkRoomStatusLabel(room) }}
            </span>
          </header>
          <div class="mini-track"><span :style="{ width: roomPct(room) + '%' }"></span></div>
          <label v-for="item in hkRoomItems" :key="item" :class="['tick', { done: room.checks[item] }]">
            <input v-model="room.checks[item]" type="checkbox" />
            <span class="box"><i class="fas fa-check"></i></span>
            <span class="tick-label">{{ item }}</span>
          </label>
        </article>
      </div>
    </section>

    <!-- ═════════ CHECKLISTS (toutes les zones à cases) ═════════ -->
    <section v-if="current.groups" class="block">
      <h3 v-if="activeTab === 'housekeeping'" class="block-title">Parties communes</h3>
      <div class="groups">
        <article v-for="[gk, gt] in current.groups" :key="gk" class="panel group">
          <header>
            <h4>{{ gt }}</h4>
            <span class="g-count">{{ groupDone(activeTab, gk) }}/{{ checklists[activeTab][gk].length }}</span>
            <button class="g-all no-print" type="button" @click="setGroup(activeTab, gk)">
              {{ groupDone(activeTab, gk) === checklists[activeTab][gk].length ? 'Tout décocher' : 'Tout cocher' }}
            </button>
          </header>
          <div class="mini-track"><span :style="{ width: groupPct(activeTab, gk) + '%' }"></span></div>
          <button
            v-for="(item, idx) in checklists[activeTab][gk]"
            :key="idx"
            type="button"
            :class="['tick', { done: item.done }]"
            :aria-pressed="item.done"
            @click="item.done = !item.done"
          >
            <span class="box"><i class="fas fa-check"></i></span>
            <span class="tick-label">{{ item.label }}</span>
          </button>
        </article>
      </div>
    </section>

    <!-- ═════════ QUALITÉ ═════════ -->
    <template v-if="activeTab === 'qualite'">
      <section class="block">
        <h3 class="block-title">Contrôle qualité journalier</h3>
        <div class="rows">
          <div v-for="zone in qualiteZones" :key="zone.key" class="panel row">
            <span class="row-zone">{{ zone.label }}</span>
            <div class="seg">
              <label :class="['seg-opt ok', { on: qualiteForm[zone.key].etat === 'ok' }]">
                <input type="radio" :name="`zone_${zone.key}`" value="ok" v-model="qualiteForm[zone.key].etat" />
                <i class="fas fa-circle-check"></i> OK
              </label>
              <label :class="['seg-opt nok', { on: qualiteForm[zone.key].etat === 'nok' }]">
                <input type="radio" :name="`zone_${zone.key}`" value="nok" v-model="qualiteForm[zone.key].etat" />
                <i class="fas fa-circle-xmark"></i> Non OK
              </label>
            </div>
            <input type="text" v-model="qualiteForm[zone.key].obs" class="input" placeholder="Observations" />
          </div>
        </div>

        <div class="panel pills-bar">
          <strong>Appréciation globale</strong>
          <div class="pills">
            <label v-for="lvl in appreciations" :key="lvl.value" :class="['pill', lvl.cls, { on: qualiteGlobal === lvl.value }]">
              <input type="radio" :value="lvl.value" v-model="qualiteGlobal" />
              <i :class="lvl.icon"></i> {{ lvl.label }}
            </label>
          </div>
        </div>
      </section>

      <section class="block">
        <h3 class="block-title">Contrôle de propreté détaillé</h3>
        <div class="prop-grid">
          <div v-for="zone in propreteZones" :key="zone" :class="['panel prop', propreteForm[zone]]">
            <span class="prop-zone">{{ zone }}</span>
            <div class="seg small">
              <label :class="['seg-opt ok', { on: propreteForm[zone] === 'conforme' }]">
                <input type="radio" :name="`prp_${zone}`" value="conforme" v-model="propreteForm[zone]" />
                Conforme
              </label>
              <label :class="['seg-opt nok', { on: propreteForm[zone] === 'non_conforme' }]">
                <input type="radio" :name="`prp_${zone}`" value="non_conforme" v-model="propreteForm[zone]" />
                Non conforme
              </label>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ═════════ SATISFACTION ═════════ -->
    <section v-if="activeTab === 'satisfaction'" class="block">
      <div class="panel form-card">
        <div class="form-row">
          <strong>Note du client</strong>
          <div class="pills big">
            <label v-for="lvl in satisfactionLevels" :key="lvl.value" :class="['pill', lvl.cls, { on: satForm.note === lvl.value }]">
              <input type="radio" :value="lvl.value" v-model="satForm.note" />
              <i :class="lvl.icon"></i> {{ lvl.label }}
            </label>
          </div>
        </div>
        <label class="form-row">
          <strong>Service reçu</strong>
          <input type="text" v-model="satForm.service" class="input" placeholder="Décrivez le service reçu" />
        </label>
        <label class="form-row">
          <strong>Remarques du client</strong>
          <textarea v-model="satForm.remarques" class="input" rows="3" placeholder="Remarques éventuelles"></textarea>
        </label>
        <label class="form-row">
          <strong>Responsable</strong>
          <input type="text" v-model="satForm.responsable" class="input" placeholder="Nom du responsable" />
        </label>
      </div>
    </section>

    <!-- ═════════ RAPPORT ═════════ -->
    <section v-if="activeTab === 'rapport'" class="block">
      <div class="figures">
        <label v-for="f in rapportFields" :key="f.key" class="panel figure">
          <span class="fig-icon"><i :class="f.icon"></i></span>
          <input type="number" v-model="rapportForm[f.key]" class="fig-input" min="0" :max="f.max" placeholder="0" />
          <span class="fig-label">{{ f.label }}</span>
        </label>
      </div>
      <div class="panel form-card">
        <div class="form-row">
          <strong>Situation globale</strong>
          <div class="pills">
            <label v-for="sit in situations" :key="sit.value" :class="['pill', sit.cls, { on: rapportForm.situation === sit.value }]">
              <input type="radio" :value="sit.value" v-model="rapportForm.situation" />
              <i :class="sit.icon"></i> {{ sit.label }}
            </label>
          </div>
        </div>
        <label class="form-row">
          <strong>Décisions prises</strong>
          <textarea v-model="rapportForm.decisions" class="input" rows="4" placeholder="Décisions et actions à mener"></textarea>
        </label>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '~/composables/useApi'
import { notify } from '~/composables/useNotification'
import { useUser } from '~/composables/useUser'

definePageMeta({ layout: 'admin' })

// ─── Meta ────────────────────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10)
const form = reactive({ date: today, controleur: '', session: 'journee' })
const saving = ref(false)
const currentUser = ref({})
const controleurName = computed(() => (
  `${currentUser.value.first_name || ''} ${currentUser.value.last_name || ''}`.trim() ||
  currentUser.value.full_name ||
  currentUser.value.username ||
  currentUser.value.email ||
  'Utilisateur connecté'
))
const historyFilters = reactive({ date: '', controleur: '' })
const historyRecords = ref([])
const loadingHistory = ref(false)

const fetchHistory = async () => {
  if (loadingHistory.value) return
  loadingHistory.value = true
  try {
    const { data } = await api.get('controles/', {
      params: {
        ...(historyFilters.date ? { date: historyFilters.date } : {}),
        ...(historyFilters.controleur.trim() ? { controleur: historyFilters.controleur.trim() } : {}),
      },
    })
    historyRecords.value = Array.isArray(data) ? data : (data.results || [])
  } catch (error) {
    notify(error?.response?.data?.detail || 'Impossible de charger l’historique des contrôles', 'danger')
  } finally {
    loadingHistory.value = false
  }
}

const clearHistoryFilters = () => {
  historyFilters.date = ''
  historyFilters.controleur = ''
  fetchHistory()
}

const sessionLabel = (session) => ({
  matin: 'Matin',
  apres_midi: 'Après-midi',
  soir: 'Soir',
  journee: 'Journée complète',
})[session] || session || '—'
const sectionLabel = (section) => tabs.find(tab => tab.id === section)?.label || section

// ─── Onglets ─────────────────────────────────────────────────────────────────
const tabs = [
  { id: 'salle', label: 'Salle', icon: 'fas fa-champagne-glasses', title: "Salle de réception, jour de l'événement",
    groups: [['avant', 'Avant événement'], ['pendant', 'Pendant événement'], ['apres', 'Après événement']] },
  { id: 'reception', label: 'Réception', icon: 'fas fa-concierge-bell', title: 'Réception',
    groups: [['ouverture', 'Ouverture'], ['accueil', 'Accueil client'], ['journee', 'Durant la journée'], ['fermeture', 'Fermeture']] },
  { id: 'housekeeping', label: 'Housekeeping', icon: 'fas fa-broom', title: 'Housekeeping et propreté',
    groups: [['communs', 'Espaces communs'], ['controle_final', 'Contrôle final']] },
  { id: 'cuisine', label: 'Cuisine', icon: 'fas fa-utensils', title: 'Cuisine et restauration',
    groups: [['avant', 'Avant service'], ['pendant', 'Pendant service'], ['apres', 'Après service']] },
  { id: 'securite', label: 'Sécurité', icon: 'fas fa-shield-halved', title: 'Sécurité',
    groups: [['surveillance', 'Surveillance'], ['incidents', 'Incidents']] },
  { id: 'gerant', label: 'Gérant', icon: 'fas fa-user-tie', title: 'Gérant, contrôle quotidien',
    groups: [['daily', 'Points à valider']] },
  { id: 'qualite', label: 'Qualité', icon: 'fas fa-clipboard-check', title: 'Fiches qualité et propreté' },
  { id: 'satisfaction', label: 'Satisfaction', icon: 'fas fa-face-smile', title: 'Satisfaction client' },
  { id: 'rapport', label: 'Rapport', icon: 'fas fa-file-lines', title: 'Rapport journalier de gestion' },
]
const activeTab = ref('salle')
const current = computed(() => tabs.find(t => t.id === activeTab.value) || tabs[0])

// ─── Checklists ──────────────────────────────────────────────────────────────
const L = (labels) => labels.map(label => ({ label, done: false }))

const checklists = reactive({
  salle: {
    avant:   L(['Toilettes nettoyées', 'Sonorisation testée', 'Chaises propres', 'Tables installées', 'Décoration prête', 'Boissons disponibles']),
    pendant: L(['Accueil organisé', 'Personnel présent et au service des clients', 'Porte Jardin fermée', 'Suivi du déroulement', 'Ronde de nettoyage Toilettes']),
    apres:   L(['Nettoyage complet', 'Inventaire matériel', 'Inventaire boissons', "Rapport d'événement"]),
  },
  reception: {
    ouverture: L(['Poste propre et organisé', 'Registre de réservation à jour', 'Téléphone fonctionnel', 'Clés disponibles']),
    accueil:   L(['Sourire et salutation systématique', 'Vérification réservation', 'Enregistrement client complet', 'Explication claire des services']),
    journee:   L(['Réservations mises à jour', 'Réponse rapide aux appels', 'Demandes clients traitées']),
    fermeture: L(['Caisse équilibrée', 'Registre mis à jour', 'Rapport journalier transmis']),
  },
  housekeeping: {
    communs: L([
      'Cuisine nettoyée', 'Couloirs étage nettoyés', 'Escaliers nettoyés',
      'Petite salle VIP BIMBO VIP Residence Hall impeccable',
      'Couloirs Rez-de-chaussée nettoyés', 'Cour Hôtel propre', 'Espace linge propre',
      'Nettoyage linge', 'Grande cour propre',
      'Grande Salle LaGombo Conference Hall impeccable',
      'Jardin Matrona Garden propre', 'Parking Extérieur propre',
      "Petite salle Back'Lea Conference Hall propre",
    ]),
    controle_final: L(['Aucune trace de déchet visible', 'Aucun oubli', 'Vérification par superviseur']),
  },
  cuisine: {
    avant:   L(['Mains lavées', 'Plan de travail propre', 'Ingrédients disponibles', 'Tenue propre']),
    pendant: L(['Respect hygiène', 'Cuisson correcte', 'Présentation soignée', 'Rapidité du service']),
    apres:   L(['Cuisine nettoyée', 'Déchets évacués', 'Stock mis à jour']),
  },
  securite: {
    surveillance: L(['Accès contrôlé', 'Ronde effectuée', 'Parking sécurisé']),
    incidents:    L(['Intervention rapide', 'Gérant informé', 'Rapport rédigé']),
  },
  gerant: {
    daily: L([
      'Inspection générale faite', 'Personnel présent et discipliné',
      'Réservations vérifiées', 'Propreté validée', 'Cuisine contrôlée',
      'Événements suivis', 'Caisse vérifiée', 'Clients satisfaits',
    ]),
  },
})

const groupDone = (sec, g) => checklists[sec][g].filter(i => i.done).length
const groupPct = (sec, g) => Math.round(groupDone(sec, g) / checklists[sec][g].length * 100)
const setGroup = (sec, g) => {
  const all = groupDone(sec, g) === checklists[sec][g].length
  checklists[sec][g].forEach(i => { i.done = !all })
}

// ─── Housekeeping : chambres ─────────────────────────────────────────────────
const hkRoomItems = [
  'Lit bien fait (draps propres)', 'Sol propre', 'Salle de bain désinfectée', 'Odeur agréable',
  'Poubelles vidées', 'Meubles et appareils nettoyés', 'Vitres et Murs nettoyés',
]
const hkRooms = reactive(
  ['100', '101', '102', '103', '104', '200', '201', '202', '203', '204', 'VIP1', 'VIP2'].map(n => ({
    number: n,
    checks: Object.fromEntries(hkRoomItems.map(i => [i, false])),
  }))
)
const roomDone = (room) => Object.values(room.checks).filter(Boolean).length
const roomPct = (room) => Math.round(roomDone(room) / hkRoomItems.length * 100)
const hkRoomStatus = (room) => {
  const d = roomDone(room)
  return d === 0 ? 'pending' : d === hkRoomItems.length ? 'done' : 'partial'
}
const hkRoomStatusLabel = (room) => ({ done: 'Terminée', partial: 'En cours', pending: 'À faire' })[hkRoomStatus(room)]
const hkRoomStatusIcon = (room) => ({ done: 'fas fa-circle-check', partial: 'fas fa-spinner', pending: 'far fa-circle' })[hkRoomStatus(room)]

// ─── Qualité ─────────────────────────────────────────────────────────────────
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
  { value: 'ameliorer',    label: 'À améliorer',  cls: 'ameliorer',    icon: 'fas fa-triangle-exclamation' },
  { value: 'inacceptable', label: 'Inacceptable', cls: 'inacceptable', icon: 'fas fa-ban' },
]

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

// ─── Satisfaction ────────────────────────────────────────────────────────────
const satisfactionLevels = [
  { value: 'tres_satisfait', label: 'Très satisfait', cls: 'excellent',    icon: 'fas fa-face-grin-stars' },
  { value: 'satisfait',      label: 'Satisfait',      cls: 'bon',          icon: 'fas fa-face-smile' },
  { value: 'moyen',          label: 'Moyen',          cls: 'ameliorer',    icon: 'fas fa-face-meh' },
  { value: 'insatisfait',    label: 'Insatisfait',    cls: 'inacceptable', icon: 'fas fa-face-frown' },
]
const satForm = reactive({ note: '', service: '', remarques: '', responsable: '' })

// ─── Rapport ─────────────────────────────────────────────────────────────────
const situations = [
  { value: 'bonne',    label: 'Bonne',    cls: 'excellent',    icon: 'fas fa-circle-check' },
  { value: 'moyenne',  label: 'Moyenne',  cls: 'ameliorer',    icon: 'fas fa-circle-half-stroke' },
  { value: 'critique', label: 'Critique', cls: 'inacceptable', icon: 'fas fa-circle-exclamation' },
]
const rapportFields = [
  { key: 'nb_clients',      label: 'Clients',            icon: 'fas fa-users' },
  { key: 'taux_occupation', label: "Taux d'occupation %", icon: 'fas fa-bed', max: 100 },
  { key: 'evenements',      label: 'Événements',         icon: 'fas fa-champagne-glasses' },
  { key: 'incidents',       label: 'Incidents',          icon: 'fas fa-triangle-exclamation' },
]
const emptyRapport = () => ({ nb_clients: '', taux_occupation: '', evenements: '', incidents: '', situation: '', decisions: '' })
const rapportForm = reactive(emptyRapport())

// ─── Progression ─────────────────────────────────────────────────────────────
const progressOf = (id) => {
  let total = 0, done = 0
  if (checklists[id]) {
    Object.values(checklists[id]).forEach(g => { total += g.length; done += g.filter(i => i.done).length })
  }
  if (id === 'housekeeping') {
    total += hkRooms.length * hkRoomItems.length
    done += hkRooms.reduce((s, r) => s + roomDone(r), 0)
  } else if (id === 'qualite') {
    total = qualiteZones.length + propreteZones.length
    done = qualiteZones.filter(z => qualiteForm[z.key].etat).length + propreteZones.filter(z => propreteForm[z]).length
  } else if (id === 'satisfaction') {
    total = 4
    done = [satForm.note, satForm.service, satForm.remarques, satForm.responsable].filter(Boolean).length
  } else if (id === 'rapport') {
    total = 6
    done = Object.values(rapportForm).filter(v => v !== '' && v !== null && v !== undefined).length
  }
  return { total, done, pct: total ? Math.round(done / total * 100) : 0 }
}
const activeProgress = computed(() => progressOf(activeTab.value))

// Totaux globaux : checklists + chambres (comme avant)
const checklistTabs = tabs.filter(t => t.groups).map(t => t.id)
const totalChecklists = computed(() => checklistTabs.reduce((s, id) => s + progressOf(id).total, 0))
const totalDone = computed(() => checklistTabs.reduce((s, id) => s + progressOf(id).done, 0))
const totalPending = computed(() => totalChecklists.value - totalDone.value)
const globalPct = computed(() => totalChecklists.value ? Math.round(totalDone.value / totalChecklists.value * 100) : 0)

// ─── Réinitialiser / Imprimer ────────────────────────────────────────────────
const resetAll = () => {
  if (!confirm('Réinitialiser tous les champs de cette session ?')) return
  Object.values(checklists).forEach(sec => Object.values(sec).forEach(g => g.forEach(i => { i.done = false })))
  hkRooms.forEach(room => hkRoomItems.forEach(i => { room.checks[i] = false }))
  qualiteZones.forEach(z => { qualiteForm[z.key] = { etat: '', obs: '' } })
  propreteZones.forEach(z => { propreteForm[z] = '' })
  qualiteGlobal.value = ''
  Object.assign(satForm, { note: '', service: '', remarques: '', responsable: '' })
  Object.assign(rapportForm, emptyRapport())
}

const saveControle = async () => {
  if (saving.value) return
  if (!form.date) {
    notify('Veuillez renseigner la date du contrôle', 'warning')
    return
  }

  saving.value = true
  try {
    await api.post('controles/', {
      date: form.date,
      controleur: controleurName.value,
      session: form.session,
      data: JSON.parse(JSON.stringify({
        checklists,
        chambres: hkRooms,
        qualite: {
          zones: qualiteForm,
          appreciation: qualiteGlobal.value,
          proprete: propreteForm,
        },
        satisfaction: satForm,
        rapport: rapportForm,
      })),
    })
    notify('Contrôle enregistré avec succès')
    await fetchHistory()
  } catch (error) {
    notify(error?.response?.data?.detail || 'Erreur lors de l’enregistrement du contrôle', 'danger')
  } finally {
    saving.value = false
  }
}

const printPage = () => window.print()

onMounted(() => {
  currentUser.value = useUser().getUser()
  form.controleur = controleurName.value
  fetchHistory()
})
</script>

<style scoped>
/* ───────── Tokens : branchés sur le thème global (--white, --gray-*) clair / sombre ───────── */
.ctrl {
  --ink: #12302d;
  --ink-2: #1c4a44;
  --brass: #c28a2c;
  --brass-soft: rgba(194, 138, 44, 0.14);
  --ok: #1d7f57;
  --warn: #b7791f;
  --bad: #b83227;
  --info: #2563a8;
  --surface: var(--white, #ffffff);
  --line: var(--gray-200, #e2e8f0);
  --fg: var(--gray-800, #1e293b);
  --muted: var(--gray-500, #64748b);
  --edge: var(--gray-400, #94a3b8);
  --hover: color-mix(in srgb, var(--gray-500, #64748b) 13%, transparent);

  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: var(--fg);
}
.ctrl :is(button, input, select, textarea) { font: inherit; }
.ctrl :is(button, .tick, .seg-opt, .pill, .strip-tab):focus-visible,
.ctrl .input:focus-visible { outline: 2px solid var(--brass); outline-offset: 2px; }

/* Mode sombre : html[data-admin-theme="dark"] (voir main.css) */
:global(html[data-admin-theme="dark"]) .ctrl {
  --ink: #0f2a27;
  --ink-2: #6fc2b0;
  --brass: #e0a63c;
  --brass-soft: rgba(224, 166, 60, 0.16);
  --ok: #34d399;
  --warn: #fbbf24;
  --bad: #f87171;
  --info: #60a5fa;
}
:global(html[data-admin-theme="dark"]) .ctrl .hero { border: 1px solid rgba(255, 255, 255, 0.08); }
:global(html[data-admin-theme="dark"]) .ctrl .seg-opt.on,
:global(html[data-admin-theme="dark"]) .ctrl .tick.done .box { color: #0b1220; }

/* Titres : on neutralise le style global des h1–h6 (orange, très grand) */
.ctrl :is(h1, h2, h3, h4) { margin: 0; line-height: 1.25; color: var(--fg); font-family: var(--font-sans, inherit); }
.ctrl :is(h1, h2) { font-family: var(--font-serif, Georgia, serif); }

.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; }

/* ───────── Boutons ───────── */
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 0.6rem 1.05rem; border-radius: 10px; border: 1px solid transparent;
  font-size: 0.875rem; font-weight: 600; cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn-brass { background: var(--brass); color: #1b1305; }
.btn-brass:hover { background: #d29a38; }
.btn-ghost { background: transparent; color: #e6efec; border-color: rgba(255, 255, 255, 0.25); }
.btn-ghost:hover { background: rgba(255, 255, 255, 0.1); }

/* ───────── En-tête ───────── */
.hero {
  background: var(--ink);
  color: #f3f7f5;
  border-radius: 18px;
  padding: 1.5rem 1.75rem 1.4rem;
  display: flex; flex-direction: column; gap: 1.4rem;
}
.hero-top { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; }
.hero-title { display: flex; align-items: center; gap: 1rem; }
.hero-badge {
  width: 50px; height: 50px; border-radius: 12px; flex-shrink: 0;
  display: grid; place-items: center; font-size: 1.3rem;
  background: var(--brass-soft); color: var(--brass); border: 1px solid rgba(194, 138, 44, 0.45);
}
.hero h1 { margin: 0; color: #fff; font-size: 1.65rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; }
.hero p { margin: 4px 0 0; font-size: 0.9rem; color: rgba(243, 247, 245, 0.62); }
.hero-actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }

.hero-progress { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem 2.5rem; flex-wrap: wrap; }
.hp-figures { display: flex; gap: 1.75rem; }
.hp-figures div { display: flex; align-items: baseline; gap: 6px; }
.hp-figures strong { font-size: 1.35rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.hp-figures span { font-size: 0.8rem; color: rgba(243, 247, 245, 0.6); }
.hp-bar { flex: 1; min-width: 240px; display: flex; align-items: center; gap: 0.8rem; }
.hp-bar b { font-size: 0.95rem; min-width: 2.6rem; text-align: right; font-variant-numeric: tabular-nums; }
.hp-track { flex: 1; height: 8px; border-radius: 99px; background: rgba(255, 255, 255, 0.14); overflow: hidden; }
.hp-fill { height: 100%; border-radius: 99px; background: var(--brass); transition: width 0.4s ease; }

/* ───────── Meta ───────── */
.meta { display: flex; flex-wrap: wrap; gap: 1rem; padding: 1rem 1.25rem; }
.field { display: flex; flex-direction: column; gap: 6px; min-width: 180px; }
.field.grow { flex: 1; min-width: 220px; }
.field > span { font-size: 0.8rem; font-weight: 600; color: var(--muted); display: flex; align-items: center; gap: 6px; }
.field > span i { color: var(--ink-2); }
.input {
  width: 100%; box-sizing: border-box; padding: 0.55rem 0.75rem;
  background: var(--surface); color: var(--fg);
  border: 1px solid var(--line); border-radius: 8px; font-size: 0.9rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.input:focus { outline: none; border-color: var(--brass); box-shadow: 0 0 0 3px var(--brass-soft); }
textarea.input { resize: vertical; min-height: 4.5rem; }
.history { padding: 1rem 1.25rem; }
.history-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
.history-head h2 { font-size: 1.1rem; font-weight: 700; }
.history-head p { margin: 0.25rem 0 0; color: var(--muted); font-size: 0.85rem; }
.history-refresh { color: var(--fg); border-color: var(--line); }
.history-filters { display: flex; flex-wrap: wrap; align-items: end; gap: 0.8rem; margin-top: 1rem; }
.history-filters .field { flex: 1; }
.history-filter-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.history .btn-outline { color: var(--fg); border-color: var(--line); background: transparent; }
.history-empty { margin: 1rem 0 0; color: var(--muted); font-size: 0.9rem; }
.history-list { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem; }
.history-record { border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.history-record summary { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 1rem; cursor: pointer; list-style: none; }
.history-record summary::-webkit-details-marker { display: none; }
.history-record summary > span:nth-child(2) { flex: 1; }
.history-record summary > i { color: var(--muted); transition: transform 0.15s; }
.history-record[open] summary > i { transform: rotate(180deg); }
.history-record-date { font-weight: 700; font-variant-numeric: tabular-nums; }
.history-session { color: var(--muted); font-size: 0.85rem; }
.history-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.9rem; padding: 0.2rem 1rem 1rem; }
.history-section { min-width: 0; padding: 0.75rem; background: var(--hover); border-radius: 9px; }
.history-section h3 { margin-bottom: 0.5rem; font-size: 0.9rem; }
.history-group + .history-group { margin-top: 0.65rem; }
.history-group h4 { margin-bottom: 0.25rem; font-size: 0.82rem; }
.history-section ul { display: grid; gap: 0.25rem; margin: 0; padding: 0; list-style: none; }
.history-section li, .history-section p { margin: 0.2rem 0; font-size: 0.82rem; line-height: 1.4; overflow-wrap: anywhere; }
.history-section li i { width: 1rem; color: var(--muted); }
.history-section li .history-done { color: var(--ok); }

/* ───────── Bande de zones (navigation + progression) ───────── */
.strip {
  position: sticky; top: 0.5rem; z-index: 5;
  display: grid; grid-template-columns: repeat(9, minmax(104px, 1fr)); gap: 6px;
  padding: 6px; border-radius: 16px; overflow-x: auto;
  background: var(--surface); border: 1px solid var(--line);
  box-shadow: 0 6px 20px -12px rgba(18, 48, 45, 0.35);
  scrollbar-width: thin;
}
.strip-tab {
  position: relative; display: grid; grid-template-columns: auto 1fr; align-items: center; column-gap: 8px; row-gap: 1px;
  padding: 0.55rem 0.7rem 0.75rem; border: 0; border-radius: 11px; cursor: pointer; text-align: left;
  background: transparent; color: var(--muted); transition: background 0.15s, color 0.15s;
}
.strip-tab > i { grid-row: 1 / 3; font-size: 1.05rem; color: var(--ink-2); }
.st-label { font-size: 0.85rem; font-weight: 600; color: var(--fg); line-height: 1.2; }
.st-count { font-size: 0.72rem; font-variant-numeric: tabular-nums; }
.st-bar { position: absolute; left: 0.7rem; right: 0.7rem; bottom: 0.4rem; height: 3px; border-radius: 99px; background: var(--line); overflow: hidden; }
.st-bar span { display: block; height: 100%; background: var(--brass); transition: width 0.35s ease; }
.strip-tab:hover { background: var(--hover); }
.strip-tab.complete > i { color: var(--ok); }
.strip-tab.complete .st-bar span { background: var(--ok); }
.strip-tab.active { background: var(--ink); color: rgba(255, 255, 255, 0.7); }
.strip-tab.active > i { color: var(--brass); }
.strip-tab.active .st-label { color: #fff; }
.strip-tab.active .st-bar { background: rgba(255, 255, 255, 0.18); }

/* ───────── Titre de section ───────── */
.section-head { display: flex; align-items: center; gap: 0.9rem; padding: 0.35rem 0.25rem 0; }
.sh-icon { width: 42px; height: 42px; border-radius: 11px; display: grid; place-items: center; background: var(--brass-soft); color: var(--brass); font-size: 1.05rem; }
.sh-text { flex: 1; }
.sh-text h2 { margin: 0; font-size: 1.25rem; font-weight: 700; letter-spacing: -0.015em; }
.sh-text p { margin: 2px 0 0; font-size: 0.85rem; color: var(--muted); }
.sh-pct { font-size: 1.5rem; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--warn); }
.sh-pct.full { color: var(--ok); }

.block { display: flex; flex-direction: column; gap: 0.75rem; }
.block-title { margin: 0.4rem 0.25rem 0; font-size: 0.95rem; font-weight: 700; color: var(--muted); }

/* ───────── Cases à cocher ───────── */
.groups { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 0.9rem; align-items: start; }
.group { padding: 1rem 1rem 0.6rem; display: flex; flex-direction: column; gap: 2px; }
.group header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem; }
.group h4 { margin: 0; flex: 1; font-size: 0.95rem; font-weight: 700; }
.g-count { font-size: 0.8rem; font-weight: 600; color: var(--muted); font-variant-numeric: tabular-nums; }
.g-all {
  border: 1px solid var(--line); background: transparent; color: var(--ink-2);
  border-radius: 8px; padding: 3px 9px; font-size: 0.75rem; font-weight: 600; cursor: pointer;
}
.g-all:hover { background: var(--hover); }
.mini-track { height: 4px; border-radius: 99px; background: var(--line); overflow: hidden; margin-bottom: 0.5rem; }
.mini-track span { display: block; height: 100%; background: var(--brass); transition: width 0.3s ease; }

.tick {
  display: flex; align-items: center; justify-content: flex-start; gap: 0.7rem; width: 100%;
  padding: 0.6rem 0.5rem; border: 0; border-radius: 9px; background: transparent;
  color: var(--fg); text-align: left; cursor: pointer; transition: background 0.12s;
}
.tick:hover { background: var(--hover); }
.tick input { position: absolute; opacity: 0; pointer-events: none; }
.box {
  width: 22px; height: 22px; flex-shrink: 0; border-radius: 7px; border: 2px solid var(--edge);
  display: grid; place-items: center; font-size: 0.7rem; color: transparent;
  transition: background 0.15s, border-color 0.15s, color 0.15s, transform 0.15s;
}
.tick.done .box { background: var(--ok); border-color: var(--ok); color: #fff; transform: scale(1.04); }
.tick-label { font-size: 0.9rem; line-height: 1.35; }
.tick.done .tick-label { color: var(--muted); text-decoration: line-through; }

/* ───────── Chambres ───────── */
.rooms { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 0.9rem; }
.room { padding: 0.9rem 0.8rem 0.5rem; position: relative; }
.room header { display: flex; justify-content: space-between; align-items: center; margin: 0 0.3rem 0.6rem; }
.room-number { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.01em; }
.room .mini-track { margin: 0 0.3rem 0.4rem; }
.room .tick { padding: 0.42rem 0.3rem; }
.room .tick-label { font-size: 0.82rem; }
.chip { font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 99px; display: inline-flex; gap: 5px; align-items: center; }
.chip.pending { background: var(--hover); color: var(--muted); }
.chip.partial { background: rgba(183, 121, 31, 0.14); color: var(--warn); }
.chip.done    { background: rgba(29, 127, 87, 0.14);  color: var(--ok); }

/* ───────── Qualité : lignes + segments ───────── */
.rows { display: flex; flex-direction: column; gap: 0.6rem; }
.row { display: grid; grid-template-columns: 170px auto 1fr; align-items: center; gap: 1rem; padding: 0.7rem 1rem; }
.row-zone { font-weight: 600; font-size: 0.92rem; }
.seg { display: inline-flex; padding: 3px; gap: 3px; background: var(--hover); border-radius: 10px; }
.seg-opt {
  display: inline-flex; align-items: center; gap: 6px; padding: 0.4rem 0.9rem; border-radius: 8px;
  font-size: 0.83rem; font-weight: 600; color: var(--muted); cursor: pointer; transition: background 0.15s, color 0.15s;
}
.seg-opt input { position: absolute; opacity: 0; pointer-events: none; }
.seg-opt.ok.on  { background: var(--ok);  color: #fff; }
.seg-opt.nok.on { background: var(--bad); color: #fff; }
.seg.small .seg-opt { padding: 0.3rem 0.7rem; font-size: 0.78rem; }

.pills-bar { display: flex; align-items: center; flex-wrap: wrap; gap: 0.9rem 1.2rem; padding: 0.9rem 1.1rem; }
.pills { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.pill {
  display: inline-flex; align-items: center; gap: 7px; padding: 0.5rem 1rem; border-radius: 99px;
  font-size: 0.86rem; font-weight: 600; cursor: pointer; background: var(--surface);
  border: 1.5px solid var(--line); color: var(--muted); transition: all 0.15s;
}
.pill input { position: absolute; opacity: 0; pointer-events: none; }
.pill:hover { background: var(--hover); }
.pill.excellent.on    { background: rgba(29, 127, 87, 0.12);  border-color: var(--ok);   color: var(--ok); }
.pill.bon.on          { background: rgba(37, 99, 168, 0.12);  border-color: var(--info); color: var(--info); }
.pill.ameliorer.on    { background: rgba(183, 121, 31, 0.14); border-color: var(--warn); color: var(--warn); }
.pill.inacceptable.on { background: rgba(184, 50, 39, 0.12);  border-color: var(--bad);  color: var(--bad); }
.pills.big .pill { padding: 0.7rem 1.2rem; font-size: 0.92rem; }
.pills.big .pill i { font-size: 1.15rem; }

/* ───────── Propreté ───────── */
.prop-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 0.6rem; }
.prop { display: flex; align-items: center; justify-content: space-between; gap: 0.7rem; padding: 0.6rem 0.8rem; border-left: 4px solid var(--line); }
.prop.conforme { border-left-color: var(--ok); }
.prop.non_conforme { border-left-color: var(--bad); }
.prop-zone { font-size: 0.85rem; font-weight: 500; flex: 1; line-height: 1.3; }

/* ───────── Formulaires ───────── */
.form-card { padding: 1.4rem; display: flex; flex-direction: column; gap: 1.2rem; }
.form-row { display: flex; flex-direction: column; gap: 0.5rem; }
.form-row > strong { font-size: 0.85rem; color: var(--muted); font-weight: 600; }

.figures { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 0.9rem; }
.figure { display: grid; grid-template-columns: auto 1fr; align-items: center; column-gap: 0.8rem; padding: 0.9rem 1rem; cursor: text; }
.figure:focus-within { border-color: var(--brass); box-shadow: 0 0 0 3px var(--brass-soft); }
.fig-icon { grid-row: 1 / 3; width: 40px; height: 40px; border-radius: 10px; display: grid; place-items: center; background: var(--hover); color: var(--ink-2); }
.fig-input { width: 100%; border: 0; background: transparent; color: var(--fg); font-size: 1.6rem; font-weight: 700; padding: 0; font-variant-numeric: tabular-nums; }
.fig-input:focus { outline: none; }
.fig-label { font-size: 0.78rem; color: var(--muted); }

/* ───────── Responsive ───────── */
@media (max-width: 760px) {
  .ctrl { padding: 0.75rem 0.75rem 2.5rem; }
  .hero { padding: 1.1rem; }
  .row { grid-template-columns: 1fr; gap: 0.6rem; }
  .strip { grid-template-columns: repeat(9, 128px); }
  .hp-figures { gap: 1rem; flex-wrap: wrap; }
}
@media (prefers-reduced-motion: reduce) {
  .ctrl * { transition: none !important; }
}

/* ───────── Impression ───────── */
@media print {
  .no-print, .strip { display: none !important; }
  .ctrl { padding: 0; max-width: none; color: #000; }
  .hero { background: #fff; color: #000; border: 1px solid #999; }
  .hero p, .hp-figures span { color: #444; }
  .hp-track { background: #ddd; }
  .groups, .prop-grid, .figures { grid-template-columns: repeat(2, 1fr); }
  .rooms { grid-template-columns: repeat(3, 1fr); }
  .panel { break-inside: avoid; }
}
</style>