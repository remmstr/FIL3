# Built-in modules
import argparse

# Internal modules
from core.config            import ApplicationInfo, ApplicationSettings
from core.logger            import ApplicationLog
from core.resource_manager  import FontLibrary, ImageLibrary, IconLibrary
from ui.window              import MainWindow

#~~~~~ LOGGING ~~~~~#

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

    # Set informations of the app
    ApplicationInfo(
        title="FIL3 - Gestionnaire de casques",
        version=(1, 0, 0)
        )

    # Set parameters of the app
    ApplicationSettings(theme_file="src/theme.json")

    # Start the application logger
    ApplicationLog(log_level=args.loglevel)

    # Loading ressources
    FontLibrary("assets/fonts")
    IconLibrary("assets/icons")
    ImageLibrary("assets/images")

    # Launch the application
    App = MainWindow()
    App.mainloop()

if __name__ == '__main__':
    main()