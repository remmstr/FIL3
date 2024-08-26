import os
import sys
import platform
import traceback
import re
from singletonMeta import SingletonMeta

class Config(metaclass=SingletonMeta):
    def __init__(self):
        """Initialise la configuration en définissant les chemins nécessaires."""
        self.init_paths()

    def init_paths(self):
        """Initialise les chemins en fonction du système d'exploitation et crée les répertoires requis."""
        self.system_name = platform.system()

        if self.system_name == "Darwin":
            self.adb_exe_path = self.config_path("platform-tools/mac/adb")
            self.platform_tools_path = self.config_path("platform-tools/mac")
        elif self.system_name == "Windows":
            self.adb_exe_path = self.config_path("platform-tools/windows/adb.exe")
            self.platform_tools_path = self.config_path("platform-tools/windows")
        else:
            raise RuntimeError("Unsupported OS")

        print(f"ADB Path: {self.adb_exe_path}")
        print(f"Platform Tools Path: {self.platform_tools_path}")

        self.json_file_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/hardware.json"
        self.package_name = "com.VRAI_Studio.Reverto"
        self.package_old_name_PPV1 = "com.reverto.player"
        self.package_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto"
        self.local_archivage_path = self.config_path("./Archivage")
        self.upload_casque_path = "/sdcard/Android/data/com.VRAI_Studio.Reverto/files/Downloaded"
        self.Bibliothèque_de_solution_path = "./Bibliothèque_de_solution"
        self.APK_path = self.config_path("./APK")
        self.img_path = self.config_path("resources/images")
        self.img_path_menu = self.config_path("resources/images/image.png")
        self.img_path_icon_setting = self.config_path("resources/images/parametres.png")

        self.ensure_directory_exists(self.Bibliothèque_de_solution_path)
        self.ensure_directory_exists(self.APK_path)

    def safe_string(self, nom):
        """
        Crée une version sécurisée d'une chaîne de caractères pour l'utiliser comme nom de dossier.

        Args:
            nom (str): Le nom original à sécuriser.

        Returns:
            str: Le nom sécurisé, adapté pour être utilisé comme nom de dossier.
        """
        # Remplace les caractères non alphanumériques par des underscores
        safe_solution_name = re.sub(r'[^a-zA-Z0-9]', '_', nom)
        # Remplace les multiples underscores par un seul
        safe_solution_name = re.sub(r'_+', '_', safe_solution_name)
        # Supprime les underscores en début et fin de chaîne
        safe_solution_name = safe_solution_name.strip('_')

        return safe_solution_name

    def config_path(self, relative_path):
        """
        Crée un chemin absolu basé sur le chemin relatif fourni.

        Args:
            relative_path (str): Le chemin relatif à convertir.

        Returns:
            str: Le chemin absolu résultant.
        """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def ensure_directory_exists(self, path):
        """
        Vérifie si un répertoire existe, et le crée si nécessaire.

        Args:
            path (str): Le chemin du répertoire à vérifier ou à créer.
        """
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Le répertoire {path} a été créé.")

    def get_apk_version(self, brand_name):
        """
        Récupère la version de l'APK pour une marque donnée.

        Args:
            brand_name (str): Le nom de la marque pour laquelle récupérer la version de l'APK.

        Returns:
            str: La version de l'APK, ou "✗" si aucune version n'est trouvée ou en cas d'erreur.
        """
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
