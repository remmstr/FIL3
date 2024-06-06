from casque import Casque
from gestionCasques import GestionCasques
from solution import Solution
from marque import Marque
from ressources import Ressources

def display_welcome_message():
    print("------ Hello Nathalie ! Bienvenue dans l'application de gestion des solutions VR ------")

def main():
    try:
        display_welcome_message()
        casques = GestionCasques()
        casques.print()
        casques.install_All_APK()
        casques.install_All_Solution()

    except Exception as e:
        print(f"Une erreur est survenue: {e}")

if __name__ == "__main__":
    main()
    input("Appuyez sur Entrée pour fermer la fenêtre...")
