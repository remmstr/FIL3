class Solution:
    """
    ATTENTION : dans les objets solutionCasque le nom de l'attribut n'est pas passé par la fonction safe, 
    alors que pour la solution Biblio puique l'on tire le nom d'un dossier c'est déja safe

    ATTENTION : dans les attibuts suivants :
        self.image = []
        self.image360 = []
        self.sound = []
        self.srt = []
        self.video = []
    dans l'objet solutionBiblio il y a juste le nom du ficher 
    alors que dans l'objet solutionCasque il y aussi le chemin dans le dossier upload
        
    """


    def __init__(self):

        self.size = 0
        self.nom = ""
        self.version = ""
        self.image = []
        self.image360 = []
        self.sound = []
        self.srt = []
        self.video = []

    def get_sol_size(self):
        pass


    def print_light(self):
        """
        Affiche les détails principaux de la solution.
        """
        print(f"Solution: {self.nom}")
        print(f"  Version: {self.version}")
        print(f"  Size: {self.size}")
        
    def print(self):
        """
        Affiche les détails complet de la solution .
        """
        print(f"Solution: {self.nom}")
        print(f"  Version: {self.version}")
        print(f"  Size: {self.size}")

        
        print("  Images:")
        for img in self.image:
            print(f"    - {img}")
        print()
        
        print("  Images360:")
        for img360 in self.image360:
            print(f"    - {img360}")
        print()
        
        print("  Sounds:")
        for snd in self.sound:
            print(f"    - {snd}")
        print()
        
        print("  Subtitles:")
        for subtitle in self.srt:
            print(f"    - {subtitle}")
        print()
        
        print("  Videos:")
        for vid in self.video:
            print(f"    - {vid}")
        print()
