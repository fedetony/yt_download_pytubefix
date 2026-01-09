# -*- mode: python ; coding: utf-8 -*-
# run with:  pyinstaller --clean yt_pytubefix_pyinstaller.spec  --noconfirm
import os
import sys
import platform
import re

system = platform.system()
sys_txt = ""
if system == "Windows":
    sys_txt = "_Win"
elif system == "Linux":
    sys_txt = "_Linux"
elif system == "Darwin":
    sys_txt = "_Mac"

from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, FixedFileInfo, StringFileInfo,
    StringTable, StringStruct, VarFileInfo, VarStruct,
)

# Determine project path safely
if 'specfile' in globals():
    project_path = os.path.dirname(os.path.abspath(specfile))
else:
    project_path = os.getcwd()

main_script = os.path.join(project_path, "yt_pytubefix_main.py")

# Extract version
with open(main_script, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
APP_VERSION = match.group(1) if match else "0.0.0"

numeric = [int(x) if x.isdigit() else 0 for x in APP_VERSION.split(".")]
numeric += [0] * (4 - len(numeric))

sys_txt += "_V" + APP_VERSION.replace(".", "").replace(" ", "").strip()

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=tuple(numeric),
        prodvers=tuple(numeric),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904B0',
                [
                    StringStruct('CompanyName', 'YourName'),
                    StringStruct('FileDescription', 'yt_pytubefix GUI'),
                    StringStruct('FileVersion', APP_VERSION),
                    StringStruct('InternalName', 'yt_pytubefix_main'),
                    StringStruct('OriginalFilename', f'yt_pytubefix_main{sys_txt}.exe'),
                    StringStruct('ProductName', 'yt_pytubefix GUI'),
                    StringStruct('ProductVersion', APP_VERSION),
                ]
            )
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)

img_path = os.path.join(project_path, "img")

# -------------------------
# THE ONLY VALID ANALYSIS
# -------------------------
a = Analysis(
    [main_script],
    pathex=[project_path],
    binaries=None,
    datas=None,
    hiddenimports=None,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

# after Analysis(...) and before PYZ
from PyInstaller.utils.hooks import copy_metadata
import glob, os, sys

def add_metadata_safe(pkg_name):
    meta = []
    try:
        meta = copy_metadata(pkg_name)
    except Exception:
        meta = []

    fixed = []
    for entry in meta:
        # entry may be (dest, src, type) or (name, src)
        if len(entry) == 3:
            fixed.append(entry)
        elif len(entry) == 2:
            name, src = entry
            dest = os.path.basename(name)
            fixed.append((dest, src, 'DATA'))
        else:
            raise RuntimeError("Unexpected metadata entry: %r" % (entry,))

    # fallback: find dist-info directly in the venv site-packages
    if not fixed:
        if sys.platform == 'win32':
            site_pkgs = os.path.join(sys.prefix, 'Lib', 'site-packages')
        else:
            site_pkgs = os.path.join(sys.prefix, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
        matches = glob.glob(os.path.join(site_pkgs, f'{pkg_name}-*.dist-info'))
        if not matches:
            # package not installed in this venv; skip silently
            return
        dist_info_path = matches[0]
        fixed.append((os.path.basename(dist_info_path), dist_info_path, 'DATA'))

    a.datas += fixed

# call add_metadata_safe for the packages you need
for pkg in [
    'imageio', 'imageio_ffmpeg', 'moviepy', 'numpy',
    'requests', 'urllib3', 'certifi',
    'websockets', 'aiohttp', 'async_timeout',
    'multidict', 'yarl', 'frozenlist',
    'pytubefix', 'yt_dlp', 'pillow',
    'PyQt5', 'selenium'
]:
    add_metadata_safe(pkg)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name=f'yt_pytubefix_main{sys_txt}',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(img_path, "main_icon.ico"),
)