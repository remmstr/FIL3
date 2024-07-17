# FIL3.spec
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import platform


# Determine platform-specific paths
if platform.system() == 'Windows':
    adb_path = os.path.join('..', 'platform-tools', 'windows')
else:
    adb_path = os.path.join('..', 'platform-tools', 'mac')

a = Analysis(
    ['../src/FIL_interface.py'],
    pathex=[],
    binaries=[],
    datas=[
        (adb_path, 'platform-tools'),
        ('../resources', 'resources')
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
    name='FIL',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
