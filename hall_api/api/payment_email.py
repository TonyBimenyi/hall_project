import json
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape

from .models import Payment


DEFAULT_BRANDING = {
    'name': 'Labertha Villa',
    'tagline': 'Reception & Evenementiel',
    'email': 'info@labertha-villa.com',
    'address': 'Karurama, Cibitoke, Bujumbura, Burundi',
    'contacts': ['+257 66 47 66 43', '+257 76 65 39 31', 'info@labertha-villa.com'],
    'documents': {
        'invoiceTitle': 'Recu de paiement',
    },
}

BRANDING_FILE = Path(__file__).resolve().parents[2] / 'config' / 'document-branding.json'


@lru_cache(maxsize=1)
def _load_document_branding():
    branding = dict(DEFAULT_BRANDING)
    try:
        with BRANDING_FILE.open('r', encoding='utf-8') as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            branding.update(payload)
    except Exception:
        pass

    contacts = branding.get('contacts')
    if not isinstance(contacts, list):
        branding['contacts'] = list(DEFAULT_BRANDING['contacts'])

    documents = dict(DEFAULT_BRANDING.get('documents') or {})
    raw_documents = branding.get('documents')
    if isinstance(raw_documents, dict):
        documents.update(raw_documents)
    branding['documents'] = documents
    return branding


def _format_money(value):
    try:
        amount = Decimal(str(value or 0)).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal('0.00')
    return f"{amount:,.2f} Fbu".replace(',', ' ')


def _format_date(value):
    if not value:
        return '-'
    if hasattr(value, 'strftime'):
        return value.strftime('%d/%m/%Y')
    return str(value)


def _format_period(start_date, end_date):
    if not start_date and not end_date:
        return '-'
    return f"{_format_date(start_date)} au {_format_date(end_date)}"


def _payment_type_label(kind):
    return 'Paiement total' if kind == 'full' else 'Avance'


def _build_payment_invoice_subject(payment, booking, branding):
    invoice_title = ((branding.get('documents') or {}).get('invoiceTitle') or 'Facture de paiement').strip()
    payment_code = (getattr(payment, 'code', '') or '').strip()
    booking_code = (getattr(booking, 'code', '') or '').strip()
    if payment_code and booking_code:
        return f"{invoice_title} {payment_code} - {booking_code}"
    if payment_code:
        return f"{invoice_title} {payment_code}"
    return invoice_title


def _build_payment_invoice_html(payment, booking, branding):
    remaining = booking.total_price - booking.paid_amount
    if remaining < 0:
        remaining = Decimal('0.00')

    payment_code = (getattr(payment, 'code', '') or '').strip() or f"Paiement #{payment.pk}"
    booking_code = (getattr(booking, 'code', '') or '').strip() or f"Reservation #{booking.pk}"
    hall_name = getattr(getattr(booking, 'hall', None), 'name', '') or '-'
    contacts = [str(item).strip() for item in (branding.get('contacts') or []) if str(item).strip()]
    contacts_text = ' | '.join(escape(item) for item in contacts) if contacts else '-'

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(payment_code)}</title>
</head>
<body style="margin:0;padding:24px;background:#f8fafc;font-family:Arial,sans-serif;color:#0f172a;">
  <div style="max-width:680px;margin:0 auto;background:#ffffff;border:1px solid #e2e8f0;border-radius:20px;overflow:hidden;">
    <div style="padding:28px 32px;background:linear-gradient(135deg,#0f172a,#1d4ed8);color:#ffffff;">
      <div style="font-size:13px;letter-spacing:0.08em;text-transform:uppercase;opacity:0.82;">{escape((branding.get('documents') or {}).get('invoiceTitle') or 'Recu de paiement')}</div>
      <div style="margin-top:8px;font-size:28px;font-weight:700;">{escape(branding.get('name') or DEFAULT_BRANDING['name'])}</div>
      <div style="margin-top:6px;font-size:14px;opacity:0.88;">{escape(branding.get('tagline') or DEFAULT_BRANDING['tagline'])}</div>
    </div>
    <div style="padding:32px;">
      <p style="margin:0 0 18px;font-size:15px;">Bonjour {escape(booking.customer_name or 'Client')},</p>
      <p style="margin:0 0 24px;font-size:15px;line-height:1.6;">Votre paiement a bien ete enregistre. Voici votre facture de paiement.</p>

      <div style="padding:18px;border:1px solid #dbeafe;border-radius:16px;background:#f8fbff;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;gap:16px;padding:6px 0;border-bottom:1px solid #e2e8f0;">
          <span style="color:#64748b;">Code paiement</span>
          <strong>{escape(payment_code)}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:12px 0 6px;border-bottom:1px solid #e2e8f0;">
          <span style="color:#64748b;">Code reservation</span>
          <strong>{escape(booking_code)}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:12px 0 6px;border-bottom:1px solid #e2e8f0;">
          <span style="color:#64748b;">Date paiement</span>
          <strong>{escape(_format_date(payment.date))}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:12px 0 6px;">
          <span style="color:#64748b;">Type</span>
          <strong>{escape(_payment_type_label(payment.kind))}</strong>
        </div>
      </div>

      <div style="margin-bottom:24px;">
        <div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#64748b;margin-bottom:10px;">Client</div>
        <div style="padding:18px;border:1px solid #e2e8f0;border-radius:16px;background:#ffffff;">
          <div style="font-weight:700;margin-bottom:6px;">{escape(booking.customer_name or 'Client')}</div>
          <div style="color:#475569;margin-bottom:4px;">{escape((booking.customer_email or '-').strip() or '-')}</div>
          <div style="color:#475569;margin-bottom:4px;">{escape(hall_name)}</div>
          <div style="color:#64748b;">Periode: {escape(_format_period(booking.start_date, booking.end_date))}</div>
        </div>
      </div>

      <div style="margin-bottom:24px;">
        <div style="font-size:12px;letter-spacing:0.08em;text-transform:uppercase;color:#64748b;margin-bottom:10px;">Details</div>
        <div style="padding:18px;border:1px solid #e2e8f0;border-radius:16px;background:#ffffff;">
          <div style="display:flex;justify-content:space-between;gap:16px;padding:6px 0;border-bottom:1px solid #f1f5f9;">
            <span style="color:#64748b;">Reference</span>
            <strong>{escape(payment.reference or '-')}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;gap:16px;padding:12px 0 6px;border-bottom:1px solid #f1f5f9;">
            <span style="color:#64748b;">Methode</span>
            <strong>{escape(payment.method or '-')}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;gap:16px;padding:12px 0 6px;">
            <span style="color:#64748b;">Salle</span>
            <strong>{escape(hall_name)}</strong>
          </div>
        </div>
      </div>

      <div style="padding:20px;border-radius:18px;background:#0f172a;color:#ffffff;">
        <div style="display:flex;justify-content:space-between;gap:16px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.12);">
          <span style="opacity:0.8;">Montant paye</span>
          <strong>{escape(_format_money(payment.amount))}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:12px 0 6px;border-bottom:1px solid rgba(255,255,255,0.12);">
          <span style="opacity:0.8;">Total reservation</span>
          <strong>{escape(_format_money(booking.total_price))}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;gap:16px;padding:16px 0 4px;font-size:18px;font-weight:700;">
          <span>Reste a payer</span>
          <span>{escape(_format_money(remaining))}</span>
        </div>
      </div>

      <div style="margin-top:28px;padding-top:20px;border-top:1px solid #e2e8f0;color:#475569;font-size:14px;line-height:1.7;">
        <div style="font-weight:700;color:#0f172a;margin-bottom:6px;">Adresse et contact</div>
        <div>{escape(branding.get('address') or DEFAULT_BRANDING['address'])}</div>
        <div>{contacts_text}</div>
      </div>
    </div>
  </div>
</body>
</html>"""


def _build_payment_invoice_text(payment, booking, branding):
    remaining = booking.total_price - booking.paid_amount
    if remaining < 0:
        remaining = Decimal('0.00')

    hall_name = getattr(getattr(booking, 'hall', None), 'name', '') or '-'
    contacts = [str(item).strip() for item in (branding.get('contacts') or []) if str(item).strip()]
    return (
        f"Bonjour {booking.customer_name or 'Client'},\n\n"
        "Votre paiement a bien ete enregistre. Voici votre facture de paiement.\n\n"
        f"Code paiement : {payment.code or f'Paiement #{payment.pk}'}\n"
        f"Code reservation : {booking.code or f'Reservation #{booking.pk}'}\n"
        f"Date paiement : {_format_date(payment.date)}\n"
        f"Type : {_payment_type_label(payment.kind)}\n"
        f"Reference : {payment.reference or '-'}\n"
        f"Methode : {payment.method or '-'}\n"
        f"Client : {booking.customer_name or 'Client'}\n"
        f"Email : {(booking.customer_email or '-').strip() or '-'}\n"
        f"Salle : {hall_name}\n"
        f"Periode : {_format_period(booking.start_date, booking.end_date)}\n"
        f"Montant paye : {_format_money(payment.amount)}\n"
        f"Total reservation : {_format_money(booking.total_price)}\n"
        f"Reste a payer : {_format_money(remaining)}\n\n"
        f"Adresse : {branding.get('address') or DEFAULT_BRANDING['address']}\n"
        f"Contacts : {' | '.join(contacts) if contacts else '-'}\n"
    )


def send_payment_invoice_email(payment):
    payment = Payment.objects.select_related('booking', 'booking__hall').filter(pk=getattr(payment, 'pk', None)).first()
    if payment is None or payment.status != 'paid' or payment.booking is None:
        return False

    booking = payment.booking
    to_email = (getattr(booking, 'customer_email', '') or '').strip()
    if not to_email:
        return False

    branding = _load_document_branding()
    subject = _build_payment_invoice_subject(payment, booking, branding)
    text_body = _build_payment_invoice_text(payment, booking, branding)
    html_body = _build_payment_invoice_html(payment, booking, branding)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@hall.local',
        to=[to_email],
    )
    message.attach_alternative(html_body, 'text/html')
    message.send(fail_silently=False)
    return True
