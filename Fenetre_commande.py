# coding=utf-8

# Imports

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
from Settings import Params
from Objets import Reference, Commande, Box, Utilisateur
from Fonctions import *
from Fenetre_entrepot import Fenetre_Entrepot
from Details_commande import Details_Commande

# Classe principale

class Fenetre_Commande(): 
    """
    La fenêtre de gestion des commandes permet de visualiser les commandes en cours et de les traiter.
    On peut trier les commandes si elles sont traitées ou non, et on peut rechercher une commande par son numéro et si elle est faisable ou non.
    """

    def __init__(self, parent, user=None):
        """
        Initialise la fenêtre de gestion des commandes.
        Entrées : parent (Main_fenetre) : la fenêtre principale ayant appelé cette fenêtre
                  user (Utilisateur) : l'utilisateur connecté
        """

        # Création de la fenêtre

        self.racine = tk.Toplevel(parent.racine)
        self.racine.title("Softwarehouse - Gestion commandes")
        self.racine.geometry("900x620")
        self.racine.resizable(False, False)

        # Variables

        self.parent = parent
        self.user = user
        self.v_chercher_com = tk.StringVar()
        self.fen_chercher_com = None
        self.fen_detail_com = None

        self.creer_widgets(self.racine)
        self.update_labels()
        self.update_table()

    def quit(self, event):
        """
        Quitte la fenêtre
        """
        self.racine.destroy()

    def creer_widgets(self, root):
        """
        Crée les widgets de la fenêtre
        Entrées : root (tk.Tk) : la fenêtre racine
        """

        # Label Titre principal

        l_titre = tk.Label(root, text="Commandes", anchor=tk.CENTER, font="Helvetica 20 bold")
        l_titre.pack(side=tk.TOP, fill="x", pady=10)

        # Barre de scroll Listbox

        sb_scroll = tk.Scrollbar(root)
        sb_scroll.pack(side=tk.LEFT, fill="y")
        
        # Tableau références

        self.tv_coms = ttk.Treeview(root, yscrollcommand=sb_scroll.set, selectmode="browse")
        self.tv_coms["columns"] = ("Date", "Client", "Articles", "Traitée", "Opérateur")
        self.tv_coms.heading("#0", text="Numéro")
        self.tv_coms.column("#0",anchor=tk.CENTER, width=80)
        self.tv_coms.heading("#1", text="Date")
        self.tv_coms.column("#1",anchor=tk.CENTER, width=100)
        self.tv_coms.heading("#2", text="Client")
        self.tv_coms.column("#2",anchor=tk.CENTER, width=150)
        self.tv_coms.heading("#3", text="Articles")
        self.tv_coms.column("#3",anchor=tk.CENTER, width=100)
        self.tv_coms.heading("#4", text="Traitée")
        self.tv_coms.column("#4",anchor=tk.CENTER, width=100)
        self.tv_coms.heading("#5", text="Opérateur")
        self.tv_coms.column("#5",anchor=tk.CENTER, width=150)
        self.tv_coms.bind("<Double-1>", self.double_clic_com)
        self.tv_coms.pack(side=tk.LEFT, fill="y", pady=5)

        # Configuration scrollbar sur listbox

        sb_scroll.config(command=self.tv_coms.yview)

        # Bouton retour

        b_quit = tk.Button(root, text="Retour", width=2, height=2)
        b_quit.bind("<Button-1>", self.quit)
        b_quit.pack(side=tk.BOTTOM, pady=5, padx=10, fill="x")

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Bouton chercher commande

        b_chercher = tk.Button(root, text="Chercher une commande", height=2)
        b_chercher.bind("<Button-1>", self.show_chercher_com)
        b_chercher.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Bouton ouvrir commande 

        b_open = tk.Button(root, text="Ouvrir la commande", height=2)
        b_open.bind("<Button-1>", self.double_clic_com)
        b_open.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label filtre

        tk.Label(root, text="Commandes déjà traitées", font="Helvetica 10").pack(side=tk.TOP)
                  
        # Check Button afficher commandes traitées

        self.v_traitee = tk.IntVar()
        checkbtraitee= tk.Checkbutton(root, text="Afficher", variable=self.v_traitee, onvalue=True, offvalue=False)
        checkbtraitee.bind("<Button-1>", self.update_filtered_table1)
        checkbtraitee.pack(side= tk.TOP)     
        checkbtraitee.deselect()

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)
        
        # Label filtre

        tk.Label(root, text="Commandes non réalisables", font="Helvetica 10").pack(side=tk.TOP)

        # Check Button afficher commandes non réalisables

        self.v_possible = tk.IntVar()
        checkbpossible= tk.Checkbutton(root, text="Afficher", variable=self.v_possible, onvalue=True, offvalue=False)
        checkbpossible.bind("<Button-1>", self.update_filtered_table2)
        checkbpossible.pack(side= tk.TOP) 
        checkbpossible.select()

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label indicateur nombre de commandes non traitées

        tk.Label(root, text="Commandes non traitées", font="Helvetica 10").pack(side=tk.TOP)
        self.l_non_traitee = tk.Label(root, text="", font="Helvetiva 13 bold")
        self.l_non_traitee.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Label indicateur nombre de commandes réalisables

        tk.Label(root, text="Commandes réalisables", font="Helvetica 10").pack(side=tk.TOP)
        self.l_possible = tk.Label(root, text="", font="Helvetiva 13 bold")
        self.l_possible.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Bouton statistiques

        b_stats = tk.Button(root, text="Statistiques", height=2)
        b_stats.bind("<Button-1>", self.show_stats)
        b_stats.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

    def update_labels(self):
        """
        Met à jour les labels indiquant le nombre de commandes non traitées, réalisables et total
        """
        self.l_non_traitee.config(text=str(Commande.nb_non_traitee_coms()))
        self.l_possible.config(text=str(Commande.nb_possible_coms()))

    def update_filtered_table1(self, event):
        """
        Met à jour le tableau en fonction des filtres
        Appelé par le filtre "Commandes déjà traitées"
        """
        self.update_table(not bool(self.v_traitee.get()), bool(self.v_possible.get()))

    def update_filtered_table2(self, event):
        """
        Met à jour le tableau en fonction des filtres
        Appelé par le filtre "Commandes non réalisables"
        """
        self.update_table(bool(self.v_traitee.get()), not bool(self.v_possible.get()))

    def double_clic_com(self, event):
        """
        Ouvre les détails de la commande sélectionnée dans le tableau
        """
        item = self.tv_coms.selection() # Récupère l'item sélectionné
        if item: 
            num = self.tv_coms.item(item[0])["text"]
            commande = Commande.commandes[num] # Récupère la commande correspondante
            self.details_com(commande) # Ouvre les détails de la commande
        else: # Si aucun item n'est sélectionné
            tk.messagebox.showerror("Erreur", f"Veuillez sélectionner une commande", parent=self.racine)

    def clear_all(self):
        """
        Supprime tous les items du tableau
        """
        for item in self.tv_coms.get_children():
            self.tv_coms.delete(item)

    def update_table(self, afficher_traitee = False, afficher_non_possible = True):
        """
        Supprime et actualise tous les items du tableau en fonction des filtres
        Entrées :
            afficher_traitee : booléen indiquant si les commandes déjà traitées doivent être affichées
            afficher_non_possible : booléen indiquant si les commandes non réalisables doivent être affichées
        """
        self.clear_all()
        
        for com in list(Commande.commandes.values()): # Pour chaque commande
            if afficher_traitee or (com.traitee == False): # Si la commande n'est pas traitée ou si on veut afficher les commandes traitées
                if afficher_non_possible or com.is_possible(): # Si la commande est réalisable ou si on veut afficher les commandes non réalisables
                    tag = ()
                    if com.traitee:
                        tag = ("traitee") # Si la commande est traitée, on la met en gris
                    elif com.is_possible():
                        tag = ("possible") # Si la commande est réalisable, on la met en vert
                    else:
                        tag = ("pas_possible") # Si la commande n'est pas réalisable, on la met en rouge
                    self.tv_coms.insert(parent="", tags=tag, index="end" ,text=com.id, values=(str(com.date), str(com.client), com.nb_refs(), bool_to_str(com.traitee), com.get_operateur_name()))
        # Configuration des couleurs des lignes
        self.tv_coms.tag_configure("traitee", foreground="black", background="light gray")
        self.tv_coms.tag_configure("possible", foreground="dark green")
        self.tv_coms.tag_configure("pas_possible", foreground="red")

    def details_com(self, commande):
        """
        Affichage et initialisation de la fenêtre Top Level pour les détails d'une commande
        Entrées :
            commande : Commande - commande dont on veut afficher les détails
        """
        if self.fen_detail_com != None:
            self.fen_detail_com.destroy()
        self.fen_detail_com = Details_Commande(self, commande, self.user).racine
        self.fen_detail_com.mainloop()

    def show_chercher_com(self, event):
        """
        Affichage et initialisation de la fenêtre Top Level pour la saisie d'une recherche de commande
        """
        if self.fen_chercher_com != None:
            self.fen_chercher_com.destroy()

        # Initialisation de la fenêtre de recherche de commandes

        self.fen_chercher_com = tk.Toplevel()
        self.fen_chercher_com.resizable(False, False)
        self.fen_chercher_com.geometry("250x80")
        self.fen_chercher_com.title("Rechercher")
        self.fen_chercher_com.bind('<Escape>', self.quit_chercher_com)

        # Bouton validation de recherche

        b_valider_chercher_com = tk.Button(self.fen_chercher_com, text="Rechercher")
        b_valider_chercher_com.bind("<Button-1>", self.chercher_coms)
        b_valider_chercher_com.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)

        # Label préfixe commande

        l_R = tk.Label(self.fen_chercher_com, text=Params.prefix_commande, font="Helvetica 11 bold")
        l_R.pack(side=tk.LEFT, padx=10, pady=5)

        # Entry de saisie de recherche

        e_chercher_com = tk.Entry(self.fen_chercher_com, textvariable=self.v_chercher_com, width=60)
        e_chercher_com.bind("<Return>", self.chercher_coms)
        e_chercher_com.pack(side=tk.RIGHT, fill="x", padx=10, pady=5)
        e_chercher_com.focus()
    
    def quit_chercher_com(self, event):
        """
        Fermer la fenêtre de recherche de commandes
        """
        self.fen_chercher_com.destroy()

    def chercher_coms(self, event):
        """
        Recherche d'une commande
        """
        text = self.v_chercher_com.get() # Récupère la saisie de l'utilisateur
        # Si le texte saisi commence par le préfixe de commande, on ne l'ajoute pas
        if len(text) > len(Params.prefix_commande)-1 and text[0:len(Params.prefix_commande)].upper() == Params.prefix_commande.upper():
            id = text.upper()
        else: # Sinon, on l'ajoute
            id = Params.prefix_commande+ text.upper()
        
        if id not in list(Commande.commandes.keys()): # Si la commande n'existe pas
            tk.messagebox.showerror("Erreur", f"Commande {id} introuvable", parent=self.fen_chercher_com)
            self.show_chercher_com(None)
        else: 
            self.v_chercher_com.set("")
            self.fen_chercher_com.destroy()
            self.details_com(Commande.commandes[id]) # Ouvre les détails de la commande

    def show_stats(self, event):
        """
        Affichage d'une message box avec des statistiques sur les commandes
        """
        messagebox.showinfo("Statistiques", f"Nombre de commandes au total : {Commande.nb_total_coms()}\nNombre de commandes traitées : {Commande.nb_traitee_coms()}\nNombre de commandes non traitées : {Commande.nb_non_traitee_coms()}\nNombre de commandes réalisables : {Commande.nb_possible_coms()}\nNombre de commandes non réalisables : {Commande.nb_impossible_coms()}\nChiffre d'affaires acquis : {Commande.get_chiffre_affaire()[0]} €\nChiffre d'affaires en attente : {Commande.get_chiffre_affaire()[1]} €\nRéférence la plus commandée : {Commande.refs_plus_commandes()}\nEmployé ayant validé le plus de commandes : {Utilisateur.max_commandes()}", parent=self.racine)
