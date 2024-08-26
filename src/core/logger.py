# Built-in modules
from logging    import StreamHandler, Formatter, Handler, root

class ApplicationLog():
    log_handlers: list = []
    log_level: int = 10
    log_format: Formatter

    def __init__(self, log_level: int | str = 'info') -> None:
        self.set_level(log_level)
        self.set_format(
            fmt='[%(asctime)s] [%(threadName)s] \x1b[47m[%(levelname)s]\x1b[m \x1b[30m[%(name)s]\x1b[m %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S'
            )
        self.add_handler(StreamHandler()) # Set the handler for stderr

    @classmethod
    def set_level(cls, level: int | str):
        # Check class type of level
        if isinstance(level, int):
            cls.log_level = level
        elif isinstance(level, str):
            cls.log_level = level.upper()
        
        root.setLevel(cls.log_level)

    @classmethod
    def set_format(cls, fmt: str, datefmt: str):
        cls.log_format = Formatter(fmt=fmt, datefmt=datefmt)

    @classmethod
    def add_handler(cls, handler: Handler):
        cls.log_handlers.append(handler)

        # Check if handler has already a format
        if handler.formatter is None:
            cls.log_handlers[-1].setFormatter(cls.log_format)

        # Adding Handler to root
        root.addHandler(cls.log_handlers[-1])

class CTkLoggingHandler(Handler):
    terminator = '\n'

    def __init__(self, text_area, level: int | str = 0) -> None:
        super().__init__(level)
        self.text_area = text_area

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_area.write(msg + self.terminator)
        self.text_area.after(0, append)