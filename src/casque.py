import subprocess
import os
import re
import threading
import traceback
import json
import base64
import time

from marque import Marque
from solutionCasque import SolutionCasque
from config import Config
import adbtools
from biblioManager import BiblioManager

class Casque:

    def __init__(self):
        self.device = str
        self.numero = ""
        self.marque = Marque()
        self.modele = ""
        self.battery_level : int
        self.version_apk = ""
        self.JSON_path = "NULL"
        self.JSON_size = -1
        self.solutions_casque = []
        self.code = ""
        self.name = ""
        self.entreprise_association = ""
        self.download_progress = 0

        self.config = Config()
        self.lock = threading.Lock()
        self.refresh_lock = threading.Lock()

        self.biblio = BiblioManager()


    
    #-----------------------------------------------------
    # INSTANCIATION INFO ET VERIFICATION
    #-----------------------------------------------------

    def refresh_casque(self, device, apk_folder):
        with self.refresh_lock:
            self.device = device
            adbtools.wake_up_device(self.config.adb_exe_path, self.numero) 
            try:
                self.numero = self.device.get_serial_no().strip()
            except Exception as e:
                print(f"Erreur lors de l'obtention du numéro de série : {e}")
                traceback.print_exc()
                self.numero = "Inconnu"

            try:
                self.marque.setNom(self.device.shell("getprop ro.product.manufacturer").strip(),apk_folder)
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

            self.battery_level = adbtools.check_battery_level(self.config.adb_exe_path,self.numero)
            
            self.version_apk = self.get_installed_apk_version()
            # Vérifier si l'ancienne APK est installée
            self.old_apk_installed = self.check_old_apk_installed()
            
            self.JSON_path = self.check_json_file()

            
            #self.pull_solutions()

    def refresh_casque_serveur(self):
            self.refresh_JSON()
            self.JSON_path = self.check_json_file()
            
            if ( self.JSON_size != self.get_json_file_size() ) :
                self.JSON_size = self.get_json_file_size()
                if  self.JSON_path != "NULL" :
                    self.solutions_casque = self.load_solutions_from_json()


    def load_solutions_from_json(self):
        solutions_casque = []
        if self.JSON_path != "Fichier JSON inexistant":
            try:
                # Lire le contenu du fichier JSON encodé en base 64 sur le casque
                encoded_output = subprocess.check_output(["adb", "-s", self.numero, "shell", "cat", self.JSON_path], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8')
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
                entreprises = json_data.get('enterprises_associate', [])
                self.entreprise_association = entreprises[0] if entreprises else ""

                # Créer des objets Solution à partir des données JSON
                for solution_data in json_data.get('versions', []):
                    solution_casque = SolutionCasque().from_json(solution_data, self.numero, self.config.upload_casque_path)
                    #solution_casque.size = solution_casque.get_sol_size(self.config.upload_casque_path)
                    solutions_casque.append(solution_casque)
            except Exception as e:
                print(f"Erreur lors du chargement du fichier JSON : {e}")
                traceback.print_exc()
        return solutions_casque

    def check_old_apk_installed(self):
        """
        Vérifie si l'ancienne APK est installée sur le casque.
        
        Returns:
            bool: True si l'ancienne APK est installée, False sinon.
        """
        try:
            result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "pm", "list", "packages", self.config.package_old_name_PPV1],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            output = result.stdout.decode('utf-8')
            if self.config.package_old_name_PPV1 in output:
                return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la vérification de l'ancienne APK : {e}")
        return False
    
    def get_json_file_size(self):
        """
        Retourne la taille du fichier JSON en octets en utilisant ADB.
        """
        if self.JSON_path != "Fichier JSON inexistant":
            command = [self.config.adb_exe_path, "-s", self.numero, "shell", "stat", "-c%s", self.JSON_path]
            try:
                output = subprocess.check_output(command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8").strip()
                return int(output)
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de la récupération de la taille du fichier JSON : {e}")
        return 0
    
    def get_installed_apk_version(self):
        with self.lock:
            try:
                result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "dumpsys", "package", self.config.package_name],
                                        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
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

    
    def getEntreprise(self):
        return self.entreprise_association
    
    def is_solution_in_library(self, solution):
        """
        Vérifie si une solution est déjà dans la bibliothèque.
        
        Parameters:
            solution (Solution): La solution à vérifier.
                
        Returns:
            bool: True si la solution est déjà dans la bibliothèque, False sinon.
        """
        self.biblio.is_sol_in_library(solution)

    def is_solution_in_library_old(self, solution):
        """
        Vérifie si une solution est déjà dans la bibliothèque.
        
        Parameters:
            solution (Solution): La solution à vérifier.
                
        Returns:
            bool: True si la solution est déjà dans la bibliothèque, False sinon.
        """

        safe_solution_name = self.config.safe_string(solution.nom)

        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)

        # Vérifie si le dossier de la solution existe
        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            
            for subdir in subdirs:
                target_dir = os.path.join(solution_dir, subdir)
                
                # Vérifie si le sous-dossier existe
                if os.path.exists(target_dir):

                    media_files = getattr(solution, subdir, [])
                    
                    if media_files:
                        pass
                        #print(f"4: Media files found in library {subdir}: {media_files}")
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
                output = subprocess.check_output(["adb", "-s", self.numero, "shell", "ls", self.config.json_file_path], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")
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
        for solution in self.solutions_casque:
            if solution.sol_install_on_casque:
                installed_solutions.append(solution)
        return installed_solutions

    def refresh_JSON(self):
        adbtools.wake_up_device(self.config.adb_exe_path, self.numero)
        if(adbtools.is_application_running(self.config.adb_exe_path,self.numero,self.config.package_name)):
            adbtools.stop_application(self.config.adb_exe_path,self.numero,self.config.package_name)
        adbtools.start_application(self.config.adb_exe_path,self.numero,self.config.package_name)
    
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
        for solution in self.solutions_casque:
            print(f"solution :" + solution.nom)
            if not solution.sol_install_on_casque :
                print(f" -> Solution not on casque")
                # Vérifier si la solution qui est sur le casque est dans la bibliothèque, 
                # Si la sol est bien dans la biblio alors la fonction renvoie l'objet qui se trouve dans la biblio
                solution_from_bibli = self.biblio.is_sol_in_library(solution)
                if solution_from_bibli != False :
                    print(f" -> Push solution !")
                    self.push_solution_with_progress(solution,solution_from_bibli)

    def push_solution_with_progress(self,solution_json_casque, solution_biblio):
        safe_solution_name = self.config.safe_string(solution_json_casque.nom)
        print(safe_solution_name)
        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)
        print(f"solution_dir")
        print(solution_dir)

        print(solution_biblio.size)
        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            
            total_size = solution_biblio.size
            # Calculate  size
            copied_size = 0
            def progress_callback(copied_bytes):
                nonlocal copied_size
                copied_size += copied_bytes
                progress = copied_size / total_size *100
                #print (f"téléversement en cours : {copied_size}/{total_size}")
                print(f"Progress: {progress:.2f}%")
                self.download_progress = progress  # Mise à jour de la progression du téléchargement


            for subdir in subdirs:
                source_dir = os.path.join(solution_dir, subdir)
                
                if os.path.exists(source_dir):
                    media_files = getattr(solution_json_casque, subdir, [])
                    
                    for media_file in media_files:
                        local_file_path = os.path.join(source_dir, os.path.basename(media_file)).replace("'\'", "/")
                        
                        try:
                            self.copy_media_file(local_file_path, self.config.upload_casque_path + media_file , solution_json_casque.nom, "push")
                            progress_callback(os.path.getsize(local_file_path)) # mesure taille du fichier envoyé et incrément du poid envoyé
                        except Exception as e:
                            print(f"Erreur lors du téléversement du fichier {local_file_path} pour {solution_json_casque.nom} : {e}")
                            return

            solution_json_casque.sol_install_on_casque = True
            print(f"Solution {solution_json_casque.nom} copiée avec succès dans le casque.")
        else:
            self._log_message(f"Solution directory does not exist for '{solution_json_casque.nom}' in the library")
    

    def push_solution(self, solution):
        """
        Copie les fichiers média de la solution dans le casque.

        Args:
            solution (Solution): L'objet Solution pour lequel créer le répertoire.
        """

        safe_solution_name = self.config.safe_string(solution.nom)

        solution_dir = os.path.join(self.config.Banque_de_solution_path, safe_solution_name)

        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            for subdir in subdirs:
                source_dir = os.path.join(solution_dir, subdir)
                
                if os.path.exists(source_dir):
                    media_files = getattr(solution, subdir, [])
                    
                    for media_file in media_files:
                        local_file_path = os.path.join(source_dir, os.path.basename(media_file)).replace("'\'", "/")
                        
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
        for solution in self.solutions_casque:
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
        
        safe_solution_name = self.config.safe_string(solution.nom)

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


    def calculate_total_files_and_size(self, solution_dir):
        total_files = 0
        total_size = 0
        subdirs = ["image", "image360", "sound", "srt", "video"]

        for subdir in subdirs:
            source_dir = os.path.join(solution_dir, subdir)
            if os.path.exists(source_dir):
                for root, _, files in os.walk(source_dir):
                    total_files += len(files)
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)

        return total_files, total_size

    def copy_media_file(self, source_dir, target_dir, solution_name, direction):
        """
        Copie un fichier vers le répertoire cible.

        Args:
            source_dir (str): Le chemin du fichier média sur le casque.
            target_dir (str): Le répertoire cible local.
            solution_name (str): Le nom de la solution associée.
            direction (str): pull or push
        """
        
        #print(f"Solution source  : {source_dir} target : {target_dir}.")
        try:
            result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, direction , source_dir, target_dir], check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du téléversement du fichier {source_dir} pour {solution_name} : {e}")

    def add_solution(self):
        with self.lock:
            print("----->>>> Téléversement de la solution")
            print("Ajout d'une solution... cela peut prendre quelques minutes")
            try:
                subprocess.run([self.config.adb_exe_path, "-s", self.numero, "shell", "rm", "-r", self.config.upload_casque_path], check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                print("Fichier upload supprimé avec succès, téléversement du nouveau fichier en cours...")
            except subprocess.CalledProcessError as e:
                print(f"Une erreur est survenue lors de la suppression du fichier upload : {e}")
            try:
                result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, "push", self.config.upload_path, self.config.upload_casque_path], check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                print(f"Téléversement réussi.")
            except subprocess.CalledProcessError as e:
                print(f"Une erreur est survenue lors de la copie : {e}")
                print(e.stderr.decode("utf-8"))
            print("-----------Fin du téléversement-----------")

    
    #-----------------------------------------------------
    # APK 
    #-----------------------------------------------------
    
    def install_APK(self):
        print("----->>>> Installation de l'APK")
        adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)
        try:
            subprocess.run([self.config.adb_exe_path, "-s", self.numero, "install", self.marque.APK_path], check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            print(f"Installation de l'APK réussie.")
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'installation de l'APK : {e}")
            print(f"forcer l'installation en supprimant l'ancienne app")
            self.uninstall_APK()
            self.install_APK()
            return  # Ajouté pour éviter de tenter de donner des permissions si l'installation a échoué

        # Octroyer les permissions nécessaires
        adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)

        self.refresh_casque_serveur()

        print("-----------Fin de l'installation-----------")


    def uninstall_APK(self):
        print("----->>>> Désinstallation de l'APK")
        if (self.version_apk != 'X') :
            try:
                subprocess.run([self.config.adb_exe_path, "-s", self.numero, "uninstall", self.config.package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                print( "Désinstallation de l'APK réussie." )
            except subprocess.CalledProcessError as e:
                if "Unknown package" in str(e):
                    print(f"L'application n'était pas installée.")
                else:
                    print(f"Une erreur est survenue lors de la désinstallation de l'APK : {e}")
        else :
            print(f"L'application est déjà desinstallée.")


    def archivage_casque(self):
        print("----->>>> Archivage du casque")
        print("\nCopie des dossiers... cela peut prendre quelques minutes")
        if not os.path.exists(self.config.local_archivage_path):
            os.makedirs(self.config.local_archivage_path)
        try:
            result = subprocess.run(
                [self.config.adb_exe_path, "-s", self.numero, "pull", self.config.package_path, self.config.local_archivage_path],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW
            )
            print( f"Copie réussi.")
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Une erreur est survenue lors de l'archivage : {e}")
            print(e.stderr.decode("utf-8"))
        print("-----------Fin de l'archivage-----------")


    #-----------------------------------------------------
    # CONFIGURATION WIFI
    #-----------------------------------------------------

    def is_wifi_connected(self):
        try:
            wifi_status_output = subprocess.check_output(
                [self.config.adb_exe_path, "-s", self.numero, "shell", "dumpsys", "wifi"],
                stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW
            ).decode("utf-8")

            if "mWifiInfo" in wifi_status_output:
                wifi_info = next((line for line in wifi_status_output.split('\n') if "mWifiInfo" in line), None)
                if wifi_info and "SSID: " in wifi_info:
                    ssid_info = wifi_info.split("SSID: ")[1].split(",")[0].strip()
                    if ssid_info == "<unknown ssid>":
                        print("Device not connected.")
                        return False, "not connected"           
                    else :
                        return True, ssid_info
           
        except subprocess.CalledProcessError as e:
            print(f"Failed to check Wi-Fi status: {e}")
            return False, "Erreur"
