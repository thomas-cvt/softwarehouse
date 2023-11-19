# coding=utf-8

# Imports

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
from Settings import Params
from Objets import Reference, Commande, Box, Case
from Fonctions import *
from random import randint
import math
import csv

class Fenetre_Entrepot():
    """
    Cette fenêtre est un affichage graphique de l'entrepôt concerné. 
    Composée principalement d'un canevas, le schéma des allées et box est créé. 
    Cette fenêtre peut être ouverte pour de multiples raisons appelées "modes d'ouverture" :
    - Mode de sélection : Permet de sélectionner un box en cliquant dessus pour définir l'emplacement d'une référence
    - Mode de création : Permet de créer ou modifier la configuration de l'entrepôt, place les boxs, départ et arrivée des préparateurs
    - Mode de commande : Permet de suivre le chemin à suivre pour préparer une commande. Affichage d'un bandeau de parcours des étapes
    - Mode de visualisation : Permet de visualiser l'entrepôt sans pouvoir interagir avec
    """

    # Fonctions d'initialisation de la fenêtre, des widgets et du canvevas en fonction du mode d'ouverture

    def __init__(self, class_parent, select=False, ref=None, commande=None, user = None, create=False, min_box=0):
        """
        Initialise la fenêtre et la paramètre correctement
        Création des variables nécessaires
        class_parent = Fenêtre ayant déclenché l'ouverture de la fenêtre
        Si select = True, mode de sélection par clic
        Si init = True, la fenêtre est initialisée sans ouverture de fenêtre
        Si commande != None, la fenêtre est ouverte pour observer le chemin à suivre
        Si create = True, la fenêtre est ouverte pour créer la configuration de l'entrepôt
        min_box indique le nombre minimum de box à créer
        """
        
        # Variables 

        self.select = select
        self.ref = ref
        self.lettres = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.rectangles = {}
        self.chemins = []
        self.elements_chemin = []
        self.create = create
        self.user = user

        # Initialisation de la fenêtre

        self.class_parent = class_parent
        if class_parent == None:
            self.racine = tk.Tk()
        else:
            self.racine = tk.Toplevel(class_parent.racine)
        self.racine.title("Softwarehouse - Entrepôt")
        self.racine.resizable(False, False)

        # Variables relatives à la commande

        self.commande = commande
        self.step = 0
        self.ordre = []
        self.distance = 0

        # Intervalle de temps et id du timer

        self.dt = 3
        self.timer_id = None
        
        # Etat du timer
        
        self.running = False 

        # Id image dans canevas

        self.id_truck = None
        self.truck = tk.PhotoImage(file="assets/truck.png", master=self.racine)
        self.index_case = 0

        self.create_widgets(self.racine) # Création des widgets
        
        if create == True: # Si on initialise ou modifie la configuration de l'entrepot
            self.min_box = min_box
            self.old_box = Box.boxs.copy()
            self.selected = []
            self.choix_depart = None
            self.choix_arrivee = None
            self.etat = 0
            self.racine.bind("<Return>", self.modif_entrepot)
            self.config_entrepot()
            if self.min_box == 1:
                self.min_box = 2
            messagebox.showinfo("Configuration", f"Vous devez placer les boxs de l'entrepôt\nVous devez placer au minimum {self.min_box} boxs", parent=self.racine)
        else: # Si on affiche l'entrepot
            self.config_with_box_objets()
            self.init_cases() # On initialise les cases
            self.get_case_dep_arr() # On récupère les cases de départ et d'arrivée

            # Si on ouvre la fenêtre pour modifier l'emplacement d'une référence
            # On met le box courant de la référence en surbrillance

            if self.ref != None:
                box_ref = self.ref.get_box()
                for id, box in list(self.rectangles.items()):
                    if box == box_ref:
                        self.canevas.itemconfig(id, fill="light blue")
                        break
            rayon = 5
            if self.depart == self.arrivee: # Si le départ et l'arrivée sont au même endroit, on supperpose les points avec un plus grand que l'autre
                rayon = 10
            self.canevas.create_oval(self.depart.x-rayon,self.depart.y-rayon,self.depart.x+rayon,self.depart.y+rayon, fill="green2") # On affiche le point de départ
            rayon = 5
            self.canevas.create_oval(self.arrivee.x-rayon,self.arrivee.y-rayon,self.arrivee.x+rayon,self.arrivee.y+rayon, fill="red4") # On affiche le point d'arrivée

            Box.save() # On sauvegarde les box

            if self.commande != None: # Si la fenêtre est ouverte pour observer le chemin à suivre
                self.init_tous_les_chemins() # On initialise tous les chemins
                self.create_bandeau(self.racine) # On crée le bandeau de parcours des étapes
                self.update_buttons()
                self.show_step()
        
    def create_widgets(self, root):
        """
        Création des widgets de la fenêtre
        Entrées : root (tk.Tk) : la fenêtre racine
        """

        # Bouton Quitter

        self.Bquit = tk.Button(root, text="Quitter", font=("Calibri", 12))
        self.Bquit.pack(side=tk.BOTTOM, fill="x")
        self.Bquit.bind("<Button-1>", self.quitter)

        if self.create == True:
            self.Bsave = tk.Button(root, text="Sauvegarder", font=("Calibri", 12))
            self.Bsave.pack(side=tk.BOTTOM, fill="x", pady=5)
            self.Bsave.bind("<Button-1>", self.modif_entrepot)

        # Création d'un canevas

        self.canevas = tk.Canvas(root, bg=Params.color_background, width=Params.largeur_canevas, height=Params.hauteur_canevas)
        self.canevas.pack()  

    def create_bandeau(self, root):
        """
        Création du bandeau de navigation entre les étapes du chemin
        Entrées : root (tk.Tk) : la fenêtre racine
        """

        color = "light blue"

        # Cadre du bandeau

        self.frame = tk.Frame(root, background= color)
        self.frame.pack(side=tk.TOP, fill="x")

        # Label titre

        tk.Label(self.frame, text=f"Commande {self.commande.id}", font="Helvetica 11 bold", anchor=tk.CENTER, background=color).pack(side=tk.TOP, fill="x", anchor=tk.CENTER)

        # Boutons de navigation

        self.b_back = tk.Button(self.frame, text="< Étape précédente",background=color, height=2, font="Helvetica 9 bold")
        self.b_back.bind("<Button-1>", self.back)
        self.b_back.pack(side=tk.LEFT, pady=5, padx=10)

        self.b_next = tk.Button(self.frame, text="Étape suivante >",font="Helvetica 9 bold", background= color, height=2)
        self.b_next.bind("<Button-1>", self.next)
        self.b_next.pack(side=tk.RIGHT, pady=5, padx=10)

        # Label étape

        self.l_step = tk.Label(self.frame, text="AAAAA", anchor=tk.CENTER, font="Helvetica 15", background=color)
        self.l_step.pack(fill="x", anchor=tk.CENTER, expand=True)
    
    def quitter(self, event):
        """
        Ferme la fenêtre
        """
        if self.create == True:
            Box.boxs = self.old_box
        if self.racine != None:
            self.stop()
            self.racine.destroy()

    # Fonctions relatives à l'affichage de l'entrepôt et des boxs sur le canevas

    def config_with_box_objets(self):
        """
        Initialise les boxs à partir des objets Box
        """
        for box in list(Box.boxs.values()):
            self.ajouter_box(box)

    def place_box(self, index, x, y, allee, num):
        """
        Place une box à l'index donné avec les coordonnées données
        Si le box existe déjà, on le modifie
        Si le box n'existe pas, on le crée
        Entrées : index (int) : l'index du box
                    x (int) : la coordonnée x du box
                    y (int) : la coordonnée y du box
                    allee (str) : l'allee du box
                    num (int) : le numéro du box
        """
        box = Box.boxs.get(Params.prefix_box+str(index), None) 
        if box == None:
            box = Box(Params.prefix_box+str(index), allee, num, x, y)
        else:
            box.allee = allee
            box.num = num
            box.x = x
            box.y = y
        if self.init == False:
            self.ajouter_box(box)

    def ajouter_box(self, box):
            """
            Ajoute une box au canevas
            Ajoute le texte de l'allee et du numéro ainsi que la référence si le box en contient une
            Entrée : box (Box)
            """
            # Ajout du rectangle

            id = self.canevas.create_rectangle(box.x-Params.cote/2, box.y-Params.cote/2, box.x+Params.cote/2, box.y+Params.cote/2, fill=Params.color_box)
            co = (box.x, box.y+0.35*Params.cote)
            id_allee = self.canevas.create_text(co[0], co[1], text=str(box.allee)+ str(box.num), font='Helvetica 10 bold')
            self.rectangles[id] = box
            self.rectangles[id_allee] = box
            id_ref = None

            # Ajout de la référence si le box en contient une

            if box.stockes != None:
                mid = (box.x, box.y-0.15*Params.cote)
                if self.commande == None:
                    color = ""
                    if Params.alert_stock_3 >= 0 and box.stockes.stock <= Params.alert_stock_3:
                        color = Params.color_alert_stock_3
                    elif Params.alert_stock_2 >= 0 and box.stockes.stock <= Params.alert_stock_2:
                        color = Params.color_alert_stock_2
                    elif Params.alert_stock_1 >= 0 and box.stockes.stock <= Params.alert_stock_1:
                        color = Params.color_alert_stock_1
                    else:
                        color=Params.color_no_alert
                    id_ref = self.canevas.create_text(mid[0], mid[1], text=f"{box.stockes.id} ({box.stockes.stock})", font='Helvetica 10', fill=color)
                    self.rectangles[id_ref] = box
                else:
                    if box.stockes in list(self.commande.contenu.keys()):
                        id_ref = self.canevas.create_text(mid[0], mid[1], text=f"{box.stockes.id} ({self.commande.contenu[box.stockes]})", font='Helvetica 10 bold', fill="dark green")
                        self.rectangles[id_ref] = box       

            # On ajoute les évènements pour les clics

            self.canevas.tag_bind(id, "<Button-1>", self.clic_box)
            self.canevas.tag_bind(id_allee, "<Button-1>", self.clic_box)
            if id_ref != None:
                self.canevas.tag_bind(id_ref, "<Button-1>", self.clic_box)

    def init_cases(self):
        """
        Initialise toutes les cases du canevas
        Une case est créée si aucun box n'est dessus
        """

        Case.cases = {}
        for i in range(Params.nb_colonnes):
            for j in range(Params.nb_lignes):
                x = Params.cote/2+i*Params.cote
                y = Params.cote/2+j*Params.cote
                co_boxs = Box.dico_co()
                if (co_boxs.get((x, y), None) == None):
                    obj = Case(x, y)
                    obj.trouver_voisins()
                    obj.trouver_boxs()
                    # Pour afficher les cases, les voisins et les boxs
                    """
                    self.canevas.create_oval(x-5,y-5,x+5,y+5, fill="blue")
                    for sommet in obj.ad:
                        self.canevas.create_line(obj.x, obj.y, sommet.x, sommet.y, fill="red", arrow="both")
                    for box in obj.boxs:
                        self.canevas.create_line(obj.x, obj.y, box.x, box.y, fill="green", arrow="both")
                    """

    # Fonctions relatives au calcul de chemin pour l'affichage d'une commande
    
    def init_tous_les_chemins(self):
        """
        Deux fonctions :
        Création de la liste self.ordre qui contient les références à aller chercher dans l'ordre et le chemin pour y aller
        La première valeur est la case de départ et la dernière est la case d'arrivée
        Les valeurs intermédiaires sont des tuples (référence, chemin)

        Calcul de la distance totale du chemin pour faire toutes les étapes
        """

        refs = list(self.commande.contenu.keys())  # Liste des références à aller chercher
        dic_distances = self.dico_distances(refs) # Dictionnaire des distances entre les références
        ordre = []
        a_faire = list(self.commande.contenu.keys()) # Liste des références restantes à aller chercher

        for i in range(len(refs)+1): 
            if i == 0: # Si on est à la première étape
                ordre.append(self.depart) # On ajoute la case de départ à la liste des étapes
                dmin = math.inf
                ref_proche = None
                for j in a_faire: # On cherche la référence la plus proche de la case de départ
                    d = self.calcul_distance(self.chemin_case_to_ref(self.depart, j))

                    if Params.path_mode == "lightest": 
                        d = d*j.weight*self.commande.contenu[j]
                    elif Params.path_mode == "fastest":
                        d = d*Params.vitesse

                    if d < dmin:
                        dmin = d
                        ref_proche = j
                ordre.append((ref_proche, self.chemin_case_to_ref(ordre[0], ref_proche))) # On ajoute la référence la plus proche
                a_faire.remove(ref_proche) # On la retire de la liste des références restantes à aller chercher

            elif i == len(refs): # Si on est à la dernière étape
                ordre.append(self.arrivee) # On ajoute la case d'arrivée à la liste des étapes

            else: # Si on est dans le cas général
                dmin = math.inf
                ref_proche = None
                for j in a_faire: # On cherche la référence la plus proche de la dernière référence visitée
                    if (ordre[-1][0], j) in list(dic_distances.keys()):
                        key = (ordre[-1][0], j)
                    else:
                        key = (j, ordre[-1][0])

                    if Params.path_mode == "lightest": # Si on veut le chemin le plus léger, on prend en compte le poids de la référence
                        d = dic_distances[key]*j.weight*self.commande.contenu[j]
                    elif Params.path_mode == "fastest": # Si on veut le chemin le plus rapide, on prend en compte la vitesse de déplacement
                        d = dic_distances[key]*Params.vitesse
                    else: # Si on veut le chemin le plus court, on prend en compte la distance
                        d = dic_distances[key]

                    if d < dmin:
                        dmin = d
                        ref_proche = j

                ordre.append((ref_proche, self.chemin_case_to_ref(ordre[-1][1][-1], ref_proche))) # On ajoute la référence la plus proche à la liste des étapes
                a_faire.remove(ref_proche) # On retire la retire de la liste des références restantes à aller chercher

        self.ordre = ordre

        # Calcul de la distance totale du chemin

        distance_totale = 0
        for i in range(1, len(ordre)): 
            if i == len(ordre)-1:
                distance_totale += self.calcul_distance(self.chemin_case_to_case(ordre[i-1][1][-1],self.arrivee)) 
            else:
                distance_totale += self.calcul_distance(ordre[i][1])
        self.distance = distance_totale
    
    def dico_distances(self, refs):
        """
        Création d'un dictionnaire des distances entre les références
        Entrées : Liste - Liste des références - refs
        Sortie : Dictionnaire - Dictionnaire des distances entre les références
        """
        dic_distances = {}
        for i in range(len(refs)): # On parcourt la liste des références
            for j in range(i+1, len(refs)): # On parcourt la liste des références à partir de la référence i
                dmin = math.inf
                for case in Case.dico_boxs_cases()[refs[i].get_box()]: 
                   d = self.calcul_distance(self.chemin_case_to_ref(case, refs[j])) # On cherche la distance entre la référence i et la référence j
                   if d < dmin:
                      dmin = d
                dic_distances[(refs[i], refs[j])] = dmin # On ajoute la distance minimale au dictionnaire
        return dic_distances
    
    def save_case_dep_arr(self):
        """
        Enregistre les cases de départ et d'arrivée dans le fichier entrepot.csv
        """
        with open("data/entrepot.csv", "w+", encoding="UTF8", newline="") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["case_depart", self.choix_depart.x, self.choix_depart.y])
            writer.writerow(["case_arrivee", self.choix_arrivee.x, self.choix_arrivee.y])

    def get_case_dep_arr(self):
        """
        Récupère les cases de départ et d'arrivée dans le fichier entrepot.csv
        """
        with open("data/entrepot.csv", "r", encoding="UTF8", newline="") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if row[0] == "case_depart":
                    self.depart = Case.dico_coos_cases()[(float(row[1]), float(row[2]))]
                elif row[0] == "case_arrivee":
                    self.arrivee = Case.dico_coos_cases()[(float(row[1]), float(row[2]))]

    # Mode de sélection de l'emplacment des références

    def clic_box(self, event):
        """
        Fonction appelée lors d'un clic sur un box
        Si le mode sélection est activé, on renvoie le box sélectionné à la fenêtre parente
        Sinon, on affiche les informations de la référence stockée dans le box sélectionné si elle existe
        """
        if self.select: # Si le mode sélection est activé
            ident = self.canevas.find_withtag("current")[0] # On récupère l'identifiant du box cliqué
            box = self.rectangles[ident]
            self.racine.destroy()
            if self.class_parent != None:
                self.class_parent.change_location(box)
        else: 
            ident = self.canevas.find_withtag("current")[0]
            box = self.rectangles[ident]
            ref = box.stockes
            if ref != None and self.commande == None: # Si le box contient une référence
                tk.messagebox.showinfo(f"Box {box.allee}{box.num}", f"Référence : {ref.id}\nDésignation : {ref.name}\nPrix : {ref.price} €\nPoids : {ref.weight} kg\nStock : {ref.stock} unités\n", parent=self.racine)
    # Fonctions relatives au bandeau de prévisualisation de la préparation de commande

    def update_buttons(self):
        """
        Met à jour l'état des boutons en fonction de l'étape actuelle
        Bloque le bouton précédent si on est à la première étape
        Bloque le bouton suivant si on est à la dernière étape
        """
        if self.commande != None: 
            if self.step == 0:
                self.b_back.config(state="disabled")
            else:
                self.b_back.config(state="normal")

            if self.step == len(self.commande.contenu)+2:
                self.b_next.config(state="disabled")
            else:
                self.b_next.config(state="normal")

    def back(self, event):
        """
        Fonction appelée lors d'un clic sur le bouton précédent
        Décrémente l'étape actuelle et met à jour les boutons
        """
        if self.b_back.cget("state") != "disabled": # Si le bouton précédent n'est pas bloqué
            self.step -= 1
            self.update_buttons()
            self.show_step()

    def next(self, event):
        """
        Fonction appelée lors d'un clic sur le bouton suivant
        Incrémente l'étape actuelle et met à jour les boutons
        """
        if self.b_next.cget("state") != "disabled": # Si le bouton suivant n'est pas bloqué
            self.step += 1
            self.update_buttons()
            self.show_step()

    def show_step(self):
        """
        Affiche l'étape actuelle
        Si l'étape est 0, on affiche les données générales sur le chemin total Distance totale, temps total, nombre d'étapes
        Si l'étape est la dernière, on affiche un message de fin
        Sinon, on affiche les données de l'étape actuelle : numéro de l'étape, distance de l'étape, temps de l'étape aisi que le chemin de l'étape sur le canevas
        """
        self.stop()
        if self.step == 0: # Si on est à la première étape
            self.del_chemin()
            self.l_step.config(text=f"Étapes : {len(self.commande.contenu)+1} / Distance totale : {self.distance} / Temps : {afficher_temps(self.distance/Params.vitesse)}")

        elif self.step == len(self.commande.contenu)+1: # Si on est à l'avant dernière étape
            chemin = self.chemin_case_to_case(self.ordre[self.step-1][1][-1],self.ordre[self.step]) 
            self.l_step.config(text=f"Étape {self.step} / Distance : {self.calcul_distance(chemin)} / Temps : {afficher_temps(self.calcul_distance(chemin)/Params.vitesse)}")
            self.show_chemin(chemin)
            self.start(chemin)

        elif self.step == len(self.commande.contenu)+2: # Si on est à la dernière étape
            self.l_step.config(text=f"Préparation terminée !")
            self.del_chemin()
        else: # Si on est dans le cas général
            ref, chemin = self.ordre[self.step]
            self.l_step.config(text=f"Étape {self.step} / Référence : {ref.id} / Quantité : {self.commande.contenu[ref]} u / Distance : {self.calcul_distance(chemin)} / Temps : {afficher_temps(self.calcul_distance(chemin)/Params.vitesse)}")
            self.show_chemin(chemin, self.ordre[self.step][0])
            self.start(chemin)
    
    # Fonctions de gestion du timer lors de l'animation du chemin

    def start(self, chemin):
        """
        Lance la boucle du timer
        Vérifie que le timer n'est pas déjà lancéù
        Entrées :
            chemin : Liste - Liste des cases à parcourir
        """
        if not(self.running) :
            self.index_case = 0
            self.timer_loop(chemin)
        self.running = True

    def stop(self, delete=True):
        """
        Arrete la boucle du timer
        """
        if delete and self.id_truck != None:
                self.canevas.delete(self.id_truck)
        if self.running :
            self.racine.after_cancel(self.timer_id) 
        self.running = False

    def timer_loop(self, chemin):
        """
        Boucle principale du timer
        Entrées :
            chemin : Liste - Liste des cases à parcourir
        """
        if self.index_case == 0:
            self.id_truck = self.canevas.create_image(chemin[self.index_case].x, chemin[self.index_case].y, image=self.truck)
            self.index_case += 1

        nx, ny = chemin[self.index_case].x, chemin[self.index_case].y
        x, y = self.canevas.coords(self.id_truck)
        if (x, y) != (nx, ny):
            if x != nx:
                if x > nx:
                    x -= 1
                else:
                    x += 1
            elif y != ny:
                if y > ny:
                    y -= 1
                else:
                    y += 1
            self.canevas.coords(self.id_truck, x, y)
            self.timer_id = self.racine.after(self.dt, self.timer_loop, chemin)
        else:
            if self.index_case == len(chemin)-1:
                self.stop(False)
            else:
                self.index_case += 1
                self.timer_id = self.racine.after(self.dt, self.timer_loop, chemin)

    # Fonctions relatives au calcul et traitement des chemins entre les cases / boxs / références

    def qualite(self, case, casesarr):
        """
        Calcule la qualité d'une case
        Elle correspond à la somme de la distance euclidienne et la distance manhattan entre la case et les cases d'arrivées
        Entrées :
            case : Case - Case à évaluer
            casesarr : Liste - Liste des cases d'arrivées
        Sortie : Int - Qualité de la case
        """
        d1 = math.inf
        d2 = math.inf
        for case in casesarr:
            if case.distance_euclidienne(case) < d1:
                d1 = int(case.distance_euclidienne(case)**2)
            if case.distance_manhattan(case) < d2:
                d2 = int(case.distance_manhattan(case)**2)
        return d1 + d2

    def calcul_chemin(self, casedep, casesarr):
        """
        Calcule le chemin le plus court entre la case de départ et les cases d'arrivées
        Utilise l'algorithme A*
        Entrées :
            casedep : Case - Case de départ
            casesarr : Liste - Liste des cases d'arrivées
        Sortie : Liste - Liste des cases du chemin
        """
        self.closed = [casedep] # Liste des cases visitées
        self.open = [] # Liste des cases à visiter
        self.qualites = {casedep: self.qualite(casedep, casesarr)} # Dictionnaire des qualités des cases
        self.parents = {} # Dictionnaire des parents des cases
        resultat = self.a_star(casedep, casedep, casesarr) # On lance l'algorithme
        if resultat[0]: # Si un chemin a été trouvé
            return resultat[1]
        else: # Sinon
            return None
        
    def a_star(self, case, casedep, casesarr):
        """
        Algorithme A*
        Entrées :
            case : Case - Case à évaluer
            casedep : Case - Case de départ
            casesarr : Liste - Liste des cases d'arrivées
        Sortie : Tuple - (Booléen, Liste) - Booléen indiquant si un chemin a été trouvé et liste des cases du chemin
        """
        if case in casesarr: # Si la case est une case d'arrivée
            chemin = [case]
            while chemin[0] != casedep: # On remonte le chemin
                chemin.insert(0, self.parents[chemin[0]])
            return (True, chemin)
        else: # Sinon
            for voisin in case.ad: # On parcourt les voisins
                if voisin not in self.closed: # Si le voisin n'a pas déjà été visité
                    if voisin in self.open: # Si le voisin est déjà dans la liste des cases à visiter
                        qualite = self.qualite(voisin, casesarr) # On calcule la qualité du voisin
                        if self.qualites[voisin] > qualite: # Si la qualité du voisin est meilleure, on met à jour le parent et la qualité
                            self.parents[voisin] = case 
                            self.qualites[voisin] = qualite 
                    else: 
                        self.open.append(voisin) # On ajoute le voisin à la liste des cases à visiter et on met à jour le parent et la qualité
                        self.parents[voisin] = case 
                        self.qualites[voisin] = self.qualite(voisin, casesarr)

            if len(self.open) == 0: # Si la liste des cases à visiter est vide, on n'a pas trouvé de chemin
                return (False, [])
            else: # Sinon, on cherche la case à visiter avec la meilleure qualité
                meilleur_sommet = None
                meilleure_qualite = math.inf
                for sommet in self.open:
                    if self.qualites[sommet] < meilleure_qualite:
                        meilleur_sommet = sommet
                        meilleure_qualite = self.qualites[sommet]
                self.open.remove(meilleur_sommet) 
                # On ajoute la case à visiter à la liste des cases visitées et on relance l'algorithme
                self.closed.append(meilleur_sommet)
                return self.a_star(meilleur_sommet, casedep, casesarr)

    def ref_to_cases(self ,ref):
       """
       Renvoie la liste des cases adjacentes au box contenant la référence donnée
       Entrée : Référence - ref
       Sortie : Liste - Cases adjacentes
       """
       loc = ref.get_box()
       if loc != None:
          return Case.dico_boxs_cases().get(loc, None)

    def chemin_case_to_ref(self, casedep, ref):
        """
        Renvoie le chemin le plus court entre la case de départ et la référence donnée
        Entrée : Case - Case de départ - casedep
                 Référence - Référence d'arrivée - ref
        Sortie : Liste - chemin
        """
        casesarr = self.ref_to_cases(ref)
        self.chemins = self.calcul_chemin(casedep, casesarr)
        return self.chemins
    
    def chemin_case_to_box(self, casedep, box):
        """
        Renvoie le chemin le plus court entre la case de départ et le box donné
        Entrée : Case - Case de départ - casedep
                 Box - Box d'arrivée - box
        Sortie : Liste - chemin
        """
        casesarr = Case.dico_boxs_cases().get(box, None) # On récupère les cases adjacentes au box
        self.chemins = None
        self.chemins = self.calcul_chemin(casedep, casesarr)
        return self.chemins

    def chemin_case_to_case(self, casedep, casearr):
        """
        Renvoie le chemin le plus court entre la case de départ et la case d'arrivée
        Entrée : Case - Case de départ - casedep
                 Case - Case d'arrivée - casesarr
        Sortie : Liste - chemin
        """
        self.chemins = None # Chemin final non défini
        self.chemins = self.calcul_chemin(casedep, [casearr])
        return self.chemins
    
    def show_chemin(self, list, ref=None):
        """
        Affiche le chemin sur le canevas par des lignes et des cercles
        Entrée : Liste - Chemin à afficher - list
                    Référence - Référence d'arrivée - ref si l'arrivée est une référence
        """
        self.del_chemin() # Suppression du chemin précédent

        # Création d'une ligne entre chaque case du chemin
        for i in range(len(list)-1): 
            id = self.canevas.create_line(list[i].x, list[i].y, list[i+1].x, list[i+1].y, fill="red", arrow="last")
            self.elements_chemin.append(id)

        # Création d'un cercle au début et à la fin du chemin
        id = self.canevas.create_oval(list[0].x-5, list[0].y-5, list[0].x+5, list[0].y+5, fill="green")
        self.elements_chemin.append(id)
        id = self.canevas.create_oval(list[-1].x-5, list[-1].y-5, list[-1].x+5, list[-1].y+5, fill="red")
        self.elements_chemin.append(id)

        # Création d'une ligne entre le dernier cercle et la référence d'arrivée si elle existe
        # Gère les différentes orientations du box en fonction de la case d'arrivée

        if ref != None and ref.get_box() != None:
            milieu_box = (ref.get_box().x, ref.get_box().y)
            if milieu_box[0] == list[-1].x:
                if milieu_box[1] > list[-1].y:
                    id = self.canevas.create_line(list[-1].x, list[-1].y, milieu_box[0], ref.get_box().y-Params.cote/2, arrow="both")
                else:
                    id = self.canevas.create_line(list[-1].x, list[-1].y, milieu_box[0], ref.get_box().y+Params.cote/2, arrow="both")
            elif milieu_box[1] == list[-1].y:
                if milieu_box[0] > list[-1].x:
                    id = self.canevas.create_line(list[-1].x, list[-1].y, ref.get_box().x-Params.cote/2, milieu_box[1], arrow="both")
                else:
                    id = self.canevas.create_line(list[-1].x, list[-1].y, ref.get_box().x+Params.cote/2, milieu_box[1], arrow="both")
            else:
                id = self.canevas.create_line(list[-1].x, list[-1].y, ref.get_box().x, ref.get_box().y, arrow="both")
            self.elements_chemin.append(id)

    def del_chemin(self):
        """
        Supprime le chemin déjà affiché sur le canevas
        """
        for element in self.elements_chemin:
            self.canevas.delete(element)
        self.elements_chemin = []

    def calcul_distance(self, list):
        """
        Calcule la distance totale du chemin
        Entrée : Liste - Chemin à calculer - list
        Sortie : Float - Distance totale
        """
        if list == None:
            return math.inf
        else:
            dist = 0
            for i in range(len(list)-1):
                dist += list[i].distance_euclidienne(list[i+1])
            return dist
       
    # Fonctions relatives au mode de configuration de l'entrepôt
    
    def config_entrepot(self):
        """
        Configuration de l'entrepot dans l'optique de placer les boxs dans le canevas
        Création de la grille
        """
        for i in range(Params.nb_colonnes):
            for j in range(Params.nb_lignes):
                x = Params.cote/2+i*Params.cote
                y = Params.cote/2+j*Params.cote
                id = self.canevas.create_rectangle(x-Params.cote/2, y-Params.cote/2, x+Params.cote/2, y+Params.cote/2, fill="light gray")
                self.canevas.tag_bind(id, "<Button-1>", self.select_case)
    
    def select_case(self, event):
        """
        Sélection d'une case dans le canevas lors de la configuration de l'entrepot
        """
        id = self.canevas.find_withtag("current")[0] # On récupère l'identifiant du box cliqué
        if self.etat == 0: # Si on est en train de placer les boxs
            if id in self.selected: # Si le box est déjà sélectionné
                self.canevas.itemconfig(id, fill="light gray") 
                self.selected.remove(id) 
            else: # Sinon on le sélectionne
                self.canevas.itemconfig(id, fill="light blue")
                self.selected.append(id)
        elif self.etat == 1: # Si on est en train de placer la case départ
            if self.choix_depart != None:
                self.canevas.itemconfig(self.choix_depart, fill="light gray")
            self.choix_depart = id
            self.canevas.itemconfig(id, fill="green")
        elif self.etat == 2: # Si on est train de placer la case arrivée
            if self.choix_arrivee != None:
                if self.choix_arrivee == self.choix_depart:
                    #self.canevas.itemconfig(self.choix_arrivee, fill="green")
                    self.canevas.delete(self.id_temp)
                else:
                    self.canevas.itemconfig(self.choix_arrivee, fill="light gray")

            self.choix_arrivee = id
            if self.choix_arrivee == self.choix_depart:
                x0, y0, x1, y1 = self.canevas.coords(id)
                retrait = Params.cote/10
                self.id_temp = self.canevas.create_rectangle(x0+retrait, y0+retrait, x1-retrait, y1-retrait, fill="red")
                #self.canevas.itemconfig(id, fill="green")
            else:
                self.canevas.itemconfig(id, fill="red")

    def modif_entrepot(self, event):
        """
        Sauvegarde de la configuration de l'entrepot
        Gère d'abord le positionnement des boxs puis le positionnement de la case départ et de la case arrivée
        Vérifie que la configuration de l'entrepot est correcte, que tous les boxs sont accessibles depuis la case départ
        Et que la case d'arrivée est accessible depuis la case départ
        """
        if self.etat == 0: # Si on est en train de placer les boxs
            if len(self.selected) == 0: # Si aucun box n'a été sélectionné
                messagebox.showerror("Erreur", "Vous n'avez pas sélectionné de case", parent=self.racine)
            elif self.min_box != 0 and len(self.selected) < self.min_box: # Si le nombre de boxs sélectionnés est inférieur au nombre minimum de boxs
                messagebox.showerror("Erreur", f"Vous devez sélectionner au moins {self.min_box} cases", parent=self.racine)
            else: # Sinon on passe à la configuration de la case départ
                dico_allees = {} # Dictionnaire qui contient le nombre de boxs dans chaque allée
                Box.boxs = {} # On réinitialise la liste des boxs
                i = 0 # Numéro du box
                for id in self.canevas.find_all(): # On parcourt tous les boxs du canevas
                    if id in self.selected: # Si le box est sélectionné
                        coords = self.canevas.coords(id) # On récupère ses coordonnées
                        x = coords[0]+Params.cote/2
                        y = coords[1]+Params.cote/2
                        num_allee = int(coords[0] / Params.cote) # On récupère le numéro de l'alleé
                        allee = self.lettres[num_allee]  # On récupère la lettre de l'alleé
                        if allee not in list(dico_allees.keys()): # On actualise le nombre de boxs dans l'allée
                            dico_allees[allee] = 0
                        dico_allees[allee] = dico_allees[allee] + 1
                        num = dico_allees[allee] # On récupère le numéro du box dans l'allée
                        Box(Params.prefix_box + str(i), allee, num, x, y, None) # On crée un box 
                        i +=1 

                self.init_cases() # On initialise les cases

                valid = True 

                # On vérifie d'abord que tous les boxs sont reliés à au moins une case (Pas de box isolé)

                lien_boxs_cases = Case.dico_boxs_cases() # Dictionnaire qui contient les boxs reliés à chaque case
                for box in list(Box.boxs.values()):  # On parcourt tous les boxs
                    if box not in list(lien_boxs_cases.keys()): # Si le box n'est relié à aucune case
                        valid = False
                if valid == False: # Si un box n'est relié à aucune case
                    messagebox.showerror("Erreur", "Tous les boxs doivent être reliés à au moins une case", parent=self.racine)
                else: 
                    for box in self.selected: # On retire la réaction au clic des rectangles affectés en box
                        self.canevas.tag_unbind(box, "<Button-1>")
                    self.etat = 1 # On passe à la configuration de la case départ
                    messagebox.showinfo("Configuration", "Veuillez choisir l'emplacement de départ des préparateurs", parent=self.racine)
        
        elif self.etat == 1: # Si on est en train de chosir la case départ
            if self.choix_depart == None: # Si aucune case n'a été sélectionnée
                messagebox.showerror("Erreur", "Vous n'avez pas sélectionné de case", parent=self.racine)
            else: # Sinon on passe à la configuration de la case arrivée
                self.etat = 2
                messagebox.showinfo("Configuration", "Veuillez choisir l'emplacement d'arrivée des préparateurs", parent=self.racine)
            
        elif self.etat == 2: # Si on est en train de choisir la case arrivée
            if self.choix_arrivee == None: # Si aucune case n'a été sélectionnée
                messagebox.showerror("Erreur", "Vous n'avez pas sélectionné de case", parent=self.racine)
            else: # Sinon on vérifie que la configuration est correcte
                self.canevas.tag_unbind(self.choix_arrivee, "<Button-1>") # On retire la réaction au clic de la case arrivée
                
                # On récupère les instances cases de départ et d'arrivée associées aux coordonnées des rectangles

                self.choix_depart = Case.dico_coos_cases()[(self.canevas.coords(self.choix_depart)[0]+Params.cote/2, self.canevas.coords(self.choix_depart)[1]+Params.cote/2)]
                self.choix_arrivee = Case.dico_coos_cases()[(self.canevas.coords(self.choix_arrivee)[0]+Params.cote/2, self.canevas.coords(self.choix_arrivee)[1]+Params.cote/2)]

                valid = True
                self.access = [self.choix_depart] # On récupère les cases accessibles depuis la case départ
                self.check(self.choix_depart)

                if self.choix_arrivee not in self.access: # Si la case arrivée n'est pas accessible depuis la case départ
                    valid = False
                for box in list(Box.boxs.values()): # Si un box n'est pas accessible depuis la case départ
                    accesible = False
                    for case in Case.dico_boxs_cases().get(box, []): # On vérifie que le box est relié à une case accessible depuis la case départ
                        if case in self.access:
                            accesible = True
                            break
                    if accesible == False:
                        valid = False
                        break                
            if valid:  # Si la configuration est correcte
                # On transfère les références dans les nouveaux box (la disposition est perdue et sera à refaire)
                i = 0
                new_boxs = list(Box.boxs.values()) # On récupère les nouveaux boxs
                for box in list(self.old_box.values()): # On parcourt les anciens boxs
                    if box.stockes != None: # Si le box contient une référence
                        new_boxs[i].stockes = box.stockes # On transfère la référence
                        box.stockes.loc = new_boxs[i].id
                        i += 1

                self.save_case_dep_arr() # On enregistre la case départ et la case arrivée
                Reference.save() # On enregistre les références
                Box.save() # On enregistre les boxs
                messagebox.showinfo("Configuration", "Configuration enregistrée", parent=self.racine)
                if self.class_parent != None:
                    self.class_parent.update_table() # On met à jour la table de la fenêtre principale
                self.racine.after(100, self.racine.destroy)
            else:
                messagebox.showerror("Erreur", "La case d'arrivée n'est pas accessible depuis la case de départ ou un box n'est pas accessible depuis la case de départ", parent=self.racine)
                Box.boxs = self.old_box # On rétablit les boxs
                self.racine.after(100, self.racine.destroy)

    def check(self, case):
        """
        Fonction récurssive qui ajoute les cases accessibles à la liste self.access
        Entrée : case (Case)
        """
        for case in case.ad:
            if case not in self.access:

                self.access.append(case)
                self.check(case)
