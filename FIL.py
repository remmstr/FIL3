from casque import Casque
from gestionCasques import GestionCasques
from solution import Solution
from marque import Marque
from config import Config
import sys
import subprocess
import threading
import time
import traceback

# Fonction pour démarrer le suivi des périphériques
def track_devices(casques):
    while True:

        casques.refresh_casques()

        time.sleep(3)  # Ajout d'un délai pour éviter une boucle trop rapide

def display_menu():
    subprocess.run(["powershell", "-Command", "Clear-Host"])
    print("\n" + "="*40)
    print("          Menu Principal          ")
    print("="*40)
    print("1. Afficher les casques")
    print("2. Installer les APKs")
    print("3. Installer les solutions ")
    print("4. Archiver un casque (brancher un seul casque)")
    print("5. Configurer le wifi sur tous les casques (beta)")
    print("6. Quitter")
    print("="*40)
    print()

def main():
    try:
        casques = GestionCasques.getInstance()
        casques.refresh_casques()
        time.sleep(1)  # Ajout d'un délai pour éviter une boucle trop rapide
        # Démarrer le suivi des périphériques dans un thread séparé
        tracking_thread = threading.Thread(target=track_devices, args=(casques,))
        tracking_thread.start()

        while True:
            display_menu()
            try:
                casques.print()
            except Exception as e:
                print(f"Erreur lors de l'affichage des casques: {e}")
                traceback.print_exc()
            print("COMMENTAIRE: Veuillez relancer l'application en cas de rebranchements ")
            print()

            try:
                choix = input("Choisissez une option (1-6) : ")
            except EOFError:
                print("Entrée inattendue fermée. Terminaison du programme.")
                break
            except Exception as e:
                print(f"Erreur lors de la saisie de l'option: {e}")
                traceback.print_exc()
                continue

            subprocess.run(["powershell", "-Command", "Clear-Host"])

            if choix == '1':
                print("\n" + "-"*40)
                print("       Affichage des casques       ")
                print("-"*40)
                try:
                    casques.print()
                except Exception as e:
                    print(f"Erreur lors de l'affichage des casques: {e}")
                    traceback.print_exc()
            elif choix == '2':
                print("\n" + "-"*40)
                print("       Installation des APKs       ")
                print("-"*40)
                try:
                    casques.install_All_APK()
                except Exception as e:
                    print(f"Erreur lors de l'installation des APKs: {e}")
                    traceback.print_exc()
            elif choix == '3':
                print("\n" + "-"*40)
                print("       Installation des solutions       ")
                print("-"*40)
                try:
                    casques.install_All_Solution()
                except Exception as e:
                    print(f"Erreur lors de l'installation des solutions: {e}")
                    traceback.print_exc()
            elif choix == '4':
                print("\n" + "-"*40)
                print("           Archivage du casque         ")
                try:
                    casques.archivage()
                except Exception as e:
                    print(f"Erreur lors de l'archivage du casque: {e}")
                    traceback.print_exc()
                print("-"*40)   
            elif choix == '5':
                print("\n" + "-"*40)
                print("           Configuration du wifi         ")
                try:
                    casques.share_wifi_to_ALL_casque()
                except Exception as e:
                    print(f"Erreur lors de la configuration du wifi: {e}")
                    traceback.print_exc()
                print("-"*40)   
            elif choix == '6':
                print("\n" + "-"*40)
                print("           Quitter le menu         ")
                tracking_thread.join()  # Attend que le thread se termine proprement
                print("-"*40)
                break
            else:
                print("\n" + "-"*40)
                print("    Option invalide, veuillez réessayer")
                print("-"*40)

            input("[ Appuyez sur Entrée pour revenir au menu ]")

    except KeyboardInterrupt:
        print("Interruption de l'utilisateur. Fermeture de l'application...")
        tracking_thread.join()  # Attend que le thread se termine proprement
        sys.exit()
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    input("Appuyez sur Entrée pour fermer la fenêtre...")
