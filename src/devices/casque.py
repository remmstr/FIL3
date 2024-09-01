import subprocess
import os
import re
import threading
import traceback
import json
import base64
import time

from .marque import Marque
from .solutionCasque import SolutionCasque
from .config import Config
from .adbtools import Adbtools
from .biblioManager import BiblioManager

class Casque:

    def __init__(self):
        """
        Initialise un objet Casque avec les attributs nécessaires pour gérer un casque VR.
        """
        self.device = str
        self.numero = ""
        self.marque = Marque()
        self.modele = ""
        self.battery_level: int
        self.version_apk = ""
        self.JSON_path = "NULL"
        self.JSON_size = -1
        self.solutions_casque = []
        self.code = ""
        self.name = ""
        self.entreprise_association = ""
        self.download_progress = 0

        self.adbtools = Adbtools()
        self.config = Config()
        self.lock = threading.Lock()
        self.refresh_lock = threading.Lock()

        self.biblio = BiblioManager()

    #-----------------------------------------------------
    # INSTANCIATION INFO ET VERIFICATION
    #-----------------------------------------------------

    def refresh_casque(self, device, apk_folder):
        """
        Rafraîchit les informations du casque, telles que le numéro de série, la marque,
        le modèle, le niveau de batterie, et les versions APK installées.

        Args:
            device: L'objet représentant le casque.
            apk_folder (str): Le chemin vers le dossier des APK.
        """
        with self.refresh_lock:
            self.device = device
            
            try:
                self.numero = self.device.get_serial_no().strip()
            except Exception as e:
                print(f"{self.name} {self.numero}: Erreur lors de l'obtention du numéro de série : {e}")
                traceback.print_exc()
                self.numero = "Inconnu"
            self.adbtools.wake_up_device(self.config.adb_exe_path, self.numero) 
            try:
                self.marque.setNom(self.device.shell("getprop ro.product.manufacturer").strip(), apk_folder)
            except Exception as e:
                print(f"{self.name} {self.numero}: Erreur lors de l'obtention de la marque: {e}")
                traceback.print_exc()
                self.marque.setNom("Inconnu")

            try:
                self.modele = self.device.shell("getprop ro.product.model").strip()
            except Exception as e:
                print(f"{self.name} {self.numero}: Erreur lors de l'obtention du modèle: {e}")
                traceback.print_exc()
                self.modele = "Inconnu"

            self.battery_level = self.adbtools.check_battery_level(self.config.adb_exe_path, self.numero)
            
            self.version_apk = self.get_installed_apk_version()
            # Vérifier si l'ancienne APK est installée
            self.old_apk_installed = self.check_old_apk_installed()
            
            # Vérifie que le fichier JSON a une taille différente et que le fichier existe bien
            if (self.JSON_path != self.check_json_file()) or (self.JSON_size != self.get_json_file_size()):
                
                self.JSON_path = self.check_json_file()
                self.JSON_size = self.get_json_file_size()

                self.solutions_casque = self.load_datas_from_json()

    def reset_JSON(self):
        """
        Réinitialise les informations du JSON, telles que le nom, le code, et l'association d'entreprise.
        """
        self.name = ""
        self.code = ""
        self.entreprise_association = ""

    def load_datas_from_json(self):
        """
        Charge les données depuis le fichier JSON stocké sur le casque.

        Returns:
            list: Une liste d'objets SolutionCasque représentant les solutions disponibles sur le casque.
        """
        solutions_casque = []
        self.reset_JSON()
        if self.JSON_path != "Fichier JSON inexistant" and self.JSON_path != "NULL":
            try:
                # Lire le contenu du fichier JSON encodé en base 64 sur le casque
                encoded_output = subprocess.check_output(["adb", "-s", self.numero, "shell", "cat", self.JSON_path], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8')
                if encoded_output.strip() == "":
                    raise ValueError(f"{self.name} {self.numero}: Le fichier JSON est vide")

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
                    solution_casque = SolutionCasque().from_json_opti(solution_data, self.numero, self.config.upload_casque_path)
                    solutions_casque.append(solution_casque)
            except Exception as e:
                print(f"{self.name} {self.numero}: Erreur lors du chargement du fichier JSON : {e}")
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
            print(f"{self.name} {self.numero}: Erreur lors de la vérification de l'ancienne APK : {e}")
        return False
    
    def get_json_file_size(self):
        """
        Retourne la taille du fichier JSON en octets en utilisant ADB.

        Returns:
            int: La taille du fichier JSON en octets, ou 0 en cas d'erreur.
        """
        if self.JSON_path != "Fichier JSON inexistant":
            command = [self.config.adb_exe_path, "-s", self.numero, "shell", "stat", "-c%s", self.JSON_path]
            try:
                output = subprocess.check_output(command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8").strip()
                return int(output)
            except subprocess.CalledProcessError as e:
                print(f"{self.name} {self.numero}: Erreur lors de la récupération de la taille du fichier JSON : {e}")
        return 0
    
    def get_installed_apk_version(self):
        """
        Retourne la version de l'APK installée sur le casque.

        Returns:
            str: La version de l'APK installée, ou "X" si aucune version n'est trouvée.
        """
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
                print(f"{self.name} {self.numero}: Une erreur est survenue lors de l'obtention de la version de l'APK : {e}")
                print(e.stderr.decode("utf-8"))
                return None

    
    def getEntreprise(self):
        """
        Retourne l'entreprise associée à la solution.

        Returns:
            str: Le nom de l'entreprise associée.
        """
        return self.entreprise_association
    
    def is_solution_in_library(self, solution):
        """
        Vérifie si une solution est déjà dans la bibliothèque.

        Args:
            solution (Solution): La solution à vérifier.
                
        Returns:
            bool: True si la solution est déjà dans la bibliothèque, False sinon.
        """
        return self.biblio.is_sol_in_library(solution)
    
    def check_json_file(self):
        """
        Vérifie si le fichier JSON existe sur le casque et retourne son chemin.

        Returns:
            str: Le chemin du fichier JSON, ou "Fichier JSON inexistant" si le fichier est absent.
        """
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

    def getListSolInstall(self):
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
        """
        Rafraîchit le JSON sur le casque en réinitialisant les données et en redémarrant l'application si nécessaire.
        """
        self.reset_JSON()
        self.adbtools.wake_up_device(self.config.adb_exe_path, self.numero)
        
        # Vérifier si l'application est en cours d'exécution, et si oui, l'arrêter
        if self.adbtools.is_application_running(self.config.adb_exe_path, self.numero, self.config.package_name):
            self.adbtools.stop_application(self.config.adb_exe_path, self.numero, self.config.package_name)
        
        # Vérifier si l'application est installée avant de la démarrer
        if self.version_apk and self.version_apk != "X":
            self.adbtools.start_application(self.config.adb_exe_path, self.numero, self.config.package_name)
        else:
            print(f"{self.name} {self.numero}: L'application n'est pas installée sur le casque {self.numero}.")

    #-----------------------------------------------------
    # PUSH ET PULL SOLUTION
    #-----------------------------------------------------

    def push_solutions(self):
        """
        Transfère les solutions disponibles dans la bibliothèque vers le casque.
        """
        if not self.solutions_casque:
            print(f"{self.name} {self.numero}: Aucune solution n'est associée au casque, rien n'est à push (téléverser) sur le casque.")
            return

        if not self.JSON_path or self.JSON_path == "Fichier JSON inexistant":
            print(f"{self.name} {self.numero}: Aucun fichier JSON détecté, cela est nécessaire. Veuillez vérifier la connexion du casque ou cliquer sur le bouton 'Rafraîchir fichier JSON'.")
            return

        solutions_pushed = False

        print(f"{self.name} {self.numero}: push_solutions")
        for solution in self.solutions_casque:
            if not solution.sol_install_on_casque:
                solution_from_bibli = self.biblio.is_sol_in_library(solution)
                if solution_from_bibli:
                    self.push_solution_with_progress(solution, solution_from_bibli)
                    solutions_pushed = True
                else:
                    print(f"{self.name} {self.numero}: Push impossible car la solution '{solution.nom}' n'est pas disponible dans la bibliothèque, veuillez la télécharger manuellement sur le casque via l'APK.")

        if not solutions_pushed:
            print(f"{self.name} {self.numero}: Toutes les solutions sont déjà installées ou ne sont pas disponibles dans la bibliothèque.")



    def push_solution_with_progress(self, solution_json_casque, solution_biblio):
        """
        Transfère une solution spécifique du PC vers le casque avec un suivi de la progression.

        Args:
            solution_json_casque (SolutionCasque): L'objet SolutionCasque à transférer.
            solution_biblio (SolutionBiblio): L'objet SolutionBiblio correspondant dans la bibliothèque.
        """
        safe_solution_name = self.config.safe_string(solution_json_casque.nom)
        print(f"{self.name} {self.numero}: {safe_solution_name}")
        solution_dir = os.path.join(self.config.Bibliothèque_de_solution_path, safe_solution_name)
        print(f"{self.name} {self.numero}: solution_dir {solution_dir}")

        print(solution_biblio.size)
        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            
            total_size = solution_biblio.size
            copied_size = 0

            def progress_callback(copied_bytes):
                nonlocal copied_size
                copied_size += copied_bytes
                progress = copied_size / total_size * 100
                print(f"{self.name} {self.numero}: Progress: {progress:.2f}%")
                self.download_progress = progress  # Mise à jour de la progression du téléchargement

            for subdir in subdirs:
                source_dir = os.path.join(solution_dir, subdir)
                
                if os.path.exists(source_dir):
                    media_files = getattr(solution_json_casque, subdir, [])
                    
                    for media_file in media_files:
                        local_file_path = os.path.join(source_dir, os.path.basename(media_file)).replace("'\'", "/")
                        
                        try:
                            self.copy_media_file(local_file_path, self.config.upload_casque_path + media_file, solution_json_casque.nom, "push")
                            progress_callback(os.path.getsize(local_file_path))  # Mesure de la taille du fichier envoyé et mise à jour du poids envoyé
                        except Exception as e:
                            print(f"{self.name} {self.numero}: Erreur lors du téléversement du fichier {local_file_path} pour {solution_json_casque.nom} : {e}")
                            return

            solution_json_casque.sol_install_on_casque = True
            print(f"{self.name} {self.numero}: Solution {solution_json_casque.nom} copiée avec succès dans le casque.")
        else:
            self._log_message(f"{self.name} {self.numero}: Solution directory does not exist for '{solution_json_casque.nom}' in the library")

    def push_solution(self, solution):
        """
        Copie les fichiers média d'une solution spécifique du PC vers le casque.

        Args:
            solution (Solution): L'objet Solution à transférer.
        """
        safe_solution_name = self.config.safe_string(solution.nom)

        solution_dir = os.path.join(self.config.Bibliothèque_de_solution_path, safe_solution_name)

        if os.path.exists(solution_dir):
            subdirs = ["image", "image360", "sound", "srt", "video"]
            for subdir in subdirs:
                source_dir = os.path.join(solution_dir, subdir)
                
                if os.path.exists(source_dir):
                    media_files = getattr(solution, subdir, [])
                    
                    for media_file in media_files:
                        local_file_path = os.path.join(source_dir, os.path.basename(media_file)).replace("'\'", "/")
                        
                        try:
                            self.copy_media_file(local_file_path, self.config.upload_casque_path + media_file, solution.nom, "push")
                        except Exception as e:
                            print(f"{self.name} {self.numero}: Erreur lors du téléversement du fichier {local_file_path} pour {solution.nom} : {e}")
                            return

            solution.sol_install_on_casque = True
            print(f"{self.name} {self.numero}: Solution {solution.nom} copiée avec succès dans le casque.")
        else:
            self._log_message(f"{self.name} {self.numero}: Solution directory does not exist for '{solution.nom}' in the library")

    def pull_solutions(self):
        """
        Reconstitue les répertoires des solutions installées sur le casque en les transférant vers le PC.
        """
        solutions_to_pull = 0

        for solution in self.solutions_casque:
            # Vérifie si la solution est installée sur le casque
            if solution.sol_install_on_casque:
                # Si la solution n'est pas encore dans la bibliothèque, la "pull"
                if not self.is_solution_in_library(solution):
                    self.pull_solution_sans_progress(solution)
                    self.biblio.refresh_biblio()
                    solutions_to_pull += 1

        # Si aucune solution n'a été "pullée", afficher un message
        if solutions_to_pull == 0:
            print(f"{self.name} {self.numero}: Aucune solution à 'pull'(prélever) du casque à la bibliothque, car pas de solution téléchargé dans le casque.")


    def pull_solution_sans_progress(self, solution):
        """
        Transfère les fichiers média d'une solution spécifique du casque vers le PC sans suivi de la progression.

        Args:
            solution (Solution): L'objet Solution à transférer.
        """
        try:
            safe_solution_name = self.config.safe_string(solution.nom)
            solution_dir = os.path.join(self.config.Bibliothèque_de_solution_path, safe_solution_name)
            print(f"{self.name} {self.numero}: Creating directory for solution: {solution_dir}")

            if not os.path.exists(solution_dir):
                os.makedirs(solution_dir)
                print(f"Directory created: {solution_dir}")

                subdirs = ["image", "image360", "sound", "srt", "video"]
                for subdir in subdirs:
                    target_dir = os.path.join(solution_dir, subdir)
                    os.makedirs(target_dir, exist_ok=True)
                    print(f"Subdirectory created: {target_dir}")

                    media_files = getattr(solution, subdir, [])
                    #print(f"Media files in {subdir}: {media_files}")

                    for media_file in media_files:
                        try:
                            print(f"Copying media file: {media_file} to {target_dir}")
                            self.copy_media_file(self.config.upload_casque_path + media_file, target_dir, solution.nom, "pull")
                        except Exception as e:
                            print(f"Erreur lors de la copie du fichier {self.config.upload_casque_path + media_file} pour {solution.nom} : {e}")
                            continue  # Passer au fichier suivant en cas d'erreur
                print(f"Solution {solution.nom} reconstruite avec succès dans {solution_dir}.")
            else:
                print(f"Directory already exists, skipping: {solution_dir}")
        except Exception as e:
            print(f"Error occurred while pulling solution {solution.nom}: {e}")
            traceback.print_exc()

    def pull_solution(self, solution):
        """
        Transfère les fichiers média d'une solution spécifique du casque vers le PC avec suivi de la progression.

        Args:
            solution (Solution): L'objet Solution à transférer.
        """
        try:
            safe_solution_name = self.config.safe_string(solution.nom)
            solution_dir = os.path.join(self.config.Bibliothèque_de_solution_path, safe_solution_name)
            print(f"{self.name} {self.numero}: Creating directory for solution: {solution_dir}")

            if not os.path.exists(solution_dir):
                os.makedirs(solution_dir)
                print(f"Directory created: {solution_dir}")

                subdirs = ["image", "image360", "sound", "srt", "video"]
                
                # Utiliser la taille déjà calculée dans solution.size
                total_size = solution.size
                copied_size = 0

                def progress_callback(copied_bytes):
                    nonlocal copied_size
                    copied_size += copied_bytes
                    progress = copied_size / total_size * 100
                    print(f"Progress: {progress:.2f}%")
                    self.download_progress = progress  # Mise à jour de la progression du téléchargement

                for subdir in subdirs:
                    target_dir = os.path.join(solution_dir, subdir)
                    os.makedirs(target_dir, exist_ok=True)
                    print(f"Subdirectory created: {target_dir}")

                    media_files = getattr(solution, subdir, [])
                    print(f"Media files in {subdir}: {media_files}")

                    for media_file in media_files:
                        print(f"Copying media file: {self.config.upload_casque_path + media_file} to {target_dir}")
                        try:
                            progress_callback(os.path.getsize(self.config.upload_casque_path + media_file))  # Mise à jour de la taille copiée
                            self.copy_media_file(self.config.upload_casque_path + media_file, target_dir, solution.nom, "pull")
                        except Exception as e:
                            print(f"Erreur lors de la copie du fichier {self.config.upload_casque_path + media_file} pour {solution.nom} : {e}")
                            continue  # Passer au fichier suivant en cas d'erreur

                print(f"Solution {solution.nom} reconstruite avec succès dans {solution_dir}.")
            else:
                print(f"Directory already exists, skipping: {solution_dir}")
        except Exception as e:
            print(f"Error occurred while pulling solution {solution.nom}: {e}")
            traceback.print_exc()

    def calculate_total_files_and_size(self, solution_dir):
        """
        Calcule le nombre total de fichiers et la taille totale d'une solution dans un répertoire spécifique.

        Args:
            solution_dir (str): Le chemin vers le répertoire de la solution.

        Returns:
            tuple: Un tuple contenant le nombre total de fichiers et la taille totale en octets.
        """
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
        Copie un fichier média entre le casque et le PC.

        Args:
            source_dir (str): Le chemin du fichier source sur le casque.
            target_dir (str): Le chemin du fichier cible sur le PC.
            solution_name (str): Le nom de la solution associée.
            direction (str): Direction du transfert, "push" pour transférer du PC vers le casque, "pull" pour l'inverse.
        """
        try:
            result = subprocess.run([self.config.adb_exe_path, "-s", self.numero, direction, source_dir, target_dir], check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.CalledProcessError as e:
            print(f"{self.name} {self.numero}: Erreur lors du téléversement du fichier {source_dir} pour {solution_name} : {e}")

    #-----------------------------------------------------
    # APK 
    #-----------------------------------------------------
    
    def install_APK(self):
        """
        Installe une APK sur le casque, en réessayant plusieurs fois en cas d'échec.

        Note:
            Cette méthode tente d'installer une APK jusqu'à trois fois en cas d'échec.
        """
        if self.marque.version_apk != "" :
            max_attempts = 3
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    self.adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)
                    subprocess.run([self.config.adb_exe_path, "-s", self.numero, "install", self.marque.APK_path], check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                    print(f"{self.name} {self.numero}: Installation de l'APK {self.marque.version_apk} réussie.")
                    
                    self.adbtools.grant_permissions(self.config.adb_exe_path, self.numero, self.config.package_name)
                    self.adbtools.wake_up_device(self.config.adb_exe_path, self.numero)
                    self.adbtools.start_application(self.config.adb_exe_path, self.numero, self.config.package_name)
                    break  # Sortir de la boucle si l'installation réussit
                
                except subprocess.CalledProcessError as e:
                    attempt += 1

                    if attempt < max_attempts:
                        print(f"{self.name} {self.numero}: Difficulté a l'installation, suppression de l'ancienne application avant d'essayer d'installer de nouveau, essai n° {attempt}")
                        self.uninstall_APK()
                    else:
                        return

            if attempt < max_attempts:
                pass
            else:
                print(f"{self.name} {self.numero}: Impossible d'installer l'APK")
        else:
            print(f"{self.name} {self.numero}: Aucune APK disponible -> Veuillez ajouter une version d'apk dans le dossier du même nom pour installer une application")

    def uninstall_APK(self):
        """
        Désinstalle l'APK du casque si elle est présente.
        """
        if self.version_apk != 'X':
            try:
                subprocess.run([self.config.adb_exe_path, "-s", self.numero, "uninstall", self.config.package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
                print(f"{self.name} {self.numero}: Désinstallation de l'APK réussie.")
            except subprocess.CalledProcessError as e:
                if "Unknown package" in str(e):
                    print(f"{self.name} {self.numero}: L'application n'était pas installée.")
                else:
                    print(f"{self.name} {self.numero}: Une erreur est survenue lors de la désinstallation de l'APK : {e}")
        else:
            print(f"{self.name} {self.numero}: L'application est déjà désinstallée.")

    def open_apk(self):
        """
        Ouvre l'application installée sur le casque.
        """
        if self.version_apk != 'X':
            self.adbtools.start_application(self.config.adb_exe_path, self.numero, self.config.package_name)
            print(f"{self.name} {self.numero}: Ouverture de l'application.")
        else:
            print(f"{self.name} {self.numero}: L'application est désinstallée, vous ne pouvez pas l'ouvrir.")

    def close_apk(self):
        """
        Ferme l'application installée sur le casque.
        """
        if self.version_apk != 'X':
            self.adbtools.stop_application(self.config.adb_exe_path, self.numero, self.config.package_name)
            print(f"{self.name} {self.numero}: Fermeture de l'application.")
        else:
            print(f"{self.name} {self.numero}: L'application est désinstallée, vous ne pouvez pas la fermer.")

    #-----------------------------------------------------
    # CONFIGURATION WIFI
    #-----------------------------------------------------

    def is_wifi_connected(self):
        """
        Vérifie si le casque est connecté à un réseau Wi-Fi.

        Returns:
            tuple: Un tuple contenant un booléen indiquant si le casque est connecté,
            et le SSID du réseau connecté ou une indication d'erreur.
        """
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
                        return False, "not connected"
                    else:
                        return True, ssid_info
           
        except subprocess.CalledProcessError as e:
            print(f"{self.name} {self.numero}: Failed to check Wi-Fi status: {e}")
            return False, "Erreur"
