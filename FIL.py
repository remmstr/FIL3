from casque import Casque
from gestionCasques import GestionCasques
from solution import Solution
from marque import Marque
from config import Config
import sys

import subprocess
import threading
import time


# Fonction pour démarrer le suivi des périphériques MAIS JE SOUHAITERAIS FAIRE DES INTERRUPTIONS JE TROUVE PAS OU CETTE PARTIE
def track_devices(casques):
    while True :
        casques.refresh_casques()
        time.sleep(0.5)

            
def display_menu():
    subprocess.run(["powershell", "-Command", "Clear-Host"])
    print("\n" + "="*40)
    print("          Menu Principal          ")
    print("="*40)
    print("1. Afficher les casques")
    print("2. Installer les APKs")
    print("3. Installer les solutions ")
    print("4. Archiver un casque (brancher un seul casque)")
    print("5. Quitter")
    print("="*40)
    print()
    


# Fonction principale
def main():
    try:
        casques = GestionCasques.getInstance()
        casques.refresh_casques()

        # Démarrer le suivi des périphériques dans un thread séparé
        #tracking_thread = threading.Thread(target=track_devices, args=(casques,))
        #tracking_thread.daemon = True
        #tracking_thread.start()

        while True:
            
            display_menu()
            print("COMMENTAIRE: Veuillez relancer l'application en cas de rebranchements ")
            print()
            choix = input("Choisissez une option (1-5) : ")

            subprocess.run(["powershell", "-Command", "Clear-Host"])

            if choix == '1':
                print("\n" + "-"*40)
                print("       Affichage des casques       ")
                print("-"*40)
                casques.print()
            elif choix == '2':
                print("\n" + "-"*40)
                print("       Installation des APKs       ")
                print("-"*40)
                casques.install_All_APK()
            elif choix == '3':
                print("\n" + "-"*40)
                print("       Installation des solutions       ")
                print("-"*40)
                casques.install_All_Solution()
            elif choix == '4':
                print("\n" + "-"*40)
                print("           Archivage du casque         ")
                casques.archivage()
                print("-"*40)   
            elif choix == '5':
                print("\n" + "-"*40)
                print("           Quitter le menu         ")
                sys.exit()  # Fermer le programme
                print("-"*40)   
            else:
                print("\n" + "-"*40)
                print("    Option invalide, veuillez réessayer")
                print("-"*40)

            input("[ Appuyez sur Entrée pour revenir au menu ]")

    except Exception as e:
        print(f"Une erreur est survenue: {e}")

if __name__ == "__main__":
    main()
    input("Appuyez sur Entrée pour fermer la fenêtre...")