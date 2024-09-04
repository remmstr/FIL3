import os
import subprocess
import platform  # Import to check the OS type
import logging

class Adbtools:
    def __init__(self):
        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

    def check_file_exists(self, filepath):
        """
        Vérifie si un fichier existe à un chemin spécifié.

        Args:
            filepath (str): Le chemin vers le fichier à vérifier.

        Raises:
            FileNotFoundError: Si le fichier n'est pas trouvé au chemin spécifié.
        """
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"Le fichier spécifié est introuvable: {filepath}")

    def check_adb_connection(self, platform_tools_path):
        """
        Vérifie la connexion ADB et démarre le serveur ADB si nécessaire.

        Args:
            platform_tools_path (str): Le chemin vers le dossier des outils de plateforme ADB.

        Returns:
            bool: True si la connexion ADB est réussie, False en cas d'échec.
        """
        try:
            os.environ["PATH"] += os.pathsep + platform_tools_path
            self.log.info(f"Demarrage du serveur adb {platform_tools_path}")
            # Conditionally set flags based on OS
            if platform.system() == "Windows":
                subprocess.check_output(["adb", "start-server"], stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.check_output(["adb", "start-server"], stderr=subprocess.DEVNULL)
        except Exception as e:
            self.log.info(f"Erreur lors du démarrage du serveur ADB : {e}")
            return False
        return True

    def is_permission_granted(self, adb_exe_path, numero, package_name, permission):
        """
        Vérifie si une permission spécifique est accordée à une application.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.
            package_name (str): Le nom du package de l'application.
            permission (str): La permission à vérifier.

        Returns:
            bool: True si la permission est accordée, False sinon.
        """
        try:
            check_command = [
                adb_exe_path, "-s", numero, "shell", "dumpsys", "package", package_name
            ]
            # Conditionally set flags based on OS
            if platform.system() == "Windows":
                output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")
            else:
                output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL).decode("utf-8")
            return f"grantedPermissions: {permission}" in output
        except subprocess.CalledProcessError as e:
            self.log.info(f"Erreur lors de la vérification de la permission {permission} : {e}")
            return False

    def grant_permissions(self, adb_exe_path, numero, package_name):
        """
        Accorde les permissions nécessaires à une application.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.
            package_name (str): Le nom du package de l'application.
        """
        permissions = [
            "android.permission.ACCESS_FINE_LOCATION",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
        ]
        for permission in permissions:
            if not self.is_permission_granted(adb_exe_path, numero, package_name, permission):
                full_command = [adb_exe_path, "-s", numero, "shell", "pm", "grant", package_name, permission]
                try:
                    # Conditionally set flags based on OS
                    if platform.system() == "Windows":
                        subprocess.run(full_command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                    else:
                        subprocess.run(full_command, check=True, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError as e:
                    pass

    def is_device_awake(self, adb_exe_path, numero):
        """
        Vérifie si l'appareil est éveillé.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.

        Returns:
            bool: True si l'appareil est éveillé, False sinon.
        """
        try:
            command = [adb_exe_path, "-s", numero, "shell", "dumpsys power | grep 'Display Power'"]
            # Conditionally set flags based on OS
            if platform.system() == "Windows":
                output = subprocess.check_output(command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8')
            else:
                output = subprocess.check_output(command, stderr=subprocess.DEVNULL).decode('utf-8')
            if 'state=ON' in output:
                return True
        except subprocess.CalledProcessError as e:
            self.log.info(f"Erreur lors de la vérification de l'état de l'appareil : {e}")
        return False

    def wake_up_device(self, adb_exe_path, numero):
        """
        Réveille l'appareil s'il est en veille.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.
        """
        if not self.is_device_awake(adb_exe_path, numero):
            command = [adb_exe_path, "-s", numero, "shell", "input", "keyevent", "KEYCODE_POWER"]
            try:
                # Conditionally set flags based on OS
                if platform.system() == "Windows":
                    subprocess.run(command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.run(command, check=True, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                self.log.info(f"Erreur lors de l'exécution de la commande POWER : {e}")

    def start_application(self, adb_exe_path, numero, package_name):
        """
        Démarre une application sur l'appareil.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.
            package_name (str): Le nom du package de l'application.
        """
        try:
            # Obtenir le nom complet de l'activité principale
            activity_output = subprocess.check_output(
                [adb_exe_path, "-s", numero, "shell", "cmd", "package", "resolve-activity", "--brief", package_name],
                stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            ).decode("utf-8").strip()

            # Extraire le nom de l'activité (dernière ligne normalement)
            activity_name = activity_output.split('\n')[-1].strip()

            # Démarrer l'application avec le nom complet de l'activité
            start_command = [
                adb_exe_path, "-s", numero, "shell", "am", "start",
                "-n", activity_name
            ]
            if platform.system() == "Windows":
                subprocess.run(start_command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run(start_command, check=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self.log.info(f"Erreur lors de l'obtention ou du démarrage de l'activité principale : {e}")

    def stop_application(self, adb_exe_path, numero, package_name):
        """
        Arrête une application en cours d'exécution sur l'appareil.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.
            package_name (str): Le nom du package de l'application.
        """
        try:
            stop_command = [adb_exe_path, "-s", numero, "shell", "am", "force-stop", package_name]
            if platform.system() == "Windows":
                subprocess.run(stop_command, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run(stop_command, check=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            self.log.info(f"Erreur lors de l'arrêt de l'application {package_name} : {e}")

    def is_application_running(self, adb_exe_path, numero, package_name):
        """
        Vérifie si une application est en cours d'exécution sur l'appareil.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            numero (str): Le numéro de série de l'appareil.
            package_name (str): Le nom du package de l'application.

        Returns:
            bool: True si l'application est en cours d'exécution, False sinon.
        """
        try:
            check_command = [adb_exe_path, "-s", numero, "shell", "pidof", package_name]
            if platform.system() == "Windows":
                output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8").strip()
            else:
                output = subprocess.check_output(check_command, stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if output:
                return True
        except subprocess.CalledProcessError:
            pass
        return False

    def configure_wifi_on_casque(self, adb_exe_path, ssid, password):
        """
        Configure le Wi-Fi sur l'appareil en envoyant un broadcast.

        Args:
            adb_exe_path (str): Le chemin vers l'exécutable ADB.
            ssid (str): Le SSID du réseau Wi-Fi.
            password (str): Le mot de passe du réseau Wi-Fi.
        """
        if not ssid or not password:
            self.log.info("SSID or password is missing, cannot configure WiFi.")
            return

        try:
            set_network_command = [
                "shell", "am", "broadcast", "-a", 
                "com.yourapp.CONFIGURE_WIFI", "--es", "ssid", ssid, "--es", "password", password
            ]

            if platform.system() == "Windows":
                result = subprocess.run([adb_exe_path] + set_network_command, text=True, capture_output=True, check=True, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                result = subprocess.run([adb_exe_path] + set_network_command, text=True, capture_output=True, check=True, stderr=subprocess.DEVNULL)
            
            if "Broadcast completed: result=0" in result.stdout:
                self.log.info("Broadcast was sent, but no changes were made. Output:", result.stdout)
            else:
                self.log.info("WiFi configuration applied successfully. Output:", result.stdout)

        except subprocess.CalledProcessError as e:
            self.log.info(f"An error occurred while configuring WiFi on the casque: {e}\n{e.stderr.decode()}")

    def check_battery_level(self, adb_exe_path, device_serial):
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
            if platform.system() == "Windows":
                output = subprocess.check_output(battery_info_command, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW).decode("utf-8")
            else:
                output = subprocess.check_output(battery_info_command, stderr=subprocess.STDOUT).decode("utf-8")

            for line in output.split('\n'):
                if 'level' in line:
                    level = int(line.split(':')[1].strip())
                    return level
        except subprocess.CalledProcessError as e:
            self.log.info(f"Erreur lors de la vérification du niveau de batterie : {e.output.decode('utf-8')}")
        except Exception as e:
            self.log.info(f"Erreur inattendue lors de la vérification du niveau de batterie : {e}")

        return -1
