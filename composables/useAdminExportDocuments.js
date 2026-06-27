import { useDocumentBranding } from '~/composables/useDocumentBranding'
import { getStoredUser } from '~/composables/useRoleAccess'

export const useAdminExportDocuments = () => {
  const { documentBranding, documentLogoUrl, escapeHtml } = useDocumentBranding()

  const pad = (value) => String(value).padStart(2, '0')

  const buildExportTimestamp = (date = new Date()) => {
    const d = date instanceof Date ? date : new Date(date)
    return `${pad(d.getDate())}${pad(d.getMonth() + 1)}${String(d.getFullYear()).slice(-2)}${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`
  }

  const buildExportFileName = (type, extension) => {
    const normalizedType = String(type || 'document').toLowerCase().replace(/[^a-z0-9]+/g, '')
    return `${normalizedType}${buildExportTimestamp()}.${extension}`
  }

  const getPrintedByLabel = () => {
    const user = getStoredUser()
    return user?.full_name || user?.name || user?.username || user?.email || 'Utilisateur inconnu'
  }

  const removeActionColumns = (root) => {
    const tables = root.matches?.('table') ? [root] : Array.from(root.querySelectorAll?.('table') || [])
    for (const table of tables) {
      const headerCells = Array.from(table.querySelectorAll('thead tr th'))
      const actionIndexes = headerCells
        .map((th, index) => ({ index, text: String(th.textContent || '').trim().toLowerCase() }))
        .filter(({ text }) => /^actions?$/.test(text))
        .map(({ index }) => index)

      if (!actionIndexes.length) continue

      for (const row of Array.from(table.querySelectorAll('tr'))) {
        const cells = Array.from(row.children)
        actionIndexes.slice().reverse().forEach((index) => {
          if (cells[index]) cells[index].remove()
        })
      }
    }
  }

  const sanitizeExportNode = (node, { removeActionsColumn = true } = {}) => {
    if (!node) return node

    if (removeActionsColumn) removeActionColumns(node)

    node.querySelectorAll?.('th button, th .table-sort-btn').forEach((el) => {
      const text = normalizeText(el.textContent || '')
      const replacement = document.createElement('span')
      replacement.textContent = text
      el.replaceWith(replacement)
    })

    node.querySelectorAll?.('button, .btn, .btn-icon, .actions-dropdown, .actions-menu, .filters-toggle').forEach(el => el.remove())
    node.querySelectorAll?.('.skeleton-line, .skeleton-chart, .skeleton-overlay').forEach(el => el.remove())
    node.querySelectorAll?.('[style*="position: sticky"]').forEach((el) => {
      el.style.position = 'static'
      el.style.top = 'auto'
    })

    return node
  }

  const getSanitizedExportHtml = (sourceEl, { htmlMode = 'outer', removeActionsColumn = true } = {}) => {
    if (!sourceEl || !process.client) return ''
    const clone = sourceEl.cloneNode(true)
    sanitizeExportNode(clone, { removeActionsColumn })
    return htmlMode === 'inner' ? clone.innerHTML : clone.outerHTML
  }

  const buildPdfDocumentHtml = ({
    title,
    documentTitle = '',
    subtitle = '',
    typeLabel = 'Export PDF',
    headerVariant = 'default',
    headerEyebrow = '',
    headerReference = '',
    contentHtml = '',
    tableTitle = '',
    tableTitles = [],
    periodLabel = 'Toutes les dates',
    printedBy = getPrintedByLabel(),
    generatedAt = new Date().toLocaleString('fr-FR'),
    showMeta = true,
  }) => {
    const metaItems = [
      { label: 'Période sélectionnée', value: periodLabel || 'Toutes les dates' },
      { label: 'Exporté par', value: printedBy || 'Utilisateur inconnu' },
      { label: "Date d'édition", value: generatedAt },
    ]
    const normalizedTableTitles = (Array.isArray(tableTitles) ? tableTitles : [])
      .map(value => normalizeText(value))
      .filter(Boolean)
    if (!normalizedTableTitles.length && tableTitle) {
      normalizedTableTitles.push(normalizeText(tableTitle))
    }

    return `<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(documentTitle || title)}</title>
  ${normalizedTableTitles.map(value => `<meta name="doc-export-table-title" content="${escapeHtml(value)}">`).join('\n  ')}
  <style>
    :root {
      color-scheme: light;
      --ink: #0f172a;
      --muted: #64748b;
      --line: #dbe3ee;
      --paper: #f8fafc;
      --card: #ffffff;
      --success: #166534;
      --danger: #b91c1c;
      --warning: #92400e;
      --info: #1d4ed8;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 28px;
      font-family: Arial, sans-serif;
      background: #eef2f7;
      color: var(--ink);
    }
    .sheet {
      max-width: 1040px;
      margin: 0 auto;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 28px;
      overflow: hidden;
      box-shadow: 0 24px 50px rgba(15, 23, 42, 0.12);
    }
    .head {
      padding: 28px 30px 24px;
      background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #8b6b12 100%);
      color: #ffffff;
    }
    .head.ticket-head {
      position: relative;
      padding: 0;
      background: #ffffff;
      color: var(--ink);
      border-bottom: 1px solid var(--line);
    }
    .head.ticket-head::before {
      content: '';
      display: block;
      height: 5px;
      background: linear-gradient(90deg, #0f172a 0%, #1d4ed8 52%, #8b6b12 100%);
    }
    .brand {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
    }
    .ticket-head .brand {
      align-items: center;
      padding: 24px 30px;
    }
    .brand-main {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .logo-wrap {
      width: 78px;
      height: 78px;
      border-radius: 22px;
      background: rgba(255,255,255,0.14);
      border: 1px solid rgba(255,255,255,0.22);
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    .logo-wrap img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .ticket-head .logo-wrap {
      width: 70px;
      height: 70px;
      border-radius: 20px;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
    }
    .brand-copy small {
      display: block;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.28em;
      font-size: 11px;
      color: rgba(255,255,255,0.74);
    }
    .brand-copy h1 {
      margin: 0;
      font-size: 30px;
      line-height: 1.08;
    }
    .brand-copy p {
      margin: 8px 0 0;
      color: rgba(255,255,255,0.84);
      max-width: 560px;
      line-height: 1.6;
    }
    .ticket-head .brand-copy small {
      margin-bottom: 6px;
      color: var(--info);
    }
    .ticket-head .brand-copy h1 {
      color: var(--ink);
      font-size: 26px;
    }
    .ticket-head .brand-copy p {
      color: var(--muted);
      margin-top: 6px;
      max-width: 640px;
    }
    .chip {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 10px 14px;
      border-radius: 999px;
      background: rgba(255,255,255,0.14);
      border: 1px solid rgba(255,255,255,0.22);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }
    .ticket-head .chip {
      background: #eff6ff;
      border-color: #bfdbfe;
      color: var(--info);
    }
    .brand-side {
      display: grid;
      justify-items: end;
      gap: 10px;
      min-width: 220px;
    }
    .brand-side-card {
      min-width: 220px;
      padding: 14px 16px;
      border-radius: 18px;
      border: 1px solid var(--line);
      background: #f8fafc;
      text-align: right;
    }
    .brand-side-label {
      display: block;
      margin-bottom: 6px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--muted);
    }
    .brand-side-value {
      display: block;
      font-size: 20px;
      font-weight: 800;
      line-height: 1.2;
      color: var(--ink);
      word-break: break-word;
    }
    .body {
      padding: 28px 30px 24px;
    }
    .meta {
      display: grid;
      grid-template-columns: 1.2fr .8fr;
      gap: 16px;
      margin-bottom: 18px;
    }
    .meta-card,
    .card,
    .stat-card,
    .summary-card,
    .section-card {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--paper);
      padding: 16px 18px;
      box-shadow: none !important;
    }
    .meta-card strong {
      display: block;
      margin-bottom: 4px;
      font-size: 1.05rem;
    }
    .meta-card span {
      color: var(--muted);
      line-height: 1.6;
    }
    .export-content {
      display: grid;
      gap: 16px;
    }
    .export-content h2,
    .export-content h3,
    .export-content .table-title,
    .export-content .section-header h2,
    .export-content .card-header span {
      margin: 0 0 10px;
      color: var(--ink);
    }
    .export-content p,
    .export-content .label,
    .export-content .stat-label,
    .export-content .subtitle,
    .export-content .admin-card-subtitle,
    .export-content .muted-line,
    .export-content .k {
      color: var(--muted);
    }
    .export-content .stats-grid,
    .export-content .summary-cards,
    .export-content .admin-cards {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .export-content .stat-card,
    .export-content .summary-card,
    .export-content .admin-card {
      display: flex;
      gap: 14px;
      align-items: flex-start;
    }
    .export-content .stat-icon,
    .export-content .summary-icon {
      flex-shrink: 0;
    }
    .export-content .value,
    .export-content .stat-value,
    .export-content .admin-card-title,
    .export-content .v {
      color: var(--ink);
      font-weight: 800;
    }
    .export-content .success { color: var(--success) !important; }
    .export-content .danger { color: var(--danger) !important; }
    .export-content .warning { color: var(--warning) !important; }
    .export-content .info,
    .export-content .primary { color: var(--info) !important; }
    table {
      width: 100%;
      border-collapse: collapse;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 12px 10px;
      text-align: left;
      font-size: 13px;
      vertical-align: top;
    }
    th {
      background: #f8fafc;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 11px;
    }
    td:last-child {
      color: var(--ink);
    }
    tr:last-child td {
      border-bottom: none;
    }
    .footer {
      margin-top: 18px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 16px;
    }
    .footer-card {
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--paper);
      padding: 16px 18px;
    }
    .footer-card strong {
      display: block;
      margin-bottom: 8px;
    }
    .footer-card p,
    .footer-card li {
      color: #334155;
      line-height: 1.6;
      margin: 0;
    }
    .footer-card ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }
    @media (max-width: 780px) {
      .brand, .meta, .footer, .export-content .stats-grid, .export-content .summary-cards, .export-content .admin-cards {
        grid-template-columns: 1fr;
        display: grid;
      }
      .brand-main {
        align-items: flex-start;
      }
      .brand-side {
        width: 100%;
        justify-items: stretch;
      }
      .brand-side-card {
        width: 100%;
        min-width: 0;
        text-align: left;
      }
    }
    @media print {
      body {
        background: #ffffff;
        padding: 0;
      }
      .sheet {
        border: none;
        box-shadow: none;
        border-radius: 0;
      }
    }
  </style>
</head>
<body>
  <div class="sheet">
    <div class="head ${headerVariant === 'ticket' ? 'ticket-head' : ''}">
      <div class="brand">
        <div class="brand-main">
          <div class="logo-wrap">
            <img src="${escapeHtml(documentLogoUrl)}" alt="${escapeHtml(documentBranding.name)}" />
          </div>
          <div class="brand-copy">
            <small>${escapeHtml(headerEyebrow || documentBranding.tagline)}</small>
            <h1>${escapeHtml(documentBranding.name)}</h1>
            <p>${escapeHtml(subtitle || title)}</p>
          </div>
        </div>
        <div class="brand-side">
          <div class="chip">${escapeHtml(typeLabel)}</div>
          ${headerReference ? `
          <div class="brand-side-card">
            <span class="brand-side-label">Référence</span>
            <span class="brand-side-value">${escapeHtml(headerReference)}</span>
          </div>` : ''}
        </div>
      </div>
    </div>
    <div class="body">
      <div class="doc-export-title" style="display:none;">${escapeHtml(title)}</div>
      <div class="doc-export-table-titles" style="display:none;">${normalizedTableTitles.map(value => `<span>${escapeHtml(value)}</span>`).join('')}</div>
      ${showMeta ? `
      <div class="meta">
        ${metaItems.map(item => `
        <div class="meta-card">
          <strong>${escapeHtml(item.label)}</strong>
          <span class="${escapeHtml(item.valueClass || '')}">${escapeHtml(item.value)}</span>
        </div>`).join('')}
      </div>` : ''}
      <div class="export-content">${contentHtml}</div>
      <div class="footer">
        <div class="footer-card">
          <strong>Adresse</strong>
          <p>${escapeHtml(documentBranding.address)}</p>
        </div>
        <div class="footer-card">
          <strong>Contacts</strong>
          <ul>${documentBranding.contacts.map(contact => `<li>${escapeHtml(contact)}</li>`).join('')}</ul>
        </div>
      </div>
    </div>
  </div>
</body>
</html>`
  }

  const normalizeText = (value) => String(value || '').replace(/\s+/g, ' ').trim()

  const getText = (node) => normalizeText(node?.textContent || '')

  const toRgb = (hex) => {
    const clean = String(hex || '').replace('#', '')
    const source = clean.length === 3
      ? clean.split('').map(char => char + char).join('')
      : clean.padEnd(6, '0')
    return [
      Number.parseInt(source.slice(0, 2), 16),
      Number.parseInt(source.slice(2, 4), 16),
      Number.parseInt(source.slice(4, 6), 16),
    ]
  }

  const loadImageAsDataUrl = async (url) => {
    if (!process.client || !url) return null
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      return await new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onloadend = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(blob)
      })
    } catch {
      return null
    }
  }

  const extractSummaryCard = (card) => {
    const label = getText(
      card.querySelector('.stat-label, .admin-card-subtitle, .label, .subtitle, .k, span, small'),
    )
    const value = getText(
      card.querySelector('.stat-value, .admin-card-title, .value, .v, strong, h3, h4'),
    )
    const tone = ['success', 'danger', 'warning', 'primary', 'info'].find(className => card.classList.contains(className)) || 'primary'
    if (!label && !value) return null
    return { label: label || 'Valeur', value: value || label, tone }
  }

  const resolveTableTitle = (table, index, fallbackTitle = '', fallbackTitles = []) => {
    const localTitle = getText(
      table.closest('.section-card, .card, .admin-card, .table-card')?.querySelector('.section-title, .table-title, .section-header h2, .section-header h3, h2, h3'),
    )
    if (localTitle) return localTitle

    let previous = table.previousElementSibling
    while (previous) {
      const text = getText(previous)
      if (text) return text
      previous = previous.previousElementSibling
    }

    if (fallbackTitles[index]) {
      return fallbackTitles[index]
    }

    if (fallbackTitle) {
      return index === 0 ? fallbackTitle : `${fallbackTitle} ${index + 1}`
    }

    return `Tableau ${index + 1}`
  }

  const extractTable = (table, index, fallbackTitle = '', fallbackTitles = []) => {
    const headRows = Array.from(table.querySelectorAll('thead tr'))
    const bodyRows = Array.from(table.querySelectorAll('tbody tr'))
    const allRows = bodyRows.length ? bodyRows : Array.from(table.querySelectorAll('tr')).slice(headRows.length)

    let head = headRows.length
      ? Array.from(headRows[headRows.length - 1].children).map(cell => getText(cell))
      : []

    let body = allRows
      .map(row => Array.from(row.children).map(cell => getText(cell)))
      .filter(row => row.some(Boolean))

    if (!head.length && body.length) {
      head = body[0]
      body = body.slice(1)
    }

    return {
      title: resolveTableTitle(table, index, fallbackTitle, fallbackTitles),
      head,
      body: body.map((row) => {
        if (row.length === head.length) return row
        return head.map((_, cellIndex) => row[cellIndex] || '')
      }),
    }
  }

  const parseExportDocument = (html) => {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const exportRoot = doc.querySelector('.export-content') || doc.body
    const parsedTitle = getText(doc.querySelector('.doc-export-title')) || getText(doc.querySelector('meta[name="doc-export-title"]')) || getText(doc.querySelector('title')) || 'Document'
    const parsedTableTitles = [
      ...Array.from(doc.querySelectorAll('.doc-export-table-titles span')).map(node => getText(node)),
      ...Array.from(doc.querySelectorAll('meta[name="doc-export-table-title"]')).map(node => normalizeText(node.getAttribute('content') || '')),
    ].filter(Boolean)
    const metaCards = Array.from(doc.querySelectorAll('.meta .meta-card'))
      .map(card => ({
        label: getText(card.querySelector('strong')) || 'Information',
        value: getText(card.querySelector('span, p, div:last-child')),
      }))
      .filter(item => item.label || item.value)

    const summaries = Array.from(exportRoot.querySelectorAll('.summary-card, .stat-card, .admin-card'))
      .map(extractSummaryCard)
      .filter(Boolean)

    const tables = Array.from(exportRoot.querySelectorAll('table'))
      .map((table, index) => extractTable(table, index, parsedTitle, parsedTableTitles))
      .filter(table => table.head.length || table.body.length)

    const notes = Array.from(exportRoot.querySelectorAll('.section-card'))
      .filter(card => !card.querySelector('table'))
      .map((card) => {
        const title = getText(card.querySelector('.section-title, .section-header h2, .section-header h3, h2, h3, strong'))
        const lines = Array.from(card.querySelectorAll('p, li'))
          .map(line => getText(line))
          .filter(Boolean)
        if (!title && !lines.length) return null
        return { title: title || 'Informations', lines }
      })
      .filter(Boolean)

    return {
      documentTitle: getText(doc.querySelector('title')) || 'Document',
      title: parsedTitle,
      subtitle: getText(doc.querySelector('.brand-copy p')),
      typeLabel: getText(doc.querySelector('.chip')) || 'Export PDF',
      meta: metaCards,
      summaries,
      tables,
      notes,
      address: getText(doc.querySelector('.footer .footer-card p')) || documentBranding.address,
      contacts: Array.from(doc.querySelectorAll('.footer .footer-card li')).map(contact => getText(contact)).filter(Boolean),
    }
  }

  const drawPageChrome = (pdf, docData, logoDataUrl, palette) => {
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const marginX = 34
    const [brandR, brandG, brandB] = palette.brand
    const [accentR, accentG, accentB] = palette.accent

    pdf.setFillColor(brandR, brandG, brandB)
    pdf.rect(0, 0, pageWidth, 86, 'F')
    pdf.setFillColor(accentR, accentG, accentB)
    pdf.rect(0, 82, pageWidth, 4, 'F')

    if (logoDataUrl) {
      try {
        pdf.addImage(logoDataUrl, 'PNG', marginX, 18, 42, 42)
      } catch {
        // Ignore logo failures and keep document export working.
      }
    }

    const textX = logoDataUrl ? marginX + 56 : marginX
    pdf.setTextColor(255, 255, 255)
    pdf.setFont('helvetica', 'bold')
    pdf.setFontSize(10)
    pdf.text(String(documentBranding.tagline || '').toUpperCase(), textX, 24)
    pdf.setFontSize(18)
    pdf.text(docData.title || documentBranding.name, textX, 42)
    pdf.setFont('helvetica', 'normal')
    pdf.setFontSize(10)
    const subtitle = pdf.splitTextToSize(docData.subtitle || 'Document exporte depuis l’administration.', pageWidth - textX - 120)
    pdf.text(subtitle, textX, 58)

    const chipText = docData.typeLabel || 'Export PDF'
    pdf.setDrawColor(255, 255, 255)
    pdf.setTextColor(255, 255, 255)
    pdf.setFont('helvetica', 'bold')
    pdf.setFontSize(10)
    const chipWidth = Math.max(90, pdf.getTextWidth(chipText) + 24)
    pdf.roundedRect(pageWidth - marginX - chipWidth, 24, chipWidth, 24, 12, 12, 'S')
    pdf.text(chipText, pageWidth - marginX - (chipWidth / 2), 40, { align: 'center' })

    pdf.setDrawColor(219, 227, 238)
    pdf.line(marginX, pageHeight - 32, pageWidth - marginX, pageHeight - 32)
    pdf.setTextColor(100, 116, 139)
    pdf.setFont('helvetica', 'normal')
    pdf.setFontSize(9)
    const pageNumber = pdf.getCurrentPageInfo().pageNumber
    const footerText = `${documentBranding.address}  |  ${documentBranding.contacts.join('  |  ')}`
    pdf.text(pdf.splitTextToSize(footerText, pageWidth - (marginX * 2) - 70), marginX, pageHeight - 18)
    pdf.text(`Page ${pageNumber}`, pageWidth - marginX, pageHeight - 18, { align: 'right' })
  }

  const ensureSpace = (pdf, currentY, requiredHeight, docData, logoDataUrl, palette) => {
    const pageHeight = pdf.internal.pageSize.getHeight()
    if (currentY + requiredHeight <= pageHeight - 54) return currentY
    pdf.addPage()
    drawPageChrome(pdf, docData, logoDataUrl, palette)
    return 108
  }

  const drawMetaCards = (pdf, currentY, meta, palette, docData, logoDataUrl) => {
    if (!meta.length) return currentY
    const pageWidth = pdf.internal.pageSize.getWidth()
    const marginX = 34
    const gap = 14
    const cardWidth = (pageWidth - (marginX * 2) - gap) / 2
    let y = ensureSpace(pdf, currentY, 110, docData, logoDataUrl, palette)
    let rowStartY = y
    let rowHeight = 0

    meta.forEach((item, index) => {
      if (index > 0 && index % 2 === 0) {
        rowStartY += rowHeight + gap
        y = ensureSpace(pdf, rowStartY, 110, docData, logoDataUrl, palette)
        rowStartY = y
        rowHeight = 0
      }

      const colIndex = index % 2
      const x = marginX + (colIndex * (cardWidth + gap))
      const valueLines = pdf.splitTextToSize(item.value || '-', cardWidth - 28)
      const cardHeight = Math.max(58, 34 + (valueLines.length * 12))

      pdf.setFillColor(248, 250, 252)
      pdf.setDrawColor(219, 227, 238)
      pdf.roundedRect(x, rowStartY, cardWidth, cardHeight, 14, 14, 'FD')
      pdf.setTextColor(100, 116, 139)
      pdf.setFont('helvetica', 'bold')
      pdf.setFontSize(10)
      pdf.text(item.label || 'Information', x + 14, rowStartY + 18)
      pdf.setTextColor(15, 23, 42)
      pdf.setFont('helvetica', 'normal')
      pdf.setFontSize(11)
      pdf.text(valueLines, x + 14, rowStartY + 34)
      rowHeight = Math.max(rowHeight, cardHeight)
    })

    return rowStartY + rowHeight + 18
  }

  const drawSummaryCards = (pdf, currentY, summaries, palette, docData, logoDataUrl) => {
    if (!summaries.length) return currentY
    const pageWidth = pdf.internal.pageSize.getWidth()
    const marginX = 34
    const gap = 12
    const columns = pdf.internal.pageSize.getWidth() > 700 ? 4 : 2
    const cardWidth = (pageWidth - (marginX * 2) - (gap * (columns - 1))) / columns
    let y = currentY

    summaries.forEach((item, index) => {
      if (index % columns === 0) {
        y = ensureSpace(pdf, y, 82, docData, logoDataUrl, palette)
      }

      const rowIndex = Math.floor(index / columns)
      const colIndex = index % columns
      const boxY = y + (rowIndex > 0 && colIndex === 0 ? 88 : 0)
      const x = marginX + (colIndex * (cardWidth + gap))
      const toneMap = {
        success: [22, 101, 52],
        danger: [185, 28, 28],
        warning: [146, 64, 14],
        primary: [29, 78, 216],
        info: [29, 78, 216],
      }
      const [r, g, b] = toneMap[item.tone] || toneMap.primary
      pdf.setFillColor(r, g, b)
      pdf.roundedRect(x, boxY, cardWidth, 64, 16, 16, 'F')
      pdf.setTextColor(255, 255, 255)
      pdf.setFont('helvetica', 'bold')
      pdf.setFontSize(9)
      pdf.text(pdf.splitTextToSize(item.label || 'Indicateur', cardWidth - 24), x + 12, boxY + 18)
      pdf.setFontSize(13)
      pdf.text(pdf.splitTextToSize(item.value || '-', cardWidth - 24), x + 12, boxY + 40)
      if (colIndex === columns - 1 || index === summaries.length - 1) {
        y = boxY + 78
      }
    })

    return y
  }

  const drawNoteSections = (pdf, currentY, notes, palette, docData, logoDataUrl) => {
    let y = currentY
    notes.forEach((note) => {
      y = ensureSpace(pdf, y, 88, docData, logoDataUrl, palette)
      pdf.setFillColor(248, 250, 252)
      pdf.setDrawColor(219, 227, 238)
      pdf.roundedRect(34, y, pdf.internal.pageSize.getWidth() - 68, 64, 16, 16, 'FD')
      pdf.setTextColor(100, 116, 139)
      pdf.setFont('helvetica', 'bold')
      pdf.setFontSize(10)
      pdf.text(note.title || 'Informations', 48, y + 18)
      pdf.setTextColor(15, 23, 42)
      pdf.setFont('helvetica', 'normal')
      pdf.setFontSize(11)
      const noteText = note.lines.join('  |  ') || '-'
      pdf.text(pdf.splitTextToSize(noteText, pdf.internal.pageSize.getWidth() - 96), 48, y + 38)
      y += 80
    })
    return y
  }

  const drawContactSection = (pdf, currentY, docData, palette, logoDataUrl) => {
    let y = ensureSpace(pdf, currentY, 96, docData, logoDataUrl, palette)
    const pageWidth = pdf.internal.pageSize.getWidth()
    const marginX = 34
    const gap = 14
    const cardWidth = (pageWidth - (marginX * 2) - gap) / 2

    const address = docData.address || documentBranding.address
    const contacts = (docData.contacts && docData.contacts.length ? docData.contacts : documentBranding.contacts).join('  |  ')

    pdf.setFillColor(248, 250, 252)
    pdf.setDrawColor(219, 227, 238)
    pdf.roundedRect(marginX, y, cardWidth, 64, 16, 16, 'FD')
    pdf.roundedRect(marginX + cardWidth + gap, y, cardWidth, 64, 16, 16, 'FD')

    pdf.setTextColor(100, 116, 139)
    pdf.setFont('helvetica', 'bold')
    pdf.setFontSize(10)
    pdf.text('Adresse', marginX + 14, y + 18)
    pdf.text('Contacts', marginX + cardWidth + gap + 14, y + 18)

    pdf.setTextColor(15, 23, 42)
    pdf.setFont('helvetica', 'normal')
    pdf.setFontSize(11)
    pdf.text(pdf.splitTextToSize(address, cardWidth - 28), marginX + 14, y + 38)
    pdf.text(pdf.splitTextToSize(contacts, cardWidth - 28), marginX + cardWidth + gap + 14, y + 38)

    return y + 78
  }

  const downloadHtmlAsXls = ({ type, contentHtml }) => {
    if (!process.client) return
    const html = `<!doctype html><html><head><meta charset="utf-8"></head><body>${contentHtml}</body></html>`
    const blob = new Blob([html], { type: 'application/vnd.ms-excel' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = buildExportFileName(type, 'xls')
    link.click()
    URL.revokeObjectURL(url)
  }

  const downloadPdfHtml = async ({ html, fileName = buildExportFileName('document', 'pdf') }) => {
    if (!process.client || !html) return false
    const docData = parseExportDocument(html)
    const maxColumns = Math.max(2, ...docData.tables.map(table => table.head.length || table.body[0]?.length || 0))
    const orientation = maxColumns >= 6 ? 'l' : 'p'
    const [{ jsPDF }, { default: autoTable }, logoDataUrl] = await Promise.all([
      import('jspdf'),
      import('jspdf-autotable'),
      loadImageAsDataUrl(documentLogoUrl),
    ])

    const pdf = new jsPDF({
      orientation,
      unit: 'pt',
      format: 'a4',
      compress: true,
    })

    const palette = {
      brand: toRgb('#0f172a'),
      accent: toRgb('#d4af37'),
      line: toRgb('#dbe3ee'),
      paper: toRgb('#f8fafc'),
      text: toRgb('#0f172a'),
      muted: toRgb('#64748b'),
      headFill: toRgb('#0f172a'),
      headText: [255, 255, 255],
    }

    pdf.setProperties({
      title: docData.documentTitle || fileName.replace(/\.pdf$/i, ''),
      subject: docData.title || 'Export',
      author: documentBranding.name,
      creator: documentBranding.name,
    })

    drawPageChrome(pdf, docData, logoDataUrl, palette)

    let currentY = 108
    currentY = drawMetaCards(pdf, currentY, docData.meta, palette, docData, logoDataUrl)
    currentY = drawSummaryCards(pdf, currentY, docData.summaries, palette, docData, logoDataUrl)
    currentY = drawNoteSections(pdf, currentY, docData.notes, palette, docData, logoDataUrl)

    docData.tables.forEach((table) => {
      currentY = ensureSpace(pdf, currentY, 56, docData, logoDataUrl, palette)
      pdf.setTextColor(...palette.muted)
      pdf.setFont('helvetica', 'bold')
      pdf.setFontSize(10)
      pdf.text(table.title || 'Tableau', 34, currentY)
      autoTable(pdf, {
        startY: currentY + 10,
        head: [table.head],
        body: table.body,
        margin: { top: 96, right: 34, bottom: 48, left: 34 },
        theme: 'grid',
        headStyles: {
          fillColor: palette.headFill,
          textColor: palette.headText,
          fontStyle: 'bold',
          fontSize: 9,
          halign: 'left',
        },
        styles: {
          font: 'helvetica',
          fontSize: 8.5,
          cellPadding: 6,
          lineColor: palette.line,
          lineWidth: 0.6,
          textColor: palette.text,
          overflow: 'linebreak',
        },
        bodyStyles: {
          fillColor: [255, 255, 255],
        },
        alternateRowStyles: {
          fillColor: palette.paper,
        },
        didDrawPage: () => {
          drawPageChrome(pdf, docData, logoDataUrl, palette)
        },
      })
      currentY = (pdf.lastAutoTable?.finalY || currentY) + 18
    })

    currentY = drawContactSection(pdf, currentY, docData, palette, logoDataUrl)
    pdf.save(fileName)
    return true
  }

  const openPrintPreviewHtml = ({ html, title = 'Document', autoPrint = true }) => {
    if (!process.client || !html) return false
    const printWindow = window.open('', '_blank', 'noopener,noreferrer,width=1180,height=920')
    if (!printWindow) return false

    const safeTitle = escapeHtml(title || 'Document')
    let preparedHtml = String(html)
      .replace(/<title>[\s\S]*?<\/title>/i, `<title>${safeTitle}</title>`)

    if (autoPrint) {
      preparedHtml = preparedHtml.replace('</body>', `
        <script>
          window.addEventListener('load', function () {
            setTimeout(function () {
              try { window.focus(); } catch (e) {}
              try { window.print(); } catch (e) {}
            }, 250);
          });
        </script>
      </body>`)
    }

    printWindow.document.open()
    printWindow.document.write(preparedHtml)
    printWindow.document.close()
    return true
  }

  return {
    buildExportFileName,
    buildExportTimestamp,
    getPrintedByLabel,
    getSanitizedExportHtml,
    buildPdfDocumentHtml,
    downloadHtmlAsXls,
    downloadPdfHtml,
    openPrintPreviewHtml,
  }
}
