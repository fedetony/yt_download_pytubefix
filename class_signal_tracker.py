"""
Signal tracker to connect dialogs and threads signals
F.Garcia
11.08.2024
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget

import class_pytubefix_use


class SignalTracker(QWidget):
    """
    Only incharged of signaling information when changes are present.
    signals for Enableing/disabling objects in GUI
    Or values to track positions,states etc..
    Signals then can be connected to GUI events.
    """

    # signals from pytube fix to main
    signal_th2m_thread_file_download_progress = QtCore.pyqtSignal(int, int, float)
    signal_th2m_thread_log_update = QtCore.pyqtSignal(str)
    signal_th2m_thread_end = QtCore.pyqtSignal(bool)
    signal_th2m_download_start = QtCore.pyqtSignal(str, str)
    signal_th2m_download_end = QtCore.pyqtSignal(str, str, str)
    signal_th2m_on_progress = QtCore.pyqtSignal(str, float)
    signal_th2m_to_log = QtCore.pyqtSignal(str)

    # signals from pytubefix to thread
    signal_ptf2th_download_start = QtCore.pyqtSignal(str, str)
    signal_ptf2th_download_end = QtCore.pyqtSignal(str, str, str)
    signal_ptf2th_on_progress = QtCore.pyqtSignal(str, float)
    signal_ptf2th_to_log = QtCore.pyqtSignal(str)

    # signals from log dialog
    signal_ld_logging_level=QtCore.pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__name__ = "Signal Tracker"
        self.ptf = class_pytubefix_use.use_pytubefix()
        self.ptf.to_log[str].connect(self.ptf2th_to_log)
        self.ptf.download_start[str, str].connect(self.ptf2th_download_start)
        self.ptf.download_end[str, str, str].connect(self.ptf2th_download_end)
        self.ptf.on_progress[list].connect(self.ptf2th_on_progress)

    def send_th_exit(self, fine_exit: bool):
        """Emits thread to main the thread exit

        Args:
            fine_exit (bool): True if exited normally, False if it was killed
        """
        self.signal_th2m_thread_end.emit(fine_exit)
        
    def send_th_log_update(self, text: str):
        """Emits thread to main the log text signal

        Args:
            text (str): text
        """
        self.signal_th2m_thread_log_update.emit(text)
    
    def send_ld_log_level(self, text: str):
        """Emits log dialog to main the log level signal

        Args:
            text (str): text
        """
        self.signal_ld_logging_level.emit(text)

    def send_th_file_download_progress(self, num_downloaded: int, num_total: int, per: float):
        """Emits thread to main the percentage file download progress

        Args:
            num_downloaded (int): Number of downloaded files
            num_total (int): Total to download
            per (float): percentage
        """
        self.signal_th2m_thread_file_download_progress.emit(num_downloaded, num_total, per)

    def send_download_start(self, url: str, title: str):
        """Emits from thread to main the pytubefix signal download_start

        Args:
            url (str): url
            title (str): title
        """
        self.signal_th2m_download_start.emit(url, title)

    def send_download_end(self, url: str, title: str, filename: str):
        """Emits from thread to main the pytubefix signal download_end

        Args:
            url (str): url
            title (str): title
        """
        self.signal_th2m_download_end.emit(url, title, filename)

    def send_to_log(self, txt: str):
        """Emits from thread to main the pytubefix signal to_log

        Args:
            txt (str): log string
        """
        self.signal_th2m_to_log.emit(txt)

    def send_on_progress(self, url: str, percentage: float):
        """Emits from thread to main the pytubefix signal on_progress

        Args:
            url (str): the url
            percentage (float): percentage
        """
        self.signal_th2m_on_progress.emit(url, percentage)

    def ptf2th_download_start(self, url: str, title: str):
        """Emits from pytubefix to thread signal download_start

        Args:
            url (str): url
            title (str): title
        """
        self.signal_ptf2th_download_start.emit(url, title)

    def ptf2th_download_end(self, url: str, title: str, filename: str):
        """Emits from pytubefix to to thread signal download_end

        Args:
            url (str): url
            title (str): title
        """
        self.signal_ptf2th_download_end.emit(url, title, filename)

    def ptf2th_to_log(self, txt: str):
        """Emits from pytubefix to thread signal to_log

        Args:
            txt (str): log string
        """
        self.signal_ptf2th_to_log.emit(txt)

    def ptf2th_on_progress(self, alist: list):
        """Emits from pytubefix to thread signal on_progress

        Args:
            url (str): the url
            percentage (float): percentage
        """
        self.signal_ptf2th_on_progress.emit(alist)
