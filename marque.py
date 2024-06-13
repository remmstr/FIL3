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
        apk_names = []
        for file_name in os.listdir("./APK"):
            if file_name.endswith(".apk"):
                apk_names.append(file_name)
        
        for apk_name in apk_names:
            if self.nom.lower() in apk_name.lower():
                self.version_apk = apk_name
                self.APK_path = os.path.join("./APK", apk_name)
                break
        else:
            print(" !!! AUCUNE APK trouvé ")