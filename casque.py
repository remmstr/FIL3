from solution import Solution
from marque import Marque
from config import Config
import subprocess
import os
import re
import sys
    

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
        self.config = Config()
        
    def refresh_casque(self, device):
        self.device = device
        self.numero = self.device.get_serial_no().strip()
        self.marque.setNom(self.device.shell("getprop ro.product.manufacturer").strip())
        self.modele = self.device.shell("getprop ro.product.model").strip()
        self.version_apk = self.get_installed_apk_version()
        self.check_json_file()
        self.solutions_install = []
        self.solutions_pour_install = []
       

    def print(self):
        BLUE = self.config.BLUE
        RESET = self.config.RESET

        print(BLUE + f"| Numéro de série : {self.numero}" + RESET)
        print(BLUE + f"| Modèle : {self.modele}" + RESET)
        print(BLUE + f"| Marque : {self.marque.nom}" + RESET)
        print(BLUE + f"|     APK de la marque : {self.marque.version_apk}" + RESET)
        print(BLUE + f"|     Chemin de l'APK disponible de la marque : {self.marque.APK_path}" + RESET)
        print(BLUE + f"| APK installé sur le casque : {self.version_apk}" + RESET)
        print(BLUE + f"| JSON : {self.JSON_path}" + RESET)


    def check_json_file(self):

        try:
            # Exécuter la commande adb shell ls pour lister les fichiers dans le répertoire spécifié et evite 'afficher que JSON n'exite pas car sortie rediriger vers fichier NULL
            output = subprocess.check_output(["adb", "-s", self.numero, "shell", "ls", self.config.json_file_path], stderr=subprocess.DEVNULL).decode("utf-8")
            # Vérifier si le nom du fichier existe dans la sortie
            if self.config.json_file_path in output:
                self.JSON_path = os.path.dirname(self.config.json_file_path)
                return True
            else:
                self.JSON_path = "Fichier JSON inexistant"
                return False
        except subprocess.CalledProcessError as e:
            self.JSON_path = "Fichier JSON inexistant" # bizarre car pas une erreur
            return False

    def install_APK(self):
 
        print("----->>>> Installation de l'APK")
        self.print()

        # Commandes pour accorder les permissions
        commands = [
            [self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "grant", self.config.package_name, "android.permission.ACCESS_FINE_LOCATION"],
            [self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "grant", self.config.package_name, "android.permission.READ_EXTERNAL_STORAGE"],
            [self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "grant", self.config.package_name, "android.permission.WRITE_EXTERNAL_STORAGE"]
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
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "install", self.marque.APK_path], check=True)
            print(self.config.GREEN +f"Installation de l'APK réussie."+ self.config.RESET)

        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'installation de l'APK : {e}")
            
            print(f"forcer l'installaion en supprimant l'ancienne app")
            #ATTTENTION BOUCLE INFINI POSSIBLE ON EN VEUT PAAAAAAAAAAAAAAAAS
            self.uninstall_APK()  # Désinstaller l'APK avant l'installation
            self.install_APK()  # Désinstaller l'APK avant l'installation
        
        # Commandes pour accorder les permissions
        commands = [
            [self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "grant", self.config.package_name, "android.permission.ACCESS_FINE_LOCATION"],
            [self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "grant", self.config.package_name, "android.permission.READ_EXTERNAL_STORAGE"],
            [self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "grant", self.config.package_name, "android.permission.WRITE_EXTERNAL_STORAGE"]
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

        try:
            # Exécuter la commande adb pour désinstaller l'APK
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "uninstall", self.config.package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(self.config.GREEN + "Désinstallation de l'APK réussie." + self.config.RESET )
        except subprocess.CalledProcessError as e:
            if "Unknown package" in str(e):
                print("L'application n'était pas installée.")
            else:
                print(f"Une erreur est survenue lors de la désinstallation de l'APK : {e}")

        print("-----------Fin de la désinstallation-----------")

    

    def get_installed_apk_version(self):

        try:
            result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "dumpsys", "package", self.config.package_name], 
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode('utf-8')
            
            # Rechercher la version de l'APK
            version_match = re.search(r'versionName=(\S+)', output)
            if version_match:
                version = version_match.group(1)
                return version
            else:
                print("Impossible de déterminer la version de l'APK installée.")
                return None

        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'obtention de la version de l'APK : {e}")
            print(e.stderr.decode("utf-8"))
            return None


    def add_solution(self):
        print("----->>>> Téléversement de la solution")
        self.print()
        print("Ajout d'une solution... cela peut prendre quelques minutes")
        
        try:
            # Supprimer le fichier upload existant sur l'appareil
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "rm", "-r", self.config.upload_casque_path], check=True)
            print("Fichier upload supprimé avec succès, téléversement du nouveau fichier en cours...")

        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de la suppression du fichier upload : {e}")

        try:
            # Téléverser le nouveau fichier upload
            result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "push", self.config.upload_path, self.config.upload_casque_path], check=True)
            print(self.config.GREEN +f"Téléversement réussi."+ self.config.RESET)

        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de la copie : {e}")
            print(e.stderr.decode("utf-8"))
        print("-----------Fin du téléversement-----------")
    
    def archivage_casque(self) :
        print("----->>>> Archivage du casque")
        print("\nCopie des dossiers... cela peut prendre quelques minutes")

        # Créer le dossier Archivage s'il n'existe pas
        if not os.path.exists(self.config.local_archivage_path):
            os.makedirs(self.config.local_archivage_path)

        try:
            # Téléverser le nouveau fichier upload
            result = subprocess.run(
                [self.config.adb_exe_path, "-s", self.numero, "pull", self.config.package_path,self.config.local_archivage_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            print(self.config.GREEN +f"Copie réussi."+ self.config.RESET)
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'archivage : {e}")
            print(e.stderr.decode("utf-8"))

        print("-----------Fin de l'archivage-----------")
        