#!/usr/bin/env python3
# ===============================================================
#  collect_abusech.py
#  Author: Lello Molinario
#  Description:
#   Scarica e normalizza IoC da Abuse.ch (URLhaus + MalwareBazaar)
#   Esporta in formato STIX 2.1 compatibile.
# ===============================================================

import os
import requests
import pandas as pd
from datetime import datetime
from stix2 import Indicator, Bundle

# === CONFIGURAZIONE ===
OUTPUT_DIR = "../feeds/processed"
SOURCES = {
    "urlhaus": "https://urlhaus.abuse.ch/downloads/csv_recent/",
    "bazaar":  "https://bazaar.abuse.ch/export/csv/recent/"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")

def download_feed(url):
    """Scarica un feed CSV da Abuse.ch e restituisce il contenuto testuale."""
    print(f"[+] Downloading {url}")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[!] Errore nel download: {e}")
        return None

def parse_csv(content):
    """Pulisce e restituisce un DataFrame con gli IoC principali."""
    try:
        df = pd.read_csv(
            pd.io.common.StringIO(content),
            comment="#",
            header=None,
            names=["date", "url", "status", "threat", "tld", "url_status",
                   "urlhaus_link", "reporter"],
            usecols=[0, 1, 2, 3, 4],
            engine="python"
        )
        df = df.dropna(subset=["url"])
        return df
    except Exception as e:
        print(f"[!] Errore nel parsing CSV: {e}")
        return pd.DataFrame()

def create_stix(df, source_name):
    """Crea indicatori STIX a partire dal DataFrame."""
    indicators = []
    for _, row in df.iterrows():
        pattern = f"[url:value = '{row['url']}']"
        ioc = Indicator(
            name=f"{source_name} – {row['threat']}",
            description=f"Indicator from {source_name} ({row['status']})",
            pattern=pattern,
            pattern_type="stix",
            valid_from=datetime.utcnow()
        )
        indicators.append(ioc)
    return indicators

def main():
    all_indicators = []
    for name, url in SOURCES.items():
        content = download_feed(url)
        if not content:
            continue
        df = parse_csv(content)
        indicators = create_stix(df.head(50), name)  # Limita per test
        all_indicators.extend(indicators)

    if all_indicators:
        bundle = Bundle(objects=all_indicators)
        out_path = os.path.join(OUTPUT_DIR, f"abusech_stix_{timestamp}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(bundle))
        print(f"[✓] Salvato: {out_path} ({len(all_indicators)} indicatori)")
    else:
        print("[!] Nessun indicatore generato")

if __name__ == "__main__":
    main()
