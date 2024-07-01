import os
import sys
import platform

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
        # Détecter le système d'exploitation
        system = platform.system()
        self.system_name = system

        # Configurer les chemins en fonction du système d'exploitation
        if system == "Darwin":  # macOS
            self.adb_exe_path = self.config_path("platform-tools/mac/adb")
            self.platform_tools_path = self.config_path("platform-tools/mac")
        elif system == "Windows":  # Windows
            self.adb_exe_path = self.config_path("platform-tools/windows/adb.exe")
            self.platform_tools_path = self.config_path("platform-tools/windows")
        else:
            raise RuntimeError("Unsupported OS")

        self.json_file_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/hardware.json"
        self.package_name = "com.VRAI_Studio.Reverto"
        self.package_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto"
        self.local_archivage_path = "./Archivage"
        self.upload_casque_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded/upload"
        self.upload_path = "./Banque_de_solutions/upload"
        self.Banque_de_solution_path = "./Banque_de_solutions"
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.GREEN = '\033[92m'

    def config_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

