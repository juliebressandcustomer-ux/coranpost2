# 🚀 Guide de Démarrage Rapide

## 📦 Installation en 5 minutes

### 1. Prérequis

```bash
# Python 3.11+
python3 --version

# Git
git --version
```

### 2. Clone et Installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/duaa-image-generator.git
cd duaa-image-generator

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Télécharger les Polices Arabes

**Option A: Polices Google Fonts (Recommandé)**

```bash
# Créer le dossier fonts
mkdir fonts

# Télécharger Amiri (gratuite)
cd fonts
wget https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf
wget https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Bold.ttf
cd ..
```

**Option B: Polices SIL (Alternative)**

```bash
cd fonts
# Scheherazade
wget https://software.sil.org/downloads/r/scheherazade/Scheherazade-2.100.zip
unzip Scheherazade-2.100.zip
mv Scheherazade-2.100/*.ttf .
rm -rf Scheherazade-2.100*

# Lateef
wget https://software.sil.org/downloads/r/lateef/Lateef-4.200.zip
unzip Lateef-4.200.zip
mv Lateef-4.200/*.ttf .
rm -rf Lateef-4.200*
cd ..
```

### 4. Lancer le Serveur

```bash
python api_duaa_images.py
```

Votre API est maintenant disponible sur `http://localhost:8000` ! 🎉

### 5. Test Rapide

```bash
# Dans un autre terminal
python test_api.py
```

## 🌐 Déploiement sur Railway

### Étape 1: Créer un Repository GitHub

```bash
git init
git add .
git commit -m "Initial commit - Duaa Image Generator"

# Créer un nouveau repo sur GitHub puis:
git remote add origin https://github.com/VOTRE_USERNAME/duaa-image-generator.git
git push -u origin main
```

### Étape 2: Déployer sur Railway

1. Aller sur https://railway.app
2. Se connecter avec GitHub
3. Cliquer sur "New Project"
4. Choisir "Deploy from GitHub repo"
5. Sélectionner votre repository
6. Railway va automatiquement détecter Python et déployer

⏱️ **Temps de déploiement: ~3-5 minutes**

### Étape 3: Récupérer l'URL

Une fois déployé, Railway vous donne une URL comme:
```
https://duaa-image-generator-production.up.railway.app
```

Copiez cette URL, vous en aurez besoin pour n8n!

## 🔧 Configuration n8n

### Créer votre Premier Workflow

1. Ouvrir n8n
2. Créer un nouveau workflow
3. Ajouter les nodes suivants:

#### Node 1: Manual Trigger
- Type: "Manual Trigger"

#### Node 2: HTTP Request
- Method: `POST`
- URL: `https://votre-url.railway.app/api/generate`
- Body Type: `JSON`
- Body:
```json
{
  "duaa_text": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ",
  "output_name": "bismillah",
  "config": {
    "format": "instagram_square",
    "font_size": 90,
    "background_color": "#1a472a"
  }
}
```

#### Node 3: Wait
- Amount: 5
- Unit: Seconds

#### Node 4: HTTP Request
- Method: `GET`
- URL: `https://votre-url.railway.app/api/status/{{ $json.job_id }}`

#### Node 5: IF
- Condition: `{{ $json.status }}` equals `completed`

#### Node 6: HTTP Request (True branch)
- Method: `GET`
- URL: `https://votre-url.railway.app{{ $json.download_url }}`
- Response Format: `File`

### Tester le Workflow

1. Cliquer sur "Execute Workflow"
2. Attendre ~10 secondes
3. Télécharger l'image générée

## 💡 Premiers Exemples

### Exemple 1: Image Instagram Simple

```bash
curl -X POST https://votre-url.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "duaa_text": "سُبْحَانَ اللهِ وَبِحَمْدِهِ",
    "output_name": "subhanallah",
    "config": {
      "format": "instagram_square",
      "font_size": 85,
      "text_color": "#FFFFFF",
      "background_color": "#2c3e50"
    }
  }'
```

### Exemple 2: Story avec Fond Personnalisé

```bash
curl -X POST https://votre-url.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "duaa_text": "الْحَمْدُ للهِ رَبِّ الْعَالَمِينَ",
    "output_name": "alhamdulillah_story",
    "config": {
      "format": "instagram_story",
      "font_size": 100,
      "background_image": "https://images.unsplash.com/photo-1591604129939-f1efa4d9f7fa",
      "background_blur": 4,
      "overlay_opacity": 0.7,
      "add_footer": true,
      "footer_text": "@votre_compte"
    }
  }'
```

### Exemple 3: Post Facebook avec Logo

```bash
curl -X POST https://votre-url.railway.app/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "duaa_text": "لَا إِلَٰهَ إِلَّا اللهُ",
    "output_name": "tawheed_fb",
    "config": {
      "format": "facebook_post",
      "font_size": 95,
      "background_color": "#50C878",
      "add_logo": true,
      "logo_path": "logo.png",
      "logo_position": "top_right"
    }
  }'
```

## 📱 Templates Prêts à l'Emploi

### Template 1: Minimaliste
```json
{
  "format": "instagram_square",
  "font_size": 80,
  "text_color": "#FFFFFF",
  "background_color": "#1a1a1a",
  "text_shadow": true
}
```

### Template 2: Élégant
```json
{
  "format": "instagram_square",
  "font_size": 85,
  "text_color": "#FFFFFF",
  "background_color": "#2c3e50",
  "add_border": true,
  "border_width": 15,
  "border_color": "#FFD700"
}
```

### Template 3: Moderne
```json
{
  "format": "instagram_square",
  "font_size": 90,
  "background_image": "URL_DE_VOTRE_IMAGE",
  "background_blur": 5,
  "overlay_opacity": 0.6,
  "text_color": "#FFFFFF",
  "text_shadow": true,
  "add_footer": true,
  "footer_text": "@votre_compte"
}
```

## 🎨 Palette de Couleurs Islamiques

```
Verts:
- Vert foncé:    #1a472a
- Vert sauge:    #87a96b
- Vert émeraude: #50C878
- Vert olive:    #808000

Dorés:
- Or:            #FFD700
- Bronze:        #CD7F32
- Cuivre:        #B87333

Bleus:
- Bleu nuit:     #191970
- Turquoise:     #40E0D0
- Cobalt:        #0047AB

Neutres:
- Beige:         #f5f5dc
- Ivoire:        #FFFFF0
- Anthracite:    #2c3e50
```

## 🚨 Dépannage Rapide

### Erreur: Police non trouvée
```bash
# Vérifier que les polices sont dans fonts/
ls fonts/

# Si vide, télécharger Amiri:
cd fonts && wget https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf
```

### Erreur: Module non trouvé
```bash
pip install -r requirements.txt
```

### Erreur: Port déjà utilisé
```bash
# Changer le port dans api_duaa_images.py ligne finale:
app.run(debug=True, host='0.0.0.0', port=8001)
```

### Image générée vide
- Vérifier que le texte arabe est correct (UTF-8)
- Vérifier que la police supporte l'arabe
- Tester avec un texte simple: "بسم الله"

## 📞 Support & Ressources

- Documentation complète: `README.md`
- Exemples de dou'a: `duaa_examples.json`
- Tests: `test_api.py`
- Workflow n8n: `n8n_workflow_example.json`

## ✅ Checklist de Démarrage

- [ ] Python 3.11+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Polices arabes téléchargées dans `fonts/`
- [ ] Serveur lancé localement (`python api_duaa_images.py`)
- [ ] Tests passent (`python test_api.py`)
- [ ] Repository GitHub créé
- [ ] Déployé sur Railway
- [ ] URL Railway récupérée
- [ ] Workflow n8n configuré
- [ ] Premier test réussi

**Félicitations! Vous êtes prêt à générer des images de dou'a! 🎉**

---

**Temps total estimé: 15-20 minutes**
