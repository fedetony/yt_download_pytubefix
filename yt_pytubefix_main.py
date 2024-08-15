# -*- coding: utf-8 -*-
"""
# *********************************
# Author :F. Garcia
# Created 19.08.2022
# *********************************
"""
__author__ = "FG"
__version__ = "1.0.0 Beta"
__creationdate__ = "04.08.2024"
__gitaccount__ = "<a href=\"https://github.com/fedetony\">' Github for fedetony'</a>"

# Form implementation generated automaticaly from reading ui file 'yt_pytubefix_gui.ui'
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to 'yt_pytubefix_gui.py' will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


import sys
import os
import logging
import yaml
import requests
import threading
import time

from PyQt5 import QtCore, QtGui, QtWidgets

# from genericpath import isfile
# from operator import index

import class_file_dialogs
import class_table_widget_functions
import class_pytubefix_use
import class_signal_tracker
import thread_download_pytubefix
import yt_pytubefix_gui

# import datetime
# import json
# import re
# Setup Logger
# set up logging to file - see previous section for more details
log = logging.getLogger("")  # root logger
# For file
"""
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',
                    datefmt='%y-%m-%d %H:%M',
                    filename='/temp/__last_run__.log',
                    filemode='w')
"""
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s", datefmt="%y-%m-%d %H:%M"
)
# define a Handler which writes INFO messages or higher to the sys.stderr
# console = logging.StreamHandler()
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter("[%(levelname)s] (%(threadName)-10s) %(message)s")
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger("").addHandler(console)


class UiMainWindowYt(yt_pytubefix_gui.Ui_MainWindow):
    """GUI for handleing Pytubefix

    Args:
        yt_pytubefix_gui (_type_): Gui build automatically by useing Designer and
        python -m PyQt5.uic.pyuic -x yt_pytubefix_gui.ui  -o yt_pytubefix_gui.py
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.a_dialog = class_file_dialogs.Dialogs()
        self.app_path = ""
        self.general_config = {}
        self.download_path = ""
        self.url_struct = {}
        self.url_id_counter = 0
        self.ongoing_download_url = None
        self.ongoing_download_title = None
        self.url_struct_mask = {}
        self.url_struct_options = {}
        self.icon_main_pixmap = None
        self.icon_main_pixmap = None
        self.icon_main = None
        self.icon_main = None
        self.twf = None
        self.ptf = None
        self.st = None
        self.default_config_path = None
        self.path_config_file = None
        self.item_menu = None
        self.threads_event_list=[]
        self.threads_mapping_dict={}

    def start_up(self):
        """Start the UI first to get all objects in"""
        log.info("UI started!")
        # Initial conditions variables
        self.app_path = self.a_dialog.get_app_path()
        self.general_config = self.get_general_config()
        try:
            self.download_path = self.general_config["Last_Path_for_Download"][0]
            if not os.path.exists(self.download_path):
                self.download_path = self.app_path
        except (TypeError, KeyError):
            self.download_path = self.app_path
        self.url_struct = {}
        self.url_struct_mask = {
            "__any__": {
                "Index": {"__m__1": "is_unique", "__mv__1": ""},
                "Title": {"__m__1": "is_value_type", "__mv__1": str(str)},
                "URL": {"__m__1": "is_value_type", "__mv__1": str(str), "__m__2": "is_not_change", "__mv__2": ""},
                "DL Enable": {"__m__1": "is_value_type", "__mv__1": str(bool)},
                "MP3": {"__m__1": "is_value_type", "__mv__1": str(bool)},
                "Skip Existing": {"__m__1": "is_value_type", "__mv__1": str(bool)},
                "Timeout sec": {
                    "__m__1": "is_value_type",
                    "__mv__1": str(int),
                    "__m__2": "is_value_gteq",
                    "__mv__2": 0,
                },
                "Max Retries": {
                    "__m__1": "is_value_type",
                    "__mv__1": str(int),
                    "__m__2": "is_value_gteq",
                    "__mv__2": 0,
                    "__m__3": "is_value_lteq",
                    "__mv__3": 10,
                },
                "File Name": {"__m__1": "is_format", "__mv__1": r"^[a-zA-Z0-9._-]+(\.[a-zA-Z0-9._-]+)?$"},
                "File Name Prefix": {"__m__1": "is_format", "__mv__1": r"^[a-zA-Z0-9._-]+$"},
                "Download Path": {"__m__1": "is_not_change", "__mv__1": ""},
            },
            # This was to test restriction on a specific id :) works
            # "URL0": {
            #     "Title": {'__m__1':"is_value_type",'__mv__1':str(str),
            #             '__m__2':"is_not_change",'__mv__2':""},
            # },
        }

        self.url_id_counter = 0
        self.ongoing_download_url = None
        self.ongoing_download_title = None

    def setup_ui2(self, amain_window: QtWidgets.QMainWindow):
        """Start main

        Args:
            amain_window (QtWidgets.QMainWindow): Mainwindow Object From Mywindow Class
            Modifies the closing event.
        """
        # Add objects by code here additional to objects in GUI_PostProcessing
        # Or set configuration of objects
        # initial conditions
        self.start_up()
        # ------------- Mainwindow
        # set the icon
        path_to_file = self.app_path + os.sep + "img" + os.sep + "main_icon.png"
        file_exists = os.path.exists(path_to_file)
        self.icon_main_pixmap = None
        self.icon_main = None
        if file_exists:
            self.icon_main_pixmap = QtGui.QPixmap(path_to_file)
            self.icon_main = QtGui.QIcon(QtGui.QPixmap(path_to_file))
            amain_window.setWindowIcon(self.icon_main)

        # set the title
        amain_window.setWindowTitle("Gui for pytubefix by " + __author__ + " V" + __version__)
        # amain_window.showMaximized()

        # -----------TableWidgetFunctions

        self.twf = class_table_widget_functions.TableWidgetFunctions(
            self.tableWidget_url, self.url_struct, self.url_struct_mask, None, []
        )
        # self.model=self.twf.modelobj
        self.twf.signal_data_change[list, str, str, str].connect(self._table_widget_data_changed)
        self.twf.signal_item_button_right_clicked[list, QtCore.QPoint].connect(self._table_item_right_clicked)
        # self.icons_dict={'Plots':self.icon_main}

        # self.tvf.Expand_to_Depth(1)
        # self.tvf.set_Icons(self.icons_dict)

        # --------------use_pytubefix
        self.ptf = class_pytubefix_use.use_pytubefix()
        # self.st = class_signal_tracker.SignalTracker()
        # self.st.signal_th2m_to_log[str].connect(self.pytubefix_log)
        # self.st.signal_th2m_download_start[str, str].connect(self.pytubefix_download_start)
        # self.st.signal_th2m_download_end[str, str].connect(self.pytubefix_download_end)
        # self.st.signal_th2m_on_progress[str, float].connect(self.pytubefix_download_progress)

        # -----------Splitter
        # self._set_splitter_pos(400,1/3) #initial position
        # --------------
        self._set_path_labels()
        self.a_dialog.set_default_dir(self.app_path)
        self._connect_actions()

    def _table_widget_data_changed(self, track: list[str], val: any, valtype: str, subtype: str):
        """Sets the changed information in table widget by user into the Structure

        Args:
            track (list[str]): _description_
            val (any): _description_
            valtype (str): _description_
            subtype (str): _description_
        """
        # print("before: %s",self.url_struct)
        processed_val = self.twf.check_restrictions.set_type_to_value(val, valtype, subtype)
        self.twf.set_tracked_value_to_dict(track, processed_val, self.url_struct, subtype, False)
        self._update_shared_struct_options()
        # update shared values

    def _update_shared_struct_options(self):
        """Updates the info shared in both dictionaries"""

        for key_s in self.url_struct:
            struct_dict = self.url_struct[key_s]
            self.url_struct_options.update(
                {
                    key_s: {
                        "URL": struct_dict["URL"],
                        "output_path": (
                            self.download_path if struct_dict["Download Path"] == "" else struct_dict["Download Path"]
                        ),
                        "filename": None if struct_dict["File Name"] == "" else struct_dict["File Name"],
                        "filename_prefix": (
                            None if struct_dict["File Name Prefix"] == "" else struct_dict["File Name Prefix"]
                        ),
                        "skip_existing": struct_dict["Skip Existing"],
                        "timeout": None if int(struct_dict["Timeout sec"]) <= 0 else int(struct_dict["Timeout sec"]),
                        "max_retries": int(struct_dict["Max Retries"]),
                        "mp3": struct_dict["MP3"],
                    },
                }
            )
            self.url_struct_options[key_s].update({"mp3": self.url_struct[key_s]["MP3"]})

    def pytubefix_download_progress(self, url: str, per: float):
        """
        Shows download progress
        """
        # url = self.ongoing_download_url
        # This is momentary
        txt = f"Downloaded {per}% for {url}"
        log.info(txt)

    def pytubefix_download_start(self, url: str, title: str):
        """Receives Signal form Pytube fix when a Download is started

        Args:
            url (str): url of download
            title (str): title of the download
        """
        # print("========== >>>>>> Main got Signal Start <<<<<<< ==========  \n"*5)
        self.ongoing_download_url = url
        self.ongoing_download_title = title
        log.info("Download started for %s", title)

    def pytubefix_download_end(self, url: str, title: str):
        """Receives Signal form Pytube fix when a Download is ended

        Args:
            url (str): url of download
            title (str): title of the download
        """
        if url == self.ongoing_download_url:
            self.ongoing_download_url = None
            self.ongoing_download_title = None
        log.info("Download finished for %s", title)

    def pytubefix_log(self, log_msg: str):
        """
        Logs message from pytubefix
        Args:
             log_msg (str): message
        """
        if "error" in log_msg.lower():
            if self.ongoing_download_title:
                log.error("Error while downloading %s", self.ongoing_download_title)
                self.ongoing_download_title = None
                self.ongoing_download_url = None
            log.error(log_msg)
        elif "warning" in log_msg.lower():
            log.warning(log_msg)
        else:
            log.info(log_msg)

    def get_general_config(self):
        """
        Returns the configuration set in yml file
        """
        self.default_config_path = self.app_path + os.sep + "config" + os.sep + "cfg.yml"
        return self.open_configuration_yml_file(self.default_config_path)

    def open_configuration_yml_file(self, path_config_file):
        """
        Opens configuration file in yml format
        """
        path_config = ""
        try:
            with open(path_config_file, encoding="UTF-8") as file:
                path_config = yaml.load(file, Loader=yaml.SafeLoader)
                log.info("Environment configuration loaded")
                self.path_config_file = path_config_file
        except FileNotFoundError:
            log.error("Environment configuration file not found at %s", path_config_file)
            self.a_dialog.send_critical_msgbox(
                "Configuration File not Found!", "Please select location of configuration File"
            )
            errpath = self.a_dialog.open_file_dialog("7")  # 7->yml Files (*.yml)
            if errpath is None:
                with open(errpath, encoding="UTF-8") as file:
                    path_config = yaml.load(file, Loader=yaml.SafeLoader)
                    log.info("Environment configuration loaded")
                    log.warning("Save configuration path as %s to not be prompted for a file", self.default_config_path)
            else:
                raise
            # print(f"Create new {config_file} file?")
            # input_config(config_parameters)
            # generate_config_file(config_parameters)
        return path_config

    def _connect_actions(self):
        """
        Connect all objects
        """
        self.lineEdit_url.textChanged.connect(self._lineedit_url_changed)
        self.actionAbout.triggered.connect(self.show_aboutbox)
        self.actionSet_Path.triggered.connect(self.set_download_path)
        self.pushButton_url.pressed.connect(self._pushbutton_url_pressed)

        # right click menu

        self.tableWidget_url.customContextMenuRequested.connect(self._table_item_right_clicked)

    # Right click Menu
    def _table_item_right_clicked(self, track: list, apos: QtCore.QPoint):
        """Displays right click menu where item was right clicked

        Args:
            track (list): track of item
            apos (QtCore.QPoint): global position of event
        """
        id_key_list, track_list = self._get_id_key_list_from_selection()

        log.debug("Rightclick Selected->  id_key_list: %s, track_list %s, track %s", id_key_list, track_list, track)
        if len(track) == 0:
            return
        self.item_menu = QtWidgets.QMenu()
        menu_item01 = self.item_menu.addAction(f"Toggle {track}")
        self.item_menu.addSeparator()
        menu_item10 = self.item_menu.addAction(f"URL info {track[0]}")
        menu_item11 = self.item_menu.addAction(f"Set Download Path {id_key_list}")
        self.item_menu.addSeparator()
        # menu_item20 = self.item_menu.addAction(f"Download {track[0]}")
        menu_item21 = self.item_menu.addAction(f"Download {id_key_list}")
        self.item_menu.addSeparator()
        menu_item40 = self.item_menu.addAction(f"Remove {id_key_list}")
        self.item_menu.addSeparator()
        menu_item60 = self.item_menu.addAction("Download All")
        self.item_menu.addSeparator()
        menu_item61 = self.item_menu.addAction("Remove All")

        # default enabled in menu
        menu_item01.setEnabled(False)
        menu_item10.setEnabled(True)
        menu_item11.setEnabled(True)
        #menu_item20.setEnabled(True)
        menu_item21.setEnabled(True)
        menu_item40.setEnabled(True)
        menu_item60.setEnabled(True)
        menu_item61.setEnabled(True)

        if len(id_key_list) == 0:
            menu_item11.setEnabled(False)
            menu_item21.setEnabled(False)
            menu_item40.setEnabled(False)
            menu_item60.setEnabled(False)
            menu_item61.setEnabled(False)

        # itm = self.twf.get_item_from_track(track)
        # mask = self.twf.get_mask_for_item(itm)
        value_of_rc = self.twf.get_tracked_value_in_struct(track, self.url_struct)
        is_itm_bool = self.twf.check_restrictions.check_type(str(bool), value_of_rc, True)
        if is_itm_bool:
            menu_item01.setEnabled(True)
            menu_item01.triggered.connect(lambda: self._toggle_bool_item(track))

        if len(id_key_list) > 0:
            menu_item11.setEnabled(True)
            menu_item11.triggered.connect(lambda: self._select_special_download_path(id_key_list))

            menu_item40.setEnabled(True)
            menu_item40.triggered.connect(lambda: self._remove_url_items(id_key_list, True))

            menu_item61.triggered.connect(lambda: self._remove_url_items(self.get_id_list(), True))

            menu_item21.setEnabled(True)
            menu_item21.triggered.connect(lambda: self._download_selected_items(id_key_list))

        # print("Position:",apos)
        # parentPosition = self.tableWidget_url.mapToGlobal(QtCore.QPoint(0, 0))
        # self.item_menu.move(parentPosition + apos)
        # position is already global
        self.item_menu.move(apos)
        self.item_menu.show()
    
    def _download_selected_items(self, id_key_list: list):
        """
        Downloads the items in the list, starts a thread for each download
        """
        # prepare dict
        if len(self.threads_event_list)<=5:
            file_properties_dict={}
            map_list=[]
            for index, url_id in enumerate(id_key_list):
                file_properties_dict.update({str(index):self.url_struct_options[url_id]})
                map_list.append((url_id,file_properties_dict))
            self.threads_mapping_dict.update({})
            kill_ev = threading.Event()
            kill_ev.clear() 
            cycle_time = 0.1
            local_st = class_signal_tracker.SignalTracker()
            q_dl_stream = thread_download_pytubefix.ThreadQueueDownloadStream(file_properties_dict, cycle_time, kill_ev, local_st)
            local_st.signal_th2m_to_log[str].connect(self.pytubefix_log)
            local_st.signal_th2m_download_start[str, str].connect(self.pytubefix_download_start)
            local_st.signal_th2m_download_end[str, str].connect(self.pytubefix_download_end)
            local_st.signal_th2m_on_progress[str, float].connect(self.pytubefix_download_progress)
            local_st.signal_th2m_thread_end[bool].connect(self._thread_exit_event)
            self.threads_event_list.append((kill_ev,local_st,q_dl_stream))
            q_dl_stream.start()
            log.info("Thread started with %s",id_key_list)
            print(q_dl_stream.is_alive())
        else:
            log.error("There are already 5 downloading threads simultaneously!")

    def _thread_exit_event(self,fine_exit:bool):
        """Thread ended and exit signal

        Args:
            fine_exit (bool): Ended normally or was killed
        """
        log.info("========== >>>>>> Thread Finished <<<<<<< ==========  ")
        if fine_exit:
            log.info("Tread Finalized correctly")
        th_ev_list=self.threads_event_list.copy()
        log.info("Number of running threads: %s", len(self.threads_event_list))
        time.sleep(1)
        for list_index,threads in enumerate(th_ev_list):
            q_dl_stream=threads[2]
            # print("Is thread alive? ->",list_index, q_dl_stream.is_alive())
            if not q_dl_stream.is_alive():
                # print("Is thread alive? ->",list_index, q_dl_stream.is_alive())
                q_dl_stream.join()
                self.threads_event_list.pop(list_index)
        log.info("Number of running threads: %s", len(self.threads_event_list))

    def _select_special_download_path(self, id_key_list: list):
        """Sets a different download path than the Default path"""
        dl_dir = self.a_dialog.open_directory_dialog(caption="Select Download directory", directory=self.download_path)
        download_path = ""
        if len(dl_dir) > 0:
            for url_key in id_key_list:
                if self.download_path != dl_dir[0]:
                    download_path = dl_dir[0]
                else:
                    download_path = ""
                    log.info("Same path as default!")
                log.info("Setting to %s Download dir: %s", url_key, dl_dir[0])
                track = [url_key, "Download Path"]
                self.twf.set_tracked_value_to_dict(track, str(download_path), self.url_struct, "", False)
                # mask returns it to ""
                # self.twf.set_value_and_trigger_data_change(track,str(download_path),str(str),"")
        # Refresh and update
        self.twf.data_struct = self.url_struct
        self.twf.set_show_dict()
        self.twf.refresh_tablewidget(self.twf.show_dict, self.twf.modelobj, self.twf.tablewidgetobj)
        self._update_shared_struct_options()
        # print(self.url_struct_options)

    def _is_same_list(self, list1: list, list2: list) -> bool:
        """Compares two lists

        Args:
            list1 (list): list1
            list2 (list): list2

        Returns:
            bool: True if the same,False if different
        """
        if len(list1) != len(list2):
            return False
        for iii, jjj in zip(list1, list2):
            if iii != jjj:
                return False
        return True

    def _remove_url_items(self, id_key_list: list, prompt_msgbox: bool = False):
        """Removes items from table

        Args:
            id_key_list (list): list of items to remove
            prompt_msgbox (bool, optional): Prompt message box yes/no to delete. Defaults to False.
        """
        if prompt_msgbox:
            if self._is_same_list(self.get_id_list(), id_key_list):
                msg_title = "Removing ALL URLS"
                msg_ = f"Are you sure to remove ALL items: {len(id_key_list)} in total"
            else:
                msg_title = "Removing URLS"
                msg_ = f"Are you sure to remove items {id_key_list}"
            if not self.a_dialog.send_question_yes_no_msgbox(msg_title, msg_):
                return

        for a_key in id_key_list:
            self.url_struct = self.get_dict_wo_key(self.url_struct, a_key)
            self.url_struct_options = self.get_dict_wo_key(self.url_struct_options, a_key)
        self.twf.data_struct = self.url_struct
        self.twf.set_show_dict()
        self.twf.refresh_tablewidget(self.twf.show_dict, self.twf.modelobj, self.twf.tablewidgetobj)

    def get_dict_wo_key(self, dictionary: dict, key) -> dict:
        """Returns a **shallow** copy of the dictionary without a key."""
        _dict = dictionary.copy()
        _dict.pop(key, None)
        return _dict

    def _toggle_bool_item(self, track: list):
        """Toggles the value of a bool item in the Table

        Args:
            track (list): track of item
        """
        value_of_rc = self.twf.get_tracked_value_in_struct(track, self.url_struct)
        is_itm_bool = self.twf.check_restrictions.check_type(str(bool), value_of_rc, True)
        if is_itm_bool:
            log.debug("Toggle Triggered %s", track)
            value_of_rc = self.twf.check_restrictions.set_type_to_value(value_of_rc, str(bool), "")
            self.twf.set_value_and_trigger_data_change(track, not value_of_rc, "")

            # self.twf.set_tracked_value_to_dict(track,not value_of_rc,self.twf.show_dict,"",True)
            # self.twf.refresh_tablewidget(self.twf.show_dict, self.twf.modelobj, self.twf.tablewidgetobj)

    def _get_id_key_list_from_selection(self) -> tuple[list, list]:
        """Gets a list of keys of the items selected

        Returns:
            tuple[list,list]: list of selected items, list of track lists
        """
        selindex = self.tableWidget_url.selectedIndexes()
        id_key_list = []
        track_list = []
        for selection in selindex:
            itm = self.twf.tablewidgetobj.itemFromIndex(selection)
            id_key = self.twf.get_key_value_from_item(itm)
            # #itm=selection.model().itemFromIndex(selection)
            track = self.twf.get_track_of_item_in_table(itm)
            # track=self.twf.get_key_value_from_row(itm.row())
            # if isinstance(self.twf.data_struct,list):
            #     id_key=self.twf.get([track[0],'ID'])
            # if isinstance(self.twf.data_struct,dict):
            #     id_key=self.get_tracked_value_in_dict([track[0],'ID'])
            if id_key not in id_key_list:
                id_key_list.append(id_key)
                track_list.append(track)
        return id_key_list, track_list

    def _pushbutton_url_pressed(self):
        """
        On pressed url button add to list
        """
        # fast regex check
        is_valid, _ = self.ptf.is_yt_valid_url(self.lineEdit_url.text())
        # slow html check
        if not is_valid:
            return
        urlexists = self.does_url_exist(self.lineEdit_url.text())
        if urlexists:
            # passed checks
            self.add_item_to_url_struct(self.lineEdit_url.text())

    def get_id_list(self):
        """
        Get the ids of the items in view
        """
        return self.twf.get_dict_key_list(self.url_struct)

    def is_id_taken(self, an_id) -> bool:
        """
        Check if the id is taken
        """
        idlist = self.get_id_list()
        if an_id in idlist:
            return True
        return False

    def get_unique_id(self, desired_id):
        """Gets a unique id
        if None will give a "UID_#" value is not taken

        Args:
            desired_id (_type_): wanted id

        Returns:
            str: An id which is not taken.
        """
        if not self.is_id_taken(desired_id) and desired_id != "" and desired_id is not None:
            return desired_id

        if desired_id is None or desired_id != "":
            desired_id = "UID_"
        iii = 1
        copydid = desired_id + str(iii)
        while self.is_id_taken(copydid):
            iii = iii + 1
            copydid = desired_id + str(iii)
        return copydid

    def add_item_to_url_struct(self, url: str):
        """
        Adds item to list
        """
        vid_list, vid_list_url = self.ptf.get_any_yt_videos_list(url)
        for vid_title, vid_url in zip(vid_list, vid_list_url):
            new_id = self.get_unique_id("URL" + str(self.url_id_counter))
            self.url_struct.update(
                {
                    new_id: {
                        "Index": self.url_id_counter,
                        "Title": vid_title,
                        "URL": vid_url,
                        "DL Enable": True,
                        "MP3": False,
                        "Skip Existing": True,
                        "Timeout sec": 0,
                        "Max Retries": 0,
                        "File Name": "",
                        "File Name Prefix": "",
                        "Download Path": "",
                    },
                }
            )

            self.url_id_counter = self.url_id_counter + 1
        # This sets options dict
        self._update_shared_struct_options()
        self.twf.data_struct = self.url_struct
        self.twf.set_show_dict()
        self.twf.refresh_tablewidget(self.twf.show_dict, self.twf.modelobj, self.twf.tablewidgetobj)

    def _get_request_exceptions_tuple(self) -> tuple:
        """Get exceptions from resource package

        Returns:
            tuple: tuple of exceptions
        """
        exception_list_ini = dir(requests.exceptions)
        exception_list = []
        for except_item in exception_list_ini:
            if "_" not in except_item:
                exception_list.append(except_item)
        exception_tuple = None
        for iii, except_item in enumerate(exception_list):
            if iii == 0:
                exception_tuple = (getattr(requests.exceptions, except_item),)
            else:
                exception_tuple = exception_tuple + (getattr(requests.exceptions, except_item),)
        return exception_tuple

    def does_url_exist(self, url):
        """
        Check if the given url exists or not
        """
        try:
            response = requests.get(url, timeout=10)
        except self._get_request_exceptions_tuple() as eee:
            log.error(eee)
            return False
        if response.status_code == 200:
            return True
        return False

    def set_download_path(self):
        """
        Sets the path for download and stores the configuration
        """
        dl_dir = self.a_dialog.open_directory_dialog(caption="Select Download directory")
        log.info("Download dir: %s", dl_dir)
        self.general_config["Last_Path_for_Download"] = dl_dir
        self.set_general_config_to_yml_file()
        self.download_path = self.general_config["Last_Path_for_Download"]
        self.label_DownloadPath.setText(f"Downloading to: {self.download_path}")

    def set_general_config_to_yml_file(self):
        """
        Saves the general configuration
        """
        try:
            if os.path.exists(self.path_config_file):
                with open(self.path_config_file, "w", encoding="UTF-8") as file:
                    yaml.dump(self.general_config, file)
            else:
                raise FileExistsError
        except (FileExistsError, PermissionError, FileNotFoundError, IsADirectoryError, NotImplementedError):
            log.error("Saving yml configuration file!")

    def _lineedit_url_changed(self):
        """
        When line edit changed
        """
        urlexists = self.does_url_exist(self.lineEdit_url.text())
        if urlexists:
            self.lineEdit_url.setToolTip("Exists!")
        else:
            self.lineEdit_url.setToolTip("")

    def _set_splitter_pos(self, pos, per=None):
        """
        Sets the position of the splitter
        """
        sizes = self.splitter.sizes()
        tot = sizes[1] + sizes[0]
        if per is not None and 0 <= per <= 1:  # per >= 0 and per <= 1:
            pos = int(tot * per)
            newsizes = [pos, tot - pos]
            self.splitter.setSizes(newsizes)
        elif pos <= tot:
            newsizes = [pos, tot - pos]
            self.splitter.setSizes(newsizes)
        self.splitter.adjustSize()

    def _set_path_labels(self):
        """
        Set texts and labels in Gui
        """
        self.groupBox.setTitle("List of URLs:")
        self.groupBox_2.setTitle("Processed URLs:")
        self.label_DownloadPath.setText(f"Downloading to: {self.download_path}")

    def show_aboutbox(self):
        """
        Shows About box
        """
        title = "About YT Downloader PytubeFix Tool"
        amsg = (
            '<h1 style="font-size:160%;color:red;">Programmed with love</h1>'
            + '<h1 style="font-size:160%;color:black;">by '
            + __author__
            + '</h1> <p style="color:black;">github: '
            + __gitaccount__
            + '</p> <p style="color:black;"> Current version: V'
            + __version__
            + '</p> <p style="color:black;">Creation date: '
            + __creationdate__
            + "</p>"
        )
        # msgbox = QMessageBox.about(main_window,title,amsg)
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle(title)
        # msgbox.setIcon(QMessageBox.Information)
        msgbox.setWindowIcon(self.icon_main)
        if self.icon_main_pixmap is not None:
            thepm = self.icon_main_pixmap.scaled(
                160, 160, QtCore.Qt.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation
            )  # QtCore.Qt.FastTransformation)
            # thepm.scaledToWidth(90,QtCore.Qt.TransformationMode.SmoothTransformation)
            #  QtCore.Qt.TransformationMode.SmoothTransformation) #QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            msgbox.setIconPixmap(thepm)
        msgbox.setText(amsg)
        msgbox.setTextFormat(QtCore.Qt.RichText)
        msgbox.exec_()


class MyWindow(QtWidgets.QMainWindow):
    """
    Override Window events to close
    """

    def closeEvent(self, event):
        """Close Event override

        Args:
            event (_type_): an event
        """

        # ask to leave?
        result = QtWidgets.QMessageBox.question(
            self,
            "Confirm Exit...",
            "Are you sure you want to exit ?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        event.ignore()

        if result == QtWidgets.QMessageBox.Yes:
            # print('inside class')
            # close dialogs
            # self.CCDialog

            # try:
            #     ui.CCDialog.quit()
            # except Exception as e:
            #     # log.error(e)
            #     pass
            # kill threads
            # threads_event_list is list of tuples : (kill_ev,local_st,q_dl_stream)
            print("On Close -> number of threads: ",len(ui.threads_event_list))
            for threads in ui.threads_event_list:
                try:
                    kill_ev=threads[0]
                    kill_ev.set()
                    q_dl_stream=threads[2]
                    q_dl_stream.join()
                except:
                    pass

            event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MyWindow()  # QtWidgets.QMainWindow() #Modified to close windows
    ui = UiMainWindowYt()  # GUI_PostProcessing.Ui_MainWindow()
    # Create Queue and redirect sys.stdout to this queue
    # sys.stdout = WriteStream(a_queue)
    # Log handler

    ui.setupUi(main_window)
    ui.setup_ui2(main_window)

    main_window.show()
    sys.exit(app.exec_())
