from ppadb.client import Client as AdbClient
from casque import Casque
import subprocess
import os
import sys
from adbtools import Adbtools

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
        self.adbtools.check_adb_connection()
        self.liste_casques = []
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.refresh_casques()

    def refresh_casques(self):
        self.liste_casques.clear()
        devices = self.client.devices()
        for device in devices:
            nouveau_casque = Casque()
            nouveau_casque.refresh_casque(device)
            self.liste_casques.append(nouveau_casque)

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

# Utilisation du Singleton
gestion_casques = GestionCasques.getInstance()
