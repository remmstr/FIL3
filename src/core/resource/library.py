# Internal modules
from core.resource import FontHandler, IconHandler, ImageHandler, ResourceHandler

# Requirements modules
from customtkinter import CTkFont, CTkImage

# Built-in modules
from typing import Tuple
from pathlib import Path

class FontLibrary(ResourceHandler):
    """
    This object is used to find and load font resources that is used for the application.\n
    The class starts looking for font files in the library path and can only handle one level of recursion.

    Class Variables
    ---------------
    Contents : `dict`
        Contain a list of available fonts. The dict is organized as follow:\n
        `{Family name : {Subfamily name : FontHandler object}}`

    Methods
    -------
    retrieve_fonts :
        Add the font into the system file to be used by the application
    get_font_handler : `classmethod`
        Returns the handler object of the font
    get_font_tkinter : `classmethod`
        Returns a CTkFont object with applied parameters

    Examples
    --------
    You can call the FontHandler with the function `get_font_handler()`:
    >>> FontLibrary.get_font_handler('Roboto', 'Regular') -> Return a FontHandler object

    You could also directly call the Tkinter object and set different parameter with the function `get_font_tkinter()`:
    >>> FontLibrary.get_font_tkinter('Roboto', 'Regular', size=16, underline=True, overstrike=True) -> Return a CTkFont object

    But it only works on one level of recursion. So be aware to not nested more than one folder!
    """

    Contents = {}

    def __init__(self, library_path: str | Path) -> None:
        """
        Initialize the library of font with the specified relative path.

        Parameters
        ----------
        library_path: `str | Path`
            The path to search for files (Relative to the program root folder)
        """
        # Initialize the resource handler
        super().__init__(Path(library_path))

        self.log.info('Initializing font library')
        self.retrieve_fonts()

    def retrieve_fonts(self):
        """
        Search into the library path for font files. Can only handle one level of recursive search.
        When a font file is found, it is saved into the class variable `Contents`.
        """
        self.log.info("Searching for font file in {}".format(self.resource_path))
        count = 0

        # List all folders and files that is accessible at the path folder
        folders = [path for path in self.resource_path.glob("*") if path.is_dir()]
        files = [path for path in self.resource_path.glob('*.ttf') if path.is_file()]

        # Register individual font file in library path
        for font_file in files:
            font = FontHandler(font_file)

            # Registering to library of image
            FontLibrary.Contents.update({font.family: {font.subfamily: font}})
            count += 1

            self.log.debug("Single font family named \x1b[1m{}\x1b[m was added to the library.".format(font.family))

        # Search for individual font files into the folders that has been found and register ir
        for folder in folders:
            self.log.debug("Folder named \x1b[1m{}\x1b[m found in library path, searching for individual subfamily font file inside...".format(folder.name))

            for font_file in folder.glob("*.ttf"):
                font = FontHandler(font_file)

                # Add the folder name to library if at least one image has been found
                if font.family not in FontLibrary.Contents.keys():
                    FontLibrary.Contents.update({font.family : {}})

                # Registering to library of font
                FontLibrary.Contents[font.family].update({font.subfamily : font})
                count += 1

                self.log.debug("Subfamily named \x1b[1m{}\x1b[m from the family {} was added to the library.".format(font.subfamily, font.family))

        self.log.info("Found {} font files in total".format(count))

    @classmethod
    def get_font_handler(cls, font_family: str, font_subfamily: str = 'Regular') -> FontHandler:
        """
        Returns the handler object of the font.

        Parameters
        ----------
        font_family: `str`
            The family correspond to the font name. Be aware, the name doesn't directly correspond to the filename. The FontHandler use the metadata that can be found on the file.
        font_subfamily: `str`, optional
            The subfamily is corresponding to the weight of the font. It could be multiple name but there is some commons name across font like `Regular` or `Bold`. By default 'Regular'

        Returns
        -------
        FontHandler
            Returns a `FontHandler` object that can be used to retrieve information on the font (file path, family name, etc...)
        """
        return cls.Contents[font_family][font_subfamily]

    @classmethod
    def get_font_tkinter(cls, font_family: str, font_subfamily: str, size : int | None = None, underline: bool = False, overstrike: bool = False) -> CTkFont:
        """
        Returns a CTkFont object with applied parameters.
        Only works if the mainloop of CTk is launched!

        Parameters
        ----------
        font_family: `str`
            The family correspond to the font of the name. Be aware that the name doesn't correspond to the filename. The FontHandler use the metadata that can be found on the file.
        font_subfamily: `str`, optional
            The subfamily is corresponding to the weight of the font. It could be multiple name but there is some commons name across font like `Regular` or `Bold`, by default is `Regular`
        size: `int | None`, optional
            Set the default size, by default None
        underline: `bool`, optional
            Set the option for underline, by default False
        overstrike: `bool`, optional
            Set the option for overstrike, by default False

        Returns
        -------
        `CTkFont`
            Return an object usable with Tkinter widgets
        """
        return cls.Contents[font_family][font_subfamily].get_ctk_font(size, underline, overstrike)


class ImageLibrary(ResourceHandler):
    """
    This object is used to find and load image resources that is used for the application.\n
    The class starts looking for image files in the library path and can only handle one level of recursion.

    Class Variables
    ---------------
    Contents : `dict`
        Contain a list of available images. The dict is organized as follow:\n
        `{Group : {Image name w/o extension : ImageHandler object}}`

    Methods
    -------
    retrieve_images :
        Search into the library path for image files. Can only handle one level of recursive search.
    get_image_handler : `classmethod`
        Returns the handler object of the image
    get_image_tkinter : `classmethod`
        Returns a CTkImage object with applied parameters

    Examples
    --------
    You can retrieve any ImageHandler with the function `get_image_handler()`:
    >>> ImageLibrary.get_image_handler('name_of_the_image') -> Return an ImageHandler object

    You could also directly call the Tkinter object and set different parameter with the function `get_image_tkinter()`:
    >>> ImageLibrary.get_image_tkinter('name_of_the_image', size=(256, 256)) -> Return a CTkImage object

    The Library will first search into the root of the given path.
    If you placed the image into a subfolder of the library path, you can use the parameter `group` to point inside of it:
    >>> ImageLibrary.get_image_tkinter('name_of_the_image', 'folder_name', size=(64, 64))

    But it only works on one level of recursion. So be aware to not nested more than one folder!
    """

    Contents = {'root' : {}}

    def __init__(self, library_path: str | Path) -> None:
        """
        Initialize the library of image with the specified path.

        Parameters
        ----------
        library_path : `str | Path`
            The path to search for files (Relative to the program root folder)
        """
        # Initialize inherited class
        super().__init__(library_path)

        self.log.info('Initializing image library')
        self.retrieve_images()

    def retrieve_images(self):
        """
        Search into the library path for image files. Can only handle one level of recursive search.
        When an image file is found, it is registered inside the class variable `Contents`.
        """

        self.log.info("Searching for image file in {}".format(self.resource_path))
        count = 0

        # List all folders and files that is accessible at the path folder
        folders = [path for path in self.resource_path.glob('*') if path.is_dir()]
        files = [path for path in self.resource_path.glob('*.ttf') if path.is_file()]

        # List all available image file in library_path
        for image_file in files:
            image = ImageHandler(image_file)

            # Registering to library of image
            ImageLibrary.Contents['root'].update({image.stem: image})
            count += 1

            self.log.debug("Image named \x1b[1m{}\x1b[m was added to the library.".format(image.stem))

        # Search one level deeper into the folders that has been found
        for folder in folders:
            self.log.info("Found folder named \x1b[1m{}\x1b[m, searching for image files inside...".format(folder.name))

            for image_file in folder.glob('*.png'):
                image_file = ImageHandler(image)

                # Add the folder name to library if at least one image has been found
                if folder.name not in FontLibrary.Contents.keys():
                    FontLibrary.Contents.update({folder.name : {}})

                # Registering to library of image
                FontLibrary.Contents[folder.name].update({image.stem: image})
                count += 1

                self.log.debug("Image named \x1b[1m{}\x1b[m was added to library".format(image.stem))

        self.log.info('Found {} images in total'.format(count))

    @classmethod
    def get_image_handler(cls, image_name: str, group: str = 'root') -> ImageHandler:
        """
        Returns the handler object of the image.

        Parameters
        ----------
        image_name : `str`
            Set the name of the image that you want to use
        group : `str`, optional
            Set the name of the group where the resource is located, by default is `root`

        Returns
        -------
        `ImageHandler`
            Returns an `ImageHandler` object that can be used to retrieve information on the font (file path, family name, etc...)
        """
        return cls.Contents[group][image_name]

    @classmethod
    def get_image_tkinter(cls, image_name: str, group: str = 'root', size: Tuple[int, int] | None = None) -> CTkImage:
        """
        Returns a CTkImage object with applied parameters.
        Only works if the mainloop of CTk is launched!

        Parameters
        ----------
        image_name : `str`
            Set the name of the image that you want to use
        group : `str`, optional
            Set the name of the group where the resource is located, by default is `root`
        size : `int | None`, optional
            Set the size of the image, by default it is using the size of the image when set to None

        Returns
        -------
        `CTkFont`
            Returns an object usable with Tkinter widgets
        """
        return cls.Contents[group][image_name].get_ctk_image(size)


class IconLibrary(ResourceHandler):
    """
    This object is used to find and load icon resources that is used for the application.\n
    The class starts looking for icon files in the library path and can only handle one level of recursion.

    The difference with the Image Library is for handling different color of icon, if the luminosity of the UI is changed.

    Class Variables
    ---------------
    Contents : `dict`
        Contain a list of available images. The dict is organized as follow:\n
        ` {Group : {Icon name w/o extension : IconHandler object}}`

    Methods
    -------
    retrieve_icons :
        Search into the library path for icon files. Can only handle one level of recursive search.
    get_icon_handler : `classmethod`
        Returns the handler object of the icon
    get_icon_tkinter : `classmethod`
        Returns a CTkImage object with applied parameters

    Examples
    --------
    You can retrieve any IconHandler with the function `get_icon_handler()`:
    >>> IconLibrary.get_icon_handler('name_of_the_icon') -> Return an ImageHandler object

    You could also directly call the Tkinter object and set different parameter with the function `get_icon_tkinter()`:
    >>> IconLibrary.get_icon_tkinter('name_of_the_icon', size=(64, 64)) -> Return a CTkImage object

    If you placed the icon into a subfolder of the library path, you can set the parameter `group` to point inside of it:
    >>> IconLibrary.get_icon_tkinter('name_of_the_icon', 'name_of_group', size=(64, 64))

    But it only works on one level of recursion. So be aware to not nested more than one folder!
    """

    Contents = {'root' : {}}

    def __init__(self, library_path: str | Path) -> None:
        """
        Initialize the library of icon with the specified path.

        Parameters
        ----------
        library_path : `str | Path`
            The path to search for files  (Relative to the program root folder)
        """
        # Initialize inherited class
        super().__init__(library_path)
        self.resource_path.glob("*")

        self.log.info('Initializing icon library')
        self.retrieve_icons()

    def retrieve_icons(self):
        """
        Search into the library path for icon files. Can only handle one level of recursive search.
        When an icon file is found, it is registered inside the class variable `Contents`.
        """

        self.log.info("Searching for icon file in {}".format(self.resource_path))
        count = 0

        # List all folders and files that is accessible at the path folder
        folders = [path for path in self.resource_path.glob('*') if path.is_dir()]
        files = [path for path in self.resource_path.glob("*.png") if path.is_file()]

        # List all available icon file in library_path
        for icon_file in files:
            icon = IconHandler(icon_file)

            # Registering to library of image
            IconLibrary.Contents['root'].update({icon_file.stem: icon})
            count += 1

            self.log.debug("Icon named \x1b[1m{}\x1b[m was added to library".format(icon_file.stem))

        # Search one level deeper into the folders that has been found
        for folder in folders:
            self.log.info("Found folder named \x1b[1m{}\x1b[m, searching for image files inside...".format(folder.name))

            for icon_file in folder.glob('*.png'):
                icon = IconHandler(icon_file)

                # Add the folder name to library if at least one image has been found
                if folder.name not in FontLibrary.Contents.keys():
                    IconLibrary.Contents.update({folder.name : {}})

                # Registering to library of image
                IconLibrary.Contents[folder.name].update({icon_file.stem: icon})
                count += 1

                self.log.debug("Image named \x1b[1m{}\x1b[m was added to library".format(icon_file.stem))

        self.log.info('Found {} icons'.format(count))

    @classmethod
    def get_icon_handler(cls, icon_name: str, group: str = 'root') -> IconHandler:
        """
        Returns the handler object of the icon

        Parameters
        ----------
        icon_name : `str`
            Set the name of the icon that you want to use
        group : `str`, optional
            Set the name of the group where the resource is located, by default is `'root'`

        Returns
        -------
        `IconHandler`
            An `IconHandler` object can be used to retrieve information on the font (file path, family name, etc...)
        """
        return cls.Contents[group][icon_name]

    @classmethod
    def get_icon_tkinter(cls, icon_name: str, group: str = 'root', size: Tuple[int, int] | None = None) -> CTkImage:
        """
        Returns a CTkImage object with applied parameters.
        Only works if the mainloop of CTk is launched!

        Parameters
        ----------
        icon_name : `str`
            Set the name of the icon that you want to use
        group : `str`, optional
            Set the name of the group where the resource is located, by default is `'root'`
        size : `int | None`, optional
            Set the size of the icon, by default it is using the size of the icon when set to None

        Returns
        -------
        `CTkImage`
            Returns an object usable with Tkinter widgets
        """
        return cls.Contents[group][icon_name].get_ctk_icon(size)