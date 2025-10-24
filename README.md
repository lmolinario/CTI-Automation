# 🛰️ CTI-Automation
Repository di automazione OSINT e Threat Intelligence sviluppata da **Lello Molinario**  
Profilo: Digital Forensics & AI Security | Procura della Repubblica di Sassari

## 🎯 Obiettivo
Creare una pipeline automatizzata per la raccolta, normalizzazione e analisi di indicatori di compromissione (IoC) provenienti da fonti OSINT, Dark Web e Telegram.

## ⚙️ Struttura
- `scripts/` → raccolta e normalizzazione feed
- `feeds/` → dati grezzi e STIX normalizzati
- `analysis/` → notebook per classificazione e NER
- `reports/` → report periodici in PDF o STIX
- `docker/` → servizi MISP / OpenCTI / Kibana

## 🔧 Stack Tecnologico
Python 3.11 · pandas · stix2 · requests · spaCy · transformers · Jupyter · Docker

## 📘 Output Fase 1
- Feed automatizzato di IoC (Abuse.ch, OTX, Ahmia, Telegram)
- Dataset STIX 2.1 strutturato
- Mini-report tecnico: *Automated OSINT Intelligence for Digital Forensics – A Proof of Concept*

---

> ⚠️ **Nota:** Tutti i dati raccolti sono pubblici o de-identificati.  
> La repository è destinata a scopo di ricerca accademica e formazione.
