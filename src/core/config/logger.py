# Built-in modules
from logging import StreamHandler, Formatter, Handler, root

class LoggerSettings():
    """
    Base class for setting the logging system of the application.
    It's using the built-in module `logging` to handle the work.
    """
    log_handlers: list = []
    log_level: int = 10
    log_format: Formatter

    def __init__(self, log_level: int | str = 'info') -> None:
        """
        Initialize the logger

        Parameters
        ----------
        log_level : `int | str`, optional
            Set the level of logging that should be streamed when the application is running , by default is `'info'`
        """
        self.set_level(log_level)
        self.set_format(
            fmt='[%(asctime)s] [%(threadName)s] \x1b[47m[%(levelname)s]\x1b[m \x1b[30m[%(name)s]\x1b[m %(message)s',
            #datefmt='%Y/%m/%d %H:%M:%S'
            datefmt='%H:%M:%S'
            )
        self.add_handler(StreamHandler()) # Set the handler for stderr

    @classmethod
    def set_level(cls, level: int | str):
        """
        Set the level of logging that should be streamed when the application is running

        Parameters
        ----------
        level : `int | str`
            Only those value will be valid : debug(0), info(1), warn(2), warning(3), error(4)
        """
        # Check class type of level
        if isinstance(level, int):
            cls.log_level = level
        elif isinstance(level, str):
            cls.log_level = level.upper()
        
        root.setLevel(cls.log_level)

    @classmethod
    def set_format(cls, fmt: str, datefmt: str):
        """
        Set the format of the string that would be used as default format.

        Parameters
        ----------
        fmt : `str`
            The general format of the string. There is a lot of available helps on the internet to how format the string of a log.
        datefmt : `str`
            The format of the time
        """
        cls.log_format = Formatter(fmt=fmt, datefmt=datefmt)

    @classmethod
    def add_handler(cls, handler: Handler):
        """
        Add a new handler to the root logger

        Parameters
        ----------
        handler : `Handler`
            It can be any Handler based of `logging` module
        """
        cls.log_handlers.append(handler)

        # Check if handler has already a format
        if handler.formatter is None:
            cls.log_handlers[-1].setFormatter(cls.log_format)

        # Adding Handler to root
        root.addHandler(cls.log_handlers[-1])