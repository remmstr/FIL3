import subprocess

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
        if self.verif_sol_install(device_serial,upload_casque_path):
            self.sol_install_on_casque = True
        
        return self

    def verif_sol_install(self,device_serial,upload_casque_path):
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
