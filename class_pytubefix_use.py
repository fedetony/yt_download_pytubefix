import re
import os
from pytubefix import YouTube, Playlist, Stream
from pytubefix.cli import on_progress
from pytubefix import Channel

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import proglog
from moviepy.editor import VideoFileClip, AudioFileClip

import class_file_dialogs


class use_pytubefix(QWidget):   
    download_start=QtCore.pyqtSignal(str,str)
    download_end=QtCore.pyqtSignal(str,str)
    on_progress=QtCore.pyqtSignal(list) 
    to_log=QtCore.pyqtSignal(str) 
    
    def __init__(self, *args, **kwargs):        
        super(use_pytubefix, self).__init__(*args, **kwargs)    
        self.__name__="pytubefix"
        self.cfd =class_file_dialogs.Dialogs()

    def _on_progress(self, stream: Stream,
                chunk: bytes,
                bytes_remaining: int
                ) -> None:  

        filesize = stream.filesize
        bytes_received = filesize - bytes_remaining
        self.display_progress_bar(bytes_received, filesize)

    def display_progress_bar(self,bytes_received, filesize):  
        if filesize <= 0:
            filesize=1
        self.on_progress.emit([bytes_received,filesize])
    
    def get_yt_video_from_url(self,url):
        try:
            yt = YouTube(url, on_progress_callback = self._on_progress)
        except Exception as eee:
            #print(eee)
            self.to_log.emit("Error Video: {}".format(eee))
            yt = None
        return yt

    def get_yt_playlist_from_url(self,url):
        try:
            pl = Playlist(url)
        except Exception as eee:
            #print(eee)
            self.to_log.emit("Error Playlist: {}".format(eee))
            pl = None
        return pl
    
    def get_yt_channel_from_url(self,url):
        try:
            ch = Channel(url)
        except Exception as eee:
            #print(eee)
            self.to_log.emit(f"Error Channel: {eee}")
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
            self.to_log.emit(f"PyTubefix Downloading: {yt.title}")
            if not mp3:
                ys = yt.streams.get_highest_resolution()
            else:
                ys = yt.streams.get_audio_only()
            try:
                self.download_start.emit(url,yt.title)
                ys.download(output_path = output_path,
                    filename = filename,
                    filename_prefix = filename_prefix,
                    skip_existing = skip_existing,
                    timeout = timeout,
                    max_retries = max_retries,
                    mp3 = mp3)
                self.download_end.emit(url,yt.title)
            except Exception as eee:
                #print(eee)
                self.to_log.emit("Error Downloading: {}".format(eee))
    
    def get_streams_available(self, url: str):
        """Gets progressive (audio and video together low resolution)
        and adaptive (audio and video together high resolution) streams"""
        yt = self.get_yt_video_from_url(url)
        ys_progressive=None
        ys_adaptive=None
        if yt:
            ys_progressive=yt.streams.filter(progressive=True,file_extension='mp4').desc()
            ys_adaptive = yt.streams.filter(adaptive=True,file_extension='mp4').desc()
        return ys_progressive,ys_adaptive


    def download_video_best_quality(self, url: str, output_path: str,
                filename: str = None,
                filename_prefix: str = None,
                skip_existing: bool = True,
                timeout: int = None,
                max_retries: int = 0,
                mp3: bool = False,
                ):    
        yt = self.get_yt_video_from_url(url)
        if yt:
            self.to_log.emit(f"PyTubefix Downloading: {yt.title}")
            if mp3:                
                ys = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
                try:
                    self.download_start.emit(url,yt.title)
                    ys.download(output_path = output_path,
                        filename = filename,
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    self.download_end.emit(url,yt.title)
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))
            else:
                try:
                    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
                    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
                    if not filename:
                        filename=self.clean_filename(yt.title,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ -')
                    filename_prefix_txt=""
                    if filename_prefix:
                        filename_prefix_txt=filename_prefix
                    # filename=self.cfd.extract_filename(filename,False)
                    complete_output_path=output_path+os.sep+filename_prefix_txt+filename+".mp4"
                    self.download_start.emit(url,yt.title)
                    if os.path.exists(complete_output_path) and skip_existing:
                        self.to_log.emit("Already existing: {}".format(complete_output_path))
                        self.download_end.emit(url,yt.title)
                        return
                    video_stream.download(output_path = output_path,
                        filename = "vid_"+filename+".mp4",
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    audio_stream.download(output_path = output_path,
                        filename = "aud_"+filename+".mp4",
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    vid_complete_output_path=output_path+os.sep+filename_prefix_txt+"vid_"+filename+".mp4"
                    aud_complete_output_path=output_path+os.sep+filename_prefix_txt+"aud_"+filename+".mp4"
                    self.to_log.emit(f"PyTubefix Downloaded video and audio file for: {yt.title}")
                    video_clip = VideoFileClip(vid_complete_output_path)
                    audio_clip = AudioFileClip(aud_complete_output_path)
                    self.to_log.emit(f"Joining video and audio file for: {yt.title}")
                    final_clip = video_clip.set_audio(audio_clip)
                    _the_logger=MyProgLogger()
                    _the_logger.set_signal_on_progress(self.on_progress)
                    final_clip.write_videofile(complete_output_path, codec='libx264',logger=_the_logger)
                    os.remove(vid_complete_output_path)
                    os.remove(aud_complete_output_path)
                    self.download_end.emit(url,yt.title)
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))

    def clean_filename(self, filename, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._ -'):
        """Remove all undesired characters from a file name while preserving the file extension.

        Args:
            filename (str): The file name to be cleaned.
            allowed_chars (str): A string of allowed characters. Defaults to 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._ -'.

        Returns:
            str: The cleaned file name.
        """
        base, extension = os.path.splitext(filename)
        cleaned_base = re.sub('[^' + allowed_chars + ']', '', base)
        return cleaned_base + extension
        
    
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
    
    def get_any_yt_videos_list(self,url: str):
        """
        Gets lists of titles and urls of any type of yt url 
        playlist, channel or video
        """
        vid_list=[]
        vid_list_url=[]
        is_valid, yt_type= self.is_yt_valid_url(url)
        if is_valid:
            if yt_type == 'channel':
                ch_name=self.get_channel_name(url)
                self.to_log.emit(f"Fetching videos from channel {ch_name}")
                return self.get_channel_video_list(url)
            elif yt_type == 'playlist':
                pl_title = self.get_playlist_name(url)
                self.to_log.emit(f"Fetching videos from playlist {pl_title}")
                return self.get_playlist_video_list(url)
            elif yt_type == 'video':    
                yt = self.get_yt_video_from_url(url)
                if yt:
                    vid_list=[yt.title]
                    vid_list_url=[url]
        return vid_list, vid_list_url

    def is_yt_valid_url(self,url: str):
        """
        Finds if the url is valid
        """
        if self.is_url_a_channel(url):
            return True,'channel'
        elif self.is_url_a_playlist(url):
            return True,'playlist' 
        elif self.is_url_a_video(url):
            return True,'video'
        return False,''
        

    def get_playlist_video_list(self,url: str):
        """
        Gets lists of titles and urls of a playlist url
        """
        pl=self.get_yt_playlist_from_url(url)
        vid_list=[]
        vid_list_url=[]
        if pl:
            try:
                for video in pl.videos:
                    vid_list.append(video.title)
                    vid_list_url.append(str(video.watch_url))
            except:
                pass
        return vid_list, vid_list_url
    
    def get_channel_video_list(self,url: str):
        """
        Gets lists of titles and urls of a channel url
        """
        ch=self.get_yt_channel_from_url(url)
        vid_list=[]
        vid_list_url=[]
        if ch:
            try:
                for video in ch.videos:
                    vid_list.append(video.title)
                    vid_list_url.append(str(video.watch_url))
            except:
                pass
        return vid_list, vid_list_url

    def is_url_a_channel(self,url):
        patterns = [
            r"(?:\/(c)\/([%\d\w_\-]+)(\/.*)?)",
            r"(?:\/(channel)\/([%\w\d_\-]+)(\/.*)?)",
            r"(?:\/(u)\/([%\d\w_\-]+)(\/.*)?)",
            r"(?:\/(user)\/([%\w\d_\-]+)(\/.*)?)",
            r"(?:\/(\@)([%\d\w_\-\.]+)(\/.*)?)"
        ]
        for pattern in patterns:
            regex = re.compile(pattern)
            function_match = regex.search(url)
            if function_match:
                return True
        return False
    
    def is_url_a_video(self,url):
        """
        Finds if is a video
        - :samp:`https://youtube.com/watch?v={video_id}`
        """
        patterns = [
            #r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", -> vid and playlist
            #r"^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=([0-9A-Za-z_-]{11})|https?:\/\/(?:www\.)?youtu\.be\/([0-9A-Za-z_-]{11})", -> vid and playlist
            r"^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=([0-9A-Za-z_-]{11})(?:&[^l]|$)|https?:\/\/(?:www\.)?youtu\.be\/([0-9A-Za-z_-]{11})",
        ]
        for pattern in patterns:
            regex = re.compile(pattern)
            function_match = regex.search(url)
            if function_match:
                return True
        return False

    def is_url_a_playlist(self,url):
        """
        Finds if is a playlist
        - :samp:`https://youtube.com/playlist?list={playlist_id}`
        - :samp:`https://youtube.com/watch?v={video_id}&list={playlist_id}`
        """
        patterns = [
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/(playlist\?list=|.*&list=)([a-zA-Z0-9_-]+)',
            r"^https?:\/\/(?:www\.)?youtube\.com\/playlist\?list=([0-9A-Za-z_-]{34})|^https?:\/\/(?:www\.)?youtube\.com\/(?:user\/|channel\/)?([a-zA-Z0-9_-]+)\/playlists\/([0-9A-Za-z_-]+)",
        ]
        for pattern in patterns:
            regex = re.compile(pattern)
            function_match = regex.search(url)
            if function_match:
                return True
        return False

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
                self.to_log.emit(f"{video.title}")
                if not mp3:
                    ys = video.streams.get_highest_resolution()
                else:
                    ys = video.streams.get_audio_only()
                try:
                    if filename:
                        new_filename = filename + "_" + str(nnn+1)
                    else:
                        new_filename = filename
                    self.download_start.emit(str(video.watch_url),video.title)
                    ys.download(output_path = output_path,
                        filename = new_filename,
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    self.download_end.emit(str(video.watch_url),video.title)
                except Exception as eee:
                    #print(eee)
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
        self.to_log.emit(f"{subtitles}")
    
    def get_subtitles(self,url,language='en'):
        yt = self.get_yt_video_from_url(url)
        if yt:
            try:
                caption = yt.captions.get_by_language_code(language)
                return caption.generate_srt_captions()
            except Exception as eee:
                #print(eee)
                self.to_log.emit("Error Captions: {}".format(eee))       
        return ''
    
    def save_subtitles_to_file(self,url,filename="captions.txt",language='en'):
        yt = self.get_yt_video_from_url(url)
        if yt:
            caption = yt.captions.get_by_language_code(language)
            caption.save_captions(filename)
    
    def get_channel_name(self,urlchannel):
        """
        Get the channel name
        """
        ch = self.get_yt_channel_from_url(urlchannel)
        if ch:
            self.to_log.emit(f'Channel name: {ch.channel_name}')
            return ch.channel_name
        return None
    
    def get_playlist_name(self,urlplaylist):
        """
        Get the playlist title
        """
        pl = self.get_yt_playlist_from_url(urlplaylist)
        if pl:
            #print(f'Playlist title: {pl.title}')
            return pl.title
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
        ccc = self.get_yt_channel_from_url(url)
        if ccc:
            self.to_log.emit(f'Downloading videos by: {ccc.channel_name}')
            for nnn, video in enumerate(ccc.videos):
                #ys = video.streams.get_audio_only()
                #ys.download(mp3=in_mp3) # pass the parameter mp3=True to save in .mp3
                self.to_log.emit(f'Downloading video: {video.title}')
                if not mp3:
                    ys = video.streams.get_highest_resolution()
                else:
                    ys = video.streams.get_audio_only()
                try:
                    if filename:
                        new_filename = filename + "_" + str(nnn+1)
                    else:
                        new_filename = filename
                    self.download_start.emit(str(video.watch_url),video.title)
                    ys.download(output_path = output_path,
                        filename = new_filename,
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        mp3 = mp3)
                    self.download_end.emit(str(video.watch_url),video.title)
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))

class MyProgLogger(proglog.ProgressBarLogger):
    def set_signal_on_progress(self,on_progress):
        """Sets signal """ 
        self.on_progress=on_progress

    def bars_callback(self, bar, attr, value, old_value=None):
        """Execute a custom action after the progress bars are updated.

        Parameters
        ----------
        bar
          Name/ID of the bar to be modified.

        attr
          Attribute of the bar attribute to be modified

        value
          New value of the attribute

        old_value
          Previous value of this bar's attribute.

        This default callback does nothing, overwrite it by subclassing.
        """
        try:
            self.on_progress.emit([value,self.state['bars'][bar]['total']])
        except (NameError,AttributeError):
            print(self.state)
            print( bar, attr, value, old_value)
        if value<1:
            print(self.state['bars'][bar][attr],self.state['bars'][bar]['total'])
            # {'bars': OrderedDict([('chunk', {'title': 'chunk', 'index': 0, 'total': 46010, 'message': None, 'indent': 0})]), 
            # 'message': 'MoviePy - Writing audio in FreeCAD020ForBeginners8PartvsPartDesignRevolveWorkflowsWhenandWheretouseTEMP_MPY_wvf_snd.mp3'}
            # {'bars': OrderedDict([('chunk', {'title': 'chunk', 'index': 46010, 'total': 46010, 'message': None, 'indent': 0}), 
            # ('t', {'title': 't', 'index': 0, 'total': 62598, 'message': None, 'indent': 2})]), 
            # 'message': 'Moviepy - Writing video D:/Tonys Data/Python/yt_download_pytubefix/Downloads\\FreeCAD020ForBeginners8PartvsPartDesignRevolveWorkflowsWhenandWheretouse.mp4\n'}
        # print( bar, attr, value, old_value)
    
    