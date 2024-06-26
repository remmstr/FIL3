import os
import sys

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance.init_paths()
        return cls._instance

    def init_paths(self):
        self.adb_exe_path = self.config_path("platform-tools/adb.exe")
        self.json_file_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/hardware.json"
        self.package_name = "com.VRAI_Studio.Reverto"
        self.package_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto"
        self.local_archivage_path = "./Archivage"
        self.upload_casque_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded/upload"
        self.upload_path = "./Banque_de_solutions/upload"
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.GREEN = '\033[92m'

    def config_path(self, relative_path):
        """ Get absolute path to config, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)