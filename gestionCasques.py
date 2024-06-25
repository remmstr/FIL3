from ppadb.client import Client as AdbClient
from casque import Casque
import subprocess
import os
import sys

# Fonction pour obtenir le chemin absolu du fichier/dossier
def resource_path(relative_path):
    """Obtenir le chemin absolu du fichier, fonctionne pour dev et pour PyInstaller"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    
 

# le mieux serait de le metttre dans une classe GestionAdb dont heriterai GestionCasques
def check_adb_connection():
    try:
        adb_path = resource_path("platform-tools")
        os.environ["PATH"] += os.pathsep + adb_path
        output = subprocess.check_output(["adb", "start-server"])
        print(output.decode('utf-8'))
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur ADB : {e}")
        return False
    return True

from ppadb.client import Client as AdbClient

class GestionCasques:

    client = AdbClient(host="127.0.0.1", port=5037)
    
    def __init__(self):
        check_adb_connection()
        self.liste_casques = []

        self.refresh_casques()
            
    def refresh_casques(self):
        # Effacez d'abord la liste actuelle pour éviter les doublons
        self.liste_casques.clear()

        # Réinitialisez la liste des casques avec les nouvelles informations
        devices = self.client.devices()  # Supposons qu'il existe une fonction pour obtenir les périphériques connectés

        for device in devices:
            nouveau_casque = Casque()
            nouveau_casque.refresh_casque(device)
            self.liste_casques.append(nouveau_casque)

    
    def print(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print()
            print(f"Casque #{i}:")
            casque.print()
            print("-" * 20)
    

    def install_All_APK(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print()
            print(f"Casque #{i}:")
            casque.install_APK()
            print("-" * 20)

    def install_All_Solution(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print()
            print(f"Casque #{i}:")
            casque.add_solution()
            print("-" * 20)

    def archivage(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print()
            print(f"Casque #{1}:")
            casque.archivage_casque()
            print("-" * 20)

    pass