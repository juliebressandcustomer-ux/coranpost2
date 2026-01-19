# 📁 Dossier Fonts

## Police par défaut: KFGQPC-Uthman-Taha

Ce dossier doit contenir la police **KFGQPC-Uthman-Taha.ttf** pour générer les images de dou'a.

### Structure attendue:
```
fonts/
└── KFGQPC-Uthman-Taha.ttf    ← Votre police ici
```

## 📥 Installation

### Méthode 1: Copier votre police

```bash
cp /chemin/vers/KFGQPC-Uthman-Taha.ttf fonts/
```

### Méthode 2: Via Git LFS (pour fichiers > 50MB)

Si votre police est très lourde:

```bash
# Installer Git LFS
git lfs install

# Tracker les fichiers .ttf
git lfs track "*.ttf"

# Ajouter la police
cp KFGQPC-Uthman-Taha.ttf fonts/
git add fonts/KFGQPC-Uthman-Taha.ttf
git commit -m "Add KFGQPC font"
git push
```

## ✅ Vérification

Après avoir ajouté la police:

```bash
# Vérifier que le fichier existe
ls -lh fonts/KFGQPC-Uthman-Taha.ttf

# Vérifier qu'il est dans Git
git status
```

## 🚀 Déploiement sur Railway

Une fois la police dans ce dossier et poussée sur GitHub, Railway la déploiera automatiquement avec votre application.

## 🔧 Utilisation dans l'API

La police est configurée par défaut dans l'API:

```python
DEFAULT_CONFIG = {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 80,
    ...
}
```

Vous pouvez la spécifier explicitement dans vos requêtes n8n:

```json
{
  "config": {
    "font_name": "KFGQPC-Uthman-Taha.ttf",
    "font_size": 90
  }
}
```

## 📝 Polices Alternatives (Optionnel)

Vous pouvez ajouter d'autres polices dans ce dossier:

- **Amiri-Regular.ttf** - Style élégant
- **Scheherazade-Regular.ttf** - Très lisible
- **Cairo-Regular.ttf** - Moderne
- **Lateef-Regular.ttf** - Style Naskh

Pour les utiliser, spécifiez simplement le nom dans la config:

```json
{
  "config": {
    "font_name": "Amiri-Regular.ttf",
    "font_size": 85
  }
}
```

## ⚠️ Important

- **Ne commiter que les polices dont vous avez les droits d'utilisation**
- Les fichiers .ttf sont traités comme binaires par Git (voir .gitattributes)
- La taille maximale recommandée par fichier: 10MB

## 🔍 Dépannage

### Problème: Police non trouvée

```bash
# Vérifier le nom exact du fichier
ls -la fonts/

# Le nom doit correspondre EXACTEMENT (sensible à la casse)
```

### Problème: Erreur Git lors du push

Si le fichier est trop lourd (> 100MB), utilisez Git LFS:

```bash
git lfs install
git lfs track "*.ttf"
git add .gitattributes
git add fonts/KFGQPC-Uthman-Taha.ttf
git commit -m "Add font with LFS"
git push
```

---

**Pour plus d'informations, consultez FONT_GUIDE.md**
