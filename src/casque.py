import subprocess
import os
import re
import threading
import traceback
import json
from solution import Solution
from marque import Marque
from config import Config
from adbtools import Adbtools
import base64
import time

class Casque:
    def __init__(self):
        self.device = str
        self.numero = ""
        self.marque = Marque()
        self.modele = ""
        self.version_apk = ""
        self.JSON_path = "NULL"
        self.solutions = []

        self.config = Config.getInstance()
        self.adbtools = Adbtools()
        self.lock = threading.Lock()
        self.refresh_lock = threading.Lock()

    def refresh_casque(self, device):
        with self.refresh_lock:
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
            start_time = time.time()
            self.solutions = self.load_solutions_from_json()
            end_time = time.time()
            
            elapsed_time = end_time - start_time
            print(f"Temps d'exécution de load_solutions_from_json: {elapsed_time} secondes")

            self.pull_solutions()

    def load_solutions_from_json(self):
        solutions = []
        if self.JSON_path != "Fichier JSON inexistant":
            try:
                # Lire le contenu du fichier JSON encodé en base 64 sur le casque
                encoded_output = subprocess.check_output(["adb", "-s", self.numero, "shell", "cat", self.JSON_path], stderr=subprocess.DEVNULL).decode('utf-8')
                if encoded_output.strip() == "":
                    raise ValueError("Le fichier JSON est vide")

                # Décoder le contenu du fichier JSON de la base 64
                decoded_output = base64.b64decode(encoded_output).decode('utf-8')

                # Charger les données JSON
                json_data = json.loads(decoded_output)

                # Créer des objets Solution à partir des données JSON
                for solution_data in json_data.get('versions', []):
                    solution = Solution().from_json(solution_data, self.numero)
                    solutions.append(solution)
            except Exception as e:
                print(f"Erreur lors du chargement du fichier JSON : {e}")
                traceback.print_exc()
        return solutions


    def pull_solutions(self):
        """
        Reconstitue les répertoires des solutions installées sur le casque.
        """
        print("pull_solutions")
        for solution in self.solutions:
            print("pull_solutions1")
            if solution.sol_install_on_casque:
                print("pull_solutions2")
                # Vérifier si la solution qui est sur le casque est dans la bibliothèque
                if not self.is_solution_in_library(solution):
                    self.pull_solution(solution)

    def is_solution_in_library(self, solution):
        """
        Vérifie si une solution est déjà dans la bibliothèque.
        
        Parameters:
            solution (Solution): La solution à vérifier.
            
        Returns:
            bool: True si la solution est déjà dans la bibliothèque, False sinon.
        """

        print("is_solution_in_library")

        safe_solution_name = re.sub(r'[^\w\-_\. ]', '_', solution.nom)
        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)

        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            for subdir in subdirs:
                target_dir = os.path.join(solution_dir, subdir)
                if os.path.exists(target_dir):
                    media_files = getattr(solution, subdir, [])
                    if media_files:
                        check_file_command = f"adb -s {self.numero} shell 'ls -l {media_files[0]}'"
                        try:
                            result = subprocess.run(check_file_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            if result.returncode == 0:
                                print("la sol est déjà dans la bibli")
                                return True
                                
                        except subprocess.CalledProcessError as e:
                            print(f"Erreur lors de la vérification du fichier {media_files[0]} pour {solution.nom} : {e}\n{e.stderr.decode('utf-8')}")
        print("la sol est pas déjà dans la bibli")
        return False

    def pull_solution(self, solution):
        """
        Crée un répertoire pour une solution et copie les fichiers média depuis le casque.

        Args:
            solution (Solution): L'objet Solution pour lequel créer le répertoire.
        """
        safe_solution_name = re.sub(r'[^\w\-_\. ]', '_', solution.nom)
        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)

        if not os.path.exists(solution_dir):
            os.makedirs(solution_dir)
            subdirs = ["image", "image360", "sound", "srt", "video"]
            for subdir in subdirs:
                target_dir = os.path.join(solution_dir, subdir)
                os.makedirs(target_dir, exist_ok=True)
                media_files = getattr(solution, subdir, [])
                #for media_file in media_files:
                    #self.copy_media_file(media_file, target_dir, solution.nom)

            json_path = os.path.join(solution_dir, f"{safe_solution_name}.json")
            with open(json_path, 'w') as json_file:
                json.dump(solution.to_dict(), json_file, indent=4)

            print(f"Solution {solution.nom} reconstruite avec succès dans {solution_dir}.")
        else:
            self._log_message(f"Solution directory already exists for '{solution.nom}' at {solution_dir}")

    def copy_media_file(self, media_file, target_dir, solution_name):
        """
        Copie un fichier média depuis le casque vers le répertoire cible.

        Args:
            media_file (str): Le chemin du fichier média sur le casque.
            target_dir (str): Le répertoire cible local.
            solution_name (str): Le nom de la solution associée.
        """
        check_file_command = f"adb -s {self.numero} shell 'ls -l {media_file}'"
        try:
            result = subprocess.run(check_file_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                adb_pull_command = f"adb -s {self.numero} pull {media_file} {target_dir}"
                try:
                    subprocess.run(adb_pull_command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Erreur lors du téléversement du fichier {media_file} pour {solution_name} : {e}")
            else:
                print(f"Le fichier distant {media_file} n'existe pas pour {solution_name}")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la vérification du fichier {media_file} pour {solution_name} : {e}\n{e.stderr.decode('utf-8')}")

    
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
        print(BLUE + f"| Solutions installées : {len(self.solutions)}" + RESET)
        for solution in self.solutions:
            solution.print()

    def check_json_file(self):
        with self.lock:
            try:
                print("self.config.json_file_path")
                print(self.config.json_file_path)
                output = subprocess.check_output(["adb", "-s", self.numero, "shell", "ls", self.config.json_file_path], stderr=subprocess.DEVNULL).decode("utf-8")
                if self.config.json_file_path in output:
                    self.JSON_path = os.path.dirname(self.config.json_file_path)
                    return self.config.json_file_path
                else:
                    self.JSON_path = "Fichier JSON inexistant"
                    return self.JSON_path
            except subprocess.CalledProcessError as e:
                self.JSON_path = "Fichier JSON inexistant"
                return self.JSON_path

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
            check_command = ["shell", "dumpsys", "wifi"]
            result = subprocess.run([self.config.adb_exe_path] + check_command, text=True, capture_output=True, check=True)

            if "mNetworkInfo" in result.stdout:
                network_info = next((line for line in result.stdout.split('\n') if "mNetworkInfo" in line), None)
                if network_info and "CONNECTED" in network_info:
                    ssid_info = next((line for line in result.stdout.split('\n') if "SSID:" in line), None)
                    if ssid_info and ssid in ssid_info:
                        print("Device is connected to the targeted WiFi network.")
                    else:
                        print("Device is connected to a different network.")
                else:
                    print("Device is not connected to any WiFi network.")
            else:
                print("Unable to determine the WiFi status.")
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Failed to check WiFi status: {e}")
            if e.stdout:
                print(e.stdout)
            if e.stderr:
                print(e.stderr)

    def reconnect_wifi(self):
        try:
            reconnect_command = ["shell", "svc", "wifi", "disable"]
            subprocess.run([self.config.adb_exe_path] + reconnect_command, check=True)
            reconnect_command = ["shell", "svc", "wifi", "enable"]
            subprocess.run([self.config.adb_exe_path] + reconnect_command, check=True)
            print("WiFi has been reset and reconnected.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to reconnect WiFi: {e}")

    def _log_message(self, message):
        if hasattr(self, 'app'):
            self.app.log_debug(message)
        else:
            print(message)
