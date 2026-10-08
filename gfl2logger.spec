# -*- mode: python ; coding: utf-8 -*-

import platform
import re
from pathlib import Path


# Single source of truth for the bundle version, so the app's Info.plist cannot drift
# from the version the program reports.
version = re.search(
    r'^VERSION = "([^"]+)"',
    Path(SPECPATH, 'gfl2logger', 'utils', 'version.py').read_text(encoding='utf-8'),
    re.MULTILINE,
).group(1)

is_macos = platform.system() == 'Darwin'
icon = 'embed/icon.png' if is_macos else 'embed/icon.ico'

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('embed', 'embed')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

if is_macos:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='gfl2logger',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='gfl2logger',
    )
    app = BUNDLE(
        coll,
        name='gfl2logger.app',
        icon='embed/icon.png',
        bundle_identifier='org.gf2logger.app',
        info_plist={
            'CFBundleDisplayName': 'gfl2logger',
            'CFBundleShortVersionString': version,
            'CFBundleVersion': version,
        },
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [('O', None, 'OPTION'), ('O', None, 'OPTION')],
        name='gfl2logger',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon,
    )
