from casque import Casque
import subprocess
import traceback
from ppadb.client import Client as AdbClient
import adbtools
from config import Config
from singletonMeta import SingletonMeta

class GestionCasques(metaclass=SingletonMeta):

    def __init__(self):
        print("GestionsCasques created")
        self.config = Config()
        adbtools.check_adb_connection(self.config.platform_tools_path)
        self.liste_casques = []
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.refresh_casques()

    def refresh_casques(self):
        try:
            devices = self.client.devices()
        except Exception as e:
            print(f"Erreur lors de la récupération des appareils : {e}")
            traceback.print_exc()
            return

        self.liste_casques.clear()

        for device in devices:
            try:
                nouveau_casque = Casque()
                nouveau_casque.refresh_casque(device)
                self.liste_casques.append(nouveau_casque)
            except Exception as e:
                print(f"Erreur lors de l'ajout du casque {device} : {e}")
                traceback.print_exc()

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
            print(f"\nCasque #{i}:")
            casque.archivage_casque()
            print("-" * 20)

    def share_wifi_to_ALL_casque(self):
        for i, casque in enumerate(self.liste_casques, 1):
            print(f"\nCasque #{i}:")
            casque.share_wifi_to_casque()
            print("-" * 20)


