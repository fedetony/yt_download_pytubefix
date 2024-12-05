"""
Download Thread for Pytubefix
F.Garcia
11.08.2024
Streaming Handle thread.
Is alive meanwhile there are downloads.
"""

import threading
import queue
import logging
import re

# from common import *
import class_pytubefix_use
import class_signal_tracker


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(levelname)s] (%(threadName)-10s) %(message)s")
ahandler = logging.StreamHandler()
ahandler.setLevel(logging.INFO)
ahandler.setFormatter(formatter)
log.addHandler(ahandler)
log.propagate = False


class ThreadQueueDownloadStream(threading.Thread):
    """A thread class to buffer and deliver the downloads using pytubefix
    The thread performs the downloads in background while GUI handles the thread.
    Can multithread for several simultaneous downloads. Each thread will download sequentially
    the files given.
    """

    def __init__(self, file_properties_dict: dict, cycle_time: float, kill_event: threading.Event, st : class_signal_tracker.SignalTracker):
        """Thread initiation

        Args:
            file_properties_dict (dict): index is an int from 0 to number of files
             {
            index:{
                "URL": ... str,
                "output_path": ... str = None,
                "filename": ... str = None,
                "filename_prefix": ... str = None,
                "skip_existing": ... bool = True,
                "timeout": ... int = None,
                "max_retries": ... int = 0,
                "mp3": ... bool = False,
                }
            }
            cycle_time (float):time forthread to wait between loops in seconds
            kill_event (threading.Event): threading event to kill thread externally
        """
        threading.Thread.__init__(self, name="File download thread")
        self.ptf = class_pytubefix_use.use_pytubefix()
        self.st = st # class_signal_tracker.SignalTracker()

        self.ptf.to_log[str].connect(self.pytubefix_log)
        self.ptf.download_start[str, str].connect(self.pytubefix_download_start)
        self.ptf.download_end[str, str, str].connect(self.pytubefix_download_end)
        self.ptf.on_progress[list].connect(self.pytubefix_download_progress)

        self.cycle_time = cycle_time
        self.killer_event = kill_event
        self.file_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.file_queue_size = self.file_queue.qsize()
        self.out_queue_size = self.output_queue.qsize()
        self.progress_bar_ini = 0
        self.progress_bar_end = 100
        self.st.send_th_file_download_progress(0, 0, 0)
        # event handled
        self.event_finished_one_file_download = threading.Event()
        self.event_finished_one_file_download.clear()
        self.event_get_next_file_to_download = threading.Event()
        self.event_get_next_file_to_download.clear()
        self.is_file_download_finished = False
        self.download_finished = False
        self.download_stream_size = 0
        self.max_buffer_size = 10
        url_list = self.get_url_list(file_properties_dict)
        self.file_list = url_list
        self.file_properties_dict = file_properties_dict
        self.number_of_files_to_download = len(url_list)
        self.number_of_files_downloaded = 0
        self.set_files_to_file_queue(url_list)
        self.actual_url_info = {}
        self.actual_url = ""
        self.actual_url_properties = {}
        self.actual_url_index = -1
        # self.last_print = [0, 0, 0]

    def get_url_list(self, file_properties_dict: dict) -> list:
        """Get URL list of files to download

        Args:
            file_properties_dict (dict): dictionary containing all downloads file information

        Returns:
            list: list of url addresses
        """
        url_list = []
        for properties in file_properties_dict:
            try:
                url_list.append(file_properties_dict[properties]["URL"])
            except (KeyError, TypeError, AttributeError, ValueError):
                url_list = []
                break
        return url_list

    def get_download_options_for_url(self, index: int, url: str) -> dict:
        """Get the download options / properties for the download
            file_properties_dict = {
            index:{
                "URL": ... str,
                "output_path": ... str = None,
                "filename": ... str= None,
                "filename_prefix": ... str = None,
                "skip_existing": ... bool = True,
                "timeout": ... int = None,
                "max_retries": ... int = 0,
                "mp3": ... bool = False,
                "selected_resolution": .... str = None
                }
            }
            Each file has to have an options dictionary
        Args:
            index (int): enumerated from 0 to N files
            url (str): file url

        Returns:
            dict: _description_
        """
        url_properties = {}
        for properties_key in self.file_properties_dict:
            try:
                prop_dict = self.file_properties_dict[properties_key]
                if url == prop_dict["URL"] and str(index) == str(properties_key):
                    url_properties = prop_dict
            except (KeyError, TypeError, AttributeError, ValueError) as eee:
                log.error("Getting Download properties: %s", eee)
                url_properties = {}
        return url_properties

    def pytubefix_log(self, log_msg: str):
        """
        Logs message from pytubefix
        Args:
             log_msg (str): message
        """
        self.st.send_to_log(log_msg)
        if "error" in log_msg.lower():
            #log.error("Error while downloading %s %s", self.actual_url_index, self.actual_url_info)
            log.error("Error while downloading %s", self.actual_url_index)
            log.error(log_msg)
            self.quit()
        elif "warning" in log_msg.lower():
            log.warning(log_msg)
        else:
            log.info(log_msg)

    def pytubefix_download_progress(self, progress_list: list):
        """
        Shows download progress
        """
        # url = self.ongoing_download_url
        [bytes_received, filesize] = progress_list
        progress_per = self.get_progress_percentage(bytes_received, filesize, per_ini=0, per_end=100)
        self.st.send_on_progress(f"{self.actual_url_index} " + self.actual_url, progress_per)
        # print(f"{self.actual_url_index} " + self.actual_url, progress_per)

    def pytubefix_download_start(self, url: str, title: str):
        """Receives Signal form Pytube fix when a Download is started

        Args:
            url (str): url of download
            title (str): title of the download
        """
        self.st.send_download_start(f"{self.actual_url_index} " + url, title)
        log.info("Download started: %s \nURL: %s", title, url)
        #log.info(self.actual_url_info)

    def pytubefix_download_end(self, url: str, title: str, filename: str):
        """Receives Signal form Pytube fix when a Download is ended

        Args:
            url (str): url of download
            title (str): title of the download
            filename (str): output filename
        """
        self.st.send_download_end(f"{self.actual_url_index} " + url, title, filename)
        self.event_get_next_file_to_download.set()
        self.number_of_files_downloaded = self.number_of_files_downloaded + 1
        log.info("Download finished: %s \nURL: %s", title, url)

    def _get_itags_from_resolution_txt(self,res_text:str) -> tuple:
        """Extracts the initial numbers from the given text format.

        Args:
            res_text (str): The text format containing numbers.
            from '[ v_itag, v_res, (v_codec,a_codec)]' or
            '[(v_itag, a_itag),(v_res, a_bitrate),(v_codec,a_codec)]'

        Returns:
            tuple: A tuple containing the itag numbers.
            (v_itag, a_itag) or (v_itag,).
        """
        # Remove leading and trailing parentheses and quotes
        text = res_text.strip("[]\"'")
        parts = text.split(', ')
        if "(" in parts[0]:
            new_parts=[parts[0].strip("()\"'"),parts[1].strip("()\"'")]
        else:
            new_parts=[parts[0].strip("()\"'")]
        numbers = []

        # Iterate over each part
        for part in new_parts:
            # Use regular expression to extract the number from the part
            match = re.search(r'\d+(?:\.\d+)?', part)
            # If a match is found, add the number to the list
            if match:
                numbers.append(int(match.group()))
        # Return the extracted numbers as a tuple
        return tuple(numbers)


    def download_file(self):
        """Downloads the file and sets actual info data."""
        if self.event_get_next_file_to_download.is_set():
            # Clear flag
            self.event_get_next_file_to_download.clear()
            # get next url
            a_url = self.add_to_output_queue()
            if a_url is not None:
                # ----------------  here sets all options
                # Index initialized in -1 -> first index = 0
                self.actual_url_index = self.actual_url_index + 1
                self.actual_url = a_url
                self.actual_url_properties = self.get_download_options_for_url(self.actual_url_index, self.actual_url)
                #print(self.actual_url_properties)
                self.actual_url_info = self.ptf.get_url_info(a_url)
                if not self.actual_url_properties["selected_resolution"]:
                    outfn=self.ptf.download_video(
                        url=self.actual_url_properties["URL"],
                        output_path=self.actual_url_properties["output_path"],
                        filename=self.actual_url_properties["filename"],
                        filename_prefix=self.actual_url_properties["filename_prefix"],
                        skip_existing=self.actual_url_properties["skip_existing"],
                        timeout=self.actual_url_properties["timeout"],
                        max_retries=self.actual_url_properties["max_retries"],
                        mp3=self.actual_url_properties["mp3"],
                    )
                else:
                    items_resolution=self._get_itags_from_resolution_txt(self.actual_url_properties["selected_resolution"])
                    outfn=self.ptf.download_video_selected_quality(
                        url=self.actual_url_properties["URL"],
                        output_path=self.actual_url_properties["output_path"],
                        filename=self.actual_url_properties["filename"],
                        filename_prefix=self.actual_url_properties["filename_prefix"],
                        skip_existing=self.actual_url_properties["skip_existing"],
                        timeout=self.actual_url_properties["timeout"],
                        max_retries=self.actual_url_properties["max_retries"],
                        mp3=self.actual_url_properties["mp3"],
                        selected_resolution=items_resolution,
                    )
                

    def add_one_line_to_buffer_ev(self):
        """Set event to add one line"""
        self.event_finished_one_file_download.set()

    def quit(self):
        """Interrupts with kill event and exit the thread"""
        self.killer_event.set()

    def get_progress_percentage(
        self, value: float, total_value: float, per_ini: float = 0, per_end: float = 100
    ) -> float:
        """Calculates percentage, can be set to start and end in different values

        Args:
            value (float): value
            total_value (float): total value
            per_ini (float, optional): initial percentage value. Defaults to 0.
            per_end (float, optional): end percentage value. Defaults to 100.

        Returns:
            float: percentage in range selected
        """
        if value > total_value:
            return per_end
        if value < 0 or total_value <= 0:
            return per_ini
        if (per_end - per_ini) <= 0:
            per = min(abs(per_ini), abs(per_end))
            return per
        per = round(per_ini + (value / total_value) * (per_end - per_ini), 2)
        return per

    def refresh_progress_bar_files_downloaded(self):
        """Refresh and emit signal from download status"""
        progress_ = self.get_progress_percentage(
            self.number_of_files_downloaded, self.number_of_files_to_download, per_ini=0, per_end=100
        )
        self.st.send_th_file_download_progress(
            self.number_of_files_downloaded, self.number_of_files_to_download, progress_
        )

    def run(self):
        """Thread run loop function"""
        # set flag to start downloading
        self.event_get_next_file_to_download.set()
        count = 0
        # print('is file:',a_url)
        self.refresh_progress_bar_files_downloaded()
        while not self.killer_event.wait(self.cycle_time):
            try:
                # Read from the file until end and close it and set Pbar
                self.download_file()
                self.update_queue_sizes()

                # if self.event_finished_one_file_download.is_set()==True:
                #     self.event_get_next_file_to_download.set()
                #     self.event_finished_one_file_download.clear()

                # delay for refreshing in class
                if count >= 1000:
                    self.refresh_progress_bar_files_downloaded()
                    count = 0
                count = count + 1
                if self.download_finished:
                    break
            except Exception as e:
                self.killer_event.set()
                log.error(e)
                log.error("Stream Queue fatal error! exiting thread!")
                raise
        if self.download_finished:
            log.info("Successfully downloaded %s Files!", self.number_of_files_to_download)
        if self.killer_event.is_set():
            log.info("Stream Queue Killing event Detected!")
            log.info("Successfully downloaded %s File(s)!", self.number_of_files_downloaded)
        log.info("File download thread Ended!")
        # True if exit normally False was killed
        self.st.send_th_exit(not self.killer_event.is_set())
        # self.killer_event.set()
        # self.quit()

    def add_to_file_queue_from_url_list(self, a_url: str):
        """Adds a url to the file queue

        Args:
            a_url (str): url to add
        """
        if not self.is_file_download_finished:
            if a_url is not None:
                # video_info=self.ptf.get_url_info(a_url)
                self.file_queue.put(a_url)

    def update_queue_sizes(self):
        """Checks How many files are downloaded and how many are missing gives the finish thread signal"""
        self.file_queue_size = self.file_queue.qsize()
        self.out_queue_size = self.output_queue.qsize()
        # Finished when
        # self.file_queue_size is empty
        # and self.out_queue_size is self.number_of_files_to_download
        # to debug
        # new_print = [
        #     self.number_of_files_to_download,
        #     self.number_of_files_downloaded,
        #     self.file_queue_size,
        # ]
        # if new_print != self.last_print or self.download_finished:
        #     print(
        #         "Exit Condition ->",
        #         self.number_of_files_to_download == self.number_of_files_downloaded and self.file_queue_size,
        #     )
        #     print("(to dl, dlded , fqsize) ", new_print)
        #     self.last_print = new_print
        #     print("Finished ->", self.download_finished)

        if self.number_of_files_to_download == self.number_of_files_downloaded and self.file_queue_size == 0:
            self.download_finished = True

    def add_to_output_queue(self):
        """Adds next url to complete output queue

        Returns:
            str: url
        """
        a_url = None
        try:
            a_url = self.file_queue.get_nowait()
            self.output_queue.put(a_url)
        except queue.Empty:
            self.download_finished = True
        self.update_queue_sizes()
        self.refresh_progress_bar_files_downloaded()
        return a_url

    def set_files_to_file_queue(self, files_to_download: list):
        """sets the URLs in the list to the queue

        Args:
            files_to_download (list): list of URLs
        """
        if files_to_download is None or self.number_of_files_to_download == 0:
            log.error("No files to download!")
            self.quit()
        self.refresh_progress_bar_files_downloaded()
        for a_url in files_to_download:
            self.add_to_file_queue_from_url_list(a_url)


def main():
    """Standalone Test for stream"""
    print("You need PyQT signals to make it work :)")


if __name__ == "__main__":
    main()
