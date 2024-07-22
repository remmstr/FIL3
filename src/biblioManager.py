
import traceback
from config import Config
from singletonMeta import SingletonMeta
from solutionBiblio import SolutionBiblio
import os

class BiblioManager(metaclass=SingletonMeta):

    def __init__(self):
        print("Bibliothèque Manager created")
        self.config = Config()
        self.liste_solutions = []
        self.liste_solutions = self.get_sols_bibli()

    def get_sols_bibli(self):
        """
        Récupère toutes les solutions disponibles dans la bibliothèque des solutions et remplit les objets solutions avec les noms des fichiers de médias.

        ATTENTION : dans les objets solutionCasque le nom de l'attribut n'est pas passé par la fonction safe,
        alors que pour la solution Biblio puisque l'on tire le nom d'un dossier c'est déjà safe.

        ATTENTION : dans les attributs suivants :
            self.image = []
            self.image360 = []
            self.sound = []
            self.srt = []
            self.video = []
        dans l'objet solutionBiblio il y a juste le nom du fichier
        alors que dans l'objet solutionCasque il y aussi le chemin dans le dossier upload.
        """
        solution_base_dir = self.config.Banque_de_solution_path
        subdirs = ["image", "image360", "sound", "srt", "video"]

        # Parcours de chaque dossier de solution dans la bibliothèque
        for solution_name in os.listdir(solution_base_dir):
            solution_dir = os.path.join(solution_base_dir, solution_name)

            # Vérifie si c'est un dossier
            if os.path.isdir(solution_dir):
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
                    self.liste_solutions.append(nouvelle_solution)
                    nouvelle_solution.print()
                except Exception as e:
                    print(f"Erreur lors de l'ajout de la solution {solution_name} : {e}")
                    traceback.print_exc()

    def is_sol_in_library(self,solution):
        for sol_in_biblio in self.liste_solutions:
            if sol_in_biblio.name == solution.name:
                return True
            else:
                return False