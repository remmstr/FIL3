from casque import Casque
from gestionCasques import GestionCasques
from solution import Solution
from marque import Marque
from ressources import Ressources
import os

def display_menu():
    
    print("\n" + "="*30)
    print("          Menu Principal          ")
    print("="*30)
    print("1. Afficher les casques")
    print("2. Installer les APKs")
    print("3. Installer la solution 'Humour et Drague'")
    print("4. Quitter")
    print("="*30)


def main():
    try:
        print("------ Hello Nathalie ! Bienvenue dans l'application de gestion des solutions VR ------")
        casques = GestionCasques()

        while True:
            
            display_menu()
            print()
            print("REMARQUES:  " )
            print(" - Relancer le logiciel en cas de rebranchement des casques" )
            print(" - Un dock multi usb peut engendrer des erreurs")
            print(" - Si aucune solution n'a jamais été installé sur le casque, cela peut malfonctionné, je conseille de le débranché puis rebranché après installation de l'apk")
            print(" - Il faut que la licence et l'ajout de la solution soit bien associé au casque avant l'utilisation du logiciel sinon ça ne marche pas  ")
            print(" - Il est probable qu'une mise à jour partiel de la solution reste à faire dans le casque malgré le téléversement réalisé ")
            print(" - Sur certain casque le téléversement de la solution ne fonctionnait pas :/, il faut donc le faire dans le casque" )
            print()
            choix = input("Choisissez une option (1-4) : (Prévu pour faire dans l'ordre) ")


            if choix == '1':
                print("\n" + "-"*30)
                print("       Affichage des casques       ")
                print("-"*30)
                casques.print()
            elif choix == '2':
                print("\n" + "-"*30)
                print("       Installation des APKs       ")
                print("-"*30)
                casques.install_All_APK()
            elif choix == '3':
                print("\n" + "-"*30)
                print("Installation de la solution 'Humour et Drague'")
                print("-"*30)
                casques.install_All_Solution()
            elif choix == '4':
                print("\n" + "-"*30)
                print("           Quitter le menu         ")
                os.exit()  # Fermer le programme
                print("-"*30)   
            else:
                print("\n" + "-"*30)
                print("    Option invalide, veuillez réessayer")
                print("-"*30)

    except Exception as e:
        print(f"Une erreur est survenue: {e}")

if __name__ == "__main__":
    main()
    input("Appuyez sur Entrée pour fermer la fenêtre...")
