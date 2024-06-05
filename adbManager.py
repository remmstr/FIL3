from ppadb.client import Client as AdbClient
import subprocess
from pathlib import Path
import re


class AdbManager:
    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        print(self.client.version())
        self.devices = self.client.devices()
        for device in self.devices:
            print(device)

    def connect_to_device(self):
        if self.devices:
            for device in self.devices:
                print(device.get_serial_no())
                return
        else:
            print("--- Aucun appareil connecté.")
    

    def install_apk_on_all_devices(apk_path, host="127.0.0.1", port=5037):
        """
        Install an APK on all connected devices.
        """
        client = AdbClient(host=host, port=port)
        devices = client.devices()
        for device in devices:
            device.install(apk_path)

    def check_apk_installed_on_all_devices(package_name, host="127.0.0.1", port=5037):
        """
        Check if an APK is installed on all connected devices.
        """
        client = AdbClient(host=host, port=port)
        devices = client.devices()
        for device in devices:
            print(f"Is {package_name} installed on {device}: {device.is_installed(package_name)}")

    def uninstall_apk_on_all_devices(package_name, host="127.0.0.1", port=5037):
        """
        Uninstall an APK from all connected devices.
        """
        client = AdbClient(host=host, port=port)
        devices = client.devices()
        for device in devices:
            device.uninstall(package_name)

    def execute_shell_command(device_id, command, host="127.0.0.1", port=5037):
        """
        Execute a shell command on a specific device.
        """
        client = AdbClient(host=host, port=port)
        device = client.device(device_id)
        device.shell(command)


    def push_file_or_folder(source, destination, device_id="emulator-5554", host="127.0.0.1", port=5037):
        """
        Push a file or folder to a specific device.
        """
        client = AdbClient(host=host, port=port)
        device = client.device(device_id)
        device.push(source, destination)

    def pull_file(source, destination, device_id="emulator-5554", host="127.0.0.1", port=5037):
        """
        Pull a file from a specific device to a local destination.
        """
        client = AdbClient(host=host, port=port)
        device = client.device(device_id)
        device.pull(source, destination)

    def connect_to_device_over_network(ip_address, port=5555, host="127.0.0.1", adb_port=5037):
        """
        Connect to a device over a network.
        """
        client = AdbClient(host=host, port=adb_port)
        client.remote_connect(ip_address, port)

    def disconnect_all_devices(host="127.0.0.1", port=5037):
        """
        Disconnect all connected devices.
        """
        client = AdbClient(host=host, port=port)
        client.remote_disconnect()

    def disconnect_device(ip_address, port=5555, host="127.0.0.1", adb_port=5037):
        """
        Disconnect a specific device from the network.
        """
        client = AdbClient(host=host, port=adb_port)
        client.remote_disconnect(ip_address, port)