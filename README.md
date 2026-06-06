# Guide d'Installation, de Compilation et de Simulation

## Projet : Système de Reconnaissance Faciale pour Biométrie Intelligente

Auteur : Tambou Donald


# 1. Objectif du Projet

L'objectif de ce projet est de développer un système de contrôle d'accès biométrique capable :

* d'identifier un utilisateur par reconnaissance faciale ;
* d'autoriser ou de refuser l'accès ;
* de communiquer avec un microcontrôleur Arduino ;
* de simuler l'ouverture d'une porte avant l'acquisition du matériel réel.

Le système est composé de deux parties :

1. Un module logiciel de reconnaissance faciale développé en Python.
2. Un module embarqué simulé sous SimulIDE représentant le système de contrôle de porte.


# 2. Architecture Générale

Le système repose sur les technologies suivantes :

## Partie Intelligence Artificielle

* YOLOv10n-face pour la détection des visages.
* FaceNet pour l'extraction des caractéristiques biométriques.
* SVM (Support Vector Machine) pour la classification des individus.

## Partie Embarquée

* Arduino Uno.
* Liaison série virtuelle.
* SimulIDE pour la simulation électronique.


# 3. Préparation de l'Environnement Python

## Création de l'environnement virtuel

```bash
python3 -m venv venv
```

Activation chez moi c'est (source ~/recon-facial-py311/venv/bin/activate):

```bash
source venv/bin/activate
```


## Installation des dépendances

```bash
pip install \
opencv-python \
numpy \
Pillow \
scikit-learn \
ultralytics \
keras-facenet \
tensorflow
```


# 4. Structure du Projet

```text
reco_facial-ai/
│
├── dataset/
├── embeddings_entrainement.npy
├── embeddings_test.npy
├── classificateur.pkl
├── label_encoder.pkl
├── inference.py
├── yolov10n-face.pt
├── Arduino/
│   └── first/
│       ├── first.ino
│       └── build/
│
├── code_arduino_porte/
│   └── code_arduino_porte.ino
│
├── first.simu
├── first_circuit.sim1
└── README.md
```


# 5. Installation de SimulIDE

## Méthode retenue

Une installation manuelle a été utilisée afin de disposer d'une version récente et compatible avec Linux.

Téléchargement :

```bash
wget https://simulide.com/p/downloads.html
```

Extraction :

```bash
tar -xvf SimulIDE_0.3.10-SR2-Lin64.tar.gz
```

Renommage :

```bash
mv SimulIDE_0.3.10-SR2-Lin64 simulide
```


# 6. Installation des Dépendances SimulIDE

Lors du premier lancement, SimulIDE signalait l'absence de bibliothèques Qt.

Exemple :

```text
libQt5SerialPort.so.5
```

Installation :

```bash
sudo apt update

sudo apt install \
libqt5serialport5 \
libqt5multimedia5 \
libqt5multimediawidgets5
```


# 7. Création des Ports Série Virtuels

Afin de simuler la communication entre Python et Arduino, des ports série virtuels ont été créés.

Installation :

```bash
sudo apt install socat
```

Création du pont série :

```bash
socat -d -d \
pty,raw,echo=0,link=/tmp/ttyV0 \
pty,raw,echo=0,link=/tmp/ttyV1
```

Résultat :

```text
/tmp/ttyV0
/tmp/ttyV1
```

Ces deux ports sont reliés entre eux.


# 8. Vérification du Fonctionnement de Socat

Terminal 1 :

```bash
socat -d -d \
pty,raw,echo=0,link=/tmp/ttyV0 \
pty,raw,echo=0,link=/tmp/ttyV1
```

Terminal 2 :

```bash
cat /tmp/ttyV0
```

Terminal 3 :

```bash
echo TEST > /tmp/ttyV1
```

Résultat attendu :

```text
TEST
```


# 9. Installation d'Arduino CLI

L'installation du paquet Arduino Debian a montré certaines incompatibilités avec la chaîne de compilation AVR.

La solution retenue a été Arduino CLI.

Installation :

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
```

Déplacement du binaire :

```bash
sudo mv bin/arduino-cli /usr/local/bin/
```

Vérification :

```bash
arduino-cli version
```


# 10. Installation du Core Arduino

Initialisation :

```bash
arduino-cli config init
```

Mise à jour de l'index :

```bash
arduino-cli core update-index
```

Installation du support Arduino Uno :

```bash
arduino-cli core install arduino:avr
```

Vérification :

```bash
arduino-cli core list
```


# 11. Difficultés Rencontrées

## Première Difficulté

L'installation du paquet :

```bash
sudo apt install arduino
```

a provoqué plusieurs erreurs de compilation.

Exemple :

```text
DECIMAL_DIG was not declared in this scope
```

Ces erreurs provenaient d'incompatibilités entre :

* Arduino IDE Debian ;
* AVR-GCC ;
* Arduino Core AVR.

Solution :

Utilisation d'Arduino CLI.


## Deuxième Difficulté

Arduino CLI impose une structure stricte :

```text
NomDuDossier/
└── NomDuDossier.ino
```

Une erreur apparaissait lorsque :

```text
reco_facial-ai/
└── first.ino
```

était utilisé.

Solution :

```text
Arduino/
└── first/
    └── first.ino
```


## Troisième Difficulté

La présence simultanée de :

```text
first.ino
test.ino
```

dans le même dossier provoquait :

```text
redefinition of setup()
redefinition of loop()
```

car Arduino fusionne tous les fichiers .ino d'un même répertoire.

Solution :

Un seul sketch principal par dossier.


# 12. Compilation du Firmware Arduino

Se placer dans le dossier :

```bash
cd Arduino/first
```

Compilation :

```bash
arduino-cli compile \
--fqbn arduino:avr:uno \
--output-dir build \
.
```

Résultat :

```text
Sketch uses 998 bytes (3%)
Global variables use 9 bytes (0%)
```

Fichiers générés :

```text
build/
├── first.ino.hex
├── first.ino.with_bootloader.hex
└── first.ino.elf
```

Le fichier utilisé dans SimulIDE est :

```text
build/first.ino.hex
```


# 13. Configuration de SimulIDE

Composants utilisés :

* Arduino Uno
* Serial Port
* LED Verte
* LED Rouge
* Buzzer
* Relais

Connexions :

| Broche | Fonction  |
| ------ | --------- |
| D7     | Relais    |
| D6     | LED Verte |
| D5     | LED Rouge |
| D4     | Buzzer    |

Configuration du port série :

```text
9600 bauds
```

Port :

```text
/tmp/ttyV1
```

---

# 14. Exécution de la Simulation

Lancement de Socat :

```bash
socat -d -d \
pty,raw,echo=0,link=/tmp/ttyV0 \
pty,raw,echo=0,link=/tmp/ttyV1
```

Lancement de SimulIDE :

```bash
./simulide
```

Chargement du firmware :

```text
build/first.ino.hex
```


# 15. Exécution du Système Biométrique

Activation de l'environnement :

```bash
source venv/bin/activate
```

Lancement :

```bash
python inference.py
```

Lorsqu'un utilisateur est reconnu :

```text
OPEN
```

est envoyé sur :

```text
/tmp/ttyV0
```

Le message traverse le lien série créé par Socat et est reçu sur :

```text
/tmp/ttyV1
```

par l'Arduino simulé.


# 16. Résultat Final

Lorsque le visage est reconnu :

* la LED verte s'allume ;
* le relais s'active ;
* le buzzer émet un signal ;
* la porte virtuelle s'ouvre.

Lorsque le visage n'est pas reconnu :

* la LED rouge s'allume ;
* l'accès est refusé ;
* aucun ordre d'ouverture n'est transmis.

Le système valide ainsi le fonctionnement complet de la chaîne :

Reconnaissance Faciale → Classification → Communication Série → Arduino → Contrôle d'Accès.
