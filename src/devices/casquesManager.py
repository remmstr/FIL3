
import subprocess
import threading
import traceback
import time

from ppadb.client import Client as AdbClient
from .adbtools import Adbtools
from .config import Config
from .singletonMeta import SingletonMeta
from .casque import Casque

# Built-in modules
import logging


class CasquesManager(metaclass=SingletonMeta):

    def __init__(self):
        """
        Initialise le gestionnaire de casques, configure ADB et récupère la liste initiale des casques connectés.
        """
        self.apk_folder = ""
        self.config = Config()
        self.adbtools = Adbtools()
        self.adbtools.check_adb_connection(self.config.platform_tools_path)
        self.liste_casques = []
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.refresh_casques()
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))
        

        

    def refresh_thread(self):
        """
        Démarre un thread pour rafraîchir la liste des casques.
        """
        try:
            self.casques.refresh_casques()
            time.sleep(2.5)
        except Exception as e:
            if self.app.running:
                self.app.handle_exception("Erreur lors de l'actualisation des casques", e)


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
        for i, casque in enumerate(self.liste_casques, 1):
            casque.marque.choixApp(apk_folder)
        # L'apk folder devait etre rafrachit à l'aide de refresh casque qui prenait en argument 
        # l'apk folder mais le rafrachissement ne marche pas de cette maniere donc je vais directement 
        # dans chaque casque rafraichir et ça marche
        self.apk_folder = apk_folder
    
    def refresh_casques(self):
        """
        Met à jour la liste des casques connectés en vérifiant les appareils connectés via ADB.
        """
        try:
            devices = self.client.devices()
        except Exception as e:
            self.log.info(f"Erreur lors de la récupération des appareils : {e}")
            traceback.print_exc()
            return

        current_casques = {casque.numero: casque for casque in self.liste_casques}
        new_casques = []

        for device in devices:
            try:
                numero = device.get_serial_no().strip()

                if numero in current_casques:
                    existing_casque = current_casques[numero]
                    existing_casque.refresh_casque(device, self.apk_folder)
                    new_casques.append(existing_casque)
                else:
                    nouveau_casque = Casque()
                    nouveau_casque.refresh_casque(device, self.apk_folder)
                    new_casques.append(nouveau_casque)
            except RuntimeError as e:
                # Specific handling for connection or authorization errors
                if "device unauthorized" in str(e) or "device offline" in str(e):
                    message = f"Erreur: le casque avec numéro de série {device.serial} est non autorisé ou hors ligne. Veuillez le rebrancher et vérifier les autorisations."
                    print(message)
                    #self.ui.handle_exception(message, e)  # Utilisation de la méthode handle_exception
                else:
                    message = f"Erreur lors de l'ajout du casque {device.serial}"
                    print(message)
                    #self.ui.handle_exception(message, e)
            except Exception as e:
                message = f"Erreur inconnue lors de l'ajout du casque {device.serial}: {e}"
                print(message)
                #self.ui.handle_exception(message, e)

        self.liste_casques = new_casques

        self.print_casques()




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

    def print_casques(self):
        """
        Affiche les informations de tous les casques gérés.
        """
        print(f"Affichage des casques : {self.liste_casques}")
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.print_casque()
            print("-" * 20)

    def install_All_APK(self):
        """
        Installe les APK sur tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            self.log.info(f"\nCasque #{i}:")
            casque.install_APK()
            print("-" * 20)

    def install_All_Solution(self):
        """
        Installe les solutions sur tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            self.log.info(f"\nCasque #{i}:")
            casque.add_solution()
            print("-" * 20)

    def archivage(self):
        """
        Archive les données de tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            self.log.info(f"\nCasque #{i}:")
            casque.archivage_casque()
            print("-" * 20)

    def share_wifi_to_ALL_casque(self):
        """
        Partage la configuration Wi-Fi avec tous les casques connectés.
        """
        for i, casque in enumerate(self.liste_casques, 1):
            self.log.info(f"\nCasque #{i}:")
            casque.share_wifi_to_casque()
            print("-" * 20)
