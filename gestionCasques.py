from ppadb.client import Client as AdbClient
from casque import Casque


class GestionCasques:

    def __init__(self):
        print("Init Gestion Casque")
        from ppadb.client import Client as AdbClient
        client = AdbClient(host="127.0.0.1", port=5037)
        print(client.version())
        devices = client.devices()
        for device in devices:
            print(device.get_serial_no())
            a = Casque()
            a.numero = device.get_serial_no()
            

     




    #def list_devices():
    #    devices = self.client.devices()
     #   if devices:
    #        for device in devices:
     #           print(device.get_serial_no())
     #           return
     #   else:
    #        print("--- Aucun appareil connecté.")
     #   input("Appuyez sur Entrée pour fermer la fenêtre...")