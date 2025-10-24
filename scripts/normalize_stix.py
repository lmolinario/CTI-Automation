#!/usr/bin/env python3
# ===============================================================
#  normalize_stix.py
#  Author: Lello Molinario
#  Description:
#   Unisce più file STIX 2.1 provenienti da fonti OSINT diverse
#   (Abuse.ch, OTX, Telegram, ecc.) in un unico dataset consolidato.
# ===============================================================

import os
import json
from datetime import datetime
from stix2 import parse, Bundle

# === CONFIGURAZIONE ===
INPUT_DIR = "../feeds/processed"
OUTPUT_DIR = "../feeds/processed"
MERGED_FILENAME = f"merged_stix_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.json"

def load_stix_files(path):
    """Carica tutti i file STIX 2.1 in formato JSON dalla directory indicata."""
    files = [f for f in os.listdir(path) if f.endswith(".json")]
    all_objects = []

    for file in files:
        full_path = os.path.join(path, file)
        print(f"[+] Caricamento file: {file}")
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                bundle = parse(data, allow_custom=True)
                all_objects.extend(bundle.objects)
        except Exception as e:
            print(f"[!] Errore nel parsing di {file}: {e}")
            continue

    return all_objects

def deduplicate_indicators(indicators):
    """Rimuove duplicati in base al pattern STIX (es. [url:value = '...'])."""
    unique = {}
    for ioc in indicators:
        if hasattr(ioc, "pattern"):
            unique[ioc.pattern] = ioc
    print(f"[i] Totale indicatori unici: {len(unique)}")
    return list(unique.values())

def main():
    print("[*] Normalizzazione feed STIX in corso...")
    indicators = load_stix_files(INPUT_DIR)

    if not indicators:
        print("[!] Nessun indicatore trovato.")
        return

    unique_indicators = deduplicate_indicators(indicators)
    merged_bundle = Bundle(objects=unique_indicators)

    output_path = os.path.join(OUTPUT_DIR, MERGED_FILENAME)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(merged_bundle))

    print(f"[✓] Dataset STIX unificato salvato in: {output_path}")

if __name__ == "__main__":
    main()
