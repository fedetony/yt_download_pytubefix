# -*- mode: python ; coding: utf-8 -*-

# run only as: pyinstaller --clean yt_pytubefix_pyinstaller.spec
#
# dist/
#     yt_pytubefix_gui/
#         yt_pytubefix_gui.exe
#         img/
#         libs/
#         config/
#         ... This is the installer folder to zip and distribute.

# don't use --onefile
import os
import sys

from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo, FixedFileInfo, StringFileInfo,
    StringTable, StringStruct, VarFileInfo, VarStruct,
)
import re
# Determine project path safely in all environments
if 'specfile' in globals():
    # When PyInstaller runs the spec file
    project_path = os.path.dirname(os.path.abspath(specfile))
else:
    # When running or linting the spec file manually
    project_path = os.getcwd()

with open(os.path.join(project_path, "yt_pytubefix_main.py"), "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
APP_VERSION = match.group(1) if match else "0.0.0"

numeric = [int(x) if x.isdigit() else 0 for x in APP_VERSION.split(".")]
numeric += [0] * (4 - len(numeric))  # pad to 4 numbers

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=tuple(numeric),       # major, minor, patch, build
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
                    StringStruct('InternalName', 'yt_pytubefix_gui'),
                    StringStruct('OriginalFilename', 'yt_pytubefix_gui.exe'),
                    StringStruct('ProductName', 'yt_pytubefix GUI'),
                    StringStruct('ProductVersion', APP_VERSION),
                ]
            )
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])
    ]
)

libs_path = os.path.join(project_path, "libs")
img_path = os.path.join(project_path, "img")
config_path = os.path.join(project_path, "config")

# Bundle your img folder (icons, PNGs, etc.)
datas = [
    (img_path, "img"),        # <--- your icons folder
]
# Add only .yml files from config/
for filename in os.listdir(config_path):
    if filename.endswith(".yml"):
        datas.append(
            (os.path.join(config_path, filename), os.path.join("config", filename))
        )


# Include external libs folder next to the EXE
if os.path.isdir(libs_path):
    datas.append((libs_path, "libs"))

# Exclude pytubefix and yt_dlp so they load from /libs
excluded = [
    "pytubefix",
    "yt_dlp",
]

main_script = os.path.join(project_path, "yt_pytubefix_gui.py")

a = Analysis(
    [main_script],
    pathex=[project_path],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name="yt_pytubefix_gui",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(img_path, "main_icon.ico"),  # <--- main icon here
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="yt_pytubefix_gui",
)
