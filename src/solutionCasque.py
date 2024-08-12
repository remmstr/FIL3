import subprocess
import time
import os
from solution import Solution
from config import Config

class SolutionCasque(Solution):

    def __init__(self):
        super().__init__()
        self.sol_install_on_casque = False
        self.config = Config()

    def from_json_opti(self, json_data, device_serial, upload_casque_path):
        """
        Initialise l'objet Solution à partir des données JSON.

        Args:
            json_data (dict): Les données JSON pour initialiser l'objet.
            device_serial (str): Le numéro de série du casque pour les vérifications ADB.

        Returns:
            Solution: L'instance de l'objet Solution initialisée.
        """
        # Fetch data using local variables for repeated access
        name_module = json_data.get('name_module', {})
        name_version = json_data.get('name_version', {})
        self.nom = name_module.get('fr', "")
        self.version = name_version.get('fr', "")
        self.device_serial = device_serial  # Utilisation de l'argument device_serial

        # Prepare media lists using dictionary to reduce condition checks
        media_mapping = {
            '.png': self.image,
            '.jpg': self.image,
            'image360': self.image360,
            '.mp3': self.sound,
            '.srt': self.srt,
            '.mp4': self.video,
            '.mkv': self.video
        }

        # Categorize medias using a single loop and optimized conditionals
        for media in json_data.get('medias', []):
            for key, media_list in media_mapping.items():
                if key in media:
                    media_list.append(media)
                    break

        # Calculate total size and check installation status
        self.size = self.verif_sol_install(device_serial, upload_casque_path)
        self.sol_install_on_casque = self.size != 0

        return self


    def from_json(self, json_data, device_serial, upload_casque_path):
        """
        Initialise l'objet Solution à partir des données JSON.

        Args:
            json_data (dict): Les données JSON pour initialiser l'objet.
            device_serial (str): Le numéro de série du casque pour les vérifications ADB.

        Returns:
            Solution: L'instance de l'objet Solution initialisée.
        """
        self.nom = json_data.get('name_module', {}).get('fr', "")
        self.version = json_data.get('name_version', {}).get('fr', "")
        self.device_serial = device_serial  # Utilisation de l'argument device_serial

        medias = json_data.get('medias', [])
        for media in medias:
            if media.endswith('.png') or media.endswith('.jpg'):
                if 'image360' in media:
                    self.image360.append(media)
                else:
                    self.image.append(media)
            elif media.endswith('.mp3'):
                self.sound.append(media)
            elif media.endswith('.srt'):
                self.srt.append(media)
            elif media.endswith('.mp4') or media.endswith('.mkv'):
                self.video.append(media)

        # Calculer la taille totale des fichiers de la solution
        #self.size = self.verif_sol_install(device_serial,upload_casque_path)

        # Vérification de l'installation de la solution sur le casque
        start_time = time.time()
        self.size = self.verif_sol_install(device_serial, upload_casque_path)
        if self.size != 0:
            self.sol_install_on_casque = True
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"VERIFICATION FICHIERS EXISTANTS en {execution_time:.2f}s :")
        print(f"EXPERIENCE : {self.nom}, INTALL: {self.sol_install_on_casque},{self.size} octets")

        return self

    def quick_verif_sol_install(self, device_serial, upload_casque_path):
        """
        Vérifie si la solution est installée sur le casque en vérifiant l'existence
        du premier fichier de chaque répertoire (image, image360, sound, srt, video).

        Returns:
            bool: True si la solution est installée, False sinon.
        """
        directories = [self.image, self.image360, self.sound, self.srt, self.video]
        for dir in directories:
            if dir:
                first_file = upload_casque_path + dir[0]
                check_file_command = [self.config.adb_exe_path, "-s", device_serial, "shell", "ls", first_file]
                try:
                    output = subprocess.check_output(check_file_command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")
                    if first_file not in output:
                        print("fichier non trouvé")
                        return False
                except subprocess.CalledProcessError:
                    return False
        return True

    def check_file(self, device_serial, file_path):
        """
        Vérifie l'existence d'un fichier sur l'appareil et retourne sa taille.

        Args:
            device_serial (str): Le numéro de série de l'appareil.
            file_path (str): Le chemin du fichier à vérifier.

        Returns:
            tuple: (bool, int) True si le fichier est présent, False sinon et la taille du fichier.
        """
        check_file_command = [self.config.adb_exe_path, "-s", device_serial, "shell", "ls", "-l", file_path]

        try:
            output = subprocess.check_output(check_file_command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")
            if file_path not in output:
                print(f"Fichier non trouvé : {file_path}")
                return False
            else:
                # Extraire la taille du fichier de la sortie de la commande `ls -l`
                try:
                    file_size = int(output.split()[4])
                    return file_size
                except (IndexError, ValueError) as e:
                    print(f"Erreur lors de la lecture de la taille du fichier {file_path}: {e}")
                    return False
        except subprocess.CalledProcessError as e:
            #print(f"Erreur lors de la vérification du fichier : {file_path}")
            # Je ne print pas ici car si le fichier n'est pas trouvé on ne souhaite pas affiché une erreur puisque c'est une simple vérification
            return False

    def verif_sol_install(self, device_serial, upload_casque_path):
        """
        Vérifie si tous les fichiers de la solution sont installés sur l'appareil et calcule la taille totale.

        Args:
            device_serial (str): Le numéro de série de l'appareil.
            upload_casque_path (str): Le chemin de base des fichiers sur l'appareil.

        Returns:
            tuple: (bool, int) True si tous les fichiers sont présents, False sinon et la taille totale des fichiers.
        """
        directories = {
            "image": self.image,
            "image360": self.image360,
            "sound": self.sound,
            "srt": self.srt,
            "video": self.video
        }
        total_size = 0

        for subdir, files in directories.items():
            for file in files:
                file_path = upload_casque_path + file
                output = self.check_file(device_serial, file_path)
                if output == 0:
                    return False
                total_size += output
        return total_size
