import os
import traceback

class Marque:
    def __init__(self):
        """
        Initialise un objet Marque avec des attributs pour le nom, la version de l'APK, et le chemin de l'APK.
        """
        self.nom = ""
        self.version_apk = ""
        self.APK_path = ""

    def setNom(self, nom: str, apk_folder):
        """
        Définit le nom de la marque et sélectionne l'application appropriée en fonction du dossier APK.

        Args:
            nom (str): Le nom de la marque.
            apk_folder (str): Le dossier contenant les fichiers APK.
        """
        if(self.nom == "HTC") : nom = "Vive" #car le nom du manufacturier n'est pas le meme que le nom du store pour HTC
        self.nom = nom
        self.choixApp(apk_folder)

    def choixApp(self, apk_folder):
        """
        Sélectionne l'APK correspondant au nom de la marque dans le dossier spécifié.

        Args:
            apk_folder (str): Le dossier contenant les fichiers APK.

        Exceptions:
            FileNotFoundError: Si le répertoire ou les fichiers ne sont pas trouvés.
            Exception: Pour toute autre erreur lors de la sélection de l'APK.
        """
        try:
            apk_names = []
            apk_directory = "./APK/" + apk_folder
            
            # Vérifier si le répertoire existe
            if not os.path.exists(apk_directory):
                print(f"Le répertoire {apk_directory} n'existe pas.")
                return

            for file_name in os.listdir(apk_directory):
                if file_name.endswith(".apk"):
                    apk_names.append(file_name)
            
            for apk_name in apk_names:
                if self.nom.lower() in apk_name.lower():
                    self.version_apk = apk_name
                    self.APK_path = os.path.join(apk_directory, apk_name)
                    break

        except FileNotFoundError as e:
            print(f"Erreur: Répertoire ou fichier non trouvé. Détails: {e}")
        except Exception as e:
            print(f"Erreur inattendue lors de la sélection de l'APK : {e}")
            traceback.print_exc()
