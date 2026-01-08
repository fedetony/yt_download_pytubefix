import yt_dlp
import yaml
import os
from PyQt5 import QtCore
# from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import *
# from PyQt5.QtCore import QEventLoop


class use_ytdlp(QWidget):
    download_start = QtCore.pyqtSignal(str, str)
    download_end = QtCore.pyqtSignal(str, str, str)
    on_progress = QtCore.pyqtSignal(list)
    to_log = QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(use_ytdlp, self).__init__(*args, **kwargs)

        self.__name__ = "yt_dlp"

        # Optional: load a config file (same pattern as pytubefix)
        # If you want a separate YAML for yt_dlp:
        # self.config = self._load_yaml_config(os.path.join(APP_PATH, "config", "ytdlp_config.yml"))

        # Or simply store defaults here
        self.config = {
            "preferred_format": "bestvideo+bestaudio/best",
            "audio_format": "mp3",
            "audio_quality": "192",
            "max_retries": 3,
            "quiet": True,
        }

        self.to_log.emit("yt_dlp backend initialized")
    
    @staticmethod
    def _load_yaml_config(filepath):
        """Load yaml configuration"""
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)


    def download_with_ytdlp(self, url, output_path, filename):
        ydl_opts = {
            'outtmpl': f'{output_path}/{filename}.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_video_ytdlp(self,
                            url: str,
                            output_path: str = None,
                            filename: str = None,
                            filename_prefix: str = None,
                            skip_existing: bool = True,
                            timeout: int = None,
                            max_retries: int = 0,
                            mp3: bool = False):
        try:
            # Build output template
            if filename_prefix:
                outname = f"{filename_prefix}{filename}"
            else:
                outname = filename

            full_path = os.path.join(output_path, outname + ".mp4")
            if skip_existing and os.path.exists(full_path):
                self.download_start.emit(url, filename)
                self.download_end.emit(url, filename, outname + ".mp4")
                return

            ydl_opts = {
                "outtmpl": os.path.join(output_path, outname + ".%(ext)s"),
                "quiet": True,
                "noprogress": True,
                "ignoreerrors": True,
                "retries": max_retries,
            }

            # Audio-only mode
            if mp3:
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]
            else:
                ydl_opts["format"] = "bestvideo+bestaudio/best"
                ydl_opts["merge_output_format"] = "mp4"

            self.download_start.emit(url, filename)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.download_end.emit(url, filename, outname + ".mp4")

        except Exception as e:
            self.to_log.emit(f"yt_dlp error: {e}")

    def download_video_selected_quality(self, url, output_path, filename=None,
                                    filename_prefix=None, skip_existing=True,
                                    timeout=None, max_retries=0, mp3=False,
                                    selected_resolution=()):
        try:
            # Build output template
            if filename_prefix:
                outname = f"{filename_prefix}{filename}"
            else:
                outname = filename
            
            full_path = os.path.join(output_path, outname + ".mp4")
            if skip_existing and os.path.exists(full_path):
                self.download_start.emit(url, filename)
                self.download_end.emit(url, filename, outname + ".mp4")
                return
            
            # Build format string
            if mp3:
                fmt = "bestaudio/best"
            else:
                if len(selected_resolution) == 2:
                    v_itag, a_itag = selected_resolution
                    fmt = f"{v_itag}+{a_itag}"
                elif len(selected_resolution) == 1:
                    fmt = f"{selected_resolution[0]}"
                else:
                    fmt = "bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(output_path, outname + ".%(ext)s"),
                "retries": max_retries,
                "ignoreerrors": True,
                "noprogress": True,
            }

            if mp3:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            self.download_start.emit(url, filename)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.download_end.emit(url, filename, outname + ".mp4")

        except Exception as e:
            self.to_log.emit(f"yt_dlp error: {e}")
    
    def download_video_selected_quality(self, url, output_path, filename=None,
                                   filename_prefix=None, skip_existing=True,
                                   timeout=None, max_retries=0, mp3=False,
                                   selected_resolution=()):
        try:
            # Build output template
            if filename_prefix:
                outname = f"{filename_prefix}{filename}"
            else:
                outname = filename

            full_path = os.path.join(output_path, outname + ".mp4")
            if skip_existing and os.path.exists(full_path):
                self.download_start.emit(url, filename)
                self.download_end.emit(url, filename, outname + ".mp4")
                return
            
            # Build format string
            if mp3:
                fmt = "bestaudio/best"
            else:
                if len(selected_resolution) == 2:
                    v_itag, a_itag = selected_resolution
                    fmt = f"{v_itag}+{a_itag}"
                elif len(selected_resolution) == 1:
                    fmt = f"{selected_resolution[0]}"
                else:
                    fmt = "bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(output_path, outname + ".%(ext)s"),
                "retries": max_retries,
                "ignoreerrors": True,
                "noprogress": True,
            }

            if mp3:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            self.download_start.emit(url, filename)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.download_end.emit(url, filename, outname + ".mp4")

        except Exception as e:
            self.to_log.emit(f"yt_dlp error: {e}")
    
    def download_video_best_quality(self, url, output_path,
                                filename=None,
                                filename_prefix=None,
                                skip_existing=True,
                                timeout=None,
                                max_retries=0,
                                mp3=False):

        try:
            # Build output filename
            if not filename:
                filename = "video"

            if filename_prefix:
                outname = f"{filename_prefix}{filename}"
            else:
                outname = filename

            full_path = os.path.join(output_path, outname + ".mp4")
            if skip_existing and os.path.exists(full_path):
                self.download_start.emit(url, filename)
                self.download_end.emit(url, filename, outname + ".mp4")
                return
            
            # Format selection
            if mp3:
                fmt = "bestaudio/best"
            else:
                fmt = "bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "outtmpl": os.path.join(output_path, outname + ".%(ext)s"),
                "retries": max_retries,
                "ignoreerrors": True,
                "noprogress": True,
            }

            if mp3:
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }]

            self.download_start.emit(url, filename)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.download_end.emit(url, filename, outname + ".mp4")

        except Exception as e:
            self.to_log.emit(f"yt_dlp error: {e}")