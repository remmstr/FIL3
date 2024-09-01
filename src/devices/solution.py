# Built-in modules
import logging

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

        self.log = logging.getLogger('.'.join([__name__, type(self).__name__]))

    def size(self):
        pass


    def print_light(self):
        """
        Affiche les détails principaux de la solution.
        """
        self.log.info(f"Solution: {self.nom}")
        self.log.info(f"  Version: {self.version}")
        self.log.info(f"  Size: {self.size}")
        
    def print(self):
        """
        Affiche les détails complet de la solution .
        """
        self.log.info(f"Solution: {self.nom}")
        self.log.info(f"  Version: {self.version}")
        self.log.info(f"  Size: {self.size}")

        
        self.log.info("  Images:")
        for img in self.image:
            self.log.info(f"    - {img}")
        self.log.info()
        
        self.log.info("  Images360:")
        for img360 in self.image360:
            self.log.info(f"    - {img360}")
        self.log.info()
        
        self.log.info("  Sounds:")
        for snd in self.sound:
            self.log.info(f"    - {snd}")
        self.log.info()
        
        self.log.info("  Subtitles:")
        for subtitle in self.srt:
            self.log.info(f"    - {subtitle}")
        self.log.info()
        
        self.log.info("  Videos:")
        for vid in self.video:
            self.log.info(f"    - {vid}")
        self.log.info()
