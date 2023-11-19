# coding=utf-8

# Imports

from Settings import Params
import csv
import math

# Objets de l'application

class Reference():
  """
  Une référence correspond à un objet physique qui est vendu par l'entreprise. 
  Toutes les références disponibles sont stockées dans un fichier CSV.
  """

  references = {} # Dictionaire des références, dont les clés sont les identifiants des références et les valeurs les instances de la classe Reference
  max = 0 # Numéro de la dernière référence
  used_id = []
  
  def __init__(self, id, name, price, weight, stock = 0, loc=None):
    """
    Initialise l'objet référence
    Entrées :
        - id : String unique - Identifiant
        - name : String - Désignation
        - price : float - Prix
        - weight : float - Poids
        - stock : int - Quantité en stock
        - loc : String - Identifiant du box qui contient la référence (None dans le cas contraire)
    """
    self.id = str(id)
    self.name = name
    self.price = round(float(price), 2)
    self.weight = round(float(weight), 2)
    self.stock = int(stock)
    self.loc = loc

    Reference.used_id.append(id)
    Reference.references[str(id)] = self
    if int(str(id)[len(Params.prefix_reference):]) > Reference.max:
      Reference.max = int(str(id)[len(Params.prefix_reference):])

  def __str__(self):
    """
    Renvoie la représentation complète de l'objet référence
    Sortie : String
    """
    return f"Référence : {self.id} | Dénomination : {self.name} | Prix : {self.price} € | Poids : {self.weight} kg | Stock : {self.stock}"
  
  def __repr__(self):
    """
    Renvoie la représentation rapide de l'objet référence
    Sortie : String
    """
    return str(self.id)
  
  def nb_active_ref():
    """
    Renvoie le nombre de références actives (qui ne sont pas supprimées)
    Sortie : int
    """
    nb = 0
    for ref in list(Reference.references.values()):
      if ref.name.lower() != "none":
        nb += 1
    return nb
  
  def delete(self):
    """
    Supprime l'objet référence, remplace ses attributs et l'enlève de son emplacement
    """
    self.name = "none"
    self.price = 0
    self.weight = 0
    self.stock = 0
    if self.get_box() != None:
      self.get_box().stockes = None
      self.loc = None

  def get_emplacement(self):
    """
    Renvoie un tuple de String correspondant respectivement à l'allée et le numéro dans l'allée de la référence (Strings vides si pas d'emplacement)
    Sortie : tuple
    """
    loc = self.get_box()
    if loc != None:
      return (str(loc.allee), str(loc.num))
    else:
      return("","")
    
  def get_box(self):
    """
    Renvoie l'instance de l'objet Box associé à l'emplacement de la référence (None si pas d'emplacement)
    Sortie : Box
    """
    if self.loc != None:
      return Box.boxs[self.loc]
    else:
      return None
    
  def get_next_reference():
    """
    Renvoie en String la référence de la prochaine référence crée
    Si l'id le plus élevé des toutes les références est R-9, elle renvoie R-10
    Sortie : String
    """
    return(Params.prefix_reference + str(Reference.max+1))
  
  def get_min_max_stock():
    """
    Renvoie un tuple d'entier composé du stock minimal existant et du stock maximal existant parmi l'ensemble des références
    Sortie : tuple
    """
    min = math.inf
    max = 0
    if Reference.nb_active_ref() == 0:
      return (0,0)
    else:
      for ref in list(Reference.references.values()):
        if ref.name.lower() != "none":
          if ref.stock < min:
            min = ref.stock
          if ref.stock > max:
            max = ref.stock
      return (min, max)
  
  def save():
    """
    Sauvegarde les données de toutes les instantes de la classe dans le fichier CSV associé
    """
    with open("data/references.csv", "w+", encoding="UTF8", newline="") as f:
      writer = csv.writer(f, delimiter=",")
      for ref in list(Reference.references.values()):
          if ref.get_box() != None:
            writer.writerow([str(ref.id), str(ref.name), str(ref.price), str(ref.weight), str(ref.stock), ref.get_box().id])
          else:
            writer.writerow([str(ref.id), str(ref.name), str(ref.price), str(ref.weight), str(ref.stock), "None"])

class Commande():
  """
  Une commande correspond à un acte d'achat par un client. 
  Elle se compose d'une ou plusieurs références de l'entreprise ainsi que d'une quantité associée. 
  L'ensemble des commandes sont stockées dans un fichier JSON. Nous supposerons que ce fichier est généré par une application extérieure (boutique en ligne) 
  et est importé dans l'application.
  """
  commandes = {} # Dictionnaire des commandes, dont les clés sont les identifiants des commandes et les valeurs les instances de la classe Commande
  
  def __init__(self, id, client, date, contenu, traitee = False, operateur = ""):
    """
    Initialise l'objet commande
    Entrées :
        - id : String unique - Identifiant
        - client : String - Nom de l'acheteur
        - date : String - Date d'achat
        - contenu : dictionnaire - Instances références et quantitée désirée
        - traitee : Boolean - État de traitement 
        - operateur : String - Nom de l'opérateur ayant valider la commande - None si aucun
    """
    self.id = str(id)
    self.client = client
    self.date = date
    self.contenu = contenu
    self.traitee = traitee
    self.operateur = operateur
    Commande.commandes[str(id)] = self
    
  def calcul_prix(self):
    """
    Calcule le prix total de la commande
    Sortie : float
    """
    total = 0
    for ref, quant in list(self.contenu.items()):
      total += ref.price * quant
    return round(total, 2)
    
  def calcul_poids(self):
    """
    Calcule le poids total de la commande
    Sortie : float
    """
    total = 0
    for ref, quant in list(self.contenu.items()):
      total += ref.weight * quant
    return round(total, 2)
  
  def is_possible(self):
    """
    Vérifie si la commande est possible, c'est à dire si le stock de chaque référence est suffisant
    Sortie : Boolean
    """
    valid = True
    for ref in list(self.contenu.keys()):
      if self.contenu[ref] > ref.stock:
        valid = False
    return valid
  
  def no_deleted_ref(self):
    """
    Vérifie si la commande ne contient pas de référence supprimée
    Sortie : Boolean
    """
    valid = True
    for ref in list(self.contenu.keys()):
      if ref.name.lower() == "none":
        valid = False
    return valid
  
  def nb_refs(self):
    """
    Renvoie le nombre de références dans la commande
    Sortie : int
    """
    return len(self.contenu)
  
  def __str__(self):
    """
    Renvoie la représentation complète de l'objet commande
    Sortie : String
    """
    return f"Commande : {self.id} | Client : {self.client} | Date : {self.date} | Contenu : {len(self.contenu)} références | Traitée : {self.traitee} | Opérateur : {self.get_operateur_name()}"
  def __repr__(self):
    """
    Renvoie la représentation rapide de l'objet commande
    Sortie : String
    """
    return str(self.id)
  
  def get_operateur_name(self):
    """
    Renvoie le nom de l'opérateur ayant validé la commande, ou une chaîne vide si aucun
    Sortie : String
    """
    if self.operateur != None:
      return self.operateur.name
    else:
      return ""
    
  def valider(self, operateur):
    """
    Valide la commande, c'est à dire que le stock de chaque référence est décrémenté
    Entrées : operateur : Instance de la classe Utilisateur - Opérateur ayant validé la commande
    """
    if self.is_possible():
      self.traitee = True
      self.operateur = operateur
      for ref in list(self.contenu.keys()):
        ref.stock -= self.contenu[ref]

  def nb_total_coms():
    """
    Renvoie le nombre total de commandes
    Sortie : int
    """
    return len(Commande.commandes)
  
  def nb_non_traitee_coms():
    """
    Renvoie le nombre de commandes non traitées
    Sortie : int
    """
    nb = 0
    for com in list(Commande.commandes.values()):
      if com.traitee == False:
        nb += 1
    return nb
  
  def nb_traitee_coms():
    """
    Renvoie le nombre de commandes traitées
    Sortie : int
    """
    return Commande.nb_total_coms() - Commande.nb_non_traitee_coms()
  
  def nb_possible_coms():
    """
    Renvoie le nombre de commandes possibles
    Sortie : int
    """
    nb = 0
    for com in list(Commande.commandes.values()):
      if com.is_possible() and com.traitee == False:
        nb += 1
    return nb
  
  def nb_impossible_coms():
    """
    Renvoie le nombre de commandes impossibles à traiter
    Sortie : int
    """
    return Commande.nb_non_traitee_coms() - Commande.nb_possible_coms()
  
  def get_chiffre_affaire():
    """
    Renvoie le chiffre d'affaire fait par l'entreprise sur les commandes traitées
    Sortie : float
    """
    total_fait = 0
    total_non_fait = 0
    for com in list(Commande.commandes.values()):
      if com.traitee:
        total_fait += com.calcul_prix()
      else:
        total_non_fait += com.calcul_prix()
    return (round(total_fait, 2), round(total_non_fait, 2))
  
  def refs_plus_commandes():
    """
    Renvoie la référence l plus commandée
    Sortie : Instance de la classe Référence
    """
    refs = {}
    if len(Commande.commandes) != 0 and len(Reference.references) != 0:
      for com in list(Commande.commandes.values()):
        for ref in list(com.contenu.keys()):
          if ref in list(refs.keys()):
            refs[ref] += com.contenu[ref]
          else:
            refs[ref] = com.contenu[ref]
      return max(refs, key = refs.get).name
    else:
      return "/"
  
  
class Utilisateur():
  """
  Un utilisateur correspond à une personne physique utilisant l'application après s'être connecté. 
  L'ensemble des utilisateurs sont stockés dans un fichier CSV.
  """
  utilisateurs = {} # Dictionnaire des utilisateurs, dont les clés sont les noms d'utilisateurs et les valeurs les instances de la classe Utilisateur

  def __init__(self, username, name, password, admin = False):
    """
    Initialise l'objet utilisateur
    Entrées :
        - username : String - Nom d'utilisateur
        - name : String - Nom de l'utilisateur
        - password : String - Mot de passe
    """
    self.username = username
    self.name = name
    self.password = password
    self.admin = admin
    Utilisateur.utilisateurs[username] = self

  def __str__(self) -> str:
    """
    Renvoie la représentation complète de l'objet utilisateur
    Sortie : String
    """
    return f"Utilisateur : {self.username} | Nom : {self.name} | Mot de passe : {self.password}"
  
  def __repr__(self):
    """
    Renvoie la représentation rapide de l'objet utilisateur
    Sortie : String
    """
    return self.username
  
  def save():
    """
    Sauvegarde l'ensemble des utilisateurs dans un fichier CSV
    """
    with open("data/users.csv", "w+", encoding="UTF8", newline="") as f:
      writer = csv.writer(f, delimiter=",")
      for user in list(Utilisateur.utilisateurs.values()):
        writer.writerow([user.username, user.name, user.password, user.admin])

  def max_commandes():
    """
    Renvoie l'utilisateur ayant validé le plus de commandes
    Sortie : Instance de la classe Utilisateur
    """
    users = {}
    if len(Utilisateur.utilisateurs) != 0 and len(Commande.commandes) != 0:
      for com in list(Commande.commandes.values()):
        if com.traitee and com.operateur != "":
          if com.operateur in list(users.keys()):
            users[com.operateur] += 1
          else:
            users[com.operateur] = 1
      return max(users, key = users.get).name
    else:
      return "/"
  
class Box():
    """
    Un Box est un emplacement de stockage au sein de l'entrepôt. 
    Un box peut être vide ou contenir au maximum une référence. 
    L'ensemble des boxs sont sauvegardés dans un fichier CSV.
    """
    boxs = {}
    def __init__(self, ident, allee, num, x, y, stockes = None):
        """
        Initialise l'objet box
        Entrées :
            - ident : String - Identifiant du box
            - allee : String - Allée du box
            - num : String - Numéro du box dans l'allée
            - x : String - Coordonnée x du box
            - y : String - Coordonnée y du box
            - stockes : String - Identifiant de la référence stockée dans le box
        """
        self.id = ident
        self.allee = allee
        self.num = num
        if stockes == None:
          self.stockes = None
        else:
          self.stockes = Reference.references[stockes]
        self.x = float(x)
        self.y = float(y)
        Box.boxs[ident] = self

    def dico_co():
      """
      Renvoie un dictionnaire dont les clés sont les tuples coordonnées du box et les valeurs les instances de la classe Box
      Sortie : Dictionnaire
      """
      dic = {} 
      for box in list(Box.boxs.values()): 
        dic[(box.x, box.y)] = box
      return dic
    
    def __repr__(self):
      """
      Renvoie la représentation rapide de l'objet box
      Sortie : String
      """
      return self.id
    
    def __str__(self):
      """
      Renvoie la représentation complète de l'objet box
      Sortie : String
      """
      return f"Box : {self.id} | Allée : {self.allee} | Numéro : {self.num} | Coordonnées : ({self.x}, {self.y}) | Stocké : {self.stockes}"
    
    def save():
      """
      Sauvegarde l'ensemble des boxs dans un fichier CSV
      """
      with open("data/boxs.csv", "w+", encoding="UTF8", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        for box in list(Box.boxs.values()):
            if box.stockes != None:
              writer.writerow([str(box.id), str(box.allee), str(box.num), str(box.x), str(box.y), str(box.stockes.id)])
            else:
              writer.writerow([str(box.id), str(box.allee), str(box.num), str(box.x), str(box.y), "None"])

class Case():
  """
  Une case est une case de la grille de l'entrepôt. Elle corrspond à un couloir sur lequel on peut se déplacer. 
  Elle peut être connectée à d'autres cases et/ou à des boxs.
  """
  cases = {} # Dictionnaire des cases, dont les clés sont les tuples coordonnées et les valeurs les instances de la classe Case

  def __init__(self, x, y):
    """
    Initialise l'objet case
    Entrées :
        - x : int - Coordonnée x de la case
        - y : int - Coordonnée y de la case
    """
    self.x = x
    self.y = y
    self.ad = []
    self.boxs = []
    Case.cases[(x,y)] = self

  def __repr__(self):
    """
    Renvoie la représentation rapide de l'objet case
    Sortie : String
    """
    return f"({self.x} / {self.y})"
  
  def __str__(self):
    """
    Renvoie la représentation complète de l'objet case
    Sortie : String
    """
    return f"Case : ({self.x}, {self.y}) | Cases adjacentes : {self.ad} | Boxs : {self.boxs}"
  
  def trouver_voisins(self):
    """
    Trouve les cases adjacentes à la case
    """
    for co in [(self.x, self.y-Params.cote), (self.x, self.y+Params.cote), (self.x-Params.cote, self.y), (self.x+Params.cote, self.y)]: 
      autre = Case.cases.get(co, None)
      if autre != None:
        self.lien(autre)

  def lien(self, autre):
    """
    Crée un lien entre la case et une autre case en ajoutant l'autre case à la liste des cases adjacentes de la case
    Entrées :
        - autre : Case - Autre case à lier à la case
    """
    if autre != None:
      self.ad.append(autre)
      autre.ad.append(self)

  def trouver_boxs(self):
    """
    Trouve les boxs adjacents à la case. Les ajoute à la liste des boxs de la case.
    """
    for co in [(self.x, self.y-Params.cote), (self.x, self.y+Params.cote), (self.x-Params.cote, self.y), (self.x+Params.cote, self.y)]:
      box = Box.dico_co().get(co, None)
      if box != None:
        self.boxs.append(box)

  def dico_boxs_cases():
      """
      Renvoie un dictionnaire dont les clés sont les instances de la classe Box et les valeurs les instances de la classe Case
      Un box peut être présent dans plusieurs cases. Une case peut contenir plusieurs boxs.
      Sortie : Dictionnaire
      """
      dic = {}
      for case in list(Case.cases.values()):
        for box in case.boxs:
          if dic.get(box, None) == None:
            dic[box] = []
          dic[box].append(case)
      return dic
  
  def dico_coos_cases():
      """
      Renvoie un dictionnaire dont les clés sont les tuples coordonnées des cases et les valeurs les instances de la classe Case
      Sortie : Dictionnaire
      """
      dic = {}
      for case in list(Case.cases.values()):
        dic[(case.x, case.y)] = case
      return dic
  
  def distance_euclidienne(self, autre):
    """
    Renvoie la distance entre la case et une autre case
    Entrées :
        - autre : Case - Autre case
    Sortie : float
    """
    return (math.sqrt((self.x-autre.x)**2 + (self.y-autre.y)**2))

  def distance_manhattan(self, autre):
    """
    Renvoie la distance de Manhattan entre la case et une autre case
    Entrées :
        - autre : Case - Autre case
    Sortie : float
    """
    return (abs(self.x-autre.x) + abs(self.y-autre.y))