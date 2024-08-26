# Built-in modules
import sys
import logging
from typing         import Literal, Tuple
from pathlib        import Path

# Requirements modules
from customtkinter  import CTkImage, CTkFont
from PIL            import Image, ImageColor
from fontTools      import ttLib

###################################################################

class ResourceHandler():
    """
    Base class to manage a file.\n
    Handles the path conversion if the application is bundled or in development environment.
    """
    def __init__(self, resource_path: str | Path):
        # Set the correct adress of the resource
        self.filepath = self.get_resource_dir(resource_path).resolve()
        self.log = logging.getLogger(self.__class__.__name__)

    @classmethod
    def get_resource_dir(cls, filepath: str | Path) -> Path:
        if cls.is_bundled():
            resource_dir = Path(sys._MEIPASS)
        else:
            resource_dir = Path(__file__).parent.parent.parent
        
        return resource_dir.joinpath(filepath)

    @staticmethod
    def is_bundled() -> bool:
        """Return `True` if the program is bundled into an executable."""
        try:
            sys._MEIPASS
        except AttributeError:
            return False
        return True

###################################################################

class FontHandler(ResourceHandler):
    def __init__(self, font_path: Path) -> None:
        super().__init__(font_path)
        self.register_font()
        self.font = ttLib.TTFont(self.filepath)

    @property
    def family(self) -> str:
        """Return the family name of the font."""
        return self.font["name"].getBestFamilyName()

    @property
    def fullname(self) -> str:
        """Return the full name of the font. (family name + subfamily name)"""
        return self.font["name"].getBestFullName()

    @property
    def subfamily(self) -> str:
        """Return the subfamily name of the font."""
        return self.font["name"].getBestSubFamilyName()

    def register_font(self, private: bool = True, enumerable: bool = False) -> bool:
        """
        Add the font into the system file.\n
        The font is available to the current process for the duration of the process and is automatically unregistered when the app is closed.
        """

        self.log.debug("Registration of the font file {} in the operating system".format(self.filepath.name))

        if not self.filepath.exists():
            raise FileNotFoundError("The specified font file {} does not exist.".format(self.filepath.name))
        
        match sys.platform:
            case 'win32':
                from ctypes import windll, byref, create_unicode_buffer, create_string_buffer

                flags = (0x10 if private else 0) | (0x20 if not enumerable else 0)

                match self.filepath.suffix.lower():
                    case ".ttf":
                        add_font_resource_ex = windll.gdi32.AddFontResourceExW
                        path_buffer = create_unicode_buffer(str(self.filepath))
                    case ".fon":
                        add_font_resource_ex = windll.gdi32.AddFontResourceExA
                        path_buffer = create_string_buffer(str(self.filepath))
                    case _:
                        raise ValueError(f"Unsupported font file format: {self.filepath.suffix}")

                return bool(min(add_font_resource_ex(byref(path_buffer), flags, 0), 1))
            case 'darwin':
                from ctypes import cdll, byref, c_void_p, c_bool, c_uint32, c_int
                from ctypes.util import find_library

                try:
                    CoreText = cdll.LoadLibrary(find_library("CoreText"))

                    # Define the correct pointer type for CFURLCreateFromFileSystemRepresentation
                    CFURLCreateFromFileSystemRepresentation = CoreText.CFURLCreateFromFileSystemRepresentation
                    CFURLCreateFromFileSystemRepresentation.restype = c_void_p
                    CFURLCreateFromFileSystemRepresentation.argtypes = [c_void_p, c_void_p, c_int, c_bool]

                    # Define the correct pointer type for CTFontManagerRegisterFontsForURL
                    CTFontManagerRegisterFontsForURL = CoreText.CTFontManagerRegisterFontsForURL
                    CTFontManagerRegisterFontsForURL.restype = c_bool
                    CTFontManagerRegisterFontsForURL.argtypes = [c_void_p, c_uint32, c_void_p]

                    # Convert the filepath to a CFURL
                    font_url = CFURLCreateFromFileSystemRepresentation(None, self.filepath.as_posix().encode(), len(self.filepath.as_posix()), False)

                    # Register the font
                    result = CTFontManagerRegisterFontsForURL(font_url, 1, byref(c_bool()))

                    return result
                except Exception:
                    self.log.error("Exception when loading font for MacOS: ", exc_info=True)
                    return False
            case 'linux':
                import shutil
                linux_fonts_dir = Path("~/.fonts/").expanduser()

                try:
                    if not linux_fonts_dir.is_dir():
                        linux_fonts_dir.mkdir()
                    shutil.copy(self.filepath, linux_fonts_dir)
                    return True
                except Exception as err:
                    sys.stderr.write("FontManager error: " + str(err) + "\n")
                    return False

    def tkObject(self, size : int | None = None,
                      weight: Literal['normal', 'bold'] = None,
                      slant: Literal['italic', 'roman'] = 'roman',
                      underline: bool = False,
                      overstrike: bool = False) -> CTkFont:
        """
        Return a Custom TKinter font object.
        Only works if the mainloop of CTk is launched!
        """
        return CTkFont(self.fullname, size, weight, slant, underline, overstrike)

class FontLibrary(ResourceHandler):
    Contents = {}

    def __init__(self, library_path: str) -> None:
        
        # Initialize the resource handler
        super().__init__(Path(library_path))
        self.log.info('Initializing font library')

        self.retrieve_resources(self.filepath)

    def retrieve_resources(self, library_path: Path):
        self.log.info("Searching for font resource in {}".format(library_path))

        count = 0
        # List all folders inside the library path
        families = [path for path in library_path.glob("*") if path.is_dir()]

        for family in families:
            self.log.debug("Font family named \x1b[1m{}\x1b[m added to library, searching subfamilies...".format(family.name))
            subgroups = {}
            for subfamily in family.glob("*.ttf"):
                font = FontHandler(subfamily)

                self.log.debug("Subfamily named \x1b[1m{}\x1b[m wad added.".format(font.subfamily))
                subgroups.update({font.subfamily: font})
                
            count += len(subgroups)
            FontLibrary.Contents.update({font.family: subgroups})

        self.log.info("Found {} font files".format(count))

###################################################################

class ImageHandler(ResourceHandler):
    def __init__(self, image_path: Path):
        super().__init__(image_path)

    @property
    def image_data(self):
        return Image.open(self.filepath)

    def tkObject(self, size: Tuple[int, int] | None = None) -> CTkImage:
        """
        Return a Custom TKinter image object.
        Only works if the mainloop of CTk is launched!
        """
        if size is None:
            return CTkImage(light_image=self.image_data, size=self.image_data.size)
        else:
            return CTkImage(light_image=self.image_data, size=size)

class ImageLibrary(ResourceHandler):
    Contents = {}

    def __init__(self, library_path: str) -> None:
        super().__init__(library_path)
        self.log.info('Initializing image library')
        self.retrieve_resources(self.filepath)

    def retrieve_resources(self, library_path: Path):
        self.log.info("Searching for image resource in {}".format(library_path))
        count = 0

        # List all folders inside the library path
        folders = [path for path in self.filepath.glob('*') if path.is_dir()]

        files_in_root = {}
        for image in [path for path in self.filepath.glob('*.png') if path.is_file()]:
            files_in_root.update({image.stem: ImageHandler(image)})
        ImageLibrary.Contents.update({'root': files_in_root})

        # List all inside inside each folders
        for folder in folders:
            self.log.debug("Found folder named \x1b[1m{}\x1b[m, going deeper...".format(folder.name))
            subgroups = {}
            for image in folder.glob('*.png'):
                self.log.debug("Resource named \x1b[1m{}\x1b[m added to library".format(image.stem))
                subgroups.update({image.stem: ImageHandler(image)})
            
            count += len(subgroups)

            self.log.info('Found {} images in folder {}'.format(len(subgroups), folder.name))
            ImageLibrary.Contents.update({folder.name: subgroups})

###################################################################

class IconHandler(ImageHandler):
    def __init__(self, icon_path: Path):
        super().__init__(icon_path)

    def tkObject(self, size: Tuple[int, int] | None = None) -> CTkImage:
        """
        Return a Custom TKinter image object.
        Only works if the mainloop of CTk is launched!
        """
        if size is None:
            return CTkImage(light_image=self.replace_color('#16191C'), dark_image=self.replace_color('#F3F3F1'), size=self.image_data.size)
        else:
            return CTkImage(light_image=self.replace_color('#16191C'), dark_image=self.replace_color('#F3F3F1'), size=size)

    def replace_color(self, color_hex: str = '#FFFFFF') -> Image:
        """
        How this works ?
        ----------------
        This function uses Pillow.Image tools to replace the color of an image.\n
        It uses the transparancy data of the source image to create a new image.\n
        The function assign the alpha channel of the source image to the new one, to recreate the image with the new color.
        """

        if self.image_data.has_transparency_data:
            # Create a new image filled with color, need to have alpha channel even if not use.
            result = Image.new("RGB", self.image_data.size, ImageColor.getrgb(color_hex))
            
            # Composite the alpha channel of the image source to the new color filled image to recreate the icon with the new color
            result.putalpha(self.image_data.getchannel('A'))

            return result
        else:
            return ImportError(name='Transparency data not found. This function can only work on image with a transparency channel.')

class IconLibrary(ResourceHandler):
    Contents = {}

    def __init__(self, library_path: str) -> None:
        super().__init__(library_path)
        self.log.info('Initializing icon library')
        self.retrieve_resources(self.filepath)

    def retrieve_resources(self, library_path: Path):
        self.log.info("Searching for icon resource in {}".format(self.filepath))

        # List all files inside the library path
        icons = [path for path in self.filepath.glob("*") if path.is_file() and path.suffix == '.png']

        for icon in icons:
            self.log.debug("Resource named \x1b[1m{}\x1b[m added to library".format(icon.stem))
            IconLibrary.Contents.update({icon.stem: IconHandler(icon)})

        self.log.info('Found {} icons'.format(len(IconLibrary.Contents)))

###################################################################

if __name__ == '__main__':
    FontsLib =  FontLibrary("assets/fonts")
    ImagesLib = ImageLibrary("assets/images")
    IconsLib =  IconLibrary("assets/icons")

    print(FontLibrary.Contents.keys())
    print(ImageLibrary.Contents.keys())
    print(IconLibrary.Contents.keys())