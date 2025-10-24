#!/usr/bin/env python3
# ===============================================================
#  collect_otx.py
#  Author: Lello Molinario
#  Description:
#   Raccolta automatica di Indicatori di Compromissione (IoC)
#   da AlienVault OTX tramite API pubblica, con esportazione STIX 2.1
# ===============================================================

import os
import json
import requests
from datetime import datetime
from stix2 import Indicator, Bundle

# === CONFIGURAZIONE ===
CONFIG_PATH = "../config.json"
OUTPUT_DIR = "../feeds/processed"
OTX_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"

os.makedirs(OUTPUT_DIR, exist_ok=True)
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")

def load_api_key():
    """Carica la API key dal file config.json."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["otx"]["api_key"]
    except Exception as e:
        raise RuntimeError(f"Impossibile leggere API key OTX: {e}")

def fetch_pulses(api_key, limit=5):
    """Scarica le pulse più recenti da OTX."""
    headers = {"X-OTX-API-KEY": api_key}
    params = {"limit": limit}
    try:
        print("[+] Download pulse da OTX...")
        r = requests.get(OTX_URL, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception as e:
        print(f"[!] Errore nel download OTX: {e}")
        return []

def extract_iocs(pulses):
    """Estrae gli IoC da una lista di pulse."""
    iocs = []
    for pulse in pulses:
        pulse_name = pulse.get("name", "Unnamed Pulse")
        indicators = pulse.get("indicators", [])
        for i in indicators:
            i_type = i.get("type", "")
            value = i.get("indicator", "")
            if not value:
                continue

            # Costruisci il pattern STIX
            if i_type in ["IPv4", "IPv6", "ip"]:
                pattern = f"[ipv4-addr:value = '{value}']"
            elif "domain" in i_type:
                pattern = f"[domain-name:value = '{value}']"
            elif "url" in i_type:
                pattern = f"[url:value = '{value}']"
            elif "hash" in i_type or i_type in ["md5", "sha1", "sha256"]:
                pattern = f"[file:hashes.'{i_type}' = '{value}']"
            else:
                continue

            ioc = Indicator(
                name=f"OTX – {pulse_name}",
                description=f"Indicator from OTX ({i_type})",
                pattern=pattern,
                pattern_type="stix",
                valid_from=datetime.utcnow()
            )
            iocs.append(ioc)

    print(f"[i] Totale IoC estratti: {len(iocs)}")
    return iocs

def save_stix(indicators):
    """Salva gli indicatori in formato STIX 2.1."""
    bundle = Bundle(objects=indicators)
    out_path = os.path.join(OUTPUT_DIR, f"otx_stix_{timestamp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(bundle))
    print(f"[✓] Salvato: {out_path} ({len(indicators)} indicatori)")

def main():
    try:
        api_key = load_api_key()
    except RuntimeError as e:
        print(e)
        return

    pulses = fetch_pulses(api_key, limit=5)
    if not pulses:
        print("[!] Nessuna pulse ricevuta da OTX.")
        return

    indicators = extract_iocs(pulses)
    if indicators:
        save_stix(indicators)
    else:
        print("[!] Nessun indicatore valido generato.")

if __name__ == "__main__":
    main()
