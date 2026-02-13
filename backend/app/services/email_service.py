"""Servizio email con Resend per invio email transazionali."""

import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

VERIFICATION_EMAIL_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#0a0a0a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a; padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#111; border-radius:16px; overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="padding:40px 40px 20px; text-align:center;">
              <h1 style="margin:0; font-size:28px; font-weight:700; color:#fff; letter-spacing:-0.5px;">
                Site Builder
              </h1>
              <div style="width:60px; height:3px; background:linear-gradient(90deg, #3b82f6, #8b5cf6); margin:16px auto 0; border-radius:2px;"></div>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:20px 40px 40px;">
              <h2 style="margin:0 0 12px; font-size:22px; color:#fff; font-weight:600;">
                Verifica il tuo indirizzo email
              </h2>
              <p style="margin:0 0 24px; font-size:15px; color:#94a3b8; line-height:1.6;">
                Grazie per esserti registrato su Site Builder! Per completare la registrazione
                e accedere a tutte le funzionalita, conferma il tuo indirizzo email cliccando
                il pulsante qui sotto.
              </p>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:8px 0 32px;">
                    <a href="{verify_url}"
                       style="display:inline-block; padding:14px 36px; background:linear-gradient(135deg, #3b82f6, #2563eb);
                              color:#fff; font-size:16px; font-weight:600; text-decoration:none;
                              border-radius:12px; letter-spacing:0.3px;">
                      Verifica Email
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px; font-size:13px; color:#64748b; line-height:1.5;">
                Se il pulsante non funziona, copia e incolla questo link nel tuo browser:
              </p>
              <p style="margin:0 0 24px; font-size:13px; color:#3b82f6; word-break:break-all; line-height:1.5;">
                {verify_url}
              </p>
              <div style="border-top:1px solid #1e293b; padding-top:20px;">
                <p style="margin:0; font-size:12px; color:#475569; line-height:1.5;">
                  Questo link scadra tra 24 ore. Se non hai richiesto questa verifica,
                  puoi ignorare questa email in sicurezza.
                </p>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px 30px; background-color:#0d0d0d; text-align:center;">
              <p style="margin:0; font-size:12px; color:#475569;">
                &copy; 2026 Site Builder &mdash; Crea il tuo sito web con l'intelligenza artificiale
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


PASSWORD_RESET_EMAIL_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0; padding:0; background-color:#0a0a0a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0a0a; padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#111; border-radius:16px; overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="padding:40px 40px 20px; text-align:center;">
              <h1 style="margin:0; font-size:28px; font-weight:700; color:#fff; letter-spacing:-0.5px;">
                Site Builder
              </h1>
              <div style="width:60px; height:3px; background:linear-gradient(90deg, #3b82f6, #8b5cf6); margin:16px auto 0; border-radius:2px;"></div>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:20px 40px 40px;">
              <h2 style="margin:0 0 12px; font-size:22px; color:#fff; font-weight:600;">
                Reimposta la tua password
              </h2>
              <p style="margin:0 0 24px; font-size:15px; color:#94a3b8; line-height:1.6;">
                Abbiamo ricevuto una richiesta per reimpostare la password del tuo account
                Site Builder. Clicca il pulsante qui sotto per scegliere una nuova password.
              </p>
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding:8px 0 32px;">
                    <a href="{reset_url}"
                       style="display:inline-block; padding:14px 36px; background:linear-gradient(135deg, #3b82f6, #2563eb);
                              color:#fff; font-size:16px; font-weight:600; text-decoration:none;
                              border-radius:12px; letter-spacing:0.3px;">
                      Reimposta Password
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px; font-size:13px; color:#64748b; line-height:1.5;">
                Se il pulsante non funziona, copia e incolla questo link nel tuo browser:
              </p>
              <p style="margin:0 0 24px; font-size:13px; color:#3b82f6; word-break:break-all; line-height:1.5;">
                {reset_url}
              </p>
              <div style="border-top:1px solid #1e293b; padding-top:20px;">
                <p style="margin:0; font-size:12px; color:#475569; line-height:1.5;">
                  Questo link scadra tra 1 ora. Se non hai richiesto il reset della password,
                  puoi ignorare questa email in sicurezza. La tua password non verra modificata.
                </p>
              </div>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px 30px; background-color:#0d0d0d; text-align:center;">
              <p style="margin:0; font-size:12px; color:#475569;">
                &copy; 2026 Site Builder &mdash; Crea il tuo sito web con l'intelligenza artificiale
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    """
    Invia email di reset password tramite Resend.
    Ritorna True se l'invio e' riuscito, False altrimenti.
    """
    if not settings.RESEND_API_KEY:
        logger.warning(
            "RESEND_API_KEY non configurata. Email di reset non inviata. "
            "Link di reset: %s", reset_url
        )
        return False

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        html_content = PASSWORD_RESET_EMAIL_HTML.replace("{reset_url}", reset_url)

        params: resend.Emails.SendParams = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "Reimposta la tua password - Site Builder",
            "html": html_content,
        }

        response = resend.Emails.send(params)
        email_id = response.get("id", "?") if isinstance(response, dict) else getattr(response, "id", "?")
        logger.info("Email di reset password inviata a %s (id: %s)", to_email, email_id)
        return True

    except Exception as e:
        logger.error("Errore invio email di reset a %s: %s", to_email, str(e))
        return False


def send_verification_email(to_email: str, verify_url: str) -> bool:
    """
    Invia email di verifica tramite Resend.
    Ritorna True se l'invio e' riuscito, False altrimenti.
    """
    if not settings.RESEND_API_KEY:
        logger.warning(
            "RESEND_API_KEY non configurata. Email di verifica non inviata. "
            "Link di verifica: %s", verify_url
        )
        return False

    try:
        import resend
        resend.api_key = settings.RESEND_API_KEY

        html_content = VERIFICATION_EMAIL_HTML.replace("{verify_url}", verify_url)

        params: resend.Emails.SendParams = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": "Verifica il tuo indirizzo email - Site Builder",
            "html": html_content,
        }

        response = resend.Emails.send(params)
        email_id = response.get("id", "?") if isinstance(response, dict) else getattr(response, "id", "?")
        logger.info("Email di verifica inviata a %s (id: %s)", to_email, email_id)
        return True

    except Exception as e:
        logger.error("Errore invio email di verifica a %s: %s", to_email, str(e))
        return False
