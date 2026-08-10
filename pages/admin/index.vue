<template>
  <div class="admin-dashboard">
    <section class="hero card">
      <div class="hero-copy">
        <div class="hero-badge">
          <i class="fas fa-gauge-high"></i>
          Tableau de bord
        </div>
        <h1 class="hero-title">Pilotage hôtelier et administratif</h1>
        <p class="hero-subtitle">
          Supervisez la réception, l'occupation des chambres, les encaissements et les alertes clés dans un tableau de bord plus propre et plus moderne.
        </p>

        <div class="hero-actions">
          <button class="btn btn-export btn-sm admin-head-btn" :class="{ 'is-loading': loading }" :disabled="loading" @click="refreshAll">
            <i class="fas fa-rotate-right"></i>
            <span class="btn-label">Actualiser</span>
          </button>
          <NuxtLink to="/admin/bookings" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-calendar-days"></i>
            <span class="btn-label">Réservations</span>
          </NuxtLink>
          <NuxtLink to="/admin/payments" class="btn btn-primary btn-sm admin-head-btn">
            <i class="fas fa-credit-card"></i>
            <span class="btn-label">Paiements</span>
          </NuxtLink>
          <NuxtLink to="/admin/reports" class="btn btn-secondary btn-sm admin-head-btn">
            <i class="fas fa-chart-line"></i>
            <span class="btn-label">Rapports</span>
          </NuxtLink>
          <NuxtLink to="/admin/calendar" class="btn btn-export btn-sm admin-head-btn">
            <i class="fas fa-calendar-alt"></i>
            <span class="btn-label">Calendrier</span>
          </NuxtLink>
        </div>
      </div>

      <div class="hero-kpis">
        <div class="kpi">
          <div class="kpi-label">Aujourd'hui</div>
          <div class="kpi-value">{{ todayYmd }}</div>
          <div class="kpi-hint">{{ displayBookingsToday }} réservations</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Arrivées hôtel</div>
          <div class="kpi-value">{{ todayPendingArrivals }}</div>
          <div class="kpi-hint">Clients attendus</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Départs jour</div>
          <div class="kpi-value">{{ todaysCheckOutsFormatted }}</div>
          <div class="kpi-hint">Check-outs prévus</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Chambres dispo</div>
          <div class="kpi-value">{{ availableRoomsCount }}</div>
          <div class="kpi-hint">Libres aujourd'hui</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Séjours en cours</div>
          <div class="kpi-value">{{ inHouseGuestsCount }}</div>
          <div class="kpi-hint">Clients hébergés</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Encaissement jour</div>
          <div class="kpi-value">{{ formatMoney(revenueTodayAmount) }}</div>
          <div class="kpi-hint">{{ unreadCount }} notification(s)</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Encaissement sem.</div>
          <div class="kpi-value">{{ formatMoney(revenueWeekAmount) }}</div>
          <div class="kpi-hint">7 derniers jours</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Occupation ch.</div>
          <div class="kpi-value">{{ roomOccupancyRateLabel }}</div>
          <div class="kpi-hint">{{ occupiedRoomsTodayCount }}/{{ activeRoomsCount }} ch.</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Solde restant</div>
          <div class="kpi-value">{{ formatMoney(roomBalanceDueAmount) }}</div>
          <div class="kpi-hint">À encaisser chambres</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Occupation salles</div>
          <div class="kpi-value">{{ hallOccupancyRate }}%</div>
          <div class="kpi-hint">{{ occupiedHallsTodayCount }}/{{ activeHallsCount || 0 }}</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">TCSTH du mois</div>
          <div class="kpi-value">{{ formatMoney(dashTcsthMonthCollected) }}</div>
          <div class="kpi-hint">Taxe 5% en cours</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">CA du mois</div>
          <div class="kpi-value">{{ formatMoney(totalRevenueMonth) }}</div>
          <div class="kpi-hint">Chambres + salles</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Moy. prix / nuit</div>
          <div class="kpi-value">{{ formatMoney(avgPricePerNight) }}</div>
          <div class="kpi-hint">Toutes périodes</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Durée moy. séjour</div>
          <div class="kpi-value">{{ avgStayNights }} n.</div>
          <div class="kpi-hint">{{ totalRoomNights }} nuits total</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Clients uniques</div>
          <div class="kpi-value">{{ uniqueCustomersCount.toLocaleString() }}</div>
          <div class="kpi-hint">{{ totalRoomBookingsCount }} séjours</div>
        </div>
        <div class="kpi">
          <div class="kpi-label">Moy. paiement</div>
          <div class="kpi-value">{{ formatMoney(avgPaymentAmount) }}</div>
          <div class="kpi-hint">{{ paidPaymentsCount }} transaction(s)</div>
        </div>
      </div>
    </section>

    <section class="stats-grid">
      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-calendar-check"></i></div>
        <div class="stat-content">
          <span class="stat-label">Réservations (total)</span>
          <strong class="stat-value">{{ totalBookingsFormatted }}</strong>
          <div class="stat-meta">Toutes périodes</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-building"></i></div>
        <div class="stat-content">
          <span class="stat-label">Salles actives</span>
          <strong class="stat-value">{{ activeHallsFormatted }}</strong>
          <div class="stat-meta">Disponibles</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-bed"></i></div>
        <div class="stat-content">
          <span class="stat-label">Taux d'occupation chambres</span>
          <strong class="stat-value">{{ roomOccupancyRateLabel }}</strong>
          <div class="stat-meta">{{ occupiedRoomsTodayCount }} occupée(s) / {{ activeRoomsCount }} active(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-right-to-bracket"></i></div>
        <div class="stat-content">
          <span class="stat-label">Check-ins du jour</span>
          <strong class="stat-value">{{ todaysCheckInsFormatted }}</strong>
          <div class="stat-meta">Arrivées enregistrées</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-right-from-bracket"></i></div>
        <div class="stat-content">
          <span class="stat-label">Check-outs du jour</span>
          <strong class="stat-value">{{ todaysCheckOutsFormatted }}</strong>
          <div class="stat-meta">Départs enregistrés</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div class="stat-content">
          <span class="stat-label">Paiements en attente</span>
          <strong class="stat-value">{{ pendingPaymentsFormatted }}</strong>
          <div class="stat-meta">{{ pendingPaymentsCount > 0 ? 'À solder' : 'Tout est à jour' }}</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-box-open"></i></div>
        <div class="stat-content">
          <span class="stat-label">Stock critique</span>
          <strong class="stat-value">{{ stockAlertsFormatted }}</strong>
          <div class="stat-meta">Rupture ou seuil</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon tcsth"><i class="fas fa-file-invoice-dollar"></i></div>
        <div class="stat-content">
          <span class="stat-label">TCSTH collecté (5%)</span>
          <strong class="stat-value">{{ formatMoney(dashTcsthCollected) }}</strong>
          <div class="stat-meta">Taxe nuitées</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-half"></i></div>
        <div class="stat-content">
          <span class="stat-label">TCSTH à verser (OBR)</span>
          <strong class="stat-value">{{ formatMoney(dashTcsthPending) }}</strong>
          <div class="stat-meta">En attente paiement</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-scale-balanced"></i></div>
        <div class="stat-content">
          <span class="stat-label">CA HT nuitées</span>
          <strong class="stat-value">{{ formatMoney(dashTcsthHT) }}</strong>
          <div class="stat-meta">Base TCSTH</div>
        </div>
      </article>

      <article v-if="showFinancialCards" class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-wallet"></i></div>
        <div class="stat-content">
          <span class="stat-label">Revenu total</span>
          <strong class="stat-value">{{ formatMoney(totalRevenueAmount) }}</strong>
          <div class="stat-meta">Depuis toujours</div>
        </div>
      </article>

      <article v-if="showFinancialCards" class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-money-bill-wave"></i></div>
        <div class="stat-content">
          <span class="stat-label">Dépenses du mois</span>
          <strong class="stat-value">{{ formatMoney(monthlyExpensesAmount) }}</strong>
          <div class="stat-meta">Mois en cours</div>
        </div>
      </article>

      <article v-if="showFinancialCards" class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-sack-dollar"></i></div>
        <div class="stat-content">
          <span class="stat-label">Bénéfice net (est.)</span>
          <strong class="stat-value">{{ formatMoney(dashNetProfit) }}</strong>
          <div class="stat-meta">Revenu − Dépenses</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-landmark"></i></div>
        <div class="stat-content">
          <span class="stat-label">TCSTH payé OBR</span>
          <strong class="stat-value">{{ formatMoney(dashTcsthMonthlyObrPaid) }}</strong>
          <div class="stat-meta">Cumul versé</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-percent"></i></div>
        <div class="stat-content">
          <span class="stat-label">Taux annulation</span>
          <strong class="stat-value">{{ cancellationRate }}</strong>
          <div class="stat-meta">{{ cancelledBookingsCount }} annulée(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-user-plus"></i></div>
        <div class="stat-content">
          <span class="stat-label">Nouveaux clients</span>
          <strong class="stat-value">{{ newCustomersThisMonth }}</strong>
          <div class="stat-meta">Ce mois-ci</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-hotel"></i></div>
        <div class="stat-content">
          <span class="stat-label">CA chambres (mois)</span>
          <strong class="stat-value">{{ formatMoney(roomRevenueMonth) }}</strong>
          <div class="stat-meta">Hébergement en cours</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-champagne-glasses"></i></div>
        <div class="stat-content">
          <span class="stat-label">CA salles (mois)</span>
          <strong class="stat-value">{{ formatMoney(hallRevenueMonth) }}</strong>
          <div class="stat-meta">{{ currentMonthHallBookings.length }} réservation(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-credit-card"></i></div>
        <div class="stat-content">
          <span class="stat-label">Top paiement</span>
          <strong class="stat-value">{{ topPaymentMethodLabel }}</strong>
          <div class="stat-meta">{{ topPaymentMethod.count }} transaction(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-moon"></i></div>
        <div class="stat-content">
          <span class="stat-label">Nuitées facturées</span>
          <strong class="stat-value">{{ totalRoomNights.toLocaleString() }}</strong>
          <div class="stat-meta">{{ roomBookings.length }} séjour(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon success"><i class="fas fa-circle-check"></i></div>
        <div class="stat-content">
          <span class="stat-label">Réservations payées</span>
          <strong class="stat-value">{{ paidBookingsCount.toLocaleString() }}</strong>
          <div class="stat-meta">Statut payé</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-clock"></i></div>
        <div class="stat-content">
          <span class="stat-label">Réservations confirmées</span>
          <strong class="stat-value">{{ confirmedBookingsCount.toLocaleString() }}</strong>
          <div class="stat-meta">À venir</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon warning"><i class="fas fa-hourglass-start"></i></div>
        <div class="stat-content">
          <span class="stat-label">Réservations en attente</span>
          <strong class="stat-value">{{ pendingBookingsCount.toLocaleString() }}</strong>
          <div class="stat-meta">À confirmer</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon info"><i class="fas fa-building-columns"></i></div>
        <div class="stat-content">
          <span class="stat-label">CA total encaissements</span>
          <strong class="stat-value">{{ formatMoney(paymentsTotalAmount) }}</strong>
          <div class="stat-meta">{{ paidPaymentsCount }} paiement(s) validé(s)</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon primary"><i class="fas fa-box"></i></div>
        <div class="stat-content">
          <span class="stat-label">Matériaux référencés</span>
          <strong class="stat-value">{{ totalMaterialsCount.toLocaleString() }}</strong>
          <div class="stat-meta">Stock total</div>
        </div>
      </article>

      <article class="stat-card card">
        <div class="stat-icon danger"><i class="fas fa-fire-flame-curved"></i></div>
        <div class="stat-content">
          <span class="stat-label">Pertes matériaux</span>
          <strong class="stat-value">{{ formatMoney(materialLossesAmount) }}</strong>
          <div class="stat-meta">Estimation valeur</div>
        </div>
      </article>
    </section>

    <section class="micro-grid room-status-grid">
      <div class="section-head">
        <h2><i class="fas fa-door-open"></i> Statut des chambres</h2>
        <p>Répartition en temps réel</p>
      </div>
      <div class="micro-grid-body">
        <article class="mini-stat success">
          <span class="mini-stat-label">Disponibles</span>
          <strong class="mini-stat-value">{{ availableRoomsCount }}</strong>
          <div class="mini-stat-icon"><i class="fas fa-check-circle"></i></div>
        </article>
        <article class="mini-stat info">
          <span class="mini-stat-label">Réservées</span>
          <strong class="mini-stat-value">{{ reservedRoomsCount }}</strong>
          <div class="mini-stat-icon"><i class="fas fa-calendar-check"></i></div>
        </article>
        <article class="mini-stat primary">
          <span class="mini-stat-label">Occupées</span>
          <strong class="mini-stat-value">{{ occupiedRoomsStatusCount }}</strong>
          <div class="mini-stat-icon"><i class="fas fa-user"></i></div>
        </article>
        <article class="mini-stat warning">
          <span class="mini-stat-label">Nettoyage</span>
          <strong class="mini-stat-value">{{ cleaningRoomsCount }}</strong>
          <div class="mini-stat-icon"><i class="fas fa-broom"></i></div>
        </article>
        <article class="mini-stat danger">
          <span class="mini-stat-label">Maintenance</span>
          <strong class="mini-stat-value">{{ maintenanceRoomsCount }}</strong>
          <div class="mini-stat-icon"><i class="fas fa-screwdriver-wrench"></i></div>
        </article>
      </div>
    </section>

    <section class="micro-grid payment-methods-grid">
      <div class="section-head">
        <h2><i class="fas fa-money-bill-trend-up"></i> Méthodes de paiement</h2>
        <p>Répartition des transactions validées</p>
      </div>
      <div class="micro-grid-body">
        <article class="mini-stat method">
          <span class="mini-stat-label">Espèces</span>
          <strong class="mini-stat-value">{{ cashPaymentCount }}</strong>
          <div class="mini-stat-icon cash"><i class="fas fa-money-bill"></i></div>
        </article>
        <article class="mini-stat method">
          <span class="mini-stat-label">Virement</span>
          <strong class="mini-stat-value">{{ bankTransferCount }}</strong>
          <div class="mini-stat-icon bank"><i class="fas fa-building-columns"></i></div>
        </article>
        <article class="mini-stat method">
          <span class="mini-stat-label">Mobile Money</span>
          <strong class="mini-stat-value">{{ mobileMoneyCount }}</strong>
          <div class="mini-stat-icon mobile"><i class="fas fa-mobile-screen-button"></i></div>
        </article>
        <article class="mini-stat method">
          <span class="mini-stat-label">Carte bancaire</span>
          <strong class="mini-stat-value">{{ cardPaymentCount }}</strong>
          <div class="mini-stat-icon card"><i class="fas fa-credit-card"></i></div>
        </article>
        <article class="mini-stat method">
          <span class="mini-stat-label">Chèque</span>
          <strong class="mini-stat-value">{{ checkPaymentCount }}</strong>
          <div class="mini-stat-icon check"><i class="fas fa-money-check"></i></div>
        </article>
        <article class="mini-stat method total">
          <span class="mini-stat-label">Total paiements</span>
          <strong class="mini-stat-value">{{ paidPaymentsCount }}</strong>
          <div class="mini-stat-icon total-icon"><i class="fas fa-chart-simple"></i></div>
        </article>
      </div>
    </section>

    <section class="hotel-overview-grid">
      <article class="focus-card card">
        <div class="focus-head">
          <div>
            <h2>Réception du jour</h2>
            <p>Vue rapide pour l'accueil, les arrivées et les départs.</p>
          </div>
          <NuxtLink to="/admin/rooms" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Front desk</span>
          </NuxtLink>
        </div>
        <div class="focus-metrics three">
          <div class="focus-metric">
            <span>Arrivées attendues</span>
            <strong>{{ todayPendingArrivals }}</strong>
          </div>
          <div class="focus-metric">
            <span>Check-ins</span>
            <strong>{{ todaysCheckInsFormatted }}</strong>
          </div>
          <div class="focus-metric">
            <span>Check-outs</span>
            <strong>{{ todaysCheckOutsFormatted }}</strong>
          </div>
        </div>
        <div class="focus-list">
          <div class="focus-list-row">
            <span>Séjours en cours</span>
            <strong>{{ inHouseGuestsCount }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Notifications à traiter</span>
            <strong>{{ unreadCount }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Paiements en attente</span>
            <strong>{{ pendingPaymentsFormatted }}</strong>
          </div>
        </div>
      </article>

      <article class="focus-card card accent">
        <div class="focus-head">
          <div>
            <h2>Capacité chambres</h2>
            <p>Disponibilité, occupation et rotation ménage / maintenance.</p>
          </div>
          <span class="focus-badge">{{ roomOccupancyRateLabel }}</span>
        </div>
        <div class="occupancy-progress">
          <div class="occupancy-track">
            <span class="occupancy-fill" :style="{ width: occupancyProgressWidth }"></span>
          </div>
          <div class="occupancy-caption">
            <span>{{ occupiedRoomsTodayCount }} occupée(s)</span>
            <strong>{{ activeRoomsCount }} chambre(s) active(s)</strong>
          </div>
        </div>
        <div class="status-chip-grid">
          <div class="status-chip">
            <span>Disponible</span>
            <strong>{{ roomStatusCounts.available || 0 }}</strong>
          </div>
          <div class="status-chip info">
            <span>Réservée</span>
            <strong>{{ roomStatusCounts.reserved || 0 }}</strong>
          </div>
          <div class="status-chip success">
            <span>Occupée</span>
            <strong>{{ roomStatusCounts.occupied || 0 }}</strong>
          </div>
          <div class="status-chip warning">
            <span>Nettoyage</span>
            <strong>{{ roomStatusCounts.cleaning || 0 }}</strong>
          </div>
          <div class="status-chip danger">
            <span>Maintenance</span>
            <strong>{{ roomStatusCounts.maintenance || 0 }}</strong>
          </div>
        </div>
      </article>

      <article class="focus-card card">
        <div class="focus-head">
          <div>
            <h2>Encaissement & relance</h2>
            <p>Suivi des entrées de caisse et des soldes ouverts.</p>
          </div>
          <NuxtLink to="/admin/payments" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-credit-card"></i>
            <span class="btn-label">Paiements</span>
          </NuxtLink>
        </div>
        <div class="focus-metrics">
          <div class="focus-metric">
            <span>Aujourd'hui</span>
            <strong>{{ formatMoney(revenueTodayAmount) }}</strong>
          </div>
          <div class="focus-metric">
            <span>7 derniers jours</span>
            <strong>{{ formatMoney(revenueWeekAmount) }}</strong>
          </div>
        </div>
        <div class="focus-list">
          <div class="focus-list-row">
            <span>Reste à encaisser chambres</span>
            <strong>{{ formatMoney(roomBalanceDueAmount) }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Revenu total encaissé</span>
            <strong>{{ formatMoney(totalRevenueAmount) }}</strong>
          </div>
          <div class="focus-list-row">
            <span>Stock critique à suivre</span>
            <strong>{{ stockAlertsFormatted }}</strong>
          </div>
        </div>
      </article>
    </section>

    <section class="dashboard-grid">
      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Réservations récentes</h2>
            <p>Dernières entrées enregistrées.</p>
          </div>
          <NuxtLink to="/admin/bookings" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Voir tout</span>
          </NuxtLink>
        </div>

        <div v-if="loadingBookings" class="panel-loading">
          <div v-for="n in 5" :key="`sk-b-${n}`" class="row-skeleton"></div>
        </div>

        <div v-else-if="recentBookings.length === 0" class="panel-empty">
          <i class="fas fa-inbox"></i>
          <div>
            <strong>Aucune réservation</strong>
            <div class="muted">Aucun enregistrement récent.</div>
          </div>
        </div>

        <div v-else class="rows">
          <div v-for="booking in recentBookings" :key="booking.id" class="row row-clickable" @click="openBookingDetails(booking)">
            <div class="row-main">
              <div class="row-title">{{ booking.customer_name || '-' }}</div>
              <div class="row-sub">
                <span class="pill">{{ booking.code || '-' }}</span>
                <span class="dot">•</span>
                <span v-html="getBookingItemSummary(booking).html"></span>
                <span class="dot">•</span>
                <span>{{ booking.start_date }} → {{ booking.end_date }}</span>
              </div>
            </div>
            <div class="row-side">
              <div class="row-value">{{ formatMoney(booking.total_price || 0) }}</div>
              <span class="badge" :class="badgeClass(booking.status)">{{ statusLabel(booking.status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Paiements récents</h2>
            <p>Dernières transactions enregistrées.</p>
          </div>
          <NuxtLink to="/admin/payments" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Voir tout</span>
          </NuxtLink>
        </div>

        <div v-if="loadingPayments" class="panel-loading">
          <div v-for="n in 5" :key="`sk-p-${n}`" class="row-skeleton"></div>
        </div>

        <div v-else-if="recentPayments.length === 0" class="panel-empty">
          <i class="fas fa-inbox"></i>
          <div>
            <strong>Aucun paiement</strong>
            <div class="muted">Aucune transaction récente.</div>
          </div>
        </div>

        <div v-else class="rows">
          <div v-for="payment in recentPayments" :key="payment.id" class="row row-clickable" @click="openPaymentDetails(payment)">
            <div class="row-main">
              <div class="row-title">{{ payment.reference || payment.code || '-' }}</div>
              <div class="row-sub">
                <span class="pill">{{ payment.booking_code || payment.booking?.code || '-' }}</span>
                <span class="dot">•</span>
                <span>{{ payment.method || '-' }}</span>
                <span class="dot">•</span>
                <span>{{ String(payment.date || '').slice(0, 10) || '-' }}</span>
              </div>
            </div>
            <div class="row-side">
              <div class="row-value">{{ formatMoney(payment.amount || 0) }}</div>
              <span class="badge" :class="paymentStatusClass(payment.status)">{{ paymentStatusLabel(payment.status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Statut des chambres</h2>
            <p>Disponibilité actuelle, entretien et occupation.</p>
          </div>
          <NuxtLink to="/admin/rooms" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-bed"></i>
            <span class="btn-label">Gérer</span>
          </NuxtLink>
        </div>

        <div class="alerts room-status-grid">
          <div class="alert-card">
            <div class="alert-icon"><i class="fas fa-circle-check"></i></div>
            <div>
              <div class="alert-title">Disponibles</div>
              <div class="alert-value">{{ roomStatusCounts.available || 0 }}</div>
            </div>
          </div>
          <div class="alert-card info">
            <div class="alert-icon"><i class="fas fa-bookmark"></i></div>
            <div>
              <div class="alert-title">Réservées</div>
              <div class="alert-value">{{ roomStatusCounts.reserved || 0 }}</div>
            </div>
          </div>
          <div class="alert-card">
            <div class="alert-icon"><i class="fas fa-bed"></i></div>
            <div>
              <div class="alert-title">Occupées</div>
              <div class="alert-value">{{ roomStatusCounts.occupied || 0 }}</div>
            </div>
          </div>
          <div class="alert-card warning">
            <div class="alert-icon"><i class="fas fa-soap"></i></div>
            <div>
              <div class="alert-title">Nettoyage</div>
              <div class="alert-value">{{ roomStatusCounts.cleaning || 0 }}</div>
            </div>
          </div>
          <div class="alert-card danger">
            <div class="alert-icon"><i class="fas fa-screwdriver-wrench"></i></div>
            <div>
              <div class="alert-title">Maintenance</div>
              <div class="alert-value">{{ roomStatusCounts.maintenance || 0 }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <div class="panel-head">
          <div>
            <h2>Alertes & Stock</h2>
            <p>Ruptures, seuils et actions rapides.</p>
          </div>
          <NuxtLink to="/admin/materials" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-arrow-right"></i>
            <span class="btn-label">Matériel</span>
          </NuxtLink>
        </div>

        <div class="alerts">
          <div class="alert-card" :class="{ danger: outOfStock.length > 0 }">
            <div class="alert-icon"><i class="fas fa-triangle-exclamation"></i></div>
            <div>
              <div class="alert-title">Rupture</div>
              <div class="alert-value">{{ outOfStock.length }}</div>
            </div>
          </div>
          <div class="alert-card" :class="{ warning: lowStock.length > 0 }">
            <div class="alert-icon"><i class="fas fa-bell"></i></div>
            <div>
              <div class="alert-title">Seuil</div>
              <div class="alert-value">{{ lowStock.length }}</div>
            </div>
          </div>
        </div>

        <div class="mini-list">
          <div v-for="item in stockPreview" :key="`m-${item.id}`" class="mini-row mini-row-clickable" @click="openMaterialDetails(item)">
            <div class="mini-main">
              <div class="mini-title">{{ item.name }}</div>
              <div class="mini-sub">{{ item.category || '—' }}</div>
            </div>
            <div class="mini-side">
              <span class="mini-pill" :class="Number(item.available_quantity || 0) <= 0 ? 'danger' : 'warning'">
                {{ Number(item.available_quantity || 0) <= 0 ? 'Rupture' : 'Seuil' }}
              </span>
              <strong>{{ Number(item.available_quantity || 0) }}</strong>
            </div>
          </div>

          <div v-if="!stockPreview.length" class="panel-empty compact">
            <i class="fas fa-circle-check"></i>
            <div>
              <strong>Aucune alerte stock</strong>
              <div class="muted">Tout est OK.</div>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card span-2">
        <div class="panel-head">
          <div>
            <h2>Notifications récentes</h2>
            <p>Dernières alertes du système.</p>
          </div>
          <NuxtLink to="/admin/notifications" class="btn btn-outline btn-sm admin-head-btn">
            <i class="fas fa-bell"></i>
            <span class="btn-label">Voir tout</span>
          </NuxtLink>
        </div>

        <div v-if="loadingNotifications" class="panel-loading">
          <div v-for="n in 4" :key="`sk-n-${n}`" class="row-skeleton"></div>
        </div>

        <div v-else-if="recentNotificationsList.length === 0" class="panel-empty compact">
          <i class="fas fa-inbox"></i>
          <div>
            <strong>Aucune notification</strong>
            <div class="muted">Rien à signaler.</div>
          </div>
        </div>

        <div v-else class="rows compact">
          <div v-for="n in recentNotificationsList" :key="n.id" class="row compact row-clickable" @click="openNotificationDetails(n)">
            <div class="row-main">
              <div class="row-title">{{ n.title }}</div>
              <div class="row-sub">
                <span class="pill">{{ typeLabel(n.type) }}</span>
                <span class="dot">•</span>
                <span>{{ formatTimeAgo(n.timestamp) }}</span>
              </div>
              <div class="row-message">{{ n.message }}</div>
            </div>
            <div class="row-side">
              <span class="badge" :class="n.read ? 'badge-info' : 'badge-warning'">{{ n.read ? 'Lue' : 'Non lue' }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from '#imports'
definePageMeta({ layout: 'admin' })

import { api } from '~/composables/useApi'
import { useMoney } from '~/composables/useMoney'
import { canSeeSyntheticRevenue, getStoredUser } from '~/composables/useRoleAccess'
import {
  unreadCount,
  recentNotifications,
  loadingNotifications,
  fetchNotifications,
  formatTimeAgo,
  markAsRead,
} from '~/composables/useNotifications'

const router = useRouter()

const { formatMoney } = useMoney()

const loading = ref(false)
const loadingSummary = ref(false)
const loadingBookings = ref(false)
const loadingPayments = ref(false)
const loadingMaterials = ref(false)

const summary = ref({
  total_bookings: 0,
  active_halls: 0,
  active_rooms: 0,
  total_revenue: 0,
  monthly_expenses: 0,
  pending_payments: 0,
  material_losses: 0,
  room_occupancy_rate_today: 0,
  occupied_rooms_today: 0,
  todays_check_ins: 0,
  todays_check_outs: 0,
  room_status_counts: {
    available: 0,
    reserved: 0,
    occupied: 0,
    cleaning: 0,
    maintenance: 0,
  },
})

const bookings = ref([])
const payments = ref([])
const materials = ref([])
const currentUser = ref({})

const toYmd = (d) => {
  const dt = (d instanceof Date) ? d : new Date(d)
  if (Number.isNaN(dt.getTime())) return ''
  const y = dt.getFullYear()
  const m = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const TCSTH_RATE_PCT = 5
const TCSTH_DIVISOR = 1 + (TCSTH_RATE_PCT / 100)
const TCSTH_LS_KEY = 'hall_ui_tcsth_status_v1'
const _tcsthRound = (n) => Math.round((Number(n || 0) + Number.EPSILON) * 100) / 100
const _tcsthExtractHT = (ttc) => {
  const v = Number(ttc || 0)
  return v > 0 ? _tcsthRound(v / TCSTH_DIVISOR) : 0
}
const _tcsthExtractTax = (ttc) => {
  const v = Number(ttc || 0)
  return v > 0 ? _tcsthRound(v - _tcsthExtractHT(v)) : 0
}
const _bookingIsRoomTcsth = (b) => String(b?.booking_type || '') === 'room'
const _tcsthBookingHT = (b) => Number(b?.subtotal_ht ?? _tcsthExtractHT(b?.total_price))
const _tcsthBookingTax = (b) => Number(b?.tva_amount ?? _tcsthExtractTax(b?.total_price))
const _tcsthReadAllObrPaid = () => {
  if (!process.client) return {}
  try {
    const raw = localStorage.getItem(TCSTH_LS_KEY) || '{}'
    return JSON.parse(raw) || {}
  } catch { return {} }
}

const todayYmd = computed(() => toYmd(new Date()))

const showFinancialCards = computed(() => canSeeSyntheticRevenue(currentUser.value))

const totalBookingsCount = computed(() => Number(summary.value.total_bookings || 0))
const activeHallsCount = computed(() => Number(summary.value.active_halls || 0))
const activeRoomsCount = computed(() => Number(summary.value.active_rooms || 0))
const pendingPaymentsCount = computed(() => Number(summary.value.pending_payments || 0))
const totalRevenueAmount = computed(() => Number(summary.value.total_revenue || 0))
const monthlyExpensesAmount = computed(() => Number(summary.value.monthly_expenses || 0))
const occupiedRoomsTodayCount = computed(() => Number(summary.value.occupied_rooms_today || 0))
const todaysCheckInsCount = computed(() => Number(summary.value.todays_check_ins || 0))
const todaysCheckOutsCount = computed(() => Number(summary.value.todays_check_outs || 0))
const roomStatusCounts = computed(() => summary.value.room_status_counts || {})
const roomOccupancyRateLabel = computed(() => `${Number(summary.value.room_occupancy_rate_today || 0).toFixed(1)}%`)

const totalBookingsFormatted = computed(() => totalBookingsCount.value.toLocaleString())
const activeHallsFormatted = computed(() => activeHallsCount.value.toLocaleString())
const pendingPaymentsFormatted = computed(() => pendingPaymentsCount.value.toLocaleString())
const todaysCheckInsFormatted = computed(() => todaysCheckInsCount.value.toLocaleString())
const todaysCheckOutsFormatted = computed(() => todaysCheckOutsCount.value.toLocaleString())

const addDays = (ymd, days) => {
  const base = new Date(`${ymd}T00:00:00`)
  if (Number.isNaN(base.getTime())) return ''
  base.setDate(base.getDate() + days)
  return toYmd(base)
}

const normalizeDate = (value) => String(value || '').slice(0, 10)

const overlapsDate = (start, end, ymd) => {
  const s = normalizeDate(start)
  const e = normalizeDate(end)
  if (!s || !e || !ymd) return false
  return s <= ymd && e >= ymd
}

const displayBookingsToday = computed(() => {
  const t = todayYmd.value
  return (bookings.value || []).filter(b => overlapsDate(b.start_date, b.end_date, t)).length
})

const roomBookings = computed(() => {
  const source = Array.isArray(bookings.value) ? bookings.value : []
  return source.filter((booking) => String(booking.booking_type || '') === 'room' && String(booking.status || '') !== 'cancelled')
})

const todayPendingArrivals = computed(() => {
  const t = todayYmd.value
  return roomBookings.value.filter((booking) => {
    const status = String(booking.status || '')
    return normalizeDate(booking.start_date) === t
      && !booking.checked_in_at
      && ['pending', 'confirmed', 'paid'].includes(status)
  }).length
})

const inHouseGuestsCount = computed(() => {
  return roomBookings.value.filter(booking => booking.checked_in_at && !booking.checked_out_at).length
})

const revenueTodayAmount = computed(() => {
  const t = todayYmd.value
  return (payments.value || []).reduce((sum, payment) => {
    if (String(payment.status || '') !== 'paid') return sum
    return normalizeDate(payment.date || payment.created_at) === t ? sum + Number(payment.amount || 0) : sum
  }, 0)
})

const revenueWeekAmount = computed(() => {
  const end = todayYmd.value
  const start = addDays(end, -6)
  return (payments.value || []).reduce((sum, payment) => {
    if (String(payment.status || '') !== 'paid') return sum
    const ymd = normalizeDate(payment.date || payment.created_at)
    return ymd >= start && ymd <= end ? sum + Number(payment.amount || 0) : sum
  }, 0)
})

const roomBalanceDueAmount = computed(() => {
  return roomBookings.value.reduce((sum, booking) => {
    const remaining = Number(booking.remaining_amount || 0)
    return remaining > 0 ? sum + remaining : sum
  }, 0)
})

const dashTcsthBookings = computed(() => {
  return (bookings.value || []).filter(b => _bookingIsRoomTcsth(b))
})
const dashTcsthHT = computed(() => _tcsthRound(
  dashTcsthBookings.value.reduce((s, b) => s + _tcsthBookingHT(b), 0)
))
const dashTcsthCollected = computed(() => _tcsthRound(
  dashTcsthBookings.value.reduce((s, b) => s + _tcsthBookingTax(b), 0)
))
const dashTcsthMonthlyObrPaid = computed(() => {
  const map = new Map()
  for (const b of dashTcsthBookings.value) {
    const ref = new Date(b.created_at || b.start_date)
    const Y = ref.getFullYear()
    const M = ref.getMonth()
    const key = `${Y}-${String(M + 1).padStart(2, '0')}`
    if (!map.has(key)) map.set(key, { key, tva: 0 })
    const r = map.get(key)
    r.tva += _tcsthBookingTax(b)
  }
  const paidAll = _tcsthReadAllObrPaid()
  let totalPaid = 0
  for (const r of map.values()) {
    const p = _tcsthRound(Number(paidAll[r.key]?.amount || (paidAll[r.key]?.paid ? r.tva : 0)))
    totalPaid += p
  }
  return _tcsthRound(totalPaid)
})
const dashTcsthPending = computed(() => _tcsthRound(
  Math.max(0, dashTcsthCollected.value - dashTcsthMonthlyObrPaid.value)
))
const dashNetProfit = computed(() => _tcsthRound(
  Math.max(0, totalRevenueAmount.value - monthlyExpensesAmount.value)
))

const currentMonthKey = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
})
const dashTcsthMonthlyBookings = computed(() => {
  const cmk = currentMonthKey.value
  return dashTcsthBookings.value.filter(b => {
    const ref = new Date(b.start_date || b.created_at)
    const k = `${ref.getFullYear()}-${String(ref.getMonth() + 1).padStart(2, '0')}`
    return k === cmk
  })
})
const dashTcsthMonthHT = computed(() => _tcsthRound(
  dashTcsthMonthlyBookings.value.reduce((s, b) => s + _tcsthBookingHT(b), 0)
))
const dashTcsthMonthCollected = computed(() => _tcsthRound(
  dashTcsthMonthlyBookings.value.reduce((s, b) => s + _tcsthBookingTax(b), 0)
))
const dashTcsthMonthObrPaid = computed(() => _tcsthRound(
  Number(_tcsthReadAllObrPaid()[currentMonthKey.value]?.amount || 0)
))

const allBookingsPaidOrCancelled = computed(() => {
  const src = Array.isArray(bookings.value) ? bookings.value : []
  return src.filter(b => String(b?.status || '').trim())
})
const cancelledBookingsCount = computed(() => {
  const src = Array.isArray(bookings.value) ? bookings.value : []
  return src.filter(b => String(b?.status || '').toLowerCase() === 'cancelled').length
})
const totalBookingsWithStatus = computed(() => Math.max(1, allBookingsPaidOrCancelled.value.length))
const cancellationRate = computed(() => {
  const rate = (cancelledBookingsCount.value / totalBookingsWithStatus.value) * 100
  return `${Number.isFinite(rate) ? rate.toFixed(1) : '0.0'}%`
})

const totalRoomNights = computed(() => {
  let nights = 0
  for (const b of roomBookings.value) {
    const s = new Date(normalizeDate(b.start_date))
    const e = new Date(normalizeDate(b.end_date))
    if (!Number.isNaN(s.getTime()) && !Number.isNaN(e.getTime())) {
      const n = Math.max(1, Math.round((e.getTime() - s.getTime()) / (24 * 3600 * 1000)))
      nights += n
    }
  }
  return nights
})
const totalRoomRevenue = computed(() => _tcsthRound(
  roomBookings.value.reduce((s, b) => s + Number(b?.total_price || 0), 0)
))
const avgPricePerNight = computed(() => {
  const n = Math.max(1, totalRoomNights.value)
  return _tcsthRound(totalRoomRevenue.value / n)
})
const avgStayNights = computed(() => {
  const nb = Math.max(1, roomBookings.value.length)
  const avg = totalRoomNights.value / nb
  return Number.isFinite(avg) ? avg.toFixed(1) : '0.0'
})

const hallBookings = computed(() => {
  const src = Array.isArray(bookings.value) ? bookings.value : []
  return src.filter(b => String(b.booking_type || '').toLowerCase() === 'hall'
    && String(b.status || '').toLowerCase() !== 'cancelled')
})
const currentMonthHallBookings = computed(() => {
  const cmk = currentMonthKey.value
  return hallBookings.value.filter(b => {
    const ref = new Date(b.start_date || b.created_at)
    const k = `${ref.getFullYear()}-${String(ref.getMonth() + 1).padStart(2, '0')}`
    return k === cmk
  })
})
const hallRevenueMonth = computed(() => _tcsthRound(
  currentMonthHallBookings.value.reduce((s, b) => s + Number(b?.total_price || 0), 0)
))
const roomRevenueMonth = computed(() => {
  const cmk = currentMonthKey.value
  const rb = roomBookings.value.filter(b => {
    const ref = new Date(b.start_date || b.created_at)
    const k = `${ref.getFullYear()}-${String(ref.getMonth() + 1).padStart(2, '0')}`
    return k === cmk
  })
  return _tcsthRound(rb.reduce((s, b) => s + Number(b?.total_price || 0), 0))
})

const totalRevenueMonth = computed(() => _tcsthRound(roomRevenueMonth.value + hallRevenueMonth.value))
const avgPaymentAmount = computed(() => {
  const paid = (payments.value || []).filter(p => String(p.status || '').toLowerCase() === 'paid')
  if (!paid.length) return 0
  const total = paid.reduce((s, p) => s + Number(p.amount || 0), 0)
  return _tcsthRound(total / paid.length)
})
const confirmedBookingsCount = computed(() => {
  return (bookings.value || []).filter(b => String(b.status || '').toLowerCase() === 'confirmed').length
})
const pendingBookingsCount = computed(() => {
  return (bookings.value || []).filter(b => String(b.status || '').toLowerCase() === 'pending').length
})
const paidBookingsCount = computed(() => {
  return (bookings.value || []).filter(b => String(b.status || '').toLowerCase() === 'paid').length
})
const uniqueCustomersCount = computed(() => {
  const s = new Set()
  for (const b of (bookings.value || [])) {
    const key = (String(b.customer_id || '') || `__name:${String(b.customer_name || '').trim().toLowerCase()}`)
    if (key) s.add(key)
  }
  return s.size
})
const totalMaterialsCount = computed(() => (materials.value || []).length)
const materialLossesAmount = computed(() => Number(summary.value.material_losses || 0))
const availableRoomsCount = computed(() => Number(roomStatusCounts.value.available || 0))
const reservedRoomsCount = computed(() => Number(roomStatusCounts.value.reserved || 0))
const occupiedRoomsStatusCount = computed(() => Number(roomStatusCounts.value.occupied || 0))
const cleaningRoomsCount = computed(() => Number(roomStatusCounts.value.cleaning || 0))
const maintenanceRoomsCount = computed(() => Number(roomStatusCounts.value.maintenance || 0))
const paidPaymentsCount = computed(() => (payments.value || []).filter(p => String(p.status || '').toLowerCase() === 'paid').length)
const paymentsTotalAmount = computed(() => _tcsthRound(
  (payments.value || []).filter(p => String(p.status || '').toLowerCase() === 'paid').reduce((s, p) => s + Number(p.amount || 0), 0)
))
const methodCount = (m) => (paymentMethodCounts.value.find(x => String(x.method).toLowerCase() === String(m).toLowerCase())?.count || 0)
const cashPaymentCount = computed(() => methodCount('cash'))
const bankTransferCount = computed(() => methodCount('bank_transfer'))
const mobileMoneyCount = computed(() => methodCount('mobile_money'))
const cardPaymentCount = computed(() => methodCount('card'))
const checkPaymentCount = computed(() => methodCount('check'))
const totalHallBookingsCount = computed(() => hallBookings.value.length)
const totalRoomBookingsCount = computed(() => roomBookings.value.length)

const newCustomersThisMonth = computed(() => {
  const cmk = currentMonthKey.value
  const seen = new Set()
  const monthSet = new Set()
  for (const b of (bookings.value || [])) {
    const dateRef = new Date(b.created_at || b.start_date)
    const k = `${dateRef.getFullYear()}-${String(dateRef.getMonth() + 1).padStart(2, '0')}`
    const customerKey = (String(b.customer_id || '') || `__name:${String(b.customer_name || '').trim().toLowerCase()}`)
    if (!customerKey) continue
    if (k < cmk) seen.add(customerKey)
    if (k === cmk) monthSet.add(customerKey)
  }
  let count = 0
  for (const key of monthSet) if (!seen.has(key)) count += 1
  return count
})

const paymentMethodCounts = computed(() => {
  const map = new Map()
  for (const p of (payments.value || [])) {
    if (String(p.status || '').toLowerCase() !== 'paid') continue
    const m = String(p.method || 'Autre').trim() || 'Autre'
    map.set(m, (map.get(m) || 0) + 1)
  }
  const arr = Array.from(map.entries()).map(([method, count]) => ({ method, count }))
  arr.sort((a, b) => b.count - a.count)
  return arr
})
const topPaymentMethod = computed(() => {
  if (!paymentMethodCounts.value.length) return { method: '—', count: 0 }
  return paymentMethodCounts.value[0]
})
const topPaymentMethodLabel = computed(() => {
  const m = topPaymentMethod.value.method
  const map = { 'cash': 'Espèces', 'bank_transfer': 'Virement', 'mobile_money': 'Mobile Money', 'card': 'Carte', 'check': 'Chèque' }
  return map[String(m).toLowerCase()] || m
})

const occupiedHallsTodayCount = computed(() => {
  const t = todayYmd.value
  return hallBookings.value.filter(b => overlapsDate(b.start_date, b.end_date, t)).length
})
const hallOccupancyRate = computed(() => {
  const total = Math.max(1, activeHallsCount.value)
  const rate = Math.min(100, (occupiedHallsTodayCount.value / total) * 100)
  return Number.isFinite(rate) ? rate.toFixed(1) : '0.0'
})

const occupancyProgressWidth = computed(() => {
  const rate = Number(summary.value.room_occupancy_rate_today || 0)
  const clamped = Math.min(100, Math.max(0, Number.isFinite(rate) ? rate : 0))
  return `${clamped}%`
})

const recentBookings = computed(() => {
  const source = Array.isArray(bookings.value) ? bookings.value : []
  return source
    .slice()
    .sort((a, b) => {
      const ad = new Date(a.created_at || a.createdAt || 0).getTime()
      const bd = new Date(b.created_at || b.createdAt || 0).getTime()
      if (Number.isFinite(ad) && Number.isFinite(bd) && ad !== bd) return bd - ad
      return Number(b.id || 0) < Number(a.id || 0) ? -1 : 1
    })
    .slice(0, 6)
})

const recentPayments = computed(() => {
  const source = Array.isArray(payments.value) ? payments.value : []
  return source
    .slice()
    .sort((a, b) => {
      const ad = new Date(a.created_at || a.createdAt || a.date || 0).getTime()
      const bd = new Date(b.created_at || b.createdAt || b.date || 0).getTime()
      if (Number.isFinite(ad) && Number.isFinite(bd) && ad !== bd) return bd - ad
      return Number(b.id || 0) < Number(a.id || 0) ? -1 : 1
    })
    .slice(0, 6)
})

const STOCK_LOW_PCT = 0.15
const STOCK_LOW_FALLBACK = 5
const outOfStock = computed(() => {
  return (materials.value || []).filter((m) => Number(m.available_quantity || 0) <= 0)
})

const lowStock = computed(() => {
  return (materials.value || []).filter((m) => {
    const available = Number(m.available_quantity || 0)
    if (available <= 0) return false
    const total = Number(m.total_quantity || 0)
    if (total > 0) {
      return available <= Math.max(1, Math.ceil(total * STOCK_LOW_PCT))
    }
    return available > 0 && available < STOCK_LOW_FALLBACK
  })
})

const stockPreview = computed(() => {
  const items = [
    ...outOfStock.value.map(m => ({ ...m, __tone: 'danger' })),
    ...lowStock.value.map(m => ({ ...m, __tone: 'warning' })),
  ]
  return items.slice(0, 6)
})

const stockAlertsCount = computed(() => Number(outOfStock.value.length + lowStock.value.length))
const stockAlertsFormatted = computed(() => stockAlertsCount.value.toLocaleString())

const recentNotificationsList = computed(() => {
  const list = Array.isArray(recentNotifications.value) ? recentNotifications.value : []
  return list.slice(0, 6)
})

const badgeClass = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'badge-success'
  if (s === 'confirmed') return 'badge-info'
  if (s === 'cancelled') return 'badge-danger'
  return 'badge-warning'
}

const statusLabel = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'Payé'
  if (s === 'confirmed') return 'Confirmé'
  if (s === 'cancelled') return 'Annulé'
  return 'En attente'
}

const paymentStatusClass = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'badge-success'
  if (s === 'failed') return 'badge-danger'
  return 'badge-warning'
}

const paymentStatusLabel = (status) => {
  const s = String(status || '')
  if (s === 'paid') return 'Payé'
  if (s === 'failed') return 'Échoué'
  return 'En attente'
}

const typeLabel = (type) => {
  const t = String(type || '').toLowerCase()
  if (t === 'success') return 'Succès'
  if (t === 'warning') return 'Alerte'
  if (t === 'danger') return 'Urgent'
  if (t === 'info') return 'Info'
  return 'Notification'
}

const openBookingDetails = async (booking) => {
  if (!booking?.id) return
  const focus = String(Date.now())
  try {
    await nextTick()
    await router.push({ path: '/admin/bookings', query: { view: String(booking.id), focus } })
  } catch (err) {
    console.error('[dashboard] openBookingDetails failed:', err)
  }
}

const openPaymentDetails = async (payment) => {
  if (!payment?.id) return
  const focus = String(Date.now())
  try {
    await nextTick()
    await router.push({ path: '/admin/payments', query: { view: String(payment.id), focus } })
  } catch (err) {
    console.error('[dashboard] openPaymentDetails failed:', err)
  }
}

const openMaterialDetails = async (material) => {
  if (!material?.id) return
  const focus = String(Date.now())
  try {
    await nextTick()
    await router.push({ path: '/admin/materials', query: { view: String(material.id), focus } })
  } catch (err) {
    console.error('[dashboard] openMaterialDetails failed:', err)
  }
}

const getNotificationTarget = (notification) => {
  const focus = String(Date.now())
  if (notification?.payment) {
    return { path: '/admin/payments', query: { view: String(notification.payment), focus } }
  }
  if (notification?.booking) {
    return { path: '/admin/bookings', query: { view: String(notification.booking), focus } }
  }
  if (notification?.material) {
    return { path: '/admin/materials', query: { view: String(notification.material), focus } }
  }
  return null
}

const openNotificationDetails = async (notification) => {
  if (!notification) return
  if (!notification.read) {
    await markAsRead(notification.id).catch(() => {})
  }
  const target = getNotificationTarget(notification)
  if (target) {
    try {
      await nextTick()
      await router.push(target)
      return
    } catch (err) {
      console.error('[dashboard] openNotificationDetails push target failed:', err)
    }
  }
  try {
    await router.push('/admin/notifications')
  } catch (err) {
    console.error('[dashboard] openNotificationDetails fallback failed:', err)
  }
}

const getBookingItemNames = (booking) => {
  const b = booking || {}
  const type = String(b.booking_type || '').toLowerCase()
  if (type === 'hall') {
    const name = b.hall_name || (b.hall && b.hall.name) || ''
    return name ? [name] : []
  }
  if (type !== 'room') return []
  const names = []
  if (Array.isArray(b.room_stays) && b.room_stays.length) {
    for (const s of b.room_stays) {
      const n = String(s?.room_display || '').trim()
      if (n) names.push(n)
    }
  }
  if (!names.length && String(b.room_display_summary || '').trim()) {
    const parts = String(b.room_display_summary).split(',').map(s => s.trim()).filter(Boolean)
    names.push(...parts)
  }
  if (!names.length && String(b.room_display || '').trim()) {
    names.push(String(b.room_display).trim())
  }
  const uniq = Array.from(new Set(names))
  if (uniq.length) return uniq
  const cnt = Number(b.room_count || 0)
  if (cnt > 0) return [cnt > 1 ? `${cnt} chambres` : 'Chambre']
  return []
}

const getBookingItemSummary = (booking) => {
  const names = getBookingItemNames(booking)
  if (!names.length) {
    return { html: '<span class="muted">—</span>', plain: '-' }
  }
  if (names.length === 1) {
    return { html: escapeHtml(names[0]), plain: names[0] }
  }
  if (names.length === 2) {
    return { html: `${escapeHtml(names[0])} <span style="color:var(--gray-400)">&</span> ${escapeHtml(names[1])}`, plain: `${names[0]} & ${names[1]}` }
  }
  return {
    html: `${escapeHtml(names[0])}, ${escapeHtml(names[1])}, <span class="text-cta">voir plus…</span>`,
    plain: `${names[0]}, ${names[1]}, voir plus…`,
  }
}

const escapeHtml = (s) => String(s || '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))

const fetchSummary = async () => {
  loadingSummary.value = true
  try {
    const { data } = await api.get('summary/')
    summary.value = data || summary.value
  } catch {
    summary.value = { ...summary.value }
  } finally {
    loadingSummary.value = false
  }
}

const fetchBookings = async () => {
  loadingBookings.value = true
  try {
    const { data } = await api.get('bookings/')
    bookings.value = Array.isArray(data) ? data : []
  } catch {
    bookings.value = []
  } finally {
    loadingBookings.value = false
  }
}

const fetchPayments = async () => {
  loadingPayments.value = true
  try {
    const { data } = await api.get('payments/')
    payments.value = Array.isArray(data) ? data : []
  } catch {
    payments.value = []
  } finally {
    loadingPayments.value = false
  }
}

const fetchMaterials = async () => {
  loadingMaterials.value = true
  try {
    const { data } = await api.get('materials/')
    materials.value = Array.isArray(data) ? data : []
  } catch {
    materials.value = []
  } finally {
    loadingMaterials.value = false
  }
}

const refreshAll = async () => {
  loading.value = true
  currentUser.value = getStoredUser()
  await Promise.allSettled([
    fetchSummary(),
    fetchBookings(),
    fetchPayments(),
    fetchMaterials(),
    fetchNotifications({ force: true }),
  ])
  loading.value = false
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
  display: grid;
  gap: var(--space-7);
}

.hero {
  padding: 0;
  overflow: hidden;
  border: 1px solid #1e293b;
  border-radius: 22px;
  background:
    linear-gradient(135deg, #0b1220 0%, #111827 45%, #1f2937 100%);
  color: #ffffff;
  display: grid;
  grid-template-columns: 1.05fr 1.35fr;
  gap: 0;

  box-shadow: 0 5px 0 0 #1e293b, 0 16px 32px #0b1220;
}

.hero-copy {
  padding: 25px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin: var(--space-4) 0 var(--space-4) var(--space-4);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(17,24,39,0.85), rgba(15,23,42,0.7));
  border: 1px solid #1e293b;

}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  border-radius: 999px;
  background: #fef3c7;
  border: 1px solid #fde68a;
  box-shadow: 0 2px 0 0 #fde68a;
  color: #78350f;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.65rem;
  width: fit-content;
}

.hero-title {
  margin: var(--space-4) 0 var(--space-3);
  color: #fefce8;
  font-family: var(--font-serif, Georgia, 'Times New Roman', serif);
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.01em;
  white-space: normal;
  max-width: 100%;
}

.hero-subtitle {
  color: #cbd5e1;
  max-width: 100%;
  font-weight: 500;
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.6;
}

.hero-actions {
  margin-top: var(--space-5);
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
}

.hero-actions .admin-head-btn {
  background: #111827;
  border: 1px solid #1f2937;
  color: #e5e7eb;
  box-shadow: 0 3px 0 0 #020617;
  font-weight: 700;
  font-size: 0.82rem;
  padding: var(--space-2) var(--space-4);
  border-radius: 12px;
  transition: var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
}

.hero-actions .admin-head-btn:hover {
  background: #1e293b;
  border-color: #d4af37;
  color: #fef3c7;
  transform: translateY(-1px);
  box-shadow: 0 4px 0 0 #0b1220, 0 8px 16px #020617;
}

.hero-actions .admin-head-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 0 0 #020617;
}

.hero-actions .admin-head-btn.btn-primary {
  background: linear-gradient(135deg, #111827, #1e293b);
  border-color: #d4af37;
  color: #fef3c7;
}

.hero-actions .admin-head-btn.btn-primary:hover {
  background: linear-gradient(135deg, #1e293b, #334155);
  border-color: #fef3c7;
  color: #fffbeb;
}

.hero-kpis {
  padding: var(--space-4) var(--space-4);
  margin: var(--space-4) var(--space-4) var(--space-4) var(--space-4);
  background: #020617;
  border: 1px solid #1e293b;
  border-radius: 16px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  align-content: center;
  gap: var(--space-2);
}

.kpi {
  min-height: 0;
  padding: var(--space-3) var(--space-3);
  border-radius: 13px;
  background: #111827;
  border: 1px solid #1f2937;
  box-shadow: 0 2px 0 0 #020617;
  transition: var(--transition-fast);
}

.kpi:hover {
  border-color: #d4af37;
  background: #1e293b;
  transform: translateY(-1px);
  box-shadow: 0 3px 0 0 #0b1220, 0 7px 16px #020617;
}

.kpi-label {
  font-weight: 900;
  letter-spacing: 0.055em;
  text-transform: uppercase;
  font-size: 0.58rem;
  color: #94a3b8;
}

.kpi-value {
  margin-top: var(--space-1);
  font-size: 0.98rem;
  font-weight: 900;
  color: #fefce8;
  line-height: 1.08;
  font-family: var(--font-serif, Georgia, serif);
}

.kpi-hint {
  margin-top: var(--space-1);
  color: #64748b;
  font-weight: 600;
  font-size: 0.65rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: var(--space-4);
}

.micro-grid {
  padding: 25px;
  border-radius: 20px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  box-shadow: 0 5px 0 0 var(--gray-100), 0 12px 24px var(--gray-100);
  margin: 20px 0px;
}

.section-head {
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--gray-100);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-3);
}

.section-head h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 900;
  color: var(--gray-900);
  font-family: var(--font-serif, Georgia, serif);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.section-head h2 i {
  width: 36px;
  height: 36px;
  border-radius: 11px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #111827;
  color: #fef3c7;
  font-size: 0.92rem;
  border: 1px solid #1f2937;
  box-shadow: 0 2px 0 0 #020617;
}

.section-head p {
  margin: 0;
  color: var(--gray-500);
  font-size: 0.82rem;
  font-weight: 600;
}

.micro-grid-body {
  display: grid;
  gap: var(--space-3);
}

.room-status-grid .micro-grid-body {
  grid-template-columns: repeat(5, minmax(0, 1fr));
}

.payment-methods-grid .micro-grid-body {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.mini-stat {
  position: relative;
  padding: var(--space-4) var(--space-4);
  border-radius: 16px;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
  box-shadow: 0 3px 0 0 var(--gray-100);
  transition: var(--transition-fast);
  overflow: hidden;
}

.mini-stat:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 0 var(--gray-200), 0 10px 20px var(--gray-100);
}

.mini-stat-label {
  display: block;
  font-size: 0.64rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-500);
}

.mini-stat-value {
  display: block;
  margin-top: var(--space-2);
  font-size: 1.55rem;
  font-weight: 950;
  color: var(--gray-900);
  line-height: 1;
  font-family: var(--font-serif, Georgia, serif);
}

.mini-stat-icon {
  position: absolute;
  right: var(--space-3);
  top: var(--space-3);
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  border: 1px solid var(--gray-200);
  background: var(--white);
  color: var(--gray-700);
}

.mini-stat.success {
  background: var(--gray-200);
  border-color: #bbf7d0;
  box-shadow: 0 3px 0 0 #dcfce7;
}
.mini-stat.success .mini-stat-value { color: #14532d; }
.mini-stat.success .mini-stat-icon {
  background: #166534;
  border-color: #14532d;
  color: #f0fdf4;
  box-shadow: 0 2px 0 0 #052e16;
}

.mini-stat.info {
  background: var(--gray-200);
  border-color: #bae6fd;
  box-shadow: 0 3px 0 0 #e0f2fe;
}
.mini-stat.info .mini-stat-value { color: #075985; }
.mini-stat.info .mini-stat-icon {
  background: #0369a1;
  border-color: #075985;
  color: #f0f9ff;
  box-shadow: 0 2px 0 0 #082f49;
}

.mini-stat.primary {
  background: var(--gray-200);
  border-color: #c7d2fe;
  box-shadow: 0 3px 0 0 #e0e7ff;
}
.mini-stat.primary .mini-stat-value { color: #3730a3; }
.mini-stat.primary .mini-stat-icon {
  background: #111827;
  border-color: #1f2937;
  color: #fef3c7;
  box-shadow: 0 2px 0 0 #020617;
}

.mini-stat.warning {
  background: var(--gray-200);
  border-color: #fde68a;
  box-shadow: 0 3px 0 0 #fef3c7;
}
.mini-stat.warning .mini-stat-value { color: #92400e; }
.mini-stat.warning .mini-stat-icon {
  background: #d97706;
  border-color: #92400e;
  color: #fffbeb;
  box-shadow: 0 2px 0 0 #451a03;
}

.mini-stat.danger {
  background: var(--gray-200);
  border-color: #fecaca;
  box-shadow: 0 3px 0 0 #fee2e2;
}
.mini-stat.danger .mini-stat-value { color: #991b1b; }
.mini-stat.danger .mini-stat-icon {
  background: #dc2626;
  border-color: #991b1b;
  color: #fef2f2;
  box-shadow: 0 2px 0 0 #450a0a;
}

.mini-stat.method {
  background: var(--white);
  border-color: var(--gray-200);
}
.mini-stat.method .mini-stat-icon.cash {
  background: #166534;
  border-color: #14532d;
  color: #f0fdf4;
  box-shadow: 0 2px 0 0 #052e16;
}
.mini-stat.method .mini-stat-icon.bank {
  background: #0369a1;
  border-color: #075985;
  color: #f0f9ff;
  box-shadow: 0 2px 0 0 #082f49;
}
.mini-stat.method .mini-stat-icon.mobile {
  background: #7c3aed;
  border-color: #5b21b6;
  color: #f5f3ff;
  box-shadow: 0 2px 0 0 #2e1065;
}
.mini-stat.method .mini-stat-icon.card {
  background: #111827;
  border-color: #1f2937;
  color: #fef3c7;
  box-shadow: 0 2px 0 0 #020617;
}
.stats-grid{
  margin:20px 0px;
}
.mini-stat.method .mini-stat-icon.check {
  background: #92400e;
  border-color: #78350f;
  color: #fffbeb;
  box-shadow: 0 2px 0 0 #451a03;
}
.mini-stat.method.total {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  border-color: #f59e0b;
  box-shadow: 0 3px 0 0 #fde68a;
}
.mini-stat.method.total .mini-stat-value { color: #78350f; }
.mini-stat.method.total .mini-stat-label { color: #92400e; }
.mini-stat.method.total .mini-stat-icon.total-icon {
  background: #111827;
  border-color: #1f2937;
  color: #fef3c7;
  box-shadow: 0 2px 0 0 #020617;
}

.hotel-overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-6);
  margin-bottom: 20px;
}

.focus-card {
  padding: 25px;
  border-radius: 20px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  box-shadow: 0 6px 0 0 var(--gray-100), 0 14px 24px var(--gray-100);
  transition: var(--transition-fast);
}

.focus-card:hover {
  box-shadow: 0 7px 0 0 var(--gray-200), 0 17px 28px var(--gray-100);
  transform: translateY(-1px);
}

.focus-card.accent {
  background: var(--white);
  border-color: var(--gray-300);
}

.focus-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--gray-100);
}

.focus-head h2 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 900;
  color: var(--gray-900);
  font-family: var(--font-serif, Georgia, serif);
}

.focus-head p {
  margin: var(--space-2) 0 0;
  color: var(--gray-500);
  font-size: 0.82rem;
  font-weight: 500;
}

.focus-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 86px;
  padding: var(--space-2) var(--space-4);
  border-radius: 12px;
  background: var(--white);
  border: 1px solid var(--gray-200);
  color: var(--gray-900);
  font-weight: 900;
  font-size: 0.9rem;
  box-shadow: 0 2px 0 0 var(--gray-100);
}

.focus-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.focus-metrics.three {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.focus-metric {
  padding: var(--space-3) var(--space-4);
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
}

.focus-metric span {
  display: block;
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-500);
}

.focus-metric strong {
  display: block;
  margin-top: var(--space-2);
  color: var(--gray-900);
  font-size: 1rem;
  font-weight: 950;
  font-family: var(--font-serif, Georgia, serif);
}

.focus-list {
  display: grid;
  gap: var(--space-3);
}

.focus-list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: 14px;
  background: var(--white);
  border: 1px solid var(--gray-200);
  color: var(--gray-600);
  font-weight: 700;
  box-shadow: 0 2px 0 0 var(--gray-50);
}

.focus-list-row strong {
  color: var(--gray-900);
  font-weight: 900;
}

.occupancy-progress {
  display: grid;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.occupancy-track {
  width: 100%;
  height: 12px;
  border-radius: 999px;
  background: var(--gray-100);
  overflow: hidden;
  border: 1px solid var(--gray-200);
}

.occupancy-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #16a34a 0%, #0284c7 55%, #d4af37 100%);
}

.occupancy-caption {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  color: var(--gray-500);
  font-weight: 700;
  font-size: 0.85rem;
}

.occupancy-caption strong {
  color: var(--gray-900);
  font-family: var(--font-serif, Georgia, serif);
}

.status-chip-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
}

.status-chip {
  padding: var(--space-3) var(--space-4);
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  background: var(--gray-200);
  box-shadow: 0 2px 0 0 var(--gray-100);
}

.status-chip span {
  display: block;
  font-size: 0.66rem;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-500);
}

.status-chip strong {
  display: block;
  margin-top: var(--space-2);
  font-size: 1.05rem;
  color: var(--gray-900);
  font-weight: 950;
  font-family: var(--font-serif, Georgia, serif);
}

.status-chip.info {
  border-color: var(--gray-300);
  background: var(--gray-50);
}

.status-chip.success {
  border-color: #bbf7d0;
   background: var(--gray-200);
  box-shadow: 0 2px 0 0 #dcfce7;
}

.status-chip.warning {
  border-color: #fde68a;
  background: var(--gray-200);
  box-shadow: 0 2px 0 0 #fef3c7;
}

.status-chip.danger {
  border-color: #fecaca;
  background: var(--gray-200);
  box-shadow: 0 2px 0 0 #fee2e2;
}

.stat-card {
  padding: var(--space-4) var(--space-5);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  border-radius: 16px;
  border: 1px solid var(--gray-200);
  box-shadow: 0 4px 0 0 var(--gray-100), 0 8px 18px var(--gray-100);
  transform: none;
  transition: var(--transition-fast);
  background: var(--white);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 0 0 var(--gray-200), 0 14px 24px var(--gray-100);
  border-color: var(--gray-300);
}

.stat-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
  color: var(--gray-900);
  font-size: 0.95rem;
  box-shadow: 0 2px 0 0 var(--gray-100);
}

.stat-icon.primary {
  background: #111827;
  border-color: #1f2937;
  color: #fefce8;
  box-shadow: 0 2px 0 0 #020617;
}

.stat-icon.info {
  background: #f0f9ff;
  border-color: #bae6fd;
  color: #0369a1;
  box-shadow: 0 2px 0 0 #e0f2fe;
}

.stat-icon.warning {
  background: #fffbeb;
  border-color: #fde68a;
  color: #92400e;
  box-shadow: 0 2px 0 0 #fef3c7;
}

.stat-icon.danger {
  background: #fef2f2;
  border-color: #fecaca;
  color: #b91c1c;
  box-shadow: 0 2px 0 0 #fee2e2;
}

.stat-icon.success {
  background: #f0fdf4;
  border-color: #bbf7d0;
  color: #166534;
  box-shadow: 0 2px 0 0 #dcfce7;
}

.stat-icon.tcsth {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #78350f;
  border: 1px solid #f59e0b;
  box-shadow: 0 3px 0 0 #d97706;
}

.stat-content {
  min-width: 0;
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 0.62rem;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--gray-500);
}

.stat-value {
  display: block;
  margin-top: var(--space-1);
  font-size: 1.1rem;
  font-weight: 950;
  color: var(--gray-900);
  line-height: 1.05;
  font-family: var(--font-serif, Georgia, serif);
}

.stat-card.wide {
  grid-column: span 2;
}

.stat-meta {
  margin-top: var(--space-1);
  font-weight: 600;
  font-size: 0.72rem;
  color: var(--gray-500);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-6);
  align-items: start;
}

.panel {
  padding: var(--space-6) var(--space-7);
  border-radius: 20px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  box-shadow: 0 6px 0 0 var(--gray-100), 0 14px 24px var(--gray-100);
  padding: 25px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
  flex-wrap: wrap;
  padding: 0 0 var(--space-4) 0;
  border-bottom: 1px solid var(--gray-100);
}

.panel-head h2 {
  margin: 0;
  padding-top: 2px;
  font-size: 1.05rem;
  font-weight: 900;
  color: var(--gray-900);
  font-family: var(--font-serif, Georgia, serif);
}

.panel-head p {
  margin-top: var(--space-2);
  color: var(--gray-500);
  font-weight: 500;
  font-size: 0.85rem;
}

.panel-head .admin-head-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: 11px;
  font-weight: 800;
  font-size: 0.78rem;
  border: 1px solid #d4af37;
   background: var(--gray-200);
  color: #78350f;
  box-shadow: 0 1px 0 0 #fde68a;
  white-space: nowrap;
  transition: var(--transition-fast);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.panel-head .admin-head-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 0 0 #fbbf24, 0 8px 16px #fde68a;
}

.panel-loading {
  display: grid;
  gap: var(--space-3);
}

.row-skeleton {
  height: 58px;
  border-radius: 14px;
  background: linear-gradient(90deg, var(--gray-100), var(--gray-200), var(--gray-100));
  background-size: 200% 100%;
  animation: skeleton-move 1.2s ease-in-out infinite;
}

@keyframes skeleton-move {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.panel-empty {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-4);
  border: 1px dashed var(--gray-200);
  border-radius: 16px;
  color: var(--gray-500);
  font-weight: 700;
  background: var(--gray-50);
}

.panel-empty i {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--white);
  color: var(--gray-500);
  border: 1px solid var(--gray-200);
}

.panel-empty.compact {
  padding: var(--space-3) var(--space-4);
}

.muted {
  color: var(--gray-500);
  font-weight: 600;
  font-size: 0.82rem;
  margin-top: var(--space-1);
}

.rows {
  display: grid;
  gap: var(--space-3);
}

.rows.compact .row {
  padding: var(--space-3) var(--space-4);
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  box-shadow: 0 2px 0 0 var(--gray-50);
  transition: var(--transition-fast);
}

.row:hover {
  border-color: #d4af37;
  background: var(--gray-50);
}

.row.row-clickable {
  cursor: pointer;
  position: relative;
  user-select: none;
}

.row.row-clickable:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 0 0 var(--gray-200), 0 10px 22px var(--gray-100);
  border-color: #d4af37;
}

.row.row-clickable:active {
  transform: translateY(0);
  box-shadow: 0 2px 0 0 var(--gray-200), 0 4px 10px var(--gray-100);
}

.row-main {
  min-width: 0;
}

.row-title {
  font-weight: 900;
  color: var(--gray-900);
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-sub {
  margin-top: var(--space-1);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
  color: var(--gray-500);
  font-weight: 600;
  font-size: 0.82rem;
}

.row-message {
  margin-top: var(--space-1);
  color: var(--gray-500);
  font-weight: 500;
  font-size: 0.85rem;
  line-height: 1.45;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: 999px;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
  color: var(--gray-900);
  font-weight: 800;
  font-size: 0.7rem;
}

.dot {
  opacity: 0.55;
  color: var(--gray-400);
}

.text-cta {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-weight: 900;
  color: #b45309;
  font-size: 0.76rem;
}

:global(html[data-admin-theme="dark"]) .text-cta {
  color: #fbbf24;
}

.text-cta i {
  font-size: 0.68rem;
}

.row-side {
  text-align: right;
  display: grid;
  justify-items: end;
  gap: var(--space-1);
  flex-shrink: 0;
}

.row-value {
  font-weight: 900;
  color: var(--gray-900);
}

.alerts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}

.room-status-grid {
  margin-bottom: 0;
}

.alert-card {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  background: var(--white);
  box-shadow: 0 3px 0 0 var(--gray-100);
}

.alert-card.danger {
  border-color: #f87171;
  background: #fef2f2;
  box-shadow: 0 3px 0 0 #fecaca;
}

.alert-card.warning {
  border-color: #fbbf24;
  background: #fffbeb;
  box-shadow: 0 3px 0 0 #fde68a;
}

.alert-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--gray-50);
  color: var(--gray-600);
  border: 1px solid var(--gray-200);
}

.alert-title {
  font-weight: 900;
  color: var(--gray-900);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.alert-value {
  font-weight: 900;
  font-size: 1.15rem;
  color: var(--gray-900);
  margin-top: var(--space-1);
  font-family: var(--font-serif, Georgia, serif);
}

.mini-list {
  display: grid;
  gap: var(--space-3);
}

.mini-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-radius: 14px;
  border: 1px solid var(--gray-200);
  transition: var(--transition-fast);
  background: var(--white);
  box-shadow: 0 2px 0 0 var(--gray-50);
}

.mini-row.mini-row-clickable {
  cursor: pointer;
  user-select: none;
}

.mini-row.mini-row-clickable:hover {
  transform: translateY(-1px);
  background: var(--gray-50);
  border-color: #d4af37;
  box-shadow: 0 4px 0 0 var(--gray-100), 0 8px 18px var(--gray-100);
}

.mini-row.mini-row-clickable:active {
  transform: translateY(0);
  box-shadow: 0 2px 0 0 var(--gray-100), 0 4px 10px var(--gray-100);
}

.mini-title {
  font-weight: 900;
  color: var(--gray-900);
}

.mini-sub {
  color: var(--gray-500);
  font-weight: 600;
  font-size: 0.78rem;
  margin-top: var(--space-1);
}

.mini-side {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--gray-900);
}

.mini-pill {
  display: inline-flex;
  align-items: center;
  padding: var(--space-1) var(--space-3);
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.7rem;
  border: 1px solid var(--gray-200);
  background: var(--gray-50);
}

.mini-pill.danger {
  border-color: #f87171;
  background: #fef2f2;
  color: #b91c1c;
}

.mini-pill.warning {
  border-color: #fbbf24;
  background: #fffbeb;
  color: #92400e;
}

.span-2 {
  grid-column: span 2;
}

:global(html[data-admin-theme="dark"]) .hero {
  border-color: var(--gray-700);
  box-shadow: 0 5px 0 0 var(--gray-600), 0 16px 32px var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .hero-copy {
  background: linear-gradient(135deg, var(--gray-800), var(--gray-900));
  border-color: var(--gray-700);
}

:global(html[data-admin-theme="dark"]) .hero-badge {
  background: #78350f;
  border-color: #d97706;
  color: #fef3c7;
  box-shadow: 0 3px 0 0 #451a03;
}

:global(html[data-admin-theme="dark"]) .hero-kpis {
  background: var(--gray-900);
  border-color: var(--gray-700);
}

:global(html[data-admin-theme="dark"]) .kpi {
  background: var(--gray-800);
  border-color: var(--gray-700);
  box-shadow: 0 2px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .kpi:hover {
  border-color: #d4af37;
  background: var(--gray-700);
  box-shadow: 0 3px 0 0 var(--gray-600), 0 7px 16px var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .micro-grid,
:global(html[data-admin-theme="dark"]) .stat-card,
:global(html[data-admin-theme="dark"]) .focus-card,
:global(html[data-admin-theme="dark"]) .panel,
:global(html[data-admin-theme="dark"]) .row,
:global(html[data-admin-theme="dark"]) .alert-card,
:global(html[data-admin-theme="dark"]) .mini-row {
  background: var(--gray-800);
  border-color: var(--gray-700);
  box-shadow: 0 4px 0 0 var(--gray-600), 0 10px 24px var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .micro-grid:hover,
:global(html[data-admin-theme="dark"]) .stat-card:hover,
:global(html[data-admin-theme="dark"]) .focus-card:hover,
:global(html[data-admin-theme="dark"]) .panel:hover {
  box-shadow: 0 6px 0 0 var(--gray-600), 0 16px 30px var(--gray-600);
  border-color: var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .focus-card.accent {
  background: var(--gray-800);
  border-color: var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .section-head {
  border-bottom-color: var(--gray-700);
}
:global(html[data-admin-theme="dark"]) .section-head h2 { color: var(--gray-100); }
:global(html[data-admin-theme="dark"]) .section-head h2 i {
  background: var(--gray-900);
  border-color: var(--gray-700);
  color: #fbbf24;
  box-shadow: 0 2px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .section-head p { color: var(--gray-400); }

:global(html[data-admin-theme="dark"]) .mini-stat {
  background: var(--gray-900);
  border-color: var(--gray-700);
  box-shadow: 0 3px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .mini-stat-label { color: var(--gray-400); }
:global(html[data-admin-theme="dark"]) .mini-stat-value { color: var(--gray-100); }
:global(html[data-admin-theme="dark"]) .mini-stat-icon {
  background: var(--gray-800);
  border-color: var(--gray-700);
  color: var(--gray-300);
}
:global(html[data-admin-theme="dark"]) .mini-stat.success {
  background: #052e16;
  border-color: #14532d;
  box-shadow: 0 3px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .mini-stat.success .mini-stat-value { color: #86efac; }
:global(html[data-admin-theme="dark"]) .mini-stat.success .mini-stat-label { color: #4ade80; }
:global(html[data-admin-theme="dark"]) .mini-stat.info {
  background: #082f49;
  border-color: #075985;
  box-shadow: 0 3px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .mini-stat.info .mini-stat-value { color: #7dd3fc; }
:global(html[data-admin-theme="dark"]) .mini-stat.info .mini-stat-label { color: #38bdf8; }
:global(html[data-admin-theme="dark"]) .mini-stat.primary {
  background: #1e1b4b;
  border-color: #3730a3;
  box-shadow: 0 3px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .mini-stat.primary .mini-stat-value { color: #c7d2fe; }
:global(html[data-admin-theme="dark"]) .mini-stat.warning {
  background: #451a03;
  border-color: #92400e;
  box-shadow: 0 3px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .mini-stat.warning .mini-stat-value { color: #fbbf24; }
:global(html[data-admin-theme="dark"]) .mini-stat.warning .mini-stat-label { color: #f59e0b; }
:global(html[data-admin-theme="dark"]) .mini-stat.danger {
  background: #450a0a;
  border-color: #991b1b;
  box-shadow: 0 3px 0 0 var(--gray-600);
}
:global(html[data-admin-theme="dark"]) .mini-stat.danger .mini-stat-value { color: #fca5a5; }
:global(html[data-admin-theme="dark"]) .mini-stat.danger .mini-stat-label { color: #f87171; }
:global(html[data-admin-theme="dark"]) .mini-stat.method {
  background: var(--gray-900);
  border-color: var(--gray-700);
}
:global(html[data-admin-theme="dark"]) .mini-stat.method.total {
  background: linear-gradient(135deg, #78350f, #92400e);
  border-color: #d97706;
  box-shadow: 0 3px 0 0 #451a03;
}
:global(html[data-admin-theme="dark"]) .mini-stat.method.total .mini-stat-value { color: #fef3c7; }
:global(html[data-admin-theme="dark"]) .mini-stat.method.total .mini-stat-label { color: #fde68a; }

:global(html[data-admin-theme="dark"]) .stat-label,
:global(html[data-admin-theme="dark"]) .stat-meta,
:global(html[data-admin-theme="dark"]) .panel-head p,
:global(html[data-admin-theme="dark"]) .row-sub,
:global(html[data-admin-theme="dark"]) .row-message,
:global(html[data-admin-theme="dark"]) .muted,
:global(html[data-admin-theme="dark"]) .focus-head p,
:global(html[data-admin-theme="dark"]) .focus-metric span,
:global(html[data-admin-theme="dark"]) .status-chip span,
:global(html[data-admin-theme="dark"]) .focus-list-row,
:global(html[data-admin-theme="dark"]) .occupancy-caption,
:global(html[data-admin-theme="dark"]) .mini-sub {
  color: var(--gray-400);
}

:global(html[data-admin-theme="dark"]) .stat-value,
:global(html[data-admin-theme="dark"]) .panel-head h2,
:global(html[data-admin-theme="dark"]) .row-title,
:global(html[data-admin-theme="dark"]) .row-value,
:global(html[data-admin-theme="dark"]) .alert-title,
:global(html[data-admin-theme="dark"]) .alert-value,
:global(html[data-admin-theme="dark"]) .mini-title,
:global(html[data-admin-theme="dark"]) .mini-side,
:global(html[data-admin-theme="dark"]) .focus-head h2,
:global(html[data-admin-theme="dark"]) .focus-metric strong,
:global(html[data-admin-theme="dark"]) .focus-list-row strong,
:global(html[data-admin-theme="dark"]) .occupancy-caption strong,
:global(html[data-admin-theme="dark"]) .status-chip strong {
  color: var(--gray-100);
}

:global(html[data-admin-theme="dark"]) .stat-icon,
:global(html[data-admin-theme="dark"]) .alert-icon,
:global(html[data-admin-theme="dark"]) .panel-empty i,
:global(html[data-admin-theme="dark"]) .mini-pill,
:global(html[data-admin-theme="dark"]) .focus-badge,
:global(html[data-admin-theme="dark"]) .focus-metric,
:global(html[data-admin-theme="dark"]) .status-chip,
:global(html[data-admin-theme="dark"]) .focus-list-row,
:global(html[data-admin-theme="dark"]) .pill,
:global(html[data-admin-theme="dark"]) .focus-head,
:global(html[data-admin-theme="dark"]) .panel-head,
:global(html[data-admin-theme="dark"]) .mini-row {
  background: var(--gray-900);
  border-color: var(--gray-700);
}

:global(html[data-admin-theme="dark"]) .panel-head {
  border-bottom-color: var(--gray-700);
}
:global(html[data-admin-theme="dark"]) .panel-head .admin-head-btn {
  background: linear-gradient(135deg, #78350f, #92400e);
  border-color: #d97706;
  color: #fef3c7;
  box-shadow: 0 3px 0 0 #451a03;
}

:global(html[data-admin-theme="dark"]) .stat-icon.primary {
  background: var(--gray-900);
  border-color: var(--gray-700);
  box-shadow: 0 2px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .stat-icon.info {
  background: #082f49;
  border-color: #0369a1;
  color: #7dd3fc;
  box-shadow: 0 2px 0 0 #082f49;
}

:global(html[data-admin-theme="dark"]) .stat-icon.warning {
  background: #451a03;
  border-color: #92400e;
  color: #fbbf24;
  box-shadow: 0 2px 0 0 #451a03;
}

:global(html[data-admin-theme="dark"]) .stat-icon.danger {
  background: #450a0a;
  border-color: #991b1b;
  color: #fca5a5;
  box-shadow: 0 2px 0 0 #450a0a;
}

:global(html[data-admin-theme="dark"]) .stat-icon.success {
  background: #052e16;
  border-color: #14532d;
  color: #86efac;
  box-shadow: 0 2px 0 0 #052e16;
}

:global(html[data-admin-theme="dark"]) .stat-icon.tcsth {
  background: linear-gradient(135deg, #78350f, #92400e);
  border-color: #d97706;
  color: #fef3c7;
  box-shadow: 0 3px 0 0 #451a03;
}

:global(html[data-admin-theme="dark"]) .status-chip.success {
  background: #052e16;
  border-color: #14532d;
  box-shadow: 0 2px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .status-chip.warning {
  background: #451a03;
  border-color: #92400e;
  box-shadow: 0 2px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .status-chip.danger {
  background: #450a0a;
  border-color: #991b1b;
  box-shadow: 0 2px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .alert-card.danger {
  border-color: #991b1b;
  background: #450a0a;
  box-shadow: 0 3px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .alert-card.warning {
  border-color: #92400e;
  background: #451a03;
  box-shadow: 0 3px 0 0 var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .mini-pill.danger {
  border-color: #991b1b;
  background: #450a0a;
  color: #fca5a5;
}

:global(html[data-admin-theme="dark"]) .mini-pill.warning {
  border-color: #92400e;
  background: #451a03;
  color: #fbbf24;
}

:global(html[data-admin-theme="dark"]) .row:hover,
:global(html[data-admin-theme="dark"]) .row.row-clickable:hover,
:global(html[data-admin-theme="dark"]) .mini-row.mini-row-clickable:hover {
  background: var(--gray-700);
  border-color: #d4af37;
  box-shadow: 0 4px 0 0 var(--gray-600), 0 10px 22px var(--gray-600);
}

:global(html[data-admin-theme="dark"]) .occupancy-track {
  background: var(--gray-900);
  border-color: var(--gray-700);
}

:global(html[data-admin-theme="dark"]) .panel-empty {
  border-color: var(--gray-700);
  background: var(--gray-900);
}

@media (max-width: 1500px) {
  .stats-grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}

@media (max-width: 1300px) {
  .stats-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
  .hero-kpis {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .payment-methods-grid .micro-grid-body {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 1100px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-kpis {
    border-left: none;
    border-top: 1px solid #1e293b;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .stats-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .hotel-overview-grid {
    grid-template-columns: 1fr;
  }

  .stat-card.wide {
    grid-column: span 2;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: span 1;
  }

  .room-status-grid .micro-grid-body {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .payment-methods-grid .micro-grid-body {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 850px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .hero-kpis {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .room-status-grid .micro-grid-body {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .payment-methods-grid .micro-grid-body {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .hero-kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 440px) {
  .hero-copy,
  .hero-kpis,
  .micro-grid {
    padding: var(--space-5);
  }

  .hero-title {
    font-size: 1.5rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .room-status-grid .micro-grid-body,
  .payment-methods-grid .micro-grid-body {
    grid-template-columns: 1fr;
  }

  .focus-metrics,
  .focus-metrics.three,
  .status-chip-grid {
    grid-template-columns: 1fr;
  }

  .focus-head,
  .occupancy-caption,
  .focus-list-row,
  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
