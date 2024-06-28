import os
import sys

class Config:
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.init_paths()
        return cls._instance

    def __init__(self):
        # L'initialisation réelle se fait dans init_paths pour éviter la réinitialisation si __init__ est appelé à nouveau.
        pass

    def init_paths(self):
        self.adb_exe_path = self.config_path("platform-tools/adb.exe")
        self.json_file_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/hardware.json"
        self.package_name = "com.VRAI_Studio.Reverto"
        self.package_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto"
        self.local_archivage_path = "./Archivage"
        self.upload_casque_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded/upload"
        self.upload_path = "./Banque_de_solutions/upload"
        self.Banque_de_solution_path = "./Banque_de_solutions"
        self.platform_tools_path = self.config_path("platform-tools")
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.GREEN = '\033[92m'

    def config_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

# Utilisation de Config
config = Config.getInstance()
