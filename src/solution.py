import subprocess
import time
import threading

class Solution:
    def __init__(self):
        self.sol_install_on_casque = False
        self.nom = ""
        self.version = ""
        self.image = []
        self.image360 = []
        self.sound = []
        self.srt = []
        self.video = []


    def from_json(self, json_data, device_serial,upload_casque_path):
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

        # Vérification de l'installation de la solution sur le casque
        

        start_time = time.time()
        if self.quick_verif_sol_install(device_serial,upload_casque_path):
            self.sol_install_on_casque = True
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"VERIFICATION FICHIERS EXISTANTS en {execution_time:.2f}s :")
        print(f"EXPERIENCE : {self.nom}, INTALL: {self.sol_install_on_casque}")

        return self

    def quick_verif_sol_install(self,device_serial,upload_casque_path):
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
                check_file_command = ["adb", "-s", device_serial, "shell", "ls", first_file]
                try:
                    output = subprocess.check_output(check_file_command, stderr=subprocess.DEVNULL).decode("utf-8")
                    if first_file not in output:
                        print("fichier non trouvé")
                        return False
                except subprocess.CalledProcessError:
                    return False
        return True

    def check_file(self, device_serial, file_path, results, index, stop_event):
        """
        Vérifie l'existence d'un fichier sur l'appareil et met à jour le résultat.

        Args:
            device_serial (str): Le numéro de série de l'appareil.
            file_path (str): Le chemin du fichier à vérifier.
            results (list): Une liste pour stocker les résultats des vérifications.
            index (int): L'index dans la liste des résultats pour ce fichier.
            stop_event (threading.Event): Un événement pour indiquer l'arrêt des vérifications.

        Returns:
            None
        """
        if stop_event.is_set():
            return

        check_file_command = ["adb", "-s", device_serial, "shell", "ls", file_path]

        try:
            output = subprocess.check_output(check_file_command, stderr=subprocess.DEVNULL).decode("utf-8")
            if file_path not in output:
                results[index] = False
                stop_event.set()
                print(f"Fichier non trouvé : {file_path}")
            else:
                results[index] = True
        except subprocess.CalledProcessError:
            results[index] = False
            stop_event.set()
            #print(f"Erreur lors de la vérification du fichier : {file_path}")

    def verif_sol_install(self, device_serial, upload_casque_path):
        """
        Vérifie si tous les fichiers de la solution sont installés sur l'appareil.

        Args:
            device_serial (str): Le numéro de série de l'appareil.
            upload_casque_path (str): Le chemin de base des fichiers sur l'appareil.

        Returns:
            bool: True si tous les fichiers sont présents, False sinon.
        """
        directories = [self.image, self.image360, self.sound, self.srt, self.video]
        all_files = []

        # Créer une liste de tous les fichiers à vérifier
        for dir in directories:
            if dir:
                all_files.extend([upload_casque_path + file for file in dir])

        results = [None] * len(all_files)
        threads = []
        stop_event = threading.Event()

        # Lancer un thread pour chaque fichier à vérifier
        for i, file_path in enumerate(all_files):
            if stop_event.is_set():
                break
            thread = threading.Thread(target=self.check_file, args=(device_serial, file_path, results, i, stop_event))
            threads.append(thread)
            thread.start()

        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()

        # Si un fichier est manquant, retourner False
        if stop_event.is_set() or not all(results):
            return False

        # Tous les fichiers sont présents
        return True

    def print_light(self):
        """
        Affiche les détails principaux de la solution.
        """
        print(f"Solution: {self.nom}")
        print(f"  Installed on casque: {self.sol_install_on_casque}")
        print(f"  Version: {self.version}")
        
    def print(self):
        """
        Affiche les détails de la solution de manière formatée.
        """
        print(f"Solution: {self.nom}")
        print(f"  Installed on casque: {self.sol_install_on_casque}")
        print(f"  Version: {self.version}")

        
        print("  Images:")
        for img in self.image:
            print(f"    - {img}")
        print()
        
        print("  Images360:")
        for img360 in self.image360:
            print(f"    - {img360}")
        print()
        
        print("  Sounds:")
        for snd in self.sound:
            print(f"    - {snd}")
        print()
        
        print("  Subtitles:")
        for subtitle in self.srt:
            print(f"    - {subtitle}")
        print()
        
        print("  Videos:")
        for vid in self.video:
            print(f"    - {vid}")
        print()
