# Built-in modules
import sys
import platform
import argparse

# Internal modules
from core.config import WindowSettings, LoggerSettings
from core.resource import FontLibrary, ImageLibrary, IconLibrary
from ui.windows import MainWindow

#~~~~~ ARGUMENTS ~~~~~#

parser = argparse.ArgumentParser()
parser.add_argument("-log",
                    "--loglevel",
                    choices=['debug', 'info', 'warning', 'error', 'critical'],
                    default='info',
                    help='Change the log level that is output from the program.',
                    required=False)

args = parser.parse_args()

#~~~~~ MAIN ~~~~~#

def main():
    # Start the application logger
    LoggerSettings(log_level=args.loglevel)

    # Set parameters of the window
    WindowSettings(
        title='My python app',
        version=(1, 0, 0),
        win_icon='release/{os}/appicon.{ext}'.format(os=platform.system().lower(), ext='icns' if sys.platform == 'darwin' else 'ico'),
        taskbar_icon='release/linux/appicon.png',
        theme_file="res/theme.json"
    )

    # Loading ressources
    FontLibrary("res/fonts")
    IconLibrary("res/icons")
    # ImageLibrary("res/images")

    # Launch the application
    app_window = MainWindow()
    app_window.mainloop()

if __name__ == '__main__':
    main()