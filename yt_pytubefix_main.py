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

from PyQt5 import QtCore, QtGui, QtWidgets
from genericpath import isfile
from operator import index

import class_file_dialogs
import class_table_widget_functions
import class_pytubefix_use
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
        self.url_struct_mask={}

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
        self.url_struct_mask={
                    "__any__": {
                        "Index": {'__m__1':"is_unique",'__mv__1':""},
                        "Title": {'__m__1':"is_value_type",'__mv__1':str(str)},
                        "URL": {'__m__1':"is_value_type",'__mv__1':str(str),
                                '__m__2':"is_not_change",'__mv__2':""},
                        "DL Enable": {'__m__1':"is_value_type",'__mv__1':str(bool)},
                        "MP3": {'__m__1':"is_value_type",'__mv__1':str(bool)},
                        # "DL Button": "",
                    },
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
        self.twf.signal_data_change[list,str,str,str].connect(self._table_widget_data_changed)
        # self.icons_dict={'Plots':self.icon_main}

        # self.tvf.Expand_to_Depth(1)
        # self.tvf.set_Icons(self.icons_dict)

        # --------------use_pytubefix
        self.ptf = class_pytubefix_use.use_pytubefix()
        self.ptf.to_log[str].connect(self.pytubefix_log)
        self.ptf.download_start[str, str].connect(self.pytubefix_download_start)
        self.ptf.download_end[str, str].connect(self.pytubefix_download_end)
        self.ptf.on_progress[list].connect(self.pytubefix_download_progress)

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
        processed_val=self.twf.check_restrictions.set_type_to_value(val,valtype,subtype)
        self.twf.set_tracked_value_to_dict(track,processed_val,self.url_struct,subtype,False)
        # log.debug("after: %s",self.url_struct)

    def pytubefix_download_progress(self, progress_list: list):
        """
        Shows download progress
        """
        # url = self.ongoing_download_url
        title = self.ongoing_download_title
        [bytes_received, filesize] = progress_list
        per = round(bytes_received / filesize * 100, 2)
        # This is momentary
        txt = f"Downloaded {per}% for {title}"
        log.info(txt)

    def pytubefix_download_start(self, url: str, title: str):
        """Receives Signal form Pytube fix when a Download is started

        Args:
            url (str): url of download
            title (str): title of the download
        """
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
        # right click menu
        # self.treeView.customContextMenuRequested.connect(self.listItemRightClicked)

        self.lineEdit_url.textChanged.connect(self._lineedit_url_changed)
        self.actionAbout.triggered.connect(self.show_aboutbox)
        self.actionSet_Path.triggered.connect(self.Set_download_Path)
        self.pushButton_url.pressed.connect(self._pushbutton_url_pressed)

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

    def is_id_taken(self, id):
        """
        Check if the id is taken
        """
        idlist = self.get_id_list()
        if id in idlist:
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
        if self.is_id_taken(desired_id) == False and desired_id != "" and desired_id != None:
            return desired_id

        if desired_id == None or desired_id != "":
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
            newId = self.get_unique_id("URL" + str(self.url_id_counter))
            self.url_struct.update(
                {
                    newId: {
                        "Index": self.url_id_counter,
                        "Title": vid_title,
                        "URL": vid_url,
                        "DL Enable": True,
                        "MP3": False,
                        "DL Button": "",
                    },
                }
            )
            self.url_id_counter = self.url_id_counter + 1

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
            response = requests.get(url)
        except self._get_request_exceptions_tuple() as eee:
            log.error(eee)
            return False
        if response.status_code == 200:
            return True
        return False

    def Set_download_Path(self):
        """
        Sets the path for download and stores the configuration
        """
        dl_dir = self.a_dialog.open_directory_dialog(caption="Select Download directory")
        log.info("Download dir: %s", dl_dir)
        self.general_config["Last_Path_for_Download"] = dl_dir
        self.set_general_config_to_yml_file()
        self.download_path = self.general_config["Last_Path_for_Download"]
        self.label_DownloadPath.setText("Downloading to: {}".format(self.download_path))

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
        if per != None and per >= 0 and per <= 1:
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
        self.label_DownloadPath.setText("Downloading to: {}".format(self.download_path))

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
        if self.icon_main_pixmap != None:
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
