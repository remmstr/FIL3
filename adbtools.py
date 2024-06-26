from config import Config
import os
import subprocess


class Adbtools:

    def __init__(self):
        self.config = Config.getInstance()
        
    def check_adb_connection(self):
        try:
            
            os.environ["PATH"] += os.pathsep + self.config.platform_tools_path
            output = subprocess.check_output(["adb", "start-server"])
            print(output.decode('utf-8'))
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur ADB : {e}")
            return False
        return True
    
    def grant_permissions(self,numero):
    
        commands = [
            ["pm", "grant", self.config.package_name, "android.permission.ACCESS_FINE_LOCATION"],
            ["pm", "grant", self.config.package_name, "android.permission.READ_EXTERNAL_STORAGE"],
            ["pm", "grant", self.config.package_name, "android.permission.WRITE_EXTERNAL_STORAGE"]
        ]
        for command in commands:
            full_command = [self.config.adb_exe_path, "-s", numero, "shell"] + command
            try:
                subprocess.run(full_command, check=True)
                print(f"Permission accordée avec succès : {command[-1]}")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'accord de la permission {command[-1]} : {e}")


    def configure_wifi_on_casque(self, ssid, password):
        if not ssid or not password:
            print("SSID or password is missing, cannot configure WiFi.")
            return

        try:
            # Connect to the WiFi network using adb
            # Example: Using the Android WiFi Configuration API instead of wpa_cli
            set_network_command = [
                "shell", "am", "broadcast", "-a", 
                "com.yourapp.CONFIGURE_WIFI", "--es", "ssid", ssid, "--es", "password", password
            ]
            result = subprocess.run([self.config.adb_exe_path] + set_network_command, text=True, capture_output=True, check=True)
            if result.stdout:
                print("WiFi configuration applied successfully.")
            else:
                print("Failed to apply WiFi configuration.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while configuring WiFi on the casque: {e}\n{e.stderr.decode()}")
