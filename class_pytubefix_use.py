from pytubefix import YouTube, Playlist, Stream
from pytubefix.cli import on_progress
from pytubefix import Channel

from PyQt5 import QtCore
from PyQt5.QtWidgets import *

class use_pytubefix(QWidget):   
    download_start=QtCore.pyqtSignal(str)
    download_end=QtCore.pyqtSignal(str)
    on_progress=QtCore.pyqtSignal(list) 
    to_log=QtCore.pyqtSignal(str) 
    
    def __init__(self, *args, **kwargs):        
        super(use_pytubefix, self).__init__(*args, **kwargs)    
        self.__name__="pytubefix"

    def _on_progress(self, stream: Stream,
                chunk: bytes,
                bytes_remaining: int
                ) -> None:  

        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        self.display_progress_bar(bytes_received, filesize)

    def display_progress_bar(self,bytes_received, filesize):  
        self.on_progress.emit([bytes_received,filesize])
    
    def get_yt_video_from_url(self,url):
        try:
            yt = YouTube(url, on_progress_callback = self._on_progress)
        except Exception as eee:
            print(eee)
            self.to_log.emit("Error Video: {}".format(eee))
            yt = None
        return yt

    def get_yt_playlist_from_url(self,url):
        try:
            pl = Playlist(url)
        except Exception as eee:
            print(eee)
            self.to_log.emit("Error Playlist: {}".format(eee))
            pl = None
        return pl
    
    def get_yt_channel_from_url(self,url):
        try:
            ch = Channel(url)
        except Exception as eee:
            print(eee)
            self.to_log.emit("Error Channel: {}".format(eee))
            ch = None
        return ch

    def download_video(self, url: str, output_path: str = None,
                filename: str= None,
                filename_prefix: str = None,
                skip_existing: bool = True,
                timeout: int = None,
                max_retries: int = 0,
                mp3: bool = False,
                ):    
        yt = self.get_yt_video_from_url(url)
        if yt:
            print(yt.title)
            if not mp3:
                ys = yt.streams.get_highest_resolution()
            else:
                ys = yt.streams.get_audio_only()
            try:
                self.download_start.emit(yt.title)
                ys.download(output_path = output_path,
                    filename = filename,
                    filename_prefix = filename_prefix,
                    skip_existing = skip_existing,
                    timeout = timeout,
                    max_retries = max_retries,
                    mp3 = mp3)
                self.download_end.emit(yt.title)
            except Exception as eee:
                print(eee)
                self.to_log.emit("Error Downloading: {}".format(eee))

    
    def get_url_info(self,url):
        yt_info={}
        yt = self.get_yt_video_from_url(url)
        if yt:
            yt_info.update({"title":yt.title})
            yt_info.update({"age_restricted":yt.age_restricted})
            yt_info.update({"author":yt.author})
            yt_info.update({"caption_tracks":yt.caption_tracks})
            yt_info.update({"captions":yt.captions})
            yt_info.update({"channel_id":yt.channel_id})
            yt_info.update({"channel_url":yt.channel_url})
            yt_info.update({"chapters":yt.chapters})
            yt_info.update({"description":yt.description})
            yt_info.update({"length":yt.length})
            yt_info.update({"keywords":yt.keywords})
            yt_info.update({"publish_date":yt.publish_date})
            yt_info.update({"rating":yt.rating})
            yt_info.update({"key_moments":yt.key_moments})
            yt_info.update({"metadata":yt.metadata})
            yt_info.update({"views":yt.views})
            yt_info.update({"vid_info":yt.vid_info})
        return yt_info    
        
    def download_playlist(self,url: str, 
                output_path: str = None,
                filename: str= None,
                filename_prefix: str = None,
                skip_existing: bool = True,
                timeout: int = None,
                max_retries: int = 0,
                mp3: bool = False,
                ):    
        #if you want to download complete playlists:

        pl=self.get_yt_playlist_from_url(url)
        if pl:
            for nnn, video in enumerate(pl.videos):
                #ys = video.streams.get_audio_only()
                #ys.download(mp3=in_mp3) # pass the parameter mp3=True to save in .mp3
                print(video.title)
                if not mp3:
                    ys = video.streams.get_highest_resolution()
                else:
                    ys = video.streams.get_audio_only()
                try:
                    if filename:
                        new_filename = filename + "_" + str(nnn+1)
                    else:
                        new_filename = filename
                    self.download_start.emit(video.title)
                    ys.download(output_path = output_path,
                        filename = new_filename,
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    self.download_end.emit(video.title)
                except Exception as eee:
                    print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))
    
    def download_mp3_authentication(self,url = "url"):
    
        # if you want to add authentication
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
                
        ys = yt.streams.get_audio_only()

        ys.download(mp3=True) # you will only get the request to authenticate once you download
    
    def view_subtitiles(self,url):
        #Subtitle/Caption Tracks:
        #viewing available subtitles:
        yt = YouTube(url)
        subtitles = yt.captions

        print(subtitles)
    
    def get_subtitiles(self,url,language='en'):
        yt = self.get_yt_video_from_url(url)
        if yt:
            try:
                caption = yt.captions.get_by_language_code(language)
                return caption.generate_srt_captions()
            except Exception as eee:
                print(eee)
                self.to_log.emit("Error Captions: {}".format(eee))       
        return ''
    
    def save_subtittles_to_file(self,url,filename="captions.txt",language='en'):
        yt = self.get_yt_video_from_url(url)
        if yt:
            caption = yt.captions.get_by_language_code(language)
            caption.save_captions(filename)
    
    def get_channel_name(self,urlchannel="https://www.youtube.com/@ProgrammingKnowledge/featured"):
        #Using Channels:
        #get the channel name:
        ch = self.get_yt_channel_from_url(urlchannel)
        if ch:
            print(f'Channel name: {ch.channel_name}')
            return ch.channel_name
        return None
    
    def download_all_videos_from_a_channel(self,url: str, 
                output_path: str = None,
                filename: str= None,
                filename_prefix: str = None,
                skip_existing: bool = True,
                timeout: int = None,
                max_retries: int = 0,
                mp3: bool = False,
                ):    
        # to download all videos from a channel:
        c = self.get_yt_channel_from_url(url)
        if c:
            print(f'Downloading videos by: {c.channel_name}')
            for nnn, video in enumerate(c.videos):
                #ys = video.streams.get_audio_only()
                #ys.download(mp3=in_mp3) # pass the parameter mp3=True to save in .mp3
                print(video.title)
                if not mp3:
                    ys = video.streams.get_highest_resolution()
                else:
                    ys = video.streams.get_audio_only()
                try:
                    if filename:
                        new_filename = filename + "_" + str(nnn+1)
                    else:
                        new_filename = filename
                    self.download_start.emit(video.title)
                    ys.download(output_path = output_path,
                        filename = new_filename,
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    self.download_end.emit(video.title)
                except Exception as eee:
                    print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))