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