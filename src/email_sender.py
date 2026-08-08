import os
import requests


def send_brevo_email(subject: str, html: str, settings: dict):
    email_cfg = settings["email"]
    api_key = os.getenv(email_cfg["api_key_env"])
    sender_email = os.getenv(email_cfg["sender_email_env"])
    recipient_email = os.getenv(email_cfg["recipient_email_env"])

    if not api_key or not sender_email or not recipient_email:
        raise RuntimeError("Variabili email mancanti: BREVO_API_KEY, EMAIL_FROM, EMAIL_TO")

    payload = {
        "sender": {"name": email_cfg.get("sender_name", "Crypto Deep Alert"), "email": sender_email},
        "to": [{"email": recipient_email}],
        "subject": subject,
        "htmlContent": html,
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={"api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if response.status_code >= 300:
        raise RuntimeError(f"Errore invio email Brevo: {response.status_code} {response.text}")
    return response.json()
