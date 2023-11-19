# coding=utf-8

# Imports

import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from tkinter import ttk
from Settings import Params
from Objets import Reference, Commande, Box
from Fonctions import *
from Fenetre_entrepot import Fenetre_Entrepot
from Edition_reference import Edition_Reference
from Fenetre_commande import Fenetre_Commande
from Create_user import CreateUserPage

# Classe principale

class Main_fenetre():
    """
    Classe principale de l'application. Elle contient toutes les sous-fenêtres et les widgets de la fenêtre principale.
    """
    def __init__(self, user=None):
        """
        Initialise la fenêtre et la paramètre correctement
        Création des variables nécessaires dans le reste
        Lance les autres fonctions utiles dans l'ordre
        """

        # Initialisation paramètre fenêtre

        self.racine = tk.Tk()
        self.racine.title("Softwarehouse - Menu principal - Gestion références")
        self.racine.geometry("1350x540")
        self.racine.resizable(False, False)
        

        # Initialisation sous fenêtres

        self.fen_chercher_ref = None
        self.fen_chercher_com = None
        self.fen_detail_ref = None
        self.fen_manage_coms = None
        self.fen_show_entrepot = None
        self.fen_create_user = None

        # Initialisation des variables

        self.user = user
        self.v_chercher_ref = tk.StringVar()
        self.v_scale_stock = tk.IntVar()
        self.v_name_sort = tk.StringVar()
        self.v_scale_stock.set(Reference.get_min_max_stock()[1])
        self.v_name_sort.set("")

        # Création widgets

        self.creer_widgets(self.racine)
        self.permissions()

        # Lancement de la boucle d'attente

        self.racine.mainloop()

    def creer_widgets(self, root):
        """
        Création des widgets de la fenêtre principale
        Entrées : root (tk.Tk) : la fenêtre racine
        """

        # Label Titre principal

        l_titre = tk.Label(root, text="Menu principal", anchor=tk.CENTER, font="Helvetica 20 bold")
        l_titre.pack(side=tk.TOP, fill="x", pady=10)

        # Barre de scroll Listbox

        sb_scroll = tk.Scrollbar(root)
        sb_scroll.pack(side=tk.LEFT, fill="y")
        
        # Tableau références

        self.tv_refs = ttk.Treeview(root, yscrollcommand=sb_scroll.set, selectmode="browse")
        self.tv_refs["columns"] = ("Dénomination", "Prix", "Poids", "Stock", "Emplacement")
        self.tv_refs.heading("#0", text="Référence")
        self.tv_refs.column("#0",anchor=tk.CENTER, width=80)
        self.tv_refs.heading("#1", text="Dénomination")
        self.tv_refs.column("#1",anchor=tk.CENTER, width=200)
        self.tv_refs.heading("#2", text="Prix")
        self.tv_refs.column("#2",anchor=tk.CENTER, width=100)
        self.tv_refs.heading("#3", text="Poids")
        self.tv_refs.column("#3",anchor=tk.CENTER, width=100)
        self.tv_refs.heading("#4", text="Stock")
        self.tv_refs.column("#4",anchor=tk.CENTER, width=100)
        self.tv_refs.heading("#5", text="Emplacement")
        self.tv_refs.column("#5",anchor=tk.CENTER, width=100)
        self.tv_refs.bind("<Double-1>", self.double_clic_ref)
        self.tv_refs.pack(side=tk.LEFT, fill="y", pady=5)

        # Configuration scrollbar sur listbox

        sb_scroll.config(command=self.tv_refs.yview)

        # Frames
        
        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.TOP, fill="both", expand=True)

        self.frame_gauche = tk.Frame(self.frame)
        self.frame_droit = tk.Frame(self.frame)

        self.frame_gauche.grid(row=0, column=0, sticky="nsew")
        self.frame_droit.grid(row=0, column=1, sticky="nsew")

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # Label Référence

        tk.Label(self.frame_gauche, text="Références :", font="Helvetiva 13 bold").pack(side=tk.TOP, fill="x", padx=10, pady=5)
        
        # Séparateur

        ttk.Separator(self.frame_gauche, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label indications

        tk.Label(self.frame_gauche, text="Double-cliquez sur une référence\npour la modifier / supprimer", font="Helvetica 10").pack(side=tk.TOP)
                                                      
        # Bouton chercher référence

        b_chercher_ref = tk.Button(self.frame_gauche, text="Chercher une référence", height=2)
        b_chercher_ref.bind("<Button-1>", self.show_chercher_ref)
        b_chercher_ref.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Bouton ajouter référence

        self.b_add_ref = tk.Button(self.frame_gauche, text="Ajouter une référence", height=2)
        self.b_add_ref.bind("<Button-1>", self.add_ref)
        self.b_add_ref.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Séparateur

        ttk.Separator(self.frame_gauche, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label scale

        tk.Label(self.frame_gauche, text="Afficher seulement si\nstock inférieur ou égal à :", font="Helvetiva 10 underline").pack(side=tk.TOP, fill="x", padx=10)
        
        # Scale

        min, max = Reference.get_min_max_stock()
        self.scale = tk.Scale(self.frame_gauche, orient="horizontal", from_=min, to=max, variable=self.v_scale_stock, resolution=1)
        self.v_scale_stock.set(max)
        self.scale.bind("<ButtonRelease-1>", self.sort_table)
        self.scale.pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Label Entry

        tk.Label(self.frame_gauche, text="Afficher seulement si\nla désignation contient :", font="Helvetiva 10 underline").pack(side=tk.TOP, fill="x", padx=10)
       
        # Entry

        entry = tk.Entry(self.frame_gauche, textvariable=self.v_name_sort)
        entry.bind("<KeyRelease>", self.sort_table)
        entry.pack(side=tk.TOP, fill="x", padx=10, pady=15)

        # Label commandes

        tk.Label(self.frame_droit, text="Commandes :", font="Helvetiva 13 bold").pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Séparateur

        ttk.Separator(self.frame_droit, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Bouton onglet commande

        b_chercher_com = tk.Button(self.frame_droit, text="Gérer commandes", height=2)
        b_chercher_com.pack(side=tk.TOP, fill="x", padx=10, pady=5)
        b_chercher_com.bind("<Button-1>", self.show_gerer_com)
        
        # Séparateur

        ttk.Separator(self.frame_droit, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label entrepôt

        tk.Label(self.frame_droit, text="Entrepôt :", font="Helvetiva 13 bold").pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Bouton afficher entrepôt

        b_quit = tk.Button(self.frame_droit, text="Afficher entrepôt", height=2)
        b_quit.bind("<Button-1>", self.show_entrepot)
        b_quit.pack(side=tk.TOP, pady=5, padx=10, fill="x")

        # Bouton modiifier entrepôt

        self.b_modif = tk.Button(self.frame_droit, text="Modifier l'entrepôt", height=2)
        self.b_modif.bind("<Button-1>", self.show_modif_entrepot)
        self.b_modif.pack(side=tk.TOP, pady=5, padx=10, fill="x")

        # Séparateur

        ttk.Separator(self.frame_droit, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label utilisateurs

        tk.Label(self.frame_droit, text="Utilisateurs :", font="Helvetiva 13 bold").pack(side=tk.TOP, fill="x", padx=10, pady=5)

        # Bouton modiifier entrepôt

        self.b_user = tk.Button(self.frame_droit, text="Ajouter un utilisateur", height=2)
        self.b_user.bind("<Button-1>", self.create_user)
        self.b_user.pack(side=tk.TOP, pady=5, padx=10, fill="x")

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Bouton quitter

        b_quit = tk.Button(root, text="Quitter", width=2, height=2)
        b_quit.bind("<Button-1>", self.quit)
        b_quit.pack(side=tk.BOTTOM, pady=5, padx=10, fill="x")

        self.update_table() # Actualise le tableau
        
    def permissions(self):
        """
        Active ou désactive les boutons en fonction des permissions de l'utilisateur
        """
        if self.user != None and self.user.admin == True:
            self.b_add_ref.config(state="normal")
            self.b_modif.config(state="normal")
            self.b_user.config(state="normal")
        else:
            self.b_add_ref.config(state="disabled")
            self.b_modif.config(state="disabled")
            self.b_user.config(state="disabled")

    def clear_all(self):
        """
        Supprime tous les items du tableau
        """
        for item in self.tv_refs.get_children():
            self.tv_refs.delete(item)

    def update_table(self):
        """
        Supprime et actualise tous les items du tableau
        Prend en compte les seuils d'alertes et configure les bonnes couleurs
        Actualise aussi les bornes du scale
        """
        self.clear_all()
        min, max = Reference.get_min_max_stock() 
        self.scale.config(from_=min, to=max) 
        for ref in list(Reference.references.values()):
            if ref.name.lower() != "none":
                if (ref.stock <= float(self.v_scale_stock.get())) and (self.v_name_sort.get().lower() in ref.name.lower()):
                    tag = ()
                    if Params.alert_stock_3 >= 0 and ref.stock <= Params.alert_stock_3:
                        tag = ("alert3")
                    elif Params.alert_stock_2 >= 0 and ref.stock <= Params.alert_stock_2:
                        tag = ("alert2")
                    elif Params.alert_stock_1 >= 0 and ref.stock <= Params.alert_stock_1:
                        tag = ("alert1")
                    else:
                        tag = ("noalert")
                    self.tv_refs.insert(parent="", tags=tag, index="end" ,text=ref.id, values=(ref.name, str(ref.price) + " €", str(ref.weight) + " kg", str(ref.stock) + " u", f"{ref.get_emplacement()[0]}{ref.get_emplacement()[1]}"))
        self.tv_refs.tag_configure("alert1", foreground=Params.color_alert_stock_1, background=Params.color_bg_alert_stock_1)
        self.tv_refs.tag_configure("alert2", foreground=Params.color_alert_stock_2, background=Params.color_bg_alert_stock_2)
        self.tv_refs.tag_configure("alert3", foreground=Params.color_alert_stock_3, background=Params.color_bg_alert_stock_3)
        self.tv_refs.tag_configure("noalert", foreground=Params.color_no_alert) 
        
    def quit(self, event):
        """
        Ferme la fenêtre
        """
        self.racine.destroy()
    
    def show_entrepot(self, event):
        """
        Permet l'affichage de la fenêtre de l'entrepot
        """
        if self.fen_show_entrepot != None:
            self.fen_show_entrepot.racine.destroy()
        self.fen_show_entrepot = Fenetre_Entrepot(self)
        self.fen_show_entrepot.racine.mainloop()

    def show_chercher_ref(self, event):
        """
        Affichage et initialisation de la fenêtre Top Level pour la saisie d'une recherche de référence
        """
        if self.fen_chercher_ref != None:
            self.fen_chercher_ref.destroy()

        # Initialisation de la sous-fenêtre

        self.fen_chercher_ref = tk.Toplevel()
        self.fen_chercher_ref.resizable(False, False)
        self.fen_chercher_ref.geometry("250x80")
        self.fen_chercher_ref.title("Rechercher")
        self.fen_chercher_ref.bind('<Escape>', self.quit_chercher_ref)

        # Bouton validation de recherche

        b_valider_chercher_ref = tk.Button(self.fen_chercher_ref, text="Rechercher")
        b_valider_chercher_ref.bind("<Button-1>", self.chercher_refs)
        b_valider_chercher_ref.pack(side=tk.BOTTOM, fill="x", padx=10, pady=5)

        # Label préfixe référence

        l_R = tk.Label(self.fen_chercher_ref, text=Params.prefix_reference, font="Helvetica 11 bold")
        l_R.pack(side=tk.LEFT, padx=10, pady=5)

        # Entry de saisie de recherche

        e_chercher_ref = tk.Entry(self.fen_chercher_ref, textvariable=self.v_chercher_ref, width=60)
        e_chercher_ref.bind("<Return>", self.chercher_refs)
        e_chercher_ref.pack(side=tk.RIGHT, fill="x", padx=10, pady=5)
        e_chercher_ref.focus()
    
    def create_user(self, event):
        """
        Permet l'affichage de la fenêtre de création d'un utilisateur
        """
        if self.b_user.cget("state") != "disabled":
            if self.fen_create_user != None:
                self.fen_create_user.racine.destroy()
            self.fen_create_user = CreateUserPage(self)
            self.fen_create_user.racine.mainloop()

    def quit_chercher_ref(self, event):
        """
        Fermer la fenêtre de recherche de références
        """
        self.fen_chercher_ref.destroy()

    def chercher_refs(self, event):
        """
        Recherche d'une référence parmi le catalogue
        Si la référence est trouvée, la fenêtre de recherche est fermée et la référence est affichée
        Si la référence n'est pas trouvée, une erreur est affichée
        """
        text = self.v_chercher_ref.get() 
        # Si la saisie commence par le préfixe de référence, on le supprime
        if len(text) > len(Params.prefix_reference)-1 and text[0:len(Params.prefix_reference)].upper() == Params.prefix_reference.upper():
            id = text.upper()
        else: # Sinon on l'ajoute
            id = Params.prefix_reference + text.upper()
        
        if id not in list(Reference.references.keys()): # Si la référence n'existe pas
            tk.messagebox.showerror("Erreur", f"Référence {id} introuvable", parent=self.fen_chercher_ref)
            self.show_chercher_ref(None)
        elif Reference.references[id].name.lower() == "none": # Si la référence a été supprimée
            self.v_chercher_ref.set("")
            tk.messagebox.showerror("Erreur", f"Référence {id} n'existe plus", parent=self.fen_chercher_ref)
            self.fen_chercher_ref.destroy()
        else: # Si la référence existe
            self.v_chercher_ref.set("")
            self.fen_chercher_ref.destroy()
            self.details_ref(Reference.references[id])
            
    def details_ref(self, ref):
        """
        Affichage la fenêtre Top Level pour l'affichage des détails d'une référence
        """
        if self.fen_detail_ref != None:
            self.fen_detail_ref.destroy()
        self.fen_detail_ref = Edition_Reference(self, ref, user=self.user).racine
        self.fen_detail_ref.mainloop()

    def sort_table(self, event):
        """
        Trie la table des références
        """
        self.update_table()
    
    def double_clic_ref(self, event):
        """
        Affiche les détails d'une référence lors d'un double clic sur une référence dans le tableau
        """
        item = self.tv_refs.selection() # On récupère l'item sélectionné
        if item: # Si un item est sélectionné
            ref = self.tv_refs.item(item[0])["text"] # On récupère la référence
            self.details_ref(Reference.references[ref]) 

    def add_ref(self, event):
        """
        Affiche la fenêtre Top Level pour l'ajout d'une référence
        """
        if self.b_add_ref.cget("state") != "disabled": # Si le bouton est actif
            if Reference.nb_active_ref() >= len(Box.boxs)-1: # Si le nombre de références actives est supérieur au nombre de boxs
                tk.messagebox.showerror("Erreur", f"Nombre maximum de référence atteint", parent=self.racine)
            else: 
                if self.fen_detail_ref != None:
                    self.fen_detail_ref.destroy()
                self.fen_detail_ref = Edition_Reference(self, None, user=self.user).racine 
                self.fen_detail_ref.mainloop()
    
    def show_gerer_com(self, event):
        """
        Affiche la fenêtre Top Level pour la gestion des commandes
        """
        if self.fen_manage_coms != None:
            self.fen_manage_coms.destroy()
        self.fen_manage_coms = Fenetre_Commande(self, self.user).racine
        self.fen_manage_coms.mainloop()
        
    def show_modif_entrepot(self, event):
        """
        Affiche la fenêtre Top Level pour la modification de l'entrepôt
        """
        if self.b_modif.cget("state") != "disabled":
            if self.fen_show_entrepot != None:
                self.fen_show_entrepot.racine.destroy()
            self.fen_show_entrepot = Fenetre_Entrepot(self, create=True, min_box=Reference.nb_active_ref()+1)
            self.fen_show_entrepot.racine.mainloop()