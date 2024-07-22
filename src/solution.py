class Solution:
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
        print(f"  Installed on casque: {self.sol_install_on_casque}")
        print(f"  Version: {self.version}")
        
    def print(self):
        """
        Affiche les détails de la solution de manière formatée.
        """
        print(f"Solution: {self.nom}")
        print(f"  Installed on casque: {self.sol_install_on_casque}")
        print(f"  Version: {self.version}")

        
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
