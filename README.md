# Système de Reconnaissance Faciale pour Biométrie Intelligente

Ce projet est un système de reconnaissance faciale conçu pour fonctionner **même sans carte graphique (CPU)**.
Il utilise :
- **YOLOv10n-face** pour la détection ultra-rapide des visages.
- **FaceNet** pour extraire les caractéristiques uniques d'un visage (embeddings).
- **SVM** (Support Vector Machine) pour classifier et identifier la personne.

## Prérequis

Assurez-vous que votre environnement virtuel Python est activé.
Si vous utilisez l'environnement mentionné précédemment :
```bash
source ~/recon-facial-py311/venv/bin/activate
```

Les dépendances principales du projet sont :
- `opencv-python`
- `numpy`
- `Pillow`
- `scikit-learn`
- `ultralytics`
- `keras-facenet`
- `tensorflow` (version CPU)

## Utilisation

Nous avons créé un script Python dédié et optimisé pour la capture vidéo. Il remplace le code contenu à la fin du Notebook qui comportait des erreurs et surchargait le processeur.

### Lancer la Reconnaissance Faciale en temps réel

Pour lancer la webcam et identifier les visages, exécutez simplement :

```bash
python inference.py
```

**Optimisations CPU incluses dans ce script :**
1. **Frame Skipping** : Le modèle lourd ne s'exécute qu'une image sur 3. Les images intermédiaires reprennent la dernière détection connue, ce qui rend la vidéo beaucoup plus fluide.
2. **Désactivation forcée du GPU** : `CUDA_VISIBLE_DEVICES="-1"` est utilisé pour supprimer les erreurs liées à l'absence de GPU.
3. **Redimensionnement dynamique** : L'image passée à YOLO est redimensionnée à 480 pixels pour accélérer grandement la détection.

### Quitter l'application
Appuyez sur la touche **`q`** de votre clavier lorsque la fenêtre de la webcam est active pour arrêter le programme proprement.

---
## Simulation de l'Ouverture de Porte (avec SimulIDE)

Si vous souhaitez voir la porte s'ouvrir virtuellement avant d'acheter le matériel (Arduino, Relais, Serrure), voici la marche à suivre :

1. **Installer pyserial et socat** :
   ```bash
   pip install pyserial
   sudo apt install socat
   ```

2. **Créer les Ports Série Virtuels** :
   Dans un nouveau terminal, tapez cette commande et laissez-la tourner (elle crée un câble virtuel entre Python et SimulIDE) :
   ```bash
   socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
   ```

3. **Lancer SimulIDE** :
   - Ajoutez un **Arduino UNO**.
   - Ajoutez un composant **Serial Port** (dans *Logic* ou *Communications*) et configurez son port sur `/tmp/ttyV1` à `9600` bauds.
   - Reliez les broches suivantes :
     - **Broche 7** : Un Relais (ou une LED simulant l'ouverture de porte).
     - **Broche 6** : Une **LED Verte** (Personne Autorisée).
     - **Broche 5** : Une **LED Rouge** (Personne Inconnue).
     - **Broche 4** : Un **Sounder / Buzzer** (Signal sonore).
   - Chargez le code fourni dans le dossier `code_arduino_porte/code_arduino_porte.ino` sur l'Arduino virtuel et lancez la simulation.

4. **Lancer la Caméra** :
   Retournez dans votre terminal principal et lancez `python inference.py`. 
   Quand la caméra vous reconnaîtra, le script Python enverra le signal `"OPEN"` dans `/tmp/ttyV0`. Il traversera le câble virtuel `socat`, sera reçu par SimulIDE sur `/tmp/ttyV1`, et l'Arduino virtuel allumera la LED !

---
*Note : Si vous souhaitez ré-entraîner le modèle sur de nouvelles données, vous pouvez utiliser le code du notebook `reconnaissance faciale.ipynb` (première moitié du fichier).*
