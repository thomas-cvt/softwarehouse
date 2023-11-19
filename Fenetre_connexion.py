# coding=utf-8

# Imports

import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
from Main_fenetre import Main_fenetre
from Fonctions import connect

# Classe principale

class Fenetre_connexion():
  """
  La fenêtre de connexion permet de se connecter à l'application par un nom d'utilisateur et un mot de passe.
  Si ils sont valides, la fenêtre se ferme et la fenêtre principale s'ouvre.
  """
  def __init__(self):
    """
    Initialise la fenêtre de connexion.
    """
    # Création de la fenêtre
    self.racine = tk.Tk()
    self.racine.title("Softwarehouse - Connexion")
    self.racine.geometry("400x215")
    self.racine.resizable(False, False)

    # Variables

    self.username = tk.StringVar()
    self.password = tk.StringVar()

    # Evenements

    self.racine.bind("<Return>", self.connexion)
    self.racine.bind('<Escape>', self.quit)

    self.cree_widgets(self.racine)
    self.id.focus()
    self.racine.mainloop()
    
  def cree_widgets(self, root):
    """
    Crée les widgets de la fenêtre de connexion.
    Entrées : root (tk.Tk) : la fenêtre racine
    """
    # Titre

    self.Presentation = tk.Label(root, text="Softwarehouse", font=("Helvetical 14 bold"))
    self.Presentation.pack(side=tk.TOP, pady=7, fill="x")

    # Séparateur

    ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=5)

    # Cadre nom d'utilisateur

    self.user_frame = tk.Frame(root)
    self.user_frame.pack(side=tk.TOP, fill="x", padx=10, pady=2)

    # Label nom d'utilisateur

    tk.Label(self.user_frame, text="Nom d'utilisateur : ", font="Helvetica 12").pack(padx=10, side=tk.LEFT)

    # Champ nom d'utilisateur

    self.id = tk.Entry(self.user_frame, textvariable=self.username)
    self.id.pack(fill="x", padx=10, side=tk.TOP)
    
    # Cadre mot de passe

    self.mdp_frame = tk.Frame(root)
    self.mdp_frame.pack(side=tk.TOP, fill="x", padx=10, pady=2)

    # Label mot de passe

    tk.Label(self.mdp_frame, text="Mot de passe : ", font="Helvetica 12").pack(padx=10, side=tk.LEFT)

    # Champ mot de passe

    self.mdp = tk.Entry(self.mdp_frame, show="*", textvariable=self.password)
    self.mdp.pack(fill="x", padx=10, side=tk.TOP)

    # Bouton connexion

    self.connect = tk.Button(root, text="Connexion", height=2)
    self.connect.bind("<Button-1>", self.connexion)
    self.connect.pack(side=tk.TOP, padx=10, pady=1, fill="both")

    # Séparateur

    ttk.Separator(root, orient="horizontal").pack(fill="x", side=tk.TOP, padx=20, pady=5)

    # Bouton quitter

    self.Quitter = tk.Button(root, text="Quitter", bg="light gray", height=1)
    self.Quitter.bind("<Button-1>", self.quit)
    self.Quitter.pack(fill="x", side=tk.TOP,padx=10, pady=5)
      
  def quit(self, event):
      """
      Quitte l'application.
      """
      self.racine.destroy()

  def connexion(self, event):
    """
    Vérifie si le nom d'utilisateur et le mot de passe sont valides.
    Si oui, la fenêtre se ferme et la fenêtre principale s'ouvre.
    Si non, un message d'erreur s'affiche.
    """

    connecte, user = connect(self.username.get(), self.password.get()) # On récupère les informations de connexion

    if connecte == False:
      tk.messagebox.showerror("Erreur", f"Nom d'utilisateur ou mot de passe invalide", parent=self.racine)
      self.id.focus()
    else:
      if user.admin: 
        tk.messagebox.showinfo("Connecté", f"Connecté en tant que {user.name}\nVous êtes administrateur", parent=self.racine)   
      else:
        tk.messagebox.showinfo("Connecté", f"Connecté en tant que {user.name}", parent=self.racine)
      
      self.quit(None)
      Main_fenetre(user)
      
