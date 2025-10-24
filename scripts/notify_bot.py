#!/usr/bin/env python3
# ===============================================================
#  notify_bot.py
#  Author: Lello Molinario
#  Description:
#   Invia notifiche Telegram sull'esito della pipeline CTI.
#   Integrabile con scheduler.py.
# ===============================================================

import os
import requests
from datetime import datetime

# === CONFIG ===
BOT_TOKEN = "INSERISCI_IL_TUO_TOKEN"
CHAT_ID = "INSERISCI_IL_TUO_CHAT_ID"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

def send_message(text):
    """Invia un messaggio testuale su Telegram."""
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(API_URL, data=payload, timeout=10)
        r.raise_for_status()
        print(f"[✓] Notifica Telegram inviata ({r.status_code})")
    except Exception as e:
        print(f"[!] Errore invio Telegram: {e}")

def notify_pipeline(status: str, log_file: str):
    """Crea un messaggio formattato con stato e log."""
    emoji = "✅" if status.lower() == "success" else "❌"
    time_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    msg = (
        f"{emoji} *CTI Automation Pipeline – {status.upper()}*\n"
        f"🕒 `{time_now}`\n"
        f"📄 Log file: `{os.path.basename(log_file)}`"
    )
    send_message(msg)

if __name__ == "__main__":
    # Test manuale
    notify_pipeline("success", "../logs/run_test.log")
