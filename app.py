#!/usr/bin/env python3
"""
Repair-Café Vault Renderer
Rendert den Obsidian Vault (20-Bereiche/Repair-Cafe) als Web-Interface
"""

from flask import Flask, render_template, send_from_directory, abort, url_for
import os
import markdown
import re


def convert_obsidian_links(text, base_path=''):
    """Konvertiert [[Obsidian Link|Text]] und relative [Markdown](url) Links"""
    
    # 1. [[Obsidian Link|Text]] konvertieren
    def replace_obsidian(match):
        link_text = match.group(1)
        display_text = link_text
        if '|' in link_text:
            link_text, display_text = link_text.split('|', 1)
        
        folder = ''
        file_name = link_text
        
        if '/' in link_text:
            parts = link_text.rsplit('/', 1)
            folder = parts[0] + '/'
            file_name = parts[1]
        
        # Entscheidung: Ordner oder Datei?
        # 1. Wenn mit / endet → immer Ordner
        # 2. Wenn / im Pfad → Datei (z.B. Ordner/Datei)
        # 3. Wenn kein / und kein . im Namen → Ordner
        # 4. Sonst → Datei
        if link_text.endswith('/'):
            link_url = f'/vault/{base_path}{folder}{file_name}'  # Ordner, kein .md
        elif '/' in link_text:
            # Pfad mit Datei → .md hinzufügen
            if not file_name.endswith('.md'):
                file_name += '.md'
            link_url = f'/vault/{base_path}{folder}{file_name}'
        elif '.' not in file_name:
            # Kein Punkt im Namen → wahrscheinlich Ordner
            link_url = f'/vault/{base_path}{file_name}'  # Kein .md
        else:
            # Hat einen Punkt → Datei
            if not file_name.endswith('.md'):
                file_name += '.md'
            link_url = f'/vault/{base_path}{file_name}'
        
        return f'<a href="{link_url}">{display_text}</a>'
    
    text = re.sub(r'\[\[([^\]]+)\]\]', replace_obsidian, text)
    
    # 2. Obsidian Bilder-Links ![[Bild.png]] konvertieren → <img src="...">
    def replace_obsidian_image(match):
        image_path = match.group(1)
        
        # Pfad extrahieren (kann Ordner/Bild.png sein)
        folder = ''
        file_name = image_path
        if '/' in image_path:
            parts = image_path.rsplit('/', 1)
            folder = parts[0] + '/'
            file_name = parts[1]
        
        # Nur Bilder mit Extension behandeln
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
        if file_name.lower().endswith(image_extensions):
            # Bild-Pfad zusammenbauen
            if folder:
                img_url = f'/vault/{base_path}{folder}{file_name}'
            else:
                img_url = f'/vault/{base_path}{file_name}'
            return f'<img src="{img_url}" alt="{file_name}">'
        
        return match.group(0)  # Kein Bild → unverändert lassen
    
    text = re.sub(r'!\[\[([^\]]+)\]\]', replace_obsidian_image, text)
    
    # 3. Markdown Bilder-Links ![Alt](url) konvertieren → <img src="...">
    def replace_image(match):
        alt = match.group(1)
        url = match.group(2)
        
        # Externe Links und absolute Pfade nicht verändern
        if url.startswith('http') or url.startswith('/'):
            return match.group(0)
        
        # Bilder mit Extension (.png, .jpg, .gif, .svg, etc.) → Pfad korrigieren
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')
        if url.lower().endswith(image_extensions):
            if url.startswith('../'):
                # Relativer Pfad mit .. → Pfad bereinigen
                clean_path = '/vault/' + os.path.normpath(f'/vault/{url}').lstrip('/vault/').lstrip('/')
                return f'<img src="{clean_path}" alt="{alt}">'
            else:
                # Einfacher relativer Pfad
                return f'<img src="/vault/{base_path}{url}" alt="{alt}">'
        
        return match.group(0)  # Kein Bild → unverändert lassen
    
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)
    
    # 4. Relative [Markdown](url) Links konvertieren (KEINE Bilder!)
    def replace_md_link(match):
        display = match.group(1)
        url = match.group(2)
        
        # Externe Links und absolute Pfade nicht verändern
        if url.startswith('http') or url.startswith('/'):
            return match.group(0)
        
        # PDF-Links und Bilder (und andere Dateien) nicht verändern - KEIN .md anhängen!
        if '.' in url and not url.endswith('.md'):
            # Hat eine Extension (.pdf, .png, .jpg, .gif, etc.) → nicht verändern
            if url.startswith('../'):
                # Relativer Pfad mit .. → Pfad bereinigen (../ auflösen)
                # Aus ../99-Assets/Bild.png wird /vault/99-Assets/Bild.png
                clean_path = f'/vault/{url}'
                clean_path = '/vault/' + os.path.normpath(clean_path).lstrip('/vault/').lstrip('/')
                return f'<a href="{clean_path}">{display}</a>'
            else:
                # Einfacher relativer Pfad (z.B. Ordner/Bild.png)
                # base_path davor setzen
                return f'<a href="/vault/{base_path}{url}">{display}</a>'
        
        # Markdown-Links (.md oder keine Extension → als Markdown behandeln)
        folder = base_path if base_path else ''
        if url.endswith('/'):
            # Ordner → kein .md
            link_url = f'/vault/{folder}{url.rstrip("/")}'
        else:
            # Datei → .md anhängen wenn nicht schon vorhanden
            if not url.endswith('.md'):
                url += '.md'
            link_url = f'/vault/{folder}{url}'
        
        return f'<a href="{link_url}">{display}</a>'
    
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_md_link, text)
    return text


app = Flask(__name__)

# Konfiguration
VAULT_PATH = '/home/pi/repair-cafe/vault/20-Bereiche/Repair-Cafe'


@app.route('/')
def index():
    """Startseite mit Vault-Übersicht"""
    uebersicht_path = os.path.join(VAULT_PATH, '00-Uebersicht.md')
    if os.path.exists(uebersicht_path):
        with open(uebersicht_path, 'r') as f:
            content = f.read()
        # ERST Links konvertieren, DANN Markdown rendern!
        content = convert_obsidian_links(content)
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        return render_template('page.html', title='Repair-Café Verwaltung', content=html)
    else:
        return render_template('index.html', vault_path=VAULT_PATH)


@app.route('/vault/<path:filename>')
def vault_file(filename):
    """Vault Markdown-Dateien rendern oder Ordner auflisten"""
    filepath = os.path.join(VAULT_PATH, filename)
    
    if not filepath.startswith(VAULT_PATH):
        abort(403)
    
    # Wenn es ein Ordner ist, zeige die .md Dateien darin
    if os.path.isdir(filepath):
        files = []
        for f in sorted(os.listdir(filepath)):
            if f.endswith('.md'):
                files.append(f)
        return render_template('folder.html', folder=filename, files=files)
    
    if not os.path.exists(filepath):
        abort(404)
    
    if filename.endswith('.md'):
        with open(filepath, 'r') as f:
            content = f.read()
        # Ordner-Pfad für Links extrahieren
        folder_path = os.path.dirname(filename) + '/' if os.path.dirname(filename) else ''
        # ERST Links konvertieren, DANN Markdown rendern!
        content = convert_obsidian_links(content, folder_path)
        html = markdown.markdown(content, extensions=['tables', 'fenced_code'])
        return render_template('page.html', title=filename.replace('.md', ''), content=html)
    else:
        return send_from_directory(VAULT_PATH, filename)


@app.route('/<path:filename>')
def static_file(filename):
    """Statische Dateien ausliefern"""
    return send_from_directory('static', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8054, debug=False)
