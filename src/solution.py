import json

class Solution:
    def __init__(self):
        self.sol_install_on_casque = False
        self.nom = ""
        self.version = ""
        self.image = ""
        self.image360 = ""
        self.sound = ""
        self.srt = ""
        self.video = ""
        self.data_path = ""

    @staticmethod
    def from_json(json_data):
        solution = Solution()
        solution.sol_install_on_casque = json_data.get('auto_install', False)
        solution.nom = json_data.get('name_module', {}).get('fr', "")
        solution.version = json_data.get('name_version', {}).get('fr', "")
        solution.data_path = json_data.get('data_path', "")

        medias = json_data.get('medias', [])
        for media in medias:
            if media.endswith('.png') or media.endswith('.jpg'):
                if 'image360' in media:
                    solution.image360 = media
                else:
                    solution.image = media
            elif media.endswith('.mp3'):
                solution.sound = media
            elif media.endswith('.srt'):
                solution.srt = media
            elif media.endswith('.mp4') or media.endswith('.mkv'):
                solution.video = media
        
        return solution
