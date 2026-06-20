# Debug Session: post-broken-pipe
- **Status**: [OPEN]
- **Issue**: POST sur `bookings/` et `payments/` retourne `201`, mais l'utilisateur observe que l'action "ne marche pas" et le serveur Django affiche ensuite `Broken pipe`.
- **Debug Server**: http://127.0.0.1:7777/event
- **Log File**: .dbg/trae-debug-log-post-broken-pipe.ndjson

## Reproduction Steps
1. Ouvrir l'admin.
2. Soumettre une création de réservation ou de paiement.
3. Observer le comportement UI.
4. Vérifier les logs Django affichant `201` puis `Broken pipe`.

## Hypotheses & Verification
| ID | Hypothesis | Likelihood | Effort | Evidence |
|----|------------|------------|--------|----------|
| A | Le `POST` réussit bien côté backend, puis le frontend casse juste après sur un traitement local (print modal, parsing, refresh, notification). | High | Low | Pending |
| B | Le client annule la connexion après réception partielle de la réponse, ce qui produit le `Broken pipe` sans empêcher la création réelle. | High | Low | Pending |
| C | La réponse `201` contient une forme de données inattendue pour le frontend, qui provoque une erreur JS silencieuse ou non visible. | Medium | Low | Pending |
| D | Un envoi secondaire après le `POST` (email, jeton, fetch suivant) déclenche une coupure de socket ou un échec de chaîne UI. | Medium | Medium | Pending |
| E | Le problème se situe surtout sur la page paiements/réservations avec une course entre fermeture de modal, reload des listes, et rendu. | Medium | Low | Pending |

## Log Evidence
- Instrumentation ajoutée dans `composables/useApi.js`, `pages/admin/bookings.vue`, `pages/admin/payments.vue`, `hall_api/api/views.py`
- Collecteur runtime actif sur `http://127.0.0.1:7777/event`
- Logs vidés et prêts pour une reproduction `runId=pre-fix`

## Verification Conclusion
[En attente]
