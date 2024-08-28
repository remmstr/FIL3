# Built-in modules
from pathlib import Path
from shutil import copy, copy2

class FileHandler(Path):
    """
    Base class for handling a file
    """

    def __init__(self, str_path: str) -> None:
        """
        Create an instance of FileHandler

        Parameters
        ----------
        str_path : `str`
            Set the path of the file to be handled
        """
        super().__init__(str_path)

    def add_prefix(self, value: str):
        """
        Add a string before the stem

        Parameters
        ----------
        value : `str`
            Set the string to add before the stem
        """
        # Check if the prefix has a underscore character in it, add it if not.
        if value is not None:
            if value.endsswith('_') is True:
                prefix =  value
            else:
                prefix =  value + '_'

        self.rename(self.with_stem(prefix + self.stem).resolve())

    def add_suffix(self, value: str):
        """
        Add a string after the stem

        Parameters
        ----------
        value : `str`
            Set the string to add after the stem
        """
        # Check if the suffix has a underscore character in it, add it if not.
        if value.startswith('_') is True:
            suffix =  value
        else:
            suffix =  '_' + value

        self.rename(self.with_stem(self.stem + suffix))

    def duplicate_file(self, new_name: str | None = None, preserve_metadata: bool = False, zero_fill: int = 4):
        """
        Duplicate the file in place

        Parameters
        ----------
        new_name : `str | None`, optional
            Set a new name for duplicated file. If none, the function will use count number, by default is `None`
        preserve_metadata : `bool`, optional
            Preserve a larger portion of metadata when duplicate, by default is `False`
        zero_fill : `int`, optional
            Set the number of 0 when renaming the file. Only used if `new_name` is None, by default is `4`

        Returns
        -------
        FileHandler
            Returns a new FileHandler object pointing to the duplicated file
        """
        if new_name is None:
            duplicate_count = len(sorted(self.parent.glob(self.stem + "_*" + self.suffix)))
            duplicate_next = f"_{duplicate_count + 1}"
            duplicate_suffix = duplicate_next.zfill(zero_fill)

            filename = self.add_suffix(duplicate_suffix)
        else:
            filename = self.with_stem(new_name)

        if preserve_metadata is True:
            return FileHandler(copy2(self.resolve(), self.parent.joinpath(filename, self.suffix), self.is_symlink()))
        else:
            return FileHandler(copy(self.resolve(), self.parent.joinpath(filename, self.suffix).resolve(), self.is_symlink()))

class DirectoryHandler(Path):
    def __init__(self, dir_path: str) -> None:
        super().__init__(dir_path)

    def scan_path(self, glob: str = '*'):
        """
        Parameters
        ----------
        glob : str, optional
            _description_, by default '*'

        Yields
        ------
        _type_
            _description_
        """
        for f in self.iterdir():

            if f.is_dir():
                pass
            elif f.is_file():
                pass
            yield f