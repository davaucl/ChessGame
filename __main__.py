
from pychecs2.echecs.partie import Partie
from pychecs2.interface.Interface import Fenetre

if __name__ == '__main__':
    # Création d'une instance de Partie.
    p = Partie()

    # Création et affichage d'une fenêtre (aucun lien avec la partie ci-haut).
    f = Fenetre(p)
    f.mainloop()
