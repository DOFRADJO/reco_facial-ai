# Système de Reconnaissance Faciale pour Biométrie Intelligente

Ce projet est un système de reconnaissance faciale conçu pour fonctionner **même sans carte graphique (CPU)**.

Il utilise :

* **YOLOv10n-face** pour la détection ultra-rapide des visages.
* **FaceNet** pour extraire les caractéristiques uniques d'un visage (embeddings).
* **SVM (Support Vector Machine)** pour classifier et identifier la personne.

## Prérequis

Assurez-vous que votre environnement virtuel Python est activé.

```bash
source ~/recon-facial-py311/venv/bin/activate
```

Les dépendances principales du projet sont :

* opencv-python
* numpy
* Pillow
* scikit-learn
* ultralytics
* keras-facenet
* tensorflow (version CPU)

## Utilisation

Nous avons créé un script Python dédié et optimisé pour la capture vidéo. Il remplace le code contenu à la fin du Notebook qui comportait des erreurs et surchargait le processeur.

### Lancer la Reconnaissance Faciale en Temps Réel

```bash
python inference.py
```

### Optimisations CPU incluses

1. **Frame Skipping** : le modèle lourd ne s'exécute qu'une image sur 3.
2. **Désactivation forcée du GPU** : `CUDA_VISIBLE_DEVICES="-1"`.
3. **Redimensionnement dynamique** : l'image est réduite à 480 px avant détection.

### Quitter l'application

Appuyez sur la touche **q** lorsque la fenêtre de la webcam est active.

---

# Simulation de l'Ouverture de Porte avec SimulIDE

Cette simulation permet de tester l'ouverture d'une porte virtuelle avant l'achat du matériel réel (Arduino, Relais, Serrure électrique, etc.).

## Installation des dépendances

```bash
pip install pyserial
sudo apt update
sudo apt install socat
```

## Installation de SimulIDE (Flatpak)

Installer Flatpak :

```bash
sudo apt install flatpak
```

Ajouter le dépôt Flathub :

```bash
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
```

Installer SimulIDE :

```bash
flatpak install flathub com.simulide.simulide -y
```

Lancer SimulIDE :

```bash
flatpak run com.simulide.simulide
```

## Autoriser l'accès aux ports série sous Flatpak

Si SimulIDE est installé via Flatpak, il faut lui donner accès aux périphériques du système :

```bash
flatpak override --user --filesystem=host com.simulide.simulide
flatpak override --user --device=all com.simulide.simulide
```

Redémarrer ensuite SimulIDE.

---

## Création des Ports Série Virtuels

Dans un nouveau terminal, exécuter :

```bash
socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
```

Exemple de sortie :

```text
2026/06/05 23:37:13 socat[2461569] N PTY is /dev/pts/7
2026/06/05 23:37:13 socat[2461569] N PTY is /dev/pts/8
2026/06/05 23:37:13 socat[2461569] N starting data transfer loop with FDs [5,5] and [7,7]
```

Conserver cette fenêtre ouverte pendant toute la simulation.

Les liens créés seront :

```text
/tmp/ttyV0 -> /dev/pts/7
/tmp/ttyV1 -> /dev/pts/8
```

Vérification :

```bash
ls -l /tmp/ttyV*
```

Exemple :

```text
lrwxrwxrwx 1 td2f td2f 10 Jun  5 23:37 /tmp/ttyV0 -> /dev/pts/7
lrwxrwxrwx 1 td2f td2f 10 Jun  5 23:37 /tmp/ttyV1 -> /dev/pts/8
```

---

## Vérification de la communication série

Terminal 1 :

```bash
socat -d -d pty,raw,echo=0,link=/tmp/ttyV0 pty,raw,echo=0,link=/tmp/ttyV1
```

Terminal 2 :

```bash
cat /dev/pts/7
```

Terminal 3 :

```bash
echo TEST > /dev/pts/8
```

Si tout fonctionne correctement :

```text
TEST
```

doit apparaître dans le Terminal 2.

---

## Configuration de SimulIDE

### Ajouter les composants

* Arduino UNO
* Serial Port
* LED Verte
* LED Rouge
* Buzzer (Sounder)
* Relais ou LED représentant la porte

### Connexions Arduino

| Broche Arduino | Fonction                 |
| -------------- | ------------------------ |
| D7             | Relais / Ouverture Porte |
| D6             | LED Verte                |
| D5             | LED Rouge                |
| D4             | Buzzer                   |

### Configuration du Serial Port

Baudrate :

```text
9600
```

Si vous utilisez SimulIDE natif :

```text
/tmp/ttyV1
```

Si vous utilisez SimulIDE Flatpak :

```text
/dev/pts/8
```

Puis cliquer sur **Open**.

---

## Chargement du Programme Arduino

Ouvrir :

```text
code_arduino_porte/code_arduino_porte.ino
```

Compiler puis lancer la simulation.

---

## Lancer le Système de Reconnaissance Faciale

Dans un nouveau terminal :

```bash
python inference.py
```

Le script Python envoie automatiquement :

```text
OPEN
```

sur :

```text
/tmp/ttyV0
```

qui correspond à :

```text
/dev/pts/7
```

Le message traverse le lien créé par `socat` et arrive dans SimulIDE sur :

```text
/dev/pts/8
```

Lorsque l'utilisateur est reconnu :

* La LED Verte s'allume.
* Le relais s'active.
* Le buzzer peut émettre un signal.
* La porte virtuelle s'ouvre.

---

## Dépannage

### Vérifier les ports série disponibles

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

### Vérifier les pseudo-terminaux créés par socat

```bash
ls -l /tmp/ttyV*
```

### Vérifier les pseudo-terminaux visibles dans Flatpak

```bash
flatpak run --command=sh com.simulide.simulide
```

Puis :

```bash
ls -l /dev/pts
```

### Vérifier les permissions Flatpak

```bash
flatpak override --user --filesystem=host com.simulide.simulide
flatpak override --user --device=all com.simulide.simulide
```

---

## Réentraînement du Modèle

Si vous souhaitez ajouter de nouveaux utilisateurs ou améliorer la précision du modèle :

Utilisez le notebook :

```text
reconnaissance faciale.ipynb
```

La première partie du notebook permet :

* la collecte des images,
* l'extraction des embeddings FaceNet,
* l'entraînement du classificateur SVM,
* la sauvegarde des nouveaux modèles.
