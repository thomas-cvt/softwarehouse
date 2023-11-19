# coding=utf-8

# Imports

import json, csv
from Objets import Reference, Commande, Utilisateur, Box
from Main_fenetre import Main_fenetre
from Fenetre_entrepot import Fenetre_Entrepot
from Fenetre_connexion import Fenetre_connexion
from Create_user import CreateUserPage
from Fonctions import *
# Fonctions

def init_data():
  """
  Execute dans le bon ordre le chargement de toutes les données et la création de toutes les instances. Cette fonction doit être obligatoirement exécutée avant toutes les autres.
  """
  create_references()
  create_users()
  create_commandes()
  create_boxs()

  if len(Box.boxs) == 0: # Si premier lancement et qu'aucun box n'existe déjà, on configure l'entrepot
    fen = Fenetre_Entrepot(None, create=True, min_box=Reference.nb_active_ref()+1)
    fen.racine.mainloop()

  if len(Utilisateur.utilisateurs) == 0: # Si premier lancement et qu'aucun utilisateur n'existe déjà, on crée un compte administrateur
    fen = CreateUserPage(None)
    fen.racine.mainloop()

  if len(Box.boxs) != 0 and len(Utilisateur.utilisateurs) != 0: # Si des box existent et qu'un utilisateur existe, on lance la fenetre principale
    Fenetre_connexion()

def load_references():
  """
  Lit les références présentes dans le fichier CSV references.csv
  S'execute dans create_references
  """
  with open("data/references.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    l = []
    for ligne in reader:
      l.append(ligne)
    return l

def load_commandes():
  with open("data/commandes.json", encoding="utf-8") as f:
    """
  Lit les commandes présentes dans le fichier JSON commandes.json
  S'execute dans create_commandes
  """

    return json.load(f)

def load_boxs():
  """
  Lit les boxs présents dans le fichier CSV boxs.csv
  S'execute dans create_references
  """
  with open("data/boxs.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    l = []
    for ligne in reader:
      l.append(ligne)
    return l

def load_users():
  """
  Lit les utilisateurs présents dans le fichier CSV users.csv
  S'execute dans create_references
  """
  with open("data/users.csv", newline="", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=",")
    l = []
    for ligne in reader:
      l.append(ligne)
    return l
  
def create_references():
  """
  Crée, à partir des données lues dans le SCV, toutes les instances de la classe Reference avec les attributs associés dans leur bon type
  S'execute toujours avant create_commandes
  """
  references_lues = load_references()
  for ref in references_lues:
    loc = None
    if str(ref[5]) == "" or str(ref[5]) == "None":
      loc = None
    else:
      loc = str(ref[5])

    Reference(str(ref[0]), str(ref[1]), float(ref[2]), float(ref[3]), int(ref[4]), loc)
    
def create_commandes():
  """
  Crée, à partir des données lues dans le JSON, toutes les instances de la classe Commande avec les attributs associés dans leur bon type
  S'execute toujours après create_references
  """
  commandes_lues = load_commandes() # On lit les données du JSON
  for com in commandes_lues:
    new_contenu = {} # On recrée le dictionnaire contenu en remplaçant les String lus par les instances de Reference
    for ref, quant in list(com["contenu"].items()):
      new_contenu[Reference.references[ref]] = int(quant)
    operateur = Utilisateur.utilisateurs.get(str(com["operateur"]), None)
    Commande(str(com["id"]), str(com["client"]), str(com["date"]), new_contenu, bool(com["traitee"]), operateur)

def create_boxs():
  """
  Crée, à partir des données lues dans le CSV, toutes les instances de la classe Box avec les attributs associés dans leur bon type
  S'execute toujours après create_references
  """
  boxs_lues = load_boxs()
  for box in boxs_lues:
    stockes = None
    if str(box[5]) == "" or str(box[5]) == "None":
      stockes = None
    else:
      stockes = str(box[5])
    Box(str(box[0]), str(box[1]), str(box[2]), str(box[3]), str(box[4]), stockes)

def create_users():
  """
  Crée, à partir des données lues dans le CSV, toutes les instances de la classe utilsateur avec les attributs associés dans leur bon type
  """
  users_lus = load_users()
  for user in users_lus:
    if user[3].lower() == "true":
      admin = True
    else:
      admin = False
    Utilisateur(user[0], user[1], user[2], admin)

init_data() # On initialise toutes les données

