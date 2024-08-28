# -*- mode: python ; coding: utf-8 -*-
import os
import platform
from typing import Literal
from pathlib import Path

###################
##### METHODS #####
###################

def search_file(dir_path: str | Path, relative_to: str | None = None, pattern: str = '*', recursive: bool = True, set_same_root: bool = True):
    results = []
    source = []
    dest = []

    if isinstance(dir_path, str):
        dir_path = Path(dir_path)

    # List all files that correspond to the pattern in the path
    files = [path for path in dir_path.glob(pattern) if path.is_file()]

    for file in files:
        # Ignore all hidden files
        if file.stem.startswith('.'):
            continue

        source.append(str(file.resolve().relative_to(relative_to)))
        if set_same_root is True:
            dest.append(str(file.parent.resolve().relative_to(relative_to)))
        else:
            dest.append("{}/{}".format(dir_path.stem, file.parent.stem))

    # Search file on any folders that has been found
    if recursive is True:

        # List all folders available
        folders = [path for path in dir_path.glob('*') if path.is_dir()]

        for folder in folders:
            for file in folder.glob(pattern):
                # Ignore all hidden files
                if file.stem.startswith('.'):
                    continue

                if Path(file).is_file():
                    source.append(str(file.resolve().relative_to(relative_to)))
                    if set_same_root is True:
                        dest.append(str(file.parent.resolve().relative_to(relative_to)))
                    else:
                        dest.append("{}/{}".format(dir_path.stem, file.parent.stem))

    results += zip(source, dest)

    return results

#####################
##### VARIABLES #####
#####################

# Directory list
root_dir = Path(os.getcwd()).resolve()
release_dir = root_dir.joinpath("release", platform.system().lower())
bin_dir = release_dir.joinpath("bin")
ressource_dir = root_dir.joinpath("res")

# Program infos
scripts = ["src/__main__.py"]
binaries = []
datas = []
hiddenimports = []
program_name = "CTk Template"
bundle_id = "com.yourCompany.ctk-template"
version = "1.0.0"
icon_path = None
program_file = None

# Set the icon path and full program name for the specified OS
match platform.system().lower():
    case 'darwin':
        icon_path = str(release_dir.joinpath("appicon.icns"))
        program_file = "{}.app".format(program_name)
    case 'linux':
        icon_path = str(release_dir.joinpath("appicon.png"))
        program_file = "{}".format(program_name)
    case 'windows':
        icon_path = str(release_dir.joinpath("appicon.ico"))
        program_file = "{}.exe".format(program_name)

binaries += search_file(bin_dir, relative_to=root_dir, recursive=True)

datas += search_file(ressource_dir.joinpath("fonts"), relative_to=root_dir, pattern="*.ttf", set_same_root=True)
datas += search_file(ressource_dir.joinpath("icons"), relative_to=root_dir, pattern="*.png", set_same_root=True)
datas += search_file(ressource_dir, relative_to=root_dir, pattern="*.json", recursive=False, set_same_root=True)

hiddenimports.append("core.config")
hiddenimports.append("core.fileio")
hiddenimports.append("core.resource")
hiddenimports.append("core.constants")
hiddenimports.append("core.credantials")
hiddenimports.append("ui.panels")
hiddenimports.append("ui.utils")
hiddenimports.append("ui.widgets")
hiddenimports.append("ui.windows")

# pyinstaller
block_cipher = None

a = Analysis(
    scripts,
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=program_name,
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ctk_framework",
)
app = BUNDLE(
    coll,
    name=program_file,
    icon=icon_path,
    bundle_identifier=bundle_id
)