# Simple GUI for pytubefix
---------------------------------------
![Python Logo](https://github.com/fedetony/yt_download_pytubefix/blob/master/img/main_icon48.png "GUI pytubefix V1.0beta by FG")
 This is a simple GUI to download videos from yt using pytubefix, for latest state check [my github][wp] account. Please contribute with bug reports, or enhancements you would like to have.

Here’s a polished, clearer, more inviting version of your description and feature list.  
It keeps your intent but reads smoother, more professional, and more user‑friendly.

---

# 📥 yt_pytubefix GUI — Simple YouTube Downloader

---

# 🎉 Introduction

**yt_pytubefix GUI** is a lightweight, user‑friendly desktop application built on top of the excellent `pytubefix` library. Its goal is simple: make downloading YouTube videos, playlists, and channels as smooth and frustration‑free as possible — no command‑line knowledge required.

Whether you want to archive your favorite videos, save playlists for offline viewing, extract metadata, or manage large batches of URLs, this tool gives you a clean and intuitive interface to get it done quickly.

The project is actively maintained, and new features from `pytubefix` can be used immediately when running from source. If you enjoy the tool, feel free to report bugs, request enhancements, or contribute improvements. Community feedback is always welcome and helps shape the next version.

---

# ✨ Features

### 📄 Manage URL Lists
- Create, load, and save custom lists of YouTube URLs.
- Add URLs in multiple ways:
  - Paste a single video, playlist, or channel URL.
  - Provide a comma‑separated list inside brackets:  
    `[URL1, URL2, URL3]`
  - Provide a space‑separated list:  
    `URL1 URL2 URL3`
- Automatic detection of playlists and channels.

### 🎯 Flexible Selection
- Select individual or multiple URLs for download.
- Multi‑selection support for batch operations.

### ⚙️ Smart Downloading
- Uses background threads to keep the GUI responsive while downloading.
- Choose resolution, codec, and format.
- Supports both **Progressive** and **Adaptive** streams.
- Save subtitles/captions to file.
- Export full metadata and technical information.

### 🎬 Post‑Download Tools
- Play downloaded videos directly from the interface.
- Remove video files from the results list or disk.

---

# 🧪 Run From Source (Recommended for Updating pytubefix)

If you want the **latest features and fixes** from `pytubefix`, the best way is to run the application directly from source. This allows the built‑in updater (in the **About** menu) to work correctly, because `pytubefix` must be installed via `pip` and cannot update itself inside a PyInstaller executable.

Follow these steps:

---

## 1. Clone the repository

```bash
git clone https://github.com/yourname/yourrepo.git
cd yourrepo
```

---

## 2. Create a virtual environment

### Windows
```powershell
python -m venv venv
```

### Linux
```bash
python3 -m venv venv
```

---

## 3. Activate the virtual environment

### Windows
```powershell
venv\Scripts\activate
```

### Linux
```bash
source venv/bin/activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `pytubefix`
- `yt_dlp`
- GUI dependencies
- all required libraries

---

## 5. Run the application from source

```bash
python yt_pytubefix_main.py
```

This launches the full GUI exactly as the packaged version does.

---

# 🔄 Updating pytubefix (Source Mode Only)

There are **two ways** to update `pytubefix` when running from source:

---

## ✔ Option A — Update via pip (recommended)

```bash
pip install --upgrade pytubefix
```

This ensures you always have the newest version.

---

## ✔ Option B — Use the built‑in updater (GUI)

1. Run the app from source:
   ```bash
   python yt_pytubefix_main.py
   ```
2. Open the **About** menu  
3. Click **Update pytubefix**

The updater will run `pip` internally and upgrade the package.

---

# ⚠️ Important Note About PyInstaller Builds

When running the **packaged executable**, updating `pytubefix` is **not possible**, because:

- PyInstaller bundles everything into a frozen environment  
- pip cannot modify packages inside the EXE  
- pytubefix wheels cannot be installed inside the frozen app  

So if you want the newest pytubefix features, **run from source**.

---

# 📦 Installation & Build Guide (Windows & Linux)

This project can be built into a standalone executable using **PyInstaller**.  
Below is a complete step‑by‑step guide for both platforms.

---

## 🧰 1. Clone the repository

```bash
git clone https://github.com/fedetony/yt_download_pytubefix.git
cd yourrepo
```

---

## 🐍 2. Create a virtual environment

### **Windows**
```powershell
python -m venv venv
```

### **Linux**
```bash
python3 -m venv venv
```

---

## ▶️ 3. Activate the virtual environment

### **Windows**
```powershell
venv\Scripts\activate
```

### **Linux**
```bash
source venv/bin/activate
```

---

## 🔍 4. Verify Python & pip point to the venv

Run:

```bash
where python
where pip
```

or on Linux:

```bash
which python
which pip
```

Both should show paths inside your `venv/` folder.

---

## 📦 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🛠 6. Install PyInstaller

```bash
pip install pyinstaller
```

---

## 🏗️ 7. Build the executable

Use the provided `.spec` file:

```bash
pyinstaller --clean yt_pytubefix_pyinstaller.spec
```

After the build completes, you’ll find the output in:

```
dist/
    yt_pytubefix_main_<OS>_V<version>/
```

Inside that folder:

- `yt_pytubefix_main_<OS>_V####` → your executable  
- `img/` → **copy and place your image folder here**  
- `config/` → **copy and place your config folder here**  
  - includes `.yml` files  
  - includes `potoken.json` if you use it  

---

## 📁 8. Prepare the distribution folder

Your final distributable folder should look like:

```
yt_pytubefix_main_<OS>_V####/
    yt_pytubefix_main_<OS>_V####  (the executable)
    img/
    config/
```

You can now zip this folder or distribute it as-is.

---

## 🎉 9. Run the application

### **Windows**
Double‑click the executable.

### **Linux**
Make it executable if needed:

```bash
chmod +x yt_pytubefix_main_Linux_V#### 
```

Then run:

```bash
./yt_pytubefix_main_Linux_V####
```

Enjoy using the GUI.

---

Absolutely — here’s an improved version of the configuration section that includes your clarification:  
**users may add or omit fields**, and pytubefix will automatically match supported attributes for each function (`Youtube`, `Channel`, `List`, etc.).  
This keeps things flexible while still warning users not to break the YAML structure.

---

# ⚙️ Configuration File (`pytubefix_config.yaml`)

The application uses a configuration file located in the **`config/`** folder:

```
config/pytubefix_config.yaml
```

This file controls how `pytubefix` authenticates with YouTube and which client profile it should emulate.  
Most users can leave the defaults unchanged, but advanced users may customize authentication or client behavior here.

---

## 🔐 Authentication & Client Settings

The YAML file contains a `Youtube` section where you can configure:

- which **client** profile pytubefix should emulate  
- whether to use **OAuth**  
- whether OAuth tokens may be cached  
- whether to use the legacy **PoToken** method (deprecated)

Here is the structure:

```
functions:
  Youtube:
    # clients: WEB, WEB_EMBED, WEB_MUSIC, WEB_CREATOR, WEB_SAFARI, ANDROID, ANDROID_MUSIC, ANDROID_CREATOR, ANDROID_VR, ANDROID_PRODUCER
    #          ANDROID_TESTSUITE, IOS, IOS_MUSIC, IOS_CREATOR, MWEB, TV_EMBED, MEDIA_CONNECT
    client: "ANDROID"
    use_oauth: false          # anonymous mode
    allow_oauth_cache: false  # do not store OAuth tokens
    # use_oauth: true         # enable if you want to authenticate via Google
    # allow_oauth_cache: true
    # use_po_token: true      # deprecated, ignored automatically
```

---

## ⚠️ Important Notes

### **1. Keep the YAML format intact**
YAML is indentation‑sensitive.  
If you break the spacing, remove colons, or misalign blocks, the application will fail to load the configuration.

### **2. Do not rename dictionary keys**
Keys such as:

- `functions`
- `Youtube`
- `client`

must remain exactly as written.

### **3. You *may* add or omit fields**
pytubefix is flexible:  
If a function (`Youtube`, `Channel`, `List`, etc.) supports a given attribute, it will automatically use it.  
If an attribute is missing or unsupported, pytubefix simply ignores it.

This means you can safely:

- add new fields introduced in future pytubefix versions  
- remove fields you don’t need  
- keep the file minimal or extended  

as long as the YAML structure remains valid. For example:
- `use_oauth: true`
- `allow_oauth_cache: true`

### **4. PoToken is deprecated**
If you still use `potoken.json`, place it inside the `config/` folder.  
However, pytubefix may ignore it automatically depending on the client and authentication mode.

---

## 📘 More Details

For advanced configuration, custom clients, or deeper authentication details, refer to the official pytubefix documentation:

👉 https://github.com/JuanBindez/pytubefix

---

Totally fair — no need to make it look like a corporate roadmap when it’s really just you building something cool in your spare time. Let’s keep it simple, honest, and human. Here’s a version that captures the spirit without pretending you’re a whole team.

---

# 🛠️ To‑Do (A Realistic List From a One‑Person Project)

This project is built and maintained by a single developer, so updates happen when time and energy allow. These are the things I *plan* to work on next — no promises, just goals.

- Add subtitle embedding for downloaded videos  
- Improve the logger (currently slow and occasionally buggy)  
- Support loading simple URL lists from `.csv` or `.txt`  
- Migrate the GUI from PyQt5 to PyQt6  
- Enable search functionality in the GUI (already implemented internally)  
- Activate optional `yt_dlp` backend support  
  - It’s already implemented, just not enabled yet  
  - Useful because YouTube changes constantly and some tools adapt faster  

---

Modified code from Potoken generator originally from [youtube-trusted-session-generator][pogen]. Modified to generate file as required.

---------------------------------------------------------------------------------------

![Python Logo](https://github.com/fedetony/yt_download_pytubefix/blob/master/img/main_icon48.png "GUI pytubefix V1.0beta by FG") If you like my work consider [supporting me!][sp]

G1(junas) Cesium: D9CFSvUHQDJJ4iFExVU4fTMAidADV8kedabeqtV6o3CS

BTC Bitcoin: n211bgvuTVfwFoV6xwcHE5pPe4zWuQ27je

[sp]: https://github.com/sponsors/fedetony

[Github web page][wp].

[wp]: https://github.com/fedetony

[pogen]: https://github.com/iv-org/youtube-trusted-session-generator

<p align="center"> <img src="https://img.shields.io/badge/With%20coffee%20and%20love%20by-FG-6f4e37?style=for-the-badge&logo=coffee&logoColor=white" /> </p>