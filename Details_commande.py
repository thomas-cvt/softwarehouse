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

# Classe principale

class Details_Commande():
    """
    Classe permettant d'afficher les détails d'une commande
    Permet aussi de la valider, d'afficher les références qu'elle contient et d'afficher le chemin à suivre pour préparer la commande
    """

    def __init__(self, parent, commande, user=None):
        """
        Constructeur de la classe
        Entrées:
            parent: Fenetre parente ayant appelé la classe
            commande: Commande à afficher
            user: Utilisateur connecté
        """

        # Initialisation de la fenêtre
        self.racine = tk.Toplevel(parent.racine)
        self.parent = parent
        self.racine.title(f"Softwarehouse - Commande {commande.id}")
        self.racine.geometry("1200x585")
        self.racine.resizable(False, False)

        # Variables

        self.commande = commande
        self.user = user
        self.fen_show_entrepot = None

        self.creer_widgets(self.racine)
        self.update_table()
        self.update_labels()

    def quit(self, event):
        """
        Quitte la fenêtre
        """
        self.racine.destroy()

    def creer_widgets(self, root):
        """
        Crée les widgets de la fenêtre
        Entrées:
            root: Racine de la fenêtre
        """

        # Label Titre principal

        l_titre = tk.Label(root, text=f"Commande {self.commande.id}", anchor=tk.CENTER, font="Helvetica 20 bold")
        l_titre.pack(side=tk.TOP, fill="x", pady=10)

        # Barre de scroll Listbox

        sb_scroll = tk.Scrollbar(root)
        sb_scroll.pack(side=tk.LEFT, fill="y")
        
        # Tableau références

        self.tv_com = ttk.Treeview(root, yscrollcommand=sb_scroll.set, selectmode="browse")
        self.tv_com["columns"] = ("Désignation", "Poids unitaire", "Poids total", "Prix unitaire", "Prix total", "En stock", "Quantité", "Emplacement")
        self.tv_com.heading("#0", text="Référence")
        self.tv_com.column("#0",anchor=tk.CENTER, width=80)
        self.tv_com.heading("#1", text="Désignation")
        self.tv_com.column("#1",anchor=tk.CENTER, width=150)
        self.tv_com.heading("#2", text="Poids unitaire")
        self.tv_com.column("#2",anchor=tk.CENTER, width=100)
        self.tv_com.heading("#3", text="Poids total")
        self.tv_com.column("#3",anchor=tk.CENTER, width=100)
        self.tv_com.heading("#4", text="Prix unitaire")
        self.tv_com.column("#4",anchor=tk.CENTER, width=100)
        self.tv_com.heading("#5", text="Prix total")
        self.tv_com.column("#5",anchor=tk.CENTER, width=100)
        self.tv_com.heading("#6", text="En stock")
        self.tv_com.column("#6",anchor=tk.CENTER, width=100)
        self.tv_com.heading("#7", text="Quantité")
        self.tv_com.column("#7",anchor=tk.CENTER, width=100)
        self.tv_com.heading("#8", text="Emplacement")
        self.tv_com.column("#8",anchor=tk.CENTER, width=80)
        self.tv_com.pack(side=tk.LEFT, fill="y", pady=5)

        # Configuration scrollbar sur listbox

        sb_scroll.config(command=self.tv_com.yview)

        # Bouton retour

        b_quit = tk.Button(root, text="Retour", width=2, height=2)
        b_quit.bind("<Button-1>", self.quit)
        b_quit.pack(side=tk.BOTTOM, pady=5, padx=10, fill="x")

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.BOTTOM, padx=20, pady=10)

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label état commande

        color = ""
        text = ""
        if self.commande.traitee: # Si la commande est traitée
            color = "black"
            text = f"Commande traitée par\n{self.commande.get_operateur_name()}"
        elif self.commande.is_possible(): # Si la commande est faisable
            color = "dark green"
            text = "Commande faisable en\nattente de validation"
        else: # Si la commande n'est pas faisable
            color = "dark red"
            text = "Commande non faisable"
        tk.Label(root, text= text, foreground=color, anchor=tk.CENTER, font="Helvetica 13 bold").pack(side=tk.TOP, fill="x", padx=20, pady=10)

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Label infos commande

        tk.Label(root, text="Client :", font="Helvetica 10").pack(side=tk.TOP)
        self.l_client= tk.Label(root, text="", font="Helvetiva 10 bold")
        self.l_client.pack(side=tk.TOP, fill="x", padx=10)

        tk.Label(root, text="Date :", font="Helvetica 10").pack(side=tk.TOP)
        self.l_date = tk.Label(root, text="", font="Helvetiva 10 bold")
        self.l_date.pack(side=tk.TOP, fill="x", padx=10)

        tk.Label(root, text="Nb articles", font="Helvetica 10").pack(side=tk.TOP)
        self.l_nb = tk.Label(root, text="", font="Helvetiva 10 bold")
        self.l_nb.pack(side=tk.TOP, fill="x", padx=10)

        tk.Label(root, text="Poids total :", font="Helvetica 10").pack(side=tk.TOP)
        self.l_poids = tk.Label(root, text="", font="Helvetiva 10 bold")
        self.l_poids.pack(side=tk.TOP, fill="x", padx=10)

        tk.Label(root, text="Prix total :", font="Helvetica 10").pack(side=tk.TOP)
        self.l_prix = tk.Label(root, text="", font="Helvetiva 10 bold")
        self.l_prix.pack(side=tk.TOP, fill="x", padx=10)

        # Séparateur

        ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=10)

        # Bouton valider

        self.b_valider = tk.Button(root, text="Valider la commande", width=2, height=2)
        self.b_valider.bind("<Button-1>", self.valider)
        self.b_valider.pack(side=tk.BOTTOM, pady=5, padx=10, fill="x")

         # Bouton entrepot

        self.b_entrepot = tk.Button(root, text="Préparer la commande", width=2, height=2)
        self.b_entrepot.bind("<Button-1>", self.chemin_preparation)
        self.b_entrepot.pack(side=tk.BOTTOM, pady=5, padx=10, fill="x")

        # Si la commande est traitée ou si elle n'est pas faisable, on désactive le bouton valider
        # Si la commande n'est pas faisable, on désactive le bouton préparer

        if not self.commande.is_possible() or self.commande.traitee: 
            self.b_valider.config(state="disabled")
        if self.commande.no_deleted_ref() == False:
            self.b_entrepot.config(state="disabled")
        if self.commande.traitee == True:
            self.b_entrepot.config(state="disabled")

    def update_labels(self):
        """
        Met à jour les labels de la fenêtre en fonction de la commande
        """
        self.l_client.config(text=self.commande.client)
        self.l_date.config(text=self.commande.date)
        self.l_nb.config(text=self.commande.nb_refs())
        self.l_poids.config(text=str(self.commande.calcul_poids()) + " kg")
        self.l_prix.config(text=str(self.commande.calcul_prix()) + " €")

    def valider(self, event):
        """
        Valide la commande
        Demande confirmation à l'utilisateur
        Soustrait les quantités des références de l'entrepôt
        Note le nom de l'opérateur qui a validé la commande
        """

        if self.b_valider.cget("state") != "disabled": # Si le bouton est activé
            msg_box = tk.messagebox.askquestion('Validation commande', f'Voulez-vous vraiment valider la commande {self.commande.id} ?', icon='question', parent=self.racine) # Demande confirmation
            if msg_box == 'yes': # Si l'utilisateur confirme
                self.commande.valider(self.user) # Valide la commande
                messagebox.showinfo("Validation", f"La commande {self.commande.id} a bien été validée", parent=self.racine)
                self.parent.parent.update_table() # Met à jour la table des références
                self.parent.update_table() # Met à jour la table des commandes
                self.parent.update_labels() # Met à jour les labels de la fenêtre
                self.parent.details_com(self.commande) # Relance la fenêtre de détails de la commande

    def chemin_preparation(self, event):
        """
        Affiche la fenetre de l'entrepot en mode préparation
        Permet d'afficher les étapes de préparation de la commande et le chemin à suivre
        """
        if self.b_entrepot.cget("state") != "disabled":
            if self.fen_show_entrepot != None:
                self.fen_show_entrepot.racine.destroy()

            # Initialise la fenetre

            self.fen_show_entrepot = Fenetre_Entrepot(self, commande=self.commande, user=self.user)
            self.fen_show_entrepot.racine.mainloop()

    def clear_all(self):
        """
        Supprime tous les items du tableau
        """
        for item in self.tv_com.get_children():
            self.tv_com.delete(item)

    def update_table(self):
        """
        Supprime et actualise tous les items du tableau
        """
        self.clear_all()
        for ref, quant in list(self.commande.contenu.items()):
            tag = ()
            name = str(ref.name)
            if self.commande.traitee: # Si la commande est traitée, les lignes sont normales
                tag = ()
            elif ref.name.lower() == "none": # Si la référence n'existe plus, la ligne est rouge
                tag = ("error")
                name = "Supprimée"
            elif quant > ref.stock: # Si la quantité demandée est supérieure au stock, la ligne est rouge
                tag = ("no")
            else: # Sinon, la ligne est verte
                tag = ("yes") 
            self.tv_com.insert(parent="", tags=tag, index="end" ,text=ref.id, values=(name, str(ref.weight) + " kg", str(round(ref.weight*quant, 2)) + "kg", str(ref.price) + " €", str(round(ref.price*quant, 2)) + " €", str(ref.stock), str(quant), f"{ref.get_emplacement()[0]}{ref.get_emplacement()[1]}"))
        # Couleurs des lignes
        self.tv_com.tag_configure("error", foreground="black", background="red2")
        self.tv_com.tag_configure("yes", foreground="dark green")
        self.tv_com.tag_configure("no", foreground="red")