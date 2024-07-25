# FIL3


## Installation des dépendances

Pour exécuter ce projet, suivez les étapes ci-dessous :

#### 1. Créer un environnement virtuel
Il est recommandé de créer un environnement virtuel pour isoler les dépendances du projet. Pour ce faire, utilisez la commande suivante dans ke dossier orijet, téléchargé cloner prélablement :
```sh
python3 -m venv venv
```
#### 2. Activer l'environnement virtuel

Sur macOS et Linux :
```sh
source venv/bin/activate
```
Sur Windows :
```sh
venv\Scripts\activate
```

#### 3. Installer les dépendances
Installez les dépendances requises à partir du fichier requirements.txt :

```sh
pip install -r config/requirements.txt
```

#### 4. Exécuter le projet
Une fois les dépendances installées, vous pouvez exécuter le projet comme suit :
```sh
python src/FIL_interface.py
```
Si il y a une erreur sur le lancement du serveur adb (sur mac), cela peut être du à une absence d'autorisation
```sh
sudo chmod +x platform-tools/mac/adb
```

Notes supplémentaires -> Si vous ajoutez de nouvelles dépendances, pensez à mettre à jour le fichier requirements.txt en utilisant la commande suivante :
```sh
pip freeze > requirements.txt
```

Désactiver l'environnement virtuel : Pour désactiver l'environnement virtuel, utilisez la commande :
```sh
deactivate
```


## Création du fichier exécutable sur mac et windows
```sh
python -m PyInstaller config/FIL3.spec
```

## Diagramme de classes

Voici un diagramme de classes pour le projet.

```mermaid
classDiagram
    class Casque {
        +str device
        +str numero
        +Marque marque
        +str modele
        +int battery_level
        +str version_apk
        +str JSON_path
        +str JSON_size
        +list~SolutionCasque~ solutions_casque
        +str code
        +str name
        +str entreprise_association
        +float download_progress
        +Config config
        +threading.Lock lock
        +threading.Lock refresh_lock
        +BiblioManager biblio
        +void refresh_casque(device)
        +list~SolutionCasque~ load_solutions_from_json()
        +bool check_old_apk_installed()
        +int get_json_file_size()
        +str get_installed_apk_version()
        +str getEntreprise()
        +bool is_solution_in_library(solution)
        +bool is_solution_in_library_old(solution)
        +str check_json_file()
        +list~SolutionCasque~ getListSolInstall()
        +void push_solutions()
        +void push_solution_with_progress(solution_json_casque, solution_biblio)
        +void push_solution(solution)
        +void pull_solutions()
        +void pull_solution(solution)
        +tuple~int, int~ calculate_total_files_and_size(solution_dir)
        +void copy_media_file(source_dir, target_dir, solution_name, direction)
        +void add_solution()
        +void install_APK()
        +void uninstall_APK()
        +void archivage_casque()
        +bool is_wifi_connected()
        +void share_wifi_to_casque()
        +void check_wifi_connection(ssid)
        +void reconnect_wifi()
        +void _log_message(message)
    }

    class CasquesManager {
        +Config config
        +list~Casque~ liste_casques
        +AdbClient client
        +void refresh_casques()
        +bool is_device_online(device)
        +void print()
        +void install_All_APK()
        +void install_All_Solution()
        +void archivage()
        +void share_wifi_to_ALL_casque()
    }

    class BiblioManager {
        +Config config
        +list~SolutionBiblio~ liste_solutions
        +void print()
        +list~SolutionBiblio~ get_sols_bibli()
        +SolutionBiblio is_sol_in_library(solution)
    }

    class Config {
        +str adb_exe_path
        +str platform_tools_path
        +str json_file_path
        +str package_name
        +str package_old_name_PPV1
        +str package_path
        +str local_archivage_path
        +str upload_casque_path
        +str upload_path
        +str Banque_de_solution_path
        +str APK_path
        +str img_path
        +void init_paths()
        +str safe_string(nom)
        +str config_path(relative_path)
        +void ensure_directory_exists(path)
        +str get_apk_version(brand_name)
    }

    class SolutionBiblio {
        +str nom
        +list~str~ image
        +list~str~ image360
        +list~str~ sound
        +list~str~ srt
        +list~str~ video
        +int size
    }

    class SolutionCasque {
        +str nom
        +list~str~ image
        +list~str~ image360
        +list~str~ sound
        +list~str~ srt
        +list~str~ video
        +bool sol_install_on_casque
        +SolutionCasque from_json(json_data, device_serial, upload_casque_path)
        +bool quick_verif_sol_install(device_serial, upload_casque_path)
        +tuple~bool, int~ check_file(device_serial, file_path)
        +int verif_sol_install(device_serial, upload_casque_path)
    }

    class Solution {
        +str nom
        +str version
        +list~str~ image
        +list~str~ image360
        +list~str~ sound
        +list~str~ srt
        +list~str~ video
        +int size
        +void get_sol_size()
        +void print_light()
        +void print()
    }

    class Marque {
        +str nom
        +str version_apk
        +str APK_path
        +void setNom(nom)
        +void choixApp()
    }

    class adbtools {
        +bool check_adb_connection(platform_tools_path)
        +bool is_permission_granted(adb_exe_path, numero, package_name, permission)
        +void grant_permissions(adb_exe_path, numero, package_name)
        +bool is_device_awake(adb_exe_path, numero)
        +void wake_up_device(adb_exe_path, numero)
        +void start_application(adb_exe_path, numero, package_name)
        +void configure_wifi_on_casque(adb_exe_path, ssid, password)
        +int check_battery_level(adb_exe_path, device_serial)
    }
        class FIL_interface {
        +bool running
        +BiblioManager biblio_manager
        +CasquesManager casques
        +Config config
        +UI_Front ui_front
        +UI_Back ui_back
        +threading.Event stop_event
        +threading.Thread tracking_thread
        +void start()
        +void log_debug(message)
        +void handle_exception(message, exception)
        +void update_progress(casque_numero, value)
        +void update_progress_from_output(casque_numero, output)
        +void highlight_row(casque_numero, color)
        +void update_status(casque_numero, status)
    }

    class UI_Front {
        +tk.Tk root
        +FIL_interface app
        +dict progress_bars
        +dict widget_cache
        +void create_widgets()
        +void load_image(path, parent)
        +void create_apk_frame(parent)
        +void create_install_button(parent)
        +void create_debug_area()
        +void create_table_frame()
        +void create_table_headers()
        +void create_banque_button()
        +void create_biblio_solutions_button()
        +void show_biblio_solutions()
        +void afficher_casques()
        +tk.Frame create_casque_row(index, casque)
        +void update_casque_row(index, casque)
        +void update_progress_bars()
        +tk.DoubleVar create_progress_bar(item_frame)
        +void log_debug(message)
        +void _log_debug(message)
        +void write(message)
        +void flush()
    }

    class UI_Back {
        +FIL_interface app
        +CasquesManager casques
        +void installer_apks_et_solutions()
        +void _installer_apks_et_solutions()
        +bool install_apk_with_progress(casque)
        +void add_solution_with_progress(casque)
        +void open_solution_manager(casque)
        +void track_devices(stop_event)
        +void download_banque_solutions()
        +void install_apk(casque)
        +void uninstall_apk(casque)
        +void push_solutions(casque)
    }

    

    Casque --> Config
    Casque --> BiblioManager
    Casque --> Marque
    Casque --> SolutionCasque
    Casque --> adbtools
    CasquesManager --> Config
    CasquesManager --> Casque
    BiblioManager --> Config
    BiblioManager --> SolutionBiblio
     CasquesManager --> adbtools
    Config --> platform
    SolutionBiblio --> Solution
    SolutionCasque --> Solution
    Solution --> Config
    FIL_interface --> CasquesManager
    FIL_interface --> BiblioManager
    FIL_interface --> UI_Front
    FIL_interface --> UI_Back
    UI_Front --> FIL_interface
    UI_Back --> FIL_interface
    UI_Back --> CasquesManager





