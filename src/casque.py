from solution import Solution
from marque import Marque
from config import Config
from adbtools import Adbtools
import subprocess
import os
import re
import threading
import traceback


class Casque:

    def __init__(self):
        self.device = str
        self.numero = ""
        self.marque = Marque()
        self.modele = ""
        self.version_apk = ""
        self.JSON_path = "NULL"
        self.solutions_install = []

        # Permettant de créer une instance de classe, pour déléguer des méthodes
        self.config = Config.getInstance()
        self.adbtools = Adbtools()
        self.lock = threading.Lock()
        
        
    def refresh_casque(self, device):
        with self.lock:
            self.device = device

            try:
                self.numero = self.device.get_serial_no().strip()
            except Exception as e:
                print(f"Erreur lors de l'obtention du numéro de série : {e}")
                traceback.print_exc()
                self.numero = "Inconnu"
        
            try:
                self.marque.setNom(self.device.shell("getprop ro.product.manufacturer").strip())
            except Exception as e:
                print(f"Erreur lors de l'obtention de la marque: {e}")
                traceback.print_exc()
                self.marque.setNom("Inconnu")

            try:
                self.modele = self.device.shell("getprop ro.product.model").strip()
            except Exception as e:
                print(f"Erreur lors de l'obtention du modèle: {e}")
                traceback.print_exc()
                self.modele = "Inconnu"

        self.version_apk = self.get_installed_apk_version()
        self.JSON_path = self.check_json_file()
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
        with self.lock:
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

        self.adbtools.grant_permissions(self.numero)

        try:
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "install", self.marque.APK_path], check=True)
            print(self.config.GREEN + f"Installation de l'APK réussie." + self.config.RESET)

        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'installation de l'APK : {e}")
            print(f"forcer l'installation en supprimant l'ancienne app")
            self.uninstall_APK()
            self.install_APK()
        
        self.adbtools.grant_permissions(self.numero)
        print("-----------Fin de l'installation-----------")


    def uninstall_APK(self):
        print("----->>>> Désinstallation de l'APK")
        self.print()

        try:
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "uninstall", self.config.package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(self.config.GREEN + "Désinstallation de l'APK réussie." + self.config.RESET)

        except subprocess.CalledProcessError as e:
            if "Unknown package" in str(e):
                print("L'application n'était pas installée.")
            else:
                print(f"Une erreur est survenue lors de la désinstallation de l'APK : {e}")

        print("-----------Fin de la désinstallation-----------")


    def get_installed_apk_version(self):
        with self.lock:
            try:
                result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "dumpsys", "package", self.config.package_name], 
                                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = result.stdout.decode('utf-8')
                
                version_match = re.search(r'versionName=(\S+)', output)
                if version_match:
                    version = version_match.group(1)
                    return version
                else:
                    return None

            except subprocess.CalledProcessError as e:
                print(f"Une erreur est survenue lors de l'obtention de la version de l'APK : {e}")
                print(e.stderr.decode("utf-8"))
                return None
            

    def add_solution(self):
        with self.lock:
            print("----->>>> Téléversement de la solution")
            self.print()
            print("Ajout d'une solution... cela peut prendre quelques minutes")
            
            try:
                subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "rm", "-r", self.config.upload_casque_path], check=True)
                print("Fichier upload supprimé avec succès, téléversement du nouveau fichier en cours...")

            except subprocess.CalledProcessError as e:
                print(f"Une erreur est survenue lors de la suppression du fichier upload : {e}")

            try:
                result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "push", self.config.upload_path, self.config.upload_casque_path], check=True)
                print(self.config.GREEN + f"Téléversement réussi." + self.config.RESET)

            except subprocess.CalledProcessError as e:
                print(f"Une erreur est survenue lors de la copie : {e}")
                print(e.stderr.decode("utf-8"))
            print("-----------Fin du téléversement-----------")
    
    def archivage_casque(self):

        print("----->>>> Archivage du casque")
        print("\nCopie des dossiers... cela peut prendre quelques minutes")

        if not os.path.exists(self.config.local_archivage_path):
            os.makedirs(self.config.local_archivage_path)

        try:
            result = subprocess.run(
                [self.config.adb_exe_path, "-s", self.numero, "pull", self.config.package_path, self.config.local_archivage_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            print(self.config.GREEN + f"Copie réussi." + self.config.RESET)
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'archivage : {e}")
            print(e.stderr.decode("utf-8"))

        print("-----------Fin de l'archivage-----------")

    def get_wifi_credentials(self):
        with self.lock:
            try:
                ssid_output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], shell=False).decode('cp850')
                print(ssid_output)

                ssid = ""
                for line in ssid_output.split("\n"):
                    if "SSID" in line and "BSSID" not in line:
                        ssid = line.split(":")[1].strip()
                        break
                
                if ssid:
                    password_output = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', shell=True).decode('cp850')
                    password = ""
                    for line in password_output.split("\n"):
                        if "Contenu de la clé" in line or "Key Content" in line:
                            password = line.split(":")[1].strip()
                            break
                    return ssid, password
                else:
                    print("SSID not found.")
                    return None, None

            except subprocess.CalledProcessError as e:
                print(f"Command failed: {e}")
                return None, None
            except UnicodeDecodeError as e:
                print(f"Decode error: {e}")
                return None, None

    def share_wifi_to_casque(self):
        with self.lock:
            try:
                ssid, password = self.get_wifi_credentials()
                if ssid and password:
                    print(ssid)
                    print(password)
                    self.adbtools.configure_wifi_on_casque(ssid, password)
                    self.reconnect_wifi()
                    self.check_wifi_connection(ssid)
                else:
                    print("Failed to retrieve WiFi credentials.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def check_wifi_connection(self, ssid):
        try:
            # Exécution de la commande pour obtenir le statut du WiFi
            check_command = ["shell", "dumpsys", "wifi"]
            result = subprocess.run([self.config.adb_exe_path] + check_command, text=True, capture_output=True, check=True)
            
            # Analyser la sortie pour vérifier si le casque est connecté à un réseau spécifique
            if "mNetworkInfo" in result.stdout:
                network_info = next((line for line in result.stdout.split('\n') if "mNetworkInfo" in line), None)
                if network_info and "CONNECTED" in network_info:
                    ssid_info = next((line for line in result.stdout.split('\n') if "SSID:" in line), None)
                    if ssid_info and ssid in ssid_info:  # Remplacer "your_target_ssid" par le SSID attendu
                        print("Device is connected to the targeted WiFi network.")
                    else:
                        print("Device is connected to a different network.")
                else:
                    print("Device is not connected to any WiFi network.")
            else:
                print("Unable to determine the WiFi status.")
                print(result.stdout)  # Pour diagnostic

        except subprocess.CalledProcessError as e:
            print(f"Failed to check WiFi status: {e}")
            if e.stdout:
                print(e.stdout.decode('utf-8'))
            if e.stderr:
                print(e.stderr.decode('utf-8'))


    def reconnect_wifi(self):
        try:
            reconnect_command = ["shell", "svc", "wifi", "disable"]
            subprocess.run([self.config.adb_exe_path] + reconnect_command, check=True)
            reconnect_command = ["shell", "svc", "wifi", "enable"]
            subprocess.run([self.config.adb_exe_path] + reconnect_command, check=True)
            print("WiFi has been reset and reconnected.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to reconnect WiFi: {e}")
