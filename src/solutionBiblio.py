import os
from solution import Solution

class SolutionBiblio(Solution):

    def __init__(self):
        super().__init__()
    
    #-----------------------------------------------------
    # METHODES SOLUTION IN BIBLIOTHEQUE
    #-----------------------------------------------------

    def get_sol_size(self):
        """
        Calcule la taille totale de la solution en additionnant les tailles de tous les fichiers.
        """
        total_size = 0
        directories = [self.image, self.image360, self.sound, self.srt, self.video]

        for dir in directories:
            for file in dir:
                file_path = os.path.join(self.config.Banque_de_solution_path, self.config.safe_string(self.nom), file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
                else:
                    print(f"Fichier manquant: {file_path}")

        return total_size
    