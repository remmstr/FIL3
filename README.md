# FIL
### A ecire avant usage:  pip install -U pure-python-adb
python -m PyInstaller --onefile --clean --hidden-import ppadb --add-data "platform-tools:platform-tools" FIL.py
python -m PyInstaller FIL.spec

# Diagramme des classes

Voici un diagramme des classes pour le projet.

```mermaid
classDiagram
    class Config {
        +getInstance() Config
        -init_paths()
        +config_path(relative_path: str) str
        +get_apk_version(brand_name: str) str
        +json_file_path: str
        +package_name: str
        +package_path: str
        +local_archivage_path: str
        +upload_casque_path: str
        +upload_path: str
        +Banque_de_solution_path: str
        +BLUE: str
        +RESET: str
        +GREEN: str
        +apk_directory: str
    }

    class Adbtools {
        +__init__()
        +check_adb_connection() bool
        +grant_permissions(numero: str)
        +configure_wifi_on_casque(ssid: str, password: str)
    }

    class App {
        -root: Tk
        -casques: GestionCasques
        -config: Config
        -progress_bars: dict
        +__init__(root: Tk)
        +create_widgets()
        +load_image(path: str, parent: Frame)
        +afficher_casques()
        +create_progress_bar(item_id: str) DoubleVar
        +installer_apks_et_solutions()
        +_installer_apks_et_solutions()
        +install_apk_with_progress(casque: Casque) bool
        +add_solution_with_progress(casque: Casque)
        +update_progress_from_output(casque_numero: str, output: str)
        +update_progress(casque_numero: str, value: int)
        +highlight_row(casque_numero: str, color: str)
        +update_status(casque_numero: str, status: str)
        +archiver_casque()
        +configurer_wifi()
        +quit()
        +track_devices()
        +download_banque_solutions()
        +handle_exception(message: str, exception: Exception)
        +log_debug(message: str)
        +write(message: str)
        +flush()
    }

    class Casque {
        +str device
        +str numero
        +Marque marque
        +str modele
        +str version_apk
        +str JSON_path
        +list~Solution~ solutions_install

        +__init__()
        +refresh_casque(device: Device)
        +print()
        +check_json_file() bool
        +install_APK()
        +uninstall_APK()
        +get_installed_apk_version() str
        +add_solution()
        +archivage_casque()
        +get_wifi_credentials() tuple
        +share_wifi_to_casque()
        +check_wifi_connection(ssid: str)
        +reconnect_wifi()
    }

    class GestionCasques {
        +getInstance() GestionCasques
        +refresh_casques()
        +print()
        +install_All_APK()
        +install_All_Solution()
        +archivage()
        +share_wifi_to_ALL_casque()
    }

    class Marque {
        +setNom(nom: str)
        +choixApp()
    }

    class Solution {
        +sol_install_on_casque: bool
        +nom: str
        +version: str
        +image: str
        +image360: str
        +sound: str
        +srt: str
        +video: str
    }

    Config <-- Adbtools : instancie
    Config <-- Casque : instancie
    Config <-- GestionCasques : instancie
    Config <-- App : accède
    Adbtools <-- Casque : utilise
    GestionCasques <-- Casque : utilise
    GestionCasques <-- App : instancie
    Casque <-- Marque : instancie
    App <-- GestionCasques : accède
