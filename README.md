# 🌙 Générateur d'Images Dou'a pour Instagram & Facebook

API Flask pilotable depuis n8n pour générer des images de dou'a (invocations) en arabe, optimisées pour les réseaux sociaux.

## 🚀 Déploiement sur Railway

### 1. Créer un compte Railway
- Aller sur https://railway.app
- Se connecter avec GitHub

### 2. Créer un nouveau projet
```bash
# Depuis votre terminal local
git init
git add .
git commit -m "Initial commit"
```

### 3. Pousser sur GitHub
```bash
# Créer un nouveau repo sur GitHub puis:
git remote add origin https://github.com/VOTRE_USERNAME/duaa-image-generator.git
git branch -M main
git push -u origin main
```

### 4. Déployer sur Railway
1. Sur Railway.app, cliquer sur "New Project"
2. Choisir "Deploy from GitHub repo"
3. Sélectionner votre repository
4. Railway détecte automatiquement Python et lance le déploiement
5. Une fois déployé, copier l'URL publique (ex: `https://votre-app.railway.app`)

## 📋 Configuration des Polices Arabes

### Police par Défaut: KFGQPC-Uthman-Taha

Cette application utilise par défaut la police **KFGQPC-Uthman-Taha** (Uthmanic Hafs) qui est parfaite pour le texte coranique car elle respecte les règles de typographie du Mushaf.

**⚠️ Important**: Vous devez ajouter le fichier `KFGQPC-Uthman-Taha.ttf` à votre repository GitHub.

### Installation de la Police

```bash
# 1. Créer le dossier fonts
mkdir fonts

# 2. Copier votre fichier de police
cp /chemin/vers/KFGQPC-Uthman-Taha.ttf fonts/

# 3. Ajouter au Git
git add fonts/KFGQPC-Uthman-Taha.ttf
git commit -m "Add KFGQPC Uthman Taha font"
git push
```

**📖 Guide détaillé**: Consultez `FONT_GUIDE.md` pour plus d'informations.

### Polices Alternatives (Optionnel)

Si vous souhaitez utiliser d'autres polices, voici quelques options gratuites:

1. **Amiri** (élégante, traditionnelle)
   - Télécharger: https://fonts.google.com/specimen/Amiri
   - Fichiers: `Amiri-Regular.ttf`, `Amiri-Bold.ttf`

2. **Scheherazade** (lisible, moderne)
   - Télécharger: https://software.sil.org/scheherazade/
   - Fichier: `Scheherazade-Regular.ttf`

3. **Cairo** (moderne, polyvalente)
   - Télécharger: https://fonts.google.com/specimen/Cairo
   - Fichiers: `Cairo-Regular.ttf`, `Cairo-Bold.ttf`

### Structure du Projet avec la Police

```
votre-projet/
├── fonts/
│   └── KFGQPC-Uthman-Taha.ttf     ← Votre police ici
├── backgrounds/
├── api_duaa_images.py
└── requirements.txt
```

## 🎨 Utilisation avec n8n

### Workflow n8n type

```
[Trigger] → [HTTP Request] → [Wait] → [HTTP Request Check Status] → [Download Image]
```

### 1. Générer une image

**Node: HTTP Request**
- Method: `POST`
- URL: `https://votre-app.railway.app/api/generate`
- Body (JSON):
```json
{
  "duaa_text": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ",
  "output_name": "bismillah_instagram",
  "config": {
    "format": "instagram_square",
    "font_size": 90,
    "font_name": "Amiri-Regular.ttf",
    "text_color": "#FFFFFF",
    "background_color": "#1a472a",
    "add_footer": true,
    "footer_text": "@votre_compte"
  }
}
```

**Réponse:**
```json
{
  "success": true,
  "job_id": "a1b2c3d4",
  "status": "processing",
  "status_url": "/api/status/a1b2c3d4",
  "estimated_time": 5
}
```

### 2. Vérifier le statut

**Node: HTTP Request**
- Method: `GET`
- URL: `https://votre-app.railway.app/api/status/{{ $json.job_id }}`

**Réponse (en cours):**
```json
{
  "id": "a1b2c3d4",
  "status": "generating",
  "progress": 50
}
```

**Réponse (terminé):**
```json
{
  "id": "a1b2c3d4",
  "status": "completed",
  "progress": 100,
  "download_url": "/api/download/bismillah_instagram.png",
  "output_path": "outputs/bismillah_instagram.png"
}
```

### 3. Télécharger l'image

**Node: HTTP Request**
- Method: `GET`
- URL: `https://votre-app.railway.app{{ $json.download_url }}`
- Response Format: `File`

## 📐 Formats Disponibles

```json
{
  "instagram_square": {"width": 1080, "height": 1080},
  "instagram_story": {"width": 1080, "height": 1920},
  "instagram_portrait": {"width": 1080, "height": 1350},
  "facebook_post": {"width": 1200, "height": 630},
  "facebook_story": {"width": 1080, "height": 1920},
  "twitter_post": {"width": 1200, "height": 675},
  "pinterest_pin": {"width": 1000, "height": 1500}
}
```

## ⚙️ Options de Configuration

### Texte
```json
{
  "font_name": "Amiri-Regular.ttf",
  "font_size": 80,
  "text_color": "#FFFFFF",
  "text_align": "center",
  "line_spacing": 1.5,
  "max_width_percent": 85
}
```

### Fond
```json
{
  "background_color": "#1a472a",
  "background_image": "https://url-de-votre-image.jpg",
  "background_blur": 3,
  "background_overlay": true,
  "overlay_opacity": 0.6
}
```

### Effets
```json
{
  "text_shadow": true,
  "shadow_color": "#000000",
  "shadow_offset": [3, 3],
  "text_outline": true,
  "outline_width": 2,
  "outline_color": "#000000"
}
```

### Bordure
```json
{
  "add_border": true,
  "border_width": 20,
  "border_color": "#FFD700"
}
```

### Footer
```json
{
  "add_footer": true,
  "footer_text": "@mon_compte",
  "footer_font_size": 30,
  "footer_color": "#CCCCCC"
}
```

### Logo
```json
{
  "add_logo": true,
  "logo_path": "logo.png",
  "logo_position": "top_right",
  "logo_size": 100
}
```

## 🎨 Couleurs Recommandées

### Thèmes Islamiques
- Vert foncé: `#1a472a`
- Vert émeraude: `#50C878`
- Doré: `#FFD700`
- Turquoise: `#40E0D0`

### Thèmes Neutres
- Blanc pur: `#FFFFFF`
- Noir profond: `#1a1a1a`
- Gris anthracite: `#2c3e50`
- Beige: `#f5f5dc`

## 📸 Images de Fond

### Utilisation locale
Placer vos images dans `backgrounds/`:
```json
{
  "background_image": "mosque.jpg"
}
```

### Utilisation URL
```json
{
  "background_image": "https://unsplash.com/photos/mosque-image.jpg"
}
```

### Sources recommandées (gratuites)
- Unsplash: https://unsplash.com/s/photos/islamic-art
- Pexels: https://www.pexels.com/search/mosque/
- Pixabay: https://pixabay.com/images/search/islamic/

## 🔧 Exemples de Requêtes

### 1. Image simple (Instagram)
```json
{
  "duaa_text": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ",
  "output_name": "duaa_jannah",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "format": "instagram_square",
    "font_size": 85,
    "background_color": "#1a472a"
  }
}
```

### 2. Image avec fond personnalisé
```json
{
  "duaa_text": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً",
  "output_name": "duaa_dunya",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "format": "instagram_square",
    "background_image": "https://images.unsplash.com/photo-mosque.jpg",
    "background_blur": 4,
    "overlay_opacity": 0.7,
    "text_color": "#FFFFFF",
    "text_shadow": true,
    "add_footer": true,
    "footer_text": "@islamic_reminders"
  }
}
```

### 3. Story Instagram avec bordure
```json
{
  "duaa_text": "سُبْحَانَ اللهِ وَبِحَمْدِهِ",
  "output_name": "tasbih_story",
  "config": {
    "format": "instagram_story",
    "font_size": 100,
    "background_color": "#2c3e50",
    "add_border": true,
    "border_width": 15,
    "border_color": "#FFD700",
    "text_color": "#FFFFFF"
  }
}
```

### 4. Post Facebook avec logo
```json
{
  "duaa_text": "الْحَمْدُ للهِ رَبِّ الْعَالَمِينَ",
  "output_name": "alhamdulillah_fb",
  "config": {
    "format": "facebook_post",
    "background_color": "#50C878",
    "add_logo": true,
    "logo_path": "logo.png",
    "logo_position": "top_right",
    "logo_size": 120,
    "add_footer": true,
    "footer_text": "www.monsite.com"
  }
}
```

## 🛠️ API Endpoints

### GET /api/health
Health check
```bash
curl https://votre-app.railway.app/api/health
```

### GET /api/formats
Liste des formats disponibles
```bash
curl https://votre-app.railway.app/api/formats
```

### GET /api/docs
Documentation complète de l'API
```bash
curl https://votre-app.railway.app/api/docs
```

### POST /api/generate
Génère une image

### GET /api/status/:job_id
Vérifie le statut d'un job

### GET /api/download/:filename
Télécharge l'image générée

## 🐛 Debugging

### Logs Railway
```bash
# Dans Railway Dashboard
Project → Deployments → View Logs
```

### Test local
```bash
pip install -r requirements.txt
python api_duaa_images.py

# Puis dans un autre terminal:
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"duaa_text": "بسم الله", "config": {"format": "instagram_square"}}'
```

## 📝 Workflow n8n Complet

```
1. [Schedule Trigger] - Tous les jours à 9h
   ↓
2. [Google Sheets] - Lire une dou'a aléatoire
   ↓
3. [HTTP Request] - POST /api/generate
   ↓
4. [Wait] - 10 secondes
   ↓
5. [HTTP Request] - GET /api/status/{{job_id}}
   ↓
6. [IF] - status === "completed" ?
   ↓ OUI
7. [HTTP Request] - GET /api/download/{{filename}}
   ↓
8. [Instagram] - Publier l'image
   ↓
9. [Facebook] - Publier l'image
```

## 💡 Conseils

1. **Polices**: Utilisez Amiri ou Scheherazade pour un rendu professionnel
2. **Taille de police**: 70-90 pour carrés, 90-120 pour stories
3. **Contraste**: Toujours tester la lisibilité du texte sur le fond
4. **Footer**: Ajoutez votre @ pour la reconnaissance de marque
5. **Batch**: Générez plusieurs images avec différents formats d'un coup

## 📦 Limites Railway (Plan Gratuit)

- 500 MB RAM
- 1 GB Storage
- $5/mois de compute inclus
- Upgrade possible si besoin

## 🔐 Sécurité

Pour ajouter une authentification (optionnel):
```python
# Dans api_duaa_images.py
from functools import wraps

API_KEY = os.environ.get('API_KEY', 'votre-clé-secrète')

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/generate', methods=['POST'])
@require_api_key
def api_generate():
    # ...
```

Puis dans Railway, ajouter la variable d'environnement `API_KEY`.

## 📞 Support

En cas de problème:
1. Vérifier les logs Railway
2. Tester l'endpoint `/api/health`
3. Vérifier que les polices sont bien uploadées

## 📄 Licence

MIT License - Libre d'utilisation pour projets personnels et commerciaux
