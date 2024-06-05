
from solution import Solution
from marque import Marque
from ressources import Ressources
import subprocess
import os

class Casque:

    def __init__(self):
        self.numero = "NULL"
        self.marque = "NULL"
        self.modele = "NULL"
        self.JSON_path = "NULL"
        self.solutions_install = []
        self.solutions_pour_install = []
    
    def print(self):
        print(f"Numéro de série : {self.numero}")
        print(f"Modèle : {self.modele}")
        print(f"Marque : {self.marque}")
        print(f"JSON : {self.JSON_path}")
        # affiche toutes les solutions

    #le truc cool serait de faire venir ici l'instanciation des données pour + de logique 
    def init_info_casque(self):
        print("Initialisation des informations du casque")
        # Implémentation de l'initialisation des informations du casque
        pass


    def check_json_file(self):
        json_file_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/hardware.json"

        try:
            # Exécuter la commande adb shell ls pour lister les fichiers dans le répertoire spécifié
            output = subprocess.check_output(["adb", "-s", self.numero, "shell", "ls", json_file_path]).decode("utf-8")
            # Vérifier si le nom du fichier existe dans la sortie
            if json_file_path in output:
                self.JSON_path = os.path.dirname(json_file_path)
                return True
            else:
                self.JSON_path = "Fichier JSON inexistant"
                return False
        except subprocess.CalledProcessError as e:
            self.JSON_path = "Fichier JSON inexistant" # bizarre car pas une erreur
            return False

    def install_APK(self):
        print("Installation de l'APK")
        # Implémentation de l'installation de l'APK
        pass

    def uninstall_APK(self):
        print("Desinstallation de l'APK")
        # Implémentation de l'installation de l'APK
        pass

    def add_solution(self):
        print("Ajout d'une solution")
        # Implémentation de l'ajout d'une solution
        pass

    def add_all_solutions(self):
        print("Ajout de toutes les solutions")
        # Implémentation de l'ajout de toutes les solutions
        pass