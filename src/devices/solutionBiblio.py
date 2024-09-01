import os
from .solution import Solution
from .config import Config

# Built-in modules
import logging

class SolutionBiblio(Solution):

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.size = self.get_sol_size()

        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))
        

    def get_sol_size(self):
        """
        Calcule la taille totale de la solution en additionnant les tailles de tous les fichiers.
        """
        total_size = 0
        subdirs = ["image", "image360", "sound", "srt", "video"]
        media_directories = [self.image, self.image360, self.sound, self.srt, self.video]

        # Itérer sur chaque type de média et son sous-dossier correspondant
        for subdir, media_files in zip(subdirs, media_directories):
            for file in media_files:
                # Construire le chemin complet du fichier en incluant le sous-dossier
                file_path = os.path.join(self.config.Bibliothèque_de_solution_path, self.config.safe_string(self.nom), subdir, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                else:
                    self.log.info(f"Fichier manquant: {file_path}")

        return total_size
    