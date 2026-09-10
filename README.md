# vault-renderer

Obsidian Vault Web-Interface — Rendert Markdown-Vaults als durchsuchbare Web-Oberfläche.

## ✨ Features

- 🌙 **Dark Mode** mit Toggle
- 📁 **Ordner-Ansicht** für Vault-Strukturen
- 🔗 **Obsidian-Links** [[Link|Text]] werden automatisch konvertiert
- 📊 **Tabellen** mit korrektem Styling
- 🚀 **Flask-basiert** (leichtgewichtig, schnell)
- ⚙️ **Systemd-Service** für Production

## 🚀 Quick Start

```bash
# Installation
python3 -m venv venv
venv/bin/pip install -r requirements.txt

# Starten
venv/bin/python app.py

# Auf Port 8054 öffnen
http://localhost:8054
```

## 📁 Struktur

```
vault-renderer/
├── app.py                 # Flask-Anwendung
├── requirements.txt       # Python-Abhängigkeiten
├── templates/             # HTML-Templates
│   ├── base.html         # Layout mit Navigation
│   ├── index.html        # Startseite
│   ├── page.html         # Markdown-Seite
│   └── folder.html       # Ordner-Ansicht
├── static/               # Statische Dateien (CSS, JS)
└── vault-renderer.service # Systemd-Service-Datei
```

## ⚙️ Konfiguration

In `app.py` den `VAULT_PATH` anpassen:

```python
VAULT_PATH = '/home/pi/repair-cafe/vault/20-Bereiche/Repair-Cafe'
```

## 🔧 Systemd-Service installieren

```bash
sudo cp vault-renderer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vault-renderer
sudo systemctl start vault-renderer
```

## 📊 Verwendung als Submodule

```bash
# In einem Projekt hinzufügen
git submodule add git@github.com:robotfreak/vault-renderer.git

# Config anpassen (app.py)
# - VAULT_PATH auf lokalen Vault zeigen lassen
# - Port anpassen (z.B. 8053, 8054, etc.)
```

## 🎯 Projekte die vault-renderer verwenden

- **Repair-Café** — Port 8054
- **Makerspace-Verwaltung** — Port 8053

## 📝 Lizenz

MIT License

---

**vault-renderer** — Made with ❤️ for berlinCreators Makerspace & Repair-Café
