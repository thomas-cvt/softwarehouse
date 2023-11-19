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

# Classe principale

class Edition_Reference():
    """
    Fenêtre création et édition de référence
    Si ref = None -) Mode création, sinon modification
    Modification de tous les champs sauf id
    Sauvegarde et suprression
    """

    def __init__(self, parent, ref=None, user=None):
        """
        Initialise la fenêtre d'édition de référence.
        Entrées : parent (Fenetre_Entrepot) : la fenêtre parente
                  ref (Reference) : la référence à éditer ou None si création
                  user (User) : l'utilisateur connecté
        """
        
        # Création de la fenêtre

        self.parent = parent
        self.racine = tk.Toplevel(parent.racine)
        self.ref = ref
        self.racine.resizable(False, False)

        # Variables

        self.fen_change_loc = None
        self.user = user
        
        self.racine.bind("<Return>", self.validate)
        self.creer_widgets(self.racine)
        self.permissions()
        self.current_box = None
    
        if ref != None: # Mode édition
            self.racine.title(f"Édition référence {ref.id}")
            self.current_box = self.ref.get_box()
            self.show_data()
        else: # Mode création
            self.racine.title("Création référence")
            self.init_create()

    def creer_widgets(self, root):
        """
        Crée les widgets de la fenêtre d'édition de référence.
        Entrées : root (tk.Tk) : la fenêtre racine
        """
        # Titre

        self.l_title = tk.Label(root, text="Informations Référence :", anchor=tk.CENTER, font="Helvetica 12 bold")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=10, padx=20)

        # Labels des champs

        tk.Label(root, text="Identifiant : ").grid(row=1, column=0, pady=5, padx=10)
        tk.Label(root, text="Désignation : ").grid(row=2, column=0, pady=5, padx=10)
        tk.Label(root, text="Prix : ").grid(row=3, column=0, pady=5, padx=10)
        tk.Label(root, text="Poids : ").grid(row=4, column=0, pady=5, padx=10)
        tk.Label(root, text="Stock : ").grid(row=5, column=0, pady=5, padx=10)
        tk.Label(root, text="Emplacement : ").grid(row=6, column=0, pady=5, padx=10)

        # Variables des champs de saisie

        self.v_name = tk.StringVar()
        self.v_price = tk.StringVar()
        self.v_weight = tk.StringVar()
        self.v_stock = tk.StringVar()
        self.v_add = tk.StringVar()

        # Champs de saisie

        self.e_name = tk.Entry(root, textvariable=self.v_name, width=30)
        self.e_price = tk.Entry(root, textvariable=self.v_price, width=30)
        self.e_weight = tk.Entry(root, textvariable=self.v_weight, width=30)
        self.e_stock = tk.Entry(root, textvariable=self.v_stock, width=30)
        
        self.e_name.grid(row=2, column=1, padx=10, pady=5, columnspan=2, sticky="nesw")
        self.e_price.grid(row=3, column=1, padx=10, pady=5, columnspan=2, sticky="nesw")
        self.e_weight.grid(row=4, column=1, padx=10, pady=5, columnspan=2, sticky="nesw")
        self.e_stock.grid(row=5, column=1, padx=10, pady=5, columnspan=2, sticky="nesw")

        # Labels unités

        tk.Label(root, font="Helvetica 14").grid(row=2, column=3, padx=10, pady=5)
        tk.Label(root, text="€", font="Helvetica 14").grid(row=3, column=3, padx=10, pady=5)
        tk.Label(root, text="kg", font="Helvetica 14").grid(row=4, column=3, padx=10, pady=5)
        tk.Label(root, text="u", font="Helvetica 14").grid(row=5, column=3, padx=10, pady=5)

        # Label référence

        self.l_reference = tk.Label(root, text="", font="Helvetica 14 bold")
        self.l_reference.grid(row=1, column=1, padx=10, pady=5, columnspan=4)

        # Label emplacement
        
        self.l_emplacement = tk.Label(root, text="", font="Helvetica 14")
        self.l_emplacement.grid(row=6, column=1, padx=10, pady=5)

        # Bouton modifier emplacement

        self.b_change_loc = tk.Button(root, text="Modifier")
        self.b_change_loc.bind("<Button-1>", self.show_change_location)
        self.b_change_loc.grid(row=6, column=2, padx=10, pady=5, sticky="nesw")

        # Entry ajouter stock et label

        row = 7
        if self.ref != None:
            tk.Label(root, text="Ajouter au stock : ").grid(row=7, column=0, pady=5, padx=10)
            self.e_add = tk.Entry(root, textvariable=self.v_add, width=30)
            self.e_add.grid(row=7, column=1, padx=10, pady=5, columnspan=2, sticky="nesw")
            tk.Label(root, text="u", font="Helvetica 14").grid(row=7, column=3, padx=10, pady=5)
            row = 8

        # Boutons retour

        self.b_retour = tk.Button(root, text="Retour / Annuler")
        self.b_retour.bind("<Button-1>", self.quit)
        
        if self.ref != None: # Mode édition
            self.b_retour.grid(row=row, column=0, padx=10, pady=5, columnspan=1, sticky="nesw") 

            self.b_delete = tk.Button(root, text="Supprimer") # On ajoute le bouton supprimer
            self.b_delete.bind("<Button-1>", self.delete)
            self.b_delete.grid(row=row, column=1, padx=10, pady=5, columnspan=1, sticky="nesw")
        else: # Mode création
            self.b_retour.grid(row=row, column=0, padx=10, pady=5, columnspan=2, sticky="nesw")
        
        # Bouton valider

        self.b_valider = tk.Button(root, text="Valider")
        self.b_valider.bind("<Button-1>", self.validate)
        self.b_valider.grid(row=row, column=2, padx=10, pady=5,columnspan=2, sticky="nesw")

    def permissions(self):
        """
        Gère les permissions de l'utilisateur.
        Désactive la modification / suppression et création de référence si l'utilisateur n'est pas administrateur.
        """
        if self.user != None and self.user.admin == True: # Si l'utilisateur est administrateur
            if self.ref != None:
                self.b_delete.config(state="normal")
                self.e_add.config(state="normal")
            self.b_valider.config(state="normal")
            self.b_change_loc.config(state="normal")
            self.e_name.config(state="normal")
            self.e_price.config(state="normal")
            self.e_stock.config(state="normal")
            self.e_weight.config(state="normal")
            
        else: 
            if self.ref != None:
                self.b_delete.config(state="disabled")
                self.e_add.config(state="disabled")
            self.b_valider.config(state="disabled")
            self.b_change_loc.config(state="disabled")
            self.e_name.config(state="disabled")
            self.e_price.config(state="disabled")
            self.e_weight.config(state="disabled")
            self.e_stock.config(state="disabled")

    def show_data(self):
        """
        Affiche les données actuelles de la référence dans les champs de saisie si mode édition.
        """
        ref = self.ref
        self.l_reference.config(text=ref.id)
        self.v_name.set(ref.name)
        self.v_price.set(ref.price)
        self.v_weight.set(ref.weight)
        self.v_stock.set(ref.stock)
        e = ref.get_emplacement()
        self.l_emplacement.config(text=f"{e[0]} {e[1]}")

        # Modifie le texte de certains éléments

        self.l_title.config(text="Informations référence :")
        self.b_valider.config(text="Enregistrer")
        self.b_retour.config(text="Retour")

    def init_create(self):
        """
        Initialise la fenêtre en mode création.
        """
        # Modifie le texte de certains éléments
        self.l_title.config(text="Création référence :")
        self.l_reference.config(text=Reference.get_next_reference()) # Affiche la référence à créer
        self.b_valider.config(text="Valider")
        self.b_retour.config(text="Annuler")
        
    def quit(self, event):
        """
        Quitte la fenêtre.
        """
        self.racine.destroy()

    def delete(self, event):
        """
        Supprime la référence en cours d'édition.
        Demande confirmation à l'utilisateur.
        """
        if self.b_delete.cget("state") != "disabled":
            name = self.ref.name
            msg_box = tk.messagebox.askquestion('Suppression référence', f'Voulez-vous vraiment supprimer {name} ?', icon='warning', parent=self.racine)
            if msg_box == 'yes': # Si l'utilisateur confirme
                self.ref.delete() # Supprime la référence
                Reference.save() # Sauvegarde les références
                Box.save() # Sauvegarde les boxs
                self.parent.update_table() # Met à jour la table
                tk.messagebox.showinfo("Suppression référence", f"{name} supprimée avec succès", parent=self.racine)
                self.racine.destroy()

    def validate(self, event):
        """
        Valide les données saisies.
        Vérifie que les données saisies sont valides, bien renseignées et cohérentes.
        Si mode création, crée la référence.
        Si mode édition, modifie la référence.
        """
        if self.b_valider.cget("state") != "disabled":  # Si le bouton est actif
            valeurs = { # Récupère les données saisies
                "id": self.l_reference.cget("text"),
                "name": self.e_name.get(),
                "price": self.e_price.get().replace(",", "."),
                "weight": self.e_weight.get().replace(",", "."),
                "stock": self.e_stock.get(),
                "loc": self.current_box
            }
            if self.ref != None: 
                valeurs["add"] = self.e_add.get()
            else:
                valeurs["add"] = 0
                
            is_valid, formate = self.is_valid(valeurs) # Vérifie que les données sont valides

            if is_valid:
                if self.ref != None:  # Modification de référence
                    ref = self.ref
                    ref.name = formate["name"]
                    ref.price = formate["price"]
                    ref.weight = formate["weight"]
                    ref.stock = formate["stock"]
                    ref.stock += formate["add"]
                    ancien = ref.loc
                    ref.loc = formate["loc"]

                    # Si la référence a changé de box, on met à jour les boxs

                    if ancien != formate["loc"]:
                        if ancien != None:
                            Box.boxs[ancien].stockes = None
                        if formate["loc"] != None:
                            Box.boxs[formate["loc"]].stockes = ref

                    # On sauvegarde

                    Reference.save()
                    Box.save()
                    self.parent.update_table() # Met à jour la table
                    tk.messagebox.showinfo("Modification référence", f"{formate['name']} modifiée avec succès", parent=self.racine)

                else: # Création de référence
                    ref = Reference(formate["id"], formate["name"], formate["price"], formate["weight"], formate["stock"], formate["loc"]) # Création de la référence
                    if formate["loc"] != None: 
                        Box.boxs[formate["loc"]].stockes = ref

                    # On sauvegarde

                    Reference.save()
                    Box.save()
                    self.parent.update_table() 
                    tk.messagebox.showinfo("Ajout référence", f"{formate['name']} ajouté avec succès", parent=self.racine)
                self.racine.destroy()

    def is_valid(self, champs):
        """
        Vérifie que tous les champs sont renseingnés et les formates au bon format
        En cas d'erreur, affiche un message d'erreur et renvoie False
        SI tout est bon, renvoie True
        Entrées : champs : dictionnaire contenant les champs à vérifier
        Sorties : (bool, dict) : bool indique si les champs sont valides, dict contient les champs formatés
        """
        if len(champs["name"]) < 1 or champs["name"].lower() == "none": # Si la désignation est vide ou égale à "none" dans le cas d'une référence supprimée
            tk.messagebox.showerror("Erreur", f"Désignation non valide", parent=self.racine)
            self.e_name.focus()
            return (False, None)
            
        elif len(champs["price"]) < 1 or not isfloat(champs["price"]) or float(champs["price"]) < 0: # Si le prix est vide ou n'est pas un nombre ou est négatif
            tk.messagebox.showerror("Erreur", f"Prix non valide", parent=self.racine)
            self.e_price.focus()
            return (False, None)

        elif len(champs["weight"]) < 1 or not isfloat(champs["weight"]) or float(champs["weight"]) < 0: # Si le poids est vide ou n'est pas un nombre ou est négatif
            tk.messagebox.showerror("Erreur", f"Poids non valide", parent=self.racine)
            self.e_weight.focus()
            return (False, None)

        elif len(champs["stock"]) < 1 or not isint(champs["stock"]) or int(champs["stock"]) < 0: # Si le stock est vide ou n'est pas un nombre entier ou est négatif
            tk.messagebox.showerror("Erreur", f"Stock non valide", parent=self.racine)
            self.e_stock.focus()
            return (False, None)
        elif self.current_box == None: # Si la référence n'a pas de box
            tk.messagebox.showerror("Erreur", f"Emplacement non valide", parent=self.racine)
            self.e_stock.focus()
            return (False, None)
        elif self.ref != None and len(champs["add"]) > 0 and (not isint(champs["add"]) or int(champs["add"]) < 0): # Si le stock à rajouter n'est pas un nombre entier ou est négatif
            tk.messagebox.showerror("Erreur", f"Stock à rajouter non valide", parent=self.racine)
            self.e_add.focus()
            return (False, None)
        else: # Si tout est bon
            new_valeurs = { # Formate les données
            "id": self.l_reference.cget("text"),
            "name": self.e_name.get(),
            "price": float(self.e_price.get().replace(",", ".")),
            "weight": float(self.e_weight.get().replace(",", ".")),
            "stock": int(self.e_stock.get()),
        }
            if self.ref != None and len(champs["add"]) > 0:
                new_valeurs["add"] = int(self.e_add.get())
            else:
                new_valeurs["add"] = 0

            if self.current_box == None: # Récupère l'emplacement sélectionné
                new_valeurs["loc"] = None
            else:
                new_valeurs["loc"] = self.current_box.id
            return (True, new_valeurs)

    def show_change_location(self, event):
        """
        Affiche la fenêtre de sélection d'emplacement
        """
        if self.b_change_loc.cget("state") != "disabled":
            if self.fen_change_loc != None:
                self.fen_change_loc.destroy()

            # Initalisation de la fenêtre

            self.new_location = None
            if self.ref != None:
                self.fen_change_loc = Fenetre_Entrepot(self, select=True, ref=self.ref).racine
            else:
                self.fen_change_loc = Fenetre_Entrepot(self, select=True).racine
            
            self.fen_change_loc.mainloop()

    def change_location(self, box):
        """
        Change l'emplacement de la référence
        Entrées : box : Box : nouveau box
        """
        if box != None: 
            if box.stockes != None: # Si le box est déjà occupé
                if self.ref == None or (self.ref != None and box != self.ref.get_box()): # Si le box est déjà occupé par une autre référence
                    tk.messagebox.showerror("Erreur", f"Box {box.allee + box.num} déjà occupé", parent=self.racine) # On affiche un message d'erreur
                    self.show_change_location(None) # On réaffiche la fenêtre de sélection d'emplacement
                else: # Si le box est déjà occupé par la référence
                    self.current_box = box # On change l'emplacement
                    self.l_emplacement.config(text=f"{self.current_box.allee}{self.current_box.num}") # On met à jour l'affichage
            else: # Si le box est libre
                self.current_box = box # On change l'emplacement
                self.l_emplacement.config(text=f"{self.current_box.allee}{self.current_box.num}") # On met à jour l'affichage