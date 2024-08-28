# FIL3.spec
# -*- mode: python ; coding: utf-8 -*-

import os
import sys

########################### PERMET DE BUILD AUSSI L'EXECUTABLE POUR MAC ###########################
import subprocess
subprocess.run(['python', '-m', 'PyInstaller', 'build_macos.spec'])
###################################################################################################



a = Analysis(
    ['src/__main__.py'],
    pathex=['../src'],
    binaries=[],
    datas=[
        ('res', 'res'),

        ('platform-tools', 'platform-tools'),
        ('src', 'src')
        #('../platform-tools', 'platform-tools'),
        #('../resources', 'resources')
        ],
    hiddenimports=['ppadb'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FIL3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    windowed=True,  # Add this line to create a windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
