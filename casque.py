from solution import Solution
from marque import Marque
from ressources import Ressources
import subprocess
import os
import re




# Fonction pour obtenir le chemin absolu du fichier/dossier
def resource_path(relative_path):
    """Obtenir le chemin absolu du fichier, fonctionne pour dev et pour PyInstaller"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
    

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
        # Définir le code de couleur ANSI pour le bleu
        BLUE = '\033[94m'
        RESET = '\033[0m'

        # Utiliser les codes de couleur pour chaque ligne
        print(BLUE + f"| Numéro de série : {self.numero}" + RESET)
        print(BLUE + f"| Modèle : {self.modele}" + RESET)
        print(BLUE + f"| Marque : {self.marque.nom}" + RESET)
        print(BLUE + f"|     APK de la marque : {self.marque.version_apk}" + RESET)
        print(BLUE + f"|     Chemin de l'APK disponible de la marque : {self.marque.APK_path}" + RESET)
        print(BLUE + f"| APK installé sur le casque : {self.version_apk}" + RESET)
        print(BLUE + f"| JSON : {self.JSON_path}" + RESET)
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
        adb_exe = resource_path("platform-tools/adb.exe")
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
            
            RESET = '\033[0m'
            GREEN = '\033[92m'
            print(GREEN +f"Installation de l'APK réussie."+ RESET)
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
        adb_exe = resource_path("platform-tools/adb.exe")

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

    

    def get_installed_apk_version(self):

        adb_exe = resource_path("platform-tools/adb.exe")
        package_name = "com.VRAI_Studio.Reverto"

        try:
            result = subprocess.run([adb_exe, "-s", self.numero, "shell", "dumpsys", "package", package_name], 
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
            print(e.stderr.decode('utf-8'))
            return None


    def add_solution(self):
        print("----->>>>Téléversement de la solution")
        self.print()
        print("Ajout d'une solution... cela peut prendre quelques minutes")

        # Définir les chemins vers adb et le chemin du fichier sur l'appareil
        adb_exe = resource_path("platform-tools/adb.exe")
        remote_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded/upload"
        
        try:
            # Supprimer le fichier upload existant sur l'appareil
            subprocess.run([adb_exe, "-s", self.numero, "shell", "rm", "-r", remote_path], check=True)
            print("Fichier upload supprimé avec succès, téléversement du nouveau fichier en cours...")
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de la suppression du fichier upload : {e}")

        try:
            # Téléverser le nouveau fichier upload
            result = subprocess.run(
                [adb_exe, "-s", self.numero, "push", "./Banque_de_solutions/upload", remote_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            RESET = '\033[0m'
            GREEN = '\033[92m'
            print(GREEN +f"Téléversement réussi.."+ RESET)
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors du téléversement de la solution : {e}")
            print(e.stderr.decode("utf-8"))
        print("-----------Fin du téléversement-----------")

    def find_All_Solutions(self):
        print("e")
        #lecture du fichier json
        #récuper pour chaque partie les dossier associé et les mettres dedans