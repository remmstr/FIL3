from ppadb.client import Client as AdbClient
from casque import Casque
import subprocess 
import os


# le mieux serait de le metttre dans une classe GestionAdb dont heriterai GestionCasques
def check_adb_connection():
        try:
            # Assurez-vous que le chemin vers le dossier contenant 'adb' est correct
            adb_path = os.path.join(os.path.dirname(__file__), "platform-tools")
            os.environ["PATH"] += os.pathsep + adb_path

            output = subprocess.check_output(["adb", "start-server"])
            print(output.decode('utf-8'))
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur ADB : {e}")
            return False
        return True

class GestionCasques:

    def __init__(self):
        print("Init Gestion Casque")
        check_adb_connection()
        from ppadb.client import Client as AdbClient
        client = AdbClient(host="127.0.0.1", port=5037)

        self.liste_casques = []

        devices = client.devices()
        # enregistre toutes les infos pour chaque casque en supprimante les caractere parasites avec strip()
        for device in devices:
            a = Casque()
            a.numero = device.get_serial_no().strip()
            a.marque = device.shell("getprop ro.product.manufacturer").strip()
            a.modele = device.shell("getprop ro.product.model").strip()
            a.check_json_file()

            
            self.liste_casques.append(a)
    
    def print(self):
        for casque in self.liste_casques:
            casque.print()
            print( f"-" * 20)
        

            
    
     


