import os
import sys
import platform
import traceback
import re
from singletonMeta import SingletonMeta

class Config(metaclass=SingletonMeta):
    def __init__(self):
        print("config")
        self.init_paths()

    def init_paths(self):

        self.system_name = platform.system()

        if self.system_name == "Darwin":
            self.adb_exe_path = self.config_path("platform-tools/mac/adb")
            self.platform_tools_path = self.config_path("platform-tools/mac")
        elif self.system_name == "Windows":
            self.adb_exe_path = self.config_path("platform-tools/windows/adb.exe")
            self.platform_tools_path = self.config_path("platform-tools/windows")
        else:
            raise RuntimeError("Unsupported OS")

        self.json_file_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/hardware.json"
        self.package_name = "com.VRAI_Studio.Reverto"
        self.package_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto"
        self.local_archivage_path = "./Archivage"
        self.upload_casque_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded"
        self.upload_path = "./Banque_de_solutions/upload"
        self.Banque_de_solution_path = "./Banque_de_solutions"
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'
        self.GREEN = '\033[92m'
        self.APK_path = "./APK"

        self.ensure_directory_exists(self.Banque_de_solution_path)
        self.ensure_directory_exists(self.APK_path)

    def config_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def ensure_directory_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Le répertoire {path} a été créé.")

    def get_apk_version(self, brand_name):
        try:
            apk_names = []
            for file_name in os.listdir(self.APK_path):
                if file_name.endswith(".apk"):
                    apk_names.append(file_name)

            for apk_name in apk_names:
                if brand_name.lower() in apk_name.lower():
                    version_match = re.search(r'(\d+\.\d+\.\d+)', apk_name)
                    if version_match:
                        return version_match.group(1)
                    return apk_name

            return "✗"  # Aucun APK trouvé

        except FileNotFoundError as e:
            print(f"Erreur: Répertoire ou fichier non trouvé. Détails: {e}")
            return "✗"
        except Exception as e:
            print(f"Erreur inattendue lors de la sélection de l'APK : {e}")
            traceback.print_exc()
            return "✗"

