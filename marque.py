import os

class Marque:
    def __init__(self):
        self.nom = ""
        self.version_apk = ""
        self.APK_path = ""

    def setNom(self, nom: str):
        self.nom = nom
        self.choixApp()

    def choixApp(self):
        # Liste des noms d'APK que on va chercher dans le dossier APK
        apk_names = []

        # Parcourir les fichiers du dossier
        for file_name in os.listdir("./APK"):
            # Vérifier si le fichier se termine par ".apk"
            if file_name.endswith(".apk"):
                # Ajouter le nom de l'APK à la liste
                apk_names.append(file_name)
        
        # Parcourir la liste des noms d'APK
        for apk_name in apk_names:
            # Vérifier si la chaîne de caractères device_type se trouve dans le nom de l'APK
            if self.nom.lower() in apk_name.lower():
                self.version_apk = apk_name
                self.APK_path = "./APK/" + apk_name
                break
        else:
            print(" !!! AUCUNE APK trouvé ")
            
