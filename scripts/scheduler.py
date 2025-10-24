#!/usr/bin/env python3
# ===============================================================
#  scheduler.py
#  Author: Lello Molinario
#  Description:
#   Orchestratore della pipeline CTI Automation:
#   esegue la raccolta OSINT (Abuse.ch, OTX, Telegram, etc.)
#   e la normalizzazione STIX, con log e timestamp.
# ===============================================================

import subprocess
import time
import os
from datetime import datetime

# === CONFIGURAZIONE ===
LOG_DIR = "../logs"
SCRIPTS = [
    "collect_abusech.py",
    # "collect_otx.py",
    # "collect_telegram.py",
    "normalize_stix.py"
]
INTERVAL_SECONDS = 3  # tempo tra gli script (per evitare saturazione)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.log")

def run_script(script):
    """Esegue uno script Python e cattura stdout/stderr nel log."""
    start = datetime.utcnow()
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"\n[{start}] ▶ Avvio: {script}\n")
        try:
            result = subprocess.run(
                ["python3", script],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
                timeout=300
            )
            log.write(result.stdout)
            if result.stderr:
                log.write("\n[!] STDERR:\n" + result.stderr)
            log.write(f"[✓] Terminato: {script} ({datetime.utcnow() - start})\n")
        except subprocess.TimeoutExpired:
            log.write(f"[X] Timeout: {script}\n")
        except Exception as e:
            log.write(f"[X] Errore esecuzione {script}: {e}\n")

def main():
    print(f"[*] Avvio scheduler CTI – {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"[*] Log file: {LOG_FILE}")

    for script in SCRIPTS:
        run_script(script)
        time.sleep(INTERVAL_SECONDS)

    print("[✓] Pipeline completata. Controlla i log per i dettagli.")

if __name__ == "__main__":
    main()
