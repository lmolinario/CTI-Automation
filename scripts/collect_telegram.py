#!/usr/bin/env python3
# ===============================================================
#  collect_telegram.py
#  Author: Lello Molinario
#  Description:
#   Raccolta OSINT da canali Telegram pubblici tramite Telethon.
#   Estrae IoC (IP, URL, hash, e-mail) e li esporta in STIX 2.1.
# ===============================================================

import os
import re
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import RPCError
from stix2 import Indicator, Bundle

# === CONFIG ===
CONFIG_PATH = "../config.json"
OUTPUT_DIR = "../feeds/processed"
os.makedirs(OUTPUT_DIR, exist_ok=True)
timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M")

# === REGEX per IoC ===
IOC_PATTERNS = {
    "ipv4": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
    "domain": re.compile(r"\b([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"),
    "url": re.compile(r"https?://[^\s]+"),
    "md5": re.compile(r"\b[a-fA-F0-9]{32}\b"),
    "sha256": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
}

def load_config():
    """Carica configurazione da config.json"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["telegram"]["api_id"], data["telegram"]["api_hash"], data["telegram"]["channels"]

def extract_iocs_from_text(text):
    """Estrae tutti gli IoC da una stringa."""
    results = {}
    for ioc_type, pattern in IOC_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            results[ioc_type] = list(set(matches))
    return results

async def collect_messages():
    """Collega ai canali Telegram e raccoglie IoC."""
    api_id, api_hash, channels = load_config()
    client = TelegramClient("session_cti", api_id, api_hash)
    await client.start()

    all_indicators = []
    for channel in channels:
        try:
            print(f"[+] Scansione canale: {channel}")
            async for msg in client.iter_messages(channel, limit=100):
                if not msg.message:
                    continue
                found_iocs = extract_iocs_from_text(msg.message)
                for ioc_type, values in found_iocs.items():
                    for value in values:
                        if ioc_type == "ipv4":
                            pattern = f"[ipv4-addr:value = '{value}']"
                        elif ioc_type == "domain":
                            pattern = f"[domain-name:value = '{value}']"
                        elif ioc_type == "url":
                            pattern = f"[url:value = '{value}']"
                        elif ioc_type in ["md5", "sha256"]:
                            pattern = f"[file:hashes.'{ioc_type}' = '{value}']"
                        elif ioc_type == "email":
                            pattern = f"[email-addr:value = '{value}']"
                        else:
                            continue

                        ioc = Indicator(
                            name=f"Telegram – {channel}",
                            description=f"Indicator from Telegram ({ioc_type})",
                            pattern=pattern,
                            pattern_type="stix",
                            valid_from=datetime.utcnow()
                        )
                        all_indicators.append(ioc)
        except RPCError as e:
            print(f"[!] Errore Telegram ({channel}): {e}")
        except Exception as e:
            print(f"[!] Errore generico su {channel}: {e}")

    await client.disconnect()

    # Salva risultati STIX
    if all_indicators:
        bundle = Bundle(objects=all_indicators)
        out_path = os.path.join(OUTPUT_DIR, f"telegram_stix_{timestamp}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(str(bundle))
        print(f"[✓] Salvato: {out_path} ({len(all_indicators)} indicatori)")
    else:
        print("[!] Nessun indicatore trovato nei canali.")

def main():
    import asyncio
    asyncio.run(collect_messages())

if __name__ == "__main__":
    main()
