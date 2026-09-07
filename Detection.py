import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import *
from tkinter import Text
from PIL import ImageTk, Image

def convertir_en_nuance_de_gris(image_bgr):
    # Assurer que l'image est en float pour une précision lors de la multiplication
    bgr_float = image_bgr.astype(float)

    # Extraire les canaux B, G, R
    B = bgr_float[:, :, 0]
    G = bgr_float[:, :, 1]
    R = bgr_float[:, :, 2]

    # Appliquer la formule de conversion en niveaux de gris
    Gris = 0.299 * R + 0.587 * G + 0.114 * B

    # Convertir à uint8
    image_grise = Gris.astype(np.uint8)

    return image_grise

def calculer_difference_absolue(image1, image2):
    # Convertir les deux images en int16 pour éviter les problèmes de sous-débit lors de la soustraction
    image1_int = image1.astype(np.int16)
    image2_int = image2.astype(np.int16)
    
    # Soustraire les images et prendre la valeur absolue
    diff = np.abs(image1_int - image2_int)
    
    # Convertir à uint8
    diff = diff.astype(np.uint8)
    
    return diff

def appliquer_seuil_binaire(image, valeur_seuil, valeur_maximale):
    # Créer un nouveau tableau en fonction de la condition
    seuille = np.zeros_like(image)
    seuille[image > valeur_seuil] = valeur_maximale

    return seuille

def trouver_contours(seuil):
    # Trouver les contours en utilisant la fonction OpenCV intégrée
    contours, _ = cv2.findContours(seuil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filtrer les petits contours
    contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 100]

    return contours

def detecter_et_dessiner_mouvement(cadre, seuil):
    # Convertir le cadre en niveaux de gris
    gris = cv2.cvtColor(cadre, cv2.COLOR_BGR2GRAY)
    
    # Calculer la différence absolue entre les images actuelle et précédente
    diff = cv2.absdiff(prvs_gray, gris)
    
    # Appliquer un seuil binaire pour obtenir les zones de mouvement
    _, seuil = cv2.threshold(diff, seuil, 255, cv2.THRESH_BINARY)
    
    # Trouver les contours dans l'image binaire
    contours, _ = cv2.findContours(seuil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dessiner des rectangles autour des zones de mouvement détectées
    for contour in contours:
        if cv2.contourArea(contour) > 100: # Ignorer les petits contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(cadre, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Afficher le cadre avec les zones de mouvement détectées
    cv2.imshow('Détection de mouvement', cadre)

def selectionner_video():
    global prvs_gray, out  
    chemin_fichier = filedialog.askopenfilename(filetypes=[("Fichiers vidéo", "*.mp4")])
    if chemin_fichier:
        chemin.delete(1.0, END)
        chemin.insert(1.0, chemin_fichier)
        cap = cv2.VideoCapture(chemin_fichier)
        if not cap.isOpened():
            print("Erreur : Impossible d'ouvrir la vidéo.")
            return
        ret, cadre1 = cap.read()
        if not ret:
            print("Erreur : Impossible de lire la première image de la vidéo.")
            return
        
        hauteur, largeur, _ = cadre1.shape
        prvs_gray = cv2.cvtColor(cadre1, cv2.COLOR_BGR2GRAY)
        
        # Initialiser le rédacteur vidéo
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output_video.mp4', fourcc, 20.0, (largeur, hauteur))
        
        while True:
            ret, cadre2 = cap.read()
            if not ret:
                break
            prochain_gris = convertir_en_nuance_de_gris(cadre2)
            diff = calculer_difference_absolue(prvs_gray, prochain_gris)
            seuil_binaire = appliquer_seuil_binaire(diff, seuil, 255)
            contours = trouver_contours(seuil_binaire)
            detecter_et_dessiner_mouvement(cadre2, seuil)
            out.write(cadre2)  # Enregistrer l'image traitée
            prvs_gray = prochain_gris
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        cap.release()
        out.release()
        cv2.destroyAllWindows()

def enregistrer_video():
    global out
    if out:
        out.release()
        print("Video saved as 'output_video.mp4'")
        
def update_seuil(value):
    global seuil
    seuil = int(value)

# Création de la fenêtre principale de l'interface graphique
racine = tk.Tk()
racine.title("Détection de mouvement")
racine.geometry("560x400")
racine.config(bg='#dcdcdc')

# Éléments d'interface utilisateur
# Titre de l'application
Label(racine, text="Détection de Mouvement", bg='#dcdcdc', font=("Times", "14", "bold")).place(relx=0.5, rely=0.35, anchor=CENTER)
Label(racine, text="Réalisé par:\nMohammed ABO ORAIG", bg='#dcdcdc', fg="black", font=("Times", 10)).place(relx=0.65, rely=0.8, anchor=CENTER)
# Année du projet
Label(racine, text="2023-2024", bg='#dcdcdc', fg="black", font=("Times", 8)).pack(side=BOTTOM)


# Champ de texte pour afficher le chemin de la vidéo sélectionnée
chemin = Text(racine, height=1, width=40, bg='#dcdcdc', font=("Times", 10))
chemin.place(relx=0.65, rely=0.48, anchor=CENTER)

# Bouton pour sélectionner la vidéo
button = tk.Button(racine, width=18, text="Sélectionner la Vidéo", command=selectionner_video)
button.place(relx=0.30, rely=0.48, anchor=CENTER)

# Bouton pour enregistrer la vidéo
save_button = tk.Button(racine, width=18, text="Enregistrer la vidéo", command=enregistrer_video)
save_button.place(relx=0.30, rely=0.6, anchor=CENTER)

# Échelle pour ajuster le seuil de détection de mouvement
seuil = 20
seuil_scale = Scale(racine, from_=1, to=100, orient=HORIZONTAL, length=240, label="Seuil de détection de mouvement :", bg='#dcdcdc', font=("Times", 10), command=update_seuil)
seuil_scale.set(seuil)
seuil_scale.place(relx=0.65, rely=0.6, anchor=CENTER)

# Lancement de la boucle principale de l'interface graphique
racine.mainloop()
