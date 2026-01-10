# -*- mode: python ; coding: utf-8 -*-
#############################################################
# Run with pyinstaller --clean yt_pytubefix_pyinstaller.spec
# dist/
#   yt_pytubefix_main_XXX_V#### <- your executable file in windows,linux or mac
#   img/ <- add image folder
#   config/ <-add config folder with yml and your potoken.json file if used
#############################################################
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

# Set data and metadata
from PyInstaller.utils.hooks import copy_metadata

packages = [
    'imageio', 'imageio_ffmpeg', 'moviepy', 'numpy',
    'requests', 'urllib3', 'certifi',
    'websockets', 'aiohttp', 'async_timeout',
    'multidict', 'yarl', 'frozenlist',
    'pytubefix', 'yt_dlp', 'pillow',
    'PyQt5', 'selenium'
]

img_path = os.path.join(project_path, "img")

datas = []

# Add your entire img folder
# datas.append((img_path, "img"))
for f in os.listdir(img_path):
    datas.append((os.path.join(img_path, f), "img"))

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas += collect_data_files("PyQt5")
datas += collect_data_files("moviepy")
datas += collect_data_files("PIL")
datas += collect_data_files("imageio")
datas += collect_data_files("certifi")

# hidden imports
hiddenimports = collect_submodules("PyQt5")
hiddenimports += collect_submodules("aiohttp") + collect_submodules("websockets")
hiddenimports += collect_submodules("moviepy")


# Add packages
for pkg in packages:
    try:
        datas += copy_metadata(pkg)
    except Exception:
        pass

project_final_name=f'yt_pytubefix_main{sys_txt}'

# Versioning Windows
if system == "Windows":
    from PyInstaller.utils.win32.versioninfo import (
        VSVersionInfo, FixedFileInfo, StringFileInfo,
        StringTable, StringStruct, VarFileInfo, VarStruct,
    )

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
else: 
    version_info = None

a = Analysis(
    [main_script],
    pathex=[project_path], # pathex=[], 
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name=project_final_name,
    version=version_info, 
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
    icon=os.path.join(img_path, "main_icon.ico"),
)
