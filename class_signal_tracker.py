
from PyQt5 import QtCore
from PyQt5.QtWidgets import *

class signal_tracker(QWidget):
    '''
    Only incharged of signaling information when changes are present.
    signals for Enableing/disabling objects in GUI
    Or values to track positions,states etc..
    Signals then can be connected to GUI events.
    '''
    thread_file_download_progress=QtCore.pyqtSignal(int,int,float)        
    thread_log_update=QtCore.pyqtSignal(str)
    # signals from pytube fix
    ptf_download_start=QtCore.pyqtSignal(str,str)
    ptf_download_end=QtCore.pyqtSignal(str,str)
    ptf_on_progress=QtCore.pyqtSignal(str,float) 
    ptf_to_log=QtCore.pyqtSignal(str) 
    
    def __init__(self, *args, **kwargs):        
        super().__init__(*args, **kwargs)    
        self.__name__="Signal Tracker"
    
    def send_th_log_update(self,text:str):
        """Emits thread log text signal

        Args:
            text (str): text
        """
        self.thread_log_update.emit(text)

    def send_th_file_download_progress(self,num_downloaded:int,num_total:int,per: float):
        """Emits thread percentage file download progress

        Args:
            num_downloaded (int): Number of downloaded files
            num_total (int): Total to download
            per (float): percentage
        """
        self.thread_file_download_progress.emit(num_downloaded,num_total,per)
    
    def send_download_start(self,url:str,title:str):
        """Emits from thread pytubefix signal download_start

        Args:
            url (str): url
            title (str): title
        """
        self.ptf_download_start.emit(url,title)
    
    def send_download_end(self,url:str,title:str):
        """Emits from thread pytubefix signal download_end

        Args:
            url (str): url
            title (str): title
        """
        self.ptf_download_end.emit(url,title)
        
    def send_to_log(self,txt:str):
        """Emits from thread pytubefix signal to_log

        Args:
            txt (str): log string
        """
        self.ptf_to_log.emit(txt)
    
    def send_on_progress(self, url:str,percentage:float): 
        """Emits from thread pytubefix signal on_progress

        Args:
            url (str): the url
            percentage (float): percentage
        """
        self.ptf_on_progress.emit(url,percentage)

    