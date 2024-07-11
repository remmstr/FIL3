import os
import subprocess
    
def check_adb_connection(platform_tools_path):
        try:
            os.environ["PATH"] += os.pathsep + platform_tools_path
            output = subprocess.check_output(["adb", "start-server"])
            print(output.decode('utf-8'))
        except Exception as e:
            print(f"Erreur lors du démarrage du serveur ADB : {e}")
            return False
        return True

def grant_permissions(adb_exe_path, numero, package_name):
    commands = [
        ["pm", "grant", package_name, "android.permission.ACCESS_FINE_LOCATION"],
        ["pm", "grant", package_name, "android.permission.READ_EXTERNAL_STORAGE"],
        ["pm", "grant", package_name, "android.permission.WRITE_EXTERNAL_STORAGE"]
    ]
    for command in commands:
        full_command = [adb_exe_path, "-s", numero, "shell"] + command
        try:
            subprocess.run(full_command, check=True)
            print(f"Permission accordée avec succès : {command[-1]}")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'accord de la permission {command[-1]} : {e}")

def configure_wifi_on_casque(self, adb_exe_path, ssid, password):
    if not ssid or not password:
        print("SSID or password is missing, cannot configure WiFi.")
        return

    try:
        set_network_command = [
            "shell", "am", "broadcast", "-a", 
            "com.yourapp.CONFIGURE_WIFI", "--es", "ssid", ssid, "--es", "password", password
        ]

        result = subprocess.run([adb_exe_path] + set_network_command, text=True, capture_output=True, check=True)
        
        if "Broadcast completed: result=0" in result.stdout:
            print("Broadcast was sent, but no changes were made. Output:", result.stdout)
        else:
            print("WiFi configuration applied successfully. Output:", result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while configuring WiFi on the casque: {e}\n{e.stderr.decode()}")


