from logging import Handler


class CTkLoggingHandler(Handler):
    terminator = '\n'

    def __init__(self, text_area, level: int | str = 0) -> None:
        super().__init__(level)
        self.text_area = text_area

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_area.emit(msg + self.terminator)
        self.text_area.after(0, append)