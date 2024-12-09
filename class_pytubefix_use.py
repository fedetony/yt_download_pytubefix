import re
import os
import json
from pytubefix import YouTube, Playlist, Stream
from pytubefix.innertube import InnerTube
from pytubefix.cli import on_progress
from pytubefix import Channel,Caption

from PyQt5 import QtCore
from PyQt5.QtWidgets import *
import proglog
#from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

import class_file_dialogs

ALLOWED_CHARS = 'áéíóúüöäÜÖÄÁÉÍÓÚçÇabcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_ -'

CLIENT=InnerTube().client_name

class use_pytubefix(QWidget):   
    download_start=QtCore.pyqtSignal(str,str)
    download_end=QtCore.pyqtSignal(str,str,str)
    on_progress=QtCore.pyqtSignal(list) 
    to_log=QtCore.pyqtSignal(str) 
    
    def __init__(self, *args, **kwargs):        
        super(use_pytubefix, self).__init__(*args, **kwargs)    
        self.__name__="pytubefix"
        self.cfd =class_file_dialogs.Dialogs()
        self.po_token_verifier=None
        self._read_file_po_token()
        self.to_log.emit(f'potoken value: {self.po_token_verifier}')
        
    def _read_file_po_token(self):
        """Read Json file with potoken info
        """
        # here read potoken 
        filename=os.path.join(self.cfd.get_app_path(),'token_info.json')
        if os.path.exists(filename):
            try: 
                with open(filename, encoding="utf-8") as fff:
                    data = fff.read()
                    # reconstructing the data as a dictionary
                    fff.close()
                js_data = json.loads(data)
                self.po_token_verifier=(js_data['visitor_data'],js_data['po_token'])
            except Exception as eee:
                self.po_token_verifier = None
                self.to_log.emit(f'Error Failed to read token_info.json: {eee}')
        else:
            self.to_log.emit(f'Warning Could not find potoken file {filename}')

        #if not self.po_token_verifier:
        #    self._set_po_token_manually()

    def clear_po_token(self):
        """Delete potoken file and reset potoken
        """
        self.po_token_verifier=None
        # here delete cache file
        try:
            filename=os.path.join(self.cfd.get_app_path(),'token_info.json')
            os.remove(filename)
        except Exception as eee:
            self.to_log.emit(f'Error Failed to remove token info: {eee}')

    def save_token_info_to_json(self, token_info: tuple[str]):
        """
        Saves token information to a JSON file.

        Args:
            token_info (Optional[TokenInfo]): Token info object.
            filename (str): Name of the output JSON file. Defaults to 'token_info.json'.
        """
        filename=os.path.join(self.cfd.get_app_path(),'token_info.json')
        visitor_data = token_info[0]
        po_token = token_info[1]
        # Create a dictionary with the extracted information
        data_dict = {
            'visitor_data': visitor_data,
            'po_token': po_token
        }
        try:
            # Open the file in write mode and load any existing content
            with open(filename, 'w', encoding="utf-8") as fff:
                json.dump(data_dict, fff)
                self.to_log.emit(f'Token info saved to {filename}')
        except Exception as eee:
            self.to_log.emit(f'Error Failed to save token info: {eee}')

    def _set_po_token_manually(self):
        """Generate the token_info.json file with potoken data input
        """
        if not self.po_token_verifier:
            verifier=self.cfd.get_text_dialog("YT anti robot verification Verifier","Please type the Visitor\n")
            potoken=self.cfd.get_text_dialog("YT anti robot verification Potoken","Please type the Proof of Origin Token (potoken)\n")
            if verifier and potoken:
                if len(potoken)<160:
                    self.to_log.emit(f'Warning potoken will probably not work!')
                self.po_token_verifier=(verifier,potoken)
                do_save=self.cfd.send_question_yes_no_msgbox("Set Potoken?",f"Do you want to set the following potoken into file? \n Visitor: {verifier}\n po_token: {potoken}")
                if do_save:
                    self.save_token_info_to_json(self.po_token_verifier)
                    self.to_log.emit(f"Manual potoken set: {self.po_token_verifier}")
                else:
                    self.to_log.emit(f"Manual potoken set for this session: {self.po_token_verifier}")
            else:
                self.to_log.emit("Error No Manual potoken set!")
                self.po_token_verifier=None

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

    def call_po_token(self):
        return self.po_token_verifier
    #clients: WEB, WEB_EMBED, WEB_MUSIC, WEB_CREATOR, WEB_SAFARI, ANDROID, ANDROID_MUSIC, ANDROID_CREATOR, ANDROID_VR, ANDROID_PRODUCER
    # , ANDROID_TESTSUITE, IOS, IOS_MUSIC, IOS_CREATOR, MWEB, TV_EMBED, MEDIA_CONNECT

    def get_yt_video_from_url(self,url,client=CLIENT,use_po_token=True): #'WEB_CREATOR'):
        try:
            #if client=='WEB':
            #    yt = YouTube(url, client=client, use_po_token=True, on_progress_callback = self._on_progress)
            #else:
            #    yt = YouTube(url, client=client, on_progress_callback = self._on_progress)
            if use_po_token:
                if not self.po_token_verifier:
                    self.to_log.emit("Adaptive files require a potoken to download correctly!")
                    self.to_log.emit(f"Set file token_info.json in {self.cfd.get_app_path()} folder!\nIf you don't have one, it can be generated by running potoken-generator program!")
                    #if self.cfd.send_question_yes_no_msgbox("Manual input of potoken","Would you like to input the Proof of Origin Token (potoken) manually?"):
                    self._set_po_token_manually()
                if self.po_token_verifier is not None:
                    yt = YouTube(url, client=client,use_po_token=use_po_token, po_token_verifier=self.call_po_token, on_progress_callback = self._on_progress)
                else:
                    yt = None
            else:
                yt = YouTube(url, client=client, on_progress_callback = self._on_progress)
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
                if not filename:
                    filename=self.clean_filename(yt.title,ALLOWED_CHARS)+'.mp4'
                ys.download(output_path = output_path,
                    filename = filename,
                    filename_prefix = filename_prefix,
                    skip_existing = skip_existing,
                    timeout = timeout,
                    max_retries = max_retries,
                    )#mp3 = mp3)
                self.download_end.emit(url,yt.title,filename)
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
            try:
                ys_progressive=yt.streams.filter(progressive=True,file_extension='mp4').desc()
            except:
                ys_progressive=None
            try:
                ys_adaptive = yt.streams.filter(adaptive=True,file_extension='mp4').desc()
            except:
                ys_adaptive=None
        return ys_progressive,ys_adaptive

    def download_video_selected_quality(self, url: str, output_path: str,
                filename: str = None,
                filename_prefix: str = None,
                skip_existing: bool = True,
                timeout: int = None,
                max_retries: int = 0,
                mp3: bool = False,
                selected_resolution: tuple = ()
                ):    
        """Downloads a audio or a video with selected quality

        Args:
            url (str): url of yt video
            output_path (str): path
            filename (str, optional): filename. Defaults to None.
            filename_prefix (str, optional): prefix. Defaults to None.
            skip_existing (bool, optional): if file exists skip. Defaults to True.
            timeout (int, optional): timeout for download. Defaults to None.
            max_retries (int, optional): retries. Defaults to 0.
            mp3 (bool, optional): if mp3. Defaults to False.
            selected_resolution (tuple, optional): resolution string (v_itag, a_itag) or (v_itag,)  
                        Defaults to ().
        """
        if len(selected_resolution)==0:
            self.to_log.emit(f"No resolution given, setting max resolution!")
            return self.download_video_best_quality(url, output_path,filename,filename_prefix,skip_existing,timeout,max_retries,mp3) 
        yt = self.get_yt_video_from_url(url,use_po_token=True)
        if yt:
            if not filename:
                filename=self.clean_filename(yt.title,ALLOWED_CHARS)
            self.to_log.emit(f"PyTubefix Downloading {selected_resolution}: {yt.title}")
            if mp3:    
                if len(selected_resolution)==2:
                    ys = yt.streams.get_by_itag(selected_resolution[1])
                else:            
                    ys = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
                try:
                    self.download_start.emit(url,yt.title)
                    ys.download(output_path = output_path,
                        filename = filename + '.mp4',
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        )#mp3 = mp3)
                    self.download_end.emit(url,yt.title,filename + '.mp4')
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit(f"Error Downloading {selected_resolution}: {eee}")
            else:
                try:
                    if len(selected_resolution)==2:
                        video_stream = yt.streams.get_by_itag(selected_resolution[0])
                        audio_stream = yt.streams.get_by_itag(selected_resolution[1])
                        res="_"+str(video_stream.resolution)+"_"+str(audio_stream.bitrate)
                        filename_prefix_txt = ""
                        if filename_prefix:
                            filename_prefix_txt=filename_prefix
                        # filename=self.cfd.extract_filename(filename,False)
                        complete_output_path=output_path+os.sep+filename_prefix_txt+filename+res+".mp4"
                        self.download_start.emit(url,yt.title)
                        if os.path.exists(complete_output_path) and skip_existing:
                            self.to_log.emit("Already existing: {}".format(complete_output_path))
                            self.download_end.emit(url,yt.title,filename+res+".mp4")
                            return
                        video_stream.download(output_path = output_path,
                            filename = "vid_"+filename+".mp4",
                            filename_prefix = filename_prefix,
                            skip_existing = skip_existing,
                            timeout = timeout,
                            max_retries = max_retries,
                            )#mp3 = mp3)
                        audio_stream.download(output_path = output_path,
                            filename = "aud_"+filename+".mp4",
                            filename_prefix = filename_prefix,
                            skip_existing = skip_existing,
                            timeout = timeout,
                            max_retries = max_retries,
                            )#mp3 = mp3)
                        vid_complete_output_path = output_path + os.sep + filename_prefix_txt + "vid_" + filename + ".mp4"
                        aud_complete_output_path = output_path + os.sep + filename_prefix_txt + "aud_" + filename + ".mp4"
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
                        self.download_end.emit(url,yt.title,filename+res+".mp4")
                    elif len(selected_resolution)==1:
                        self.to_log.emit(f"PyTubefix Downloading {selected_resolution}: {yt.title}")
                        ys = yt.streams.get_by_itag(selected_resolution[0])
                        self.download_start.emit(url,yt.title)
                        res = "_" + str(ys.resolution)
                        ys.download(output_path = output_path,
                            filename = filename + res + ".mp4",
                            filename_prefix = filename_prefix,
                            skip_existing = skip_existing,
                            timeout = timeout,
                            max_retries = max_retries,
                            )#mp3 = mp3)
                        self.download_end.emit(url,yt.title,filename + res + ".mp4")
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))

    def download_video_best_quality(self, url: str, output_path: str,
                filename: str = None,
                filename_prefix: str = None,
                skip_existing: bool = True,
                timeout: int = None,
                max_retries: int = 0,
                mp3: bool = False,
                ):  
        """Downloads a audio or a video with best quality

        Args:
            url (str): url of yt video
            output_path (str): path
            filename (str, optional): filename. Defaults to None.
            filename_prefix (str, optional): prefix. Defaults to None.
            skip_existing (bool, optional): if file exists skip. Defaults to True.
            timeout (int, optional): timeout for download. Defaults to None.
            max_retries (int, optional): retries. Defaults to 0.
            mp3 (bool, optional): if mp3. Defaults to False.
        """  
        yt = self.get_yt_video_from_url(url,use_po_token=True)
        if yt:
            if not filename:
                filename=self.clean_filename(yt.title,ALLOWED_CHARS)
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
                        )#mp3 = mp3)
                    self.download_end.emit(url,yt.title,filename)
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))
            else:
                try:
                    video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
                    audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
                    filename_prefix_txt=""
                    if filename_prefix:
                        filename_prefix_txt=filename_prefix
                    # filename=self.cfd.extract_filename(filename,False)
                    complete_output_path=output_path+os.sep+filename_prefix_txt+filename+".mp4"
                    self.download_start.emit(url,yt.title)
                    if os.path.exists(complete_output_path) and skip_existing:
                        self.to_log.emit("Already existing: {}".format(complete_output_path))
                        self.download_end.emit(url,yt.title,filename+".mp4")
                        return
                    video_stream.download(output_path = output_path,
                        filename = "vid_"+filename+".mp4",
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        )#mp3 = mp3)
                    audio_stream.download(output_path = output_path,
                        filename = "aud_"+filename+".mp4",
                        filename_prefix = filename_prefix,
                        skip_existing = skip_existing,
                        timeout = timeout,
                        max_retries = max_retries,
                        )#mp3 = mp3)
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
                    self.download_end.emit(url,yt.title,filename+".mp4")
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
        base = base.strip("¿?")
        cleaned_base = re.sub('[^' + allowed_chars + ']', '', base)
        return cleaned_base + extension
        
    
    def get_url_info(self,url:str)->dict:
        """Gets all info in the url.
        Args:
            url (str): url desired
        Returns:
            dict: All information of the video. 
        """
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

    def is_url_a_channel(self,url:str)->bool:
        """identify if url is a channel

        Args:
            url (str): url

        Returns:
            bool: True if is a channel
        """
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
            r'^https?:\/\/(?:www\.)?youtube\.com\/live\/([0-9A-Za-z_-]{11})',
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
                        )#mp3 = mp3)
                    self.download_end.emit(str(video.watch_url),video.title,new_filename)
                except Exception as eee:
                    #print(eee)
                    self.to_log.emit("Error Downloading: {}".format(eee))
    
    def download_mp3_authentication(self,url = "url", client='WEB_CREATOR'):
    
        # if you want to add authentication
        yt = YouTube(url, client=client, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
                
        ys = yt.streams.get_audio_only()

        ys.download() #mp3=True) # you will only get the request to authenticate once you download
    
    def view_subtitiles(self,url,client='WEB_CREATOR'):
        #Subtitle/Caption Tracks:
        #viewing available subtitles:
        yt = YouTube(url,client=client)
        subtitles = yt.captions
        self.to_log.emit(f"{subtitles}")
    
    def get_subtitles(self,url,language='en'):
        """Gets the "SubRip subtitle" captions.
        Args:
            url (str): url of video
            language (str, optional): Defaults to 'en'.
        """
        yt = self.get_yt_video_from_url(url)
        if yt:
            try:
                lang_list=[]
                lang_listtxt=[]
                for ct in yt.caption_tracks:
                    lang=self._extract_language_code(str(ct))
                    if lang:
                        lang_list.append(lang)
                        lang_listtxt.append(lang.replace("a.",""))
                if language in lang_listtxt:
                    caption = yt.captions["a."+language] #get_by_language_code(language)
                    return caption.generate_srt_captions()
            except Exception as eee:
                #print(eee)
                self.to_log.emit("Error Captions: {}".format(eee))       
        return ''
    
    def save_subtitles_to_file(self,url:str,filename:str="captions.txt",language:str='en'):
        """Saves subtitles to a file.

        Args:
            url (str): url of video
            filename (str, optional): Filename to be saved to. Defaults to "captions.txt".
            language (str, optional): If NONE will find all captions available and store them in different filename with filename_XX.txt format. Defaults to 'en'.
        """
        yt = self.get_yt_video_from_url(url)
        if yt:
            lang_list=[]
            lang_listtxt=[]
            for ct in yt.caption_tracks:
                lang=self._extract_language_code(str(ct))
                if lang:
                    lang_list.append(lang)
                    lang_listtxt.append(lang.replace("a.",""))
            if language in lang_listtxt:
                caption = yt.captions["a."+language] #get_by_language_code(language)
                if caption:
                    Caption.save_captions(caption,filename)
            elif language is None:
                for lang in lang_list:
                    caption = yt.captions[lang] #get_by_language_code(language)
                    langtxt=lang.replace("a.","_")
                    if ".txt" in filename:
                        filename=filename.replace(".txt",str(langtxt)+".txt")
                    else:
                        filename=filename+str(langtxt)+".txt"
                    if caption:
                        Caption.save_captions(caption,filename)
    
    def _extract_language_code(self,txt):
        """Define your regex pattern to extract language code """
        #pattern = r'(?<=code=\"a\.)[\w]{2}'
        pattern = r'(?<=code=\")[a\.\w]+'
        
        match = re.search(pattern, txt)
        
        if match:
            return match.group()
        else:
            return None
    
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
                        )#mp3 = mp3)
                    self.download_end.emit(str(video.watch_url),video.title,new_filename)
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
    
    