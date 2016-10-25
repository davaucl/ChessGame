from tkinter import Tk, Canvas, Label, NSEW, Button, E, W, Frame, filedialog, Text, WORD, Scrollbar, VERTICAL, CURRENT
from tkinter import END, OptionMenu, StringVar
import pickle

from pychecs2.echecs.piece import Pion, Tour, Fou, Cavalier, Dame, Roi, UTILISER_UNICODE

from pychecs2.echecs.echiquier import Echiquier, reclic_sur_piece, deplacement_invalide

class CanvasEchiquier(Canvas):
    """Classe héritant d'un Canvas, et affichant un échiquier qui se redimensionne automatique lorsque
    la fenêtre est étirée.

    """
    def __init__(self, parent, n_pixels_par_case, partie):

        self.n_lignes = 8
        self.n_colonnes = 8


        self.chiffres_rangees = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.lettres_colonnes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']


        self.n_pixels_par_case = n_pixels_par_case


        super().__init__(parent, width=self.n_lignes * n_pixels_par_case,
                         height=self.n_colonnes * self.n_pixels_par_case)


        self.pieces = partie.echiquier.dictionnaire_pieces


        self.bind('<Configure>', self.redimensionner)

        self.partie = partie

    def dessiner_cases(self, position_selectionnee):
        """Méthode qui dessine les cases de l'échiquier.

        """
        if position_selectionnee != None:
            ligne_selectionnee = 8 - int(position_selectionnee[1]) # car l'ordre des # de colonnes est inversé
            colonne_selectionnee = self.lettres_colonnes.index(position_selectionnee[0])
        else:
            ligne_selectionnee, colonne_selectionnee = 'N/A', 'N/A'

        for i in range(self.n_lignes):
            for j in range(self.n_colonnes):
                debut_ligne = i * self.n_pixels_par_case
                fin_ligne = debut_ligne + self.n_pixels_par_case
                debut_colonne = j * self.n_pixels_par_case
                fin_colonne = debut_colonne + self.n_pixels_par_case

                # On détermine la couleur.
                if [i,j] == [ligne_selectionnee, colonne_selectionnee]:
                    couleur = 'yellow'
                elif (i + j) % 2 == 0:
                    couleur = 'white'
                else:
                    couleur = 'gray'

                # Détermine les déplacements possibles
                if position_selectionnee != None:
                    position = self.lettres_colonnes[j] + str(8-i)
                    if self.partie.echiquier.deplacement_est_valide(position_selectionnee, position):
                        couleur = 'green'
                        if self.partie.echiquier.recuperer_piece_a_position(position) != None:
                            couleur = 'red'


                self.create_rectangle(debut_colonne, debut_ligne, fin_colonne, fin_ligne, fill=couleur, tags='case')

    def dessiner_pieces(self):


        for position, piece in self.pieces.items():
            coordonnee_y = (self.n_lignes - self.chiffres_rangees.index(position[1]) - 1) * self.n_pixels_par_case + self.n_pixels_par_case // 2
            coordonnee_x = self.lettres_colonnes.index(position[0]) * self.n_pixels_par_case + self.n_pixels_par_case // 2
            self.create_text(coordonnee_x, coordonnee_y, text=repr(piece),
                             font=('Deja Vu', self.n_pixels_par_case//2), tags='piece')

    def redimensionner(self, event):
        nouvelle_taille = min(event.width, event.height)


        self.n_pixels_par_case = nouvelle_taille // self.n_lignes

        self.delete('case')
        self.dessiner_cases(None)

        self.delete('piece')
        self.dessiner_pieces()

class Fenetre(Tk):
    def __init__(self, partie):
        super().__init__()

        # Nom de la fenêtre.
        self.title("Échiquier")

        # La position sélectionnée.
        self.position_selectionnee = None

        # Truc pour le redimensionnement automatique des éléments de la fenêtre.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Création du canvas échiquier.
        self.canvas_echiquier = CanvasEchiquier(self, 60, partie)
        self.canvas_echiquier.grid(sticky=NSEW)

        # Ajout d'une étiquette d'information.
        self.messages = Label(self)
        self.messages.grid()

        # Création d'un cadre a droite de l'échiquier.
        self.cadre_droite = Frame(self)
        self.cadre_droite.grid(row=0, column=1)

        # Création des étiquettes pour afficher les pièces perdues
        self.piece_perdue = Frame(self.cadre_droite)
        self.piece_perdue.grid(row=0, column=0)
        Label(self.piece_perdue, text="Piece Perdu:", font=("DejaVu Sans", 12)).grid(row=0)
        Label(self.piece_perdue, text="Noire:", font=("DejaVu Sans", 12)).grid(row=1, column=0)
        Label(self.piece_perdue, text="Blanc:", font=("DejaVu Sans", 12)).grid(row=2, column=0)
        Label(self.piece_perdue, text="", font=("DejaVu", 14)).grid(row=1, column=1)
        Label(self.piece_perdue, text="", font=("DejaVu", 14)).grid(row=2, column=1)

        # Création des étiquettes pour afficher qui joue
        self.tour = Label(self.cadre_droite, text="Tour:\nBlanc", font=("DejaVu Sans", 16))
        self.tour.grid(row=1, column=0, padx=10, pady=10)


        cadre_deplacement = Frame(self.cadre_droite)
        cadre_deplacement.grid(row=2, column=0, padx=10, pady=10)

        Label(cadre_deplacement, text="Dernier déplacements", font=("DejaVu Sans", 12)).grid(row=0, column=0)
        self.deplacements = Text(cadre_deplacement, height=5, width=15, wrap=WORD, font=("DejaVu Sans", 12))
        self.deplacements.grid(sticky=NSEW)

        barre_defilement = Scrollbar(cadre_deplacement, orient=VERTICAL)
        barre_defilement.config(command=self.deplacements.yview)
        self.deplacements.config(yscrollcommand=barre_defilement.set)
        barre_defilement.grid(row=1, column=1, sticky=NSEW)


        self.sauvegarde = Button(self.cadre_droite, text="Annuler dernier deplacement", font=("DejaVu Sans", 10), command=self.annuler_deplacement_avec_message)
        self.sauvegarde.grid(padx=5, pady=5, sticky=E+W)


        self.sauvegarde = Button(self.cadre_droite, text="Sauvegarde", font=("DejaVu Sans", 10), command=self.sauvegarder_partie)
        self.sauvegarde.grid(padx=5, pady=5, sticky=E+W)


        self.sauvegarde = Button(self.cadre_droite, text="Charger", font=("DejaVu Sans", 10), command=self.charger_partie)
        self.sauvegarde.grid(padx=5, pady=5, sticky=E+W)


        self.sauvegarde = Button(self.cadre_droite, text="Nouvelle Partie", font=("DejaVu Sans", 10), command=self.nouvelle_partie)
        self.sauvegarde.grid(padx=5, pady=5, sticky=E+W)


        self.couleur_background_defaut = self.cget("bg")


        self.couleur_theme = StringVar(self.cadre_droite)
        self.couleur_theme.set('Thème gris (défaut)')
        self.drop = OptionMenu(self.cadre_droite,self.couleur_theme,'Thème jaune','Thème bleu','Thème gris (défaut)', command=self.changer_theme)
        self.drop.grid(padx=5, pady=5, sticky=W)

        self.fin_partie_echec_et_mat = False

        
        self.canvas_echiquier.bind('<Button-1>', self.selectionner)

    def changer_theme(self, couleur):
        if couleur == 'Thème jaune':
            couleur = 'LightYellow'
        elif couleur == 'Thème bleu':
            couleur = 'LightBlue'
        else:
            couleur = self.couleur_background_defaut

        super().configure(background=couleur)
        self.cadre_droite.configure(background=couleur)
        self.piece_perdue.configure(background=couleur)

    def selectionner(self, event):

        echec_au_roi = False
        if not self.canvas_echiquier.partie.partie_terminee() and not self.fin_partie_echec_et_mat:

            # On trouve le numéro de ligne/colonne en divisant les positions en y/x par le nombre de pixels par case.
            ligne = event.y // self.canvas_echiquier.n_pixels_par_case
            colonne = event.x // self.canvas_echiquier.n_pixels_par_case
            position = "{}{}".format(self.canvas_echiquier.lettres_colonnes[colonne], int(self.canvas_echiquier.chiffres_rangees[self.canvas_echiquier.n_lignes - ligne - 1]))

            #si une pièce est déjà sélectionnée, on attend sa position cible
            if self.position_selectionnee != None:

                try:

                    self.canvas_echiquier.partie.echiquier.deplacer(self.position_selectionnee, position) # les exceptions sont situées dans cette fonction

                    if self.verifier_echec_au_roi(self.canvas_echiquier.partie.joueur_actif):
                        self.annuler_deplacement_sans_message()
                        self.messages['foreground'] = 'red'
                        self.messages['text'] = 'Déplacement invalide; Roi en position échec.'
                        echec_au_roi = True

                    self.canvas_echiquier.dessiner_cases(None)
                    self.canvas_echiquier.dessiner_pieces()
                    if not echec_au_roi:
                        self.messages['foreground'] = 'black'
                        self.messages['text'] = 'Déplacement effectué de {} à {}.'.format(self.position_selectionnee, position)

                    self.canvas_echiquier.partie.joueur_suivant()
                    echec_au_roi = self.verifier_echec_au_roi(self.canvas_echiquier.partie.joueur_actif)
                    if echec_au_roi != False:
                        if self.verifier_echec_et_mat(echec_au_roi, self.canvas_echiquier.partie.joueur_actif):
                            self.messages['foreground'] = 'black'
                            self.fin_partie_echec_et_mat = True
                            self.canvas_echiquier.partie.joueur_suivant()
                            gagnant_partie = self.canvas_echiquier.partie.joueur_actif
                            self.messages['text'] = 'Échec et mat; félicitations au joueur {}'.format(gagnant_partie)
                            self.canvas_echiquier.partie.joueur_suivant()

                    self.sauvegarder_deplacement(self.position_selectionnee, position)

                    if self.canvas_echiquier.partie.echiquier.deplacements[-1] != None:
                        self.update_piece_perdu()

                    self.tour['text'] = "Tour:\n{}".format(self.canvas_echiquier.partie.joueur_actif.title())

                    self.position_selectionnee = None

                except reclic_sur_piece: # si le joueur reclique sur sa piece, on désélectionne la pièce

                    self.position_selectionnee = None
                    self.canvas_echiquier.dessiner_cases(self.position_selectionnee)
                    self.canvas_echiquier.dessiner_pieces()

                except deplacement_invalide:

                    try:


                        assert self.canvas_echiquier.pieces[position].couleur == self.canvas_echiquier.partie.joueur_actif
                        self.position_selectionnee = position
                        piece = self.canvas_echiquier.pieces[position]

                        self.messages['foreground'] = 'black'
                        self.messages['text'] = 'Pièce sélectionnée : {} à la position {}.'.format(piece, self.position_selectionnee)
                        self.canvas_echiquier.dessiner_cases(self.position_selectionnee)
                        self.canvas_echiquier.dessiner_pieces()

                    except (AssertionError, KeyError):

                         self.messages['foreground'] = 'red'
                         self.messages['text'] = 'Veuillez sélectionner un déplacement valide'


            else:

                try:

                    piece = self.canvas_echiquier.pieces[position]
                    assert piece.couleur == self.canvas_echiquier.partie.joueur_actif
                    self.position_selectionnee = position

                    self.messages['foreground'] = 'black'
                    self.messages['text'] = 'Pièce sélectionnée : {} à la position {}.'.format(piece, self.position_selectionnee)
                    self.canvas_echiquier.dessiner_cases(self.position_selectionnee) # on redessine les cases pour visualiser la selection
                    self.canvas_echiquier.dessiner_pieces()

                except KeyError: # s'il n'y a pas de piece à l'endroit sélectionné

                    self.messages['foreground'] = 'red'
                    self.messages['text'] = 'Erreur: Aucune pièce à cet endroit.'

                except AssertionError: # si ce n'est pas le tour du joueur de la couleur de la pièce sélectionnée

                    self.messages['foreground'] = 'red'
                    self.messages['text'] = 'C\'est au tour du joueur {}.'.format(self.canvas_echiquier.partie.joueur_actif)

    def verifier_echec_au_roi(self, couleur):

        deplacements = {}
        echec = {}
        dictionnaire_pieces = self.canvas_echiquier.partie.echiquier.dictionnaire_pieces

        for position_source, piece in dictionnaire_pieces.items():
            if isinstance(piece, Roi) and piece.couleur == couleur:
                position_roi = position_source
            elif piece.couleur != couleur:
                deplacement_piece = self.deplacement_possible(position_source, piece)
                if deplacement_piece != None:
                    deplacements[position_source] = deplacement_piece

        for position_source, deplacement_possible in deplacements.items():
            for position in deplacement_possible:
                if position == position_roi:
                    echec[position_source] = deplacement_possible

        if len(echec) == 0:
            return False
        else:
            self.messages['foreground'] = 'red'
            self.messages['text'] = 'Échec au Roi'
            return echec

    def verifier_echec_et_mat(self, echecs, couleur):

        positions_echec = []
        deplacements_piece = {}
        dictionnaire_pieces = self.canvas_echiquier.partie.echiquier.dictionnaire_pieces

        # on trouve la position du roi
        for position_source, piece in dictionnaire_pieces.items():
            if isinstance(piece, Roi) and piece.couleur == couleur:
                position_roi = position_source
                roi = piece

        for echec in echecs.values():
            positions_echec = positions_echec + echec

        # déplacements possibles du roi
        deplacement_roi = self.deplacement_possible(position_roi, roi)
        for deplacement in deplacement_roi:
            if deplacement not in positions_echec:
                return False

        # si une seule pièce met en échec, vérifie si on peut la manger
        if len(echecs) == 1:
            for echec in echecs.keys():
                position_piece_echec = echec

            for position_source, piece in dictionnaire_pieces.items():
                if isinstance(piece, Roi) == False and piece.couleur == couleur:
                    deplacement = self.deplacement_possible(position_source, piece)
                    if deplacement != None:
                        if position_piece_echec in deplacement:
                            return False
                        else:
                            deplacements_piece[position_source] = deplacement

        # On continue la recherche de pour l'échec et mat
        # on regarde si les déplacements possibles des pièces permettent de protéger le Roi
        for position_source, deplacements in deplacements_piece.items():
            for deplacement in deplacements:
                self.canvas_echiquier.partie.echiquier.dictionnaire_pieces[deplacement] = self.canvas_echiquier.partie.echiquier.recuperer_piece_a_position(position_source)
                if self.verifier_echec_au_roi(couleur) == False:
                    del self.canvas_echiquier.partie.echiquier.dictionnaire_pieces[deplacement]
                    return False

                del self.canvas_echiquier.partie.echiquier.dictionnaire_pieces[deplacement]

        # Aucune solution possible
        # échec et mat
        return True

    def deplacement_possible(self, position_source, piece):

        deplacements = []
        for colonne in self.canvas_echiquier.lettres_colonnes:
            for rangee in self.canvas_echiquier.chiffres_rangees:
                if self.canvas_echiquier.partie.echiquier.deplacement_est_valide(position_source, colonne + rangee):
                    deplacements.append(colonne + rangee)

        if len(deplacements) == 0:
            return None
        else:
            return deplacements

    def verifier_si_partie_terminee(self):
        gagnant_partie = self.canvas_echiquier.partie.determiner_gagnant()
        if gagnant_partie != 'aucun':
                self.messages['foreground'] = 'black'
                self.messages['text'] = 'La partie est terminée; félicitations au joueur {}.'.format(gagnant_partie)

    def sauvegarder_partie(self):
        nom_fichier_sortie = filedialog.asksaveasfilename(title='Copy', filetypes=[('txt', '*txt')])
        if nom_fichier_sortie == '':
            return None

        ma_chaine = nom_fichier_sortie.split('.')
        if len(ma_chaine) > 1:
            self.messages['foreground'] = 'red'
            self.messages['text'] = 'Partie non sauvegarder, veiller entrer un extension valide.'
            return None
        if len(ma_chaine) == 1:
            nom_fichier_sortie += '.txt'
        elif ma_chaine[1] != '.txt':
            nom_fichier_sortie = ma_chaine[0] + '.txt'

        fichier_sortie = open(nom_fichier_sortie, 'w')

        fichier_sortie.write('joueur_actif:{}\n\n'.format(self.canvas_echiquier.partie.joueur_actif))
        fichier_sortie.write('pieces:{}\n')

        pieces = self.canvas_echiquier.pieces
        for cle in pieces:
            fichier_sortie.write('{}:{}:{}\n'.format(cle, self.canvas_echiquier.pieces[cle].__class__.__name__, pieces[cle].couleur))

        fichier_sortie.write('\ndeplacements:{}\n')

        deplacements = self.canvas_echiquier.partie.echiquier.deplacements
        for index, value in enumerate(deplacements):
            if value[3].__class__.__name__ == 'NoneType':
                value3 = None
            else:
                value3 = value[3].__class__.__name__

            fichier_sortie.write('{}:{}:{}:{}:{}\n'.format(index + 1, value[0],value[1], value[2], value3))

        fichier_sortie.close()

    def charger_partie(self):
        nom_fichier_entré = filedialog.askopenfilename(title='Copy', filetypes=[('txt', '*txt')])

        if nom_fichier_entré == '':
            return None

        fichier_entré = open(nom_fichier_entré, 'r')

        self.canvas_echiquier.partie.echiquier.initialiser_echiquier_depart
        self.fin_partie_echec_et_mat = False

        ma_chaine = fichier_entré.readline()
        ma_chaine = ma_chaine[:-1].split(':')
        self.canvas_echiquier.partie.joueur_actif = ma_chaine[1]

        ma_chaine = fichier_entré.readlines(2)
        ma_chaine = fichier_entré.readline()

        pieces = {}

        while ma_chaine != '\n':
            position, piece, couleur = ma_chaine[:-1].split(':')
            if piece == "Roi":
                pieces[position] = Roi(couleur)
            elif piece == "Dame":
                pieces[position] = Dame(couleur)
            elif piece == "Cavalier":
                pieces[position] = Cavalier(couleur)
            elif piece == "Fou":
                pieces[position] = Fou(couleur)
            elif piece == "Tour":
                pieces[position] = Tour(couleur)
            elif piece == "Pion":
                pieces[position] = Pion(couleur)

            ma_chaine = fichier_entré.readline()

        self.canvas_echiquier.partie.echiquier.dictionnaire_pieces = pieces
        self.canvas_echiquier.pieces = pieces

        ma_chaine = fichier_entré.readline()
        ma_chaine = fichier_entré.readline()
        self.deplacements.delete('1.0', END)
        self.canvas_echiquier.partie.echiquier.deplacements = []

        while ma_chaine != '':
            index, couleur, position1, position2, perdue = ma_chaine[:-1].split(':')

            if couleur == 'blanc':
                couleur2 = 'noir'
            else:
                couleur2 = 'blanc'

            if perdue == "Roi":
                perdue = Roi(couleur2)
            elif perdue == "Dame":
                perdue = Dame(couleur2)
            elif perdue == "Cavalier":
                perdue = Cavalier(couleur2)
            elif perdue == "Fou":
                perdue = Fou(couleur2)
            elif perdue == "Tour":
                perdue = Tour(couleur2)
            elif perdue == "Pion":
                perdue = Pion(couleur2)
            else:
                perdue = None

            self.canvas_echiquier.partie.echiquier.deplacements.append([couleur, position1, position2, perdue])
            texte_cible = "{}. {}: {} - {}\n".format(index, couleur, position1, position2)
            self.deplacements.insert('1.0', texte_cible)
            ma_chaine = fichier_entré.readline()


        self.messages['foreground'] = 'black'
        self.messages['text'] = 'C\'est au tour du joueur {}.'.format(self.canvas_echiquier.partie.joueur_actif)

        self.canvas_echiquier.dessiner_cases(None)
        self.canvas_echiquier.delete('piece')
        self.canvas_echiquier.dessiner_pieces()
        self.update_piece_perdu()

        fichier_entré.close()
        self.tour['text'] = "Tour:\n{}".format(self.canvas_echiquier.partie.joueur_actif.title())

    def nouvelle_partie(self):
        self.canvas_echiquier.partie.echiquier.initialiser_echiquier_depart()
        self.canvas_echiquier.pieces = self.canvas_echiquier.partie.echiquier.dictionnaire_pieces

        self.canvas_echiquier.partie.joueur_actif = 'blanc'
        self.deplacements.delete('1.0', END)
        self.tour['text'] = "Tour:\n{}".format(self.canvas_echiquier.partie.joueur_actif.title())

        self.canvas_echiquier.delete('piece')
        self.canvas_echiquier.dessiner_pieces()

        self.fin_partie_echec_et_mat = False
        self.messages['foreground'] = 'black'
        self.messages['text'] = 'C\'est au tour du joueur {}.'.format(self.canvas_echiquier.partie.joueur_actif)


    def sauvegarder_deplacement(self, position_selectionnee, position):
        mouvement_numero = len(self.canvas_echiquier.partie.echiquier.deplacements)

        texte_cible = "{}. {}: {} - {}\n".format(mouvement_numero, self.canvas_echiquier.partie.joueur_actif, position_selectionnee, position)
        self.deplacements.insert('1.0', texte_cible)

    def annuler_deplacement_sans_message(self):

        self.fin_partie_echec_et_mat = False

        self.dictionnaire_pieces = self.canvas_echiquier.partie.echiquier.dictionnaire_pieces
        self.liste_deplacements = self.canvas_echiquier.partie.echiquier.deplacements

        dernier_deplacement = self.liste_deplacements[-1]

        position_initiale = dernier_deplacement[1]
        position_finale = dernier_deplacement[2]
        piece_mangee = dernier_deplacement[3]

        self.dictionnaire_pieces[position_initiale] = self.dictionnaire_pieces[position_finale]
        if piece_mangee == None:
            del self.dictionnaire_pieces[position_finale]
        else:
            self.dictionnaire_pieces[position_finale] = piece_mangee

        del(self.liste_deplacements[-1])
        self.canvas_echiquier.partie.joueur_suivant()
        self.tour['text'] = "Tour:\n{}".format(self.canvas_echiquier.partie.joueur_actif.title())
        self.deplacements.delete('1.0', '2.0')

        self.canvas_echiquier.delete('piece')
        self.canvas_echiquier.dessiner_pieces()
        self.update_piece_perdu()

    def annuler_deplacement_avec_message(self):

        self.annuler_deplacement_sans_message()

        self.messages['foreground'] = 'black'
        self.messages['text'] = 'C\'est au tour du joueur {}.'.format(self.canvas_echiquier.partie.joueur_actif)

    def update_piece_perdu(self):

        caracteres_pieces = {'PB': '\u2659',
                             'PN': '\u265f',
                             'TB': '\u2656',
                             'TN': '\u265c',
                             'CB': '\u2658',
                             'CN': '\u265e',
                             'FB': '\u2657',
                             'FN': '\u265d',
                             'RB': '\u2654',
                             'RN': '\u265a',
                             'DB': '\u2655',
                             'DN': '\u265b'
                             }
        piece_blanc = ''
        piece_noir = ''

        for deplacement in self.canvas_echiquier.partie.echiquier.deplacements:
            if deplacement[3] != None:
                if deplacement[3].couleur == 'noir':
                    piece = deplacement[3].__class__.__name__
                    piece = str.upper(piece[:1]) + 'N'
                    piece_blanc = piece_blanc + ' ' + caracteres_pieces[piece]
                if deplacement[3].couleur == 'blanc':
                    piece = deplacement[3].__class__.__name__
                    piece = str.upper(piece[:1]) + 'B'
                    piece_noir = piece_noir + ' ' + caracteres_pieces[piece]

        Label(self.piece_perdue, text=piece_noir + ' ', font=("DejaVu", 14)).grid(row=1, column=1)
        Label(self.piece_perdue, text=piece_blanc + ' ', font=("DejaVu", 14)).grid(row=2, column=1)
