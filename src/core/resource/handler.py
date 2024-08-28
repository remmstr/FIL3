# Built-in modules
import sys
import logging
from pathlib import Path
from typing import Tuple

# Requirements modules
from PIL import Image, ImageColor
from customtkinter import CTkFont, CTkImage
from fontTools import ttLib

class ResourceHandler():
    """
    Base class to manage a file resource for internal use.\n
    Handles the path conversion if the application is bundled or in development environment.
    The handler check if the resource for the path is available.

    Methods
    -------
    get_bundle_dir : `class`
        Returns the path of the bundle directory

    Instance Variables
    ------------------
    log : `Logger`
        The logger of the instanciated class
    resource_path  : `Path`
        The file path of the resource

    Examples
    --------
    To get the correct path of the resource, you can use the `resource_path` variable:
    >>> ResourceHandler("relative_path/to/file").resource_path

    As the resource_path returns a Path object, you have access to the same functions:
    >>> dummy = ResourceHandler("relative_path/to/file")
    >>> dummy_path = dummy.resource_path
    >>> array = [dummy_path.name, dummy_path.stem]

    Or we can open the file to do some operation with it:
    >>> with dummy_path.open() as f:
            f.seek(0)
            f.readline()
    """

    def __init__(self, resource_path: str | Path):
        """
        Initialize an instance of a resource object

        Parameters
        ----------
        resource_path : `str | Path`
            The path of the file to be handled

        Raises
        ------
        FileNotFoundError
            When the path of the resource points to nothing
        """
        # Initilize the logger
        self.log = logging.getLogger(self.__class__.__name__)

        if isinstance(resource_path, str):
            resource_path = Path(resource_path)

        temp_path = self.get_bundle_dir().joinpath(resource_path)

        # Check if the file exist before registering it
        if temp_path.exists():
            self.resource_path = temp_path
        else:
            raise FileNotFoundError("The resource file in {} does not exist.".format(temp_path))

    @classmethod
    def get_bundle_dir(cls) -> Path:
        """
        The bundle in this case correspond to the root folder of the application.\n
        Whether it's in dev environment or bundled into an executable, the function will always return the correct path.

        Returns
        -------
        `Path` :
            Returns the path of the application root folder.
        """
        if cls.is_bundled():
            resource_dir = Path(sys._MEIPASS)
        else:
            resource_dir = Path(__file__).parent.parent.parent.parent # For dev environment give 

        return resource_dir

    @staticmethod
    def is_bundled() -> bool:
        """
        Return `True` if the program is bundled into an executable.
        """
        try:
            sys._MEIPASS
        except AttributeError:
            return False
        return True


class FontHandler(ResourceHandler):
    """
    Class for handling a single font file to be used in the application\n
    Inherit methods and instance variables of `ResourceHandler`

    Methods
    -------
    register_font :
        Add the font into the system file to be used by the application
    get_ctk_font :
        Returns a CTkFont object

    Properties
    ----------
    family : `str`
        Returns the family name of the font
    subfamily : `str`
        Returns the subfamily name of the font
    fullname : `str`
        Returns the full name of the font (family name + subfamily name)
    """

    def __init__(self, font_path: str | Path) -> None:
        """
        Create an instance of a font resource.\n
        When initialized, the class try to temporarily register the font into the system.

        Parameters
        ----------
        font_path : `Path`
            Path of the font file to be handled.
        """
        # Initialize inherited class
        super().__init__(font_path)

        # We need the TTFont module to get the formatted name of the font.
        self.font = ttLib.TTFont(self.resource_path)

        self.register_font()

    @property
    def family(self) -> str:
        """
        Returns the family name of the font
        """
        return self.font["name"].getBestFamilyName()

    @property
    def subfamily(self) -> str:
        """
        Returns the subfamily name of the font
        """
        return self.font["name"].getBestSubFamilyName()

    @property
    def fullname(self) -> str:
        """
        Returns the full name of the font (family name + subfamily name)
        """
        return self.font["name"].getBestFullName()

    def register_font(self) -> bool:
        """
        Add the font into the system file.\n
        The font is available to the current process for the duration of the process and is automatically unregistered when the app is closed.
        """
        self.log.debug("Registration of the font file {} in the operating system".format(self.resource_path.name))

        match sys.platform:
            case 'win32':
                from ctypes import windll, byref, create_unicode_buffer

                flags = 0x10 | 0x20

                match self.resource_path.suffix.lower():
                    case ".ttf":
                        add_font_resource_ex = windll.gdi32.AddFontResourceExW
                        path_buffer = create_unicode_buffer(str(self.resource_path))
                    case _:
                        self.log.error("Unsupported font file format for Win32: {}".format(self.resource_path.suffix))

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
                    font_url = CFURLCreateFromFileSystemRepresentation(None, self.resource_path.as_posix().encode(), len(self.resource_path.as_posix()), False)

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
                    shutil.copy(self.resource_path, linux_fonts_dir)
                    return True
                except Exception as err:
                    sys.stderr.write("FontManager error: " + str(err) + "\n")
                    return False

    def get_ctk_font(self, size : int | None = None, underline: bool = False, overstrike: bool = False) -> CTkFont:
        """
        Returns a CTkFont object.
        Only works if the mainloop of CTk is launched!

        Parameters
        ----------
        size : `int | None`, optional
            Set the default size, by default None
        underline : `bool`, optional
            Set the option of underline, by default False
        overstrike : `bool`, optional
            Set the option of overstrike, by default False

        Returns
        -------
        `CTkFont`
            Return an object usable with Tkinter widgets
        """
        return CTkFont(self.fullname, size, 'normal', 'roman', underline, overstrike)


class ImageHandler(ResourceHandler):
    """
    Class for handling a single image file to be used in the application.
    Inherit methods and instance variables of `ResourceHandler`

    Methods
    -------
    register_font :
        Add the font into the system file to be used by the application
    get_ctk_image :
        Returns a CTkFont object

    Properties
    ----------
    image_data : `PIL.Image`
        Returns the family name of the font
    """

    def __init__(self, image_path: Path):
        """
        Create an instance of an image resource

        Parameters
        ----------
        image_path : `Path`
            Path of the image file to be handled
        """

        # Initialize inherited class
        super().__init__(image_path)

    @property
    def image_data(self) -> Image:
        return Image.open(self.resource_path)

    def get_ctk_image(self, size: Tuple[int, int] | None = None) -> CTkImage:
        """
        Return a CTkImage object.
        Only works if the mainloop of CTk is launched!

        Parameters
        ----------
        size : `Tuple[int, int] | None`, optional
            Set the size of the image, by default it is using the size of the image when set to None

        Returns
        -------
        CTkImage
            Returns an object usable with Tkinter widgets
        """
        if size is None:
            return CTkImage(light_image=self.image_data, size=self.image_data.size)
        else:
            return CTkImage(light_image=self.image_data, size=size)


class IconHandler(ImageHandler):
    """
    Class for handling a single icon file to be used in the application.
    Inherit methods and instance variables of `ImageHandler`

    Methods
    -------
    register_font :
        Add the font into the system file to be used by the application
    get_ctk_image :
        Returns a CTkFont object

    Properties
    ----------
    `image_data` : `PIL.Image`
        Returns the family name of the font
    """

    def __init__(self, icon_path: Path):
        """
        Create an instance of an icon resource

        Parameters
        ----------
        icon_path : `Path`
            Path of the image file to be handled.
        """
        # Initialize inherited class
        super().__init__(icon_path)

    def get_ctk_icon(self, size: Tuple[int, int] | None = None) -> CTkImage:
        """
        Return a CTkImage object.
        Only works if the mainloop of CTk is launched!

        Parameters
        ----------
        size : `Tuple[int, int] | None`, optional
            Set the size of the icon, by default it is using the size of the image when set to None
        """
        if size is None:
            return CTkImage(light_image=self.replace_color_from_alpha('#16191C'), dark_image=self.replace_color_from_alpha('#F3F3F1'), size=self.image_data.size)
        else:
            return CTkImage(light_image=self.replace_color_from_alpha('#16191C'), dark_image=self.replace_color_from_alpha('#F3F3F1'), size=size)

    def replace_color_from_alpha(self, color_hex: str = '#FFFFFF') -> Image:
        """
        Replace the color of an icon.
        Doesn't work on image that has no alpha channel!

        Parameters
        ----------
        color_hex : `str`, optional
            Set the new color of the icon, by default it is set to '#FFFFFF'

        How this works ?
        ----------------
        This function uses Pillow.Image tools to replace the color of an image:
        - We use the transparancy data of the source image to create a new image.\n
        - And then, we assign the alpha channel of the source image to the new one, to recreate the image with the new color.

        Returns
        -------
        `PIL.Image`
            Returns a PIL.Image object that can be used with a CTkImage
        """

        if self.image_data.has_transparency_data:
            # Create a new image filled with color, need to have alpha channel even if not use.
            result = Image.new("RGB", self.image_data.size, ImageColor.getrgb(color_hex))

            # Composite the alpha channel of the image source to the new color filled image to recreate the icon with the new color
            result.putalpha(self.image_data.getchannel('A'))

            return result
        else:
            return ImportError(name='Transparency data not found. This function can only work on image with an alpha channel.')