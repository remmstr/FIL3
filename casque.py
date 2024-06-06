from solution import Solution
from marque import Marque
from ressources import Ressources
import subprocess
import os

class Casque:

    def __init__(self):
        self.device = str
        self.numero = ""
        self.marque = Marque()
        self.modele = ""
        self.version_apk = ""
        self.JSON_path = "NULL"
        self.solutions_install = []
        self.solutions_pour_install = []
    
    def print(self):
        print(f"| Numéro de série : {self.numero}")
        print(f"| Modèle : {self.modele}")
        print(f"| Marque : {self.marque.nom}")
        print(f"|     APK de la marque : {self.marque.version_apk}")
        print(f"|     Chemin de l'APK de la marque : {self.marque.APK_path}")
        print(f"| APK du casque : {self.version_apk}")
        print(f"| JSON : {self.JSON_path}")
        # affiche toutes les solutions à faire plus tard

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
        print("----->>>> Installation de l'APK")
        #self.uninstall_APK()  # Désinstaller l'APK avant l'installation
        self.print()

        # Définir les chemins vers adb et le nom de package
        adb_exe = "./platform-tools/adb.exe"
        # Package name de l'application
        package_name = "com.VRAI_Studio.Reverto"

        # Commandes pour accorder les permissions
        commands = [
            [adb_exe, "-s", self.numero, "shell", "pm", "grant", package_name, "android.permission.ACCESS_FINE_LOCATION"],
            [adb_exe, "-s", self.numero, "shell", "pm", "grant", package_name, "android.permission.READ_EXTERNAL_STORAGE"],
            [adb_exe, "-s", self.numero, "shell", "pm", "grant", package_name, "android.permission.WRITE_EXTERNAL_STORAGE"]
        ]

        # Exécution des commandes
        for command in commands:
            try:
                subprocess.run(command, check=True)
                print(f"Permission accordée avec succès")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'accord de la permission : {e}")
 
        try:
            # Exécuter la commande adb pour installer l'APK
            subprocess.run([adb_exe, "-s", self.numero, "install", self.marque.APK_path], check=True)
            print("Installation de l'APK réussie.")
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'installation de l'APK : {e}")

        
        
        # Commandes pour accorder les permissions
        commands = [
            [adb_exe, "-s", self.numero, "shell", "pm", "grant", package_name, "android.permission.ACCESS_FINE_LOCATION"],
            [adb_exe, "-s", self.numero, "shell", "pm", "grant", package_name, "android.permission.READ_EXTERNAL_STORAGE"],
            [adb_exe, "-s", self.numero, "shell", "pm", "grant", package_name, "android.permission.WRITE_EXTERNAL_STORAGE"]
        ]

        # Exécution des commandes
        for command in commands:
            try:
                subprocess.run(command, check=True)
                print(f"Permission accordée avec succès")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'accord de la permission : {e}")
 


        #self.device.install(self.marque.APK_path)
        print("-----------Fin de l'installation-----------")
        

    def uninstall_APK(self):
        print("----->>>> Désinstallation de l'APK")
        self.print()

        # Définir les chemins vers adb et le nom de package
        adb_exe = "./platform-tools/adb.exe"
        # Package name de l'application
        package_name = "com.VRAI_Studio.Reverto"

        try:
            # Exécuter la commande adb pour désinstaller l'APK
            subprocess.run([adb_exe, "-s", self.numero, "uninstall", package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Désinstallation de l'APK réussie.")
        except subprocess.CalledProcessError as e:
            if "Unknown package" in str(e):
                print("L'application n'était pas installée.")
            else:
                print(f"Une erreur est survenue lors de la désinstallation de l'APK : {e}")

        print("-----------Fin de la désinstallation-----------")


    def add_solution(self):
        print("----->>>>Téléversement de la solution")
        self.print()
        print("Ajout d'une solution... cela peut prendre quelques minutes")
        try:
            result = subprocess.run(
                ["adb", "-s", self.numero, "push", "./Banque_de_solutions/upload", "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded/upload"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print("Téléversement réussi.")
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors du téléversement de la solution : {e}")
            print(e.stderr.decode("utf-8"))
        print("-----------Fin du téléversement-----------")
