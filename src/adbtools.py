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

def is_permission_granted(adb_exe_path, numero, package_name, permission):
    try:
        # Vérifier si la permission est déjà accordée
        check_command = [
            adb_exe_path, "-s", numero, "shell", "dumpsys", "package", package_name
        ]
        output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL).decode("utf-8")
        return f"grantedPermissions: {permission}" in output
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification de la permission {permission} : {e}")
        return False

def grant_permissions(adb_exe_path, numero, package_name):
    permissions = [
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        # "android.permission.ACCESS_WIFI_STATE",
        # "android.permission.CHANGE_WIFI_STATE"
    ]
    for permission in permissions:
        if not is_permission_granted(adb_exe_path, numero, package_name, permission):
            full_command = [adb_exe_path, "-s", numero, "shell", "pm", "grant", package_name, permission]
            try:
                subprocess.run(full_command, check=True)
                #print(f"Permission accordée avec succès : {permission}")
            except subprocess.CalledProcessError as e:
                print(f"Erreur lors de l'accord de la permission {permission} : {e}")
        else:
            print(f"La permission {permission} est déjà accordée.")

def is_device_awake(adb_exe_path, numero):
    try:
        command = [adb_exe_path, "-s", numero, "shell", "dumpsys power | grep 'Display Power'"]
        output = subprocess.check_output(command).decode('utf-8')
        if 'state=ON' in output:
            return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification de l'état de l'appareil : {e}")
    return False

def wake_up_device(adb_exe_path, numero):
    if not is_device_awake(adb_exe_path, numero):
        command = [adb_exe_path, "-s", numero, "shell", "input", "keyevent", "KEYCODE_POWER"]
        try:
            subprocess.run(command, check=True)
            #print("Commande POWER exécutée avec succès")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande POWER : {e}")
    else:
        pass
        #print("L'appareil est déjà éveillé")

def start_application(adb_exe_path, numero, package_name):
    try:
        # Obtenir le nom complet de l'activité principale
        activity_output = subprocess.check_output(
            [adb_exe_path, "-s", numero, "shell", "cmd", "package", "resolve-activity", "--brief", package_name],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()

        # Extraire uniquement la ligne contenant le nom de l'activité (dernière ligne normalement)
        activity_name = activity_output.split('\n')[-1].strip()
        print(f"Activity Name: {activity_name}")

        # Démarrer l'application avec le nom complet de l'activité
        start_command = [
            adb_exe_path, "-s", numero, "shell", "am", "start",
            "-n", activity_name
        ]
        subprocess.run(start_command, check=True)
        print(f"Application {package_name} démarrée avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'obtention ou du démarrage de l'activité principale : {e}")

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


def check_battery_level(adb_exe_path, device_serial):
    """
    Vérifie le niveau de batterie de l'appareil.

    Args:
        adb_exe_path (str): Le chemin vers l'exécutable ADB.
        device_serial (str): Le numéro de série de l'appareil.

    Returns:
        int: Le niveau de batterie en pourcentage, ou -1 en cas d'erreur.
    """
    try:
        battery_info_command = [adb_exe_path, "-s", device_serial, "shell", "dumpsys", "battery"]
        output = subprocess.check_output(battery_info_command, stderr=subprocess.STDOUT).decode("utf-8")

        for line in output.split('\n'):
            if 'level' in line:
                level = int(line.split(':')[1].strip())
                return level
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la vérification du niveau de batterie : {e.output.decode('utf-8')}")
    except Exception as e:
        print(f"Erreur inattendue lors de la vérification du niveau de batterie : {e}")

    return -1
