import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1" # Force l'utilisation du CPU
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
import numpy as np
from PIL import Image
import pickle
import time
import serial
from ultralytics import YOLO
from keras_facenet import FaceNet

# Configuration du port série (pour SimulIDE ou un vrai Arduino)
# Sous Linux, avec socat, on utilisera souvent un port virtuel comme /tmp/ttyV0
PORT_SERIE = "/tmp/ttyV0"
BAUD_RATE = 9600
try:
    arduino = serial.Serial(PORT_SERIE, BAUD_RATE, timeout=1)
    print(f"Connecté à l'Arduino sur {PORT_SERIE}")
except Exception as e:
    print(f"Attention: Impossible d'ouvrir le port série {PORT_SERIE}. Mode sans Arduino activé.")
    arduino = None

dernier_envoi = 0

print("Chargement des modèles en cours (cela peut prendre quelques secondes)...")

# Chemins d'accès aux fichiers (ajustez si nécessaire)
DOSSIER_MODELES = r"/mnt/dtamboudisk/SYSTEME DE RECON-FACIAL/reco_facial-ai"
clf_path = os.path.join(DOSSIER_MODELES, "classificateur.pkl")
le_path = os.path.join(DOSSIER_MODELES, "label_encoder.pkl")
yolo_path = os.path.join(DOSSIER_MODELES, "yolov10n-face.pt")

# Vérification de la présence des modèles
for path in [clf_path, le_path, yolo_path]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier modèle introuvable : {path}")

# Chargement du SVM et du Label Encoder
with open(clf_path, "rb") as f:
    classificateur = pickle.load(f)

with open(le_path, "rb") as f:
    le = pickle.load(f)

# Chargement de YOLO et FaceNet
modele_yolo = YOLO(yolo_path)
facenet = FaceNet()
print("Modèles chargés avec succès !")

seuil_de_confiance = 0.7

def identification_visage(visage_traiter):
    """Extrait l'embedding FaceNet et prédit l'identité avec le SVM."""
    # Conversion BGR (OpenCV) vers RGB (FaceNet)
    visage_capturee = cv2.cvtColor(visage_traiter, cv2.COLOR_BGR2RGB)
    # Redimensionnement attendu par FaceNet
    visage_en_tableau = np.array(Image.fromarray(visage_capturee).resize((160, 160))).astype(np.float32)
    # Normalisation similaire à l'entraînement
    visage_en_tableau = (visage_en_tableau - 127.5) / 128.0
    
    # Extraction des embeddings
    embeddings = facenet.embeddings(np.expand_dims(visage_en_tableau, axis=0))
    
    # Prédiction
    prediction = classificateur.predict_proba(embeddings)[0]
    index = np.argmax(prediction)
    confiance = prediction[index]
    
    if confiance >= seuil_de_confiance:
        nom = le.classes_[index]
        return f"{nom} ({confiance*100:.1f}%)", (0, 255, 0), True # Vert, Autorisé
    else:
        return "Inconnu", (0, 0, 255), False # Rouge, Refusé

def run_inference():
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print("Erreur : Impossible d'ouvrir la webcam.")
        return

    print("\n--- Démarrage de la webcam ---")
    print("Appuyez sur la touche 'q' de votre clavier pour quitter.")

    frame_skip = 3  # On analyse 1 frame sur 3 pour soulager le CPU
    frame_count = 0
    
    # On stocke les dernières boîtes de détection pour fluidifier l'affichage
    dernieres_boites = []

    while True:
        retourne, image_capturee = capture.read()
        if not retourne:
            print("Erreur de capture vidéo.")
            break

        frame_count += 1
        
        # On ne lance YOLO et FaceNet que toutes les `frame_skip` images
        if frame_count % frame_skip == 0:
            dernieres_boites = []
            # On redimensionne l'image pour YOLO afin d'accélérer la détection
            # YOLO v10 gère le redimensionnement, on limite l'imgsz pour le CPU
            resultats = modele_yolo(image_capturee, verbose=False, imgsz=480)[0]

            visage_autorise_present = False
            visage_inconnu_present = False

            for boite in resultats.boxes:
                confiance_detecter = float(boite.conf[0])
                if confiance_detecter < 0.5:
                    continue
                
                # Récupération des coordonnées du visage
                x1, y1, x2, y2 = map(int, boite.xyxy[0])
                x1, y1 = max(0, x1), max(0, y1)

                extrait_visage = image_capturee[y1:y2, x1:x2]
                if extrait_visage.size == 0:
                    continue

                # Reconnaissance
                message, couleur, est_autorise = identification_visage(extrait_visage)
                dernieres_boites.append((x1, y1, x2, y2, message, couleur))

                if est_autorise:
                    visage_autorise_present = True
                else:
                    visage_inconnu_present = True

            # Envoi du signal à l'Arduino (Cooldown de 5s pour éviter le spam)
            global dernier_envoi
            temps_actuel = time.time()
            if temps_actuel - dernier_envoi > 5:
                commande = None
                if visage_autorise_present:
                    commande = b"OPEN\n"
                    log_msg = "Signal d'OUVERTURE envoyé (Autorisé)"
                elif visage_inconnu_present:
                    commande = b"DENY\n"
                    log_msg = "Signal de REFUS envoyé (Non autorisé)"
                
                if commande:
                    if arduino:
                        try:
                            arduino.write(commande)
                            print(f"[{time.strftime('%H:%M:%S')}] {log_msg}")
                        except Exception as e:
                            print("Erreur communication série:", e)
                    else:
                        print(f"[{time.strftime('%H:%M:%S')}] SIMULATION: {log_msg} (Port Série inactif)")
                    
                    dernier_envoi = temps_actuel

        # Dessin des boîtes sur TOUTES les images (même celles non analysées)
        for (x1, y1, x2, y2, message, couleur) in dernieres_boites:
            cv2.rectangle(image_capturee, (x1, y1), (x2, y2), couleur, 2)
            cv2.putText(image_capturee, message, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, couleur, 2)

        cv2.imshow("Reconnaissance Faciale (Appuyez sur Q pour quitter)", image_capturee)

        # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Arrêt de la capture.")
            break

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_inference()
