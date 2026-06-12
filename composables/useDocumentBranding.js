import branding from '~/config/document-branding.json'

export const useDocumentBranding = () => {
  const documentBranding = {
    ...branding,
    contacts: Array.isArray(branding?.contacts) ? branding.contacts : [],
    documents: branding?.documents || {},
  }

  const documentLogoUrl = new URL('../labertha-logo.png', import.meta.url).href

  const escapeHtml = (value) => String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')

  return {
    documentBranding,
    documentLogoUrl,
    escapeHtml,
  }
}
