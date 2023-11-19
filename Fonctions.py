# coding=utf-8

# Ce fichier contient des fonctions globales utilisées dans le programme à plusieurs endroits

# Imports

from Objets import Utilisateur
from tkinter import messagebox

# Fonctions

def isfloat(num):
    """
    Fonction qui vérifie si un nombre est un float
    Sortie: True si le nombre est un float, False sinon
    """
    try:
        float(num)
        return True
    except ValueError:
        return False
    
def isint(num):
    """
    Fonction qui vérifie si un nombre est un int et non un float
    Sortie: True si le nombre est un int, False sinon
    """
    try:
        if (float(num) - int(num)) == 0: 
            return True
        else:
            return False
    except ValueError: 
        return False

def bool_to_str(value):
    """
    Fonction qui convertit un booléen en chaîne de caractères
    Sortie: 'Oui' si le booléen est True, 'Non' sinon
    """
    if value:
        return "Oui"
    else:
        return "Non"
    
def afficher_temps(tempsenmin):
    """
    Fonction qui convertit un temps en minutes en une chaîne de caractères
    Sortie: String contenant le temps en minutes et secondes
    """
    if tempsenmin == 0: 
        return ""
    elif tempsenmin < 1:
        return f"{int(tempsenmin*60)} s"
    else:
        return (f"{int(tempsenmin)} min " + afficher_temps(tempsenmin-int(tempsenmin)))
    
def connect(username , password):
    """
    Fonction qui vérifie si un utilisateur existe et si son mot de passe est correct
    Sortie: (True, Utilisateur) si l'utilisateur existe et que le mot de passe est correct
            (False, None) sinon
    """
    user = Utilisateur.utilisateurs.get(username, None)
    if user != None:
        if password == user.password:
            return (True, user)
        else:
            return (False, None)
    else:
        return (False, None)
    
def username_available(username):
    """
    Fonction qui vérifie si un nom d'utilisateur est disponible
    Sortie: True si le nom d'utilisateur est disponible, False sinon
    """
    user = Utilisateur.utilisateurs.get(username, None)
    if user == None:
        return True
    else:
        return False
