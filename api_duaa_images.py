#!/usr/bin/env python3
"""
API Flask pour n8n - Génération d'images de Dou'a
Pilotable depuis n8n comme l'API vidéo
Usage: python3 api_duaa_images.py
"""

from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from pathlib import Path
import json
import uuid
from datetime import datetime
import threading
import requests
import sys
import time
from collections import deque
import builtins
import os
import re
from unicodedata import normalize
import random
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display

# ============================================
# RATE LIMITING POUR RAILWAY
# ============================================
class RateLimitedPrint:
    """Limite les print() à 15/sec pour éviter Railway rate limit"""
    def __init__(self, max_per_second=15):
        self.max_per_second = max_per_second
        self.timestamps = deque(maxlen=max_per_second)
        self.original_print = builtins.print
        self.dropped = 0
        self.last_report = time.time()
        
    def __call__(self, *args, **kwargs):
        now = time.time()
        
        while self.timestamps and now - self.timestamps[0] > 1.0:
            self.timestamps.popleft()
        
        if len(self.timestamps) < self.max_per_second:
            self.timestamps.append(now)
            self.original_print(*args, **kwargs, file=sys.stderr)
            
            if self.dropped > 0 and now - self.last_report > 5.0:
                self.original_print(f"⚠️ {self.dropped} logs supprimés", file=sys.stderr)
                self.dropped = 0
                self.last_report = now
        else:
            self.dropped += 1

print = RateLimitedPrint(max_per_second=15)

# ============================================
# CONFIGURATION
# ============================================
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['TEMP_FOLDER'] = 'temp'
app.config['BACKGROUNDS_FOLDER'] = 'backgrounds'
app.config['FONTS_FOLDER'] = 'fonts'

# Créer les dossiers
for folder in [app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER'], 
               app.config['BACKGROUNDS_FOLDER'], app.config['FONTS_FOLDER']]:
    Path(folder).mkdir(exist_ok=True)

# Configuration par défaut
DEFAULT_CONFIG = {
    # Format & Dimensions
    "format": "instagram_square",  # instagram_square, instagram_story, facebook_post, custom
    "width": 1080,
    "height": 1080,
    
    # Texte
    "font_name": "Amiri-Regular.ttf",  # Police par défaut: Amiri (élégante et compatible)
    "font_size": 80,
    "text_color": "#FFFFFF",
    "text_align": "center",  # left, center, right
    "line_spacing": 1.5,
    "max_width_percent": 85,  # % de la largeur pour le texte (gère les sauts de ligne auto)
    
    # Style
    "background_color": "#1a472a",  # Vert islamique par défaut
    "background_image": None,  # URL ou chemin
    "background_blur": 0,  # 0-10
    "background_overlay": True,  # Overlay sombre sur l'image
    "overlay_opacity": 0.6,  # 0-1
    
    # Effets texte
    "text_shadow": True,
    "shadow_color": "#000000",
    "shadow_offset": (3, 3),
    "text_outline": False,
    "outline_width": 2,
    "outline_color": "#000000",
    
    # Décoration
    "add_border": False,
    "border_width": 20,
    "border_color": "#FFD700",  # Doré
    
    # Éléments supplémentaires
    "add_logo": False,
    "logo_path": None,
    "logo_position": "top_right",  # top_left, top_right, bottom_left, bottom_right
    "logo_size": 100,
    
    "add_footer": False,
    "footer_text": "",
    "footer_font_size": 30,
    "footer_color": "#CCCCCC",
    
    # Qualité
    "quality": 95,
    "format_output": "PNG"  # PNG, JPEG
}

# Formats prédéfinis
PRESET_FORMATS = {
    "instagram_square": {"width": 1080, "height": 1080},
    "instagram_story": {"width": 1080, "height": 1920},
    "instagram_portrait": {"width": 1080, "height": 1350},
    "facebook_post": {"width": 1200, "height": 630},
    "facebook_story": {"width": 1080, "height": 1920},
    "twitter_post": {"width": 1200, "height": 675},
    "pinterest_pin": {"width": 1000, "height": 1500},
    "custom": {"width": 1080, "height": 1080}
}

jobs = {}

def sanitize_filename(filename):
    """Nettoie un nom de fichier"""
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        filename = filename.rsplit('.', 1)[0]
    
    filename = filename.replace(' ', '_')
    filename = filename.replace(':', '-')
    filename = re.sub(r'[^a-zA-Z0-9\-_.]', '', filename)
    
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename

def clean_arabic_text(text):
    """Nettoie le texte arabe"""
    text = normalize('NFC', text)
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)
    text = text.strip()
    return text

def reshape_arabic_text(text):
    """Reshape le texte arabe pour l'affichage correct"""
    reshaper = ArabicReshaper(configuration={
        'delete_harakat': False,
        'support_ligatures': True,
    })
    reshaped = reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return bidi_text

def download_file(url, destination):
    """Télécharge un fichier depuis une URL avec logs détaillés"""
    try:
        print(f"📥 Téléchargement de: {url}")
        print(f"📁 Destination: {destination}")
        
        # Vérifier que l'URL est valide
        if not url or not url.startswith('http'):
            print(f"❌ URL invalide: {url}")
            return False
        
        # Headers pour Cloudinary et autres CDN
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, stream=True, timeout=30, headers=headers)
        response.raise_for_status()
        
        # Vérifier le Content-Type
        content_type = response.headers.get('Content-Type', '')
        print(f"📋 Content-Type: {content_type}")
        
        # Vérifier la taille
        content_length = response.headers.get('Content-Length')
        if content_length:
            size_mb = int(content_length) / (1024 * 1024)
            print(f"📦 Taille: {size_mb:.2f} MB")
        
        with open(destination, 'wb') as f:
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                total_size += len(chunk)
        
        print(f"✅ Téléchargé: {total_size / 1024:.2f} KB")
        
        # Vérifier que le fichier existe et n'est pas vide
        if Path(destination).exists() and Path(destination).stat().st_size > 0:
            print(f"✅ Fichier créé: {destination}")
            return True
        else:
            print(f"❌ Fichier vide ou inexistant")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur HTTP téléchargement {url}: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale téléchargement {url}: {e}")
        return False

def download_fallback_font():
    """Télécharge une police arabe de secours si aucune police n'est trouvée"""
    fallback_fonts = [
        {
            "name": "Amiri-Regular.ttf",
            "url": "https://github.com/alif-type/amiri/raw/main/Amiri-Regular.ttf"
        },
        {
            "name": "Scheherazade-Regular.ttf", 
            "url": "https://github.com/silnrsi/font-scheherazade/raw/master/results/Scheherazade-Regular.ttf"
        }
    ]
    
    fonts_folder = Path(app.config['FONTS_FOLDER'])
    fonts_folder.mkdir(exist_ok=True)
    
    for font_info in fallback_fonts:
        font_path = fonts_folder / font_info["name"]
        if not font_path.exists():
            try:
                print(f"📥 Téléchargement police de secours: {font_info['name']}")
                response = requests.get(font_info["url"], timeout=30)
                response.raise_for_status()
                
                with open(font_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✅ Police téléchargée: {font_path}")
                return str(font_path)
            except Exception as e:
                print(f"⚠️ Échec téléchargement {font_info['name']}: {e}")
                continue
    
    return None

def get_font(font_path, size):
    """Charge une police TrueType"""
    try:
        # Si le chemin est absolu et existe, l'utiliser directement
        if Path(font_path).is_absolute() and Path(font_path).exists():
            return ImageFont.truetype(str(font_path), size)
        
        # Chercher dans le dossier fonts/ du projet
        project_font = Path(app.config['FONTS_FOLDER']) / font_path
        if project_font.exists():
            print(f"✅ Police trouvée: {project_font}")
            return ImageFont.truetype(str(project_font), size)
        
        # Chercher dans le répertoire courant (pour Railway)
        current_dir_font = Path(font_path)
        if current_dir_font.exists():
            print(f"✅ Police trouvée: {current_dir_font}")
            return ImageFont.truetype(str(current_dir_font), size)
        
        # Chercher dans fonts/ relatif au script
        script_dir = Path(__file__).parent
        script_font = script_dir / 'fonts' / font_path
        if script_font.exists():
            print(f"✅ Police trouvée: {script_font}")
            return ImageFont.truetype(str(script_font), size)
        
        # Chercher dans les polices système
        system_font_paths = [
            f"/usr/share/fonts/truetype/{font_path}",
            f"/usr/share/fonts/{font_path}",
            f"/System/Library/Fonts/{font_path}",
            f"C:/Windows/Fonts/{font_path}"
        ]
        
        for sys_path in system_font_paths:
            if Path(sys_path).exists():
                print(f"✅ Police système trouvée: {sys_path}")
                return ImageFont.truetype(sys_path, size)
        
        # ⚠️ CRITIQUE: Police arabe non trouvée - télécharger une police de secours
        print(f"⚠️ Police {font_path} introuvable!")
        print("📥 Tentative de téléchargement d'une police arabe de secours...")
        
        fallback_path = download_fallback_font()
        if fallback_path and Path(fallback_path).exists():
            print(f"✅ Utilisation de la police de secours: {fallback_path}")
            return ImageFont.truetype(fallback_path, size)
        
        # En dernier recours, utiliser la police par défaut (ne supporte PAS l'arabe)
        print(f"❌ ERREUR CRITIQUE: Aucune police arabe disponible!")
        print(f"❌ Ajoutez KFGQPC-Uthman-Taha.ttf dans le dossier fonts/")
        return ImageFont.load_default()
        
    except Exception as e:
        print(f"⚠️ Erreur chargement police {font_path}: {e}")
        return ImageFont.load_default()

def wrap_text(text, font, max_width):
    """Découpe le texte en lignes pour respecter la largeur max - Compatible RTL"""
    # Pour l'arabe, on travaille avec le texte AVANT reshape
    # On va découper puis reshaper chaque ligne individuellement
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

def create_gradient_background(width, height, color1, color2, direction='vertical'):
    """Crée un fond avec gradient"""
    base = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(base)
    
    if direction == 'vertical':
        for y in range(height):
            r = int(color1[0] + (color2[0] - color1[0]) * y / height)
            g = int(color1[1] + (color2[1] - color1[1]) * y / height)
            b = int(color1[2] + (color2[2] - color1[2]) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:  # horizontal
        for x in range(width):
            r = int(color1[0] + (color2[0] - color1[0]) * x / width)
            g = int(color1[1] + (color2[1] - color1[1]) * x / width)
            b = int(color1[2] + (color2[2] - color1[2]) * x / width)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    return base

def hex_to_rgb(hex_color):
    """Convertit couleur hex en RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def generate_duaa_image(duaa_text, config, output_path):
    """Génère l'image de dou'a"""
    try:
        # Dimensions
        if config['format'] in PRESET_FORMATS:
            width = PRESET_FORMATS[config['format']]['width']
            height = PRESET_FORMATS[config['format']]['height']
        else:
            width = config['width']
            height = config['height']
        
        print(f"📐 Dimensions: {width}x{height}")
        
        # Créer le fond
        if config['background_image']:
            print(f"🖼️ Traitement du background: {config['background_image']}")
            
            # Image de fond
            if config['background_image'].startswith('http'):
                print(f"🌐 Background depuis URL")
                bg_temp = Path(app.config['TEMP_FOLDER']) / f"bg_{uuid.uuid4()}.jpg"
                
                if download_file(config['background_image'], str(bg_temp)):
                    try:
                        print(f"📂 Ouverture de l'image téléchargée...")
                        img = Image.open(bg_temp)
                        print(f"✅ Image ouverte: {img.size}, mode: {img.mode}")
                        bg_temp.unlink()  # Supprimer le fichier temporaire
                    except Exception as e:
                        print(f"❌ Erreur ouverture image: {e}")
                        print(f"⚠️ Fallback: couleur de fond")
                        img = Image.new('RGB', (width, height), hex_to_rgb(config['background_color']))
                        if bg_temp.exists():
                            bg_temp.unlink()
                else:
                    print(f"❌ Échec téléchargement, utilisation couleur de fond")
                    img = Image.new('RGB', (width, height), hex_to_rgb(config['background_color']))
            else:
                print(f"📁 Background depuis fichier local")
                bg_path = Path(app.config['BACKGROUNDS_FOLDER']) / config['background_image']
                if bg_path.exists():
                    img = Image.open(bg_path)
                    print(f"✅ Image locale ouverte: {img.size}")
                else:
                    print(f"❌ Fichier local introuvable: {bg_path}")
                    img = Image.new('RGB', (width, height), hex_to_rgb(config['background_color']))
            
            # Redimensionner et recadrer
            print(f"🔄 Conversion en RGB...")
            img = img.convert('RGB')
            img_ratio = img.width / img.height
            target_ratio = width / height
            
            print(f"📏 Redimensionnement de {img.size} vers {width}x{height}")
            
            if img_ratio > target_ratio:
                new_height = height
                new_width = int(height * img_ratio)
            else:
                new_width = width
                new_height = int(width / img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Centrer le crop
            left = (img.width - width) // 2
            top = (img.height - height) // 2
            img = img.crop((left, top, left + width, top + height))
            print(f"✂️ Image recadrée: {img.size}")
            
            # Appliquer le blur si demandé
            if config['background_blur'] > 0:
                print(f"🌫️ Application blur: {config['background_blur']}")
                img = img.filter(ImageFilter.GaussianBlur(radius=config['background_blur']))
            
            # Overlay sombre
            if config['background_overlay']:
                print(f"🎭 Application overlay: opacité {config['overlay_opacity']}")
                overlay = Image.new('RGBA', (width, height), (0, 0, 0, int(255 * config['overlay_opacity'])))
                img = img.convert('RGBA')
                img = Image.alpha_composite(img, overlay)
                img = img.convert('RGB')
        else:
            print(f"🎨 Création fond couleur unie: {config['background_color']}")
            # Couleur unie
            img = Image.new('RGB', (width, height), hex_to_rgb(config['background_color']))
        
        # Ajouter une bordure si demandé
        if config['add_border']:
            border = config['border_width']
            bordered = Image.new('RGB', (width + border*2, height + border*2), hex_to_rgb(config['border_color']))
            bordered.paste(img, (border, border))
            img = bordered.resize((width, height), Image.Resampling.LANCZOS)
        
        draw = ImageDraw.Draw(img)
        
        # Charger la police - le nom peut être juste le nom de fichier
        font = get_font(config['font_name'], config['font_size'])
        
        # Nettoyer le texte arabe (SANS reshaper pour l'instant)
        duaa_text = clean_arabic_text(duaa_text)
        
        # Découper le texte en lignes AVANT de reshaper
        max_text_width = int(width * config['max_width_percent'] / 100)
        lines = wrap_text(duaa_text, font, max_text_width)
        
        # MAINTENANT reshaper chaque ligne individuellement pour préserver RTL
        reshaped_lines = []
        for line in lines:
            reshaped_line = reshape_arabic_text(line)
            reshaped_lines.append(reshaped_line)
        
        # Calculer la hauteur totale du texte
        line_height = int(config['font_size'] * config['line_spacing'])
        total_text_height = len(reshaped_lines) * line_height
        
        # Position de départ (centré verticalement)
        y = (height - total_text_height) // 2
        
        # Dessiner chaque ligne
        text_color = hex_to_rgb(config['text_color'])
        
        for line in reshaped_lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            
            # Position X selon alignement
            if config['text_align'] == 'center':
                x = (width - text_width) // 2
            elif config['text_align'] == 'left':
                x = (width - max_text_width) // 2
            else:  # right
                x = width - (width - max_text_width) // 2 - text_width
            
            # Ombre portée
            if config['text_shadow']:
                shadow_color = hex_to_rgb(config['shadow_color'])
                shadow_x = x + config['shadow_offset'][0]
                shadow_y = y + config['shadow_offset'][1]
                draw.text((shadow_x, shadow_y), line, font=font, fill=shadow_color)
            
            # Contour
            if config['text_outline']:
                outline_color = hex_to_rgb(config['outline_color'])
                for adj_x in range(-config['outline_width'], config['outline_width']+1):
                    for adj_y in range(-config['outline_width'], config['outline_width']+1):
                        draw.text((x+adj_x, y+adj_y), line, font=font, fill=outline_color)
            
            # Texte principal
            draw.text((x, y), line, font=font, fill=text_color)
            
            y += line_height
        
        # Ajouter un footer si demandé
        if config['add_footer'] and config['footer_text']:
            footer_font = get_font(config['font_name'], config['footer_font_size'])
            footer_text = reshape_arabic_text(config['footer_text'])
            footer_bbox = footer_font.getbbox(footer_text)
            footer_width = footer_bbox[2] - footer_bbox[0]
            footer_x = (width - footer_width) // 2
            footer_y = height - config['footer_font_size'] - 30
            
            footer_color = hex_to_rgb(config['footer_color'])
            draw.text((footer_x, footer_y), footer_text, font=footer_font, fill=footer_color)
        
        # Ajouter un logo si demandé
        if config['add_logo'] and config['logo_path']:
            logo_path = Path(app.config['BACKGROUNDS_FOLDER']) / config['logo_path']
            if logo_path.exists():
                logo = Image.open(logo_path).convert('RGBA')
                logo.thumbnail((config['logo_size'], config['logo_size']), Image.Resampling.LANCZOS)
                
                # Position du logo
                positions = {
                    'top_left': (20, 20),
                    'top_right': (width - logo.width - 20, 20),
                    'bottom_left': (20, height - logo.height - 20),
                    'bottom_right': (width - logo.width - 20, height - logo.height - 20)
                }
                
                pos = positions.get(config['logo_position'], (width - logo.width - 20, 20))
                img.paste(logo, pos, logo)
        
        # Sauvegarder
        if config['format_output'].upper() == 'PNG':
            img.save(output_path, 'PNG', quality=config['quality'], optimize=True)
        else:
            img.save(output_path, 'JPEG', quality=config['quality'], optimize=True)
        
        print(f"✅ Image générée: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_image_job(job_id, duaa_text, config, output_name):
    """Traite un job de génération d'image"""
    try:
        jobs[job_id]['status'] = 'generating'
        jobs[job_id]['progress'] = 30
        
        output_ext = 'png' if config['format_output'].upper() == 'PNG' else 'jpg'
        output_path = Path(app.config['OUTPUT_FOLDER']) / f"{output_name}.{output_ext}"
        
        if generate_duaa_image(duaa_text, config, str(output_path)):
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['progress'] = 100
            jobs[job_id]['output_path'] = str(output_path)
            jobs[job_id]['download_url'] = f"/api/download/{output_path.name}"
            jobs[job_id]['finished_at'] = datetime.now().isoformat()
            print(f"✅ Job {job_id} terminé")
        else:
            jobs[job_id]['status'] = 'error'
            jobs[job_id]['error'] = 'Erreur lors de la génération'
            
    except Exception as e:
        print(f"❌ Erreur job {job_id}: {e}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)

# ============================================
# ROUTES API
# ============================================

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Génère une image de dou'a
    Body JSON:
    {
        "duaa_text": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ",
        "output_name": "bismillah",
        "config": {
            "format": "instagram_square",
            "font_size": 80,
            "background_color": "#1a472a"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Body JSON requis'}), 400
        
        duaa_text = data.get('duaa_text')
        
        if not duaa_text:
            return jsonify({'error': 'duaa_text requis'}), 400
        
        job_id = str(uuid.uuid4())[:8]
        
        # Merger config
        config = DEFAULT_CONFIG.copy()
        custom_config = data.get('config', {})
        config.update(custom_config)
        
        # Nom de sortie
        output_name = sanitize_filename(data.get('output_name', f"duaa_{job_id}"))
        
        # Créer le job
        jobs[job_id] = {
            'id': job_id,
            'status': 'processing',
            'progress': 0,
            'duaa_text': duaa_text[:50] + '...' if len(duaa_text) > 50 else duaa_text,
            'started_at': datetime.now().isoformat(),
            'finished_at': None,
            'output_path': None,
            'download_url': None,
            'error': None
        }
        
        # Lancer le traitement en thread
        thread = threading.Thread(
            target=process_image_job,
            args=(job_id, duaa_text, config, output_name)
        )
        thread.daemon = True
        thread.start()
        
        print(f"🚀 Job {job_id} démarré")
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'status': 'processing',
            'status_url': f"/api/status/{job_id}",
            'estimated_time': 5
        }), 202
        
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>', methods=['GET'])
def api_status(job_id):
    """Vérifie le statut d'un job"""
    job = jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job introuvable'}), 404
    
    return jsonify(job)

@app.route('/api/download/<filename>', methods=['GET'])
def api_download(filename):
    """Télécharge une image générée"""
    filepath = Path(app.config['OUTPUT_FOLDER']) / filename
    
    if not filepath.exists():
        return jsonify({'error': 'Fichier introuvable'}), 404
    
    return send_file(filepath, as_attachment=True)

@app.route('/api/health', methods=['GET'])
def health():
    """Health check pour n8n"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'jobs_count': len(jobs)
    })

@app.route('/api/formats', methods=['GET'])
def api_formats():
    """Liste les formats disponibles"""
    return jsonify({
        'formats': PRESET_FORMATS,
        'default': 'instagram_square'
    })

@app.route('/api/docs', methods=['GET'])
def docs():
    """Documentation de l'API"""
    return jsonify({
        'endpoints': {
            '/api/generate': {
                'method': 'POST',
                'description': 'Génère une image de dou\'a',
                'body': {
                    'duaa_text': 'string (requis) - Le texte de la dou\'a en arabe',
                    'output_name': 'string (optionnel) - Nom du fichier de sortie',
                    'config': {
                        'format': 'string - instagram_square, instagram_story, facebook_post, etc.',
                        'font_size': 'number - Taille de la police',
                        'text_color': 'string hex - Couleur du texte',
                        'background_color': 'string hex - Couleur de fond',
                        'background_image': 'string - URL ou nom du fichier de fond',
                        'add_footer': 'boolean - Ajouter un footer',
                        'footer_text': 'string - Texte du footer'
                    }
                }
            },
            '/api/status/:job_id': {
                'method': 'GET',
                'description': 'Vérifie le statut d\'un job'
            },
            '/api/download/:filename': {
                'method': 'GET',
                'description': 'Télécharge une image générée'
            },
            '/api/formats': {
                'method': 'GET',
                'description': 'Liste les formats d\'image disponibles'
            }
        },
        'config_options': DEFAULT_CONFIG
    })

if __name__ == '__main__':
    print("=" * 60)
    print("🖼️  API Flask pour n8n - Générateur d'images Dou'a")
    print("=" * 60)
    print(f"📡 Serveur: http://localhost:8000")
    print(f"📚 Documentation: http://localhost:8000/api/docs")
    print(f"❤️  Health check: http://localhost:8000/api/health")
    print(f"📋 Formats: http://localhost:8000/api/formats")
    print()
    print("💡 Placez vos polices arabes dans fonts/")
    print("💡 Placez vos images de fond dans backgrounds/")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8000)
