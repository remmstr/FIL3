from casque import Casque
import subprocess
import traceback
from ppadb.client import Client as AdbClient
import adbtools
from config import Config
from singletonMeta import SingletonMeta

class CasquesManager(metaclass=SingletonMeta):

    def __init__(self):
        """
        Initialise le gestionnaire de casques, configure ADB et récupère la liste initiale des casques connectés.
        """
        self.apk_folder = ""
        self.config = Config()
        adbtools.check_adb_connection(self.config.platform_tools_path)
        self.liste_casques = []
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.refresh_casques()

    def get_liste_casque(self):
        """
        Retourne la liste des casques actuellement gérés.

        Returns:
            list: Liste des objets Casque actuellement gérés.
        """
        return self.liste_casques

    def set_apk_folder(self, apk_folder):
        """
        Définit le dossier APK où se trouvent les fichiers APK à installer sur les casques.

        Args:
            apk_folder (str): Le chemin du dossier contenant les fichiers APK.
        """
        self.apk_folder = apk_folder
    
    def refresh_casques(self):
        """
        Met à jour la liste des casques connectés en vérifiant les appareils connectés via ADB.
        """
        try:
            devices = self.client.devices()
        except Exception as e:
            print(f"Erreur lors de la récupération des appareils : {e}")
            traceback.print_exc()
            return

        # Création d'un dictionnaire temporaire pour les casques actuels
        current_casques = {casque.numero: casque for casque in self.liste_casques}

        # Liste temporaire pour les nouveaux casques
        new_casques = []

        for device in devices:
            numero = None  # Initialisation avec une valeur par défaut
            try:
                # Obtenir le numéro de série du device
                numero = device.get_serial_no().strip()

                if numero in current_casques:
                    # Si le casque existe déjà, on le met à jour
                    existing_casque = current_casques[numero]
                    existing_casque.refresh_casque(device, self.apk_folder)
                    new_casques.append(existing_casque)
                else:
                    # Sinon, on crée un nouveau casque
                    nouveau_casque = Casque()
                    nouveau_casque.refresh_casque(device, self.apk_folder)
                    new_casques.append(nouveau_casque)
            except Exception as e:
                if numero:
                    print(f"Erreur lors de l'ajout du casque {device} (numéro de série: {numero}) : {e}")
                else:
                    print(f"Erreur lors de l'ajout du casque {device} : {e}")
                # print(traceback.format_exc())

        # Remplacer la liste des casques par la nouvelle liste mise à jour
        self.liste_casques = new_casques


    def is_device_online(self, device):
        """
        Vérifie si un appareil est en ligne (connecté) via ADB.

        Args:
            device (ppadb.device.Device): L'objet appareil à vérifier.

        Returns:
            bool: True si l'appareil est en ligne, False sinon.
        """
        try:
            device.get_serial_no()
            return True
        except RuntimeError:
            return False

    def print(self):
        """
        Affiche les informations de tous les casques gérés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.print()
            print("-" * 20)

    def install_All_APK(self):
        """
        Installe les APK sur tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.install_APK()
            print("-" * 20)

    def install_All_Solution(self):
        """
        Installe les solutions sur tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.add_solution()
            print("-" * 20)

    def archivage(self):
        """
        Archive les données de tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.archivage_casque()
            print("-" * 20)

    def share_wifi_to_ALL_casque(self):
        """
        Partage la configuration Wi-Fi avec tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.share_wifi_to_casque()
            print("-" * 20)
