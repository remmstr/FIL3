import subprocess
import os
import re
import threading
import traceback
import json
import base64
import time

from marque import Marque
from solution import Solution
from config import Config
import adbtools

class Casque:

    def __init__(self):
        self.device = str
        self.numero = ""
        self.marque = Marque()
        self.modele = ""
        self.version_apk = ""
        self.JSON_path = "NULL"
        self.solutions = []
        self.code = ""
        self.name = ""
        self.enterprise_association = ""

        self.config = Config()
        self.lock = threading.Lock()
        self.refresh_lock = threading.Lock()


    
    #-----------------------------------------------------
    # INSTANCIATION INFO ET VERIFICATION
    #-----------------------------------------------------

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

            if  self.JSON_path != "NULL" :
                self.solutions = self.load_solutions_from_json()

            #self.pull_solutions()

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

                # Récupérer et enregistrer le nom
                self.name = json_data.get('name', "")

                # Récupérer et enregistrer le code à quatre chiffres
                self.code = json_data.get('code', "")

                # Récupérer et enregistrer l'entreprise associée
                enterprises = json_data.get('enterprises_associate', [])
                self.enterprise = enterprises[0] if enterprises else ""

                # Créer des objets Solution à partir des données JSON
                for solution_data in json_data.get('versions', []):
                    solution = Solution().from_json(solution_data, self.numero, self.config.upload_casque_path)
                    solutions.append(solution)
            except Exception as e:
                print(f"Erreur lors du chargement du fichier JSON : {e}")
                traceback.print_exc()
        return solutions

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
                    return "X"
            except subprocess.CalledProcessError as e:
                print(f"Une erreur est survenue lors de l'obtention de la version de l'APK : {e}")
                print(e.stderr.decode("utf-8"))
                return None


    def is_solution_in_library(self, solution):
        """
        Vérifie si une solution est déjà dans la bibliothèque.
        
        Parameters:
            solution (Solution): La solution à vérifier.
                
        Returns:
            bool: True si la solution est déjà dans la bibliothèque, False sinon.
        """

        # Crée un nom de dossier sûr pour la solution
        safe_solution_name = re.sub(r'[^\w\-_\. ]', '_', solution.nom)
        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)

        print(f"Checking solution directory: {solution_dir}")

        # Vérifie si le dossier de la solution existe
        if os.path.exists(solution_dir):
            print("1: Solution directory exists.")
            subdirs = ["image", "image360", "sound", "srt", "video"]
            
            for subdir in subdirs:
                target_dir = os.path.join(solution_dir, subdir)
                print(f"2: Checking subdir: {subdir} at {target_dir}")
                
                # Vérifie si le sous-dossier existe
                if os.path.exists(target_dir):
                    print("3: Subdirectory exists.")
                    media_files = getattr(solution, subdir, [])
                    
                    if media_files:
                        print(f"4: Media files found in {subdir}: {media_files}")
                        #for media_file in media_files:
                            # Extrait le nom du fichier du chemin complet
                            #local_media_file_path = os.path.join(target_dir, os.path.basename(media_file))
                            
                            # Vérifie si le fichier de média existe localement
                            #print(f"Checking local media file: {local_media_file_path}")
                            #if os.path.exists(local_media_file_path):
                            #    print("5: Media file found in library.")
                            #else:
                            #    print(f"Media file {local_media_file_path} not found in library.")
                            #    return False
                            
            print("All media files are present in the library.")
            return True

        print("Solution directory does not exist.")
        return False
    
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

    def getListSolInstall(self) : 
        """
        Retourne une liste des solutions installées sur le casque.

        Returns:
            list: Liste des solutions installées.
        """
        installed_solutions = []
        for solution in self.solutions:
            if solution.sol_install_on_casque:
                installed_solutions.append(solution)
        return installed_solutions

    
    #-----------------------------------------------------
    # PUSH ET PULL SOLUTION
    #-----------------------------------------------------

    def push_solutions(self) : 
        """
        Retourne une liste des solutions installées sur le casque.

        Returns:
            list: Liste des solutions installées.
        """
        print("push_solutions")
        for solution in self.solutions:
            print("solution :" + solution.nom)
            if not solution.sol_install_on_casque:
                print(" -> Solution not on casque")
                # Vérifier si la solution qui est sur le casque est dans la bibliothèque
                #if self.is_solution_in_library(solution):
                print(" -> Push solution !")
                self.push_solution(solution)

    def push_solution(self, solution):
        """
        Copie les fichiers média de la solution dans le casque.

        Args:
            solution (Solution): L'objet Solution pour lequel créer le répertoire.
        """

        # Crée un nom de dossier sûr pour la solution
        safe_solution_name = re.sub(r'[^\w\-_\. ]', '_', solution.nom)
        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)

        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            for subdir in subdirs:
                source_dir = os.path.join(solution_dir, subdir)
                
                if os.path.exists(source_dir):
                    media_files = getattr(solution, subdir, [])
                    
                    for media_file in media_files:
                        local_file_path = os.path.join(source_dir, os.path.basename(media_file)).replace("'\'", "/")
                        print(local_file_path)
                        try:
                            self.copy_media_file(local_file_path, self.config.upload_casque_path + media_file , solution.nom, "push")
                        except Exception as e:
                            print(f"Erreur lors du téléversement du fichier {local_file_path} pour {solution.nom} : {e}")
                            return

            solution.sol_install_on_casque = True
            print(f"Solution {solution.nom} copiée avec succès dans le casque.")
        else:
            self._log_message(f"Solution directory does not exist for '{solution.nom}' in the library")


    def pull_solutions(self):
        """
        Reconstitue les répertoires des solutions installées sur le casque.
        """
        for solution in self.solutions:
            print("solution :" + solution.nom)
            if solution.sol_install_on_casque:
                print(" -> Solution on casques")
                # Vérifier si la solution qui est sur le casque est dans la bibliothèque
                if not self.is_solution_in_library(solution):
                    print(" -> Pull solution !")
                    self.pull_solution(solution)

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
                for media_file in media_files:
                    self.copy_media_file( self.config.upload_casque_path + media_file, target_dir, solution.nom, "pull")

            print(f"Solution {solution.nom} reconstruite avec succès dans {solution_dir}.")
        else:
            self._log_message(f"Solution directory already exists for '{solution.nom}' at {solution_dir}")


    def copy_media_file(self, source_dir, target_dir, solution_name, direction):
        """
        Copie un fichier vers le répertoire cible.

        Args:
            source_dir (str): Le chemin du fichier média sur le casque.
            target_dir (str): Le répertoire cible local.
            solution_name (str): Le nom de la solution associée.
            direction (str): pull or push
        """
        
        print(f"Solution source  : {source_dir} target : {target_dir}.")
        try:
            result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, direction , source_dir, target_dir], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du téléversement du fichier {source_dir} pour {solution_name} : {e}")

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

    
    #-----------------------------------------------------
    # APK 
    #-----------------------------------------------------
    
    def install_APK(self):
        print("----->>>> Installation de l'APK")
        self.print()
        adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)
        try:
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "install", self.marque.APK_path], check=True)
            print(self.config.GREEN + f"Installation de l'APK réussie." + self.config.RESET)
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'installation de l'APK : {e}")
            print(f"forcer l'installation en supprimant l'ancienne app")
            self.uninstall_APK()
            self.install_APK()
            return  # Ajouté pour éviter de tenter de donner des permissions si l'installation a échoué

        # Octroyer les permissions nécessaires
        adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)
        
        # Extraire les permissions et les octroyer
        permissions = self.extract_permissions(self.config.package_name)
        print(permissions)
        adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)

        # Obtenir le nom complet de l'activité principale
        try:
            activity_output = subprocess.check_output(
                [self.config.adb_exe_path, "-s", self.numero, "shell", "cmd", "package", "resolve-activity", "--brief", self.config.package_name],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()

            # Extraire uniquement la ligne contenant le nom de l'activité (dernière ligne normalement)
            activity_name = activity_output.split('\n')[-1].strip()
            print(f"Activity Name: {activity_name}")

            # Démarrer l'application avec le nom complet de l'activité
            start_command = [
                self.config.adb_exe_path, "-s", self.numero, "shell", "am", "start",
                "-n", activity_name
            ]
            subprocess.run(start_command, check=True)
            print(f"Application {self.config.package_name} démarrée avec succès.")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'obtention ou du démarrage de l'activité principale : {e}")
            #self.force_stop_and_clear_cache(self.config.package_name)
        adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)

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


    #-----------------------------------------------------
    # CONFIGURATION WIFI
    #-----------------------------------------------------

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
                    adbtools.self.configure_wifi_on_casque(adbtools.adb_exe_path, ssid, password)
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


    #-----------------------------------------------------
    # PRINT
    #-----------------------------------------------------
    
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
