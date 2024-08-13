
import traceback
from config import Config
from singletonMeta import SingletonMeta
from solutionBiblio import SolutionBiblio
import os

class BiblioManager(metaclass=SingletonMeta):

    def __init__(self):
        self.config = Config()
        self.liste_solutions = []
        self.get_sols_bibli()

    def print(self):
        for i, sol in enumerate(self.liste_solutions, 1):
            print(f"\nSOlutions #{i}:")
            sol.print()
            print("-" * 20)

    def get_sols_bibli(self):
        """
        Récupère toutes les solutions disponibles dans la bibliothèque des solutions et remplit les objets solutions avec les noms des fichiers de médias.
        """
        self.liste_solutions.clear()  # Clear the list before refreshing
        solution_base_dir = self.config.Banque_de_solution_path

        # Parcours de chaque dossier de solution dans la bibliothèque
        for solution_name in os.listdir(solution_base_dir):
            solution_dir = os.path.join(solution_base_dir, solution_name)

            # Vérifie si c'est un dossier
            if os.path.isdir(solution_dir):
                nouvelle_solution = self.get_sol_bibli(solution_name, solution_dir)
                if nouvelle_solution is not None:
                    self.liste_solutions.append(nouvelle_solution)
        
        return self.liste_solutions  # Retourner la liste des solutions

    def get_sol_bibli(self, solution_name, solution_dir):
        """
        Récupère une solution unique depuis la bibliothèque des solutions, remplit l'objet solution avec les noms des fichiers de médias, et calcule sa taille totale.

        Args:
            solution_name (str): Le nom de la solution.
            solution_dir (str): Le chemin vers le dossier de la solution.

        Returns:
            SolutionBiblio: L'objet SolutionBiblio initialisé ou None en cas d'erreur.
        """
        subdirs = ["image", "image360", "sound", "srt", "video"]
        try:
            nouvelle_solution = SolutionBiblio()
            nouvelle_solution.nom = solution_name
            totale_size = 0  # Initialisation de la taille totale

            # Parcours des sous-dossiers et ajout des fichiers de médias à la solution
            for subdir in subdirs:
                target_dir = os.path.join(solution_dir, subdir)

                if os.path.exists(target_dir):
                    media_files = os.listdir(target_dir)
                    totale_size += sum(os.path.getsize(os.path.join(target_dir, f)) for f in media_files)
                    if subdir == "image":
                        nouvelle_solution.image.extend(media_files)
                    elif subdir == "image360":
                        nouvelle_solution.image360.extend(media_files)
                    elif subdir == "sound":
                        nouvelle_solution.sound.extend(media_files)
                    elif subdir == "srt":
                        nouvelle_solution.srt.extend(media_files)
                    elif subdir == "video":
                        nouvelle_solution.video.extend(media_files)

            nouvelle_solution.size = totale_size  # Attribuer la taille totale à l'objet SolutionBiblio
            return nouvelle_solution
        except Exception as e:
            print(f"Erreur lors de l'ajout de la solution {solution_name} : {e}")
            traceback.print_exc()
            return None

    def refresh_biblio(self):
        """
        Rafraîchit la liste des solutions dans la bibliothèque si un ajout ou une suppression est détecté.
        """
        # Lire tous les éléments dans le dossier bibliothèque
        solution_base_path = self.config.Banque_de_solution_path
        name_sols_in_folder = set(os.listdir(solution_base_path))

        # Mettre à jour les solutions existantes et ajouter de nouvelles solutions
        updated_solutions = []

        for solution_name in name_sols_in_folder:
            solution_path_folder = os.path.join(solution_base_path, solution_name)

            if os.path.isdir(solution_path_folder):
                existing_solution = next((sol for sol in self.liste_solutions if sol.nom == solution_name), None)
                if existing_solution:
                    # Vérifier si la taille a changé
                    current_size = existing_solution.get_sol_size()
                    print(f"current_size {current_size} != existing_solution.size {existing_solution.size} ")
                    if existing_solution.size != existing_solution.get_sol_size():
                        existing_solution.size = existing_solution.get_sol_size()
                    updated_solutions.append(existing_solution)
                else:
                    # Solution nonexistante, la crée
                    print(f"Ajout d'une nouvelle solution : {solution_name}")
                    nouvelle_solution = self.get_sol_bibli(solution_name, solution_path_folder)
                    if nouvelle_solution is not None:
                        updated_solutions.append(nouvelle_solution)

        # Mettre à jour la liste des solutions avec les nouvelles et mises à jour solutions
        self.liste_solutions = updated_solutions

        # Supprimer les solutions qui n'existent plus
        self.liste_solutions = [sol for sol in self.liste_solutions if sol.nom in name_sols_in_folder]


    def is_sol_in_library(self, solution):
        for sol_in_biblio in self.liste_solutions:
            print(f"sol_in_biblio.nom : {sol_in_biblio.nom} == solution.nom : {self.config.safe_string(solution.nom)}" )
            if sol_in_biblio.nom == self.config.safe_string(solution.nom):
                # Pour plus tard, il faudra vérifier davantage de choses que le nom, comme la version et le poids
                return sol_in_biblio
        return False
