from ppadb.client import Client as AdbClient
from casque import Casque
import subprocess
import os
import sys
from adbtools import Adbtools
import traceback
from config import Config

class GestionCasques:
    _instance = None  # Attribut privé pour stocker l'unique instance

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance.__init()
        return cls._instance

    def __init(self):  # Init privé pour éviter la création directe d'instances
        self.adbtools = Adbtools()
        self.config = Config.getInstance()
        self.adbtools.check_adb_connection()
        self.liste_casques = []
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.refresh_casques()

    def refresh_casques(self):
        try:
            devices = self.client.devices()
            #print(f"Appareils trouvés : {devices}")
        except Exception as e:
            print(f"Erreur lors de la récupération des appareils : {e}")
            traceback.print_exc()
            return

        self.liste_casques.clear()
        
        for device in devices:
            #if not self.is_device_online(device):
                #print(f"L'appareil {device} est hors ligne et ne sera pas ajouté.")
            #    continue
            try:
                nouveau_casque = Casque()
                nouveau_casque.refresh_casque(device)
                self.liste_casques.append(nouveau_casque)
                #print(f"Casque ajouté : {nouveau_casque}")
            except Exception as e:
                print(f"Erreur lors de l'ajout du casque {device} : {e}")
                traceback.print_exc()

        #print(f"Liste finale des casques : {self.liste_casques}")

    def is_device_online(self, device):
        try:
            device.get_serial_no()
            return True
        except RuntimeError:
            return False

    def print(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.print()
            print("-" * 20)

    def install_All_APK(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.install_APK()
            print("-" * 20)

    def install_All_Solution(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.add_solution()
            print("-" * 20)

    def archivage(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{1}:")
            casque.archivage_casque()
            print("-" * 20)

    def share_wifi_to_ALL_casque(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{1}:")
            casque.share_wifi_to_casque()
            print("-" * 20)


