
from casque import Casque
from gestionCasques import GestionCasques
from solution import Solution
from marque import Marque
from ressources import Ressources


def display_welcome_message():
    print("Bienvenue dans l'application de gestion des solutions VR")

def main():
    display_welcome_message()
    GestionCasques()
    input("Appuyez sur Entrée pour fermer la fenêtre...")
    

if __name__ == "__main__":
    main()
    input("Appuyez sur Entrée pour fermer la fenêtre...")
    