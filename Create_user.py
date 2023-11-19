# coding=utf-8

# Imports

import tkinter as tk
from tkinter import messagebox
from Objets import Utilisateur
from Fonctions import *

# Classe principale

class CreateUserPage():
    """
    Classe de la fenêtre de création d'un utilisateur
    """
    
    def __init__(self, master=None):
        """
        Initialise la fenêtre de création d'un utilisateur
        Si master est None, la fenêtre est une racine, sinon elle est une fenêtre toplevel de master
        Entrées:
            master: la fenêtre parente
        """
        self.parent = master
        if self.parent == None:
            self.racine = tk.Tk()
        else:
            self.racine = tk.Toplevel(self.parent.racine)
        self.racine.title("Création d'un utilisateur")
        self.racine.geometry("350x255")
        self.create_widgets(self.racine)
        self.racine.bind("<Return>", self.create_account)

    def create_widgets(self, root):
        """
        Initialise les widgets de la fenêtre
        Entrées:
            root: la fenêtre parente
        """
        # Titre

        tk.Label(root, text="Création d'un utilisateur", font="Helvetica 17 bold").pack(side=tk.TOP, anchor=tk.CENTER, pady=10)

        # Nom

        frame_nom = tk.Frame(root)
        frame_nom.pack(side=tk.TOP, anchor=tk.CENTER, pady=5, fill="x", padx=7)

        
        self.entry_name = tk.Entry(frame_nom, width=25)
        self.entry_name.pack(side=tk.RIGHT, padx=3)
        self.label_name = tk.Label(frame_nom, text="Nom :")
        self.label_name.pack(padx=7, fill="x")

        # Identifiant

        frame_id = tk.Frame(root)
        frame_id.pack(side=tk.TOP, anchor=tk.CENTER, pady=5, fill="x", padx=7)

        self.entry_id = tk.Entry(frame_id, width=25)
        self.entry_id.pack(side=tk.RIGHT, padx=3)
        self.label_id = tk.Label(frame_id, text="Identifiant :")
        self.label_id.pack(padx=7, fill="x")

        # Mot de passe

        frame_pass = tk.Frame(root)
        frame_pass.pack(side=tk.TOP, anchor=tk.CENTER, pady=5, fill="x", padx=7)

        self.entry_password = tk.Entry(frame_pass, show="*", width=25)
        self.entry_password.pack(side=tk.RIGHT, padx=3)
        self.label_password = tk.Label(frame_pass, text="Mot de passe :")
        self.label_password.pack(padx=7, fill="x")

        # Confirmation de mot de passe

        frame_pass2 = tk.Frame(root)
        frame_pass2.pack(side=tk.TOP, anchor=tk.CENTER, pady=5, fill="x", padx=7)

        self.entry_confirm_password = tk.Entry(frame_pass2, show="*", width=25)
        self.entry_confirm_password.pack(side=tk.RIGHT, padx=3)
        self.label_confirm_password = tk.Label(frame_pass2, text="Confirmer le mot de passe :")
        self.label_confirm_password.pack(padx=7, fill="x")

        # Check bouton pour les droits administrateurs
        self.admin_var = tk.IntVar()
        self.check_admin = tk.Checkbutton(root, text="Droits administrateurs", variable=self.admin_var)
        self.check_admin.pack(side=tk.TOP, padx=10, pady=5, fill="x")

        frame_buttons = tk.Frame(root)
        frame_buttons.pack(side=tk.TOP, anchor=tk.CENTER, pady=5, fill="x", padx=7)

        # Bouton pour créer un compte
        self.button_create = tk.Button(frame_buttons, text="Créer un compte", width=20)
        self.button_create.bind("<Button-1>", self.create_account)
        self.button_create.pack(side=tk.RIGHT, padx=10)

        # Bouton pour quitter l'interface
        self.button_quit = tk.Button(frame_buttons, text="Quitter", width=15, command=self.quit)
        self.button_quit.pack(side=tk.LEFT, padx=10)

    def quit(self):
        """
        Quitte l'interface
        """
        self.racine.destroy()

    def create_account(self, event):
        """
        Crée un compte utilisateur
        Vériﬁe que les champs sont remplis et que l'identifiant n'est pas déjà utilisé
        Si on est sur la première connexion, on vérifie que l'utilisateur créé est administrateur
        Si tout est bon, on crée l'utilisateur et on le sauvegarde
        """

        name = self.entry_name.get()
        id = self.entry_id.get()
        password = self.entry_password.get()
        confirm_password = self.entry_confirm_password.get()
        is_admin = bool(self.admin_var.get())
        if name == "" or id == "" or password == "" or confirm_password == "":
            messagebox.showerror("Erreur", "Tous les champs doivent être remplis.", parent=self.racine)
        elif password != confirm_password:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas.", parent=self.racine)
        elif username_available(id) == False:
            messagebox.showerror("Erreur", "L'identifiant est déjà utilisé.", parent=self.racine)
        elif self.parent == None and is_admin == False:
            messagebox.showerror("Erreur", "Vous devez créer un compte administrateur pour le premier utilisateur.", parent=self.racine)
        else:
            Utilisateur(id, name, password, is_admin)
            Utilisateur.save()
            if is_admin:
                messagebox.showinfo("Création utilisateur", f"L'utilisateur {name} a été créé avec succès. Il est administrateur.", parent=self.racine)
            else:
                messagebox.showinfo("Création utilisateur", f"L'utilisateur {name} a été créé avec succès.", parent=self.racine)
            self.racine.after(300, self.quit)
