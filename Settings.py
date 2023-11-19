# coding=utf-8

class Params():
    """
    Classe comprenant les paramètres de l'application.
    Ces paramètres peuvent être modifiées par l'utilisateur.
    Ils sont de nature esthétique ou fonctionnelle.
    """
    # Préfixes des diffentes classes
    # La modification de ces paramètres nécessite une réinitialisation de l'application

    prefix_reference = "R-"
    prefix_commande = "C-"
    prefix_utilisateur = "U-"
    prefix_box = "B-"

    # Seuils d'alerte pour stock de références
    # Mettre à -1 pour désactiver

    alert_stock_1 = 10
    alert_stock_2 = 5
    alert_stock_3 = 0
    
    # Couleurs

    color_box = "darkgray"
    color_background = "lightgray"

    color_no_alert = "black"
    color_bg_no_alert = ""

    color_alert_stock_1 = "darkorange"
    color_bg_alert_stock_1 = ""

    color_alert_stock_2 = "red2"
    color_bg_alert_stock_2 = ""
    
    color_alert_stock_3 = "red4"
    color_bg_alert_stock_3 = "coral1"

    # Graphismes
    # En cas de modification de ces paramètres, il est nécessaire de reconfigurer l'entrepot immédiatement
    
    cote = 60
    nb_lignes = 10
    nb_colonnes = 19

    largeur_canevas = cote*nb_colonnes
    hauteur_canevas = cote*nb_lignes

    # Mode de calcul des chemins

    path_mode = "shortest" # Valeurs possibles: "fastest", "shortest", "lightest"

    # Vitesse de déplacement

    vitesse = 500 # En pixels par minute