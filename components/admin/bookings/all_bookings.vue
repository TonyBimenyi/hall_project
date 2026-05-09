<!-- pages/admin/bookings.vue  or  components/BookingsTable.vue -->
<template>
  <div class="bookings-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1>{{ $t('admin.bookings.title') }}</h1>
        <p>{{ $t('admin.bookings.manage_all_reservations') }}</p>
      </div>
      <button class="btn-new">
        <span>+</span> {{ $t('admin.bookings.new_booking') }}
      </button>
    </div>

    <!-- Controls -->
    <div class="controls">
      <div class="search-wrapper">
        <input
          type="text"
          :placeholder="$t('admin.bookings.search_bookings_placeholder')"
          class="search-input"
        />
      </div>
      <div class="filter-wrapper">
        <select class="filter-select">
          <option>{{ $t('admin.bookings.all_status') }}</option>
          <option>{{ $t('admin.status.confirmed') }}</option>
          <option>{{ $t('admin.status.pending') }}</option>
          <option>{{ $t('admin.status.cancelled') }}</option>
        </select>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-container">
      <h2 class="table-title">{{ $t('admin.bookings.all_bookings', { count: 5 }) }}</h2>

      <div class="table-wrapper">
        <table class="bookings-table">
          <thead>
            <tr>
              <th>{{ $t('admin.bookings.customer') }}</th>
              <th>{{ $t('admin.bookings.hall') }}</th>
              <th>{{ $t('admin.bookings.event_type') }}</th>
              <th>{{ $t('admin.bookings.date') }}</th>
              <th>{{ $t('admin.bookings.time') }}</th>
              <th>{{ $t('admin.bookings.amount') }}</th>
              <th>{{ $t('admin.bookings.status') }}</th>
              <th>{{ $t('admin.bookings.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="booking in bookings" :key="booking.id">
              <td class="customer-cell">
                <div class="customer-name">{{ booking.customer }}</div>
                <div class="customer-email">{{ booking.email }}</div>
              </td>
              <td>{{ booking.hall }}</td>
              <td>{{ booking.eventType }}</td>
              <td class="date-cell">
                {{ booking.dateDay }}<br />
                <span class="year">{{ booking.year }}</span>
              </td>
              <td class="time-cell">{{ booking.time }}</td>
              <td class="amount-cell">{{ booking.amount }}</td>
              <td>
                <span :class="['status-badge', booking.status]">
                  {{ $t(`admin.status.${booking.status.toLowerCase()}`) }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="action-btn view" :title="$t('admin.bookings.view')">👁️</button>
                <button class="action-btn edit" :title="$t('admin.bookings.edit')">✏️</button>
                <button class="action-btn delete" :title="$t('admin.bookings.delete')">🗑️</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      bookings: [
        {
          id: 1,
          customer: 'Sarah Johnson',
          email: 'sarah@email.com',
          hall: 'Grand Ballroom',
          eventType: 'Wedding Reception',
          dateDay: 'Feb 15, 2026',
          year: '2026',
          time: '18:00 – 23:00',
          amount: '$2,500',
          status: 'confirmed'
        },
        {
          id: 2,
          customer: 'Michael Chen',
          email: 'mchen@corp.com',
          hall: 'Executive Conference Room',
          eventType: 'Corporate Meeting',
          dateDay: 'Feb 05, 2026',
          year: '2026',
          time: '09:00 – 17:00',
          amount: '$1,000',
          status: 'confirmed'
        },
        {
          id: 3,
          customer: 'Emily Davis',
          email: 'emily@email.com',
          hall: 'Garden Pavilion',
          eventType: 'Birthday Party',
          dateDay: 'Feb 20, 2026',
          year: '2026',
          time: '14:00 – 20:00',
          amount: '$1,800',
          status: 'pending'
        },
        {
          id: 4,
          customer: 'James Wilson',
          email: 'jwilson@email.com',
          hall: 'Intimate Lounge',
          eventType: 'Private Dinner',
          dateDay: 'Feb 10, 2026',
          year: '2026',
          time: '19:00 – 22:00',
          amount: '$300',
          status: 'confirmed'
        },
        {
          id: 5,
          customer: 'Lisa Anderson',
          email: 'lisa@startup.io',
          hall: 'Executive Conference Room',
          eventType: 'Product Launch',
          dateDay: 'Feb 08, 2026',
          year: '2026',
          time: '10:00 – 16:00',
          amount: '$900',
          status: 'cancelled'
        }
      ]
    }
  }
}
</script>

<style scoped>
.bookings-page {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.page-header p {
  color: #6b7280;
  margin: 4px 0 0 0;
}

.btn-new {
  background: #7c3aed;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1rem;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.2);
}

.btn-new:hover {
  background: #6d28d9;
}

/* Controls */
.controls {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-wrapper {
  flex: 1;
  min-width: 280px;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  background: white url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E") no-repeat 12px center;
  background-size: 18px;
}

.filter-wrapper {
  min-width: 180px;
}

.filter-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background: white;
  font-size: 1rem;
  cursor: pointer;
}

/* Table */
.table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  overflow: hidden;
}

.table-title {
  padding: 20px 24px;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  border-bottom: 1px solid #e5e7eb;
}

.table-wrapper {
  overflow-x: auto;
}

.bookings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.bookings-table th,
.bookings-table td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.bookings-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #4b5563;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.customer-cell {
  line-height: 1.4;
}

.customer-name {
  font-weight: 600;
  color: #1f2937;
}

.customer-email {
  color: #6b7280;
  font-size: 0.9rem;
  margin-top: 4px;
}

.date-cell {
  white-space: nowrap;
}

.year {
  color: #6b7280;
  font-size: 0.9rem;
}

.time-cell {
  white-space: nowrap;
}

.amount-cell {
  font-weight: 600;
  color: #1e40af;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: capitalize;
  display: inline-block;
}

.status-badge.confirmed {
  background: #dcfce7;
  color: #166534;
}

.status-badge.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.cancelled {
  background: #fee2e2;
  color: #991b1b;
}

.actions-cell {
  white-space: nowrap;
}

.action-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 6px;
  margin: 0 4px;
  color: #6b7280;
  border-radius: 6px;
}

.action-btn:hover {
  background: #f1f5f9;
}

.action-btn.view   { color: #3b82f6; }
.action-btn.edit   { color: #f59e0b; }
.action-btn.delete { color: #ef4444; }

/* Responsive */
@media (max-width: 1024px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn-new {
    width: fit-content;
    align-self: flex-end;
  }
}

@media (max-width: 768px) {
  .controls {
    flex-direction: column;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
}
</style>