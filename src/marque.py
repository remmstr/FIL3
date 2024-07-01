import os
import traceback

class Marque:
    def __init__(self):
        self.nom = ""
        self.version_apk = ""
        self.APK_path = ""

    def setNom(self, nom: str):
        self.nom = nom
        self.choixApp()

    def choixApp(self):
        try:
            apk_names = []
            apk_directory = "./APK"
            
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
