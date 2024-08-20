import subprocess
import re
import time
import shutil
from threading import Thread
from tkinter import filedialog
import tkinter as tk
import os
from config import Config
import adbtools
from biblioManager import BiblioManager
from casquesManager import CasquesManager


class UI_Back:
    def __init__(self, app):
        self.app = app
        self.casques = CasquesManager()
        self.biblio = BiblioManager()
        self.config = Config()

    def installer_apks_et_solutions(self):
        try:
            for casque in self.casques.liste_casques:
                Thread(target=self.installer_apks_et_solution, args=(casque,)).start()
        except Exception as e:
            self.app.handle_exception("Erreur lors de l'installation des APKs et des solutions", e)




    from threading import Thread

    def installer_apks_et_solution(self, casque):
        try:
            # 1. Obtenir la version actuelle de l'APK installée
            current_version = casque.version_apk
            selected_version = self.app.ui_front.selected_folder.get()  # Récupérer la version sélectionnée via le menu déroulant

            # 2. Comparer la version actuelle avec la version sélectionnée
            if current_version != selected_version:
                print(f"{casque.name} {casque.numero}: Installation nécessaire {current_version} -> {selected_version}")
                self.install_apk(casque)
            else:
                print(f"{casque.name} {casque.numero}: Aucune installation nécessaire. Version actuelle {current_version}")

            # 3. Lancer la vérification du fichier JSON dans un thread séparé
            thread = Thread(target=self.wait_for_json_and_push_solutions, args=(casque,))
            thread.start()

        except Exception as e:
            self.app.handle_exception("Erreur lors de l'installation des APKs et des solutions", e)

    def wait_for_json_and_push_solutions(self, casque):
        try:
            # 3.1 Attendre que le fichier JSON soit disponible, avec un maximum de 3 essais
            #print(f"Attente du fichier JSON pour le casque {casque.numero}...")
            max_attempts = 3
            attempt = 0
            time.sleep(10)
            while attempt < max_attempts:
                time.sleep(15)  # Attendre 10 secondes avant de vérifier à nouveau
                self.refresh_json(casque)  # Rafraîchir le JSON
                if casque.JSON_path != 'Fichier JSON inexistant':
                    #print(f"Fichier JSON trouvé : {casque.JSON_path}")
                    break
                attempt += 1
                #print(f"Tentative {attempt}/{max_attempts} pour trouver le fichier JSON.")

            # Si après 3 tentatives le fichier JSON est toujours inexistant
            if casque.JSON_path == 'Fichier JSON inexistant':
                raise FileNotFoundError(f"{casque.name} {casque.numero}: Fichier JSON introuvable pour le casque {casque.numero} après {max_attempts} tentatives.")

            # 4. Téléverser les solutions
            self.push_solutions(casque)
            print(f"Solutions téléversées sur le casque {casque.numero}.")

        except Exception as e:
            self.app.handle_exception("Erreur lors de l'attente du fichier JSON ou du téléversement des solutions", e)



    def open_solution_manager(self, casque):
        # Renommer la fenêtre
        solution_window = tk.Toplevel(self.app.ui_front.root)
        solution_window.title(f"Licence associée au casque {casque.numero}")

        # Zone de texte pour afficher les solutions
        solution_list = tk.Text(solution_window, wrap="word", width=100, height=20)
        solution_list.pack(padx=10, pady=10, fill="both", expand=True)

        for solution in casque.solutions_casque:
            in_library = casque.is_solution_in_library(solution)  # Stocker le résultat
            #print(f"Résultat de is_solution_in_library: {in_library}")

            if solution.sol_install_on_casque:
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n", "install_on_casque")
            elif in_library:
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n", "in_library")
                #print(f"in library")
            else:
                #print(f"casque.is_solution_in_library(solution): {in_library}")
                solution_list.insert(tk.END, f"{solution.nom} ({solution.version})\n")
                #print(f"not in library")
                
        # Configurer la couleur du texte pour les solutions installées sur le casque
        solution_list.tag_config("install_on_casque", foreground="green")
        # Configurer la couleur du texte pour les solutions dans la bibliothèque
        solution_list.tag_config("in_library", foreground="blue")
        
        solution_list.config(state=tk.DISABLED)

        # Ajouter la légende en bas de la fenêtre
        legend_frame = tk.Frame(solution_window, bg="white")
        legend_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(legend_frame, text="Légende : ", bg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        tk.Label(legend_frame, text="Solution téléchargée dans le casque", fg="green", bg="white", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=10)
        tk.Label(legend_frame, text="Pas téléchargée, disponible dans la bibliothèque", fg="blue", bg="white", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=20)
        tk.Label(legend_frame, text="Pas téléchargée", bg="white", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=10)

        # Bouton Fermer
        close_button = tk.Button(solution_window, text="Fermer", command=solution_window.destroy)
        close_button.pack(pady=10)


    def track_devices(self, stop_event):
        while not stop_event.is_set():
            try:
                self.casques.refresh_casques()
                self.biblio.refresh_biblio()
                if self.app.running:  # Vérifiez si l'application est toujours en cours d'exécution
                    self.app.ui_front.afficher_casques()
                time.sleep(2.5)
            except Exception as e:
                if self.app.running:
                    self.app.handle_exception("Erreur lors de l'actualisation des casques", e)
                else:
                    break


    def download_banque_solutions(self):
        try:
            destination = filedialog.askdirectory()
            if destination:
                shutil.copytree(self.app.config.Banque_de_solution_path, os.path.join(destination, "Banque_de_solutions"))
                self.app.log_debug("Téléchargement du dossier Banque de solutions terminé.")
        except Exception as e:
            self.app.handle_exception("Erreur lors du téléchargement de la banque de solutions", e)

    def install_apk(self, casque):
        Thread(target=casque.install_APK).start()

    def uninstall_apk(self, casque):
        Thread(target=casque.uninstall_APK).start()

    def start_apk(self, casque):
        Thread(target=casque.open_apk()).start()
        
    def close_apk(self, casque):
        Thread(target=casque.close_apk()).start()
        
    def push_solutions(self, casque):
        Thread(target=casque.push_solutions).start()

    def pull_solutions(self, casque):
        Thread(target=casque.pull_solutions).start()

    def refresh_json(self,casque):
        Thread(target=casque.refresh_JSON).start()

        
