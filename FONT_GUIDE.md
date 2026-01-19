# 📝 Guide d'Installation de la Police KFGQPC-Uthman-Taha

## 🎯 Structure du Projet avec la Police

```
votre-projet/
├── fonts/
│   └── KFGQPC-Uthman-Taha.ttf     ← Placer votre police ici
├── api_duaa_images.py
├── requirements.txt
├── Procfile
└── railway.json
```

## 📦 Ajouter la Police à votre Repository GitHub

### Méthode 1: Via Git (Recommandé)

```bash
# 1. Créer le dossier fonts
mkdir -p fonts

# 2. Copier votre fichier KFGQPC-Uthman-Taha.ttf dans fonts/
cp /chemin/vers/KFGQPC-Uthman-Taha.ttf fonts/

# 3. Vérifier que le fichier est bien là
ls -lh fonts/

# 4. Ajouter au repository
git add fonts/KFGQPC-Uthman-Taha.ttf
git commit -m "Add KFGQPC Uthman Taha font"
git push
```

### Méthode 2: Via l'Interface GitHub

1. Aller sur votre repository GitHub
2. Cliquer sur "Add file" → "Upload files"
3. Créer un dossier "fonts" (si pas encore créé)
4. Uploader `KFGQPC-Uthman-Taha.ttf`
5. Commit les changements

## 🚀 Configuration pour Railway

Une fois la police dans votre repo GitHub, Railway la déploiera automatiquement !

**Aucune configuration supplémentaire nécessaire** - l'API cherchera automatiquement la police dans:
1. Le dossier `fonts/` du projet
2. Le répertoire courant (racine du projet)
3. Les polices système

## 🔧 Utilisation dans n8n

### Configuration JSON Simple

```json
{
  "duaa_text": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ",
  "output_name": "bismillah",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 90,
    "format": "instagram_square"
  }
}
```

### Configuration JSON Complète

```json
{
  "duaa_text": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ",
  "output_name": "bismillah_complet",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 90,
    "format": "instagram_square",
    "text_color": "#FFFFFF",
    "background_color": "#1a472a",
    "text_shadow": true,
    "shadow_color": "#000000",
    "shadow_offset": [3, 3],
    "add_footer": true,
    "footer_text": "@mon_compte",
    "footer_font_size": 30
  }
}
```

## 📱 Exemples pour Différents Formats

### Instagram Carré (1080x1080)

```json
{
  "duaa_text": "سُبْحَانَ اللهِ وَبِحَمْدِهِ",
  "output_name": "subhanallah_square",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 85,
    "format": "instagram_square",
    "background_color": "#2c3e50",
    "text_color": "#FFFFFF"
  }
}
```

### Instagram Story (1080x1920)

```json
{
  "duaa_text": "الْحَمْدُ للهِ رَبِّ الْعَالَمِينَ",
  "output_name": "alhamdulillah_story",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 100,
    "format": "instagram_story",
    "background_color": "#1a472a",
    "text_color": "#FFFFFF",
    "add_footer": true,
    "footer_text": "@votre_compte"
  }
}
```

### Facebook Post (1200x630)

```json
{
  "duaa_text": "لَا إِلَٰهَ إِلَّا اللهُ",
  "output_name": "tawheed_facebook",
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 95,
    "format": "facebook_post",
    "background_color": "#50C878",
    "text_color": "#FFFFFF"
  }
}
```

## 🎨 Tailles de Police Recommandées

| Format | Taille Recommandée |
|--------|-------------------|
| Instagram Carré | 80-90 |
| Instagram Story | 100-120 |
| Instagram Portrait | 85-95 |
| Facebook Post | 90-100 |
| Twitter Post | 85-95 |

## 🧪 Tester en Local

```bash
# 1. S'assurer que la police est dans fonts/
ls fonts/KFGQPC-Uthman-Taha.ttf

# 2. Lancer l'API
python api_duaa_images.py

# 3. Tester avec curl
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "duaa_text": "بسم الله",
    "config": {
      "font_name": "KFGQPC-Uthman-Taha.ttf",
      "format": "instagram_square"
    }
  }'
```

## 🔍 Vérification de la Police

Créer un petit script pour vérifier que la police fonctionne:

```python
from PIL import ImageFont
from pathlib import Path

font_path = "fonts/KFGQPC-Uthman-Taha.ttf"

if Path(font_path).exists():
    try:
        font = ImageFont.truetype(font_path, 80)
        print("✅ Police chargée avec succès!")
    except Exception as e:
        print(f"❌ Erreur: {e}")
else:
    print("❌ Fichier non trouvé")
```

## 🚨 Dépannage

### Problème: Police non trouvée sur Railway

**Solution**: Vérifier que la police est bien dans le repository GitHub

```bash
# Vérifier localement
git ls-files | grep KFGQPC

# Devrait afficher:
# fonts/KFGQPC-Uthman-Taha.ttf
```

### Problème: Police par défaut utilisée

**Vérifier les logs Railway:**
- Aller dans Railway Dashboard
- Cliquer sur "Deployments"
- Voir les logs pour "⚠️ Police ... introuvable"

**Solutions:**
1. Vérifier l'orthographe exacte du nom de fichier
2. Vérifier que le fichier est bien commité dans Git
3. Redéployer sur Railway après avoir ajouté la police

### Problème: Texte mal affiché

**Solution**: La police KFGQPC-Uthman-Taha supporte parfaitement l'arabe coranique. Si le texte est mal affiché:
1. Vérifier que l'encodage du texte est UTF-8
2. Vérifier que `arabic-reshaper` et `python-bidi` sont installés
3. Tester avec un texte simple: "بسم الله"

## 📝 Workflow n8n Complet avec KFGQPC

```json
{
  "nodes": [
    {
      "name": "Generate Duaa",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://votre-app.railway.app/api/generate",
        "bodyParameters": {
          "parameters": [
            {
              "name": "duaa_text",
              "value": "بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ"
            },
            {
              "name": "output_name",
              "value": "bismillah"
            },
            {
              "name": "config",
              "value": {
                "font_name": "KFGQPC-Uthman-Taha.ttf",
                "font_size": 90,
                "format": "instagram_square",
                "background_color": "#1a472a",
                "text_color": "#FFFFFF",
                "add_footer": true,
                "footer_text": "@votre_compte"
              }
            }
          ]
        }
      }
    }
  ]
}
```

## ✅ Checklist

- [ ] Police `KFGQPC-Uthman-Taha.ttf` dans le dossier `fonts/`
- [ ] Police ajoutée au repository Git
- [ ] Police visible sur GitHub
- [ ] Déployé sur Railway
- [ ] Test en local réussi
- [ ] Test sur Railway réussi
- [ ] Workflow n8n configuré avec `"font_name": "KFGQPC-Uthman-Taha.ttf"`

## 💡 Conseil Pro

Si vous avez **plusieurs polices**, créez des templates:

```json
// Template 1: Police Uthman Taha (coranique)
{
  "font_name": "KFGQPC-Uthman-Taha.ttf",
  "font_size": 90
}

// Template 2: Police Amiri (élégante)
{
  "font_name": "Amiri-Regular.ttf",
  "font_size": 85
}

// Template 3: Police Cairo (moderne)
{
  "font_name": "Cairo-Regular.ttf",
  "font_size": 80
}
```

---

**La police KFGQPC-Uthman-Taha est parfaite pour le texte coranique car elle respecte les règles de typographie du Mushaf !** 🌙
