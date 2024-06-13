# FIL
### A ecire avant usage:  pip install -U pure-python-adb
python -m PyInstaller --onefile --clean --hidden-import ppadb --add-data "platform-tools:platform-tools" FIL.py
python -m PyInstaller FIL.spec